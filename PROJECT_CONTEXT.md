# PROJECT_CONTEXT — shorts-studio

> **Before making any changes, read this entire document, inspect the current project state, verify completed work, identify the last completed workflow stage, and resume from the exact next pending task. Do not repeat completed work or overwrite existing decisions without a documented reason.**
>
> Quick orientation: `python -m pipeline status` shows every content item and its next action. §22 Current status and §23 Next steps are the source of truth for where work stopped.

---

## 1. Vision & objectives
A zero-cost, local-first, multi-agent content studio that discovers opportunities, understands Indian language audiences, writes strong stories, produces 9:16 animated videos with natural narration, publishes on schedule (YouTube first), measures real performance and feeds learnings back into the next production.
- **Owner:** a single creator on a MacBook Air (Apple M5, 16 GB RAM).
- **Channel:** YouTube "Knowledge PowerBank".
- **First series:** *RAMAYANA — The Epic in Chalk* (Valmiki Ramayana, chalkboard style, English + Hindi).
- **Hard constraints:** no paid APIs, subscriptions or credits; commercial-use licenses only; human approval before any public release.

## 2. Architecture overview
```
                ┌──────────── Claude Code (judgement) ─────────────┐
 research ─▶ audience ─▶ strategy ─▶ script ─▶ [G1 script] ─▶ creative direction
 (subagents in .claude/agents, skills in .claude/skills)          │
                └──────────────────────────────────────────────────┘
                                   │ files in content/<ID>/
                ┌──────────── Python pipeline (deterministic) ─────┐
 voice ─▶ language QA ─▶ images ─▶ render ─▶ video QA ─▶ [G2 final]
 metadata ─▶ schedule ─▶ [G3 publish] ─▶ publish ─▶ analytics ─▶ optimize ─▶ next
                └──────────────────────────────────────────────────┘
 state: content/<ID>/manifest.json + data/studio.db (SQLite)
```
- **Engines (pre-existing, kept):**
  - `studio.py`: script → voice → images → audio mix → render → thumbnail.
  - `chalk.py`: chalkboard renderer and sound design.
  - `veena.py`: Hindi TTS.
  - `styles.py`: visual presets.
  - `publish.py`: YouTube and Instagram uploader.
- **New layer:**
  - `pipeline/`: orchestration CLI, database, research, QA, analytics and scheduling.
  - `.claude/agents/`: 5 active subagents + 1 dormant (§3).
  - `.claude/skills/`: storytelling, content-pipeline runbook, audio-mix, and the manual-only publish skill.
  - `profiles/`: languages, voices and characters.

## 3. Agents (`.claude/agents/*.md`)
Consolidated 2026-11-16 from 10 to 5 active + 1 dormant (owner decision O10; spec in `docs/WORKFLOW_AUDIT.md` §18.3). The retired definitions are kept for history in `docs/retired-agents/` (outside `.claude/agents/`, because Claude Code scans that folder recursively and would still load them).

