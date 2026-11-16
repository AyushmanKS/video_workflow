import json
import re
import sqlite3
import threading
import time
import uuid
from datetime import datetime

from . import db, explain

KINDS = ("started", "progress", "completed", "failed", "unknown_outcome", "waiting_approval", "approved", "rejected", "queued", "info", "warning")
STATUSES = ("Not Started", "Queued", "Running", "Waiting for Approval", "Completed", "Failed", "Paused", "Cancelled", "Needs Attention")
DEFAULT_STATUS = {"started": "Running", "progress": "Running", "completed": "Completed", "failed": "Failed", "unknown_outcome": "Needs Attention",
                  "waiting_approval": "Waiting for Approval", "approved": "Completed", "rejected": "Needs Attention", "queued": "Queued"}
WORKFLOW = ["research", "strategy", "script", "gate:script", "voice", "voice_takes", "voice_qa", "images", "render", "video_qa", "gate:final",
            "metadata", "schedule", "gate:publish:youtube", "gate:publish:instagram", "publish", "ig_dry_run", "analytics"]
ISSUE_KINDS = ("failed", "unknown_outcome", "warning", "queued", "rejected")
RESOLVE_KINDS = ("completed", "approved")
SEV_RANK = {s: i for i, s in enumerate(explain.SEVERITIES)}
ESCALATE_AT = (3, 10, 50)
ONLINE_GAP_S = 30 * 60
BUSY_MS = 5000
CONTEXT_KEYS = ("project_id", "content_id", "variant_id", "platform", "stage", "log_ref")
VARIANT_RX = re.compile(r"^(C\d{4,})-([a-z]{2,3})$")

_lock = threading.RLock()
_ready = set()
_workflows = {}
_context = {}
_flags = set()
_local = threading.local()


def fallback_path():
    return db.DATA / "logs" / "events-fallback.log"


def _fallback(reason, payload):
    try:
        p = fallback_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps({"at": db.now(), "reason": explain.redact(str(reason))[:800], "event": payload}, ensure_ascii=False, default=str)
        with open(p, "a") as fh:
            fh.write(explain.redact(line) + "\n")
    except Exception:
        pass


def set_context(**kw):
    for k, v in kw.items():
        if k in CONTEXT_KEYS:
            if v is None:
                _context.pop(k, None)
            else:
                _context[k] = v


def add_flag(flag):
    _flags.add(flag)


def clear_context():
    _context.clear()
    _flags.clear()


def ensure(con):
    key = str(db.DB_PATH)
    if key in _ready:
        return
    try:
        mode = con.execute("PRAGMA journal_mode").fetchone()[0]
        if str(mode).lower() != "wal":
            con.execute("PRAGMA journal_mode=WAL")
    except sqlite3.OperationalError:
        pass
    con.executescript(db.EVENT_SCHEMA)
    _ready.add(key)


def connect():
    con = sqlite3.connect(db.DB_PATH, timeout=BUSY_MS / 1000, isolation_level=None)
    con.row_factory = sqlite3.Row
    con.execute(f"PRAGMA busy_timeout={int(BUSY_MS)}")
    ensure(con)
    return con


def parse_ts(ts=None):
    if ts is None:
        t = time.time()
    elif isinstance(ts, (int, float)):
        t = float(ts)
    else:
        d = datetime.fromisoformat(str(ts).strip().replace("Z", "+00:00"))
        if d.tzinfo is None:
            d = d.astimezone()
        t = d.timestamp()
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(t)), t


def split_variant(variant_id):
    m = VARIANT_RX.match(variant_id or "")
    return (m.group(1), m.group(2)) if m else (None, None)


def _project_for(con, content_id):
    if not content_id:
        return None
    try:
        r = con.execute("SELECT project_id FROM contents WHERE id=?", (content_id,)).fetchone()
        return r["project_id"] if r else None
    except sqlite3.OperationalError:
        return None


