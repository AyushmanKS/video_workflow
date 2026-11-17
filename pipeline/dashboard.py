import hashlib
import hmac
import html
import json
import os
import re
import secrets
import shutil
import signal
import sqlite3
import struct
import subprocess
import sys
import threading
import time
import zlib
from collections import deque
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit

from . import DATA, ROOT, dashui, db, events, explain, monitor, notify

PORT = 8765
KEYFILE = ROOT / "secrets" / "dashboard.json"
URLFILE = DATA / "dashboard_url.json"
LOG = DATA / "logs" / "dashboard.log"
COOKIE = "ss_session"
SESSION_S = 30 * 86400
FAIL_WINDOW_S = 900
FAIL_PER_IP = 5
FAIL_GLOBAL = 30
POLL_S = 3
SSE_MAX = 8
SSE_LIFE_S = 600
TUNNEL_RX = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")
CSP = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; manifest-src 'self'; worker-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'; object-src 'none'"
SEV_ORDER = {"critical": 0, "recoverable": 1, "warning": 2, "info": 3}
BUCKETS = ("failed", "processing", "waiting", "queued", "completed", "in production")
NOT_FOUND = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Not found · Studio</title>'
             '<link rel="stylesheet" href="/static/app.css"></head><body><main><h1>Page not found</h1><section class="card"><p class="lead">This page does not exist.</p><p><a href="/">Go to Home</a></p></section></main></body></html>')
OLD_ROUTES = {"/projects": "/progress", "/queue": "/progress", "/timeline": "/progress", "/issues": "/problems", "/analytics": "/results"}
EPISODE_RX = re.compile(r"/episode/(C\d{4,})")


def log(msg):
    line = f"{time.strftime('%m-%d %H:%M:%S')} {notify.scrub(msg)}"
    print(line, flush=True)


def parse_tunnel_url(line):
    m = TUNNEL_RX.search(line or "")
    return m.group(0) if m else None


_keys = {"mtime": None, "data": None}
_keys_lock = threading.Lock()


def new_keys():
    return {"login_key": secrets.token_urlsafe(32), "cookie_secret": secrets.token_hex(32), "created": db.now()}


def keys(create=True):
    with _keys_lock:
        try:
            mt = KEYFILE.stat().st_mtime_ns
        except OSError:
            mt = None
        if mt is not None and mt == _keys["mtime"] and _keys["data"]:
            return _keys["data"]
        d = None
        if mt is not None:
            try:
                d = json.loads(KEYFILE.read_text())
            except (OSError, ValueError):
                d = None
        if not d or not d.get("login_key") or not d.get("cookie_secret"):
            if not create:
                return None
            d = new_keys()
            notify.write_secret(KEYFILE, d)
            mt = KEYFILE.stat().st_mtime_ns
        _keys.update(mtime=mt, data=d)
        return d


def rotate_key():
    d = new_keys()
    notify.write_secret(KEYFILE, d)
    _keys.update(mtime=None, data=None)
    return d


def read_url():
    try:
        return json.loads(URLFILE.read_text())
    except (OSError, ValueError):
        return {}


def login_link(base=None):
    base = base or read_url().get("url")
    if not base:
        return None
    return f"{base}/login?k={quote(keys()['login_key'])}"


def link_message(reason):
    info = read_url()
    link = login_link(info.get("url"))
    if not link:
        return None
    return (f"🔗 <b>Dashboard</b> — {html.escape(reason, quote=False)}\n<a href=\"{html.escape(link, quote=True)}\">Open the dashboard</a>\n"
            f"Address: {html.escape(info['url'], quote=False)}\nThe link signs this phone in for 30 days. Do not forward it. "
            "Use Chrome's ⋮ → Add to Home screen after it opens.")


def sign(secret, msg):
    return hmac.new(bytes.fromhex(secret), msg.encode(), hashlib.sha256).hexdigest()


def make_session(now=None):
    k = keys()
    exp = int((now or time.time()) + SESSION_S)
    nonce = secrets.token_hex(12)
    body = f"{exp}.{nonce}"
    return f"{body}.{sign(k['cookie_secret'], body)}"


