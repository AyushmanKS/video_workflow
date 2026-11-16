import http.client
import json
import os
import re
import sqlite3
import stat
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import dashboard, dashui, db, episodes, events, monitor, notify

LIVE_DB = db.DB_PATH


JARGON = ["variant", "outbox", "task_state", "sha256"]


def assert_no_jargon(body, where=""):
    low = body.lower()
    for w in JARGON:
        assert w not in low, (where, w)
    for w in ("G1", "G2", "G3"):
        assert not re.search(rf"\b{w}\b", body), (where, w)
    assert not re.search(r"\blint\b", body, re.I), (where, "lint")
    assert not re.search(r">[^<]*\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", body), (where, "iso time")
    assert "style=" not in body, (where, "inline style")


def keyfiles(tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard, "KEYFILE", tmp_path / "secrets" / "dashboard.json")
    monkeypatch.setattr(dashboard, "URLFILE", tmp_path / "dashboard_url.json")
    monkeypatch.setattr(dashboard, "_keys", {"mtime": None, "data": None})
    monkeypatch.setattr(notify, "CONFIG", tmp_path / "secrets" / "telegram.json")


@pytest.fixture
def tmpdb(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(db, "DATA", tmp_path)
    monkeypatch.setattr(events, "_ready", set())
    monkeypatch.setattr(events, "_workflows", {})
    keyfiles(tmp_path, monkeypatch)
    events.clear_context()
    with db.connect():
        pass
    events.emit("info", "system", "seed")
    yield tmp_path
    events.clear_context()


def serve():
    srv = dashboard.make_server(0)
    threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.2}, daemon=True).start()
    return srv


@pytest.fixture
def server(tmpdb):
    srv = serve()
    yield srv
    srv.app.feed.stop.set()
    srv.shutdown()
    srv.server_close()


def req(srv, path, method="GET", cookie=None, body=None, headers=None, ip=None):
    c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=10)
    h = dict(headers or {})
    if cookie:
        h["Cookie"] = f"{dashboard.COOKIE}={cookie}"
    if ip:
        h["CF-Connecting-IP"] = ip
    if body is not None:
        h["Content-Type"] = "application/x-www-form-urlencoded"
    c.request(method, path, body=body, headers=h)
    r = c.getresponse()
    data = r.read().decode("utf-8", "replace")
    c.close()
    return r, data


def login(srv, ip="10.0.0.1"):
    r, _ = req(srv, f"/login?k={dashboard.keys()['login_key']}", ip=ip)
    assert r.status == 200
    sc = r.getheader("Set-Cookie")
    return re.search(rf"{dashboard.COOKIE}=([^;]+)", sc).group(1), sc


def test_no_cookie_is_401_everywhere(server):
    for path in ("/", "/progress", "/uploads", "/problems", "/results", "/episode/C0001", "/projects", "/queue", "/issues", "/timeline", "/analytics"):
        r, body = req(server, path)
        assert r.status == 401 and "Sign-in needed" in body, path
    r, body = req(server, "/api/events")
    assert r.status == 401 and json.loads(body)["error"]
    r, _ = req(server, "/events/stream")
    assert r.status == 401
    r, _ = req(server, "/issues/1/ack", "POST", body="csrf=x")
    assert r.status == 401


def test_login_sets_strict_cookie_and_pages_work(server):
    cookie, sc = login(server)
    for flag in ("HttpOnly", "Secure", "SameSite=Lax", "Max-Age=2592000", "Path=/"):
        assert flag in sc
    r, body = req(server, "/", cookie=cookie)
    assert r.status == 200 and "Needs you" in body and 'name="viewport"' in body
    assert r.getheader("Content-Security-Policy").startswith("default-src 'self'")
    assert r.getheader("X-Frame-Options") == "DENY" and r.getheader("Referrer-Policy") == "no-referrer"
    assert r.getheader("Cache-Control") == "no-store"