def _workflow(con, project_id):
    if project_id in _workflows:
        return _workflows[project_id]
    wf = WORKFLOW
    try:
        r = con.execute("SELECT config FROM projects WHERE id=?", (project_id,)).fetchone() if project_id else None
        cfg = json.loads(r["config"] or "{}") if r else {}
        if isinstance(cfg.get("workflow"), list) and cfg["workflow"]:
            wf = cfg["workflow"]
    except (sqlite3.OperationalError, ValueError, TypeError):
        pass
    _workflows[project_id] = wf
    return wf


def _build(kind, stage, message, status, project_id, content_id, variant_id, platform, progress, detail, error, error_code, retry_safe, log_ref, run_id, ts, backfilled, context, severity):
    ctx = {k: v for k, v in _context.items()}
    given = {"project_id": project_id, "content_id": content_id, "variant_id": variant_id, "platform": platform, "stage": stage, "log_ref": log_ref}
    for k, v in given.items():
        if v is not None:
            ctx[k] = v
    variant_id = ctx.get("variant_id")
    content_id = ctx.get("content_id") or split_variant(variant_id)[0]
    kind = kind if kind in KINDS else "info"
    raw = explain.redact(error if isinstance(error, str) else repr(error)) if error is not None else None
    exp = None
    if raw:
        exp = explain.explain(raw, set(context or ()) | _flags)
        if error_code and error_code != exp["code"]:
            exp = {**explain.by_code(error_code), "raw": raw}
    elif error_code:
        exp = explain.by_code(error_code)
    if exp:
        error_code = error_code or exp["code"]
        if retry_safe is None:
            retry_safe = exp.get("retry_safe")
        if exp.get("kind") == "unknown_outcome" and kind == "failed":
            kind = "unknown_outcome"
        severity = severity or exp.get("severity")
    if status not in STATUSES:
        status = DEFAULT_STATUS.get(kind)
        if kind == "failed" and severity == "critical":
            status = "Needs Attention"
    if isinstance(progress, bool) or not isinstance(progress, (int, float)) or not 0 <= progress <= 1:
        progress = None
    d = dict(detail or {})
    if backfilled:
        d["backfilled"] = True
    if exp:
        d.setdefault("explain", {k: exp.get(k) for k in ("title", "severity")})
    ts_s, t = parse_ts(ts)
    return {
        "id": str(uuid.uuid4()), "ts": ts_s, "t": t, "project_id": ctx.get("project_id"), "content_id": content_id, "variant_id": variant_id,
        "platform": ctx.get("platform"), "stage": ctx.get("stage") or "general", "kind": kind, "status": status, "progress": progress,
        "message": explain.redact(message or "")[:1000], "detail": explain.redact(json.dumps(d, ensure_ascii=False, default=str)) if d else None,
        "error_code": error_code, "error_raw": raw[:8000] if raw else None, "retry_safe": None if retry_safe is None else int(bool(retry_safe)),
        "log_ref": ctx.get("log_ref"), "run_id": run_id, "_backfilled": bool(backfilled), "_severity": severity, "_exp": exp,
    }


EVENT_COLS = ("id", "ts", "t", "project_id", "content_id", "variant_id", "platform", "stage", "kind", "status", "progress", "message", "detail",
              "error_code", "error_raw", "retry_safe", "log_ref", "run_id")


def _insert(con, ev):
    con.execute(f"INSERT INTO events ({', '.join(EVENT_COLS)}) VALUES ({', '.join('?' for _ in EVENT_COLS)})", [ev[c] for c in EVENT_COLS])


def emit(kind, stage=None, message="", *, status=None, project_id=None, content_id=None, variant_id=None, platform=None, progress=None, detail=None,
         error=None, error_code=None, retry_safe=None, log_ref=None, run_id=None, ts=None, backfilled=False, context=None, severity=None):
    if getattr(_local, "busy", False):
        return None
    _local.busy = True
    ev = None
    try:
        ev = _build(kind, stage, message, status, project_id, content_id, variant_id, platform, progress, detail, error, error_code, retry_safe,
                    log_ref, run_id, ts, backfilled, context, severity)
        with _lock:
            return _persist(ev)
    except Exception as e:
        _fallback(f"{type(e).__name__}: {e}", {k: v for k, v in (ev or {"kind": kind, "stage": stage, "message": message, "variant_id": variant_id}).items()
                                                 if not str(k).startswith("_")})
        return None
    finally:
        _local.busy = False