def check_session(value, now=None):
    if not value:
        return None
    parts = value.split(".")
    if len(parts) != 3:
        return None
    body = f"{parts[0]}.{parts[1]}"
    if not hmac.compare_digest(sign(keys()["cookie_secret"], body), parts[2]):
        return None
    try:
        if int(parts[0]) < (now or time.time()):
            return None
    except ValueError:
        return None
    return parts[1]


def csrf_for(nonce):
    return sign(keys()["cookie_secret"], f"csrf:{nonce}")[:40]


class Limiter:
    def __init__(self):
        self.lock = threading.Lock()
        self.fails = {}
        self.all = deque()

    def _trim(self, now):
        while self.all and now - self.all[0] > FAIL_WINDOW_S:
            self.all.popleft()
        for ip in list(self.fails):
            self.fails[ip] = [t for t in self.fails[ip] if now - t <= FAIL_WINDOW_S]
            if not self.fails[ip]:
                del self.fails[ip]

    def blocked(self, ip, now=None):
        now = now or time.time()
        with self.lock:
            self._trim(now)
            return len(self.fails.get(ip, [])) >= FAIL_PER_IP or len(self.all) >= FAIL_GLOBAL

    def fail(self, ip, now=None):
        now = now or time.time()
        with self.lock:
            self.fails.setdefault(ip, []).append(now)
            self.all.append(now)


def ro_connect():
    con = sqlite3.connect(f"file:{db.DB_PATH}?mode=ro", uri=True, timeout=5)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout=5000")
    return con


HOME_RX = re.compile(r"/(?:Users|home)/[^/\s'\"]+")


def scrub(text):
    s = explain.redact("" if text is None else str(text))
    s = s.replace(str(ROOT) + os.sep, "").replace(str(ROOT), ".")
    s = re.sub(r"/(?:private/)?var/folders/\S+", "<tmp>", s)
    return HOME_RX.sub("~", s)


def rel(path):
    if not path:
        return ""
    s = str(path)
    if s.startswith(str(ROOT / "secrets")):
        return "(hidden)"
    root = str(ROOT) + os.sep
    if s.startswith(root):
        return s[len(root):]
    return os.path.basename(s) if os.path.isabs(s) else scrub(s)


def e(s):
    return html.escape("" if s is None else str(s), quote=True)


def fmt_t(t):
    if not t:
        return "-"
    d = datetime.fromtimestamp(float(t))
    if d.date() == datetime.now().date():
        return d.strftime("%H:%M")
    return d.strftime("%b %d %H:%M")


def fmt_ts(ts):
    if not ts or ts == "now":
        return ts or "-"
    try:
        d = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return fmt_t((d if d.tzinfo else d.astimezone()).timestamp())
    except ValueError:
        return str(ts)


def ts_epoch(ts):
    try:
        d = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return (d if d.tzinfo else d.astimezone()).timestamp()
    except (TypeError, ValueError):
        return None


def ig_jobs():
    try:
        from . import igschedule

        out = []
        year = datetime.now().year
        for j in igschedule.jobs():
            try:
                d = datetime.strptime(f"{year}-{j['when']}", "%Y-%m-%d %H:%M")
                if d < datetime.now() - timedelta(days=180):
                    d = d.replace(year=year + 1)
                j["t"] = d.timestamp()
            except ValueError:
                j["t"] = None
            j["log"] = rel(j.get("log"))
            out.append(j)
        return out
    except Exception:
        return []


def short_project(name, pid):
    head = re.split(r"\s+[—–-]\s+", (name or pid or "-").strip())[0]
    return head.title() if head.isupper() else head