| Agent | Role | Main outputs | Tools |
|---|---|---|---|
| series-planner | Per arc: episode map, teaser chain, language plan, profile updates with evidence (was trend-researcher + content-strategist + audience-localizer) | `content/series/<series>.md`, profile diffs | Read/Write/Edit, Bash (`pipeline research`, `trending`), Web |
| scriptwriter | Source verification (verse table with edition), hooks, scripts for every language within the 35–55 s word budgets; must pass `pipeline lint` (absorbs per-episode localization) | `research/report.md`, `<lang>/hooks.json`, `script.json`, `script.md` | Read/Write/Edit, Bash, Web |
| creative-director | Positive-only prompts with `{character}` tokens, character bible, reference sheets, regeneration requests; no longer judges its own images | `visual`/`seed` fields, `profiles/characters/*.json` | Read/Write/Edit, Bash, Web |
| reviewer | Subjective Story QA before G1, Visual and Audio QA before G2; scores and numbered fixes, never edits (was language-qa + video-qa) | review text saved by the main session as `<lang>/review.md` | Read, Grep, Glob only |
| packager | YouTube and Instagram metadata per language and the G3 bundle text; never uploads, schedules or approves (was publishing-manager) | `<lang>/publish.json` | Read/Write/Edit, Grep, Glob, WebSearch (no Bash) |
| optimizer (dormant) | Activates when ≥30 published variants have 7-day data; evidence-graded recommendations (was optimization-strategist; performance-analyst's steps are now plain `pipeline analytics/report` commands) | `recommendations` table, `data/reports/recommendations.md` | Read/Write, Bash |

Production (voice, images, render, QA, analytics, upload) is the Python pipeline, run by the main session. No agent runs `pipeline approve` or `pipeline publish`; the reviewer and packager have no Bash at all.

All agents share house rules: no fabricated data, cite evidence files or URLs, zero cost, and stop at the gates.

## 4. Execution order & gates
The full table is in `.claude/skills/content-pipeline/SKILL.md`. Summary: `(arc plan) → new → sources + hooks + scripts → visual plan → lint → story review → G1 → voice → images → render → qa → visual/audio review → G2 → metadata + schedule proposal → G3 per platform → /publish → analytics (24h/48h/7d/14d/30d) → optimize (dormant)`.
- **Gates** are recorded by the owner with `python -m pipeline approve <ID> script|final|publish`. G1 requires a `pipeline lint` pass; G2 requires a QA pass or warnings with recorded waivers; G3 is recorded per platform with times and file hashes (roadmap A10/A11, being implemented).
- `produce` refuses to run without G1, and `publish` refuses without G2 and G3.
- **Parallelism:** research per topic, and per-language script/metadata, can run in parallel through subagents. Heavy models never run in parallel (see §8).

## 5. Claude Skills
| Skill | Location | Purpose |
|---|---|---|
| `storytelling` | `.claude/skills/storytelling/` | 35–55 s beat framework and timings, per-language word budgets, hook/loop rules, edition-labelled citations, 7 genre templates, script JSON schema, review checklist |
| `content-pipeline` | `.claude/skills/content-pipeline/` | Runbook: stages, lint before G1, QA-gated G2, per-platform G3, agents, heavy lock, cleanup, recovery |
| `publish` | `.claude/skills/publish/` | Upload/schedule steps; `disable-model-invocation: true`, so only the owner can start it with `/publish` |
| `audio-mix` | `.claude/skills/audio-mix/` | Mix hierarchy, −16 LUFS narration, two-pass −14 LUFS loudnorm, ducking and SFX levels, licensed sources with `licenses.csv`, audio QA thresholds |
| `yt-script`, `yt-package`, `yt-retention`, `yt-viral`, `yt-seo`, `yt-plan`, `yt-audit`, `yt-comment` | `.claude/skills/yt-*` (vendored from Jakeschincariol/youtube-agent-skill @ a2feb21, MIT; see `.claude/skills/_vendor/youtube-agent-skill/VENDORED.md`) | Second-opinion hook scoring, title + thumbnail lint, retention leak analysis (`python -m pipeline retention-csv`), outlier-multiple research, SEO/plan/audit/comment guidance. Skipped: yt-edit, yt-shorts, yt-chapters (long-form only) |
| `skill-creator` | Built into Claude Code (anthropic-skills) | Extend or create skills; not vendored |

Ecosystem review (2026-11-15): the official `anthropics/skills` repository has 19 skills. None cover research, storytelling, video or analytics, so none were installed. Licenses there are per skill, and docx/pdf/pptx/xlsx are source-available, not open source. No MCP server is needed: the YouTube APIs are called directly.

## 6. Tools, models, APIs & licenses
| Purpose | Tool / model | License / cost | Notes |
|---|---|---|---|
| Script drafting (optional) | Ollama + Qwen3 8B | Apache-2.0 | Hallucinates facts; used only with Wikipedia grounding plus a fact-check pass. Premium scripts are written by Claude Code (your existing subscription) |
| Images | Z-Image Turbo 4-bit via mflux 0.24 | Apache-2.0 / MIT | `models/z-image-turbo-4bit` (5.5 GB); about 58 s/image at 576×1024, about 100 s at 768×1344; 8.3 GB peak |
| English voice | Kokoro-82M (`af_heart`) via mlx-audio | Apache-2.0 | Speed 1.04 |
| Hindi voice (retired 2026-11-16) | Veena 3B (`maya-research/Veena`, speaker kavya) | Apache-2.0 | About 5× slower than real time, 9.4 GB peak on MPS bf16; stochastic, so use best-of-3 takes |
| **Hindi voice (current)** | **Maya 2 Native, voice Malini** (Apache-2.0, ungated) via mlx-audio `maya2` | Apache-2.0 | About real-time on the M5 Air; 11 Indian languages + English, 20 voices; built-in number/date normalization; backend `voice: maya2:<Voice>` in studio.py and pipeline/voicepack.py |
| Other Indic voices | ai4bharat/indic-parler-tts (candidate) | Apache-2.0, gated (free HF login) | Untested; needs `HF_TOKEN` |
| Speaker verification | speechbrain ECAPA (spkrec-ecapa-voxceleb) | Apache-2.0 | `pipeline/speaker.py`; voice-consistency guard and QA |
| ASR / QA / caption timing | faster-whisper small (EN), large-v3-turbo (other languages) | MIT | |
| Fonts | macOS system fonts (Chalkduster, Chalkboard SE, Kohinoor, ITF Devanagari, Sangam MN) + libraqm | System / LGPL | Text shaping requires `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`; `studio.py` re-execs automatically |
| Video | ffmpeg + VideoToolbox | LGPL/GPL | Render is about 1 min per video (measured on the 75–95 s renders of Ep01–05) |
| Research | YouTube Data API v3, Wikimedia pageviews, Google autocomplete (unofficial) | Free (10k YouTube units/day) | **Not available:** Google Trends API (pytrends archived), Instagram/TikTok trend APIs |
| Publishing | YouTube Data API v3 (OAuth, own GCP project "upload-automation") | Free | API uploads were *not* audit-locked in practice (owner made one public). The API audit is still recommended |
| Analytics | YouTube Analytics API v2 | Free | Separate read-only token. No hour-of-day dimension; data lags 1–3 days |
| **Excluded** | macOS `say` voices (Apple SLA: personal non-commercial), IndicF5 (non-commercial training data), MusicGen (CC-BY-NC), FLUX-dev, Remotion (licence for companies with 4+ employees), Wan/LTX video (too slow on the Air) | | |

## 7. Setup (new machine)
```bash
brew install ffmpeg uv ollama libraqm espeak-ng
git clone <repo> shorts-studio && cd shorts-studio
uv venv -p 3.12 .venv && source .venv/bin/activate
uv pip install -r requirements.txt pytest
ollama pull qwen3:8b                        # optional
mflux-save --model z-image-turbo --quantize 4 --path models/z-image-turbo-4bit   # one-time ~31 GB download → 5.5 GB
hf download maya-research/Veena && hf download hubertsiuzdak/snac_24khz
python -c "from faster_whisper import WhisperModel as W; W('small'); W('large-v3-turbo')"
python -m pytest -q tests
```
For credentials, follow `docs/PUBLISHING.md`: create your own GCP project, enable YouTube Data API v3, configure the OAuth consent screen as External/Testing with yourself as test user, create a Desktop client, and save it as `secrets/youtube_client_secret.json`.

## 8. Environment & hardware rules
- **Secrets:** only in `secrets/` (chmod 700, gitignored). Optional `.env` (see `.env.example`, `HF_TOKEN`).
- **Memory (16 GB):** never run two heavy models at once (Qwen, Z-Image, Maya 2, Whisper-turbo); heavy steps hold `data/heavy.lock`. Run `ollama stop qwen3:8b` before images or voice. The fanless Air throttles on long runs, so keep it plugged in.
- **Disk:** 92 GB free at the time of writing. `~/.cache/huggingface/hub/models--Tongyi-MAI--Z-Image-Turbo` (~25 GB of bf16 blobs) can be deleted once `models/z-image-turbo-4bit` exists. The owner decides.

## 8b. Progress & ETA reporting
`python -m pipeline progress <ID>` derives progress from the files each step produces (works for runs already in progress):
- per-step status, done/total, measured seconds per unit, time left
- total time left and clock finish time

Use `--watch N --oneline` for periodic updates; the owner wants an update every few minutes during long runs. Rates are learned into `data/rates.json`. Measured so far: Veena best-of-3 about 2 min per scene, Z-Image 768×1344 about 100 s per image, Kokoro about 1 s per scene, render about 1.5 min per video.

## 9. Production standards (defaults)
- **Format:** 1080×1920, 30 fps, H.264 (VideoToolbox, 12 Mb/s), AAC 192 k.
- **Loudness:** −14 LUFS target (loudnorm); QA accepts −16.5 to −13, true peak ≤ −1 dBFS. Target chain (narration at −16 LUFS, two-pass linear loudnorm): `audio-mix` skill.
- **Duration:** 35–55 s per language, hard limit under 60 s (owner decision O1, 2026-11-16; Ep01–05 ran 74.8–111.2 s under the old 60–95 s rule). `pipeline lint` blocks G1 above a 57 s estimate; final QA rejects ≥60.0 s. 8–11 scenes of 2.5–7 s; word budgets per language in the `storytelling` skill. Show verses on screen with the meaning narrated rather than reciting them in full.
- **Chalk style:** a shared procedural board, a palette limited to white/saffron/gold/green, stroke-by-stroke reveal with chalk stick and dust, whole-board streak-erase transitions, Chalkduster titles with dark halo, word-synced captions with saffron keywords, generated tanpura + bansuri (Bhairavi) score.
- **Chalk SFX gain is permanently reduced: `chalk.CHALK_SFX_GAIN = 0.035`** (30% below the first render). Do not revert. `music_gain` is 0.25.
- **Captions:** grouped by punctuation (including । ॥ —), balanced chunks, `caption_max_chars` per language, no line starting with a Hindi postposition, word timing from Whisper.
- **Presets:** `styles.py` defines pixel, cartoon, whiteboard, papercut, cinematic and chalk.

## 10. Multilingual & localization strategy
- 10 language profiles in `profiles/languages/` (en, hi, mr, bn, te, ta, gu, kn, ml, pa). Each holds Census 2011 audience size, the regional Ramayana traditions that shape expectations, localization guidance, caption font, slot hypotheses and festivals. **Status:** en/hi in use; the other 8 are drafts that need native-speaker review.
- **Rule:** every language version is written originally (audience brief → fresh script). Sanskrit verses stay in Sanskrit in that script, followed by a natural explanation.
- **Voices:** `profiles/voices.json`. Approved: en (Kokoro af_heart); hi, gu and te (Maya 2 Native `maya2:Malini`, since 2026-11-16; Veena kavya retired). The other 6 languages are blocked until a voice is evaluated and a native speaker has listened.
- **gu/te review status (owner decision O9):** the gu and te voices were approved without the native listen the voice policy requires, so both are tagged `review_status: unreviewed-language` in their profiles and analysed as a separate cohort until a native reviewer signs off.

## 11. Research & topic selection
- **Evidence:** `python -m pipeline trending`, and `python -m pipeline research <ID> --query … --wiki … --langs …` (cached 6–24 h; about 200 YouTube units per language).
- **Scoring:** weighted factors in the `series-planner` agent, per arc. Every score cites evidence or is labelled as judgement. Topics are not chosen only because they trend.

## 12. Storytelling & hooks
See `.claude/skills/storytelling/SKILL.md`. Write at least 6 hooks per language, score them on the 6-criterion rubric (curiosity, emotion, specificity, speed, resonance, accuracy), and keep them in `hooks.json` with reasoning. Mythology rules: cite book.chapter.verse, never invent verses or dialogue, label later traditions, depict deities symbolically when in doubt.

## 13. Publishing workflow
`publish.json` (metadata) → `pipeline schedule` (slot experiment: explore each candidate IST slot until it has 3 × 48 h samples, then exploit) → **G3** → `pipeline publish` (private upload with `publishAt`, plus playlist and thumbnail; the publication is recorded in the database). Pinned comment and Related-video link are set manually in Studio. Instagram: `instagram.py` (Instagram API with Instagram Login, v27.0) publishes Reels via a temporary cloudflared tunnel (Meta fetches `video_url`). Scheduling is a self-removing launchd job; see `docs/PUBLISHING.md`. Enabled by the owner on 2026-11-16. It still needs G3 approval for the Instagram post specifically.

## 14. Analytics
`python -m pipeline analytics` takes due snapshots per publication at 24h, 48h, 7d, 14d and 30d. Each snapshot stores public counters, totals (views, watch minutes, average view duration and percentage, likes, comments, shares, subscribers), daily series, traffic sources, top countries and the retention curve. `python -m pipeline report <VARIANT>` produces a markdown report with retention insights and comparisons. Only metrics the API returns are recorded.

**Analytics checkup → understanding → improvement (every new episode).** `python -m pipeline insights [--days N]` (`pipeline/insights.py`, reusing `learn.rolling_ratios` and the report helpers) writes `data/reports/insights-<date>.md` and `data/reports/latest_insights.json`: per variant and platform the latest snapshot age, views, reach, likes, comments, shares, saves, avg watch (Instagram ms → s), watch ratio (avg watch / duration from ffprobe of the mp4, else `features.duration_s`) and shares/saves/likes per reach (per view on YouTube); per-language rolling medians at the same age bucket; findings with tiers; ≤5 carry-forward actions; conflicts. The daily LaunchAgent runs `analytics --insights` at 20:00 (read-only; never publishes). Before scripts the main session runs `analytics` (if the last snapshot is >12 h old) and `insights`; the scriptwriter applies the actions and records `applied_learnings`; the owner sees a 3–5 bullet "Learnings applied" block with the scripts at G1. No new approval.

## 15. Optimization logic
Recommendations carry evidence and a confidence level: low below 5 videos, medium 5–15, high above 15 with a consistent effect. A style or profile change needs medium confidence or better **and** owner approval. Mapping: early drop → hook; mid-video drop → scene pacing or visual; language gap → series-planner / scriptwriter; slot effects → scheduler.

Lightweight loop (`insights`): evidence tiers are **anecdote** (<6 comparable variants or <48 h of data), **directional** (≥6 per group in the same age bucket, ≥48 h) and **confirmed** (a pre-registered experiment met its rule in `learn.py`). Only like windows are compared and raw views never across languages. Actions are testable script guidance inside the approved rules (35–55 s, hook ≤3.0 s, frame 0 ≥70% drawn, engagement line ≤6 words); conflicting signals are listed, never acted on, and anecdotes never override approved rules. The optimizer stays dormant for formal recommendations until ≥30 variants have 7-day data.

## 16. Content database (`data/studio.db`, SQLite, gitignored)
| Table | Contents |
|---|---|
| `contents` | Topic, series, style, status, folder (IDs `C0001…`) |
| `variants` | Language versions (`C0001-hi`), voice, paths, duration |
| `research` | Raw evidence payloads |
| `hooks` | Hook candidates, scores, the selected hook |
| `decisions` | Who decided what and why, including gates |
| `runs` | Stage timings and failures (production time tracking) |
| `qa_reports` | QA results |
| `publications` | Platform IDs, URLs, schedule, slot |
| `analytics_snapshots` | One row per publication per window |
| `recommendations` | Optimizer output |

## 17. Repository structure
```
shorts-studio/
  PROJECT_CONTEXT.md  README.md  requirements.txt  .env.example  .gitignore
  studio.py chalk.py veena.py styles.py publish.py      # engines
  pipeline/  (__main__ CLI, db, research, qa, analytics, schedule)
  .claude/agents/*.md   .claude/skills/{storytelling,content-pipeline,audio-mix,publish}/
  profiles/languages/*.json  profiles/voices.json  profiles/characters/*.json
  content/<ID>/  manifest.json brief.md research/ audience.md strategy.md <lang>/{script.json,hooks.json,publish.json,qa.md,...}
  docs/  (BLUEPRINT.md original free-tools research, PUBLISHING.md credentials and disclosure, upgrade research docs, retired-agents/)
  tests/test_pipeline.py
  out/ models/ data/ secrets/ .venv/   # gitignored
```
**Git:**
- Repository: https://github.com/AyushmanKS/video_workflow (public, branch `main`).
- Commit author for this repo only: `AyushmanKS <AyushmanKS@users.noreply.github.com>`.
- Push auth uses a repo-local credential helper (`!gh auth git-credential`, GitHub CLI logged in as AyushmanKS). The Keychain helper is blanked for this repo only, because the Mac's Keychain holds a different GitHub account.
- Before every commit, scan staged files for secrets (`git diff --cached`) and confirm no media or DB files are staged.

**Storage strategy:** videos, audio and images stay out of git (content/** media and out/ are gitignored). Back them up to a cloud drive or external disk, or use Git LFS later if needed. Scripts, manifests and reports are small and versioned.

## 18. Key files
- **`studio.py`**: the CLI production engine. Supports `--out`, `--stop-after`, `--redo`, `--voice` (Kokoro name or `veena:<speaker>`), per-scene `tts`/`speed`/`seed`/`pause`, and Whisper word alignment (`align_words`). It also does caption grouping (`caption_tokens`, `caption_groups`, `POSTPOSITIONS`).
- **`chalk.py`**: board and palette, reveal order (connected-component trace), `plan()` timing, `render()`, `text_scene()` (verse/shloka), `font_for()` for all scripts, `music()` and `sound()` SFX, `thumbnail()`.
- **`veena.py`**: phrase chunking with punctuation pauses, SNAC decode.
- **`publish.py`**: OAuth (`google_credentials`, separate upload and analytics tokens), `youtube_upload` (publishAt, playlist, thumbnail, DB record), `instagram_publish` → `instagram.py` (tunnel + `video_url`, dry run, duplicate guard). `pipeline/igschedule.py` installs and removes the launchd jobs; `pipeline ig-jobs` lists them.
- **`pipeline/__main__.py`**: commands `new status trending research approve done produce takes progress qa schedule publish link analytics report retention-csv`.

## 19. Completed implementation
- 2026-11-15: original pipeline and 6 styles; pixel-art demo.
- 2026-11-15: Episode 01 EN + HI (chalk), Veena Hindi voice, quieter chalk SFX, both published (EN `iAOekr93Rwc`, HI `ATBD85fpgwY`) in playlist "Valmiki Ramayana".
- 2026-11-15: `publish.py` with OAuth; EN uploaded via API and made public by the owner.
- 2026-11-15: **foundation build:**
  - `pipeline/` package and SQLite database
  - research (YouTube + Wikipedia + autocomplete)
  - automated QA, analytics, slot scheduler
  - 10 subagents, 2 skills, 10 language profiles, voice registry, character bible
  - repo hygiene (`.gitignore`, `.env.example`, requirements), unit tests (7 passing)
  - Episode 01 backfilled as C0001 with publications

## 20. Pending implementation
- Analytics read-only token (owner sign-in), then the first real snapshots and reports for C0001.
- Indic Parler-TTS evaluation for mr, bn, te, ta, gu, kn, ml, pa (needs a free HF token from the owner), then native-speaker listens.
- Scheduled analytics: a launchd plist to run `python -m pipeline analytics` daily. The template is not installed yet; the owner decides.
- Optional: YouTube API compliance audit application.

## 21. Known limitations
- **Incident 2026-11-16, Hindi speaker drift:** Veena was called once per short phrase, and short prompts made the speaker identity drift. The result was different female voices and some male voices inside one narration (C0002-hi: 42 of 56 phrases off; published Ep01-hi: 38 of 47 off). Word-level QA could not detect it.
  - **Fix:** scene/sentence-level generation, a stored ECAPA reference for kavya, a speaker guard (similarity ≥0.72, pitch 150–320 Hz) and a QA `speaker_consistency` check that fails the video.
  - **Measured after the fix:** whole-scene takes score 0.81–0.84 against the reference.
  - **Final mechanism: voice-prompt priming.** Veena gets the kavya reference recording (`profiles/voices/hi_kavya_ref.wav` + text) as context before each scene. Drift-prone lines went from 0.26–0.36 to 0.78–0.85 similarity.
  - **QA calibration:** speaker checks use 2.5 s windows, failing on any window below 0.5 or any scene below 0.7. Measured: consistent voice minimum 0.61; known-mixed Ep01-hi median 0.46 with 50% of windows below 0.5. One-second clips are unreliable (the same voice scores as low as 0.57).
  - **Episode 01 Hindi (published) still has the drift.** Re-producing it needs an owner decision (new upload; YouTube can't replace a video file).
- **Data the APIs can't provide:** no Google Trends or Instagram/TikTok trend APIs; YouTube Analytics has no hour-of-day data; Shorts impressions/CTR may be missing from the API.
- **Image model:** Z-Image renders shaded pastel-like chalk, not sparse line art. The stroke reveal is algorithmic, not true artist stroke order.
- **Voice QA is limited:** Whisper CER is a proxy, inflated by digits and spelling quirks. Native listening is the real accent check.
- **Untested profiles:** 8 language profiles are unreviewed drafts.
- **English Episode 01:** some caption lines fell back to a smaller font (fixed for future videos via `caption_max_chars`).
- **Hindi Episode 01 YouTube title** begins with "valmiki ramayana episode 01 hindi:" (pasted manually); the owner may want to edit it.
- **Network:** occasional timeouts to googleapis/wikipedia; research uses retries.

## 22. Current status (update every session)
- **C0002 (Episode 02):** scheduled for 2026-11-16, HI 20:30 / EN 21:30 IST.
- **C0003 (Episode 03):**
  - **EN** is scheduled for Tue 2026-11-17 21:30 IST (`XziMigS1G0w`).
  - **HI:** the owner rejected the Veena version for pronunciation. It was re-voiced with **Maya 2 Malini**, and QA passes, including speaker consistency with the per-voice calibration.
  - **HI (Malini) approved by the owner and scheduled** for Tue 2026-11-17 20:30 IST (`fPFUIizlkl4`).
- **Voice decision (2026-11-16):** Hindi moves from Veena kavya to Maya 2 Malini, chosen via a listening pack (`python -m pipeline voicepack`). Malini is far more accurate and about 6× faster. Voice QA is now per voice: a stored reference centroid plus calibrated thresholds.
- **Other changes:** QA normalizes ज्ञ↔ग्य; the Veena lead-in was reverted; the audio folder records the voice used (`audio/voice.txt`) and QA uses it.
- **C0004 (Episode 04, Vishvamitra asks for Rama):** owner approved scripts, final videos and publish plan on 2026-11-16. Scheduled Wed 2026-11-18: HI 20:30 IST (`tuDnAZuQyGk`), EN 21:30 IST (`YgLlg2_Do7I`); publishAt verified by API read-back. Scene 4 image was regenerated twice (border, then Western bat-winged gargoyles) and edge-cropped. Hindi scene 12 was regenerated for a pitch spike.
- **Fixes 2026-11-16 (Ep04):** music padded to voice length (off-by-one crash); caption chunks keep splitting until each fits `caption_max_chars`; speaker QA now loads a reference for any voice id (`profiles/voices/<lang>_<name>_ref.npy`), with `en_af_heart_ref.npy` built from approved C0003-en. Without a reference, QA falls back to scene 1 as the reference, which causes false flags.
- **Instagram (2026-11-16): live.** @mr.aks.tale is connected through Meta Unified login: business portfolio, system-user token that never expires, IG id 17841412994195231, host graph.facebook.com (`instagram.py` handles both token types). Uploads go through a temporary cloudflared link. Reels set caption, cover, `audio_name`, `is_ai_generated=true` and `share_to_feed`. Scheduling uses launchd jobs (`pipeline/igschedule.py`): caffeinate keeps the Mac awake, tunnel failures retry, jobs remove themselves after success. **The Mac must be awake and plugged in at post time**, because Instagram has no server-side scheduling.
  - **Ep01 en/hi/gu/te published 2026-11-16 ~15:35 IST:** te DfzGhiriqnz, gu DfzG3qpD49H, hi DfzHMW2CNcl, en DfzHjJ4nBpc. Researched captions per `reports/Instagram Reels Ep01 audience strategy.md`.
  - **Ep02:** hi Tue 17 Nov 20:00 and en 20:30 IST scheduled (`python -m pipeline ig-jobs`). gu/te wait for owner G2.
  - **Token rotation:** the token was pasted in chat once; rotate it (revoke in Business settings, regenerate, `instagram.py setup` in the owner's own terminal).
- **Pending:** the owner must enable the YouTube Analytics API in GCP project 145069760719, then run `python -m pipeline analytics --force`; optional HF token (Indic-Speak/IndicConformer); old-episode Hindi re-voice was declined by the owner (2026-11-16); after each video goes live, the owner adds pinned comments and Related-video links manually.

## 23. Exact next steps
1. Episode 05 (C0005): Tataka (Bala Kanda 24–26; teaser verse 1.24.26). Only start when the owner asks. Flow: `new` → research/strategy/audience → EN+HI scripts (original Hindi) + hooks → G1 → produce EN (af_heart) then HI (`maya2:Malini`; regenerate flagged scenes with the speaker/pitch check) → `qa` → manual image review (watch for borders, Western fantasy demons, Ravana depiction) → metadata + schedule (evening, HI 20:30 / EN 21:30, one episode per day) → G2/G3 → `publish --yes`.
2. Analytics snapshots once the API is enabled; then run the optimization pass.
3. After the owner provides `HF_TOKEN`, run the adoption plan in `reports/Shorts studio voices and tools.md` §plan.

## 24. Testing
- `python -m pytest -q tests` (unit tests: captions, DB, scheduler, QA scoring, fonts, profiles).
- Smoke test: `python -m pipeline status`, `python -m pipeline trending`, `python -m pipeline qa <ID> --lang <l>` on any rendered variant.
- A render regression check uses an existing work dir: `python studio.py "<topic>" --style pixel` re-renders from cache in seconds.

## 25. Recovery & resume
- `python -m pipeline status <ID>` shows the next action; manifests record each stage with timestamps, and the `runs` table records failures.
- Interrupted production: rerun the same `produce` step. Cached scene assets are reused, and only missing ones are regenerated.
- One bad scene: delete `img/NN_raw.png` or `audio/NN.wav` + `audio/NN.words.json` and rerun. Optionally set `"seed"` / `"voice_seed"` on that scene.
- An OAuth token expired (Testing mode, about 7 days): the next command opens the browser sign-in again.
- Legacy Episode 01 assets live in `out/ramayana-ep-01-…/` (`final/` holds the published files); C0001's manifest points there.

## 26. Studio upgrade research (2026-11-16) — awaiting owner approval
The owner asked for a full audit and research plan before any change. Nothing was implemented, and no approvals or episodes were touched. Documents:
- `docs/WORKFLOW_AUDIT.md` (stage-by-stage audit, priorities; agents 10→5+1; QA scoring; learning-loop rules)
- `docs/VIDEO_QUALITY_UPGRADE_PLAN.md` (35–55 s beat framework and word budgets, readable frame 0 and reveal modes, shot grammar, visual bible with per-world accents, character consistency method, sound direction and mix chain, 27 prioritised changes)
- `docs/TOOLS_AND_SKILLS_RESEARCH.md` (ranked tools with licences; nothing external worth installing in Claude Code; do-not-use list)
- `docs/MOBILE_CONTROL_ARCHITECTURE.md` (private Telegram bot daemon + Claude Code Remote Control; optional dashboard pending a licence decision)
- `docs/GROWTH_AND_MONETIZATION_STRATEGY.md` (one channel + one IG account for now; YPP changes on 1 Feb 2027; inauthentic-content risk; compliance fixes)
- `docs/PRODUCTION_ROADMAP.md` (phases A–E)
- Notes: `research_notes/Studio upgrade research/`

**Key verified findings**
- All 20 rendered videos run 74.8–111.2 s, while the target is 35–55 s and the hard limit is under 60 s. The cause is that the 60–90 s target is written into the storytelling skill, the scriptwriter agent and §9, and QA only rejects over 180 s.
- Frame 0 is a blank board.
- Publish approval is not tied to platform, time or file hash. Instagram approval overwrote the YouTube record for C0001/C0002, and publishing never checks the QA verdict.
- Z-Image Turbo ignores negative prompts, and character consistency is text only.
- Analytics have no data yet; the API is not enabled.

**Owner approved all research documents (2026-11-16).** The owner added a disk cleanup step, now **implemented** as `python -m pipeline cleanup`; see the policy in `docs/PRODUCTION_ROADMAP.md` §7b.
- **Default is a preview.** `--models` / `--tools` widen the scope, `--apply` deletes, and every deletion is logged in `data/cleanup_log.jsonl` with its restore command.
- **Produce guard:** `produce` warns below 20 GB free and auto-removes only the safe tier below 10 GB.
- **Measured 2026-11-16:** 86.9 GB free; 45.0 GB reclaimable, mostly the 32.8 GB of full Z-Image weights, which are unused because the local 4-bit model renders with the HF cache hidden.

**Decisions pending (owner)**
- Decided 2026-11-16 ("do all the improvements except mobile"): 35–55 s target (O1), YouTube `synthetic: true` (O2), OFL fonts (O3), approval-record redesign (O4), frame 0 ≥70% drawn (O5), CLAUDE.md voice line → Maya2 Malini (O8), gu/te `unreviewed-language` cohort (O9), agents 10 → 5 + 1 dormant (O10).
- Out of scope for now: Telegram bot and Remote Control (O6), dashboard licence route (O7).

### Implementation status (2026-11-16 evening)
- **Wave 1 and Wave 2 done:** commits 0496b0e, dd9cc60, de71b37. Phase C (mobile) is deferred by the owner.
- **Owner decisions (in chat):**
  - Keep the macOS fonts; OFL only with `"fonts": "ofl"`.
  - Parallax approved: `depth: auto` by default on engine v2 (figure mask where usable, otherwise depth layers), plus breathing.
  - New opening / engine v2 approved; new episodes get `engine_version: 2`.
  - Approvals happen in chat only, in three steps (script → videos opened in Finder → schedule for YT+IG). The owner removed the terminal approval hook. Claude records approvals with `STUDIO_OWNER_APPROVED=<ID> … --channel chat --note '<owner quote>' --yes` (allowed in `.claude/settings.local.json`), and only after the owner approves in chat.
- **Instagram catch-up schedule:** one episode per day at TE 19:00, GU 19:30, HI 20:00, EN 20:30. Ep02 is all today (te/gu moved to 21:00 / 21:30); Ep03 17 Nov, Ep04 18 Nov, Ep05 19 Nov.
- **Wave 3 next (Phase E tests, one heavy model at a time):** FLUX.2 klein reference conditioning (A9), Z-Image ControlNet (E5), ACE-Step / Magenta music beds (E4), Indian painting style stills (E2), chalk LoRA pilot (E1), LTX-2.3 hero shot (E3), commercial aligner (E9), Manim (E10). E6–E8 wait for their data triggers.
- **Owner optional:** `instagram_manage_insights` permission + a new token, for Reel stats.

## Progress log
| Date | Work | Decisions |
|---|---|---|
| 2026-11-15 | Pilot C0002 stages 1–4 (research, audience, strategy, hooks + scripts EN/HI) → stopped at G1 | Topic B chosen with evidence; Hindi written originally; Rama shown from behind; Brahma symbolic rule kept |
| 2026-11-15 | Built foundation (§19) | Keep existing engines; add a thin `pipeline/` layer + SQLite; agents for judgement, Python for deterministic steps; no third-party skills installed; macOS voices excluded (licence); slot experiments instead of fixed posting times |
