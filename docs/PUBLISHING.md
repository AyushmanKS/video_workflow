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

> Written and researched by Chalk Tales. Illustrations and narration are made with AI tools; every script is checked against the Valmiki Ramayana, with verse references in the description.

Never imply hand-drawn art or a human narrator. The brand name comes from `profiles/brand.json` (owner decision 2026-11-17: one name, **Chalk Tales**, on Instagram and YouTube; the YouTube rename is pending in Studio). Episodes approved before this decision keep "Knowledge PowerBank" in their approved metadata.

### Brand cross-promotion (`python -m pipeline promo`)
Brand settings live in `profiles/brand.json` (name, colours, Instagram handle and URL, YouTube current/planned handle with one `active_url`, collab email, per-language CTA text; projects can override). Details and the live-account checklist: `docs/BRAND.md`.

| Command | What it does |
|---|---|
| `python -m pipeline promo <ID> [--lang L[,L]] [--platform youtube\|instagram]` | dry run (default): prints a readable diff of the proposed changes |
| `python -m pipeline promo <ID> --apply` | writes `publish.json`: YouTube description gets the Instagram follow line and the collab line once (above the hashtag line), `youtube.pinned_comment` gets the Instagram handle (pin it by hand), the Instagram caption gets one "watch the full series in order on YouTube, link in profile" line before the hashtags |
| `... --apply --force-reapproval-needed` | also changes sections that already have a G3 approval; it prints that the owner must re-approve G3 for them |
| `python -m pipeline promo --audit` | read-only report of every variant and platform → `data/reports/promo-audit-<date>.md` (status, promo present, exact proposed text) |

- Run it **before G3**. G3 binds a hash of each platform's section of `publish.json`, so a later change invalidates the approval; promo refuses G3-approved sections by default and always refuses sections already uploaded or published (edit those by hand in Studio or the Instagram app).
- Idempotent: lines are found by content (the Instagram URL/handle, the email, the known CTA strings), so re-runs replace rather than duplicate.
- Limits enforced: Instagram caption ≤2,200 characters and ≤5 hashtags; YouTube description ≤5,000 characters and no `<` `>`. Nothing is written when a limit would be exceeded.
- `publish.py` prints a non-blocking warning when the platform's promo line is missing.
- `python -m pipeline mediakit [--offline]` fills `docs/MEDIA_KIT.md` from the database (and read-only follower lookups) into `data/reports/media-kit-<date>.md`; anything without data says "not yet available".

### Approvals per platform (G3)
G3 is recorded separately for each platform: the record names the platform, each language's approved time, and the sha256 of that language's `publish.json` and mp4. An Instagram approval never covers YouTube, or the reverse. If the video, the metadata or the time changes after G3, the publish command refuses and the owner approves again. G2 likewise requires a QA pass, or warnings each carrying a recorded waiver. Claude never records G1, G2 or G3, and the upload steps live in the manual-only `/publish` skill.

### Gate commands (owner only; flags as in `--help`, 2026-11-16)

| Command | Flags | Notes |
|---|---|---|
| `python -m pipeline lint <ID>` | `[--lang L] [--calibrate]` | pre-G1 lint; G1 is refused while lint fails |
| `python -m pipeline approve <ID> script` | `--langs en,hi [--note …] [--by owner] [--channel chat\|telegram\|terminal] [--nonce …] [--yes]` | records the `script.json` hashes |
| `python -m pipeline approve <ID> final` | `--langs …` (same optional flags) | refused unless the latest QA verdict for the current mp4 is pass, or warn with every warning waived |
| `python -m pipeline approve <ID> publish` | `--langs … --platform youtube\|instagram --at <ISO>` or `--at en=<ISO>,hi=<ISO>` or `--at now` | YouTube falls back to `schedule.json` when `--at` is omitted; Instagram always needs `--at` |
| `python -m pipeline reject <ID> script\|final\|publish` | `--note "…" [--langs …] [--platform …] [--by …] [--channel …]` | blocks the gate for those languages |
| `python -m pipeline waive <ID>` | `--lang L --check <name>\|all-warnings --note "…" [--by …] [--channel …] [--yes]` | auto-reject checks can never be waived |

- `--langs` is required for every approval; there is no "all languages" default.
- Approvals are interactive: the owner types the variant ids. `--yes` works only when the owner has set `STUDIO_OWNER_APPROVED=<ID>` in their own shell, and then `--channel` is required. A PreToolUse hook (`pipeline/g3hook.py`) blocks approval and publish commands from Claude that don't match the records.

### Upload commands (after G3)

