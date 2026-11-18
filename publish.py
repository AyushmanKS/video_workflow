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


def emit(kind, message="", **kw):
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from pipeline import events

        return events.emit(kind, None, message, **kw)
    except Exception:
        return None


def language_playlist(variant):
    if not variant or "-" not in str(variant):
        return None
    try:
        b = json.loads((ROOT / "profiles" / "brand.json").read_text())
        return b["brand"]["youtube"].get("language_playlists", {}).get(str(variant).rsplit("-", 1)[1])
    except (OSError, ValueError, KeyError):
        return None


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


def youtube_upload(video, meta, thumb, privacy, assume_yes, publish_at=None, variant=None):
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
    emit("started", f"YouTube upload started ({Path(video).stat().st_size / 1e6:.0f} MB)")
    resp = None
    bucket = -1
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"  uploaded {status.progress() * 100:.0f}%", flush=True)
            b = int(status.progress() * 10)
            if b > bucket:
                bucket = b
                emit("progress", f"uploading {status.progress() * 100:.0f}%", progress=status.progress(), detail={"measured": "resumable upload chunks"})
    vid = resp["id"]
    long_form = (meta.get("youtube") or {}).get("format") == "long" or yt.get("format") == "long"
    result = {"platform": "youtube", "id": vid, "url": f"https://www.youtube.com/watch?v={vid}" if long_form else f"https://www.youtube.com/shorts/{vid}", "privacy": resp["status"]["privacyStatus"], "scheduled_for": resp["status"].get("publishAt"), "time": time.strftime("%Y-%m-%d %H:%M:%S")}
    print(f"  uploaded: {result['url']} (privacy reported: {result['privacy']})")
    check = svc.videos().list(part="status", id=vid).execute()["items"][0]["status"]
    result["verified"] = {"privacy": check.get("privacyStatus"), "publishAt": check.get("publishAt")}
    if publish_at and not check.get("publishAt"):
        print("  WARNING: YouTube did not keep the scheduled time; set it in Studio")
    if privacy == "public" and check.get("privacyStatus") != "public":
        print(f"  WARNING: requested public but YouTube reports {check.get('privacyStatus')} (possible unaudited-project lock)")
    if yt.get("playlist"):
        pid = find_playlist(svc, yt["playlist"])
        if pid:
            svc.playlistItems().insert(part="snippet", body={"snippet": {"playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
            result["playlist"] = pid
            print(f"  added to playlist '{yt['playlist']}'")
        else:
            print(f"  playlist '{yt['playlist']}' not found; skipped")
    lang_pl = None if long_form else language_playlist(variant)
    if lang_pl:
        try:
            svc.playlistItems().insert(part="snippet", body={"snippet": {"playlistId": lang_pl["id"], "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
            result["language_playlist"] = lang_pl["id"]
            print(f"  added to language playlist '{lang_pl['title']}'")
        except Exception as ex:
            print(f"  language playlist skipped: {type(ex).__name__}")
    if thumb and Path(thumb).exists():
        try:
            svc.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb), mimetype="image/png")).execute()
            result["thumbnail"] = "set"
            print("  thumbnail set")
        except Exception as e:
            result["thumbnail"] = f"not set: {e}"
            print(f"  thumbnail not set ({str(e)[:160]})")
    return result


def instagram_publish(video, meta, assume_yes, thumbnail=None, dry_run=False, log=None):
    import instagram

    prior = instagram.already_published(video, log) if log else None
    if prior and not dry_run:
        print(f"  already on Instagram: {prior.get('url') or prior['id']} — not posting again")
        emit("info", f"already on Instagram ({prior.get('url') or prior['id']}); not posting again")
        return None
    emit("started", "Instagram dry run started" if dry_run else "Instagram publish started")
    ig = meta["instagram"]
    return instagram.publish(video, ig["caption"], thumbnail, ig.get("thumb_offset_ms", 0), dry_run, lambda s: confirm(s, assume_yes), ig)


def gate_check(a):
    sys.path.insert(0, str(ROOT))
    from pipeline import gates

    if not a.variant or "-" not in a.variant:
        sys.exit("Refused: --variant <ID>-<lang> is required so the G2/G3 approval can be verified (use python -m pipeline publish).")
    cid, lang = a.variant.rsplit("-", 1)
    m = gates.load(cid)
    f = gates.variant_files(m, lang)
    problems = []
    if gates.sha256(a.video) != gates.sha256(f["video"]):
        problems.append(f"{a.video} is not the approved variant file {gates.rel(f['video'])}")
    if gates.sha256(a.meta) != gates.sha256(f["meta"]):
        problems.append(f"{a.meta} is not the approved metadata file {gates.rel(f['meta'])}")
    problems += gates.check_publish(m, lang, a.platform, a.publish_at, immediate=a.platform == "instagram")
    if problems:
        sys.exit("Refused (approval record does not match):\n  " + "\n  ".join(problems))


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
    ap.add_argument("--dry-run", action="store_true", help="instagram: check token, tunnel and file limits without posting")
    a = ap.parse_args()
    emit_ctx(a)
    try:
        run(a)
    except BaseException as e:
        report_failure(e)
        raise


def emit_ctx(a):
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from pipeline import events

        events.set_context(variant_id=a.variant, platform=a.platform, stage="ig_dry_run" if a.dry_run else "publish")
    except Exception:
        pass


def report_failure(e):
    if isinstance(e, SystemExit):
        if e.code in (None, 0) or e.code == 75:
            return
        raw = str(e.code)
    elif isinstance(e, KeyboardInterrupt):
        emit("failed", "publish stopped by hand", status="Cancelled", error="KeyboardInterrupt")
        return
    else:
        raw = f"{type(e).__name__}: {e}"
    emit("failed", raw.splitlines()[0][:300] if raw else "publish failed", error=raw)


def promo_warning(meta, a):
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from pipeline import promo

        lang = a.variant.rsplit("-", 1)[1] if a.variant and "-" in a.variant else None
        for w in promo.missing(meta, a.platform, lang):
            print(f"  WARNING (not blocking): {w}")
    except Exception:
        pass


def run(a):
    if not a.dry_run:
        gate_check(a)
    meta = json.loads(Path(a.meta).read_text())
    promo_warning(meta, a)
    if a.platform == "youtube":
        res = youtube_upload(a.video, meta, a.thumbnail, a.privacy, a.yes, a.publish_at, a.variant)
    else:
        res = instagram_publish(a.video, meta, a.yes, a.thumbnail, a.dry_run, Path(a.meta).with_name("published.json"))
        if not res:
            return
    log = Path(a.meta).with_name("published.json")
    entries = json.loads(log.read_text()) if log.exists() else []
    entries.append({"video": str(a.video), **res})
    log.write_text(json.dumps(entries, indent=2, ensure_ascii=False))
    print(f"  logged to {log}")
    if res["platform"] == "youtube":
        emit("completed", f"uploaded to YouTube {res['id']}" + (f", scheduled for {res.get('scheduled_for')}" if res.get("scheduled_for") else f" ({res.get('privacy')})"),
             detail={"platform_id": res["id"], "url": res.get("url"), "verified": res.get("verified")})
    else:
        emit("completed", f"published on Instagram {res.get('url') or res['id']}", detail={"platform_id": res["id"], "url": res.get("url")})
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