def test_wrong_key_tampered_and_expired_cookie(server):
    r, _ = req(server, "/login?k=wrong", ip="10.0.0.2")
    assert r.status == 403
    cookie, _ = login(server, ip="10.0.0.3")
    exp, nonce, sig = cookie.split(".")
    assert req(server, "/", cookie=f"{exp}.{nonce}.{'0' * len(sig)}")[0].status == 401
    assert req(server, "/", cookie=f"{int(exp) + 5}.{nonce}.{sig}")[0].status == 401
    old = dashboard.make_session(now=time.time() - dashboard.SESSION_S - 10)
    assert req(server, "/", cookie=old)[0].status == 401
    dashboard.rotate_key()
    assert req(server, "/", cookie=cookie)[0].status == 401


def test_failed_login_rate_limit(server):
    for _ in range(dashboard.FAIL_PER_IP):
        assert req(server, "/login?k=nope", ip="10.9.9.9")[0].status == 403
    r, _ = req(server, f"/login?k={dashboard.keys()['login_key']}", ip="10.9.9.9")
    assert r.status == 429 and r.getheader("Retry-After")
    assert req(server, f"/login?k={dashboard.keys()['login_key']}", ip="10.9.9.8")[0].status == 200


def test_global_rate_limit():
    lim = dashboard.Limiter()
    for i in range(dashboard.FAIL_GLOBAL):
        lim.fail(f"ip{i}", now=100)
    assert lim.blocked("fresh", now=101)
    assert not lim.blocked("fresh", now=100 + dashboard.FAIL_WINDOW_S + 1)


def test_static_whitelist_and_no_traversal(server):
    for path in ("/static/app.css", "/static/app.js", "/manifest.webmanifest", "/sw.js", "/icon-192.png", "/icon-512.png", "/offline.html", "/healthz"):
        assert req(server, path)[0].status == 200, path
    for path in ("/static/../secrets/telegram.json", "/secrets/telegram.json", "/data/studio.db", "/static/", "/pipeline/dashboard.py", "/%2e%2e/secrets", "/.git/config"):
        assert req(server, path)[0].status in (401, 404), path
    r, body = req(server, "/manifest.webmanifest")
    m = json.loads(body)
    assert m["display"] == "standalone" and {i["sizes"] for i in m["icons"]} == {"192x192", "512x512"}
    r, _ = req(server, "/icon-512.png")
    assert r.getheader("Content-Type") == "image/png"


def test_ack_requires_csrf_and_same_origin(server):
    events.emit("failed", "publish", "upload failed", variant_id="C0009-hi", platform="youtube", error_code="youtube_quota")
    iid = sqlite3.connect(db.DB_PATH).execute("SELECT id FROM issues").fetchone()[0]
    cookie, _ = login(server)
    r, page = req(server, "/problems", cookie=cookie)
    assert r.status == 200 and "daily allowance is used up" in page
    csrf = re.search(r'name="csrf" value="([^"]+)"', page).group(1)
    assert req(server, f"/issues/{iid}/ack", "POST", cookie=cookie, body="csrf=bad")[0].status == 403
    assert req(server, f"/issues/{iid}/ack", "POST", cookie=cookie, body=f"csrf={csrf}", headers={"Origin": "https://evil.example"})[0].status == 403
    r, _ = req(server, f"/issues/{iid}/ack", "POST", cookie=cookie, body=f"csrf={csrf}", headers={"Origin": f"http://127.0.0.1:{server.server_address[1]}"})
    assert r.status == 303
    assert sqlite3.connect(db.DB_PATH).execute("SELECT status FROM issues").fetchone()[0] == "acknowledged"
    other, _ = login(server, ip="10.0.0.5")
    assert req(server, f"/issues/{iid}/ack", "POST", cookie=other, body=f"csrf={csrf}")[0].status == 403


def test_keyfile_is_private(tmpdb):
    dashboard.keys()
    assert stat.S_IMODE(os.stat(dashboard.KEYFILE).st_mode) == 0o600
    assert len(dashboard.keys()["login_key"]) >= 43