def _persist(ev):
    con = connect()
    try:
        online = None
        con.execute("BEGIN IMMEDIATE")
        try:
            if ev["project_id"] is None:
                ev["project_id"] = _project_for(con, ev["content_id"])
            if not ev["_backfilled"]:
                last = con.execute("SELECT MAX(t) FROM events").fetchone()[0]
                if last is None or ev["t"] - last > ONLINE_GAP_S:
                    gap = None if last is None else round((ev["t"] - last) / 60)
                    online = _build("info", "system", "Mac online" + (f" (first activity after {gap} min)" if gap is not None else " (first event)"),
                                    None, None, None, None, None, None, {"mac_online": True, "gap_min": gap}, None, None, None, None, None,
                                    ev["t"] - 0.001, False, None, None)
                    _insert(con, online)
            _insert(con, ev)
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
        for e in ([online] if online else []) + [ev]:
            info = _step(con, "state", _derive, e)
            if not e["_backfilled"]:
                _step(con, "outbox", _enqueue, e, info or {})
        return ev["id"]
    finally:
        con.close()


def _step(con, name, fn, *args):
    try:
        con.execute("BEGIN IMMEDIATE")
        out = fn(con, *args)
        con.execute("COMMIT")
        return out
    except Exception as e:
        try:
            con.execute("ROLLBACK")
        except Exception:
            pass
        _fallback(f"{name}: {type(e).__name__}: {e}", {"event_id": args[0]["id"], "kind": args[0]["kind"], "stage": args[0]["stage"]})
        return None


def task_key(ev):
    scope = ev.get("variant_id") or ev.get("content_id") or ev.get("project_id") or "-"
    return f"{scope}|{ev['stage']}|{ev.get('platform') or '-'}"


def issue_key(ev):
    scope = ev.get("variant_id") or ev.get("content_id") or ev.get("project_id") or "workspace"
    return f"{scope}|{ev['stage']}|{ev.get('platform') or '-'}|{ev['error_code']}"


