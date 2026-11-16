import json
import os
import sqlite3
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import bot, dashboard, db, events, explain, notify

TOKEN = "123456789:AAH" + "x" * 32


@pytest.fixture
def tmpdb(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(db, "DATA", tmp_path)
    monkeypatch.setattr(events, "_ready", set())
    monkeypatch.setattr(events, "_workflows", {})
    monkeypatch.setattr(notify, "CONFIG", tmp_path / "secrets" / "telegram.json")
    monkeypatch.setattr(notify, "PAIR_FILE", tmp_path / "pair.json")
    monkeypatch.setattr(bot, "STATE", tmp_path / "bot_state.json")
    monkeypatch.setattr(dashboard, "URLFILE", tmp_path / "dashboard_url.json")
    monkeypatch.setattr(dashboard, "KEYFILE", tmp_path / "secrets" / "dashboard.json")
    events.clear_context()
    with db.connect() as con:
        con.execute("INSERT INTO projects (id, name, languages, config, status, created_at, updated_at) VALUES ('ramayana','RAMAYANA — The Epic in Chalk','[]','{}','active',?,?)", (db.now(), db.now()))
        con.execute("INSERT INTO contents (id, series, episode, topic, status, created_at, updated_at, project_id) VALUES ('C0004','RAMAYANA — The Epic in Chalk',4,'t','idea',?,?,'ramayana')", (db.now(), db.now()))
    events.emit("info", "system", "seed")
    con = sqlite3.connect(db.DB_PATH)
    con.execute("DELETE FROM outbox")
    con.commit()
    con.close()
    yield tmp_path
    events.clear_context()


def rows(sql, *args):
    con = sqlite3.connect(db.DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


class FakeHTTP:
    def __init__(self, script=None):
        self.calls = []
        self.script = list(script or [])
        self.mid = 100

    def __call__(self, url, payload, timeout):
        self.calls.append((url.rsplit("/", 1)[-1], payload))
        if self.script:
            r = self.script.pop(0)
            if isinstance(r, Exception):
                raise r
            return r
        self.mid += 1
        return 200, {"ok": True, "result": {"message_id": self.mid}}

    def sends(self):
        return [p for m, p in self.calls if m == "sendMessage"]


class Clock:
    def __init__(self):
        self.t = 1000.0
        self.slept = []

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


def api(http, clock=None):
    clock = clock or Clock()
    return notify.Telegram(TOKEN, http=http, sleep=clock.sleep, clock=clock)


def fail(code="youtube_upload_limit", raw=None, variant="C0004-hi", stage="publish", platform="youtube", log_ref=None):
    return events.emit("failed", stage, f"{stage} failed", variant_id=variant, platform=platform, error=raw, error_code=code, log_ref=log_ref)


def test_drain_sends_marks_sent_and_never_resends(tmpdb):
    fail(log_ref=str(ROOT / "data" / "logs" / "ig-C0004-hi.log"))
    http = FakeHTTP()
    assert notify.drain(api(http), 42) == 1
    r = rows("SELECT * FROM outbox WHERE issue_id IS NOT NULL")[0]
    assert r["status"] == "sent" and r["message_id"] == 101 and r["sent_at"]
    assert http.sends()[0]["chat_id"] == 42 and http.sends()[0]["parse_mode"] == "HTML"
    assert notify.drain(api(http), 42) == 0
    assert len(http.sends()) == 1


def test_upload_failure_message_format(tmpdb):
    fail(raw="HttpError 400 uploadLimitExceeded: The user has exceeded the number of videos they may upload.",
         log_ref=str(ROOT / "data" / "logs" / "publish_run.log"))
    http = FakeHTTP()
    notify.drain(api(http), 1)
    text = http.sends()[0]["text"]
    lines = text.split("\n")
    assert lines[0] == "❌ Upload failed — Ramayana Ep04 (Hindi)"
    assert lines[1] == "Reason: YouTube daily upload limit reached"
    assert lines[2].startswith("Details: HttpError 400 uploadLimitExceeded")
    assert lines[3].startswith("Action: Nothing to do. The publish queue retries")
    assert lines[4] == "Retry safe: yes"
    assert lines[5] == "Video: C0004-HI"
    assert lines[6].startswith("At: ") and ("AM" in lines[6] or "PM" in lines[6])
    assert lines[7] == "Log: data/logs/publish_run.log"


@pytest.mark.parametrize("entry", [e for e in explain.CATALOGUE if e["severity"] != "info"], ids=lambda e: e["code"])
def test_format_for_each_explain_code(tmpdb, entry):
    fail(code=entry["code"], raw=f"raw <error> & {entry['code']}")
    pend = rows("SELECT payload FROM outbox WHERE status='pending'")
    assert pend, entry["code"]
    con = notify._con()
    try:
        text = notify.format_payload(con, json.loads(pend[-1]["payload"]))
    finally:
        con.close()
    lines = text.split("\n")
    assert "Ramayana Ep04 (Hindi)" in lines[0]
    assert lines[1] == f"Reason: {notify.esc(entry['title'])}"
    assert lines[2].startswith("Details: ") and "&lt;error&gt; &amp;" in lines[2]
    assert lines[3] == f"Action: {notify.esc(entry['suggestion'])}"
    assert lines[4] == f"Retry safe: {'yes' if entry['retry_safe'] else 'no'}"
    assert lines[5] == "Video: C0004-HI"
    assert lines[6].startswith("At: ")
    if entry.get("kind") == "unknown_outcome":
        assert lines[0].startswith("❓")
    else:
        assert lines[0].startswith(("❌", "⚠️"))


def test_unknown_error_and_other_stage_headline(tmpdb):
    fail(code=None, raw="weird thing happened", stage="render", platform=None)
    http = FakeHTTP()
    notify.drain(api(http), 1)
    text = http.sends()[0]["text"]
    assert text.startswith("❌ Render failed — Ramayana Ep04 (Hindi)")
    assert "Reason: Unrecognised error" in text and "Retry safe: unknown" in text


def test_success_and_approval_are_concise(tmpdb):
    events.emit("completed", "publish", "uploaded as private, publishAt 20:30", variant_id="C0004-hi", platform="youtube")
    events.emit("waiting_approval", "gate:script", "script ready for G1", variant_id="C0004-hi")
    http = FakeHTTP()
    notify.drain(api(http), 1)
    texts = [p["text"] for p in http.sends()]
    assert any(t.startswith("✅ Uploaded to YouTube — Ramayana Ep04 (Hindi)") for t in texts)
    assert any(t.startswith("📝 Approval needed (G1 script) — Ramayana Ep04 (Hindi)") for t in texts)
    assert all(len(t.split("\n")) <= 5 for t in texts)


@pytest.mark.parametrize("reply,transient", [((429, {"ok": False, "error_code": 429, "description": "Too Many Requests", "parameters": {"retry_after": 7}}), True),
                                             ((502, {"ok": False, "error_code": 502, "description": "Bad Gateway"}), True),
                                             (ConnectionError(f"HTTPSConnectionPool url: /bot{TOKEN}/sendMessage"), True)])
def test_retry_on_429_5xx_network(tmpdb, reply, transient):
    fail()
    http = FakeHTTP([reply])
    now = time.time()
    assert notify.drain(api(http), 1, now=now) == 0
    r = rows("SELECT * FROM outbox WHERE issue_id IS NOT NULL")[0]
    assert r["status"] == "pending" and r["attempts"] == 1
    assert float(r["next_try_at"]) >= now + (7 if isinstance(reply, tuple) and reply[0] == 429 else notify.BACKOFF_S[0]) - 0.1
    assert TOKEN not in (r["last_error"] or "")
    assert notify.drain(api(http), 1, now=now + 1) == 0
    assert len(http.sends()) == 1
    assert notify.drain(api(http), 1, now=now + 4000) == 1
    r = rows("SELECT * FROM outbox WHERE issue_id IS NOT NULL")[0]
    assert r["status"] == "sent" and r["message_id"]


def test_permanent_error_marks_failed(tmpdb):
    fail()
    http = FakeHTTP([(403, {"ok": False, "error_code": 403, "description": "Forbidden: bot was blocked by the user"})])
    notify.drain(api(http), 1)
    r = rows("SELECT * FROM outbox WHERE issue_id IS NOT NULL")[0]
    assert r["status"] == "failed" and "blocked" in r["last_error"]


def test_max_attempts_then_failed(tmpdb):
    fail()
    con = sqlite3.connect(db.DB_PATH)
    con.execute(f"UPDATE outbox SET attempts={notify.MAX_ATTEMPTS - 1}")
    con.commit()
    con.close()
    notify.drain(api(FakeHTTP([(500, {"ok": False, "error_code": 500, "description": "oops"})])), 1)
    assert rows("SELECT status FROM outbox WHERE issue_id IS NOT NULL")[0]["status"] == "failed"


def test_html_parse_error_falls_back_to_plain(tmpdb):
    fail()
    http = FakeHTTP([(400, {"ok": False, "error_code": 400, "description": "Bad Request: can't parse entities"})])
    assert notify.drain(api(http), 1) == 1
    assert http.sends()[1].get("parse_mode") is None


def test_rate_limit_one_per_second(tmpdb):
    for lang in ("hi", "en", "gu"):
        fail(variant=f"C0004-{lang}")
    clock = Clock()
    http = FakeHTTP()
    assert notify.drain(api(http, clock), 1) == 3
    assert len(clock.slept) == 2 and all(s >= 1.0 for s in clock.slept)


def test_burst_becomes_one_digest_but_critical_stays_single(tmpdb):
    for i, lang in enumerate(("hi", "en", "gu", "te", "mr", "ta")):
        events.emit("waiting_approval", "gate:script", f"script {i} ready", variant_id=f"C0004-{lang}")
    fail(code="ig_api_blocked", platform="instagram", variant="C0004-kn")
    http = FakeHTTP()
    assert notify.drain(api(http), 1) == 7
    texts = [p["text"] for p in http.sends()]
    assert len(texts) == 2
    assert any("Instagram API access blocked" in t and t.startswith("❌ Instagram post failed") for t in texts)
    digest = next(t for t in texts if t.startswith("📬"))
    assert digest.startswith("📬 6 updates") and digest.count("\n• ") == 6
    sent = rows("SELECT message_id, last_error FROM outbox WHERE status='sent' AND issue_id IS NULL")
    assert len(sent) == 6 and len({r["message_id"] for r in sent}) == 1 and sent[0]["last_error"] == "digest"


def test_quiet_repeats_are_not_sent(tmpdb):
    fail()
    fail()
    http = FakeHTTP()
    assert notify.drain(api(http), 1) == 1
    assert rows("SELECT COUNT(*) FROM outbox WHERE status='suppressed'")[0][0] == 1
    fail()
    assert notify.drain(api(http), 1) == 1
    assert "(3×)" in http.sends()[-1]["text"]


def test_secret_local_message_scrubbed_after_send(tmpdb):
    notify.enqueue_local("Dashboard link", '<a href="https://x.trycloudflare.com/login?k=SECRETKEYSECRETKEYSECRETKEY">open</a>', secret=True)
    http = FakeHTTP()
    assert notify.drain(api(http), 1) == 1
    assert "SECRETKEY" in http.sends()[0]["text"]
    assert "SECRETKEY" not in rows("SELECT payload FROM outbox")[0]["payload"]


def test_stale_sending_rows_are_retried(tmpdb):
    fail()
    con = sqlite3.connect(db.DB_PATH)
    con.execute("UPDATE outbox SET status='sending', next_try_at=?", (f"{time.time() - 1000:.1f}",))
    con.commit()
    con.close()
    assert notify.drain(api(FakeHTTP()), 1) == 1


def test_token_redacted_everywhere():
    t = notify.Telegram(TOKEN, http=FakeHTTP([RuntimeError(f"failed GET https://api.telegram.org/bot{TOKEN}/getUpdates")]))
    with pytest.raises(notify.TelegramError) as ei:
        t.call("getMe")
    assert TOKEN not in str(ei.value)
    assert TOKEN not in explain.redact(f"url /bot{TOKEN}/x")
    assert TOKEN not in notify.scrub(f"token {TOKEN}")


def private(chat_id, text, user_id=None, date=None, ctype="private"):
    return {"update_id": 5, "message": {"message_id": 1, "date": int(date or time.time()), "text": text,
                                        "chat": {"id": chat_id, "type": ctype}, "from": {"id": user_id or chat_id, "is_bot": False}}}


def test_pair_allowlist(tmpdb):
    cfg = {"bot_token": TOKEN}
    notify.save_config(cfg)
    w = notify.open_pair_window(5)
    assert not notify.try_pair(private(-100, f"/pair {w['code']}", user_id=7, ctype="group"), w, cfg)
    assert not notify.try_pair(private(7, "/pair 000000" if w["code"] != "000000" else "/pair 111111"), w, cfg)
    assert not notify.try_pair(private(7, f"/pair {w['code']}", date=w["opened_t"] - 600), w, cfg)
    assert notify.try_pair(private(7, f"/pair {w['code']}"), w, cfg)
    saved = json.loads(notify.CONFIG.read_text())
    assert saved["owner_chat_id"] == 7 and saved["owner_user_id"] == 7 and saved["bot_token"] == TOKEN
    assert oct(os.stat(notify.CONFIG).st_mode & 0o777) == "0o600"
    assert notify.pair_window() is None
    assert bot.handle(private(8, "/help"), saved) is None
    assert bot.handle(private(7, "/help", ctype="group"), saved) is None
    assert bot.handle(private(7, "/help", user_id=9), saved) is None
    assert "read-only" in bot.handle(private(7, "/help"), saved)


def test_bot_commands_read_only(tmpdb):
    fail()
    cfg = {"bot_token": TOKEN, "owner_chat_id": 7, "owner_user_id": 7}
    out = bot.handle(private(7, "/issues"), cfg)
    assert "YouTube daily upload limit reached" in out
    iid = rows("SELECT id FROM issues")[0]["id"]
    assert "acknowledged" in bot.handle(private(7, f"/ack {iid}"), cfg)
    assert rows("SELECT status FROM issues")[0]["status"] == "acknowledged"
    assert "already" in bot.handle(private(7, f"/ack {iid}"), cfg)
    for cmd in ("/status", "/overview", "/queue", "/uploads", "/timeline", "/timeline C0004-hi", "/link", "/nonsense"):
        assert isinstance(bot.handle(private(7, cmd), cfg), str), cmd
    assert "Usage" in bot.handle(private(7, "/timeline ../../etc"), cfg)


def test_setup_rejects_bad_token(tmpdb):
    with pytest.raises(ValueError):
        notify.setup("not-a-token")


def test_first_start_skips_old_messages(tmpdb):
    cfg = {"bot_token": TOKEN, "owner_chat_id": 7}
    http = FakeHTTP([(200, {"ok": True, "result": [{"update_id": 41, "message": {"text": "hi"}}]}), (200, {"ok": True, "result": []})])
    b = bot.Bot(cfg, api(http))
    b.skip_backlog()
    assert b.state["offset"] == 42
    assert http.calls[0][1]["offset"] == -1 and http.calls[1][1]["offset"] == 42
    n = len(http.calls)
    b.skip_backlog()
    assert len(http.calls) == n
    assert bot.handle(private(7, "/help"), cfg)