@pytest.mark.skipif(not LIVE_DB.exists(), reason="no live database")
def test_pages_render_with_live_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", LIVE_DB)
    keyfiles(tmp_path, monkeypatch)
    srv = serve()
    try:
        cookie, _ = login(srv)
        con = sqlite3.connect(f"file:{LIVE_DB}?mode=ro", uri=True)
        some_variant = con.execute("SELECT id FROM variants ORDER BY id LIMIT 1").fetchone()[0]
        con.close()
        cid = some_variant.rsplit("-", 1)[0]
        expect = {"/": "Needs you", "/progress": "episodes", "/uploads": "Coming up", "/problems": "Problems", f"/episode/{cid}": "Steps",
                  "/results": "How videos are doing", f"/results?ep={cid}": "Episode"}
        for path, needle in expect.items():
            r, body = req(srv, path, cookie=cookie)
            assert r.status == 200, path
            assert needle in body, path
            assert "/Users/" not in body and "secrets/" not in body, path
            assert_no_jargon(body, path)
        for old, new in (("/timeline", "/progress"), ("/issues", "/problems"), ("/analytics", "/results"), ("/queue", "/progress"), ("/projects", "/progress")):
            r, _ = req(srv, old, cookie=cookie)
            assert r.status == 302 and r.getheader("Location") == new
        r, body = req(srv, "/api/overview", cookie=cookie)
        assert r.status == 200 and "active_projects" in json.loads(body)
    finally:
        srv.app.feed.stop.set()
        srv.shutdown()
        srv.server_close()


def test_sse_delivers_new_event(server):
    cookie, _ = login(server)
    c = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=20)
    c.request("GET", "/events/stream", headers={"Cookie": f"{dashboard.COOKIE}={cookie}"})
    r = c.getresponse()
    assert r.status == 200 and r.getheader("Content-Type").startswith("text/event-stream")
    r.fp.readline()
    threading.Timer(0.5, lambda: events.emit("progress", "voice", "voice 3/12 sse-check", variant_id="C0009-hi", progress=0.25)).start()
    deadline = time.time() + 15
    got = None
    while time.time() < deadline:
        line = r.fp.readline().decode()
        if line.startswith("data: ") and "sse-check" in line:
            got = json.loads(line[6:])
            break
    c.close()
    assert got and got["kind"] == "progress" and got["variant"] == "C0009-hi" and got["progress"] == 0.25


def test_api_events_polling_fallback(server):
    cookie, _ = login(server)
    r, body = req(server, "/api/events?after=0", cookie=cookie)
    first = json.loads(body)["events"]
    events.emit("info", "voice", "poll-check", variant_id="C0009-hi")
    r, body = req(server, f"/api/events?after={first[-1]['rowid']}", cookie=cookie)
    assert [x["message"] for x in json.loads(body)["events"]] == ["poll-check"]


LINES = [
    "2026-11-16T17:00:00Z INF Thank you for trying Cloudflare Tunnel. Doing so, without a Cloudflare account, is a quick way to experiment",
    "2026-11-16T17:00:01Z INF |  https://brave-otter-pixel-sample.trycloudflare.com                                      |",
    "2026-11-16T17:00:01Z INF Requesting new quick Tunnel on trycloudflare.com...",
]


def test_tunnel_url_parsing():
    assert dashboard.parse_tunnel_url(LINES[0]) is None
    assert dashboard.parse_tunnel_url(LINES[1]) == "https://brave-otter-pixel-sample.trycloudflare.com"
    assert dashboard.parse_tunnel_url(LINES[2]) is None
    assert dashboard.parse_tunnel_url("https://evil.com/?x=https://a.trycloudflare.com.evil.com") == "https://a.trycloudflare.com"


def test_tunnel_spawn_publish_and_announce(tmpdb, tmp_path):
    fake = tmp_path / "fakecf"
    fake.write_text("#!/bin/sh\necho 'INF Requesting new quick Tunnel' >&2\necho 'INF |  https://unit-test-host.trycloudflare.com  |' >&2\nexec sleep 30\n")
    fake.chmod(0o755)
    t = dashboard.Tunnel(1234, binary=str(fake))
    try:
        url = t.spawn()
        assert url == "https://unit-test-host.trycloudflare.com"
        t.publish(url)
        info = json.loads(dashboard.URLFILE.read_text())
        assert info["url"] == url and info["cloudflared_pid"] == t.proc.pid
        out = sqlite3.connect(db.DB_PATH).execute("SELECT payload FROM outbox WHERE event_id LIKE 'local:%'").fetchall()
        assert len(out) == 1 and "/login?k=" in json.loads(out[0][0])["html"]
        t.publish(url)
        assert len(sqlite3.connect(db.DB_PATH).execute("SELECT payload FROM outbox WHERE event_id LIKE 'local:%'").fetchall()) == 1
    finally:
        t.close()
    assert t.proc.poll() is not None