def variants(con):
    rows = con.execute("SELECT v.id, v.language, v.status AS vstatus, v.updated_at, c.id AS content_id, c.episode, c.topic, c.project_id, p.name AS project_name "
                       "FROM variants v JOIN contents c ON c.id=v.content_id LEFT JOIN projects p ON p.id=c.project_id ORDER BY c.id, v.language").fetchall()
    tasks = {}
    for t in con.execute("SELECT * FROM task_state WHERE variant_id IS NOT NULL ORDER BY t"):
        tasks[t["variant_id"]] = t
    pubs = {}
    for p in con.execute("SELECT variant_id, platform, scheduled_for, published_at, url FROM publications ORDER BY id"):
        pubs.setdefault(p["variant_id"], []).append(p)
    queue = {f"{q['content_id']}-{q['lang']}": q for q in con.execute("SELECT * FROM publish_queue")}
    jobs = {}
    for j in ig_jobs():
        if not j["dry_run"]:
            jobs[j["variant"]] = j
    iss = {}
    for r in con.execute("SELECT variant_id, severity FROM issues WHERE status IN ('open','acknowledged') AND variant_id IS NOT NULL"):
        iss.setdefault(r["variant_id"], []).append(r["severity"])
    quiet, loud = set(), set()
    for r in con.execute("SELECT variant_id, stage, status FROM issues WHERE variant_id IS NOT NULL"):
        (loud if r["status"] == "open" else quiet).add((r["variant_id"], r["stage"]))
    stale = time.time() - 6 * 3600
    now = time.time()
    out = []
    for r in rows:
        v = r["id"]
        t = tasks.get(v)
        q = queue.get(v)
        job = jobs.get(v)
        plist = pubs.get(v, [])
        status = t["status"] if t else "Not Started"
        known = t is not None and (v, t["stage"]) in quiet and (v, t["stage"]) not in loud
        if status in ("Failed", "Needs Attention") and not known:
            bucket = "failed"
        elif status == "Running" and t["t"] >= stale:
            bucket = "processing"
        elif status == "Waiting for Approval":
            bucket = "waiting"
        elif (q and q["status"] in ("queued", "waiting", "backoff", "running")) or job:
            bucket = "queued"
        elif plist:
            bucket = "completed"
        else:
            bucket = "in production"
        nxt = []
        for p in plist:
            te = ts_epoch(p["scheduled_for"])
            if te and te > now:
                nxt.append((te, p["platform"]))
        if q and q["status"] != "done" and q["publish_at"] and q["publish_at"] != "now":
            te = ts_epoch(q["publish_at"])
            if te and te > now:
                nxt.append((te, "youtube"))
        if job and job.get("t") and job["t"] > now:
            nxt.append((job["t"], "instagram"))
        out.append({
            "id": v, "language": r["language"], "content_id": r["content_id"], "episode": r["episode"], "topic": r["topic"], "project_id": r["project_id"] or "-",
            "project": short_project(r["project_name"], r["project_id"]), "stage": t["stage"] if t else "-", "status": status, "bucket": bucket,
            "message": scrub(t["message"]) if t else "", "t": t["t"] if t else None, "progress": t["progress"] if t else None,
            "platforms": sorted({p["platform"] for p in plist}), "next": min(nxt) if nxt else None, "issues": sorted(iss.get(v, []), key=lambda s: SEV_ORDER.get(s, 9)),
        })
    return out


def projects_summary(con):
    vs = variants(con)
    out = []
    for p in con.execute("SELECT * FROM projects ORDER BY created_at"):
        mine = [v for v in vs if v["project_id"] == p["id"]]
        c = {b: sum(1 for v in mine if v["bucket"] == b) for b in BUCKETS}
        nxt = min([v["next"] for v in mine if v["next"]], default=None)
        nv = next((v for v in mine if v["next"] == nxt), None) if nxt else None
        out.append({"id": p["id"], "name": p["name"], "status": p["status"], "languages": json.loads(p["languages"] or "[]"), "total": len(mine), "counts": c,
                    "videos": len({v["content_id"] for v in mine}), "next": nxt, "next_variant": nv["id"] if nv else None})
    return out


def event_json(r):
    who = " ".join(x for x in (r["variant_id"] or r["content_id"] or r["project_id"] or "-", r["platform"] or "") if x)
    return {"rowid": r["rowid"], "t": r["t"], "time": fmt_t(r["t"]), "kind": r["kind"], "icon": monitor.ICON.get(r["kind"], "."), "who": who, "variant": r["variant_id"] or "",
            "stage": r["stage"], "status": r["status"] or "", "message": scrub(r["message"]), "progress": r["progress"], "error_code": r["error_code"] or ""}


