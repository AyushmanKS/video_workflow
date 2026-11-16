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

from pipeline import dashboard, db, events, notify

LIVE_DB = db.DB_PATH


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
    assert r.status == 303
    sc = r.getheader("Set-Cookie")
    return re.search(rf"{dashboard.COOKIE}=([^;]+)", sc).group(1), sc


def test_no_cookie_is_401_everywhere(server):
    for path in ("/", "/projects", "/queue", "/uploads", "/issues", "/timeline", "/analytics"):
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
    for flag in ("HttpOnly", "Secure", "SameSite=Strict", "Max-Age=2592000", "Path=/"):
        assert flag in sc
    r, body = req(server, "/", cookie=cookie)
    assert r.status == 200 and "Active projects" in body
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
    assert req(server, f"/login?k={dashboard.keys()['login_key']}", ip="10.9.9.8")[0].status == 303


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
    r, page = req(server, "/issues", cookie=cookie)
    assert r.status == 200 and "YouTube API quota used up" in page
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
        expect = {"/": "Active projects", "/projects": "Next scheduled", "/queue": some_variant, "/uploads": "YouTube queue", "/issues": "Issues",
                  "/timeline": "feed", f"/timeline?video={some_variant}": f"History of {some_variant}", "/analytics": "Latest snapshot per video",
                  "/queue?lang=hi&status=completed": "videos", "/issues?all=1": "Issues"}
        for path, needle in expect.items():
            r, body = req(srv, path, cookie=cookie)
            assert r.status == 200, path
            assert needle in body, path
            assert "/Users/" not in body and "secrets/" not in body, path
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
    r, body = req(server, "/timeline", cookie=cookie, ip="203.0.113.9")
    assert r.status == 200 and 'data-sse="0"' in body
    r, body = req(server, "/timeline", cookie=cookie)
    assert 'data-sse="1"' in body
    r, body = req(server, "/events/stream", cookie=cookie, ip="203.0.113.9")
    assert r.status == 409 and "poll" in body
