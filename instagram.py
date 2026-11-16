import getpass
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import requests

ROOT = Path(__file__).parent
SECRETS = ROOT / "secrets"
CFG = SECRETS / "instagram.json"
API_VERSION = "v27.0"
GRAPH = f"https://graph.instagram.com/{API_VERSION}"
FB_GRAPH = f"https://graph.facebook.com/{API_VERSION}"
HOST = "https://graph.instagram.com"
REFRESH_AFTER_DAYS = 20
MAX_BYTES = 300 * 1024 * 1024
TUNNEL_FAILED = 75


def secure_write(path, text):
    SECRETS.mkdir(mode=0o700, exist_ok=True)
    path.write_text(text)
    os.chmod(path, 0o600)


def fail(where, r):
    try:
        err = r.json().get("error", r.text)
    except ValueError:
        err = r.text
    sys.exit(f"Instagram API error during {where} (HTTP {r.status_code}): {err}")


def call(method, url, where, **kw):
    timeout = kw.pop("timeout", 60)
    headers = dict(kw.pop("headers", {}) or {})
    for key in ("params", "data"):
        if kw.get(key) and "access_token" in kw[key] and "/access_token" not in url and "/refresh_access_token" not in url:
            kw[key] = dict(kw[key])
            headers["Authorization"] = f"Bearer {kw[key].pop('access_token')}"
    last = None
    for attempt in range(6):
        try:
            r = requests.request(method, url, timeout=timeout, headers=headers, **kw)
            break
        except requests.ConnectionError as e:
            last = e
            if method != "GET" and not isinstance(e, requests.ConnectTimeout):
                sys.exit(f"Network error during {where} after the request may have reached Instagram; not retrying to avoid a duplicate. Check the account before retrying.")
            print(f"  network timeout during {where}; retrying ({attempt + 1}/5)", flush=True)
            time.sleep(10 * (attempt + 1))
    else:
        sys.exit(f"Network unreachable during {where}: {type(last).__name__}")
    if r.status_code >= 400:
        fail(where, r)
    return r.json()


def graph(cfg):
    return FB_GRAPH if cfg.get("host") == "facebook" else GRAPH


def load_config():
    if not CFG.exists():
        sys.exit(f"Missing {CFG}. Run: python instagram.py setup")
    cfg = json.loads(CFG.read_text())
    age_days = (time.time() - cfg.get("saved_at", 0)) / 86400
    if cfg.get("host") != "facebook" and age_days > REFRESH_AFTER_DAYS:
        cfg = refresh(cfg)
    return cfg


def refresh(cfg):
    d = call("GET", f"{HOST}/refresh_access_token", "token refresh", params={"grant_type": "ig_refresh_token", "access_token": cfg["access_token"]})
    cfg.update(access_token=d["access_token"], expires_in=d.get("expires_in"), saved_at=time.time())
    secure_write(CFG, json.dumps(cfg, indent=2))
    print(f"  Instagram token refreshed (valid ~{int(d.get('expires_in', 0)) // 86400} days)")
    return cfg


def setup():
    print("Paste the access token from the Meta app dashboard (input is hidden).")
    token = getpass.getpass("Token: ").strip()
    if not token:
        sys.exit("No token entered.")
    r = requests.get(f"{GRAPH}/me", params={"fields": "user_id,username,account_type", "access_token": token}, timeout=60)
    if r.status_code >= 400:
        return setup_facebook(token)
    app_secret = getpass.getpass("App secret, only if the token is short-lived (press Enter to skip): ").strip()
    expires_in = None
    if app_secret:
        d = call("GET", f"{HOST}/access_token", "long-lived token exchange", params={"grant_type": "ig_exchange_token", "client_secret": app_secret, "access_token": token})
        token, expires_in = d["access_token"], d.get("expires_in")
    me = call("GET", f"{GRAPH}/me", "account lookup", params={"fields": "user_id,username,account_type", "access_token": token})
    cfg = {"ig_user_id": me["user_id"], "username": me.get("username"), "account_type": me.get("account_type"), "access_token": token, "expires_in": expires_in, "saved_at": time.time()}
    secure_write(CFG, json.dumps(cfg, indent=2))
    print(f"Connected @{cfg['username']} ({cfg['account_type']}). Saved to {CFG} (mode 600).")
    if cfg["account_type"] not in ("BUSINESS", "MEDIA_CREATOR", "CREATOR"):
        print("Warning: publishing needs a Professional (Creator or Business) account.")