class Feed:
    def __init__(self):
        self.cond = threading.Condition()
        self.recent = deque(maxlen=300)
        self.subs = 0
        self.last = self._max()
        self.stop = threading.Event()
        self.wake = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def _max(self):
        try:
            con = ro_connect()
            try:
                return con.execute("SELECT COALESCE(MAX(rowid),0) FROM events").fetchone()[0]
            finally:
                con.close()
        except sqlite3.Error:
            return 0

    def poll(self):
        con = ro_connect()
        try:
            rows = con.execute("SELECT rowid, * FROM events WHERE rowid > ? ORDER BY rowid LIMIT 200", (self.last,)).fetchall()
        finally:
            con.close()
        if rows:
            with self.cond:
                for r in rows:
                    self.recent.append(event_json(r))
                self.last = rows[-1]["rowid"]
                self.cond.notify_all()
        return len(rows)

    def run(self):
        while not self.stop.is_set():
            if self.subs <= 0:
                self.wake.wait(30)
                self.wake.clear()
                continue
            try:
                self.poll()
            except sqlite3.Error:
                pass
            self.stop.wait(POLL_S)

    def subscribe(self):
        with self.cond:
            self.subs += 1
        self.wake.set()

    def unsubscribe(self):
        with self.cond:
            self.subs -= 1

    def since(self, after, timeout):
        with self.cond:
            if self.last <= after:
                self.cond.wait(timeout)
            items = [x for x in self.recent if x["rowid"] > after]
            if items and items[0]["rowid"] > after + 1 and len(self.recent) == self.recent.maxlen:
                return None
            return items


def query_events(after=0, limit=100, video=None):
    con = ro_connect()
    try:
        q, args = "SELECT rowid, * FROM events WHERE rowid > ?", [int(after)]
        if video:
            q += " AND (variant_id=? OR content_id=?)"
            args += [video, video]
        q += " ORDER BY rowid DESC LIMIT ?"
        args.append(int(limit))
        return [event_json(r) for r in reversed(con.execute(q, args).fetchall())]
    finally:
        con.close()


def analytics_rows(con):
    out = []
    q = ("SELECT s.*, p.variant_id, p.platform AS pplat, p.url FROM analytics_snapshots s JOIN publications p ON p.id=s.publication_id "
         "WHERE s.id IN (SELECT MAX(id) FROM analytics_snapshots GROUP BY publication_id) ORDER BY p.variant_id, p.platform")
    for r in con.execute(q):
        try:
            m = json.loads(r["metrics"] or "{}")
        except ValueError:
            m = {}
        plat = r["pplat"] or r["platform"]
        row = {"variant": r["variant_id"], "platform": plat, "label": r["label"], "captured": r["captured_at"], "age_h": r["age_h"] or m.get("age_h")}
        if plat == "instagram":
            ins = m.get("insights") or {}
            avg = ins.get("ig_reels_avg_watch_time")
            row.update(views=ins.get("views"), reach=ins.get("reach"), likes=ins.get("likes"), comments=ins.get("comments"), shares=ins.get("shares"), saves=ins.get("saved"),
                       watch=round(avg / 1000, 1) if isinstance(avg, (int, float)) else None)
        else:
            pc = m.get("public_counters") or {}
            tot = m.get("totals_to_date")
            tot = tot[0] if isinstance(tot, list) and tot else tot if isinstance(tot, dict) else {}
            row.update(views=tot.get("views", pc.get("viewCount")), likes=tot.get("likes", pc.get("likeCount")), comments=tot.get("comments", pc.get("commentCount")),
                       shares=tot.get("shares"), saves=None, reach=None, watch=tot.get("averageViewDuration"), minutes=tot.get("estimatedMinutesWatched"),
                       source="Analytics totals" if tot else "public counters")
        out.append(row)
    return out


def next_collection():
    from . import analytics

    h, m = analytics.DAILY_AT
    now = datetime.now()
    nxt = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if nxt <= now:
        nxt += timedelta(days=1)
    plist = (Path.home() / "Library" / "LaunchAgents" / f"{analytics.AGENT_LABEL}.plist").exists()
    return nxt, plist


