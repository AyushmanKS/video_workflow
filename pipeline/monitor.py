import json
import time
from datetime import datetime, timezone

from . import CONTENT, db, events

ICON = {"started": ">", "progress": "~", "completed": "+", "failed": "x", "unknown_outcome": "?", "waiting_approval": "!", "approved": "+",
        "rejected": "x", "queued": "=", "info": ".", "warning": "!"}


def timeline(con, video=None, since_h=None, project=None, limit=200, kinds=None):
    q, args = "SELECT * FROM events WHERE 1=1", []
    if video:
        if "-" in video:
            q += " AND variant_id=?"
        else:
            q += " AND content_id=?"
        args.append(video)
    if since_h:
        q += " AND t >= ?"
        args.append(time.time() - float(since_h) * 3600)
    if project:
        q += " AND project_id=?"
        args.append(project)
    if kinds:
        q += f" AND kind IN ({','.join('?' for _ in kinds)})"
        args += list(kinds)
    q += " ORDER BY t DESC, rowid DESC LIMIT ?"
    args.append(int(limit))
    return list(reversed(con.execute(q, args).fetchall()))


def fmt_event(r):
    when = time.strftime("%m-%d %H:%M:%S", time.localtime(r["t"]))
    who = " ".join(x for x in (r["variant_id"] or r["content_id"] or r["project_id"] or "-", r["platform"] or "") if x)
    prog = f" {r['progress'] * 100:.0f}%" if r["progress"] is not None else ""
    code = f" [{r['error_code']}]" if r["error_code"] else ""
    bf = " (backfilled)" if r["detail"] and '"backfilled": true' in r["detail"] else ""
    return f"{when} {ICON.get(r['kind'], '.')} {r['kind']:16s} {who:20s} {r['stage']:22s} {r['status'] or '':20s} {r['message']}{prog}{code}{bf}"


def issues(con, only_open=False):
    q = "SELECT * FROM issues"
    if only_open:
        q += " WHERE status IN ('open','acknowledged')"
    q += " ORDER BY CASE status WHEN 'open' THEN 0 WHEN 'acknowledged' THEN 1 ELSE 2 END, CASE severity WHEN 'critical' THEN 0 WHEN 'recoverable' THEN 1 WHEN 'warning' THEN 2 ELSE 3 END, last_t DESC"
    return con.execute(q).fetchall()


def fmt_issue(r, full=False):
    head = f"#{r['id']:<4d} {r['status']:12s} {r['severity']:11s} {(r['variant_id'] or r['content_id'] or r['project_id'] or 'workspace'):10s} {r['platform'] or '-':9s} {r['stage']:20s} {r['title']} (x{r['occurrences']}, last {r['last_seen']})"
    if not full:
        return head
    retry = "yes" if r["retry_safe"] == 1 else "no" if r["retry_safe"] == 0 else "unknown"
    lines = [head, f"      what happened: {r['explanation']}", f"      what to do:    {r['suggestion']}", f"      retry safe:    {retry}",
             f"      technical:     {(r['technical'] or '')[:400]}"]
    if r["log_ref"]:
        lines.append(f"      log:           {r['log_ref']}")
    if r["status"] == "resolved":
        lines.append(f"      resolved:      {r['resolved_at']} {r['resolution'] or ''}")
    return "\n".join(lines)


def resolve_issue(con, issue_id, note=None, status="resolved"):
    r = con.execute("SELECT * FROM issues WHERE id=?", (issue_id,)).fetchone()
    if not r:
        return None
    con.execute("UPDATE issues SET status=?, resolved_at=?, resolution=? WHERE id=?",
                (status, db.now() if status == "resolved" else r["resolved_at"], note or f"{status} by hand", issue_id))
    return r


def projects(con):
    return con.execute("SELECT p.*, (SELECT COUNT(*) FROM contents c WHERE c.project_id=p.id) AS videos FROM projects p ORDER BY created_at").fetchall()


def add_project(con, slug, name, languages=None, description=None, objective=None, workflow=None):
    cfg = {"workflow": workflow} if workflow else {}
    con.execute("INSERT INTO projects (id, name, description, objective, languages, config, status, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET name=excluded.name, description=COALESCE(excluded.description, description), objective=COALESCE(excluded.objective, objective), "
                "languages=excluded.languages, config=CASE WHEN excluded.config='{}' THEN config ELSE excluded.config END, updated_at=excluded.updated_at",
                (slug, name, description, objective, json.dumps(languages or []), json.dumps(cfg), "active", db.now(), db.now()))


def _done(m, key):
    return m.get("stages", {}).get(key, {}).get("status") in ("done", "approved")


