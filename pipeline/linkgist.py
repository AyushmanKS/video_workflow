import base64
import json
import os

from . import DATA, ROOT, db

TOKENFILE = ROOT / "secrets" / "github_gist.json"
STATE = DATA / "dashboard_gist.json"
FILENAME = "chalk-dashboard.json"
API = "https://api.github.com"


def token():
    try:
        return json.loads(TOKENFILE.read_text()).get("token") or None
    except (OSError, ValueError):
        return None


def configured():
    return token() is not None


def state():
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {}


def save_state(d):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, indent=2))
    os.chmod(tmp, 0o600)
    os.replace(tmp, STATE)


def headers(tok):
    return {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "chalk-dashboard"}


def sync(url, log=print):
    import requests

    tok = token()
    if not tok:
        return False
    st = state()
    if st.get("url") == url and st.get("id"):
        return True
    body = {"files": {FILENAME: {"content": json.dumps({"url": url, "updated": db.now()})}}}
    try:
        if st.get("id"):
            r = requests.patch(f"{API}/gists/{st['id']}", headers=headers(tok), json=body, timeout=15)
            if r.status_code == 404:
                st.pop("id", None)
        if not st.get("id"):
            body.update(description="Chalk Tales dashboard address", public=False)
            r = requests.post(f"{API}/gists", headers=headers(tok), json=body, timeout=15)
        if r.status_code not in (200, 201):
            log(f"gist update failed: HTTP {r.status_code}")
            return False
        st.update(id=r.json()["id"], url=url, synced_at=db.now())
        save_state(st)
        log("gist updated with the new dashboard address")
        return True
    except requests.RequestException as ex:
        log(f"gist update failed: {type(ex).__name__}")
        return False


def synced(url):
    st = state()
    return bool(st.get("id")) and st.get("url") == url


def setup_code(login_key):
    gid = state().get("id")
    if not gid:
        return None
    raw = json.dumps({"g": gid, "k": login_key}, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")