MANIFEST = json.dumps({"name": "Shorts Studio", "short_name": "Studio", "start_url": "/", "scope": "/", "display": "standalone", "background_color": "#14191c",
                       "theme_color": "#14191c", "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
                                                           {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]})


def png_icon(n):
    bg, fg = (20, 25, 28), (232, 190, 110)
    rows = []
    cy = n * 0.5
    h = n * 0.36
    for y in range(n):
        row = bytearray([0])
        dy = abs(y - cy)
        for x in range(n):
            inside = (n * 0.36) <= x <= (n * 0.36 + h) and dy <= (h / 2) * (1 - (x - n * 0.36) / h) * 1.15
            row += bytes(fg if inside else bg)
        rows.append(bytes(row))
    raw = zlib.compress(b"".join(rows), 9)

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)

    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 2, 0, 0, 0)) + chunk(b"IDAT", raw) + chunk(b"IEND", b"")


_static = {}


def static_files():
    if not _static:
        _static.update({
            "/static/app.css": ("text/css; charset=utf-8", dashui.CSS.encode()), "/static/app.js": ("text/javascript; charset=utf-8", dashui.JS.encode()),
            "/sw.js": ("text/javascript; charset=utf-8", dashui.SW.encode()), "/manifest.webmanifest": ("application/manifest+json", MANIFEST.encode()),
            "/offline.html": ("text/html; charset=utf-8", dashui.offline_html().encode()), "/icon-192.png": ("image/png", png_icon(192)),
            "/icon-512.png": ("image/png", png_icon(512)),
        })
        _static["/favicon.ico"] = _static["/icon-192.png"]
    return _static


class App:
    def __init__(self):
        self.limiter = Limiter()
        self.feed = Feed()
        self.sse = 0
        self.lock = threading.Lock()
        keys()