def test_tunnel_clients_get_polling_not_sse(server):
    cookie, _ = login(server)
    r, body = req(server, "/", cookie=cookie, ip="203.0.113.9")
    assert r.status == 200 and 'data-sse="0"' in body
    r, body = req(server, "/", cookie=cookie)
    assert 'data-sse="1"' in body
    r, body = req(server, "/events/stream", cookie=cookie, ip="203.0.113.9")
    assert r.status == 409 and "poll" in body


def test_ack_can_clear_a_group(server):
    events.emit("failed", "publish", "upload failed", variant_id="C0009-hi", platform="youtube", error_code="youtube_quota")
    events.emit("failed", "publish", "upload failed", variant_id="C0009-en", platform="youtube", error_code="youtube_quota")
    ids = [r[0] for r in sqlite3.connect(db.DB_PATH).execute("SELECT id FROM issues ORDER BY id")]
    cookie, _ = login(server)
    r, page = req(server, "/problems", cookie=cookie)
    csrf = re.search(r'name="csrf" value="([^"]+)"', page).group(1)
    r, _ = req(server, f"/issues/{ids[0]}/ack", "POST", cookie=cookie, body=f"csrf={csrf}&ids={ids[0]},{ids[1]}")
    assert r.status == 303 and r.getheader("Location") == "/problems"
    assert {x[0] for x in sqlite3.connect(db.DB_PATH).execute("SELECT status FROM issues")} == {"acknowledged"}
    r, page = req(server, "/problems", cookie=cookie)
    assert "Known, no action needed" in page and "Nothing needs you" in page


def test_main_pages_have_no_jargon(server):
    events.emit("failed", "video_qa", "QA verdict fail (report #3)", variant_id="C0009-hi", error_code="qa_fail", error="QA verdict fail G2 sha256 abc")
    cookie, _ = login(server)
    for path in ("/", "/progress", "/uploads", "/problems", "/results"):
        r, body = req(server, path, cookie=cookie)
        assert r.status == 200, path
        assert 'name="viewport" content="width=device-width' in body
        assert_no_jargon(body, path)
    r, _ = req(server, "/episode/C9999", cookie=cookie)
    assert r.status == 404


def test_css_is_mobile_safe(server):
    _, css = req(server, "/static/app.css")
    assert "max-width:640px" in css and "prefers-color-scheme:light" in css and "min-height:44px" in css
    assert "overflow-x:hidden" in css and "@import" not in css and "http" not in css


PLAN = {"goal_episodes": 150, "milestones": [{"name": "Bala Kanda", "planned": 18}, {"name": "Ayodhya Kanda", "planned": 28}, {"name": "Aranya Kanda", "planned": 17},
                                             {"name": "Kishkindha Kanda", "planned": 16}, {"name": "Sundara Kanda", "planned": 16}, {"name": "Yuddha Kanda", "planned": 30},
                                             {"name": "Uttara Kanda", "planned": 25}]}


def fake_ep(n, base, done=False, milestone=None):
    return {"id": f"C{n:04d}", "episode": n, "milestone": milestone, "status": {"base": base, "done": done}}


def test_milestone_math():
    eps = [fake_ep(i, "scheduled") for i in range(1, 8)]
    pr = episodes.progress(eps, episodes.project_plan(PLAN))
    assert (pr["made"], pr["goal"], pr["pct"], pr["to_go"], pr["not_started"]) == (7, 150, 5, 143, 143)
    bala = pr["milestones"][0]
    assert (bala["name"], bala["made"], bala["planned"], bala["to_go"]) == ("Bala Kanda", 7, 18, 11)
    assert pr["current"] == 0 and all(m["made"] == 0 for m in pr["milestones"][1:])
    assert episodes.milestone_index(fake_ep(19, "idea"), PLAN["milestones"]) == 1
    assert episodes.milestone_index(fake_ep(150, "idea"), PLAN["milestones"]) == 6
    assert episodes.milestone_index(fake_ep(3, "idea", milestone="Sundara Kanda"), PLAN["milestones"]) == 4
    eps.append(fake_ep(8, "making"))
    pr = episodes.progress(eps, episodes.project_plan(PLAN))
    assert (pr["made"], pr["working"], pr["milestones"][0]["working"]) == (7, 1, 1)
    assert episodes.progress(eps, episodes.project_plan({}))["goal"] is None


