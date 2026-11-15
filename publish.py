import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).parent
SECRETS = ROOT / "secrets"
YT_SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
ANALYTICS_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/yt-analytics.readonly"]
GRAPH = "https://graph.facebook.com/v25.0"


def confirm(summary, assume_yes):
    print("\n" + summary + "\n")
    if assume_yes:
        return
    if input("Type 'yes' to continue: ").strip().lower() != "yes":
        sys.exit("Cancelled. Nothing was uploaded.")


def secure_write(path, text):
    SECRETS.mkdir(mode=0o700, exist_ok=True)
    path.write_text(text)
    os.chmod(path, 0o600)


def google_credentials(scopes, token_name):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    client = SECRETS / "youtube_client_secret.json"
    token = SECRETS / token_name
    if not client.exists():
        sys.exit(f"Missing {client}. Follow the YouTube setup steps in docs/PUBLISHING.md first.")
    creds = Credentials.from_authorized_user_file(str(token), scopes) if token.exists() else None
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            creds = None
    if not creds or not creds.valid:
        creds = InstalledAppFlow.from_client_secrets_file(str(client), scopes).run_local_server(port=0)
    secure_write(token, creds.to_json())
    return creds


def youtube_service():
    from googleapiclient.discovery import build

    return build("youtube", "v3", credentials=google_credentials(YT_SCOPES, "youtube_token.json"))


def analytics_services():
    from googleapiclient.discovery import build

    creds = google_credentials(ANALYTICS_SCOPES, "youtube_analytics_token.json")
    return build("youtube", "v3", credentials=creds), build("youtubeAnalytics", "v2", credentials=creds)


def find_playlist(svc, title):
    req = svc.playlists().list(part="snippet", mine=True, maxResults=50)
    while req is not None:
        resp = req.execute()
        for item in resp.get("items", []):
            if item["snippet"]["title"].strip().lower() == title.strip().lower():
                return item["id"]
        req = svc.playlists().list_next(req, resp)
    return None


def youtube_upload(video, meta, thumb, privacy, assume_yes, publish_at=None):
    from googleapiclient.http import MediaFileUpload

    yt = meta["youtube"]
    if len(yt["title"]) > 100:
        sys.exit(f"Title is {len(yt['title'])} characters; YouTube allows 100.")
    if publish_at:
        privacy = "private"
    confirm(
        f"YouTube upload\n  file:     {video}\n  title:    {yt['title']}\n  privacy:  {privacy}\n"
        f"  schedule: {publish_at or 'none'}\n"
        f"  playlist: {yt.get('playlist') or '-'}\n  language: {yt.get('language')}\n"
        "  note:     uploads from an unaudited API project are locked private by YouTube",
        assume_yes,
    )
    svc = youtube_service()
    body = {
        "snippet": {
            "title": yt["title"],
            "description": yt["description"],
            "tags": yt.get("tags", []),
            "categoryId": str(yt.get("category", 27)),
            "defaultLanguage": yt.get("language"),
            "defaultAudioLanguage": yt.get("language"),
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": bool(yt.get("synthetic", False)),
        },
    }
    if publish_at:
        body["status"]["publishAt"] = publish_at
    req = svc.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(str(video), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"  uploaded {status.progress() * 100:.0f}%", flush=True)
    vid = resp["id"]
    result = {"platform": "youtube", "id": vid, "url": f"https://www.youtube.com/shorts/{vid}", "privacy": resp["status"]["privacyStatus"], "scheduled_for": resp["status"].get("publishAt"), "time": time.strftime("%Y-%m-%d %H:%M:%S")}
    print(f"  uploaded: {result['url']} (privacy reported: {result['privacy']})")
    if yt.get("playlist"):
        pid = find_playlist(svc, yt["playlist"])
        if pid:
            svc.playlistItems().insert(part="snippet", body={"snippet": {"playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
            result["playlist"] = pid
            print(f"  added to playlist '{yt['playlist']}'")
        else:
            print(f"  playlist '{yt['playlist']}' not found; skipped")
    if thumb and Path(thumb).exists():
        try:
            svc.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb), mimetype="image/png")).execute()
            result["thumbnail"] = "set"
            print("  thumbnail set")
        except Exception as e:
            result["thumbnail"] = f"not set: {e}"
            print(f"  thumbnail not set ({str(e)[:160]})")
    return result