def _derive(con, ev):
    info = {"prev_status": None, "issue": None, "issue_action": None, "issue_changed": False, "resolved": []}
    key = task_key(ev)
    prev = con.execute("SELECT * FROM task_state WHERE task_key=?", (key,)).fetchone()
    info["prev_status"] = prev["status"] if prev else None
    if ev["status"] and not (prev and prev["t"] > ev["t"]):
        wf = _workflow(con, ev["project_id"])
        order = wf.index(ev["stage"]) if ev["stage"] in wf else None
        started = ev["ts"] if ev["kind"] == "started" else (prev["started_at"] if prev else None)
        prog = ev["progress"] if ev["kind"] == "progress" else None
        con.execute("INSERT INTO task_state (task_key, project_id, content_id, variant_id, stage, platform, stage_order, status, kind, progress, message, error_code, last_event_id, started_at, updated_at, t) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(task_key) DO UPDATE SET project_id=excluded.project_id, stage_order=excluded.stage_order, status=excluded.status, "
                    "kind=excluded.kind, progress=excluded.progress, message=excluded.message, error_code=excluded.error_code, last_event_id=excluded.last_event_id, "
                    "started_at=excluded.started_at, updated_at=excluded.updated_at, t=excluded.t",
                    (key, ev["project_id"], ev["content_id"], ev["variant_id"], ev["stage"], ev["platform"], order, ev["status"], ev["kind"], prog, ev["message"],
                     ev["error_code"], ev["id"], started, ev["ts"], ev["t"]))
    sev = ev["_severity"]
    if ev["error_code"] and ev["kind"] in ISSUE_KINDS and sev and sev != "info":
        exp = ev["_exp"] or explain.by_code(ev["error_code"])
        dk = issue_key(ev)
        cur = con.execute("SELECT * FROM issues WHERE dedupe_key=?", (dk,)).fetchone()
        technical = ev["error_raw"] or ev["message"]
        if cur is None:
            c = con.execute("INSERT INTO issues (dedupe_key, severity, project_id, content_id, variant_id, platform, stage, error_code, last_kind, title, explanation, technical, suggestion, retry_safe, log_ref, first_seen, last_seen, last_t, occurrences, status, last_event_id) "
                            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,'open',?)",
                            (dk, sev, ev["project_id"], ev["content_id"], ev["variant_id"], ev["platform"], ev["stage"], ev["error_code"], ev["kind"], exp.get("title"),
                             exp.get("explanation"), technical, exp.get("suggestion"), ev["retry_safe"], ev["log_ref"], ev["ts"], ev["ts"], ev["t"], ev["id"]))
            info["issue"], info["issue_action"] = c.lastrowid, "opened"
        else:
            newer = ev["t"] >= (cur["last_t"] or 0)
            occ = cur["occurrences"] + 1
            if cur["status"] == "resolved" and newer:
                status, action, resolved_at = "open", "reopened", None
            else:
                status, action, resolved_at = cur["status"], "updated", cur["resolved_at"]
            changed = cur["last_kind"] != ev["kind"] or cur["severity"] != sev or occ in ESCALATE_AT
            con.execute("UPDATE issues SET severity=?, last_kind=?, technical=?, retry_safe=?, log_ref=COALESCE(?, log_ref), last_seen=?, last_t=?, occurrences=?, status=?, resolved_at=?, "
                        "resolution=CASE WHEN ?='open' THEN NULL ELSE resolution END, last_event_id=? WHERE id=?",
                        (sev if newer else cur["severity"], ev["kind"] if newer else cur["last_kind"], technical if newer else cur["technical"], ev["retry_safe"] if newer else cur["retry_safe"],
                         ev["log_ref"], ev["ts"] if newer else cur["last_seen"], max(ev["t"], cur["last_t"] or 0), occ, status, resolved_at, status, ev["id"] if newer else cur["last_event_id"], cur["id"]))
            info["issue"], info["issue_action"], info["issue_changed"] = cur["id"], action, changed and newer
    if ev["kind"] in RESOLVE_KINDS:
        rows = con.execute("SELECT * FROM issues WHERE status IN ('open','acknowledged') AND stage=? AND COALESCE(variant_id,'')=? AND COALESCE(content_id,'')=? AND COALESCE(platform,'')=? "
                           "AND COALESCE(last_t,0) <= ?", (ev["stage"], ev["variant_id"] or "", ev["content_id"] or "", ev["platform"] or "", ev["t"])).fetchall()
        for r in rows:
            con.execute("UPDATE issues SET status='resolved', resolved_at=?, resolution=? WHERE id=?", (ev["ts"], f"resolved by {ev['kind']} event {ev['id']}: {ev['message'][:200]}", r["id"]))
            info["resolved"].append(dict(r))
    if ev["kind"] == "approved" and ev["variant_id"] and (ev["stage"] or "").startswith("gate:publish"):
        plat = ev["stage"].split(":")[2] if ev["stage"].count(":") >= 2 else (ev["platform"] or "")
        rows = con.execute("SELECT * FROM issues WHERE status IN ('open','acknowledged') AND stage='publish' AND error_code='gate_refused' AND variant_id=? "
                           "AND (?='' OR COALESCE(platform,'')='' OR platform=?) AND COALESCE(last_t,0) <= ?", (ev["variant_id"], plat, plat, ev["t"])).fetchall()
        for r in rows:
            con.execute("UPDATE issues SET status='resolved', resolved_at=?, resolution=? WHERE id=?", (ev["ts"], f"resolved by a new posting approval (event {ev['id']})", r["id"]))
            info["resolved"].append(dict(r))
    return info