class Handler(BaseHTTPRequestHandler):
    server_version = "studio"
    sys_version = ""
    protocol_version = "HTTP/1.1"
    timeout = 120
    app = None

    def log_message(self, fmt, *args):
        pass

    def log_request(self, code="-", size="-"):
        path = urlsplit(self.path).path
        if path not in ("/healthz",) and not path.startswith(("/static/", "/icon")):
            log(f"{self.client_ip()} {self.command} {path[:80]} {code}")

    def client_ip(self):
        ip = self.client_address[0]
        if ip == "127.0.0.1" and self.headers.get("CF-Connecting-IP"):
            return self.headers["CF-Connecting-IP"][:64]
        return ip

    def headers_common(self, ctype, length=None, cache="no-store"):
        self.send_header("Content-Type", ctype)
        if length is not None:
            self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", cache)
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")

    def send(self, code, body, ctype="text/html; charset=utf-8", cache="no-store", extra=None):
        fix = getattr(self, "html_fix", None)
        if fix and isinstance(body, str):
            body = body.replace(*fix)
            self.html_fix = None
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.headers_common(ctype, len(data), cache)
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def cookie(self):
        raw = self.headers.get("Cookie") or ""
        for part in raw.split(";"):
            k, _, v = part.strip().partition("=")
            if k == COOKIE:
                return v
        return None

    def session(self):
        return check_session(self.cookie())

    def tunneled(self):
        return bool(self.headers.get("CF-Connecting-IP") or self.headers.get("CF-Ray"))

    def unauthorized(self, api=False):
        if api:
            return self.send(401, json.dumps({"error": "sign-in required"}), "application/json")
        body = dashui.signin_html()
        self.send(401, body)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        try:
            self.route_get()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as ex:
            log(f"error {self.command} {urlsplit(self.path).path}: {type(ex).__name__}: {ex}")
            try:
                self.send(500, "<h1>Server error</h1><p>See data/logs/dashboard.log on the Mac.</p>")
            except Exception:
                pass

    def route_get(self):
        u = urlsplit(self.path)
        path, q = u.path, parse_qs(u.query)
        st = static_files()
        if path == "/healthz":
            return self.send(200, "ok", "text/plain; charset=utf-8")
        if path in st:
            ctype, data = st[path]
            return self.send(200, data, ctype, "no-cache" if path in ("/sw.js", "/manifest.webmanifest") else "public, max-age=3600")
        if path == "/login":
            return self.login(q)
        if path == "/logout":
            return self.send(303, "", extra={"Location": "/", "Set-Cookie": f"{COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax"})
        nonce = self.session()
        api = path.startswith("/api/") or path == "/events/stream"
        pages = ("/", "/progress", "/uploads", "/problems", "/results")
        episode = EPISODE_RX.fullmatch(path)
        if path not in pages and path not in OLD_ROUTES and not episode and path not in ("/api/events", "/api/overview", "/events/stream"):
            return self.send(404, NOT_FOUND)
        if not nonce:
            return self.unauthorized(api)
        if path in OLD_ROUTES:
            return self.send(302, "", extra={"Location": OLD_ROUTES[path]})
        if path == "/events/stream":
            if self.tunneled():
                return self.send(409, json.dumps({"error": "streaming is buffered by the quick tunnel; poll /api/events"}), "application/json")
            return self.stream(q)
        if path == "/api/events":
            raw = (q.get("after") or ["0"])[0]
            after = int(raw) if raw.isdigit() else 0
            return self.send(200, json.dumps({"events": query_events(after=after, limit=100)}), "application/json")
        con = ro_connect()
        try:
            if not api and self.tunneled():
                self.html_fix = ('data-sse="1"', 'data-sse="0"')
            if path == "/api/overview":
                return self.send(200, json.dumps(monitor.overview(con), default=str), "application/json")
            if path == "/":
                return self.send(200, dashui.render_home(con))
            if path == "/progress":
                return self.send(200, dashui.render_progress(con, q))
            if path == "/uploads":
                return self.send(200, dashui.render_uploads(con))
            if path == "/problems":
                return self.send(200, dashui.render_problems(con, csrf_for(nonce), q))
            if path == "/results":
                return self.send(200, dashui.render_results(con, q))
            if episode:
                body = dashui.render_episode(con, episode.group(1))
                return self.send(200, body) if body else self.send(404, NOT_FOUND)
        finally:
            con.close()

    def login(self, q):
        ip = self.client_ip()
        if self.app.limiter.blocked(ip):
            return self.send(429, "<h1>Too many attempts</h1><p>Wait 15 minutes, or rotate the key on the Mac.</p>", extra={"Retry-After": str(FAIL_WINDOW_S)})
        given = (q.get("k") or [""])[0]
        if not given or not hmac.compare_digest(given.encode(), keys()["login_key"].encode()):
            self.app.limiter.fail(ip)
            log(f"failed login from {ip}")
            return self.send(403, "<h1>Link not valid</h1><p>Send /link to the Telegram bot for the current link.</p>")
        cookie = f"{COOKIE}={make_session()}; Path=/; Max-Age={SESSION_S}; HttpOnly; Secure; SameSite=Lax"
        log(f"login ok from {ip}")
        page = '<meta http-equiv="refresh" content="0;url=/"><p>Signed in. <a href="/">Open the dashboard</a></p>'
        return self.send(200, page, extra={"Set-Cookie": cookie, "Cache-Control": "no-store"})

    def stream(self, q):
        with self.app.lock:
            if self.app.sse >= SSE_MAX:
                return self.send(503, json.dumps({"error": "too many streams"}), "application/json", extra={"Retry-After": "10"})
            self.app.sse += 1
        feed = self.app.feed
        feed.subscribe()
        try:
            raw = self.headers.get("Last-Event-ID") or (q.get("after") or [""])[0]
            after = int(raw) if str(raw).isdigit() else feed.last
            self.send_response(200)
            self.headers_common("text/event-stream", None, "no-cache, no-transform")
            self.send_header("X-Accel-Buffering", "no")
            self.send_header("Transfer-Encoding", "chunked")
            self.send_header("Connection", "close")
            self.end_headers()
            self.close_connection = True

            def chunk(text):
                data = text.encode()
                self.wfile.write(f"{len(data):x}\r\n".encode() + data + b"\r\n")
                self.wfile.flush()

            chunk(":" + " " * 2048 + "\nretry: 5000\n\n")
            end = time.time() + SSE_LIFE_S
            while time.time() < end:
                items = feed.since(after, 15)
                if items is None:
                    items = query_events(after=after, limit=100)
                if items:
                    chunk("".join(f"id: {x['rowid']}\nevent: ev\ndata: {json.dumps(x, ensure_ascii=False)}\n\n" for x in items))
                    after = items[-1]["rowid"]
                else:
                    chunk(f"event: ping\ndata: {int(time.time())}\n\n")
            self.wfile.write(b"0\r\n\r\n")
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            feed.unsubscribe()
            with self.app.lock:
                self.app.sse -= 1

    def do_POST(self):
        try:
            self.route_post()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as ex:
            log(f"error POST: {type(ex).__name__}: {ex}")
            self.send(500, "<h1>Server error</h1>")

    def route_post(self):
        path = urlsplit(self.path).path
        if path == "/login":
            n = int(self.headers.get("Content-Length") or 0)
            if n > 4096:
                return self.send(413, "<h1>Too large</h1>")
            form = parse_qs(self.rfile.read(n).decode("utf-8", "replace"))
            raw = (form.get("link") or [""])[0].strip()
            key = (parse_qs(urlsplit(raw).query).get("k") or [raw])[0]
            return self.login({"k": [key]})
        m = re.fullmatch(r"/issues/(\d+)/ack", path)
        if not m:
            return self.send(404, "<h1>Not found</h1>")
        nonce = self.session()
        if not nonce:
            return self.unauthorized()
        origin = self.headers.get("Origin")
        host = self.headers.get("Host")
        if origin and origin != "null" and urlsplit(origin).netloc != host:
            return self.send(403, "<h1>Cross-origin request refused</h1>")
        n = int(self.headers.get("Content-Length") or 0)
        if n > 4096:
            return self.send(413, "<h1>Too large</h1>")
        form = parse_qs(self.rfile.read(n).decode("utf-8", "replace"))
        token = (form.get("csrf") or [""])[0]
        if not hmac.compare_digest(token.encode(), csrf_for(nonce).encode()):
            return self.send(403, "<h1>Form expired</h1><p>Reload the page and try again.</p>")
        ids = [int(m.group(1))]
        for part in (form.get("ids") or [""])[0].split(",")[:50]:
            if part.strip().isdigit() and int(part) not in ids:
                ids.append(int(part))
        con = events.connect()
        try:
            for iid in ids:
                r = con.execute("SELECT status FROM issues WHERE id=?", (iid,)).fetchone()
                if r and r["status"] == "open":
                    monitor.resolve_issue(con, iid, "acknowledged on the dashboard", "acknowledged")
        finally:
            con.close()
        return self.send(303, "", extra={"Location": "/problems"})


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def make_server(port=PORT):
    app = App()
    handler = type("BoundHandler", (Handler,), {"app": app})
    srv = Server(("127.0.0.1", port), handler)
    srv.app = app
    return srv