def instagram_publish(video, meta, assume_yes):
    cfg_path = SECRETS / "instagram.json"
    if not cfg_path.exists():
        sys.exit(f"Missing {cfg_path}. Follow the Instagram setup steps in docs/PUBLISHING.md first.")
    cfg = json.loads(cfg_path.read_text())
    ig = meta["instagram"]
    size = Path(video).stat().st_size
    if size > 300 * 1024 * 1024:
        sys.exit("Instagram Reels must be 300 MB or smaller.")
    confirm(f"Instagram Reel (PUBLIC as soon as it finishes)\n  file:    {video}\n  account: {cfg['ig_user_id']}\n  caption: {ig['caption'][:90]}...", assume_yes)
    token = cfg["access_token"]
    r = requests.post(f"{GRAPH}/{cfg['ig_user_id']}/media", data={
        "media_type": "REELS", "upload_type": "resumable", "caption": ig["caption"],
        "share_to_feed": "true", "thumb_offset": str(ig.get("thumb_offset_ms", 0)), "access_token": token,
    }, timeout=60)
    r.raise_for_status()
    container = r.json()
    cid = container["id"]
    upload_uri = container.get("uri", f"https://rupload.facebook.com/ig-api-upload/v25.0/{cid}")
    with open(video, "rb") as fh:
        u = requests.post(upload_uri, headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)}, data=fh, timeout=600)
    u.raise_for_status()
    print("  video uploaded to Meta; waiting for processing", flush=True)
    for _ in range(90):
        s = requests.get(f"{GRAPH}/{cid}", params={"fields": "status_code,status", "access_token": token}, timeout=30).json()
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") in ("ERROR", "EXPIRED"):
            sys.exit(f"Instagram processing failed: {s}")
        time.sleep(10)
    else:
        sys.exit("Instagram processing timed out; container id " + cid)
    p = requests.post(f"{GRAPH}/{cfg['ig_user_id']}/media_publish", data={"creation_id": cid, "access_token": token}, timeout=60)
    p.raise_for_status()
    mid = p.json()["id"]
    link = requests.get(f"{GRAPH}/{mid}", params={"fields": "permalink", "access_token": token}, timeout=30).json().get("permalink")
    print(f"  published: {link or mid}")
    return {"platform": "instagram", "id": mid, "url": link, "time": time.strftime("%Y-%m-%d %H:%M:%S")}


def main():
    ap = argparse.ArgumentParser(description="Publish a finished, approved video to YouTube and/or Instagram.")
    ap.add_argument("platform", choices=["youtube", "instagram"])
    ap.add_argument("video")
    ap.add_argument("--meta", required=True, help="publish JSON with 'youtube' and/or 'instagram' sections")
    ap.add_argument("--thumbnail")
    ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    ap.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    ap.add_argument("--publish-at", help="schedule public release, RFC3339 e.g. 2026-11-20T19:30:00+05:30 (uploads private until then)")
    ap.add_argument("--variant", help="content variant id (e.g. C0002-hi) to record the publication in data/studio.db")
    ap.add_argument("--slot", help="publishing slot label for timing experiments, e.g. evening-1930")
    a = ap.parse_args()
    meta = json.loads(Path(a.meta).read_text())
    if a.platform == "youtube":
        res = youtube_upload(a.video, meta, a.thumbnail, a.privacy, a.yes, a.publish_at)
    else:
        res = instagram_publish(a.video, meta, a.yes)
    log = Path(a.meta).with_name("published.json")
    entries = json.loads(log.read_text()) if log.exists() else []
    entries.append({"video": str(a.video), **res})
    log.write_text(json.dumps(entries, indent=2, ensure_ascii=False))
    print(f"  logged to {log}")
    if a.variant:
        from pipeline import db

        with db.connect() as con:
            con.execute(
                "INSERT OR REPLACE INTO publications (variant_id, platform, platform_id, url, privacy, scheduled_for, published_at, slot, metadata, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (a.variant, res["platform"], res["id"], res.get("url"), res.get("privacy"), res.get("scheduled_for"), None if res.get("scheduled_for") else db.now(), a.slot, json.dumps(meta, ensure_ascii=False), db.now()),
            )
        print(f"  recorded in data/studio.db for {a.variant}")


if __name__ == "__main__":
    main()
