import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

from . import CONTENT, ROOT, db, gates

DEFAULT_CAP = 6
MIN_LEAD = timedelta(minutes=10)
BACKOFF = [timedelta(hours=1), timedelta(hours=2), timedelta(hours=4), timedelta(hours=6)]
LOG = ROOT / "data" / "publish_queue.log"


def utcnow():
    return datetime.now(timezone.utc)


def say(msg):
    line = f"{datetime.now(gates.IST):%m-%d %H:%M} {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "a") as fh:
        fh.write(line + "\n")


def add(con, cid, langs, platform="youtube", priority=0):
    m = gates.load(cid)
    out = []
    for lang in langs:
        at = gates.approved_time(m, lang, platform)
        con.execute("INSERT INTO publish_queue (content_id, lang, platform, publish_at, priority, status, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?) "
                    "ON CONFLICT(content_id, lang, platform) DO UPDATE SET priority=excluded.priority, status=CASE WHEN publish_queue.status='done' THEN 'done' ELSE 'queued' END, updated_at=excluded.updated_at",
                    (cid, lang, platform, at, priority, "queued", db.now(), db.now()))
        out.append((f"{cid}-{lang}", at))
    return out


def items(con, statuses=None):
    rows = [dict(r) for r in con.execute("SELECT * FROM publish_queue ORDER BY id")]
    return [r for r in rows if not statuses or r["status"] in statuses]


def already_published(cid, lang, platform):
    for e in gates.published_entries({"id": cid}, lang):
        if e.get("platform") == platform:
            return e
    return None


def uploads_last_24h(con, platform="youtube", now=None):
    now = now or utcnow()
    n = 0
    for r in con.execute("SELECT created_at FROM publications WHERE platform=?", (platform,)):
        try:
            t = datetime.strptime(r["created_at"], "%Y-%m-%dT%H:%M:%S%z")
        except (TypeError, ValueError):
            continue
        if now - t < timedelta(hours=24):
            n += 1
    return n


def sort_key(r):
    t = gates.parse_time(r["publish_at"]) if r["publish_at"] not in (None, gates.NOW) else None
    return (-r["priority"], t or datetime.min.replace(tzinfo=timezone.utc), r["id"])


def plan(con, now=None, cap=DEFAULT_CAP):
    now = now or utcnow()
    used = uploads_last_24h(con, now=now)
    decisions = []
    for r in sorted(items(con, ("queued", "waiting", "backoff")), key=sort_key):
        variant = f"{r['content_id']}-{r['lang']}"
        if already_published(r["content_id"], r["lang"], r["platform"]):
            decisions.append((r, "done", "already uploaded (published.json)", None))
            continue
        m = gates.load(r["content_id"])
        approved = gates.approved_time(m, r["lang"], r["platform"])
        if not approved:
            decisions.append((r, "waiting", f"no {r['platform']} G3 approval yet", None))
            continue
        if r["next_try_at"] and gates.parse_time(r["next_try_at"]) > now:
            decisions.append((r, "backoff", f"backing off until {r['next_try_at']}", None))
            continue
        if approved == gates.NOW:
            when = (now + timedelta(minutes=15)).astimezone(gates.IST).replace(second=0, microsecond=0).isoformat()
        else:
            when = approved
            if gates.parse_time(approved) < now + MIN_LEAD:
                decisions.append((r, "blocked", f"approved time {approved} has passed or is under {int(MIN_LEAD.total_seconds() // 60)} min away; needs a new owner approval", None))
                continue
        problems = gates.check_publish(m, r["lang"], r["platform"], when, now=now)
        if problems:
            decisions.append((r, "blocked", "; ".join(problems), None))
            continue
        if used >= cap:
            decisions.append((r, "capped", f"daily cap {cap} reached ({used} uploads in the last 24 h)", when))
            continue
        used += 1
        decisions.append((r, "upload", f"upload {variant} with publishAt {when}", when))
    return decisions


