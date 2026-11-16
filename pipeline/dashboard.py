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

from . import DATA, ROOT, db, events, explain, monitor, notify

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
NAV = [("/", "Overview"), ("/projects", "Projects"), ("/queue", "Queue"), ("/uploads", "Uploads"), ("/issues", "Issues"), ("/timeline", "Timeline"), ("/analytics", "Analytics")]
CSP = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; manifest-src 'self'; worker-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'; object-src 'none'"
SEV_ORDER = {"critical": 0, "recoverable": 1, "warning": 2, "info": 3}
BUCKETS = ("failed", "processing", "waiting", "queued", "completed", "in production")


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
        if status in ("Failed", "Needs Attention"):
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


def badge(text, cls=None):
    return f'<span class="b {e(cls or str(text).lower().replace(" ", "-"))}">{e(text)}</span>'


def page(title, body, active="/", live_after=None, video=""):
    nav = "".join(f'<a href="{h}"{" class=on" if h == active else ""}>{n}</a>' for h, n in NAV)
    live = f' data-live="1" data-sse="1" data-after="{int(live_after)}" data-video="{e(video)}"' if live_after is not None else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#1d2b24"><title>{e(title)} · Studio</title><link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" href="/icon-192.png"><link rel="apple-touch-icon" href="/icon-192.png"><link rel="stylesheet" href="/static/app.css"></head>
