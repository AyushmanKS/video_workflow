import json
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import backfill, db, events, explain, monitor


@pytest.fixture
def tmpdb(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(db, "DATA", tmp_path)
    monkeypatch.setattr(events, "_ready", set())
    monkeypatch.setattr(events, "_workflows", {})
    events.clear_context()
    with db.connect():
        pass
    yield tmp_path
    events.clear_context()


def rows(sql, *args):
    con = sqlite3.connect(db.DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def fallback_lines():
    p = events.fallback_path()
    return p.read_text().splitlines() if p.exists() else []


BLOCKED = "Instagram API error during container creation (HTTP 400): {'message': 'API access blocked.', 'code': 200, 'type': 'OAuthException', 'error_subcode': 5258005, 'fbtrace_id': 'AX7hlO-mmuGY7pFq_X-V9lf'}"
POST_TIMEOUT = "Network error during publish after the request may have reached Instagram; not retrying to avoid a duplicate. Check the account before retrying."
GET_TIMEOUT = ("requests.exceptions.ConnectTimeout: HTTPSConnectionPool(host='graph.facebook.com', port=443): Max retries exceeded with url: "
               "/v27.0/18180328639433140?fields=status_code%2Cstatus&access_token=REDACTED (Caused by ConnectTimeoutError(...))")
UPLOAD_LIMIT = ("googleapiclient.errors.ResumableUploadError: <HttpError 400 when requesting None returned \"The user has exceeded the number of videos they may upload.\". "
                "Details: \"[{'message': 'The user has exceeded the number of videos they may upload.', 'domain': 'youtube.video', 'reason': 'uploadLimitExceeded'}]\">")


def test_event_persisted_and_outbox_references_it(tmpdb):
    eid = events.emit("failed", "publish", "container creation failed", variant_id="C0002-hi", platform="instagram", error=BLOCKED)
    assert eid
    ev = rows("SELECT * FROM events WHERE id=?", eid)[0]
    assert ev["content_id"] == "C0002" and ev["kind"] == "failed" and ev["error_code"] == "ig_api_blocked" and ev["status"] == "Needs Attention"
    ob = rows("SELECT * FROM outbox WHERE status='pending' AND issue_id IS NOT NULL")
    assert len(ob) == 1 and ob[0]["event_id"] == eid
    assert rows("SELECT * FROM task_state WHERE variant_id='C0002-hi'")[0]["status"] == "Needs Attention"


def test_event_survives_outbox_failure(tmpdb, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("outbox down")

    monkeypatch.setattr(events, "_enqueue", boom)
    eid = events.emit("failed", "publish", "x", variant_id="C0002-hi", platform="instagram", error=BLOCKED)
    assert eid and rows("SELECT id FROM events WHERE id=?", eid)
    assert rows("SELECT COUNT(*) FROM outbox")[0][0] == 0
    assert rows("SELECT COUNT(*) FROM issues")[0][0] == 1
    assert any("outbox" in l for l in fallback_lines())


def test_repeated_identical_failures_dedupe(tmpdb):
    for _ in range(2):
        events.emit("failed", "publish", "blocked", variant_id="C0002-en", platform="instagram", error=BLOCKED)
    iss = rows("SELECT * FROM issues")
    assert len(iss) == 1 and iss[0]["occurrences"] == 2 and iss[0]["status"] == "open"
    ob = rows("SELECT status FROM outbox WHERE issue_id=? ORDER BY id", iss[0]["id"])
    assert [r["status"] for r in ob] == ["pending", "suppressed"]
    events.emit("failed", "publish", "blocked", variant_id="C0002-en", platform="instagram", error=BLOCKED)
    ob = rows("SELECT status FROM outbox WHERE issue_id=? ORDER BY id", iss[0]["id"])
    assert [r["status"] for r in ob] == ["pending", "suppressed", "pending"]


def test_issue_resolves_on_later_success(tmpdb):
    events.emit("failed", "publish", "blocked", variant_id="C0002-hi", platform="instagram", error=BLOCKED)
    events.emit("completed", "publish", "uploaded", variant_id="C0002-hi", platform="youtube")
    assert rows("SELECT status FROM issues")[0]["status"] == "open"
    events.emit("completed", "publish", "published on Instagram", variant_id="C0002-hi", platform="instagram")
    iss = rows("SELECT * FROM issues")[0]
    assert iss["status"] == "resolved" and iss["resolved_at"]
    titles = [json.loads(r["payload"])["title"] for r in rows("SELECT payload FROM outbox WHERE status='pending'")]
    assert any(t.startswith("Recovered:") for t in titles)
    assert rows("SELECT status FROM task_state WHERE variant_id='C0002-hi' AND platform='instagram'")[0]["status"] == "Completed"
    events.emit("failed", "publish", "blocked again", variant_id="C0002-hi", platform="instagram", error=BLOCKED)
    iss = rows("SELECT * FROM issues")[0]
    assert iss["status"] == "open" and iss["occurrences"] == 2


def test_post_timeout_is_unknown_outcome(tmpdb):
    eid = events.emit("failed", "publish", "network", variant_id="C0003-hi", platform="instagram", error=POST_TIMEOUT)
    ev = rows("SELECT * FROM events WHERE id=?", eid)[0]
    assert ev["kind"] == "unknown_outcome" and ev["retry_safe"] == 0 and ev["status"] == "Needs Attention"
    assert "check" in rows("SELECT suggestion FROM issues")[0]["suggestion"].lower()


def test_network_failure_after_container_is_unknown_outcome(tmpdb):
    events.add_flag("container_created")
    eid = events.emit("failed", "publish", "status check failed", variant_id="C0002-hi", platform="instagram", error=GET_TIMEOUT)
    ev = rows("SELECT * FROM events WHERE id=?", eid)[0]
    assert ev["kind"] == "unknown_outcome" and ev["error_code"] == "ig_container_orphaned" and ev["retry_safe"] == 0
    events.clear_context()
    eid = events.emit("failed", "analytics", "get failed", platform="instagram", error=GET_TIMEOUT)
    ev = rows("SELECT * FROM events WHERE id=?", eid)[0]
    assert ev["kind"] == "failed" and ev["error_code"] == "network_timeout" and ev["retry_safe"] == 1


SECRETS = ["EA" + "A" + "Bfake" * 4, "ya" + "29." + "fakeFAKE" * 3, "1/" + "/" + "0gFAKE" * 5, "fake" + "secretvalue"]


def test_tokens_are_redacted_everywhere(tmpdb):
    raw = (f"error at https://graph.facebook.com/v27.0/me?access_token={SECRETS[0]}&x=1 header Authorization: Bearer {SECRETS[1]} "
           f"{{'refresh_token': '{SECRETS[2]}', 'client_secret': '{SECRETS[3]}'}} plain {SECRETS[0]} (#10) permission")
    events.emit("failed", "publish", f"failed {SECRETS[0]}", variant_id="C0004-en", platform="instagram", error=raw, detail={"token": f"Bearer {SECRETS[1]}"})
    dump = json.dumps([dict(r) for t in ("events", "issues", "outbox", "task_state") for r in rows(f"SELECT * FROM {t}")])
    for s in SECRETS:
        assert s not in dump
    for s in ("ya" + "29.", "EAA"):
        assert explain.redact(f"x {s}abcdef123") != f"x {s}abcdef123"
    assert rows("SELECT error_code FROM issues")[0]["error_code"] == "ig_permission"


def test_emit_never_raises_when_db_locked(tmpdb, monkeypatch):
    monkeypatch.setattr(events, "BUSY_MS", 100)
    con = sqlite3.connect(db.DB_PATH, isolation_level=None)
    con.execute("BEGIN EXCLUSIVE")
    try:
        assert events.emit("failed", "publish", "while locked", variant_id="C0002-hi", error=BLOCKED) is None
    finally:
        con.execute("ROLLBACK")
        con.close()
    assert any("locked" in l for l in fallback_lines())


def test_emit_never_raises_when_tables_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "empty.db")
    monkeypatch.setattr(db, "DATA", tmp_path)
    monkeypatch.setattr(events, "ensure", lambda con: None)
    assert events.emit("started", "render", "x", variant_id="C0001-en") is None
    assert any("no such table" in l for l in fallback_lines())
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "missing" / "dir" / "x.db")
    assert events.emit("started", "render", "x") is None


def test_run_context_emits_lifecycle(tmpdb):
    with db.Run("render", "C0001", "C0001-en"):
        pass
    with pytest.raises(FileNotFoundError):
        with db.Run("voice", "C0001", "C0001-en"):
            raise FileNotFoundError(2, "No such file or directory")
    kinds = [(r["stage"], r["kind"]) for r in rows("SELECT * FROM events WHERE stage != 'system' ORDER BY t")]
    assert kinds == [("render", "started"), ("render", "completed"), ("voice", "started"), ("voice", "failed")]
    assert rows("SELECT error_code FROM issues")[0]["error_code"] == "missing_output"


def test_mac_online_only_for_live_events(tmpdb):
    events.emit("info", "x", "old", ts="2026-01-01T10:00:00+05:30", backfilled=True)
    assert not rows("SELECT * FROM events WHERE stage='system'")
    events.emit("info", "x", "now")
    assert len(rows("SELECT * FROM events WHERE stage='system'")) == 1
    events.emit("info", "x", "again")
    assert len(rows("SELECT * FROM events WHERE stage='system'")) == 1
    assert not rows("SELECT * FROM outbox WHERE event_id IN (SELECT id FROM events WHERE detail LIKE '%backfilled%')")


def test_waiting_approval_dedupes(tmpdb):
    for _ in range(2):
        events.emit("waiting_approval", "gate:final", "QA pass", variant_id="C0006-hi")
    assert [r["status"] for r in rows("SELECT status FROM outbox ORDER BY id") if r] [-2:] == ["pending", "suppressed"]
    events.emit("approved", "gate:final", "owner approved", variant_id="C0006-hi")
    assert rows("SELECT status FROM task_state WHERE stage='gate:final'")[0]["status"] == "Completed"


def test_progress_only_when_measured(tmpdb):
    events.emit("progress", "images", "images 3/12", variant_id="C0007-en", progress=0.25)
    events.emit("progress", "images", "bad", variant_id="C0007-hi", progress=3)
    got = {r["variant_id"]: r["progress"] for r in rows("SELECT * FROM events WHERE kind='progress'")}
    assert got == {"C0007-en": 0.25, "C0007-hi": None}


CASES = [
    (UPLOAD_LIMIT, "youtube_upload_limit", True),
    ("<HttpError 403 when requesting https://youtube.googleapis.com/youtube/v3/videos returned \"Forbidden\". Details: \"[{'reason': 'insufficientPermissions'}]\">", "youtube_forbidden", False),
    ("<HttpError 403 ... 'reason': 'quotaExceeded'>", "youtube_quota", True),
    ("google.auth.exceptions.RefreshError: ('invalid_grant: Token has been expired or revoked.', {'error': 'invalid_grant'})", "google_token_expired", False),
    (BLOCKED, "ig_api_blocked", False),
    ("Instagram API error during container creation (HTTP 400): {'message': '(#10) Application does not have permission for this action', 'code': 10}", "ig_permission", False),
    ("Instagram API error during status check (HTTP 400): {'message': 'Error validating access token: Session has expired', 'code': 190}", "ig_token_invalid", False),
    (GET_TIMEOUT, "network_timeout", True),
    ("getaddrinfo ENOTFOUND graph.facebook.com", "network_timeout", True),
    (POST_TIMEOUT, "network_unknown_outcome", False),
    ("Instagram processing failed: {'status_code': 'ERROR', 'status': 'Error: unsupported format', 'id': '1'}", "ig_container_error", True),
    ("Instagram processing failed: {'status_code': 'EXPIRED', 'id': '1'}", "ig_container_error", True),
    ("The temporary tunnel never became reachable.", "tunnel_failed", True),
    ("exit 75: tunnel failed after 4 attempts", "tunnel_failed", True),
    ("OSError: [Errno 28] No space left on device", "disk_low", True),
    ("QA verdict fail: duration, speaker_consistency", "qa_fail", False),
    ("FileNotFoundError(2, 'No such file or directory')", "missing_output", True),
    ("CalledProcessError(1, ['/x/python', '/x/studio.py', 'C0004 en'])", "render_failed", True),
    ("C0005-hi: publish.json differs from the youtube G3 approval (approved 38f12305282a, now 5903cabf2e12)", "gate_refused", False),
    ("C0004-en: scheduled time 2026-11-18T20:30:00+05:30 is more than 24 h ago; not posting. Job removed.", "ig_job_late", False),
    ("something odd happened", "unknown_error", None),
]


@pytest.mark.parametrize("raw,code,retry", CASES)
def test_explain_catalogue(raw, code, retry):
    e = explain.explain(raw)
    assert e["code"] == code
    assert e["retry_safe"] is retry
    assert e["title"] and e["suggestion"] and e["severity"] in explain.SEVERITIES


def test_explain_container_context():
    e = explain.explain(GET_TIMEOUT, {"container_created"})
    assert e["code"] == "ig_container_orphaned" and e["kind"] == "unknown_outcome" and e["retry_safe"] is False


def test_backfill_reads_instagram_logs(tmpdb, monkeypatch):
    logs = tmpdb / "data" / "logs"
    logs.mkdir(parents=True)
    (logs / "ig-C0002-hi.log").write_text(f"C0002-hi: Instagram publish starting 2026-11-16 20:00:05\n\n  temporary link is live; Instagram can fetch the video\n{BLOCKED}\n")
    (logs / "ig-C0002-now2.log").write_text("C0002-hi: Instagram publish starting 2026-11-16 20:45:15\n  temporary link is live; Instagram can fetch the video\n"
                                            "  container 18180328639433140 created; waiting for Instagram to process\nTraceback (most recent call last):\n"
                                            f"{GET_TIMEOUT}\nEXIT hi 1\nC0002-en: Instagram publish starting 2026-11-16 20:48:38\n")
    monkeypatch.setattr(backfill, "DATA", tmpdb / "data")
    monkeypatch.setattr(backfill, "CONTENT", tmpdb / "content")
    monkeypatch.setattr(monitor, "CONTENT", tmpdb / "content")
    items = backfill.from_ig_logs()
    kinds = [(kw["variant_id"], kw["kind"], kw.get("error_code") or explain.explain(kw.get("error", ""), kw.get("context")).get("code") if kw.get("error") else None) for t, kw in items]
    assert ("C0002-hi", "failed", "ig_api_blocked") in kinds
    assert ("C0002-hi", "unknown_outcome", "ig_container_orphaned") in kinds
    assert ("C0002-en", "warning", None) in kinds
    with db.connect() as con:
        con.execute("INSERT INTO publications (variant_id, platform, platform_id, url, created_at) VALUES ('C0002-hi','instagram','1','https://www.instagram.com/reel/x/','2026-11-16T21:47:11+0530')")
    res = backfill.run()
    assert not res["skipped"] and res["failed"] == 0
    assert backfill.run()["skipped"]
    iss = {r["error_code"]: r["status"] for r in rows("SELECT * FROM issues")}
    assert iss == {"ig_api_blocked": "resolved", "ig_container_orphaned": "resolved"}
    assert rows("SELECT COUNT(*) FROM outbox")[0][0] == 0


def test_overview_counts_are_from_db(tmpdb, monkeypatch):
    monkeypatch.setattr(monitor, "CONTENT", tmpdb / "content")
    with db.connect() as con:
        con.execute("INSERT INTO contents (id, series, topic, status, created_at, updated_at) VALUES ('C0001','RAMAYANA — The Epic in Chalk','t','x','n','n')")
        con.execute("INSERT INTO variants (id, content_id, language, status, created_at, updated_at) VALUES ('C0001-en','C0001','en','x','n','n')")
    with db.connect() as con:
        o = monitor.overview(con)
        assert con.execute("SELECT project_id FROM contents").fetchone()[0] == "ramayana"
    assert o["active_projects"] == 1 and o["videos_in_production"] == 1 and o["running"] == 0 and o["open_issues"] == {}


def test_queue_events_wait_for_the_open_transaction(tmpdb, monkeypatch):
    import time as _t

    from pipeline import queue as pqueue

    monkeypatch.setattr(pqueue, "_deferred", [])
    monkeypatch.setattr(pqueue.gates, "load", lambda cid: {"id": cid, "stages": {}})
    t0 = _t.time()
    with db.connect() as con:
        pqueue.add(con, "C0009", ["en", "hi"])
        assert not rows("SELECT * FROM events WHERE stage='publish'")
    pqueue.flush()
    assert _t.time() - t0 < 2
    got = rows("SELECT variant_id, kind, status FROM events WHERE stage='publish' ORDER BY t")
    assert [(r["variant_id"], r["kind"], r["status"]) for r in got] == [("C0009-en", "queued", "Queued"), ("C0009-hi", "queued", "Queued")]
