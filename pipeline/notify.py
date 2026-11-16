import html
import json
import os
import re
import secrets as pysecrets
import sqlite3
import threading
import time
import uuid
from datetime import datetime

from . import DATA, ROOT, db, events, explain

CONFIG = ROOT / "secrets" / "telegram.json"
PAIR_FILE = DATA / "telegram_pair.json"
API = "https://api.telegram.org"
MAX_LEN = 4000
MIN_GAP_S = 1.05
DIGEST_OVER = 5
DIGEST_WINDOW_S = 60
BACKOFF_S = (15, 30, 60, 120, 300, 900, 1800, 3600)
MAX_ATTEMPTS = 10
STALE_SENDING_S = 300
TOKEN_RX = re.compile(r"(?<![0-9])\d{6,12}:[A-Za-z0-9_-]{30,}")
LANGS = {"en": "English", "hi": "Hindi", "gu": "Gujarati", "te": "Telugu", "mr": "Marathi", "ta": "Tamil", "kn": "Kannada", "ml": "Malayalam", "bn": "Bengali",
         "pa": "Punjabi", "or": "Odia", "ur": "Urdu", "es": "Spanish", "fr": "French", "de": "German", "pt": "Portuguese", "ja": "Japanese"}
GATE_NAMES = {"gate:script": "G1 script", "gate:final": "G2 final video", "gate:publish:youtube": "G3 YouTube publish", "gate:publish:instagram": "G3 Instagram publish"}
PLATFORMS = {"youtube": "YouTube", "instagram": "Instagram"}


class TelegramError(Exception):
    def __init__(self, status, description, retry_after=None):
        super().__init__(f"{status}: {description}")
        self.status, self.description, self.retry_after = status, description, retry_after

    @property
    def transient(self):
        return self.status is None or self.status == 429 or self.status >= 500


def scrub(text, token=None):
    s = "" if text is None else str(text)
    if token:
        s = s.replace(token, "<redacted>")
    return explain.redact(TOKEN_RX.sub("<redacted-telegram-token>", s))