<body{live}><header><div class="top"><b>Shorts Studio</b><span id="live" class="live">read-only</span></div><nav>{nav}</nav></header>
<div id="banner" class="banner" hidden><a href="">New activity — tap to refresh</a></div><main><h1>{e(title)}</h1>{body}</main>
<script src="/static/app.js"></script></body></html>"""


def tile(label, value, sub=None, cls=""):
    return f'<div class="tile {cls}"><div class="v">{e(value)}</div><div class="l">{e(label)}</div>{f"<div class=s>{e(sub)}</div>" if sub else ""}</div>'


def ev_li(x):
    prog = f" {x['progress'] * 100:.0f}%" if x["progress"] is not None else ""
    code = f" [{x['error_code']}]" if x["error_code"] else ""
    return (f'<li class="ev k-{e(x["kind"])}"><span class="tm">{e(x["time"])}</span> <span class="ic">{e(x["icon"])}</span> '
            f'<a href="/timeline?video={quote(x["variant"])}">{e(x["who"])}</a> <span class="st">{e(x["stage"])}</span> '
            f'<span class="msg">{e(x["message"])}{e(prog)}{e(code)}</span></li>')


def system_health():
    info = read_url()
    beat = None
    try:
        beat = json.loads((DATA / "bot_state.json").read_text()).get("beat_t")
    except (OSError, ValueError):
        pass
    tg = notify.configured()
    return {"tunnel_since": info.get("since"), "tunnel_checked": info.get("checked_at"), "bot_beat": beat, "telegram": "paired" if tg[1] else "token only" if tg[0] else "not set up"}


def render_overview(con):
    o = monitor.overview(con)
    iss = o["open_issues"]
    pub = " · ".join(f"{k}: {v['live']} live, {v['scheduled']} scheduled" for k, v in sorted(o["published"].items())) or "none"
    tiles = [tile("Active projects", o["active_projects"]), tile("In production", o["videos_in_production"], f"of {o['videos_total']} videos"),
             tile("Running now", o["running"], f"+{o['running_stale']} silent >6 h" if o["running_stale"] else None, "run" if o["running"] else ""),
             tile("Waiting approval", o["waiting_approval"], None, "wait" if o["waiting_approval"] else ""),
             tile("YouTube queue", o["queued_uploads_youtube"]), tile("Instagram jobs", o["scheduled_instagram_jobs"] if o["scheduled_instagram_jobs"] is not None else "?"),
             tile("Failed tasks", o["failed_tasks"], None, "bad" if o["failed_tasks"] else ""),
             tile("Open issues", sum(iss.values()), ", ".join(f"{v} {k}" for k, v in sorted(iss.items(), key=lambda kv: SEV_ORDER.get(kv[0], 9))) or None,
                  "bad" if iss.get("critical") else "warn" if iss else ""),
             tile("Telegram pending", o["outbox_pending"])]
    waits = "".join(f"<li>{e(v)} <span class=st>{e(notify.GATE_NAMES.get(g, g))}</span></li>" for v, g in o["waiting_approval_list"][:20])
    h = system_health()
    beat = f"{int((time.time() - h['bot_beat']) / 60)} min ago" if h["bot_beat"] else "never"
    recent = query_events(limit=12)
    body = (f'<div class="tiles">{"".join(tiles)}</div><section><h2>Published</h2><p>{e(pub)}</p><p class=muted>Last live event: {e(o["last_live_event"] or "none")}</p></section>'
            + (f"<section><h2>Waiting for approval</h2><ul class=plain>{waits}</ul><p class=muted>Approvals happen in the Claude chat.</p></section>" if waits else "")
            + f'<section><h2>Latest activity</h2><ul id="feed" class="feed">{"".join(ev_li(x) for x in reversed(recent))}</ul><p><a href="/timeline">Full timeline →</a></p></section>'
            + f'<section><h2>System</h2><p>Telegram: {e(h["telegram"])} · bot heartbeat {e(beat)}<br>Tunnel up since {e(fmt_ts(h["tunnel_since"]))}, last check {e(fmt_ts(h["tunnel_checked"]))}</p></section>')
    return page("Overview", body, "/", live_after=recent[-1]["rowid"] if recent else 0)


def render_projects(con):
    cards = []
    for p in projects_summary(con):
        c = p["counts"]
        nxt = f"{fmt_t(p['next'][0])} · {p['next_variant']} on {p['next'][1]}" if p["next"] else "nothing scheduled"
        cards.append(f'<div class="card"><h2>{e(p["name"])}</h2><p class=muted>{e(p["id"])} · {p["videos"]} episodes · languages {e(", ".join(p["languages"]) or "-")}</p>'
                     f'<div class="tiles small">{tile("Total", p["total"])}{tile("Completed", c["completed"])}{tile("Processing", c["processing"], None, "run" if c["processing"] else "")}'
                     f'{tile("Queued", c["queued"])}{tile("Waiting", c["waiting"], None, "wait" if c["waiting"] else "")}{tile("Failed", c["failed"], None, "bad" if c["failed"] else "")}'
                     f'{tile("In production", c["in production"])}</div><p>Next scheduled: <b>{e(nxt)}</b></p>'
                     f'<p><a href="/queue?project={quote(p["id"])}">Videos →</a></p></div>')
    return page("Projects", "".join(cards) or "<p>No projects.</p>", "/projects")


def _opts(name, values, cur, label):
    o = "".join(f'<option value="{e(v)}"{" selected" if v == cur else ""}>{e(v)}</option>' for v in values)
    return f'<label>{e(label)}<select name="{name}"><option value="">all</option>{o}</select></label>'


def render_queue(con, q):
    vs = variants(con)
    f = {k: (q.get(k) or [""])[0] for k in ("project", "lang", "stage", "status", "date")}
    since = None
    if f["date"]:
        try:
            since = datetime.strptime(f["date"], "%Y-%m-%d").timestamp()
        except ValueError:
            f["date"] = ""
    sel = [v for v in vs if (not f["project"] or v["project_id"] == f["project"]) and (not f["lang"] or v["language"] == f["lang"])
           and (not f["stage"] or v["stage"] == f["stage"]) and (not f["status"] or f["status"] in (v["bucket"], v["status"]))
           and (since is None or (v["t"] or 0) >= since)]
    form = (f'<form class="filters" method="get">{_opts("project", sorted({v["project_id"] for v in vs}), f["project"], "Project")}'
            f'{_opts("lang", sorted({v["language"] for v in vs}), f["lang"], "Language")}{_opts("stage", sorted({v["stage"] for v in vs}), f["stage"], "Stage")}'
            f'{_opts("status", list(BUCKETS) + sorted({v["status"] for v in vs}), f["status"], "Status")}'
            f'<label>Updated since<input type="date" name="date" value="{e(f["date"])}"></label><button>Filter</button> <a href="/queue">reset</a></form>')
    rows = []
    for v in sorted(sel, key=lambda v: -(v["t"] or 0)):
        prog = f' · {v["progress"] * 100:.0f}% (measured)' if v["progress"] is not None and v["status"] == "Running" else ""
        nxt = f' · next: {fmt_t(v["next"][0])} {v["next"][1]}' if v["next"] else ""
        iss = f' · {len(v["issues"])} open issue(s)' if v["issues"] else ""
        rows.append(f'<div class="row"><div><a href="/timeline?video={quote(v["id"])}"><b>{e(v["id"])}</b></a> {badge(v["bucket"])} <span class=muted>{e(v["project"])} Ep{e(v["episode"] or "?")} · {e(v["language"])}</span></div>'
                    f'<div>{e(v["stage"])} — {badge(v["status"])}{e(prog)}</div><div class="muted">{e(v["message"])} · {e(fmt_t(v["t"]))}{e(nxt)}{e(iss)}'
                    f'{" · on " + e(", ".join(v["platforms"])) if v["platforms"] else ""}</div></div>')
    return page("Queue", form + f"<p class=muted>{len(sel)} of {len(vs)} videos</p>" + ("".join(rows) or "<p>No videos match.</p>"), "/queue")


def render_uploads(con):
    last = {}
    for r in con.execute("SELECT variant_id, platform, MAX(t) AS t FROM events WHERE stage='publish' GROUP BY variant_id, platform"):
        last[(r["variant_id"], r["platform"])] = r["t"]
    live = con.execute("SELECT * FROM task_state WHERE stage='publish' AND status='Running' AND progress IS NOT NULL AND t >= ?", (time.time() - 3600,)).fetchall()
    inflight = "".join(f'<div class="row"><b>{e(t["variant_id"])}</b> {e(t["platform"])} <progress max="1" value="{t["progress"]}"></progress> {t["progress"] * 100:.0f}% '
                       f'<span class=muted>{e(scrub(t["message"]))} · {fmt_t(t["t"])}</span></div>' for t in live)
    qrows = []
    for r in con.execute("SELECT * FROM publish_queue ORDER BY CASE status WHEN 'done' THEN 1 ELSE 0 END, priority DESC, id"):
        v = f"{r['content_id']}-{r['lang']}"
        err = f'<div class="err">{e(scrub(r["last_error"]))}</div>' if r["last_error"] else ""
        nt = f" · next try {fmt_ts(r['next_try_at'])}" if r["next_try_at"] else ""
        qrows.append(f'<div class="row"><b>{e(v)}</b> {badge(r["status"])} <span class=muted>publish at {e(fmt_ts(r["publish_at"]))} · attempts {r["attempts"]}{e(nt)} · '
                     f'last activity {e(fmt_t(last.get((v, r["platform"]))))}</span>{err}</div>')
    pubs = {(r["variant_id"], r["platform"]) for r in con.execute("SELECT variant_id, platform FROM publications")}
    jrows = []
    for j in ig_jobs():
        st = "posted" if (j["variant"], "instagram") in pubs else ("dry run" if j["dry_run"] else "scheduled")
        if st == "scheduled" and j.get("t") and j["t"] < time.time():
            st = "overdue"
        jrows.append(f'<div class="row"><b>{e(j["variant"])}</b> {badge(st)} <span class=muted>at {e(fmt_t(j.get("t")) if j.get("t") else j["when"])} · last activity '
                     f'{e(fmt_t(last.get((j["variant"], "instagram"))))} · log {e(j["log"])}</span></div>')
    prow = []
    for r in con.execute("SELECT * FROM publications ORDER BY id DESC LIMIT 40"):
        sched = ts_epoch(r["scheduled_for"])
        st = "scheduled" if sched and sched > time.time() else "live"
        link = f' <a href="{e(r["url"])}" rel="noreferrer" target="_blank">open</a>' if r["url"] and str(r["url"]).startswith("https://") else ""
        prow.append(f'<div class="row"><b>{e(r["variant_id"])}</b> {e(r["platform"])} {badge(st)} <span class=muted>{e(fmt_ts(r["scheduled_for"] or r["published_at"]))}</span>{link}</div>')
    iss = con.execute("SELECT * FROM issues WHERE stage='publish' AND status IN ('open','acknowledged') ORDER BY last_t DESC").fetchall()
    irows = "".join(f'<div class="row">{badge(i["severity"])} <b>{e(i["variant_id"] or "-")}</b> {e(i["platform"])} — {e(i["title"])} (×{i["occurrences"]})<div class=muted>{e(i["suggestion"])} · '
                    f'retry safe: {"yes" if i["retry_safe"] == 1 else "no" if i["retry_safe"] == 0 else "unknown"}</div></div>' for i in iss)
    body = ((f"<section><h2>Uploading now</h2>{inflight}</section>" if inflight else "")
            + (f"<section><h2>Upload problems</h2>{irows}</section>" if irows else "")
            + f"<section><h2>YouTube queue</h2>{''.join(qrows) or '<p>Empty.</p>'}</section>"
            + f"<section><h2>Instagram jobs</h2>{''.join(jrows) or '<p>None scheduled.</p>'}</section>"
            + f"<section><h2>Publications</h2>{''.join(prow) or '<p>None yet.</p>'}</section><p class=muted>Progress bars appear only when the uploader measured progress.</p>")
    return page("Uploads", body, "/uploads", live_after=0)


def render_issues(con, csrf, q):
    show_all = (q.get("all") or [""])[0] == "1"
    rows = monitor.issues(con, only_open=not show_all)
    cards = []
    for r in rows[:200]:
        retry = "yes" if r["retry_safe"] == 1 else "no" if r["retry_safe"] == 0 else "unknown"
        ack = (f'<form method="post" action="/issues/{r["id"]}/ack"><input type="hidden" name="csrf" value="{e(csrf)}"><button>Acknowledge</button></form>'
               if r["status"] == "open" else "")
        logl = f"<div class=muted>Log: {e(rel(r['log_ref']))}</div>" if r["log_ref"] else ""
        res = f"<div class=muted>Resolved {e(fmt_ts(r['resolved_at']))}: {e(scrub(r['resolution']))}</div>" if r["status"] == "resolved" else ""
        cards.append(f'<div class="card sev-{e(r["severity"])}"><div>{badge(r["severity"])} {badge(r["status"])} <b>#{r["id"]} {e(r["title"])}</b></div>'
                     f'<div class=muted>{e(r["variant_id"] or r["content_id"] or r["project_id"] or "workspace")} · {e(r["platform"] or "-")} · {e(r["stage"])} · ×{r["occurrences"]} · last {e(fmt_ts(r["last_seen"]))}</div>'
                     f'<p>{e(r["explanation"])}</p><p><b>What to do:</b> {e(r["suggestion"])}</p><p>Retry safe: <b>{retry}</b></p>'
                     f'<details><summary>Technical detail</summary><pre>{e(scrub(r["technical"])[:2000])}</pre></details>{logl}{res}{ack}</div>')
    toggle = '<a href="/issues">open only</a>' if show_all else '<a href="/issues?all=1">show resolved too</a>'
    return page("Issues", f"<p>{toggle}</p>" + ("".join(cards) or "<p>No open issues.</p>"), "/issues")


def render_timeline(con, q):
    video = (q.get("video") or [""])[0].strip()
    if video and not re.fullmatch(r"C\d{4,}(-[a-z]{2,3})?", video):
        video = ""
    kind = (q.get("kind") or [""])[0]
    rows = query_events(limit=200, video=video or None)
    if kind:
        rows = [x for x in rows if x["kind"] == kind]
    form = (f'<form class="filters" method="get"><label>Video<input name="video" value="{e(video)}" placeholder="C0006-hi"></label>'
            f'{_opts("kind", list(events.KINDS), kind, "Kind")}<button>Show</button> <a href="/timeline">all</a></form>')
    title = f"History of {video}" if video else "Timeline"
    after = max([x["rowid"] for x in rows], default=0)
    return page(title, form + f'<ul id="feed" class="feed">{"".join(ev_li(x) for x in reversed(rows))}</ul>', "/timeline", live_after=after, video=video)


def _num(x):
    if x is None or x == "":
        return "-"
    if isinstance(x, float):
        return f"{x:,.1f}" if x % 1 else f"{int(x):,}"
    return f"{x:,}" if isinstance(x, int) else str(x)


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


def render_analytics(con):
    rows = analytics_rows(con)
    head = "<tr><th>Video</th><th>Platform</th><th>Age</th><th>Views</th><th>Reach</th><th>Likes</th><th>Comments</th><th>Shares</th><th>Saves</th><th>Avg watch s</th></tr>"
    trs = "".join(f'<tr><td><a href="/timeline?video={quote(r["variant"])}">{e(r["variant"])}</a></td><td>{e(r["platform"])}</td><td>{e(r["label"])}</td>'
                  f'<td>{_num(r.get("views"))}</td><td>{_num(r.get("reach"))}</td><td>{_num(r.get("likes"))}</td><td>{_num(r.get("comments"))}</td><td>{_num(r.get("shares"))}</td>'
                  f'<td>{_num(r.get("saves"))}</td><td>{_num(r.get("watch"))}</td></tr>' for r in rows)
    ins = {}
    try:
        ins = json.loads((DATA / "reports" / "latest_insights.json").read_text())
    except (OSError, ValueError):
        pass
    finds = "".join(f'<li>{badge(f.get("tier", "?"))} <b>{e(f.get("id"))}</b> {e(f.get("text"))} <span class=muted>(n={e(f.get("n"))})</span></li>' for f in ins.get("findings", []))
    acts = "".join(f'<li><b>{e(a.get("id"))}</b> {e(a.get("text"))}</li>' for a in ins.get("actions", []))
    nxt, has_job = next_collection()
    body = (f'<p>Next collection: <b>{nxt.strftime("%a %d %b %H:%M")}</b> {"(daily job installed)" if has_job else "(daily job NOT installed)"}</p>'
            f'<section><h2>Latest snapshot per video</h2><div class="scroll"><table>{head}{trs}</table></div>'
            '<p class=muted>YouTube: public counters unless Analytics totals exist. Instagram: lifetime insights; average watch converted from ms. Numbers come straight from the stored snapshots.</p></section>'
            f'<section><h2>Insights {e(ins.get("date", ""))}{" (stale)" if ins.get("stale") else ""}</h2><ul class=plain>{finds or "<li>No insights yet.</li>"}</ul>'
            + (f"<h2>Script actions</h2><ul class=plain>{acts}</ul>" if acts else "") + "</section>")
    return page("Analytics", body, "/analytics")


def offline_html():
    return ("<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Offline · Studio</title>"
            "<link rel=stylesheet href=/static/app.css></head><body><main><h1>Mac unreachable</h1><p>The dashboard runs on the Mac. It is asleep, offline, or the tunnel address changed.</p>"
            "<p>Send <b>/link</b> to the Telegram bot for the current address, then open it here.</p></main></body></html>")


CSS = """:root{--bg:#10151a;--fg:#e8ede9;--mut:#93a09a;--card:#18211d;--line:#2a3832;--acc:#7fd1a8;--bad:#ff7b72;--warn:#f2cc60;--run:#79c0ff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
header{position:sticky;top:0;background:#1d2b24;z-index:5;border-bottom:1px solid var(--line)}.top{display:flex;justify-content:space-between;padding:10px 16px}
nav{display:flex;overflow-x:auto;gap:4px;padding:0 10px 8px}nav a{color:var(--mut);text-decoration:none;padding:6px 10px;border-radius:16px;white-space:nowrap}
nav a.on{background:var(--acc);color:#0b1410}main{padding:12px 16px 40px;max-width:980px;margin:auto}h1{font-size:1.35rem;margin:.3em 0 .6em}h2{font-size:1.05rem;margin:1em 0 .4em}
a{color:var(--acc)}.muted{color:var(--mut);font-size:.9em}.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px}
.tiles.small{grid-template-columns:repeat(auto-fill,minmax(96px,1fr))}.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px}
.tile .v{font-size:1.5rem;font-weight:600}.tile .l{color:var(--mut);font-size:.85em}.tile .s{font-size:.8em;color:var(--mut)}
.tile.bad .v{color:var(--bad)}.tile.warn .v,.tile.wait .v{color:var(--warn)}.tile.run .v{color:var(--run)}
.card,.row{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:8px 0;overflow-wrap:anywhere}
.card.sev-critical{border-left:4px solid var(--bad)}.card.sev-recoverable{border-left:4px solid var(--warn)}
.b{display:inline-block;font-size:.75em;padding:1px 7px;border-radius:9px;background:#2a3832;color:var(--fg)}
.b.critical,.b.failed,.b.needs-attention,.b.overdue{background:#5c1f1b}.b.recoverable,.b.waiting,.b.waiting-for-approval,.b.backoff{background:#5a4a16}
.b.running,.b.processing{background:#173a5c}.b.completed,.b.live,.b.posted,.b.done,.b.resolved{background:#1f4a33}
.feed{list-style:none;padding:0;margin:0}.feed li{padding:6px 0;border-bottom:1px solid var(--line);overflow-wrap:anywhere}.feed .tm{color:var(--mut);font-variant-numeric:tabular-nums}
.ev.k-failed .ic,.ev.k-unknown_outcome .ic{color:var(--bad)}.ev.k-completed .ic{color:var(--acc)}.st{color:var(--mut);font-size:.9em}
.filters{display:flex;flex-wrap:wrap;gap:8px;align-items:end;margin-bottom:8px}.filters label{display:flex;flex-direction:column;font-size:.8em;color:var(--mut)}
select,input,button{font:inherit;background:#0d1215;color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:6px 8px}button{background:var(--acc);color:#0b1410;border:0;cursor:pointer}
.err{color:var(--bad);font-size:.9em}pre{white-space:pre-wrap;font-size:.8em;background:#0d1215;padding:8px;border-radius:8px}
.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:.88em}td,th{padding:5px 6px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}
td:first-child,th:first-child,td:nth-child(2),th:nth-child(2){text-align:left}ul.plain{padding-left:18px}.live{font-size:.8em;color:var(--mut)}.live.on{color:var(--acc)}.live.poll{color:var(--warn)}
.banner{background:var(--warn);text-align:center;padding:8px}.banner a{color:#111;font-weight:600}progress{width:120px}"""

JS = """(function(){var b=document.body,live=document.getElementById('live'),feed=document.getElementById('feed'),banner=document.getElementById('banner');
if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js').catch(function(){});}
if(!b.dataset.live)return;var last=parseInt(b.dataset.after||'0',10),video=b.dataset.video||'',es=null,timer=null,seen=Date.now(),mode='';
function setMode(m,t){mode=m;live.className='live '+m;live.textContent=t;}
function add(x){if(x.rowid<=last)return;last=x.rowid;if(video&&x.variant!==video&&x.who.indexOf(video)!==0)return;
if(feed){var li=document.createElement('li');li.className='ev k-'+x.kind;var s=function(c,t){var e=document.createElement('span');e.className=c;e.textContent=t;li.appendChild(e);li.appendChild(document.createTextNode(' '));};
s('tm',x.time);s('ic',x.icon);var a=document.createElement('a');a.href='/timeline?video='+encodeURIComponent(x.variant);a.textContent=x.who;li.appendChild(a);li.appendChild(document.createTextNode(' '));
s('st',x.stage);s('msg',x.message+(x.progress!=null?' '+Math.round(x.progress*100)+'%':'')+(x.error_code?' ['+x.error_code+']':''));feed.insertBefore(li,feed.firstChild);
while(feed.children.length>300)feed.removeChild(feed.lastChild);}if(!feed||location.pathname!=='/timeline'){banner.hidden=false;}}
function poll(){fetch('/api/events?after='+last,{credentials:'same-origin',cache:'no-store'}).then(function(r){if(r.status===401){setMode('','signed out');return null;}return r.json();})
.then(function(d){if(!d)return;(d.events||[]).forEach(add);setMode('poll','live (polling)');}).catch(function(){setMode('','offline');});}
function startPoll(){if(es){es.close();es=null;}if(!timer){timer=setInterval(poll,10000);poll();}}
function startSSE(){if(!window.EventSource){startPoll();return;}es=new EventSource('/events/stream?after='+last);
es.addEventListener('ev',function(m){seen=Date.now();try{add(JSON.parse(m.data));}catch(e){}setMode('on','live');});
es.addEventListener('ping',function(){seen=Date.now();if(mode!=='on')setMode('on','live');});es.onerror=function(){if(Date.now()-seen>20000)startPoll();};}
setInterval(function(){if(es&&Date.now()-seen>25000)startPoll();},5000);setMode('','connecting');if(b.dataset.sse==='1'){startSSE();}else{startPoll();}})();"""

SW = """const C='ss-shell-v1';const SHELL=['/offline.html','/static/app.css','/static/app.js','/icon-192.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(SHELL)));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))));self.clients.claim();});
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET')return;const u=new URL(r.url);if(u.origin!==location.origin)return;
if(r.mode==='navigate'){e.respondWith(fetch(r).catch(()=>caches.match('/offline.html')));return;}
if(SHELL.includes(u.pathname)){e.respondWith(fetch(r).catch(()=>caches.match(r)));}});"""

MANIFEST = json.dumps({"name": "Shorts Studio", "short_name": "Studio", "start_url": "/", "scope": "/", "display": "standalone", "background_color": "#10151a",
                       "theme_color": "#1d2b24", "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
                                                           {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]})


def png_icon(n):
    bg, fg = (29, 43, 36), (232, 237, 233)
    rows = []
    cx, cy = n * 0.54, n * 0.5
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
            "/static/app.css": ("text/css; charset=utf-8", CSS.encode()), "/static/app.js": ("text/javascript; charset=utf-8", JS.encode()),
            "/sw.js": ("text/javascript; charset=utf-8", SW.encode()), "/manifest.webmanifest": ("application/manifest+json", MANIFEST.encode()),
            "/offline.html": ("text/html; charset=utf-8", offline_html().encode()), "/icon-192.png": ("image/png", png_icon(192)),
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
        body = ('<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Sign in · Studio</title>'
                '<link rel=stylesheet href=/static/app.css></head><body><main><h1>Sign-in needed</h1><p>Open the dashboard link from the Telegram bot '
                '(send <b>/link</b> to the bot to get it again).</p></main></body></html>')
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
            return self.send(303, "", extra={"Location": "/", "Set-Cookie": f"{COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Strict"})
        nonce = self.session()
        api = path.startswith("/api/") or path == "/events/stream"
        routes = {"/": render_overview, "/projects": render_projects, "/analytics": render_analytics}
        if path not in routes and path not in ("/queue", "/uploads", "/issues", "/timeline", "/api/events", "/api/overview", "/events/stream"):
            return self.send(404, "<h1>Not found</h1>")
        if not nonce:
            return self.unauthorized(api)
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
            if path in routes:
                return self.send(200, routes[path](con))
            if path == "/queue":
                return self.send(200, render_queue(con, q))
            if path == "/uploads":
                return self.send(200, render_uploads(con))
            if path == "/issues":
                return self.send(200, render_issues(con, csrf_for(nonce), q))
            if path == "/timeline":
                return self.send(200, render_timeline(con, q))
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
        cookie = f"{COOKIE}={make_session()}; Path=/; Max-Age={SESSION_S}; HttpOnly; Secure; SameSite=Strict"
        log(f"login ok from {ip}")
        return self.send(303, "", extra={"Location": "/", "Set-Cookie": cookie})

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
        con = events.connect()
        try:
            r = con.execute("SELECT status FROM issues WHERE id=?", (int(m.group(1)),)).fetchone()
            if r and r["status"] == "open":
                monitor.resolve_issue(con, int(m.group(1)), "acknowledged on the dashboard", "acknowledged")
        finally:
            con.close()
        return self.send(303, "", extra={"Location": "/issues"})


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
        self.proc = subprocess.Popen([self.binary, "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{self.port}"],
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


def run(port=PORT, tunnel=True):
    rotate_log()
    srv = make_server(port)
    log(f"dashboard on http://127.0.0.1:{port} (tunnel {'on' if tunnel else 'off'})")
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