def setup_facebook(token):
    print("This is a Facebook-style token (Unified login / system user).")
    ig_id = input("Instagram account ID (Business settings > Accounts > Instagram accounts, or shown in the app configuration): ").strip()
    if not ig_id.isdigit():
        sys.exit("The Instagram account ID is a number.")
    me = call("GET", f"{FB_GRAPH}/{ig_id}", "account lookup", params={"fields": "id,username", "access_token": token})
    cfg = {"host": "facebook", "ig_user_id": me["id"], "username": me.get("username"), "account_type": "BUSINESS", "access_token": token, "expires_in": None, "saved_at": time.time()}
    secure_write(CFG, json.dumps(cfg, indent=2))
    print(f"Connected @{cfg['username']} via graph.facebook.com. Saved to {CFG} (mode 600).")


def status():
    cfg = load_config()
    me = call("GET", f"{graph(cfg)}/{cfg['ig_user_id']}", "account lookup", params={"fields": "username", "access_token": cfg["access_token"]})
    lim = call("GET", f"{graph(cfg)}/{cfg['ig_user_id']}/content_publishing_limit", "publishing limit", params={"fields": "quota_usage,config", "access_token": cfg["access_token"]})
    age = (time.time() - cfg.get("saved_at", 0)) / 86400
    print(f"@{me.get('username')} ({cfg.get('host', 'instagram')} host) · token age {age:.1f} days · publishing quota {json.dumps(lim.get('data', lim))}")


class _Handler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        self.send_error(404)
        return None

    def log_message(self, *args):
        pass