def _payload(ev, title, text, severity, issue_id=None):
    return json.dumps({"title": title, "text": explain.redact(text)[:1500], "severity": severity, "kind": ev["kind"], "project_id": ev["project_id"], "content_id": ev["content_id"],
                       "variant_id": ev["variant_id"], "stage": ev["stage"], "platform": ev["platform"], "issue_id": issue_id, "event_id": ev["id"], "ts": ev["ts"]}, ensure_ascii=False)


def _who(ev):
    return " ".join(x for x in (ev["variant_id"] or ev["content_id"] or ev["project_id"] or "", ev["platform"] or "", ev["stage"]) if x)


def _enqueue(con, ev, info):
    rows = []
    if info.get("issue"):
        iss = con.execute("SELECT * FROM issues WHERE id=?", (info["issue"],)).fetchone()
        text = f"{_who(ev)}: {iss['explanation'] or ''}\nWhat to do: {iss['suggestion'] or '-'}\nRetry safe: {'yes' if iss['retry_safe'] else 'no' if iss['retry_safe'] is not None else 'unknown'} · seen {iss['occurrences']}x"
        if info["issue_action"] in ("opened", "reopened") or info["issue_changed"]:
            rows.append(("pending", _payload(ev, iss["title"], text, iss["severity"], iss["id"]), iss["id"]))
        else:
            rows.append(("suppressed", _payload(ev, iss["title"], text, iss["severity"], iss["id"]), iss["id"]))
    for r in info.get("resolved", []):
        rows.append(("pending", _payload(ev, f"Recovered: {r['title']}", f"{_who(ev)}: {ev['message']}", "info", r["id"]), r["id"]))
    if ev["kind"] == "waiting_approval":
        st = "suppressed" if info.get("prev_status") == "Waiting for Approval" else "pending"
        rows.append((st, _payload(ev, f"Approval needed: {ev['stage']}", f"{_who(ev)}: {ev['message']}", "info"), None))
    elif ev["kind"] == "completed" and ev["stage"] == "publish":
        rows.append(("pending", _payload(ev, "Published" if ev["platform"] == "instagram" else "Uploaded", f"{_who(ev)}: {ev['message']}", "info"), None))
    elif ev["kind"] == "rejected" and not info.get("issue"):
        rows.append(("pending", _payload(ev, f"Rejected: {ev['stage']}", f"{_who(ev)}: {ev['message']}", "warning"), None))
    elif ev["stage"] == "system" and ev["detail"] and '"mac_online": true' in ev["detail"]:
        rows.append(("pending", _payload(ev, "Mac online", ev["message"], "info"), None))
    for status, payload, iid in rows:
        con.execute("INSERT INTO outbox (event_id, issue_id, channel, payload, status, attempts, created_at) VALUES (?,?,?,?,?,0,?)", (ev["id"], iid, "telegram", payload, status, db.now()))
    return len(rows)


class Watch:
    def __init__(self, content_id, lang, step, interval=20):
        self.content_id, self.lang, self.step, self.interval = content_id, lang, step, interval
        self.stop = threading.Event()
        self.thread = None
        self.last = None

    def files(self):
        from . import progress

        for st in progress.steps_for(self.content_id):
            if st["name"] == f"{self.step} {self.lang}":
                return st["files"]
        return []

    def tick(self):
        files = self.files()
        if not files:
            return None
        done = sum(1 for f in files if f.exists())
        if done != self.last:
            self.last = done
            emit("progress", self.step, f"{self.step} {done}/{len(files)}", variant_id=f"{self.content_id}-{self.lang}", progress=done / len(files),
                 detail={"done": done, "total": len(files), "measured": "files on disk"})
        return done

    def loop(self):
        while not self.stop.wait(self.interval):
            try:
                self.tick()
            except Exception:
                pass

    def __enter__(self):
        try:
            self.last = sum(1 for f in self.files() if f.exists())
            self.thread = threading.Thread(target=self.loop, daemon=True)
            self.thread.start()
        except Exception:
            self.thread = None
        return self

    def __exit__(self, *exc):
        self.stop.set()
        if self.thread:
            self.thread.join(timeout=2)
        try:
            self.tick()
        except Exception:
            pass
        return False
