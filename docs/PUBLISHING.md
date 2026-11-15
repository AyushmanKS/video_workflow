# Publishing finished videos (YouTube + Instagram)

`publish.py` uploads an approved, finished video with the title, description, tags, language, category, playlist and thumbnail taken from a `publish-<lang>.json` file. It always shows a summary and waits for you to type `yes` before uploading. Credentials stay in `secrets/` (private to your user account), and every upload is logged to `published.json` next to the metadata file.

Everything here is free: the YouTube Data API and Instagram Graph API cost nothing at this volume.

---

## YouTube: one-time setup (about 10 minutes)

Use your **personal** Google account, the one that owns the YouTube channel. Don't reuse a work Google Cloud project.

1. Go to https://console.cloud.google.com/ and create a new project, e.g. "shorts-studio".
2. Open **APIs & Services → Library**, search for **YouTube Data API v3**, and click **Enable**.
3. Open **APIs & Services → OAuth consent screen**:
   - User type: **External**. App name: "shorts-studio". Use your own email for the support and developer fields.
   - Scopes: skip.
   - Test users: **add your own Google account email**.
   - Leave the app in **Testing**.
4. Open **APIs & Services → Credentials → Create credentials → OAuth client ID**:
   - Application type: **Desktop app**. Name: "shorts-studio".
   - Download the JSON file and save it as:
     `~/Desktop/work/shorts-studio/secrets/youtube_client_secret.json`
5. The first upload opens a browser window. Choose your channel and allow access. Google will warn that the app is unverified; click **Continue**, because it's your own app. A token is saved to `secrets/youtube_token.json`, so later uploads don't ask again. In Testing mode the token expires after about 7 days, after which the browser sign-in appears once more.

### The important limit

YouTube **locks videos uploaded through a new, unaudited API project as private**, and they can't be made public later. To publish publicly through the API, apply for the free YouTube API Services audit:
https://support.google.com/youtube/contact/yt_api_form

It usually takes a few weeks. Until it's approved, upload public videos in YouTube Studio; you can paste the metadata from the publish JSON.

### Upload command

```
cd ~/Desktop/work/shorts-studio && source .venv/bin/activate
F=out/ramayana-ep-01-maharishi-valmiki-the-birth-of-the-ramayana/final
python publish.py youtube $F/valmiki-ramayana-episode-01-english.mp4 \
  --meta $F/publish-english.json \
  --thumbnail $F/valmiki-ramayana-episode-01-english-thumbnail.png
```

After uploading, it adds the video to the "Valmiki Ramayana" playlist and tries to set the thumbnail. Custom thumbnails need a phone-verified channel, and YouTube may not show them on Shorts. Pin the comment from `pinned_comment` by hand; the API can't pin comments.

---

## Instagram: one-time setup (once your account exists)

1. Create the Instagram account. Then go to **Settings → Account type and tools → Switch to professional account → Creator** (or Business).
2. Create a free Facebook Page and link it: **Instagram → Edit profile → Page → Connect**.
3. Go to https://developers.facebook.com/ and click **My Apps → Create app**:
   - Use case: **Manage messaging & content on Instagram**, i.e. the Instagram API with Instagram Login.
   - In the app's Instagram settings, add your Instagram account as an **Instagram tester**, then accept the invite in Instagram (**Settings → Website permissions → Apps and websites → Tester invites**).
   - Generate an access token with the **instagram_business_basic** and **instagram_business_content_publish** permissions. Then exchange it for a **long-lived token**, which lasts 60 days and can be refreshed.
4. Save the result as `~/Desktop/work/shorts-studio/secrets/instagram.json`:
   ```json
   {"ig_user_id": "YOUR_INSTAGRAM_USER_ID", "access_token": "YOUR_LONG_LIVED_TOKEN"}
   ```
   Apps in Development mode can publish to accounts that have a role on the app, so your own account doesn't need app review.

### Publish command (posts publicly)

```
python publish.py instagram $F/valmiki-ramayana-episode-01-english.mp4 --meta $F/publish-english.json
```

The tool uploads the file directly from your Mac (Meta's resumable upload; up to 300 MB and 15 minutes), waits for processing, then publishes with the caption from the JSON. In the Instagram app afterwards, set the cover image and turn on **AI info**.

---

## Files

| File | Purpose |
|---|---|
| `publish.py` | The uploader (YouTube and Instagram) |
| `secrets/` | Your OAuth client and tokens. Never share this folder. |
| `out/<episode>/final/publish-english.json`, `publish-hindi.json` | Title, description, tags, playlist, caption |
| `out/<episode>/final/published.json` | Log of uploads with links |