def pending_approvals(con=None):
    from . import gates

    pubs = set()
    if con is not None:
        pubs = {(r[0], r[1]) for r in con.execute("SELECT variant_id, platform FROM publications")}
    out = []
    for p in sorted(CONTENT.glob("C*/manifest.json")):
        try:
            m = json.loads(p.read_text())
        except ValueError:
            continue
        g1, g2 = set(gates.approved_langs(m, gates.SCRIPT)), set(gates.approved_langs(m, gates.FINAL))
        uses_ig = "instagram" in m.get("platforms", ["youtube"]) or gates.publish_key("instagram") in m.get("stages", {})
        for lang in m.get("languages", []):
            v = f"{m['id']}-{lang}"
            if lang not in g1:
                if _done(m, f"script:{lang}"):
                    out.append((v, gates.SCRIPT))
                continue
            if lang not in g2:
                if _done(m, f"video_qa:{lang}"):
                    out.append((v, gates.FINAL))
                continue
            for plat, stage in (("youtube", "published"), ("instagram", "published_instagram")):
                if plat == "instagram" and not uses_ig:
                    continue
                if (v, plat) in pubs or _done(m, f"{stage}:{lang}"):
                    continue
                if lang not in gates.approved_langs(m, gates.publish_key(plat)):
                    out.append((v, gates.publish_key(plat)))
    return out


def _future(s):
    if not s:
        return False
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")) > datetime.now(timezone.utc)
    except ValueError:
        return False


def overview(con):
    o = {}
    o["active_projects"] = con.execute("SELECT COUNT(*) FROM projects WHERE status='active'").fetchone()[0]
    pubbed = {r[0] for r in con.execute("SELECT DISTINCT variant_id FROM publications")}
    variants = [r[0] for r in con.execute("SELECT id FROM variants")]
    o["videos_in_production"] = sum(1 for v in variants if v not in pubbed)
    o["videos_total"] = len(variants)
    stale = time.time() - 6 * 3600
    o["running"] = con.execute("SELECT COUNT(*) FROM task_state WHERE status='Running' AND t >= ?", (stale,)).fetchone()[0]
    o["running_stale"] = con.execute("SELECT COUNT(*) FROM task_state WHERE status='Running' AND t < ?", (stale,)).fetchone()[0]
    waits = pending_approvals(con)
    o["waiting_approval"] = len(waits)
    o["waiting_approval_list"] = waits
    o["queued_uploads_youtube"] = con.execute("SELECT COUNT(*) FROM publish_queue WHERE status IN ('queued','waiting','backoff')").fetchone()[0]
    try:
        from . import igschedule

        o["scheduled_instagram_jobs"] = len([j for j in igschedule.jobs() if not j["dry_run"]])
    except Exception:
        o["scheduled_instagram_jobs"] = None
    pubs = con.execute("SELECT platform, scheduled_for FROM publications").fetchall()
    o["published"] = {}
    for p in pubs:
        d = o["published"].setdefault(p["platform"], {"live": 0, "scheduled": 0})
        d["scheduled" if _future(p["scheduled_for"]) else "live"] += 1
    o["failed_tasks"] = con.execute("SELECT COUNT(*) FROM task_state WHERE status='Failed'").fetchone()[0]
    o["needs_attention_tasks"] = con.execute("SELECT COUNT(*) FROM task_state WHERE status='Needs Attention'").fetchone()[0]
    o["open_issues"] = {r[0]: r[1] for r in con.execute("SELECT severity, COUNT(*) FROM issues WHERE status IN ('open','acknowledged') GROUP BY severity")}
    o["outbox_pending"] = con.execute("SELECT COUNT(*) FROM outbox WHERE status='pending'").fetchone()[0]
    last = con.execute("SELECT MAX(t) FROM events WHERE detail IS NULL OR detail NOT LIKE '%\"backfilled\": true%'").fetchone()[0]
    o["last_live_event"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(last)) if last else None
    return o


def fmt_overview(o):
    pub = ", ".join(f"{k} {v['live']} live + {v['scheduled']} scheduled" for k, v in sorted(o["published"].items())) or "none"
    iss = ", ".join(f"{v} {k}" for k, v in sorted(o["open_issues"].items(), key=lambda kv: events.SEV_RANK.get(kv[0], 9), reverse=True)) or "none"
    lines = [
        f"Active projects:        {o['active_projects']}",
        f"Videos in production:   {o['videos_in_production']} of {o['videos_total']} variants (no publication on any platform yet)",
        f"Running now:            {o['running']}" + (f" (+{o['running_stale']} marked running but silent for over 6 h)" if o["running_stale"] else ""),
        f"Waiting for approval:   {o['waiting_approval']}" + (f" ({', '.join(f'{v} {g}' for v, g in o['waiting_approval_list'][:8])}{' …' if len(o['waiting_approval_list']) > 8 else ''})" if o["waiting_approval_list"] else ""),
        f"Queued uploads:         {o['queued_uploads_youtube']} YouTube in publish-queue · {o['scheduled_instagram_jobs'] if o['scheduled_instagram_jobs'] is not None else '?'} Instagram launchd jobs",
        f"Published:              {pub}",
        f"Failed tasks:           {o['failed_tasks']}",
        f"Needs attention:        {o['needs_attention_tasks']} tasks · open issues: {iss}",
        f"Notifications pending:  {o['outbox_pending']} (Phase 2 sends them)",
        f"Last live event:        {o['last_live_event'] or 'none yet'}",
    ]
    return "\n".join(lines)