def manifest(stages, langs=("en", "hi"), platforms=("youtube", "instagram")):
    return {"id": "C0999", "languages": list(langs), "platforms": list(platforms), "stages": stages}


def approved(langs):
    return {"status": "approved", "entries": {l: {"status": "approved"} for l in langs}}


def ctx(pubs=None, queue=None, issues=None, jobs=None, m=None):
    return {"pubs": pubs or {}, "queue": queue or {}, "issues": issues or {}, "running": {}, "jobs": jobs or {}, "manifests": {"C0999": m or {}}}


def status_of(m, c, now=1_800_000_000):
    langs = [episodes.lang_status(m, l, c, now) for l in m["languages"]]
    return episodes.overall(langs, now), langs


def test_episode_status_cases():
    now = 1_800_000_000
    m = manifest({"research": {"status": "done"}})
    assert status_of(m, ctx(m=m))[0]["label"] == "Writing"
    assert status_of(manifest({}), ctx())[0]["label"] == "Idea"
    st = {"script:en": {"status": "done"}, "script:hi": {"status": "done"}}
    m = manifest(st)
    ov, _ = status_of(m, ctx(m=m))
    assert ov["label"] == "Waiting for your OK (script)" and ov["tone"] == "wait"
    st.update({"gate:script": approved(["en", "hi"]), "voice:en": {"status": "done"}, "voice:hi": {"status": "done"}})
    m = manifest(st)
    ov, langs = status_of(m, ctx(m=m))
    assert ov["label"] == "Making video" and langs[0]["current"] == "pictures"
    for l in ("en", "hi"):
        st.update({f"images:{l}": {"status": "done"}, f"render:{l}": {"status": "done"}, f"video_qa:{l}": {"status": "done", "note": "warn (report #1)"}})
    m = manifest(st)
    assert status_of(m, ctx(m=m))[0]["label"] == "Waiting for your OK (video)"
    st["gate:final"] = approved(["en", "hi"])
    m = manifest(st)
    assert status_of(m, ctx(m=m))[0]["label"] == "Ready to post"
    iso = lambda t: time.strftime("%Y-%m-%dT%H:%M:%S+0000", time.gmtime(t))
    row = lambda sched=None, pub=None: {"scheduled_for": sched, "published_at": pub, "url": "https://example.com/x"}
    pubs = {("C0999-en", "youtube"): [row(sched=iso(now + 3600))], ("C0999-hi", "youtube"): [row(sched=iso(now + 7200))]}
    jobs = {"C0999-en": {"t": now + 1800}, "C0999-hi": {"t": now + 5400}}
    ov, _ = status_of(m, ctx(pubs=pubs, jobs=jobs, m=m), now)
    assert ov["label"] == "Scheduled" and ov["text"].startswith("First post") and not ov["done"]
    pubs[("C0999-en", "youtube")] = [row(sched=iso(now - 60))]
    pubs[("C0999-en", "instagram")] = [row(pub=iso(now - 30))]
    jobs.pop("C0999-en")
    ov, _ = status_of(m, ctx(pubs=pubs, jobs=jobs, m=m), now)
    assert ov["label"] == "Partly live" and ov["partial"] and not ov["done"] and ov["text"].startswith("Posted on ") and ov["live_counts"] == {"youtube": (1, 2), "instagram": (1, 2)}
    pubs[("C0999-hi", "youtube")] = [row(pub=iso(now - 60))]
    pubs[("C0999-hi", "instagram")] = [row(pub=iso(now - 30))]
    ov, _ = status_of(m, ctx(pubs=pubs, m=m), now)
    assert ov["label"] == "Live" and ov["done"] and ov["text"].startswith("Posted everywhere")
    queue = {("C0999-hi", "youtube"): {"status": "failed", "publish_at": iso(now - 600), "last_error": "boom", "updated_at": iso(now)}}
    pubs.pop(("C0999-hi", "youtube"))
    ov, _ = status_of(m, ctx(pubs=pubs, queue=queue, m=m), now)
    assert ov["label"] == "Problem" and ov["tone"] == "bad" and ov["text"].startswith("Hindi")
    limit = {"id": 1, "status": "open", "severity": "recoverable", "stage": "publish", "platform": "youtube", "error_code": "youtube_upload_limit", "title": "YouTube daily upload limit reached"}
    queue = {("C0999-hi", "youtube"): {"status": "waiting", "publish_at": iso(now + 600), "last_error": "daily cap", "updated_at": iso(now)}}
    ov, langs = status_of(m, ctx(pubs=pubs, queue=queue, issues={"C0999-hi": [limit]}, m=m), now)
    assert ov["label"] == "Partly live" and not langs[1]["problems"] and 1 not in langs[1]["relevant"]
    ack = dict(limit, error_code="qa_fail", stage="video_qa", status="acknowledged")
    ov, langs = status_of(m, ctx(pubs=pubs, queue=queue, issues={"C0999-hi": [ack]}, m=m), now)
    assert ov["label"] == "Partly live" and not langs[1]["problems"]