class PublicFiles:
    def __init__(self, files):
        self.files = [Path(f) for f in files]

    def __enter__(self):
        if not shutil.which("cloudflared"):
            sys.exit("cloudflared is not installed. Run: brew install cloudflared")
        self.tmp = Path(tempfile.mkdtemp(prefix="ig-share-"))
        key = secrets.token_urlsafe(24)
        (self.tmp / key).mkdir()
        names = []
        for f in self.files:
            name = secrets.token_hex(6) + f.suffix
            os.symlink(f.resolve(), self.tmp / key / name)
            names.append(name)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(_Handler, directory=str(self.tmp)))
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        port = self.server.server_address[1]
        self.proc = subprocess.Popen(["cloudflared", "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{port}"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        base = self._wait_url()
        self.urls = [f"{base}/{key}/{n}" for n in names]
        self._wait_reachable(self.urls[0])
        return self.urls

    def _wait_url(self):
        found = {}

        def reader():
            for line in self.proc.stderr:
                m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", line)
                if m and "url" not in found:
                    found["url"] = m.group(0)

        threading.Thread(target=reader, daemon=True).start()
        for _ in range(120):
            if "url" in found:
                return found["url"]
            if self.proc.poll() is not None:
                break
            time.sleep(0.5)
        self.__exit__(None, None, None)
        print("Could not start the temporary tunnel (cloudflared gave no URL).", file=sys.stderr)
        sys.exit(TUNNEL_FAILED)

    def _wait_reachable(self, url):
        for _ in range(45):
            try:
                if requests.head(url, timeout=10).status_code == 200:
                    return
            except requests.RequestException:
                pass
            time.sleep(2)
        self.__exit__(None, None, None)
        print("The temporary tunnel never became reachable.", file=sys.stderr)
        sys.exit(TUNNEL_FAILED)

    def __exit__(self, *exc):
        if getattr(self, "proc", None) and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        if getattr(self, "server", None):
            self.server.shutdown()
            self.server.server_close()
        shutil.rmtree(getattr(self, "tmp", ""), ignore_errors=True)


def duration(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)], capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def cover_jpeg(thumbnail, out_dir):
    from PIL import Image

    p = Path(out_dir) / "cover.jpg"
    Image.open(thumbnail).convert("RGB").save(p, "JPEG", quality=90)
    return p


def already_published(video, log):
    if not Path(log).exists():
        return None
    for e in json.loads(Path(log).read_text()):
        if e.get("platform") == "instagram" and Path(e.get("video", "")).name == Path(video).name and e.get("id"):
            return e
    return None


EXTRA_FIELDS = ("audio_name", "is_ai_generated", "trial_params", "collaborators", "location_id")


def publish(video, caption, thumbnail=None, thumb_offset_ms=0, dry_run=False, confirm=None, extra=None):
    video = Path(video)
    size = video.stat().st_size
    secs = duration(video)
    if size > MAX_BYTES:
        sys.exit(f"Reel is {size / 1e6:.0f} MB; Instagram allows 300 MB.")
    if not 3 <= secs <= 900:
        sys.exit(f"Reel is {secs:.1f}s; Instagram allows 3 s to 15 min.")
    cfg = load_config()
    if confirm:
        confirm(f"Instagram Reel ({'DRY RUN, nothing is posted' if dry_run else 'PUBLIC as soon as it finishes'})\n  file:    {video} ({size / 1e6:.0f} MB, {secs:.1f}s)\n  account: @{cfg.get('username')}\n  caption: {caption[:90]}...\n  extras:  {json.dumps({k: v for k, v in (extra or {}).items() if k in EXTRA_FIELDS}, ensure_ascii=False)}")
    work = Path(tempfile.mkdtemp(prefix="ig-cover-"))
    try:
        files = [video] + ([cover_jpeg(thumbnail, work)] if thumbnail else [])
        with PublicFiles(files) as urls:
            print("  temporary link is live; Instagram can fetch the video", flush=True)
            if dry_run:
                call("GET", f"{graph(cfg)}/{cfg['ig_user_id']}", "account lookup", params={"fields": "username", "access_token": cfg["access_token"]})
                print("  dry run OK: token valid, tunnel reachable, file within limits. Nothing was posted.")
                return None
            data = {"media_type": "REELS", "video_url": urls[0], "caption": caption, "share_to_feed": "true", "access_token": cfg["access_token"]}
            for k in EXTRA_FIELDS:
                v = (extra or {}).get(k)
                if v not in (None, "", []):
                    data[k] = json.dumps(v) if isinstance(v, (dict, list)) else ("true" if v is True else str(v))
            if len(urls) > 1:
                data["cover_url"] = urls[1]
            else:
                data["thumb_offset"] = str(thumb_offset_ms)
            cid = call("POST", f"{graph(cfg)}/{cfg['ig_user_id']}/media", "container creation", data=data)["id"]
            print(f"  container {cid} created; waiting for Instagram to process", flush=True)
            for _ in range(120):
                s = call("GET", f"{graph(cfg)}/{cid}", "status check", params={"fields": "status_code,status", "access_token": cfg["access_token"]})
                if s.get("status_code") == "FINISHED":
                    break
                if s.get("status_code") in ("ERROR", "EXPIRED"):
                    sys.exit(f"Instagram processing failed: {s}")
                time.sleep(10)
            else:
                sys.exit(f"Instagram processing timed out; container {cid}")
        print("  processed; temporary link closed", flush=True)
        mid = call("POST", f"{graph(cfg)}/{cfg['ig_user_id']}/media_publish", "publish", data={"creation_id": cid, "access_token": cfg["access_token"]})["id"]
        info = call("GET", f"{graph(cfg)}/{mid}", "permalink lookup", params={"fields": "permalink,media_product_type,timestamp", "access_token": cfg["access_token"]})
        print(f"  published: {info.get('permalink') or mid}")
        return {"platform": "instagram", "id": mid, "url": info.get("permalink"), "privacy": "public", "media_product_type": info.get("media_product_type"), "time": info.get("timestamp") or time.strftime("%Y-%m-%dT%H:%M:%S")}
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "setup":
        setup()
    elif cmd == "status":
        status()
    else:
        sys.exit("usage: python instagram.py setup|status")