| Command | Flags | Notes |
|---|---|---|
| `python -m pipeline publish <ID>` | `--lang L [--platform youtube\|instagram] [--at <approved ISO>] [--slot …] [--yes]` | YouTube: private upload with `publishAt` = the approved time |
| | `--check-gates-only` | verifies G2/G3, time and hashes; no tunnel, no upload |
| | Instagram only: `--dry-run`, `--now`, `--cancel` | see the Instagram section |
| `python -m pipeline publish-queue add\|list\|remove\|run [ID]` | `[--langs …] [--platform youtube] [--priority N] [--cap N] [--dry-run] [--once]` | persisted YouTube queue: daily cap (default 6), backoff, exact approved times; re-checks the gates before each upload |
| `python -m pipeline ig-jobs` | | lists scheduled Instagram posts |

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

## Analytics, experiments and the weekly report (read-only)

```
python -m pipeline analytics                    # snapshots that are due (YouTube + Instagram)
python -m pipeline analytics --dry-run          # list what is due
python -m pipeline analytics --platform instagram --force
python -m pipeline analytics --relabel [--dry-run]
python -m pipeline analytics --install-daily | --print-daily | --uninstall-daily
python -m pipeline report <VARIANT>             # one variant, every snapshot
python -m pipeline report --weekly              # data/reports/weekly-<date>.md
python -m pipeline experiment add --exp1 | list | start <N> | close <N> --result "…"
python -m pipeline features --all               # backfill the features table
```

- **Windows:** every snapshot stores `age_h = captured_at − published_at` (YouTube scheduled videos use `scheduled_for`). A snapshot is labelled `24h`, `48h`, `7d`, `14d` or `30d` only when `age_h` is within ±12 h of that window. Otherwise it is labelled `age_<n>h`, or `prepublish_<n>h` before the video is public. `--label` overrides this; avoid it.
- **YouTube:** the day series is queried one day at a time (`startDate = endDate`). Window values are sums of the first N calendar days of that series. Rows younger than 3 days are re-queried because YouTube Analytics lags 1–3 days. The `24h` and `48h` windows are calendar-day approximations, since day 1 is partial.
- **Instagram:** `GET /{media-id}/insights` on `graph.facebook.com/v27.0` asks for views, reach, saved, shares, likes, comments, total_interactions, ig_reels_avg_watch_time and ig_reels_video_view_total_time.
  - `plays`, `clips_replays_count`, `ig_reels_aggregated_all_plays_count` and `video_views` are deprecated (all versions since 2025-04-21, or 2025-01-08 for `video_views`) and are not requested.
  - The current token returns **(#10) "Application does not have permission"** for insights. Re-authorise the Meta app with `instagram_manage_insights` (Facebook Login). Until then, snapshots store `permission_error` and only the basic counters (`like_count`, `comments_count`).
  - The token is sent in an Authorization header and never printed.
- **Daily job:** `com.shortsstudio.analytics.daily` runs `python -m pipeline analytics` at 20:00 local and logs to `data/logs/analytics-daily.log`. It only reads analytics and never uploads or publishes. If the Mac is asleep at 20:00, launchd runs it on wake.
- **Learning rules (D4):**
  - One active experiment at a time.
  - Arms alternate by odd/even episode across all languages.
  - At least 6 variants per arm per language before any claim; below that the result is "anecdote".
  - Compare within a language only, by ratio to that language's rolling median (never raw views across languages).
  - The stop rule is fixed in advance, and the interval is a 95% bootstrap.
  - `schedule` ranks slots on the per-language ratio, and freezes slots while a content experiment is active.
- **E7 manual triggers:** record them in `data/reports/e7_manual.json` as `{"policy_pressure": {"gu": {"consecutive_episodes": 5, "evidence": "path or note"}}}`.

---

## Files

| File | Purpose |
|---|---|
| `publish.py` | The uploader (YouTube and Instagram) |
| `secrets/` | Your OAuth client and tokens. Never share this folder. |
| `out/<episode>/final/publish-english.json`, `publish-hindi.json` | Title, description, tags, playlist, caption |
| `out/<episode>/final/published.json` | Log of uploads with links (legacy C0001 en/hi) |
| `content/<ID>/<lang>/publish.json`, `published.json` | Metadata and upload log for pipeline episodes |
| `data/studio.db` | publications, analytics_snapshots, features, experiments, decisions, waivers, publish_queue |
| `data/reports/weekly-<date>.md` | Weekly report |
| `profiles/brand.json` | Brand name, handles, links, email, per-language CTA lines |
| `data/reports/promo-audit-<date>.md`, `media-kit-<date>.md` | Promo audit and media kit (generated, local) |
