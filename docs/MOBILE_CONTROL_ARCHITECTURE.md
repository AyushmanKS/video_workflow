# Mobile control architecture (Android phone → MacBook pipeline)

**Status:** design only, nothing implemented. **Research date:** 2026-11-16. Vendor plans and limits change, so re-check the linked pages before you build.

**Goal:** the owner runs, reviews and approves the shorts-studio pipeline from an Android phone on any network. The Mac stays the only production machine. Nothing is published without an explicit, recorded owner approval, nothing is exposed publicly without authentication, and nothing costs money.

Notation: **[V]** = verified fact with a source link. **[M]** = measured on this Mac today. **[R]** = recommendation or judgement.

---

## 1. Summary of the recommendation

| Layer | Choice | Why |
|---|---|---|
| Notifications, approvals, media review | **Private Telegram bot run by a small Python daemon on the Mac** (long polling, no inbound port) | Free, licence-neutral for a commercial channel, works on any network, has inline buttons, plays video/audio/images in chat |
| Steering Claude Code agents ("re-do scene 4 with a seed", "write the gu script") | **Claude Code Remote Control** in the Claude Android app | Already covered by the owner's Claude subscription. Outbound-only, push notifications built in, sessions stay on the Mac |
| Rich dashboard (optional, phase 3) | **FastAPI on `127.0.0.1` reached through Tailscale Serve**, *only if the owner accepts the Tailscale licence condition* (§4.1); otherwise skip it | Tailnet-only, automatic HTTPS, identity headers. The Personal plan is "only suitable for non-commercial use" |
| Recorded approvals | Existing `manifest.json` gate + `decisions` table, **extended** with actor, channel, artifact hashes and a nonce | Phone approvals use exactly the same gate the CLI uses; no parallel approval system |
| Keep-alive | `launchd` agent with `KeepAlive` for the bot; `caffeinate` during runs; `pmset schedule wake` before scheduled Instagram posts | No new software |

**[R] Build Telegram first (MVP in one day). Treat Remote Control as free and immediate (setup, not build). Build the dashboard only if Telegram review proves too cramped.**

---

## 2. Current pipeline facts this design relies on

From `pipeline/__main__.py`, `pipeline/db.py`, `pipeline/igschedule.py`, `pipeline/progress.py` and `docs/PUBLISHING.md`:

- **CLI commands:** `new`, `status [ID]`, `trending`, `research`, `approve <ID> script|final|publish [--note] [--langs]`, `done`, `produce <ID> --lang X [--steps voice,images,render]`, `qa <ID> --lang X`, `schedule --id <ID> --lang X`, `publish <ID> --lang X [--at] [--yes] [--platform youtube|instagram] [--now] [--dry-run] [--cancel]`, `ig-jobs`, `takes`, `progress <ID> [--watch N] [--oneline]`, `retention-csv`, `voicepack`, `link`, `analytics [--force]`, `report <VARIANT>`.
- **Gate recording (`cmd_approve`):**
  - It writes `manifest["stages"]["gate:script|gate:final|gate:publish"] = {status:"approved", at, note, langs}`.
  - It inserts a row into `decisions` with `decided_by="human"`.
  - **If `--langs` is omitted, the approval covers all languages.**
- **Gate enforcement (`require`):**
  - `produce` and `takes` need `gate:script`.
  - `publish` needs both `gate:final` and `gate:publish` for that language.
- **Gaps relevant to remote approval:**
  1. Approvals record no actor or channel beyond `"human"`.
  2. They are not bound to the content approved: no hash of the video, `publish.json` or publish time. A re-render after G2 keeps the old approval.
  3. There is no `reject` command and no stored change request.
  4. There is no per-scene review state.
  5. Nothing can tell which agent is running. Only `runs` rows (stage, running/ok/failed) and file-derived progress (`progress.snapshot`) exist.
- **Progress:** `progress.snapshot(cid)` returns per-step done/total, ETA and finish time. `oneline()` is already phone-sized.
- **Instagram scheduling:**
  - It is a self-removing launchd job at `~/Library/LaunchAgents/com.shortsstudio.ig.<variant>.plist`.
  - The job runs `caffeinate -i -m python -m pipeline publish … --platform instagram --now --yes --at <iso>` and logs to `data/logs/ig-<variant>.log`.
  - It refuses to post if it is more than 24 h late.
- **Media sizes [M]:**
  - `content/C0005/hi/C0005-hi.mp4` is 150 MB for 97.8 s.
  - The QA contact sheet `C0005-hi.qa.png` is 2.2 MB, and `thumbnail.png` is 2.5 MB.
  - Per-scene audio is `audio/NN.wav`; per-scene images are `img/NN_raw.png`.

---

## 3. Options evaluated

### 3.1 Transport / remote access