def set_status(con, r, status, err=None, next_try=None, attempt=False):
    con.execute("UPDATE publish_queue SET status=?, last_error=?, next_try_at=?, attempts=attempts+?, updated_at=? WHERE id=?",
                (status, err, next_try, 1 if attempt else 0, db.now(), r["id"]))


def upload(r, when):
    log = CONTENT / r["content_id"] / r["lang"] / "publish_run.log"
    cmd = [sys.executable, "-m", "pipeline", "publish", r["content_id"], "--lang", r["lang"], "--platform", r["platform"], "--at", when, "--yes"]
    with open(log, "w") as fh:
        p = subprocess.run(cmd, cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT)
    return p.returncode, log.read_text()


def next_pacific_midnight(now):
    pt = now.astimezone(timezone(timedelta(hours=-8)))
    return (pt + timedelta(days=1)).replace(hour=0, minute=5, second=0, microsecond=0).astimezone(timezone.utc)


def run(cap=DEFAULT_CAP, dry_run=False, once=False):
    while True:
        with db.connect() as con:
            decisions = plan(con, cap=cap)
            for r, action, why, when in decisions:
                variant = f"{r['content_id']}-{r['lang']}"
                if dry_run:
                    say(f"[dry-run] {variant:10s} {action:8s} {why}")
                    continue
                if action == "done":
                    set_status(con, r, "done")
                    say(f"skip {variant}: {why}")
                elif action in ("waiting", "blocked", "capped", "backoff"):
                    set_status(con, r, "waiting" if action != "blocked" else "blocked", why, r["next_try_at"] if action == "backoff" else None)
                    if action != "backoff":
                        say(f"{action} {variant}: {why}")
        if dry_run:
            return decisions
        for r, action, why, when in decisions:
            if action != "upload":
                continue
            variant = f"{r['content_id']}-{r['lang']}"
            say(f"uploading {variant} publishAt {when}")
            code, out = upload(r, when)
            with db.connect() as con:
                if code == 0:
                    set_status(con, r, "done", attempt=True)
                    say(f"OK {variant} publishAt {when}")
                elif "uploadLimitExceeded" in out:
                    k = min(r["attempts"], len(BACKOFF) - 1)
                    nt = (utcnow() + BACKOFF[k]).isoformat()
                    set_status(con, r, "backoff", "uploadLimitExceeded", nt, attempt=True)
                    say(f"limit {variant}: channel upload limit; next try {nt}")
                    break
                elif "quotaExceeded" in out:
                    nt = next_pacific_midnight(utcnow()).isoformat()
                    set_status(con, r, "backoff", "quotaExceeded", nt, attempt=True)
                    say(f"quota {variant}: API quota used up; next try {nt}")
                    break
                else:
                    tail = out.strip().splitlines()[-1][:200] if out.strip() else f"exit {code}"
                    set_status(con, r, "failed", tail, attempt=True)
                    say(f"FAIL {variant}: {tail}")
        with db.connect() as con:
            pending = items(con, ("queued", "waiting", "backoff"))
        if once or not pending:
            say("queue idle" if not pending else "queue pass done (--once)")
            return decisions
        time.sleep(900)


def cli(a):
    with db.connect() as con:
        if a.action == "add":
            if not a.id or not a.langs:
                sys.exit("publish-queue add <ID> --langs en,hi")
            for v, at in add(con, a.id, a.langs.split(","), a.platform, a.priority):
                print(f"queued {v} {a.platform} (approved time: {at or 'not approved yet'})")
            return
        if a.action == "remove":
            for lang in a.langs.split(","):
                con.execute("DELETE FROM publish_queue WHERE content_id=? AND lang=? AND platform=?", (a.id, lang, a.platform))
            print("removed")
            return
        if a.action == "list":
            for r in items(con):
                print(f"{r['content_id']}-{r['lang']:3s} {r['platform']:8s} {r['status']:8s} at {r['publish_at'] or '-'} tries {r['attempts']} {r['last_error'] or ''}")
            return
    run(a.cap or DEFAULT_CAP, a.dry_run, a.once)