def test_coming_up_puts_no_deadline_last():
    ep = {"id": "C0001", "episode": 1, "langs": [
        {"name": "Gujarati", "platforms": {"youtube": {"state": "waiting", "t": None, "held": True}}},
        {"name": "Telugu", "platforms": {"youtube": {"state": "scheduled", "t": 200.0}, "instagram": {"state": "scheduled", "t": 100.0}}}]}
    order = [(x["lang"]["name"], x["platform"]) for x in dashui.coming_up([ep])]
    assert order == [("Telugu", "instagram"), ("Telugu", "youtube"), ("Gujarati", "youtube")]


def test_friendly_times():
    now = episodes.to_dt("2026-11-17T12:00:00+05:30").timestamp()
    assert episodes.when("2026-11-17T20:00:00+05:30", now) == "Today 8:00 pm"
    assert episodes.when("2026-11-16T22:42:00+05:30", now) == "Yesterday 10:42 pm"
    assert episodes.when("2026-11-19T19:00:00+05:30", now) == "Thu 19 Nov, 7:00 pm"
    assert episodes.when("2026-11-18T02:00:00Z", now) == "Tomorrow 7:30 am"
    assert episodes.plain("QA failed for C0007-hi after G2") == "quality check failed for Ep 7 Hindi after video approval"


def test_failed_task_with_known_issue_is_not_counted(tmpdb):
    events.emit("failed", "video_qa", "QA verdict fail (report #3)", variant_id="C0009-en", status="Failed", error_code="qa_fail")
    con = events.connect()
    assert monitor.overview(con)["failed_tasks"] == 1
    iid = con.execute("SELECT id FROM issues").fetchone()[0]
    monitor.resolve_issue(con, iid, "seen", "acknowledged")
    assert monitor.overview(con)["failed_tasks"] == 0
    con.close()


def test_publish_approval_resolves_gate_refusal(tmpdb):
    events.emit("warning", "publish", "Refused: video changed after G2", variant_id="C0009-hi", platform="youtube", error_code="gate_refused")
    events.emit("warning", "publish", "Refused: video changed after G2", variant_id="C0009-en", platform="youtube", error_code="gate_refused")
    events.emit("approved", "gate:publish:instagram", "owner approved", variant_id="C0009-hi")
    con = events.connect()
    assert {r[0]: r[1] for r in con.execute("SELECT variant_id, status FROM issues")} == {"C0009-hi": "open", "C0009-en": "open"}
    events.emit("approved", "gate:publish:youtube", "owner approved", variant_id="C0009-hi")
    assert {r[0]: r[1] for r in con.execute("SELECT variant_id, status FROM issues")} == {"C0009-hi": "resolved", "C0009-en": "open"}
    con.close()