class Tunnel:
    def __init__(self, port, announce=True, binary="cloudflared"):
        self.port, self.announce, self.binary = port, announce, binary
        self.stop = threading.Event()
        self.proc = None
        self.url = None
        self.thread = threading.Thread(target=self.run, daemon=True)

    def start(self):
        self.kill_stale()
        self.thread.start()
        return self

    def kill_stale(self):
        pid = read_url().get("cloudflared_pid")
        if not pid:
            return
        try:
            cmd = subprocess.run(["ps", "-p", str(int(pid)), "-o", "command="], capture_output=True, text=True).stdout
            if "cloudflared" in cmd and f"127.0.0.1:{self.port}" in cmd:
                os.kill(int(pid), signal.SIGTERM)
                log(f"stopped stale cloudflared pid {pid}")
        except (OSError, ValueError):
            pass

    def spawn(self):
        found = threading.Event()
        holder = {}
        self.proc = subprocess.Popen([self.binary, "tunnel", "--no-autoupdate", "--protocol", "http2", "--url", f"http://127.0.0.1:{self.port}"],
                                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        proc = self.proc

        def reader():
            for line in proc.stderr:
                u = parse_tunnel_url(line)
                if u and "url" not in holder:
                    holder["url"] = u
                    found.set()
                elif " ERR " in line:
                    log("cloudflared: " + line.strip()[:200])

        threading.Thread(target=reader, daemon=True).start()
        deadline = time.time() + 60
        while time.time() < deadline and not found.is_set() and proc.poll() is None and not self.stop.is_set():
            found.wait(0.5)
        return holder.get("url")

    def reachable(self, url, tries=30, gap=4, first_wait=0):
        import requests

        if first_wait and self.stop.wait(first_wait):
            return False
        last = None
        for i in range(tries):
            if self.stop.is_set():
                return False
            try:
                code = requests.get(url + "/healthz", timeout=10).status_code
                if code == 200:
                    return True
                last = f"HTTP {code}"
            except requests.RequestException as ex:
                last = type(ex).__name__
            if tries > 1 and i % 5 == 4:
                log(f"tunnel not reachable yet ({last}), attempt {i + 1}/{tries}")
            self.stop.wait(gap)
        if tries > 1:
            log(f"tunnel never became reachable ({last})")
        return False

    def publish(self, url):
        old = read_url()
        info = {"url": url, "since": old.get("since") if old.get("url") == url else db.now(), "checked_at": db.now(), "port": self.port,
                "cloudflared_pid": self.proc.pid if self.proc else None}
        URLFILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = URLFILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(info, indent=2))
        os.chmod(tmp, 0o600)
        os.replace(tmp, URLFILE)
        if old.get("url") != url:
            log(f"tunnel address changed (was {'set' if old.get('url') else 'none'})")
            if self.announce:
                msg = link_message("new address" if old.get("url") else "now online")
                if msg:
                    notify.enqueue_local("Dashboard link", msg, secret=True, kind="local")
        self.url = url

    def terminate(self):
        p = self.proc
        if p and p.poll() is None:
            p.terminate()
            try:
                p.wait(10)
            except subprocess.TimeoutExpired:
                p.kill()

    def run(self):
        backoff = 10
        while not self.stop.is_set():
            if not shutil.which(self.binary):
                log("cloudflared is not installed (brew install cloudflared); retrying in 5 min")
                self.stop.wait(300)
                continue
            try:
                url = self.spawn()
                if url and self.reachable(url, tries=40, first_wait=10):
                    self.publish(url)
                    backoff = 10
                    fails = 0
                    while not self.stop.is_set() and self.proc.poll() is None:
                        if self.stop.wait(300):
                            break
                        if self.reachable(url, tries=1):
                            fails = 0
                            info = read_url()
                            if info.get("url") == url:
                                info["checked_at"] = db.now()
                                URLFILE.write_text(json.dumps(info, indent=2))
                        else:
                            fails += 1
                            log(f"tunnel health check failed ({fails}/3)")
                            if fails >= 3:
                                break
                else:
                    log("tunnel gave no reachable URL")
            except Exception as ex:
                log(f"tunnel error: {type(ex).__name__}: {ex}")
            self.terminate()
            if self.stop.is_set():
                break
            log(f"restarting cloudflared in {backoff} s")
            self.stop.wait(backoff)
            backoff = min(backoff * 2, 300)

    def close(self):
        self.stop.set()
        self.terminate()


def rotate_log():
    try:
        if LOG.exists() and LOG.stat().st_size > 5 * 1024 * 1024:
            os.replace(LOG, LOG.with_suffix(".log.1"))
    except OSError:
        pass


def run(port=PORT, tunnel=False):
    rotate_log()
    srv = make_server(port)
    log(f"dashboard on http://127.0.0.1:{port} (tunnel {'in this process' if tunnel else 'run separately: pipeline dashboard tunnel'})")
    tun = Tunnel(port).start() if tunnel else None

    def stop(*_):
        log("stopping")
        if tun:
            tun.close()
        threading.Thread(target=srv.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        srv.serve_forever(poll_interval=1)
    finally:
        srv.app.feed.stop.set()
        if tun:
            tun.close()
        srv.server_close()


def run_tunnel(port=PORT):
    log(f"tunnel for http://127.0.0.1:{port}; the web server can restart without changing the address")
    tun = Tunnel(port).start()
    done = threading.Event()

    def stop(*_):
        log("tunnel stopping")
        done.set()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        while not done.wait(1):
            pass
    finally:
        tun.close()
