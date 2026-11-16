# Publishing finished videos (YouTube + Instagram)

`publish.py` uploads an approved, finished video with the title, description, tags, language, category, playlist and thumbnail taken from a `publish-<lang>.json` file. It always shows a summary and waits for you to type `yes` before uploading. Credentials stay in `secrets/` (private to your user account), and every upload is logged to `published.json` next to the metadata file.

Everything here is free: the YouTube Data API and Instagram Graph API cost nothing at this volume.

---

## Disclosure, audience setting and approvals (owner decisions 2026-11-16)

### AI disclosure: `synthetic: true` on YouTube, `is_ai_generated: true` on Instagram
Every new episode sets `youtube.synthetic: true` in `publish.json` (sent as `containsSyntheticMedia`) and `instagram.is_ai_generated: true`. Already-published episodes keep their metadata; nothing is re-uploaded.

Reasoning (`docs/GROWTH_AND_MONETIZATION_STRATEGY.md` §3.5):
- YouTube requires disclosure for realistic AI content, not for clearly animated content. The chalk visuals alone would not need it; the realistic TTS narrator is the borderline case, and YouTube's page does not address generic AI narration voices.
- For animated content and non-music AI audio the label sits in the expanded description, not on the player, so disclosing costs little.
- Creators who consistently fail to disclose risk labels added by YouTube, removal or suspension from YPP. Over-disclosure has no documented penalty.
- Instagram Reels already go out with `is_ai_generated=true`; the same answer on both platforms keeps the channel's statement consistent. India's IT Rules amendment (in force 20 Feb 2026) adds a platform labelling duty for synthetic media.

### Made for Kids = No
Set "No" on the channel and on every video. The audience research describes the viewers as mostly adults, and made-for-kids content loses personalized ads, comments and memberships; mislabelling is a COPPA risk (GROWTH §3.6).

### Honest workflow statement
Use this on the About page and as one line in every description (GROWTH §3.4), adapted per language:

> Written and researched by Knowledge PowerBank. Illustrations and narration are made with AI tools; every script is checked against the Valmiki Ramayana, with verse references in the description.

Never imply hand-drawn art or a human narrator. If the channel is renamed (GROWTH §7 Phase 0), update the name here.

### Approvals per platform (G3)
G3 is recorded separately for each platform: the record names the platform, each language's approved time, and the sha256 of that language's `publish.json` and mp4. An Instagram approval never covers YouTube, or the reverse. If the video, the metadata or the time changes after G3, the publish command refuses and the owner approves again. G2 likewise requires a QA pass, or warnings each carrying a recorded waiver. The implementation is in `pipeline/__main__.py` (roadmap A10/A11); `python -m pipeline approve --help` shows the exact flags. Claude never records G3, and the upload steps live in the manual-only `/publish` skill.

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

## Instagram: one-time setup

This uses the **Instagram API with Instagram Login** (API v27.0, host `graph.instagram.com`). It needs **no Facebook Page**, and it's free.

1. **Create the account** in the Instagram app (any email or phone).
   - Then go to **Settings → Account type and tools → Switch to professional account → Creator**. Business works too; personal accounts can't publish via the API.
2. **Create a Meta developer account** at https://developers.facebook.com/ using your Facebook login, then accept the developer terms. A new Facebook account is fine; it's only used to own the app.
3. **Create the app:** go to **My Apps → Create app**.
   - Use case: **"Manage messaging & content on Instagram"**.
   - You can skip linking a business portfolio.
4. **Add yourself as a tester:** in the app, open **Instagram → API setup with Instagram business login**.
   - Under **App roles → Roles → Instagram testers**, add your Instagram username.
   - Accept the invite in the Instagram app: **Settings → Website permissions → Apps and websites → Tester invites**.
   - The app can stay in Development mode. It can publish to accounts that have a role on it.
5. **Generate a token:** back in **API setup with Instagram business login → Generate access tokens**, click **Add account**.
   - Log in and grant `instagram_business_basic` and `instagram_business_content_publish`.
   - Then click **Generate token** and copy it. **Don't paste it into any chat.**
6. In Terminal, run:
   ```
   cd ~/Desktop/work/shorts-studio && .venv/bin/python instagram.py setup
   ```
   Paste the token at the hidden prompt. Press Enter at the app-secret prompt unless Meta said the token is short-lived.
   - This saves `secrets/instagram.json` (mode 600, git-ignored).
   - The token lasts about 60 days and is refreshed automatically when it's older than 20 days and still valid.
7. Run `.venv/bin/python instagram.py status`, which shows the account, token age and publishing quota.

### How a post works

Instagram Login apps can't upload a file directly; Meta downloads the video from a public HTTPS link. So `instagram.py`:

1. Serves only that video, and the thumbnail as the cover JPEG, from your Mac through a temporary **Cloudflare quick tunnel**. That needs `brew install cloudflared`, which is free and needs no account.
2. Uses a random, unguessable path with directory listing disabled.
3. Creates the Reel container, waits until Instagram has processed the video, **closes the tunnel**, and then publishes.

The tunnel takes about 1–2 minutes to come up.

**Reel limits:** 3 s to 15 min, 300 MB or less, H.264/HEVC, AAC at 48 kHz or lower, 25 Mbps or lower. Our renders (about 12 Mbps, 1080×1920, 30 fps) are well inside these.

### Commands (only after the owner's Instagram G3: video, caption and time)

```
python -m pipeline publish C0004 --lang en --platform instagram --dry-run --now
python -m pipeline publish C0004 --lang en --platform instagram --at 2026-11-19T21:30:00+05:30 --yes
python -m pipeline publish C0004 --lang en --platform instagram --now --yes
python -m pipeline ig-jobs
python -m pipeline publish C0004 --lang en --platform instagram --cancel
```

- **Dry run:** checks the token, the tunnel and the file limits, and posts nothing.
- **Scheduled post:** the Instagram API has no scheduling, so this installs a one-off **launchd** job (`~/Library/LaunchAgents/com.shortsstudio.ig.<variant>.plist`). The job posts at that local time, logs to `data/logs/ig-<variant>.log` and removes itself after success.
  - **The Mac must be on.** If it's asleep at that time, launchd runs the job when it wakes.
  - A job that is more than 24 h late refuses to post.
  - Test a schedule once with `--dry-run --at <2 minutes from now> --yes`. macOS may ask whether Python may access the Desktop folder: allow it, or the job can't read the video.
- `--now --yes` posts immediately; the post is public at once.
- `ig-jobs` lists scheduled Instagram posts; `--cancel` removes one.

The caption comes from `publish.json → instagram.caption`. The same video can't be posted twice; the uploader checks `published.json`. Limits: 100 API posts and 400 containers per rolling 24 h.

In the Instagram app afterwards, check the cover, and confirm the **AI info** label is shown (the API sets `is_ai_generated`; add it by hand if it is missing).

---

## Files

| File | Purpose |
|---|---|
| `publish.py` | The uploader (YouTube and Instagram) |
| `secrets/` | Your OAuth client and tokens. Never share this folder. |
| `out/<episode>/final/publish-english.json`, `publish-hindi.json` | Title, description, tags, playlist, caption |
| `out/<episode>/final/published.json` | Log of uploads with links |