def write_secret(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(path.parent, 0o700)
    except OSError:
        pass
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        json.dump(data, fh, indent=2)
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def load_config():
    try:
        cfg = json.loads(CONFIG.read_text())
        return cfg if isinstance(cfg, dict) else {}
    except (OSError, ValueError):
        return {}


def save_config(cfg):
    write_secret(CONFIG, cfg)


def configured(cfg=None):
    cfg = load_config() if cfg is None else cfg
    return bool(cfg.get("bot_token")), bool(cfg.get("bot_token") and cfg.get("owner_chat_id"))


def _requests_http(url, payload, timeout):
    import requests

    r = requests.post(url, json=payload, timeout=timeout)
    try:
        body = r.json()
    except ValueError:
        body = {"ok": False, "description": f"non-JSON reply (HTTP {r.status_code})"}
    return r.status_code, body


class Telegram:
    def __init__(self, token, http=None, sleep=time.sleep, clock=time.monotonic):
        self.token, self.http, self.sleep, self.clock = token, http or _requests_http, sleep, clock
        self._lock = threading.Lock()
        self._last_send = 0.0

    def call(self, method, http_timeout=30, **params):
        payload = {k: v for k, v in params.items() if v is not None}
        try:
            status, body = self.http(f"{API}/bot{self.token}/{method}", payload, http_timeout)
        except Exception as e:
            raise TelegramError(None, scrub(f"network: {type(e).__name__}: {e}", self.token)) from None
        if isinstance(body, dict) and body.get("ok"):
            return body.get("result")
        body = body if isinstance(body, dict) else {}
        retry = (body.get("parameters") or {}).get("retry_after")
        raise TelegramError(body.get("error_code") or status, scrub(body.get("description") or f"HTTP {status}", self.token), retry)

    def send(self, chat_id, text, parse_mode="HTML", **extra):
        with self._lock:
            wait = MIN_GAP_S - (self.clock() - self._last_send)
            if wait > 0:
                self.sleep(wait)
            try:
                return self.call("sendMessage", chat_id=chat_id, text=text[:4096], parse_mode=parse_mode,
                                 link_preview_options={"is_disabled": True}, **extra)
            finally:
                self._last_send = self.clock()


def esc(s):
    return html.escape("" if s is None else str(s), quote=False)


def _con():
    con = events.connect()
    have = {r[1] for r in con.execute("PRAGMA table_info(outbox)")}
    if "message_id" not in have:
        try:
            con.execute("ALTER TABLE outbox ADD COLUMN message_id INTEGER")
        except sqlite3.OperationalError:
            pass
    return con


def _at(ts):
    try:
        d = datetime.fromisoformat(ts) if isinstance(ts, str) else datetime.fromtimestamp(float(ts))
        d = d.astimezone() if d.tzinfo else d
    except (TypeError, ValueError):
        return esc(ts)
    t = d.strftime("%I:%M %p").lstrip("0")
    return t if d.date() == datetime.now().date() else f"{d.strftime('%b')} {d.day}, {t}"


def _project_name(con, project_id):
    if not project_id:
        return None
    try:
        r = con.execute("SELECT name FROM projects WHERE id=?", (project_id,)).fetchone()
    except sqlite3.OperationalError:
        r = None
    name = r["name"] if r else project_id
    head = re.split(r"\s+[—–-]\s+", name.strip())[0]
    return head.title() if head.isupper() else head


def subject(con, p):
    cid, vid = p.get("content_id"), p.get("variant_id")
    lang = events.split_variant(vid)[1] if vid else None
    ep = None
    if cid:
        try:
            r = con.execute("SELECT episode FROM contents WHERE id=?", (cid,)).fetchone()
            ep = f"Ep{int(r['episode']):02d}" if r and r["episode"] is not None else None
        except (sqlite3.OperationalError, TypeError, ValueError):
            ep = None
    parts = [x for x in (_project_name(con, p.get("project_id")), ep or cid) if x]
    s = " ".join(parts) or (vid or "Workspace")
    if lang:
        s += f" ({LANGS.get(lang, lang)})"
    return s


def _video(p):
    vid = p.get("variant_id")
    if vid:
        cid, lang = events.split_variant(vid)
        return f"{cid}-{lang.upper()}" if cid else vid
    return p.get("content_id")


def _rel(path):
    if not path:
        return None
    s = str(path)
    root = str(ROOT) + os.sep
    if s.startswith(root):
        return s[len(root):]
    return os.path.basename(s) if os.path.isabs(s) else s


def headline(stage, platform, kind, severity):
    plat = PLATFORMS.get(platform or "", platform)
    if kind == "unknown_outcome":
        return "❓", f"{plat + ' post' if plat else 'Request'} outcome unknown"
    if kind == "queued":
        return "⏳", "Upload delayed"
    if stage == "publish":
        noun = "Instagram post" if platform == "instagram" else "Upload"
    elif stage in ("video_qa", "voice_qa", "qa"):
        noun = "QA"
    elif stage.startswith("gate:"):
        return "✋", f"Blocked at {GATE_NAMES.get(stage, stage)}"
    else:
        noun = stage.replace("_", " ").capitalize()
    icon = "⚠️" if kind == "warning" or severity == "warning" else "❌"
    return icon, f"{noun} failed"


def format_issue(con, p):
    iss = con.execute("SELECT * FROM issues WHERE id=?", (p["issue_id"],)).fetchone() if p.get("issue_id") else None
    ev = con.execute("SELECT * FROM events WHERE id=?", (p.get("event_id"),)).fetchone() if p.get("event_id") else None
    iss = dict(iss) if iss else {}
    stage = p.get("stage") or iss.get("stage") or "general"
    icon, head = headline(stage, p.get("platform"), p.get("kind"), p.get("severity") or iss.get("severity"))
    occ = iss.get("occurrences") or 1
    if occ > 1:
        head += f" ({occ}×)"
    details = (ev["error_raw"] if ev and ev["error_raw"] else None) or iss.get("technical") or (ev["message"] if ev else "") or p.get("text") or ""
    details = re.sub(r"\s+", " ", scrub(details)).strip()
    if len(details) > 300:
        details = details[:297] + "…"
    rs = iss.get("retry_safe")
    lines = [
        f"{icon} {esc(head)} — {esc(subject(con, p))}",
        f"Reason: {esc(iss.get('title') or p.get('title'))}",
        f"Details: {esc(details or '-')}",
        f"Action: {esc(iss.get('suggestion') or '-')}",
        f"Retry safe: {'yes' if rs == 1 else 'no' if rs == 0 else 'unknown'}",
    ]
    if _video(p):
        lines.append(f"Video: {esc(_video(p))}")
    lines.append(f"At: {_at(p.get('ts'))}")
    log = _rel((ev["log_ref"] if ev else None) or iss.get("log_ref"))
    if log:
        lines.append(f"Log: {esc(log)}")
    return "\n".join(lines)


def _body(p):
    text = p.get("text") or ""
    return text.split(": ", 1)[1] if ": " in text else text


def format_payload(con, p):
    if p.get("html"):
        return p["html"]
    title, kind = p.get("title") or "", p.get("kind")
    tail = []
    if _video(p):
        tail.append(f"Video: {esc(_video(p))}")
    tail.append(f"At: {_at(p.get('ts'))}")
    if title.startswith("Recovered: "):
        return "\n".join([f"✅ Recovered — {esc(subject(con, p))}", f"Was: {esc(title[len('Recovered: '):])}", esc(_body(p))] + tail)
    if p.get("issue_id") and p.get("severity") != "info":
        return format_issue(con, p)
    if kind == "waiting_approval":
        gate = GATE_NAMES.get(p.get("stage"), p.get("stage"))
        return "\n".join([f"📝 Approval needed ({esc(gate)}) — {esc(subject(con, p))}", esc(_body(p)), "Approve or reject in the Claude chat."] + tail)
    if kind == "completed" and p.get("stage") == "publish":
        what = "Posted on Instagram" if p.get("platform") == "instagram" else "Uploaded to YouTube"
        return "\n".join([f"✅ {what} — {esc(subject(con, p))}", esc(_body(p))] + tail)
    if kind == "rejected":
        return "\n".join([f"✋ {esc(title)} — {esc(subject(con, p))}", esc(_body(p))] + tail)
    if title == "Mac online":
        return f"💻 Mac online — {esc(p.get('text'))}\nAt: {_at(p.get('ts'))}"
    return "\n".join([f"ℹ️ {esc(title)} — {esc(subject(con, p))}", esc(_body(p))] + tail)


def digest_line(con, p):
    msg = format_payload(con, p)
    first = msg.split("\n", 1)[0]
    if p.get("issue_id") and p.get("severity") != "info":
        iss = con.execute("SELECT title FROM issues WHERE id=?", (p["issue_id"],)).fetchone()
        if iss:
            first += f": {esc(iss['title'])}"
    return f"• {first} ({_at(p.get('ts'))})"


def format_digest(con, payloads):
    lines = [f"📬 {len(payloads)} updates"]
    for p in payloads:
        lines.append(digest_line(con, p))
    lines.append("Details: /issues, /timeline or the dashboard.")
    out = "\n".join(lines)
    if len(out) > MAX_LEN:
        out = out[:MAX_LEN - 40].rsplit("\n", 1)[0] + "\n… (more in /timeline)"
    return out


def enqueue_local(title, html_text, secret=False, kind="local"):
    con = _con()
    try:
        payload = {"title": title, "html": html_text, "kind": kind, "secret": bool(secret), "ts": db.now(), "severity": "info"}
        con.execute("INSERT INTO outbox (event_id, issue_id, channel, payload, status, attempts, created_at) VALUES (?,?,?,?,?,0,?)",
                    (f"local:{uuid.uuid4()}", None, "telegram", json.dumps(payload, ensure_ascii=False), "pending", db.now()))
    finally:
        con.close()


def _t(created_at):
    try:
        return datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S%z").timestamp()
    except (TypeError, ValueError):
        return 0.0


def _mark_sent(con, ids, message_id, note=None):
    for i in ids:
        r = con.execute("SELECT payload FROM outbox WHERE id=?", (i,)).fetchone()
        payload = r["payload"] if r else None
        try:
            p = json.loads(payload or "{}")
            if p.get("secret"):
                payload = json.dumps({**p, "html": "(secret link removed after sending)"}, ensure_ascii=False)
        except ValueError:
            pass
        con.execute("UPDATE outbox SET status='sent', sent_at=?, message_id=?, last_error=?, payload=? WHERE id=? AND status='sending'",
                    (db.now(), message_id, note, payload, i))


def _mark_retry(con, ids, err, now):
    for i in ids:
        r = con.execute("SELECT attempts FROM outbox WHERE id=?", (i,)).fetchone()
        n = (r["attempts"] if r else 0) + 1
        if err.transient and n < MAX_ATTEMPTS:
            delay = max(err.retry_after or 0, BACKOFF_S[min(n - 1, len(BACKOFF_S) - 1)])
            con.execute("UPDATE outbox SET status='pending', attempts=?, next_try_at=?, last_error=? WHERE id=?", (n, f"{now + delay:.1f}", str(err)[:500], i))
        else:
            con.execute("UPDATE outbox SET status='failed', attempts=?, next_try_at=NULL, last_error=? WHERE id=?", (n, str(err)[:500], i))


def _claim(con, ids):
    got = []
    for i in ids:
        if con.execute("UPDATE outbox SET status='sending', next_try_at=? WHERE id=? AND status='pending'", (f"{time.time():.1f}", i)).rowcount == 1:
            got.append(i)
    return got


def _send(con, api, chat_id, ids, text, now, log):
    ids = _claim(con, ids)
    if not ids:
        return 0
    try:
        try:
            res = api.send(chat_id, text)
        except TelegramError as e:
            if e.status == 400 and "parse" in (e.description or "").lower():
                res = api.send(chat_id, html.unescape(re.sub(r"<[^>]+>", "", text)), parse_mode=None)
            else:
                raise
        _mark_sent(con, ids, (res or {}).get("message_id"), "digest" if len(ids) > 1 else None)
        return len(ids)
    except TelegramError as e:
        _mark_retry(con, ids, e, now)
        log(f"outbox {ids}: send failed ({e}); {'will retry' if e.transient else 'giving up'}")
        if e.status == 429 or e.status in (401, 404):
            raise
        return 0


def drain(api, chat_id, now=None, log=print, limit=50):
    now = time.time() if now is None else now
    con = _con()
    sent = 0
    try:
        con.execute("UPDATE outbox SET status='pending' WHERE status='sending' AND CAST(COALESCE(next_try_at,'0') AS REAL) < ?", (now - STALE_SENDING_S,))
        rows = [r for r in con.execute("SELECT * FROM outbox WHERE status='pending' AND channel='telegram' ORDER BY id").fetchall()
                if float(r["next_try_at"] or 0) <= now][:limit]
        if not rows:
            return 0
        items = []
        for r in rows:
            try:
                items.append((r["id"], json.loads(r["payload"])))
            except ValueError:
                con.execute("UPDATE outbox SET status='failed', last_error='bad payload' WHERE id=?", (r["id"],))
        created = {r["id"]: _t(r["created_at"]) for r in rows}
        recent = [i for i in items if now - created.get(i[0], 0) <= DIGEST_WINDOW_S]
        burst = len(recent) > DIGEST_OVER or len(items) > DIGEST_OVER
        try:
            if burst:
                single = [i for i in items if i[1].get("kind") == "local" or (i[1].get("issue_id") and i[1].get("severity") == "critical")]
                rest = [i for i in items if i not in single]
                for oid, p in single:
                    sent += _send(con, api, chat_id, [oid], format_payload(con, p), now, log)
                if rest:
                    sent += _send(con, api, chat_id, [oid for oid, _ in rest], format_digest(con, [p for _, p in rest]), now, log)
            else:
                for oid, p in items:
                    sent += _send(con, api, chat_id, [oid], format_payload(con, p), now, log)
        except TelegramError:
            pass
        return sent
    finally:
        con.close()


def open_pair_window(minutes=10):
    code = f"{pysecrets.randbelow(10 ** 6):06d}"
    PAIR_FILE.parent.mkdir(parents=True, exist_ok=True)
    w = {"code": code, "opened_t": time.time(), "expires_t": time.time() + minutes * 60}
    PAIR_FILE.write_text(json.dumps(w))
    os.chmod(PAIR_FILE, 0o600)
    return w


def pair_window():
    try:
        w = json.loads(PAIR_FILE.read_text())
    except (OSError, ValueError):
        return None
    if w.get("expires_t", 0) < time.time():
        return None
    return w


def close_pair_window():
    try:
        PAIR_FILE.unlink()
    except OSError:
        pass


def try_pair(update, window, cfg):
    msg = update.get("message") or {}
    chat, frm = msg.get("chat") or {}, msg.get("from") or {}
    if not window or chat.get("type") != "private" or not frm.get("id") or frm.get("is_bot"):
        return False
    if msg.get("date", 0) < int(window["opened_t"]) - 5:
        return False
    text = (msg.get("text") or "").strip()
    if text not in (window["code"], f"/pair {window['code']}", f"/start {window['code']}"):
        return False
    cfg.update({"owner_chat_id": chat["id"], "owner_user_id": frm["id"], "paired_at": db.now()})
    save_config(cfg)
    close_pair_window()
    return True


def is_owner(update, cfg):
    msg = update.get("message") or update.get("edited_message") or {}
    chat, frm = msg.get("chat") or {}, msg.get("from") or {}
    return (bool(cfg.get("owner_chat_id")) and chat.get("type") == "private" and chat.get("id") == cfg.get("owner_chat_id")
            and frm.get("id") == cfg.get("owner_user_id", cfg.get("owner_chat_id")))


def setup(token):
    token = (token or "").strip()
    if not TOKEN_RX.fullmatch(token):
        raise ValueError("that does not look like a bot token from @BotFather (digits:letters)")
    me = Telegram(token).call("getMe")
    cfg = load_config()
    if cfg.get("bot_token") != token:
        cfg = {"bot_token": token}
    cfg["bot_username"] = me.get("username")
    cfg["bot_id"] = me.get("id")
    save_config(cfg)
    return me


def pair_cli(timeout_min=10, bot_running=False, log=print):
    cfg = load_config()
    if not cfg.get("bot_token"):
        raise SystemExit("No bot token yet. Run: python -m pipeline telegram setup --token-from-stdin")
    w = open_pair_window(timeout_min)
    log(f"Open Telegram, find @{cfg.get('bot_username') or 'your bot'} and send:  /pair {w['code']}")
    log(f"Waiting up to {timeout_min} min …")
    if bot_running:
        while time.time() < w["expires_t"]:
            if load_config().get("owner_chat_id"):
                return load_config()
            time.sleep(2)
        close_pair_window()
        raise SystemExit("Timed out; nothing paired.")
    api = Telegram(cfg["bot_token"])
    offset = None
    try:
        last = api.call("getUpdates", offset=-1, timeout=0)
        offset = last[-1]["update_id"] + 1 if last else None
    except TelegramError:
        pass
    while time.time() < w["expires_t"]:
        try:
            ups = poll(api, offset)
        except TelegramError as e:
            log(f"poll error: {e}")
            time.sleep(5)
            continue
        for u in ups:
            offset = u["update_id"] + 1
            if try_pair(u, w, cfg):
                api.call("getUpdates", offset=offset, timeout=0)
                api.send(cfg["owner_chat_id"], "✅ Paired. This chat now receives shorts-studio notifications. Send /help for commands.")
                return cfg
    close_pair_window()
    raise SystemExit("Timed out; nothing paired.")


def poll(api, offset, wait=50):
    return api.call("getUpdates", http_timeout=wait + 15, offset=offset, timeout=wait, allowed_updates=["message"]) or []


def counts():
    con = _con()
    try:
        return {r[0]: r[1] for r in con.execute("SELECT status, COUNT(*) FROM outbox GROUP BY status")}
    finally:
        con.close()
