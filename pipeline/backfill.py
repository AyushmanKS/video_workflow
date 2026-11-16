import json
import re
from datetime import datetime
from pathlib import Path

from . import CONTENT, DATA, db, events, explain

QA_STAGES = ("voice_qa", "video_qa")
IG_HEAD = re.compile(r"^(C\d{4}-[a-z]{2,3}): Instagram (dry run|publish) starting (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
EXC_LINE = re.compile(r"^([A-Za-z_][\w.]*(?:Error|Exception|Timeout|Exceeded)[\w.]*): ")


def already_done(con):
    try:
        return con.execute("SELECT COUNT(*) FROM events WHERE detail LIKE '%\"backfilled\": true%'").fetchone()[0]
    except Exception:
        return 0


def ts_of(s):
    try:
        return events.parse_ts(s)[1]
    except (ValueError, TypeError):
        return None


def from_runs(con):
    out = []
    for r in con.execute("SELECT * FROM runs ORDER BY id"):
        base = {"stage": r["stage"], "content_id": r["content_id"], "variant_id": r["variant_id"], "run_id": r["id"], "detail": {"source": "runs", "run_id": r["id"]}}
        t0 = ts_of(r["started_at"])
        if t0:
            out.append((t0, {**base, "kind": "started", "message": f"{r['stage']} started"}))
        t1 = ts_of(r["finished_at"]) if r["finished_at"] else None
        secs = f" in {r['seconds']:.0f} s" if r["seconds"] is not None else ""
        if r["status"] == "ok" and t1:
            if r["stage"] in QA_STAGES:
                out.append((t1 + 0.001, {**base, "kind": "info", "message": f"{r['stage']} run finished{secs}"}))
            else:
                out.append((t1 + 0.001, {**base, "kind": "completed", "message": f"{r['stage']} finished{secs}"}))
        elif r["status"] == "failed" and t1:
            out.append((t1 + 0.001, {**base, "kind": "failed", "message": f"{r['stage']} failed{secs}", "error": r["detail"] or "failed (no detail recorded)"}))
        elif r["status"] == "running" and t0:
            out.append((t0 + 1, {**base, "kind": "warning", "status": "Cancelled", "message": f"{r['stage']} never recorded a finish (interrupted or killed)"}))
    return out


def from_qa(con):
    out = []
    for r in con.execute("SELECT id, variant_id, kind, verdict, report, created_at FROM qa_reports ORDER BY id"):
        t = ts_of(r["created_at"])
        if not t:
            continue
        stage = "voice_qa" if r["kind"] == "audio" else "video_qa"
        base = {"stage": stage, "variant_id": r["variant_id"], "detail": {"source": "qa_reports", "qa_report": r["id"], "verdict": r["verdict"]}}
        if r["verdict"] == "fail":
            try:
                rep = json.loads(r["report"])
            except ValueError:
                rep = {}
            out.append((t + 0.5, {**base, "kind": "failed", "message": f"QA fail (report #{r['id']})", "error": explain.qa_failure_text(rep), "error_code": "qa_fail"}))
        else:
            out.append((t + 0.5, {**base, "kind": "completed", "message": f"QA {r['verdict']} (report #{r['id']})"}))
    return out


def from_decisions(con):
    out = []
    for r in con.execute("SELECT * FROM decisions WHERE decided_by='human' ORDER BY id"):
        t = ts_of(r["created_at"])
        if not t:
            continue
        stage, plat = r["stage"], None
        if stage.startswith("gate:publish:"):
            plat = stage.split(":")[2]
        base = {"variant_id": r["variant_id"], "content_id": r["content_id"], "platform": plat, "detail": {"source": "decisions", "decision_id": r["id"], "channel": r["channel"]}}
        note = (r["reasoning"] or "")[:160]
        if r["decision"] == "approved":
            out.append((t, {**base, "stage": stage, "kind": "approved", "message": f"owner approved {stage}" + (f": {note}" if note else "")}))
        elif r["decision"] == "rejected":
            out.append((t, {**base, "stage": stage, "kind": "rejected", "message": f"owner rejected {stage}: {note}", "error_code": "gate_rejected"}))
        elif stage == "waiver":
            out.append((t, {**base, "stage": "waiver", "kind": "info", "message": f"owner waived {r['decision']}" + (f": {note}" if note else "")}))
    return out


def from_publications(con):
    out = []
    for r in con.execute("SELECT * FROM publications ORDER BY id"):
        t = ts_of(r["created_at"])
        if not t:
            continue
        if r["platform"] == "youtube":
            msg = f"uploaded to YouTube {r['platform_id']}" + (f", scheduled for {r['scheduled_for']}" if r["scheduled_for"] else "")
        else:
            msg = f"published on Instagram {r['url'] or r['platform_id']}"
        out.append((t, {"stage": "publish", "platform": r["platform"], "variant_id": r["variant_id"], "kind": "completed", "message": msg,
                        "detail": {"source": "publications", "publication_id": r["id"], "platform_id": r["platform_id"], "url": r["url"]}}))
    return out


def from_queue(con):
    out = []
    for r in con.execute("SELECT * FROM publish_queue ORDER BY id"):
        v = f"{r['content_id']}-{r['lang']}"
        base = {"stage": "publish", "platform": r["platform"], "variant_id": v, "detail": {"source": "publish_queue", "queue_id": r["id"], "publish_at": r["publish_at"]}}
        t0 = ts_of(r["created_at"])
        if t0:
            out.append((t0, {**base, "kind": "queued", "message": f"added to publish-queue (approved time {r['publish_at'] or 'none yet'})"}))
        t1 = ts_of(r["updated_at"]) or t0
        err = r["last_error"]
        if not t1 or r["status"] in ("queued", "done"):
            continue
        if r["status"] == "waiting":
            out.append((t1, {**base, "kind": "queued", "message": f"waiting: {err or 'in queue'}"}))
        elif r["status"] == "backoff":
            out.append((t1, {**base, "kind": "queued", "message": f"backing off until {r['next_try_at']}: {err}", "error": err}))
        elif r["status"] == "blocked":
            out.append((t1, {**base, "kind": "warning", "status": "Needs Attention", "message": f"blocked: {err}", "error": err}))
        elif r["status"] == "failed":
            out.append((t1, {**base, "kind": "failed", "message": f"upload failed: {err}", "error": err or "failed"}))
    return out


def from_publish_logs():
    out = []
    for p in sorted(CONTENT.glob("C*/*/publish_run.log")):
        text = p.read_text(errors="replace")
        if "uploaded: https" in text:
            continue
        lines = [l for l in text.splitlines() if l.strip()]
        err = next((l for l in reversed(lines) if "HttpError" in l or "ResumableUploadError" in l), None) or next((l for l in reversed(lines) if EXC_LINE.match(l)), None)
        if not err:
            continue
        v = f"{p.parent.parent.name}-{p.parent.name}"
        out.append((p.stat().st_mtime, {"stage": "publish", "platform": "youtube", "variant_id": v, "kind": "failed", "message": "YouTube upload failed",
                                        "error": err, "log_ref": str(p.relative_to(CONTENT.parent)), "detail": {"source": "publish_run.log"}}))
    return out


def ig_segments(path):
    segs, cur = [], None
    for line in path.read_text(errors="replace").splitlines():
        m = IG_HEAD.match(line)
        if m:
            cur = {"variant": m.group(1), "dry": m.group(2) == "dry run", "start": m.group(3), "lines": []}
            segs.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
    return segs


def from_ig_logs():
    out = []
    for p in sorted((DATA / "logs").glob("ig-*.log")):
        ref = str(p.relative_to(DATA.parent))
        for seg in ig_segments(p):
            t0 = ts_of(seg["start"])
            if not t0:
                continue
            stage = "ig_dry_run" if seg["dry"] else "publish"
            base = {"stage": stage, "platform": "instagram", "variant_id": seg["variant"], "log_ref": ref}
            n = 0

            def add(kind, msg, **kw):
                nonlocal n
                n += 1
                out.append((t0 + n, {**base, "kind": kind, "message": msg, "detail": {"source": "ig log", "ts_approx": n > 1, **kw.pop("detail", {})}, **kw}))

            add("started", f"Instagram {'dry run' if seg['dry'] else 'publish'} started")
            container, outcome, exc = None, False, None
            for line in seg["lines"]:
                s = line.strip()
                if s.startswith("temporary link is live"):
                    add("info", "temporary link is live; Instagram can fetch the video")
                elif s.startswith("container ") and " created" in s:
                    container = s.split()[1]
                    add("info", f"container {container} created; Instagram is processing", detail={"container_id": container})
                elif s.startswith("network timeout during"):
                    add("info", s)
                elif s.startswith("published:"):
                    outcome = True
                elif s.startswith("dry run OK"):
                    add("completed", "dry run OK: token valid, tunnel reachable, file within limits")
                    outcome = True
                elif s.startswith("Instagram API error") or s.startswith("The temporary tunnel never became reachable") or s.startswith("Could not start the temporary tunnel"):
                    add("failed", s[:300], error=s)
                    outcome = True
                elif EXC_LINE.match(s):
                    exc = s
                elif re.match(r"^EXIT \w+ [1-9]", s) and exc and not outcome:
                    if container:
                        add("unknown_outcome", f"network failure after container {container} was created; outcome not confirmed", error=exc, context=["container_created"], detail={"container_id": container})
                    else:
                        add("failed", exc[:300], error=exc)
                    outcome = True
            if not outcome and exc:
                if container:
                    add("unknown_outcome", f"network failure after container {container} was created; outcome not confirmed", error=exc, context=["container_created"], detail={"container_id": container})
                else:
                    add("failed", exc[:300], error=exc)
            elif not outcome and not seg["dry"]:
                add("warning", "attempt ended without a recorded outcome (log stops; the process was stopped)")
    return out


def pending_gates():
    from . import monitor

    out = []
    try:
        with db.connect() as con:
            waits = monitor.pending_approvals(con)
        for v, gate in waits:
            plat = gate.split(":")[2] if gate.count(":") == 2 else None
            out.append((None, {"stage": gate, "platform": plat, "variant_id": v, "kind": "waiting_approval", "message": f"waiting for owner approval ({gate})", "detail": {"source": "manifest"}}))
    except Exception:
        pass
    return out


def run(force=False):
    with db.connect() as con:
        n = already_done(con)
        if n and not force:
            return {"skipped": True, "existing": n}
        items = from_runs(con) + from_qa(con) + from_decisions(con) + from_publications(con) + from_queue(con)
    items += from_publish_logs() + from_ig_logs()
    items.sort(key=lambda x: x[0])
    items += pending_gates()
    counts, failed = {}, 0
    for t, kw in items:
        kw = dict(kw)
        eid = events.emit(kw.pop("kind"), kw.pop("stage"), kw.pop("message", ""), ts=t, backfilled=True, **kw)
        if eid:
            k = (kw.get("detail") or {}).get("source", "?")
            counts[k] = counts.get(k, 0) + 1
        else:
            failed += 1
    with db.connect() as con:
        superseded = settle_dry_runs(con)
        issues = con.execute("SELECT status, COUNT(*) FROM issues GROUP BY status").fetchall()
    return {"skipped": False, "events": counts, "failed": failed, "issues": {r[0]: r[1] for r in issues}, "settled": superseded}


def settle_dry_runs(con):
    out = []
    for r in con.execute("SELECT * FROM issues WHERE status='open' AND stage='ig_dry_run' AND error_code='tunnel_failed'").fetchall():
        later = con.execute("SELECT ts, variant_id FROM events WHERE message LIKE 'temporary link is live%' AND t > ? ORDER BY t LIMIT 1", (r["last_t"] or 0,)).fetchone()
        if later:
            con.execute("UPDATE issues SET status='resolved', resolved_at=?, resolution=? WHERE id=?",
                        (later["ts"], f"superseded: the tunnel worked on a later run ({later['variant_id']} at {later['ts']}); dry-run failure was a one-off", r["id"]))
            con.execute("UPDATE task_state SET status='Cancelled', message=? WHERE variant_id IS ? AND stage='ig_dry_run' AND status='Failed'",
                        (f"dry-run tunnel failure superseded by a later working tunnel ({later['ts']})", r["variant_id"]))
            out.append(r["id"])
    return out