| Option | Verified facts | Fit for this project |
|---|---|---|
| **Telegram Bot API, long polling** | **[V]** `getUpdates` and webhooks are "mutually exclusive"; updates are kept "not longer than 24 hours". **[V]** `callback_data` is 1–64 bytes. **[V]** Bots upload up to 50 MB per file (10 MB photos) and download up to 20 MB via `getFile`. A self-hosted local Bot API server raises upload to 2000 MB. **[V]** `protect_content` blocks forwarding/saving. **[V]** Bot chats are cloud chats stored on Telegram servers; end-to-end encryption is documented only for secret chats, which bots cannot use. Sources: [Bot API](https://core.telegram.org/bots/api), [Privacy Policy](https://telegram.org/privacy) | **Best primary channel.** The Mac only makes outbound HTTPS calls, so it works behind any NAT/CGNAT and on any phone network. It's free with no plan tiers. The privacy trade-off is acceptable for content that becomes public anyway; never send secrets (§6) |
| **Claude Code Remote Control** | **[V]** Connects the Claude app for Android or claude.ai/code to a Claude Code session running locally. "Your local Claude Code session makes outbound HTTPS requests only and never opens inbound ports." **[V]** Needs a Pro/Max/Ultra/Team/Enterprise login (API keys unsupported). **[V]** "If your laptop sleeps or your network drops, Claude Code reconnects automatically." The `claude` process must keep running. **[V]** Mobile push when a task finishes or a decision is needed (`/config` → Push when Claude decides / Push when actions required). **[V]** Trusted Devices step-up applies on Pro/Max/Ultra. Source: [Remote Control docs](https://code.claude.com/docs/en/remote-control) | **Use it for agent steering.** It's zero extra cost (existing subscription). It isn't a structured review UI: no per-scene buttons, no media player, and approvals are free-text that Claude interprets. That interpretation is acceptable for G1 change requests but **not as the record of G3** (§6.4) |
| **Claude Code Channels (Telegram plugin)** | **[V]** "Research preview". An MCP plugin pushes Telegram/Discord/iMessage messages into a running session. Sender allowlist via pairing. Optional "permission relay": "Anyone who can reply through the channel can approve or deny tool use in your session." Requires Bun. Source: [Channels docs](https://code.claude.com/docs/en/channels) | **[R] Don't make it the backbone.** It is preview (flags and protocol may change), it routes every message through the model, and Telegram allows only one `getUpdates` consumer per bot. If you try it, use a *second* bot token so it never competes with the studio bot |
| **Tailscale (Serve)** | **[V]** Personal plan: $0, "up to 6 users", "unlimited user devices", but "**only suitable for non-commercial use of Tailscale**" ([pricing](https://tailscale.com/pricing), [pricing FAQ](https://tailscale.com/kb/1251/pricing-faq)). **[V]** Serve is tailnet-only and needs HTTPS certs enabled (`*.ts.net`). It adds `Tailscale-User-Login` / `-Name` headers and strips spoofed copies; it recommends the backend listen only on localhost ([Serve](https://tailscale.com/kb/1312/serve)) | Technically the best dashboard path. **Licence conflict:** CLAUDE.md requires commercial-use licences, and a YouTube channel is arguably commercial. **Owner decision required** (§4.1) |
| **Tailscale Funnel** | **[V]** Public internet, ports 443/8443/10000 only, beta, unconfigurable bandwidth limits, available on all plans. No identity headers ([Funnel](https://tailscale.com/kb/1223/funnel)) | **Avoid.** It is public exposure; auth would rest entirely on the app |
| **Cloudflare Tunnel + Access** | **[V]** Free Zero Trust plan for teams under 50 users (Cloudflare pricing/blog; the plan page didn't render here). Third-party reports say a card may be required at signup. Public hostnames need a domain whose DNS is on Cloudflare. **[V]** Quick tunnels (`trycloudflare.com`) are "for testing and development", have a random hostname per run, a 200 in-flight request cap and **no SSE**. Auth is open by default, with optional `--allowed-mail` OTP ([quick tunnels](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/)) | Licence-clean, but **not zero cost**: it needs a registered domain (paid yearly). Quick tunnels are fine for the existing Instagram fetch, wrong for a control panel |
| **ZeroTier** | **[V]** Free plan: 10 devices, 1 network, "Personal, non-commercial use" ([pricing](https://www.zerotier.com/pricing/)) | Same licence problem as Tailscale, fewer features. **Avoid** |
| **Plain WireGuard** | Open source (GPL-2.0 kernel / MIT-style tools), no service account. Needs one reachable UDP endpoint: a port-forward on the home router plus a public IPv4/IPv6 address, or a VPS | Licence-clean and free, **but** many Indian home ISPs use CGNAT, and the Mac moves between networks. **[R] Fallback only**, if the dashboard is needed, the home connection has a public IP, and Tailscale is ruled out |
| **ntfy** | **[V]** On ntfy.sh "all topics … are public"; the topic name "is essentially a password". 4,096-byte messages, 15 MB attachments that expire in 3 h, up to three action buttons per notification. Self-hosted servers default to `auth-default-access: read-write` ([publish](https://docs.ntfy.sh/publish/), [config](https://docs.ntfy.sh/config/)) | Fine for one-way pings. Action buttons would need an HTTP endpoint the phone can reach (the dashboard problem again). **Telegram supersedes it** |
| **Discord webhook** | Outbound POST into a channel. Buttons need a bot application and gateway connection | One-way. **No advantage over Telegram** |
| **GitHub Issues approvals** | The repo `AyushmanKS/video_workflow` is **public** | Would leak unpublished scripts/titles and needs polling. **Avoid** (a private repo would work but is clumsy and can't carry media) |

### 3.2 Why not "just a PWA"
A PWA still needs an HTTPS origin reachable from the phone on any network, so it inherits the transport problem above. On the strictly free, commercial-safe path, Telegram *is* the UI. **[R]** Telegram Mini Apps also need a public HTTPS URL, so they don't help either.

---

## 4. Recommended architecture

```
                         ANDROID PHONE (any network)
        ┌───────────────────────────┬──────────────────────────────┐
        │ Telegram app              │ Claude app → Code tab        │
        │  • push notifications     │  • Remote Control session    │
        │  • buttons: approve/reject│  • push: task done / needs   │
        │  • video/audio/image view │    decision                  │
        └─────────────┬─────────────┴───────────────┬──────────────┘
                      │ HTTPS (Telegram cloud)      │ HTTPS (Anthropic API)
                      ▼                             ▼
          api.telegram.org                   api.anthropic.com
                      ▲ long poll (outbound)        ▲ outbound poll/stream
══════════════════════╪═════════════════════════════╪═══ home NAT / CGNAT
  MACBOOK AIR         │  no inbound ports           │
  ┌───────────────────┴─────────────┐   ┌───────────┴───────────────┐
  │ studio-bot (launchd KeepAlive)  │   │ claude remote-control      │
  │  ├ poller: getUpdates           │   │  (tmux / terminal, Claude  │
  │  ├ authz: owner chat_id + nonce │   │   subagents run here)      │
  │  ├ watcher: runs table +        │   └───────────┬───────────────┘
  │  │  manifests + progress → push │               │ runs the same CLI
  │  ├ proxy maker: ffmpeg → 540p   │               ▼
  │  └ actions → python -m pipeline │──▶  python -m pipeline …  (single
  └───────────────┬─────────────────┘     source of truth for gates)
                  │ reads/writes             │
                  ▼                          ▼
     content/<ID>/manifest.json   data/studio.db (decisions, runs,
     content/<ID>/<lang>/review.json   approvals, remote_actions, audit)
     data/proxies/… (gitignored)  secrets/telegram.json (chmod 600)

  Optional phase 3: FastAPI on 127.0.0.1:8765 ──tailscale serve──▶ tailnet only
```

### 4.1 Licence decision the owner must make (dashboard only)
- **Tailscale Personal** states it is "only suitable for non-commercial use".
- If the channel is or will be monetised, using it for this pipeline conflicts with the CLAUDE.md rule "Commercial-use licenses only".
- There are three ways forward:
  - **(a)** Skip the dashboard (recommended default; Telegram covers the requirements).
  - **(b)** Use WireGuard if the home line has a public IP.
  - **(c)** Accept a paid plan, which breaks zero cost.
- **Do not decide this silently.**

### 4.2 Components

| # | Component | Location (proposed) | Notes |
|---|---|---|---|
| C1 | `studio-bot` daemon | `pipeline/bot.py`, started as `python -m pipeline bot` | Standard library + `requests` (already used). No bot framework dependency |
| C2 | launchd agent | `~/Library/LaunchAgents/com.shortsstudio.bot.plist` | `KeepAlive` true, `ThrottleInterval` 30, logs to `data/logs/bot.log`. **[V]** launchd restarts kept-alive jobs and throttles respawns to ≥10 s by default (`man launchd.plist`) |
| C3 | Event watcher | inside C1 | Polls every 15 s: new or finished `runs` rows, manifest stage changes, `ig-jobs` list, `data/logs/ig-*.log` tail, `published.json` files. Diffs against `data/bot_state.json`. **Zero changes to the engines** |
| C4 | Proxy maker | inside C1, on demand | `ffmpeg -vf scale=540:-2 -c:v h264_videotoolbox -b:v 900k -maxrate 1200k -c:a aac -b:a 64k -ac 1 -movflags +faststart`. **[M]** 150 MB → 11.1 MB in 4.4 s. Per-scene audio → Opus 32 kb/s for `sendVoice` (**[M]** about 25 KB per scene). Images → JPEG 1080 px long edge, under 10 MB. Cached under `data/proxies/<ID>/<lang>/` |
| C5 | Approval service | extend `pipeline/__main__.py` | `approve` gains `--by`, `--channel`, `--nonce`; a new `reject <ID> <gate> --note` command; a new `review` command for per-scene state. The bot calls these functions, never writes manifests itself |
| C6 | Audit tables | `data/studio.db` | `remote_actions(id, nonce, actor, chat_id, action, args_json, artifact_hashes_json, status, created_at, decided_at, result)`. `decisions` gains `channel`, `actor`, `artifact_sha256` |
| C7 | Remote Control | `claude remote-control --name shorts-studio --spawn same-dir` in tmux | Push toggles in `/config` |
| C8 | (Phase 3) dashboard | `pipeline/web.py`, FastAPI on `127.0.0.1` only | Reuses C5/C6; Tailscale Serve or WireGuard per §4.1 |

---

## 5. Data flow per capability

| Capability | Flow |
|---|---|
| **Status / which stage or agent is running** | `/status` → C1 runs `next_action()` + `progress.oneline()` for each active ID → one message per content item with **[Refresh]**. "Which agent": Claude subagents don't write to `runs` today. **[R]** Add a `SubagentStart`/`SubagentStop` hook in `.claude/settings.json` that runs `python -m pipeline agent-event <name> start|stop`, writing a `runs` row with stage `agent:<name>`. Remote Control also shows subagent progress natively |
| **Notifications when tasks finish** | C3 sees a `runs` row become `ok` or `failed`, a gate become pending (`next_action` starts with "human approval"), a QA verdict, an Instagram job firing or failing, or a publication appearing → `sendMessage`. During voice/images/render it posts `progress --oneline` every 4 min, matching the CLAUDE.md 3–5 min rule, and edits **one** message in place (`editMessageText`) to avoid spam |
| **Review / approve / reject scripts (G1)** | When `script:<lang>` is done and `gate:script` is pending → the bot sends `script.md` (text split at 4,096 chars, or as a document) + top hook from `hooks.json` → buttons **[Approve en] [Request changes] [Reject]**. "Request changes" replies with Telegram `ForceReply`. The owner's text is stored in `content/<ID>/<lang>/change_requests.json` + `decisions(stage='gate:script', decision='changes_requested')` and pushed to the Remote Control session (or picked up at next session start) for the scriptwriter agent. Approve → `approve <ID> script --langs en --by telegram:<user_id> --channel telegram --nonce <n>` |
| **Listen / compare voice takes** | `/voice C0006 hi 7` → `sendVoice` of `audio/06.wav` as Opus, with caption = scene text + `voice_qa.json` score/heard text. For best-of-N comparisons, `takes.best_of` currently keeps only the best take. **[R]** Have it also save `audio/takes/NN_kK.wav`, then send them as a media group with **[Keep take 1] [Keep take 2] [Regenerate]** |
| **Review images** | After images finish, send an album (max 10 per `sendMediaGroup`) of `img/NN_raw.png` JPEG proxies, then one message per scene with **[OK] [Redo] [Redo + note]**. "Redo" records state only; regeneration is queued, never run while another heavy model is loaded (§7) |
| **Video previews** | When render finishes → `sendVideo` of the 540p proxy (`supports_streaming`, `protect_content`) + the QA contact sheet as photo |
| **Per-scene approval** | New `content/<ID>/<lang>/review.json`: `{scene_no: {image: ok|redo, voice: ok|redo, note, by, at, image_sha256, audio_sha256}}`. **[R]** G2 buttons appear only when every scene is `ok` (or explicitly waived) |
| **G2 final approval** | After QA passes → message with proxy video, QA verdict summary, sha256 of the full-resolution mp4 → **[Approve final hi] [Reject]**. Approve records `gate:final` with `artifact_sha256` |
| **G3 publish approval (two-step)** | Message shows title, description excerpt, tags, thumbnail, platform, exact `publish_at` in IST, and video sha256 → **[Approve publish…]** → second message: "Type `PUBLISH C0006-hi 4821` within 5 min". The 4-digit code is random per request. Only an exact match records `gate:publish` for **that language and platform** with hashes of mp4 + `publish.json` + `schedule.json`. Publishing itself then runs as a separate **[Run publish now]** button, or stays a terminal step (§6.4) |
| **QA reports** | `/qa C0006 hi` → `qa.md` as text (it's short) + contact sheet |
| **Publishing monitoring** | C3 reads `ig-jobs`, tails `data/logs/ig-<variant>.log`, watches `published.json` and `publications` rows; for YouTube it can read back `publishAt` (as already done manually for C0004). It alerts on failure, on a job overdue by 10 minutes, or on success with the URL. **[R]** About 10 min before each scheduled IG job, check the Mac is awake (§7) |
| **Analytics** | `/analytics C0003-hi` → runs `pipeline report` and sends a summary. A daily launchd run of `pipeline analytics` (already a pending item in PROJECT_CONTEXT §20) posts "snapshot taken" notifications. **No numbers are generated by the bot; it only relays `report` output** (no-fabrication rule) |
| **Safe remote actions** | Allowlisted verbs only: `status`, `progress`, `qa`, `report`, `produce <ID> --lang X --steps …` (gated by G1 already), `ig-jobs`, `publish --cancel`, `analytics`. **No shell, no arbitrary arguments, no `git push`, no secret reads** |

---

## 6. Security model

### 6.1 Identity and authorisation
- **Owner allowlist:** `secrets/telegram.json` holds `bot_token`, `owner_user_id` and `owner_chat_id`.
  - Every update whose `from.id` or `chat.id` doesn't match is dropped and logged. The bot makes no reply, so it doesn't confirm it exists.
  - Bootstrap once on the Mac terminal: `python -m pipeline bot pair` prints a one-time code, the owner sends it to the bot, and the IDs are saved.
- **Private-only:** ignore group/channel updates. In BotFather, set **Allow Groups = off** and leave privacy mode on.
- **Signed, single-use callbacks:**
  - `callback_data` is only 64 bytes [V], so store state server-side.
  - Button data is `a:<12-char random nonce>`.
  - `remote_actions` maps each nonce to the action, args, the artifact hashes at send time, an expiry (24 h; 5 min for G3 confirmation) and its status.
  - A nonce works once; a replay gets "already used".
  - If the artifact hash changed since the button was sent (re-render, edited `publish.json`), the bot refuses and re-sends a fresh review.
  - Telegram's transport already authenticates updates (they arrive only over TLS via the bot token). The nonce adds replay protection, binding to the artifact, and an audit link.
- **Rate limits:** at most 30 actions per 10 min and at most 3 failed G3 codes per hour (then G3 locks until the terminal unlocks it). Heavy actions are queued one at a time.
- **Dashboard (phase 3 only):**
  - Bind to `127.0.0.1`.
  - Trust `Tailscale-User-Login` only from the Serve proxy, and allowlist the owner's login.
  - Use a CSRF token on every POST plus `SameSite=Strict` cookies, and reject requests with a foreign `Origin`.
  - It uses the same nonce, hash and two-step rules as Telegram.

### 6.2 Audit trail
- Every remote action produces one `remote_actions` row: requested → confirmed/expired → result.
- Every gate change goes through `cmd_approve`/`cmd_reject`. The manifest stage then carries `by`, `channel`, `nonce` and `sha256`, and `decisions` gets the same.
- `python -m pipeline audit [ID]` (new) lists them. Manifests are versioned in git, so approvals are also reviewable in history.

### 6.3 Secrets
- The bot token lives in `secrets/telegram.json`, mode 600; `secrets/` is already gitignored.
- The bot never sends file contents from `secrets/`, `.env`, OAuth tokens or `instagram.json`.
- The allowlisted verb set has no file-read verb, and paths are built server-side from `(ID, lang, scene)` validated against `^C\d{4}$`, `^[a-z]{2}$` and an integer range.
- Logs redact anything matching a token pattern.
- If the token leaks, revoke it with `/revoke` in BotFather.

### 6.4 Gate policy for remote use **[R]**
1. **G1:** approve or request changes via Telegram or Remote Control (Claude records the approval with `--channel remote-control`).
2. **G2:** Telegram button bound to the mp4 sha256 (or terminal). Not via Claude's interpretation of chat text.
3. **G3:** Telegram two-step code bound to the mp4 + `publish.json` + `schedule.json` hashes, per language and per platform. **Claude must never record G3 itself.**
   - Enforce this with a `PreToolUse` hook that blocks Bash commands matching `pipeline approve .* publish`.
   - Also make `cmd_approve publish` require either a TTY confirmation or a valid bot nonce.
4. **Re-validate at publish time:** `publish` recomputes the hashes and refuses if they differ from those recorded at G2/G3. This closes today's gap where a re-render after approval keeps the approval.
5. **Always pass explicit `--langs`** from remote paths. Today the default covers all languages.
6. **YouTube uploads stay private + `publishAt`.** Instagram scheduling still installs a launchd job only after G3 for Instagram specifically (existing rule in PROJECT_CONTEXT §13).

### 6.5 Privacy
- Unpublished proxies and scripts sit on Telegram's servers as cloud-chat data [V]. That's acceptable because they become public at release, but:
  - use `protect_content`;
  - never send owner personal data, analytics exports with viewer data, or credentials;
  - delete review messages after publishing (`deleteMessage`, optional).
- The Telegram account itself is the owner's; no other service receives project data.

---

## 7. Mac availability, sleep and memory

- **Sleep:**
  - **[V]** `caffeinate -s` prevents system sleep only on AC power; `-i` prevents idle sleep (`man caffeinate`).
  - **[V]** launchd `StartCalendarInterval` jobs missed during sleep run at next wake; `StartInterval` firings are missed (`man launchd.plist`). The IG job therefore fires late rather than never, and the 24 h guard applies.
  - **[V]** Remote Control reconnects after sleep.
  - **[R]** Closing a MacBook lid sleeps it unless it's in clamshell mode with external power and display. Don't rely on `caffeinate` to override lid-close (observed behaviour, not documented).
  - **[R]** When an IG job is installed, also run `sudo pmset schedule wake "<MM/DD/YY HH:MM:SS>"` about 5 min before it (`man pmset`, `schedule wake`). That needs sudo once per job, so offer it as a printed command rather than automating sudo.
- **Notifications about the Mac itself:** when the bot (re)starts it says "studio-bot online (woke at …)". If the owner expects updates and none arrive, the Mac is asleep or offline. **[R]** Optionally, a free external heartbeat (e.g. a GitHub Actions cron that checks a gist timestamp) can alert "Mac silent for 2 h". It adds complexity, so it's deferred.
- **Memory (16 GB rule):**
  - The bot is lightweight (Python + requests, under 60 MB).
  - It must **queue** heavy actions (produce/takes/qa with Whisper) through a single lock file `data/heavy.lock`. It refuses "redo scene" if a heavy job is running and says when it will start.
  - The proxy maker uses VideoToolbox and is cheap (4.4 s [M]), but it also takes the lock briefly.

---

## 8. Failure modes

| Failure | Effect | Mitigation |
|---|---|---|
| Mac asleep, lid closed or offline | No pushes, actions don't run | Telegram keeps unconsumed updates up to 24 h [V], so actions apply on wake **only if still unexpired**. Stale nonces are rejected. Bot posts "back online" |
| Bot crashes | Silence | launchd `KeepAlive`, crash count in the log, startup message |
| Telegram API outage or rate limit | Delayed messages | Exponential backoff; the outbox in `bot_state.json` resends; CLI still works |
| Proxy over 50 MB (long video) | `sendVideo` fails | Lower bitrate automatically (target 40 MB); otherwise send a link via the dashboard (phase 3) |
| Artifact changed after the review was sent | Wrong thing approved | Hash binding refuses; the bot re-sends a fresh review |
| Approve tapped twice or replayed | Duplicate | Single-use nonce |
| Bot token leaked | Others could message the bot | Owner allowlist ignores them. Revoke in BotFather; rotate `secrets/telegram.json` |
| Phone lost | Attacker with an unlocked Telegram could approve | Telegram passcode + Android lock. G3 needs the typed code from the *same* chat, so it's still weak. **[R]** Enable Telegram two-step verification; remote "panic" = `python -m pipeline bot lock` from Remote Control or terminal, which disables gate actions |
| Two consumers on one bot token (e.g. Channels plugin) | Updates split unpredictably | One process per token; Channels uses a separate bot |
| Heavy jobs collide (voice + images) | Swap, crash on 16 GB | `heavy.lock` queue |
| launchd IG job fires on a sleeping Mac much later | Late post | Existing 24 h guard + alert on "overdue 10 min" + `pmset schedule wake` |
| Remote Control session exits (network 403 for over 10 min in server mode [V]) | Can't steer agents | Run in tmux with a restart wrapper; the bot reports "Remote Control offline" if `pgrep -f "claude remote-control"` fails |

---

## 9. Phased build plan

### Phase 0: setup only (about 30 min, no code)
1. Create the bot in BotFather; disable groups.
2. Start `claude remote-control --name shorts-studio` in tmux in the repo. In `/config`, enable both push toggles. Pair the Claude Android app.
3. Confirm the Telegram account has two-step verification and an app passcode.

### Phase 1: MVP in a day (about 6–8 h)
Delivers notifications, status, and G1/G2/G3 approvals.

| Task | Est. |
|---|---|
| `pipeline/bot.py`: long-poll loop, owner allowlist, `pair`, `/status`, `/progress`, `/help` | 1.5 h |
| Watcher: `runs` + manifest diff → push; one in-place progress message every 4 min during runs | 1.5 h |
| `remote_actions` table, nonce, expiry, hash binding; `approve --by --channel --nonce`; new `reject` with stored change request | 1.5 h |
| G1 (script text + Approve / Request changes), G2 (540p proxy + QA + Approve), G3 two-step code | 1.5 h |
| launchd plist install/uninstall (`python -m pipeline bot install`), log rotation, tests in `tests/` | 1 h |

**MVP done when:** the owner gets a push when a render finishes, watches the proxy, approves G2, completes G3 with the typed code, and `pipeline audit C000X` shows actor, channel, nonce and sha256 for each gate.

### Phase 2: review depth (about 1–1.5 days)
- Per-scene image and voice review (`review.json`), and G2 blocked until all scenes are OK.
- Saving voice takes and the compare UI.
- The `heavy.lock` queue and the allowlisted `produce`/`takes`/`qa` remote verbs.
- Publish verification at publish time (hash re-check).
- The `PreToolUse` hook blocking Claude from recording G3.
- Instagram job monitoring, overdue alerts and the `pmset` wake hint.
- Subagent start/stop hook → "which agent is running".

### Phase 3: optional dashboard (about 1.5–2 days, only after the §4.1 decision)
- FastAPI + server-rendered HTML (no build step), bound to localhost.
- Pages: queue, per-content timeline, scene grid with audio players, side-by-side takes, analytics tables from `report` output, and audit log.
- Same approval service and nonce rules; CSRF; Serve identity allowlist.

### Phase 4: analytics push (about 0.5 day)
- Daily launchd `pipeline analytics` → summary push.
- Weekly `optimization-strategist` report link (text only, cites `data/reports/*`).

---

## 10. What to avoid
- **Tailscale Funnel, quick tunnels or port-forwarding a web dashboard** to the internet: public exposure with app-only auth.
- **ZeroTier or Tailscale Personal** for a monetised channel without the owner explicitly accepting the "non-commercial" terms.
- **Telegram webhooks:** they need a public HTTPS endpoint. Long polling needs none.
- **Letting the bot or Claude call `publish` without the G3 two-step and a hash match**, or approving all languages by default from the phone.
- **A shell or "run any command" verb in the bot**, and file-download verbs that take a path.
- **Sending full-resolution masters** (150 MB, above the 50 MB bot limit [V]) or anything from `secrets/`.
- **GitHub Issues** on the public repo for approvals.
- **Running the Claude Code Channels plugin on the same bot token** as the studio bot.
- **Starting heavy jobs from the phone without the queue** (16 GB rule).
- **Adding paid add-ons:** ntfy Pro, Tailscale paid plans, a domain for Cloudflare Access.

---

## 11. Sources (accessed 2026-11-16)
- Telegram Bot API: https://core.telegram.org/bots/api (getUpdates vs webhooks, 24 h retention, `callback_data` 1–64 bytes, 50 MB upload / 20 MB download, local server 2000 MB, `protect_content`)
- Telegram Privacy Policy: https://telegram.org/privacy (cloud chats stored on Telegram servers; E2E only for secret chats)
- Claude Code Remote Control: https://code.claude.com/docs/en/remote-control
- Claude Code Channels: https://code.claude.com/docs/en/channels
- Tailscale pricing: https://tailscale.com/pricing · Pricing FAQ: https://tailscale.com/kb/1251/pricing-faq
- Tailscale Serve: https://tailscale.com/kb/1312/serve · Funnel: https://tailscale.com/kb/1223/funnel
- Cloudflare quick tunnels: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/
- Cloudflare Zero Trust plans: https://www.cloudflare.com/plans/zero-trust-services/ (free tier under 50 users per Cloudflare's pricing and blog; the table didn't render during research, so verify before relying on it)
- ZeroTier pricing: https://www.zerotier.com/pricing/
- ntfy: https://docs.ntfy.sh/publish/ · https://docs.ntfy.sh/config/
- macOS man pages on this Mac (macOS 27.2.1): `launchd.plist(5)` (KeepAlive, ThrottleInterval, StartCalendarInterval wake semantics), `caffeinate(8)`, `pmset(1)`
- Measured locally: proxy transcode of `content/C0005/hi/C0005-hi.mp4` (150 MB → 11.1 MB, 4.4 s); Opus scene clip about 25 KB

---

## Phase 1 implemented (2026-11-16): reliable event tracking

Hierarchy: workspace → `projects` → videos (`contents`/`variants`) → tasks (`task_state`) → `events`.

- **Tables (additive, created by `db.connect()` and by `events.connect()`):** `projects` (+ `contents.project_id`, backfilled to `ramayana`), `events`, `task_state` (latest state per variant/stage/platform; stage order from `projects.config.workflow`, default `events.WORKFLOW`), `issues` (deduped by `scope|stage|platform|error_code`; resolved by a later `completed`/`approved` event for the same scope, stage and platform), `outbox` (Telegram payloads for Phase 2; `pending` or `suppressed`).
- **`pipeline/events.py` `emit()`:** writes the event in its own transaction first, then task state and issues, then the outbox, each in a separate transaction. It never raises; on any failure it appends to `data/logs/events-fallback.log`. The DB is switched to WAL with a 5 s busy timeout. Never call `emit()` while the same process holds an open write transaction (see `queue.flush()` for the deferral pattern). A `Mac online` event is added on the first live event after 30 min of silence.
- **`pipeline/explain.py`:** catalogue of real errors → title, explanation, suggestion, retry safety, severity. Raw errors are kept verbatim after token redaction (`access_token=`, `Bearer`, `EAA…`, Google OAuth access tokens, refresh tokens, client secrets).
- **Instrumented:** `db.Run` (started/completed/failed), produce voice/images progress (files on disk, `events.Watch`), QA verdicts, approve/reject/waive and waiting-for-approval (G1 after `done script`, G2 after a non-failing video QA, G3 after `done metadata`), publish-queue (queued, status changes, upload start, limit/quota backoff, failure), `publish.py` (YouTube chunk progress at most every 10 %, uploaded/published, failures incl. `unknown_outcome`), `instagram.py` (tunnel live, container created, processing state), Instagram launchd jobs (installed, fired, skipped when over 24 h late, tunnel retries), analytics per platform.
- **CLI:** `events [--video V] [--since H] [--project P] [--kind K] [--backfill]`, `issues [--open] [--full]`, `issue show|resolve|ack <id>`, `projects [add <slug> --name … --languages …]`, `overview [--json]`.
- **Backfill (once, `events --backfill`):** 737 events from runs, QA reports, decisions, publications, publish-queue, `publish_run.log` and `data/logs/ig-*.log`, all with `detail.backfilled=true` and no outbox rows. Result: 21 issues, 18 resolved (e.g. Ep02 Instagram "API access blocked" ×2 and the container 18180328639433140 unknown outcome, resolved by the later successful posts), 3 open (C0001-gu and C0005-hi YouTube upload limit, waiting in the queue; C0005-en latest QA report fails).

## Phases 2 and 3 implemented (2026-11-16): Telegram notifications and the mobile dashboard

**Owner decisions behind these phases:** notifications come from a private Telegram bot. The dashboard is reached through a Cloudflare **quick tunnel** (trycloudflare.com: free, no account), and its current address plus a secret sign-in link are sent through Telegram. Both services run on the Mac at zero cost. These decisions override the "avoid quick tunnels" advice in §10 for the read-only dashboard. Approvals stay in the Claude chat until Phase 4. The bot and dashboard are **read-only**, except for acknowledging issues.

### What runs
| launchd label | Command | Log | Notes |
|---|---|---|---|
| `com.shortsstudio.queue` | `python -m pipeline publish-queue run` | `data/logs/queue.log` | YouTube upload queue. `service install` leaves it alone unless you pass `queue --restart` |
| `com.shortsstudio.bot` | `python -m pipeline bot run` | `data/logs/bot.log` | Long polling only (outbound HTTPS, no webhook, no open port). Drains the outbox every 5 s and writes a heartbeat to `data/bot_state.json`. Without a token it idles and logs once |
| `com.shortsstudio.dashboard` | `python -m pipeline dashboard run` | `data/logs/dashboard.log` | `ThreadingHTTPServer` on `127.0.0.1:8765` plus a supervised `cloudflared tunnel --url` child process |

All three use `KeepAlive`, `RunAtLoad`, `PYTHONUNBUFFERED` and the repo working directory. Measured at idle: about 0 % CPU and 30–35 MB RSS each.

### Commands
```
python -m pipeline service status                  # all three services
python -m pipeline service install                 # bot + dashboard (queue untouched)
python -m pipeline service install bot --restart   # restart one service
python -m pipeline service install queue --restart # only when you really want to restart the queue
python -m pipeline service remove bot dashboard
python -m pipeline telegram status | test | drain  # drain only works while the bot service is stopped
python -m pipeline dashboard link                  # queue the sign-in link to Telegram (--show prints it in this terminal)
python -m pipeline dashboard rotate-key            # new key + cookie secret; signs every phone out and queues the new link
```

### Telegram setup (one time; already done for @Chalkstudiobot)
1. In @BotFather: `/newbot`. Set **Allow Groups** to off.
2. On the Mac: `pbpaste | python -m pipeline telegram setup --token-from-stdin`, or set `TELEGRAM_BOT_TOKEN`. This validates the token with `getMe` and writes `secrets/telegram.json` with mode 600. The token is never printed, and logs redact it (`explain.redact` has a Telegram token pattern).
3. Run `python -m pipeline telegram pair` and send `/pair <6-digit code>` to the bot from your phone within 10 minutes. The bot stores `owner_chat_id`/`owner_user_id`.
   - If the bot service is running, pairing goes through the service; otherwise the command polls Telegram itself.
4. After pairing, every update from another chat, from a group, or from a different user is dropped without a reply and logged by id only.
5. On its first start the bot skips messages sent before it existed (`getUpdates offset=-1`).

### Notifications
- **Source:** `events.emit()` writes rows to `outbox`. Repeats of the same issue are stored as `suppressed`; only the first occurrence, a reopen, a severity change or the 3rd/10th/50th occurrence is `pending`.
- **Sending:** `notify.drain()` sends `pending` rows (HTML parse mode, escaped) at most 1 per second.
  - When more than 5 rows are due at once, they go out as **one digest**. Critical issues and local messages, such as the dashboard link, are still sent on their own.
  - A row is claimed (`sending`), sent, then marked `sent` with the Telegram `message_id`. A `sent` row is never sent again.
- **Retries:** 429 waits for `retry_after`; 5xx and network errors back off 15 s → 1 h. After 10 attempts, or on a permanent 4xx, the row becomes `failed`.
  - If Telegram can't parse the HTML, the message is sent again as plain text.
  - A row stuck in `sending` for 5 min (crash mid-send) goes back to `pending`.
- **Secret links:** after sending, the sign-in link is removed from the stored payload.
- **Failure format:** `❌ Upload failed — Ramayana Ep04 (Hindi)` / `Reason:` / `Details:` / `Action:` / `Retry safe:` / `Video: C0004-HI` / `At: 10:42 PM` / `Log:`.
  - The headline changes with the stage and kind: `❓ … outcome unknown`, `⏳ Upload delayed`, `Render failed`, `QA failed`, `Blocked at G2 final video`. A repeat adds `(3×)`.
- **Other messages are short:** `✅ Uploaded to YouTube — …`, `✅ Posted on Instagram — …`, `📝 Approval needed (G1 script) — …`, `✅ Recovered — …`, `💻 Mac online — …`.
- **Bot commands:** `/status`, `/overview`, `/issues`, `/queue`, `/uploads`, `/timeline [C0006-hi]`, `/link`, `/ack <id>` (acknowledge only) and `/help`.

### Dashboard
- **Pages:** Overview, Projects, Queue (filters for project, language, stage, status and date), Uploads (YouTube queue, measured upload progress only, Instagram jobs, publications, upload problems), Issues (with an Acknowledge button), Timeline (per-video history with `?video=`) and Analytics (latest snapshot per video, latest insights findings and actions, next 20:00 collection).
- **Server-rendered:** HTML with one small vanilla-JS file; no new dependencies.
- **Paths:** absolute paths are cut back to repo-relative paths, and home directories become `~`.
- **Sign-in:**
  - `secrets/dashboard.json` (mode 600) holds a random 32-byte `login_key` and `cookie_secret`.
  - `/login?k=<key>` is compared in constant time, then sets `ss_session`: HMAC-signed, expiry 30 days, `HttpOnly; Secure; SameSite=Strict`. It then redirects to `/` so the key leaves the address bar.
  - Failed logins are limited to 5 per IP (from `CF-Connecting-IP`) and 30 in total per 15 min, then return 429.
  - Every page and API requires the cookie; without it you get a 401 page.
  - Only a fixed set of static files is public: CSS, JS, manifest, service worker, icons, offline page and `/healthz`. Everything else returns 404; there is no file serving and no directory listing.
- **Security:**
  - Headers: CSP `default-src 'self'` (no inline script), `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `nosniff`, and `Cache-Control: no-store` on pages.
  - Ack is a POST with a per-session CSRF token and a same-origin `Origin` check.
  - Request logs never include query strings.
- **Live updates:** one shared poller reads `events` every 3 s, and only while someone is watching.
  - Local browsers get Server-Sent Events (`/events/stream`).
  - **Measured on 2026-11-16:** the quick tunnel buffers streamed responses until they close. SSE and chunked plain text behaved the same with 2 KB and 70 KB padding. So pages opened through the tunnel automatically use **polling** of `/api/events` every 10 s, and `/events/stream` answers 409 to tunnel requests.
- **Tunnel manager:**
  - It starts `cloudflared tunnel --no-autoupdate --url http://127.0.0.1:8765`, reads the `*.trycloudflare.com` address from stderr, and confirms `/healthz` from outside.
  - It stores the address in `data/dashboard_url.json`. When the address changes it queues a Telegram message with the sign-in link.
  - It checks the address every 5 min, restarts cloudflared after 3 failed checks or if it exits (backoff 10 s → 5 min), and stops a stale child process from a previous run.
  - Cloudflare documents quick tunnels as for testing only, with no uptime guarantee, so expect occasional new addresses.

### Android steps
1. Open the **Dashboard** message from the bot and tap **Open the dashboard**. Chrome opens, signs in and keeps you signed in for 30 days.
2. In Chrome, tap ⋮ → **Add to Home screen** (or **Install app**). The app opens full-screen.
3. **When the address changes** (Mac restart, cloudflared restart, quick-tunnel drop), the bot sends a new link.
   - The old home-screen icon points at the dead address and shows the offline page.
   - Open the new link from Telegram, then add it to the home screen again and remove the old icon. A quick-tunnel address can't be kept stable for free.
4. Send `/link` to the bot at any time to get the current link again.

### When things are offline
- **Mac asleep or lid closed:** no notifications are sent, and the dashboard shows the cached "Mac unreachable" page.
  - Events still go into the outbox; when the Mac wakes, the bot sends them (as one digest if more than 5).
  - If the bot was down for over 10 minutes, it says `💻 Mac online — … offline since …`.
- **Mac offline but awake:** the same as above. cloudflared reconnects by itself, and if the address changes you get a new link.
- **Phone offline:** Telegram delivers the queued messages when the phone reconnects, and the dashboard shows the offline page until then.

### Troubleshooting
- **No messages:** run `python -m pipeline service status` and `tail data/logs/bot.log`, then `python -m pipeline telegram status` to see outbox counts. `telegram test` sends one message.
- **Dashboard link dead:** send `/link`. If there's still no address, `tail data/logs/dashboard.log` and `python -m pipeline service install dashboard --restart`.
- **"Link not valid":** the key was rotated, so use the newest link. **"Too many attempts":** wait 15 min.
- **A leaked link:** run `python -m pipeline dashboard rotate-key`. **A leaked bot token:** `/revoke` it in BotFather, then run `telegram setup` again.
