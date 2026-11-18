# PROJECT_CONTEXT — shorts-studio

> **Before making any changes, read this entire document, inspect the current project state, verify completed work, identify the last completed workflow stage, and resume from the exact next pending task. Do not repeat completed work or overwrite existing decisions without a documented reason.**
>
> Quick orientation: `python -m pipeline status` shows every content item and its next action. §22 Current status and §23 Next steps are the source of truth for where work stopped.

---

## 1. Vision & objectives
A zero-cost, local-first, multi-agent content studio that discovers opportunities, understands Indian language audiences, writes strong stories, produces 9:16 animated videos with natural narration, publishes on schedule (YouTube first), measures real performance and feeds learnings back into the next production.
- **Owner:** a single creator on a MacBook Air (Apple M5, 16 GB RAM).
- **Channel:** YouTube "Knowledge PowerBank" (rename to **Chalk Tales** pending, §27) + Instagram @aks.chalk.tales.
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
- **Status 2026-11-16 21:40 IST:**
  - **Uploads:**
    - **YouTube:** Ep01–04 EN/HI and Ep05 TE/GU are live or scheduled. `publish-queue` holds 15 approved uploads under the 6/24 h cap: Ep01 GU/TE (now), Ep02–04 GU/TE, Ep05 HI/EN, and Ep06 in all 5 languages. The queue runs in the owner's terminal under caffeinate.
    - **Instagram:** Ep01 is live in 4 languages. Ep02 HI/EN failed at 20:00 and 20:30 with OAuthException 200, subcode 5258005, "API access blocked". The remaining launchd jobs (Ep02 TE/GU, Ep03–05) will fail the same way until the owner fixes access in Meta. After that, new times need a new Instagram G3.
  - **C0006 (Episode 06, The Divine Weapons, Bala Kanda 1.27–1.28; teaser 1.29.23):**
    - **Languages:** en, hi, gu, te and **mr** (new). This is the first episode in the 35–55 s format: en 53.5 s, hi 56.0 s, gu 55.3 s, te 54.1 s, mr 56.3 s.
    - **Gates:** G1 (re-approved 4×, after image prompt and hook fixes), G2 (with waivers) and YouTube G3 for 2026-11-20 (TE 18:30, MR 19:00, GU 19:30, HI 20:30, EN 21:30) are recorded. The YouTube uploads are queued. Instagram G3 is pending until access is fixed.
    - **Fixes made:**
      - The EN hook was changed to "…bowed before him" because Kokoro is deterministic and the old wording failed speaker_consistency (0.66).
      - HI scenes 5 and 9 were regenerated for speaker and pitch.
      - Images 03, 08, 02, 06 and 10 were redone. Scene 7 kept take 1 because take 2 was photorealistic. Image 02 was shifted down 96 px so the title zone is clear.
  - **Marathi:**
    - **Voice:** `maya2:Malini`, approved by the owner on 2026-11-16 (`content/C0006/voicepack/SUMMARY.md`; reference `profiles/voices/mr_Malini_ref.npy`). mr is `unreviewed-language`.
    - **Open issues:**
      - Whisper repeatedly hears म्हणाले/झ/ळ as Hindi-like forms. The owner waived this; a native listen is still needed.
      - The mr lint rate is uncalibrated (estimate 44.5 s vs 56.3 s rendered), so run `pipeline lint --calibrate` before the next mr script.
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

- **Monitoring Phases 2–3 (2026-11-16, details in `docs/MOBILE_CONTROL_ARCHITECTURE.md` "Phases 2 and 3 implemented"):**
  - **What runs:** the private Telegram bot `@Chalkstudiobot` (`pipeline/bot.py`, `pipeline/notify.py`) and the read-only mobile dashboard (`pipeline/dashboard.py`, `127.0.0.1:8765` behind a cloudflared quick tunnel). They run as launchd `com.shortsstudio.bot`, `com.shortsstudio.dashboard` (web server) and `com.shortsstudio.tunnel` (cloudflared, separate so `python -m pipeline service restart dashboard` keeps the address); manage them with `python -m pipeline service install|restart|remove|status` (the queue is left alone unless you pass `queue --restart`).
  - **Secrets:** `secrets/telegram.json` and `secrets/dashboard.json` (mode 600).
  - **Dashboard address:** the current address is in `data/dashboard_url.json`, and a new sign-in link is sent to Telegram whenever it changes (`/link` re-sends it).
  - **Approvals** stay in chat; the bot and dashboard can only acknowledge issues.

- **C0011 · Bala Kanda Part 1, first YouTube long-form video (2026-11-18):**
  - Scripts en/hi/te: G1 approved by the owner in chat and recorded by the owner.
  - 41 wide 16:9 drawings, shared by all three languages.
  - 31 rigged scenes (13 character puppets, 18 objects), all passing rig QA.
  - Voices: hi needed 6 scenes and te 1 scene re-recorded for speaker consistency.
  - Rendered: en 9:21, hi 10:01, te 9:30, all at −14.0 LUFS, 1920×1080.
  - QA: Story and Final 100 in all three.
    - Visual warnings in all three: near_duplicates, because verse slides look alike, and safe_zones, calibrated on vertical Shorts.
    - Telugu also has the expected warn-only narration_asr and speech_rate.
  - **G2:** approved by the owner in chat, with waivers recorded (2026-11-18 23:20).
  - **G3 (YouTube):** approved for Thu 2026-11-19, te 11:00, hi 11:30, en 12:00 IST.
  - **Queue:** `/publish` added the three videos at the front of the publish-queue. The daily cap frees at about 10:21; the videos upload as private with `publishAt`.
  - **Packaging:**
    - Thumbnails 1280×720 (`pipeline/longform.py`): "Too young to fight?" per language, on scene 3.
    - Chapters come from timeline.json.
    - Titles are 42–49 chars; the en title lint scores 98.
    - Promo lines applied.
    - The "Full Kandas" playlists don't exist yet, so the uploader skips them; the owner hasn't asked for them.
  - **Owner, after going live:** pin the comment and add end screens in Studio.
  - **Fixes made during production:**
    - Images refused a silent placeholder fallback; mflux now runs from .venv.
    - `step_extras` skips a missing thumbnail spec.
    - Render now shares the primary-language images first.
    - Rig QA gained a `--scenes` filter, and rigs merge per-scene files from `content/<ID>/rig_parts/`.
- **Animation (2026-11-18):** chalk puppets (engine v3) are active for Ep10 onwards: `puppetstudio.py`, `pipeline rig-qa`, `content/<ID>/rig.json`. The AK01 puppet episode is approved and on hold until the Ayodhya Kanda chapter (§23.0).
- **Dashboard phone app (2026-11-18, owner chose option A):**
  - **Why:** the quick tunnel's address changes whenever the Mac sleeps or the network drops, so the home-screen web app kept breaking.
  - **Fix:** after each change, the tunnel writes the current address to a secret GitHub gist (`pipeline/linkgist.py`; token `secrets/github_gist.json`, gist scope only; state `data/dashboard_gist.json`). It retries every 5 min until the sync succeeds. The Telegram link message is sent only if the gist sync fails.
  - **App:** Flutter, `mobile/chalk_dashboard`. A WebView of the dashboard. It reads the gist on launch and on any failure, checks `/healthz`, and signs in through `/login?k=` once per address. It shows "Mac offline, retrying" with backoff (15/30/60/90 s), which stays under GitHub's limit of 60 unauthenticated requests per hour.
  - **Setup:** the bot's `/app` command sends a one-time setup code: base64 of `{gist id, login key}`.
  - **Build:** signed release APK at `data/mobile/ChalkDashboard.apk`. Keystore and passwords are in `secrets/android/`; keep them, because app updates must be signed with the same key. Rebuild with `flutter build apk --release` in `mobile/chalk_dashboard`.
  - **Live since 2026-11-18 12:02.** The token is gist-only; the first, over-scoped token was revoked. v1.0.1 is installed on the owner's phone over wireless adb, and it trusts only `https://*.trycloudflare.com` addresses from the gist, so a tampered gist cannot capture the login key.
  - **Owner advice:** turn off wireless debugging. To reinstall: `adb install -r data/mobile/ChalkDashboard.apk`, or copy the APK to the phone.
- **Brand (2026-11-17):** Chalk Tales package built locally (§27); new episodes run `pipeline promo <ID> --apply` before G3.

## 23. Exact next steps
0. **Standing decisions (owner, 2026-11-18):**
   - **YouTube long-form strategy (owner, 2026-11-18, after the analytics review).** YouTube Shorts barely reached anyone (about 175 views for Ep01–03; only Ep01 Hindi entered the Shorts feed), while the same Reels drew about 14,000 views on Instagram (`data/reports/insights-2026-11-18.md`).
     - **Format:** **2 long videos per Kanda** on YouTube, each a **new continuous story** (one flowing narration, no per-episode hooks or end cards), **8–12 minutes**, **horizontal 16:9**, in **English, Hindi and Telugu**. Each uses the chalk-puppet engine with new wide drawings.
     - **Bala Kanda:** Part 1 runs from Valmiki to the divine weapons (Ep01–06 ground). Part 2 runs from the road to Mithila to Rama and Sita's wedding and Parashurama.
     - **Shorts:** unchanged on both platforms (all languages, daily, 35–55 s).
     - **Gates and duration:** the same three gates apply to each long video. The 35–55 s duration rule is for Shorts only; long videos target 8–12 min.
     - **Engine (built and tested 2026-11-18).**
       - `pipeline new … --format long` writes `format: "long"` in the manifest. `produce` and `rig-qa` then run the engine with `STUDIO_FORMAT=long`, and `frame.py` switches every size: 1920×1080 frame, 2112×1188 canvas, 1344×768 images, a wide-composition prompt suffix and captions at 0.88.
       - Lint and QA read the manifest format. Long videos target 480–720 s, warn above that, fail an estimate above 780 s, and reject renders at 900 s or longer at 1920×1080.
       - Verse and word cards are re-laid out for the wide frame.
       - Shorts (no format, or `short`) are byte-for-byte unchanged.
       - Still to do when the first long video reaches G3: the YouTube upload as a regular video (not a Short) with a 1280×720 thumbnail and chapters in the description.
   - **Animation from Episode 10 onwards** is the chalk-puppet engine v3 (§30). `pipeline new` defaults to `engine_version: 3`.
   - **Per-episode flow:** after images, write `content/<ID>/rig.json`, then run `python -m pipeline rig-qa <ID> --lang <primary>` until every scene passes, then render. The creative-director composes drawings for puppetry.
   - **Unchanged:** Ep01–09 stay on engine v2.
   - **AK01 (Ayodhya Kanda sample, approved) is on hold.** Schedule or publish it only when the series reaches the Ayodhya Kanda chapter, and raise it with the owner at that point.
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

## 27. Brand: Chalk Tales and cross-promotion (2026-11-17)
- **Owner decision:** one brand name, **Chalk Tales**, on Instagram (@aks.chalk.tales, live) and YouTube (renamed by the owner on 2026-11-18 from Knowledge PowerBank to **Chalk Tales**, handle **@aks.chalktales**; @aks.chalk.tales was taken; `brand.youtube.active_url` switched). Everything was built locally; no live account, published or scheduled item was changed.
- **Config:** `profiles/brand.json` (name, positioning, colours slate #14191C / chalk #F2EFE6 / gold #E8BE6E, fonts, IG handle/url, YouTube current/planned with one `active_url` that stays on the current channel until the rename is confirmed, collab email, per-language CTA lines en/hi/gu/te/mr with gu/te/mr "needs native review"; `projects.<slug>.overrides` for other series).
- **Promo:** `python -m pipeline promo <ID> [--lang] [--platform] [--dry-run|--apply] [--force-reapproval-needed]` (`pipeline/promo.py`) inserts the Instagram follow + collab lines into the YouTube description, the IG handle into `pinned_comment`, and one "watch on YouTube, link in profile" line above the Instagram hashtags; idempotent; enforces IG 2,200 chars / ≤5 hashtags and YT 5,000 chars; refuses G3-approved sections (G3 hashes each platform section) and anything already uploaded. Runs **before G3** (content-pipeline step 11b, packager notes). `publish.py` warns (never blocks) when the line is missing. `promo --audit` → `data/reports/promo-audit-<date>.md`.
- **Audit 2026-11-17:** all 60 platform sections of C0001–C0007 lack promo and all are G3-approved, scheduled, queued or live, so nothing was applied; proposed text is in the audit for manual Studio/app edits if the owner wants them. C0008 has no publish.json yet and will get promo before its G3.
- **Assets:** `python -m pipeline.brandart` → `data/brand/` (YouTube banner + crop-guide preview, bow-and-arrow profile picture, `mark_preview.png` old vs new at 1080/110/40 px, 4 highlight covers, `brand_review.png`). The mark was redesigned the same day: a 45° recurve bow at full draw with the arrow pointing upper-right, because the old arc-plus-vertical-arrow read as an umbrella. The old `instagram_profile_bow.png` is kept unchanged.
- **Docs:** `docs/BRAND.md` (positioning, voice, names, colours, logo use, IG name/bio, YouTube description and playlists, cross-promotion rules, owner checklist for the live accounts); `docs/MEDIA_KIT.md` template filled by `python -m pipeline mediakit` from real analytics only ("not yet available" otherwise).
- **Owner to do:** apply the checklist in `docs/BRAND.md`; confirm the YouTube rename so `brand.youtube.active_url` can be switched; unlist or privatise the unrelated July 2025 videos (`brand.youtube.external_channel_items`, shown in every audit); the channel description now says "chalkboard-style animation", not "hand-drawn"; native review of gu/te/mr CTA lines.

## 28. Ayodhya Kanda animated sample AK01 (2026-11-17) — awaiting owner review, nothing integrated
- **What:** first real-animation sample of AK01 "Rama's Crown Was Ready" in the owner-approved anime-film look (benchmark `data/anim_lab/keyframes/king.png`), Hindi (maya2:Malini) + English (Kokoro af_heart). Lab only: `data/anim_lab/` (gitignored); no pipeline code, approved content or schedule touched; nothing published.
- **Consistency system (locked):** FLUX.2 klein 4B q8 (Apache-2.0) reference edits from per-character front anchors + location plates; registry with sha256/prompts/seeds in `profiles/characters/ayodhya_kanda.json` → `locked_refs` (Dasharatha, Rama, Sita, Manthara, 5 locations, 11 AK01 keyframes). Reuse these files for every later Ayodhya episode; never regenerate.
- **Done (20:40):** finals `data/anim_lab/AK01/AK01-hi.mp4` (52.8 s) and `AK01-en.mp4` (48.0 s), all 11 shots real LTX-2.3 animation, −13.9 LUFS, speaker_consistency pass; 540p proxies + contact sheets beside them. Awaiting owner review (the style change itself is still an owner decision). Open: cinematic character sheets beyond the fronts. Details: `data/anim_lab/AK01/STATE.md`, `docs/ANIMATION_RESEARCH.md` §7.

## 29. Continuity editing layer (2026-11-17) — prototype, awaiting owner A/B review
- **Why:** the owner said AK01 "feels like multiple independent video clips simply stitched together". Measured causes (`research_notes/Continuity editing/ak01_boundary_analysis.md`, numbers in `data/anim_lab/AK01/analysis/boundaries.json`): every cut sat 0.12 s before a narration line, with picture, caption, title, ambience and motif all changing on one frame; clips played whole from frame 0, retimed 0.77–1.19× with frame blending and frozen under dissolves; 12 vs 24 fps cadence flips; camera moves that stop or reverse at cuts; time of day jumping (night → day → night at shots 7–9).
- **Research:** `research_notes/Continuity editing/editing_craft.md` (craft rules, decision table, limits: ≤3 soft transitions and ≤1 dip per Short, no whip pans in Ayodhya), `tools.md` (free, commercial-OK tools with timings on this Mac). Verdicts: keep numpy + PIL + ffmpeg as the compositor; OpenCV DIS optical flow for motion, interpolation and cadence repair; DaVinci Resolve rejected for automation (Python scripting is Studio-only from 21.1); RIFE (MIT) only for in-shot speed ramps, later; FILM (archived) and DINOv3 (custom licence) avoided; MLT/Shotcut optional later for an editable timeline.
- **Engine:** `pipeline/continuity.py` (generic, not yet wired into `produce`). Steps: `measure` (per-frame pan/zoom/local motion, luminance and Lab colour, cadence; cached per clip) → `window` (usable in/out: drops flicker, pops and light changes with no camera move, such as self-fades and pulses, with a 4-frame guard) → `decide` (one transition per boundary from the story beat in the edit spec: turn → held indigo dip, time_jump → 1 s dissolve on live frames, simile → cut with 0.7 s sound lead, parallel → J-cut sound bridge, reveal → L-cut, same_scene/new_place → cut; plus automatic flags for jump cuts, screen-side flips, camera reversals, cadence mismatch; then enforces the limits) → `allocate` (dynamic programme that moves each cut −0.75…+0.75 s off the line start so every shot fits its clean footage) → `retime` (rate 1.0 window chosen so both ends are in motion and outgoing pushes are not cut at peak acceleration; otherwise motion-aware stretch that slows only still frames (down to 0.4×) and moving frames at most to 0.9×, with optical-flow interpolation, never frame-blend ghosting) → `camera` (light digital push on static shots, ≤4%, and zoom carry across cuts, total ≤6% crop) → `grade` (per-shot Lab match toward its time-of-day group: night/dusk caps, vignette) → `repair_cadence` (on-twos clips rebuilt to 24 fps by interpolating the duplicate frames) → `report` (Markdown table of every decision with its reason and flags). Output 24 fps so rate-1.0 shots map frame for frame.
- **AK01 Version B:** `data/anim_lab/AK01/scripts/assemble.py --cut b en hi` (edit spec `EDIT_SHOTS` / `EDIT_BEATS`; Version A path unchanged) → `data/anim_lab/AK01/AK01-{en,hi}-B.mp4` (+ 540p, `-B.timeline.json`); per-language plans `analysis/edit_plan_{en,hi}.{md,json}`; cut sheets `analysis/contacts/{B}-{en,hi}-cuts.png`. Audio rebuilt with J/L beds keyed to picture cuts (hall birds under shot 1, roar and thunder 0.7 s before the peacocks, heartbeat entering under the embrace, fire under the dissolve, nagada 1 s under the shrine and 1 s into Manthara, wind and music carried into the end card); titles 0.6 s after their cut, verse 0.9 s after; "Next" shown only on the end card; chalk-line bloom at the open and a chalk drain into the end card. Results: en 48.0 s, hi 52.75 s, −13.9 LUFS, TP −1.6/−2.0 dB, 1080×1920 at 24 fps; render 106 s (en) and 117 s (hi) on the M5 under `heavy.lock`. `clips/` and the Version A finals are byte-identical before and after (md5 checked).
- **Editing cannot fix (regeneration flagged, owner's call):** s08 is daylight in a night scene (grade softens it only); s03 is a jump cut from s02 (same king, parasol and axis; needs a low angle or a cutaway); s06 fades itself to dark from frame 60 (only 2.5 s clean, so the Turn dip sits partly over the end of line 6); s05 has light pulses (frames 31–73 clean); s10/s11 read as afternoon against "lamps for the night"; Rama changes screen side at 5→6 and 8→9.
- **Superseded direction (2026-11-17, later):** the owner discarded the anime/painterly/cinematic look for Ayodhya Kanda (see §30). The continuity rules above still apply to the new chalk-puppet direction.
- **Workflow for future episodes (all Kandas, languages, genres):** (1) at G1 the creative-director adds per-shot `time`, `place`, `subject`, `size`, `intent`, `screen` and per-boundary `beat` to the shot list; (2) before rendering, run the planner on an animatic (keyframes plus voice) to lock cut points, and render 121–145 frames so every shot has handles; write motion direction and end pose into the prompts; (3) after rendering, `measure` + `window` the clips, and regenerate any shot the report flags before assembly; (4) assemble with `continuity.plan`, then review the cut sheet; store the plan with the timeline for G2. Integration into `produce` waits for the owner's A/B verdict and the Ayodhya style approval.

## 30. Chalk-puppet animation (Kathputli style) (2026-11-17) — prototype, awaiting owner review
- **Direction (owner, 2026-11-17):** drop Pahari Gold, anime, painterly and cinematic 2.5D. Return to the original chalkboard illustrations and bring them alive with subtle, deliberate string-puppet movement: only what the line needs moves, everything else stays still, and the chalk grain, strokes, board and character designs stay exactly the drawing's own. The §28 LTX/FLUX anime sample and its locked refs are no longer the Ayodhya look.
- **Research:** `research_notes/Chalk puppet animation/tools.md`. Verdict: deterministic 2D cut-out puppetry in our own numpy/OpenCV compositor beats AI video for this style (AI video smooths chalk grain and flickers texture). Usable: OpenCV, numpy, scipy (already installed); libigl (MPL-2.0) and SAM 2.1 (Apache-2.0) as optional later helpers; MI-GAN (MIT) or LaMa (Apache-2.0) as optional better fills. Avoid: Triangle/meshpy (non-free commercial), LivePortrait's InsightFace (non-commercial), bizarre-pose (AGPL), DrawingSpinUp (no licence, CUDA). Excluded as paid: Spine, Moho, Live2D PRO, Rive export. Blender headless only as a fallback for a real perspective turn. MediaPipe found a pose on only 1 of 3 chalk figures, so joint placement needs a person to confirm.
- **Engine:** `puppet.py` (root, beside `chalk.py`; not wired into `produce`). `Puppet`: bones with parents (forward kinematics), each bone owns a traced part; each part is a rigid chalk cut-out moved with one affine (cubic resampling keeps grain), drawn in z-order, with a shared joint disc at each pivot so elbows and necks stay covered; part opacity follows the chalk ink so dark board around a part never blocks what is behind it. Actions are `{bone, deg, at, dur}` (or root `dx` with `hop`/`steps` for puppet steps), eased with a string-style overshoot and settle; idle sway and breath around the string point. `Elements`: displacement fields for flags (wave from the pole), hanging cloth (pivot top), trees (pivot bottom), rigid swings (whisks, lamps), flames (flicker + optional ignite time), drifting clouds; chalk-stroke birds. `Stage`: background plate with only the moved pixels filled (`fill_holes`, Telea + chalk grain), elements, puppets, then a 3-frame chalk "boil". Falling petals reuse `chalk.Overlays`. Board, chalk conversion (`chalk.chalk_from_image`, palette `ayodhya`), camera and captions reuse `chalk`/`studio`. No new dependencies.
- **Prototype:** `data/anim_lab/AK01_puppet/` (lab, gitignored): illustrations `illus/` (Z-Image Turbo, series chalk prefix, bible prompt for Dasharatha; 3 seeds each, picks 7202/7202/7303), rigs `rigs/proto.json` (parts, joints, actions keyed to narration lines and fractions, elements), scripts `scripts/{gen,proto}.py`. Output `AK01-puppet-proto-{en,hi}.mp4` (20.8 s / 22.4 s, 1080×1920 at 30 fps, −13.7/−13.8 LUFS): (1) Dasharatha on the throne lowers his raised hand and droops his head on "longed to rest", then lifts both on "proposed Rama"; chamara whisk, banners and hanging lamps move; (2) terrace: Rama steps in, the king leans and reaches to his shoulder on "embraced", both look up on "Pushya"; flags, tree, cloth ends and birds move; (3) city at dusk: flags flutter, clouds drift, petals fall from "flowers", lamps light far to near on "lamps for the night". Render about 2.5 s per output second on the M5, no heavy model at render time.
- **v2 after owner review (2026-11-17):** owner: "pillars moving", Rama's "waist doesn't fit his lower body", "movements aren't logically correct". Fixes, now rules for every puppet shot:
  - **Cut-outs only.** Environmental objects (banners, whisks, lamps, flags, trees, flames) are rigid cut-outs too, never a bent region. Character pixels are subtracted from every object cut-out.
  - **Figure masks.** Character parts are intersected with the BiRefNet figure mask (dilated 9 px), so railings, pillars and buildings behind a figure never move.
  - **Whole figures.** Every figure is one connected puppet (legs → torso → head and arms) with shared joint discs. Standing figures keep their feet planted; sway and breath act only above the waist. Seated figures breathe only in the torso.
  - **Logical movement.** Gestures continue the drawn pose: the weary hand sinks, the proclaiming hand rises higher, the father's hand comes to rest on the son's chest, the son bows from the waist. Shoulders rotate at most about 30°.
  - **Locked stage.** No handheld jitter in puppet shots; only a slow push.
  - **Motion-map QA.** Before showing a shot, render it with a motion map (every pixel that changed is marked red) and confirm only the intended things move.
  - **Removed.** Cloud drift (rectangular strips) and garland sway were dropped. Outputs: `AK01-puppet-proto-v2-{en,hi}.mp4`.
- **v3 after second owner review (2026-11-17):** owner: Dasharatha's "shoulder gets completely cut off"; wants "a lot of movements" that are "possible as in real life", with no "arm breaking". Changes:
  - **Mesh skinning.** Rigid cut-outs were replaced by a deformable mesh per figure (scipy Delaunay, 8 px spacing). Skinning weights come from the traced part labels, blended smoothly across each joint (shoulder about 0.035 × width, elbow about 0.022). Rendering is forward triangle rasterisation with one cubic remap, so shoulders, elbows, necks and waists bend like skin and cloth instead of separating. There is no fold-over ghosting and no new dependency.
  - **Follow-through.** `follow` bones lag a parent (scarf, hanging arm, cloth).
  - **Revealed gaps** are filled dimmed, so they read as shadow.
  - **Draw the story pose; animate around it.** A single flat drawing cannot show a large reach: the hidden inner arm folds. So each illustration is generated in the narration's key pose (for example the father's arm already around Rama), and the motion stays anatomically small and rich: breathing, head turns and nods, a lean, a pat, a bow, looking up, cloth swing, plus environmental motion.
  - **Joint caps.** About 25° at elbows, 20° at shoulders, and no lifting of a hand that rests on something (the hidden surface beneath would show).
  - **Outputs:** `AK01-puppet-proto-v3-{en,hi}.mp4`. The terrace now uses the embrace drawing `illus/p2b_embrace_7603.png`, and the king's resting hand is rigged to Rama's shoulder, so it moves with Rama.
- **v4 after third owner review (2026-11-17):** owner: the whisk feathers moved but its handle stayed still, plus "multiple issues"; "figure out an automated checklist, and verify the issues and fix them before delivering". Changes:
  - **Automated motion QA, `pipeline/puppetqa.py`.** Run with `proto.py --qa`. Rendering refuses unless every shot passes; `--force` overrides. Each shot writes a report plus a crop sheet (rest vs peak, or original vs frozen rest) to `work/qa/<shot>.{json,png}`. Checks:
    - `rest_fidelity`: with all motion frozen, the frame must reproduce the drawing.
    - `torn_stroke`: a still stroke cut from a moving one. Inside characters the figure mask decides; for objects the test is the same colour on both sides of the cut and the stroke crossing it.
    - `split_surface`: one surface torn between two characters.
    - `orphan_fragment`: a small piece of a moving object left behind.
    - `lost_ink`: a moving object loses or gains drawing.
    - `fold`: crushed or flipped mesh triangles inside visible area.
    - `exposed_patch`: an uncovered fill that changes the image, in scenes without a plate.
    - `background_seam`: an uncovered area does not continue its surroundings.
    - `joint_limit`: a per-bone `limit` in the rig, defaults by joint type.
    - `pop`: a jump of more than 9 px between frames.
    - `contact_drift`: resting hands and planted feet must stay put.
    - `double_owner`: one drawn pixel owned by two moving objects.
  - **Waivers.** A flag I verified on the sheet as invisible or as correct occlusion becomes a `qa_waive` entry in the rig with the check, box and written reason; it is reported, not hidden.
  - **Engine rules learned from the flags.**
    - Every moving object is completed underneath whatever is in front of it. A body part is extended in a narrow band (about as wide as the motion) under overlapping parts of its own and of other characters. A cloth or object behind another object is completed from a clean background plate, colour-matched to that object.
    - Semi-transparent overlaps, such as feather strands over a banner, are alpha-matted against the actual composite behind them, so the rest frame is exact.
    - Clean background plates come from FLUX.2 klein reference editing (`plates/`): the same drawing without the moving figures and objects. A plate is used only for large reveals whose surroundings match; otherwise the local background is continued. Wherever nothing covers a pixel at rest, the background is always the original.
    - Ownership is exclusive. The front character claims only pixels it actually draws; character coverage stays inside its own traced outline, and traced outlines are authoritative over the figure mask.
    - Objects are colour cut-outs: flags, banners and flames keep only their saturated pieces, with their chalk edge, and never take spires, pillars or clouds.
    - The whisk rotates together with the attendant's forearm about the elbow, so the hand holding it moves.
    - Each body part is its own mesh. Parts blend only at a real joint, and only within the limb's width (`blend` and `width` per bone). Parts that merely touch, such as a hand on a dhoti or a scarf beside the body, move independently.
    - Resting limbs are `pin`ned, so the hand stays and the shoulder flexes.
    - Large rotations of arms drawn against the body are forbidden: shoulder about 6°, with gestures led by the elbow.
    - Scenes crossfade directly into each other; no blank board.
  - **Outputs:** `AK01-puppet-proto-v4-{en,hi}.mp4` (20.0 s / 21.7 s, −13.7 LUFS). All three shots pass QA, each with its recorded waivers.
- **v5 after fourth owner review (2026-11-18):** owner: Dasharatha's "upper arm still breaks" on the throne, and "the background waving flag also moves along with Dasharatha's body" in the embrace. Both had passed v4 QA, so each became a new check before it was fixed:
  - **`body_gap`.** An area of a character's body is uncovered with nothing behind it (counted where two traced parts overlap, or under another character).
    - Cause: the raised forearm uncovered about 40 px of sleeve; completion was a fixed 10 px band, and meshes only covered visible pixels.
    - Fix: each part's mesh covers its visible plus completed area, and the completion band adapts to the actual motion of the parts in front (`max_motion`, up to 70 px). Completion uses a drawn underlay when one exists (`underlay`: FLUX.2 klein edit of the character with the front part removed, for example `plates/p1_king_underlay.png`); otherwise it is inpainted from the part's own chalk and re-grained. Completion happens only under opaque front pixels.
    - Movement rule learned: a forearm drawn in front of the shoulder may not swing outward, because the hidden shoulder edge has no reliable drawing. The weary hand drifts inward and returns exactly to its drawn pose; the proclamation is carried by head lift, chest and nod.
  - **`line_captured`.** A straight scenery line (pole, rail) belongs to a moving character.
    - Cause: the small flag's white pole ran behind the king's hair inside his traced outline.
    - Fix: `scenery_lines` (Hough) are removed from character cut-outs whenever most of the line lies outside the figure mask. Near-vertical lines are extended through the character so pole pixels between hair strands stay still, and removed scenery always keeps the original pixels.
  - **`object_captured`.** A character's cut-out contains a coloured object's pixels (flags, banners, flames are claimed first).
  - **Physics rules added.** Cloth hanging from a shoulder (Rama's scarf) is `pin`ned: it blends with the shoulder at the top, and its hem stays put under gravity instead of swinging with the waist. Element holes cover only the ink they draw, so no blots appear around the tree.
  - **Gate.** All three shots pass; verified waivers are recorded per shot.
  - **Outputs:** `AK01-puppet-proto-v5-{en,hi}.mp4`.
- **Owner approval and pivot system (2026-11-18):** the owner approved v5 ("approved") and asked for pivots on characters and objects, so parts can only move logically. Changes:
  - **Templates, `profiles/rigs.json`.**
    - `human_standing` and `human_seated` skeletons with named pivots: seat or ankle_mid, waist, neck, head_top, shoulder/elbow/wrist/hand on both sides, and hip/knee/ankle/toe on both sides.
    - Each bone has an anatomical limit (degrees from the drawn pose), a blend width and contact rules: seated legs and standing hips stay put.
    - Object pivot templates: flag (pole), banner (top edge), hanging lamp (chain point), tree (trunk base), flame (wick), wheel (axle, `spin`), door (hinge), handheld prop (follows a hand bone, `attach`, with optional swing about the grip), hanging cloth (pinned at the hem).
    - Rules: only hips and torso may shift, at most 6 px; a joint may separate at most 2.5 px.
  - **Rigs declare pivots only.** A rig gives `template` plus `joints` (pivot positions); `puppet.resolve` builds bones, hierarchy and limits. Custom bones are still allowed (joined palms, a hand resting on another character, a scarf).
  - **New QA checks.**
    - `joint_gap`: a part pulls off its pivot.
    - `unpivoted_motion`: a part slides instead of turning, or shifts too far.
    - `object_without_pivot`: a moving object has no declared pivot.
    - Per-template joint limits.
    - Every shot also gets a pivot sheet, `work/qa/<shot>_rig.png`, with joints, bones, pinned joints (red) and object pivots (cyan).
  - **First run.** The checks caught v5's head sliding on the neck and the chest sliding off the waist; heads and chests now only turn about their pivots. All three prototype rigs migrated to the templates.
  - **Outputs:** `AK01-puppet-proto-v6-{en,hi}.mp4`. All shots pass.
- **Limits:** 2D only (a head can tilt, nod and shift but not truly turn from profile to front); large limb moves reveal a filled background, so actions stay small; rig fitting is manual today (about 10–15 min per illustration: trace parts, place joints); illustrations must be composed for puppetry (limbs clear of the body, side or three-quarter views). Rama's blue skin from the image model becomes a dusky dark tone through the series palette.
- **Plan for all 11 shots:** `research_notes/Chalk puppet animation/ak01_shot_plan.md`.
- **Full episode (2026-11-18, owner approved the v6 prototype and the pivot system):**
  - **Rig.** `rigs/ak01.json`, 10 illustrations for 11 lines; the throne covers lines 2–3.
  - **New drawings.** 7 new illustrations in `illus/`: s01_window, s04_peacocks, s05_rama, s07_dream, s08_urge, s09_fast, s11_manthara (seed 10303).
  - **QA.** Every shot passes `proto.py --rig=ak01 --qa`. Waivers are recorded per shot, each verified on its QA sheet.
  - **Engine and QA changes:**
    - `exposed_patch` skips reveals that are plain dark board, matching the board around them (`plain_board`).
    - Holes keep the original pixel where the drawing is board-dark and the rest cover is weak. This removes grey rings in dark gaps inside figures.
    - Swing gains `side` (one-directional swing).
    - `proto.py --only` now uses the same per-shot seed as the full render. Before this, a shot could pass alone and fail in the full run.
  - **Motion learned the hard way** (each item failed QA first):
    - A resting arm (elbow on an armrest, hand on a sill or parapet) is pinned, and then the torso may not lean, because the pinned limb tears from the moving chest. Weight and intent are carried by the head instead.
    - A head whose hair overlaps a pillar or rail cannot turn: the cut-out carries the pillar strip with it (Sita, s09).
    - A long tail lying over a railing stays still (peacock, s04).
    - A flame's halo is never cut: flames flicker in brightness and sway at most 1.5 px.
    - Hair and crown tips must sit inside the head part, and elbow tips inside the arm part.
  - **Cut on purpose** (each looked wrong at frame scale and is noted for the owner):
    - the chamara whisk swing on the throne: its arm turned about the hand, and moving the stick uncovered a grey patch on the pillar capital;
    - the s07 curtain stir;
    - the small peacock's head bobs (its neck shredded);
    - Rama's and Sita's head moves at the fire (pillar overlap);
    - torso leans in s01, s07 and s11.
  - **Outputs:** `AK01-puppet-{en,hi}.mp4` (en 52.2 s, hi 56.9 s, −13.9 LUFS). **Owner approved 2026-11-18** after the chalk draw-in, the shloka slide and the chalk sound at 0.12. Nothing is published or scheduled; publishing still needs metadata, a schedule and G3 through the manual `/publish` skill.
- **Owner review of the full episode (2026-11-18):** "video is good". The owner asked for two changes, both now in `proto.py`.
  - **Chalk drawing first, then the drawing comes alive.** Each shot is drawn in stroke by stroke with the series engine's `chalk.reveal_order`, chalk stick and dust: 2.0 s for the first shot (`draw_first`), 1.0 s for the others (`draw`). The chalk-scratch sound plays during each draw at `CHALK_SFX_SCALE = 0.12` × the approved `CHALK_SFX_GAIN`. The owner asked three times for it quieter: 0.6, then 0.3, then 0.12.
  - **Dedicated shloka slide, as in the series.** The rig shot `verse_card` (`card: "verse"`, `hold`) is drawn with `chalk.text_scene` in reading order. A preceding shot can end early with `cut_frac`: s08 cuts at 55 % of line 7, and the card carries the rest of the line plus `hold` (1.2 s) of verse-only time.
  - `chalk.text_scene` now vertically centres verses with fewer than four lines. Four-line verses render exactly as before.
  - **Open text question for the owner.** The card shows the script's half verse, श्व एव पुष्यो भविता / श्वोऽभिषेच्यस्तु मे सुतः (2.4.2). A search snippet from sanskritdocuments.org gives "श्वोऽभिषेच्येत मे सुतः" and the second half "रामो राजीवताम्राक्षो यौवराज्य इति प्रभुः". The page itself returned 403, so the full verse is unverified and not used.
- **Production integration (2026-11-18, owner: "from ep10 onwards I want videos to be generated like this"):**
  - **Engine v3.** `puppetstudio.py` renders inside `studio.step_render` whenever `engine_version >= 3`. It uses the series timings (`studio.scene_timings`), captions, titles, overlays and `chalk.plan` (draw windows and transitions).
  - **Each scene:** drawn with the chalk stick, then animated from its `rig.json` shot. Verse and shloka scenes are chalk cards with their verse-only time.
  - **Transitions:** `erase`, `black`, `crossfade` and `dip` work; others render as a cut.
  - **Chalk sound:** scaled by `chalk.PUPPET_CHALK_SFX_SCALE = 0.12` in `chalk.sound`.
  - **Gate:** `pipeline rig-qa <ID> --lang L` (also `python puppetstudio.py <content>/<lang>`) writes `<lang>/rigqa/` sheets plus a summary. Render runs the gate first and stops on failure; `STUDIO_RIG_FORCE=1` overrides, and only the owner may ask for that.
  - **Rig file:** rig coordinates refer to the cropped scene still, the same one the chalk layer uses. One shot per scene (`"scene": i`); actions use `"line": i` (scene index) with `frac`/`offset`.
- **Disk cleanup (2026-11-18, owner-approved):** about 61 GiB freed (34 → 95 GiB free). Removed:
  - the discarded video models (Wan2.2 q8, LTX-2.3 q4, FastWan) and their lab environments (`venv-ltx`, `ltx-2-mlx`, `mlx-video`);
  - Gemma 3 12B from the Hugging Face cache;
  - puppet prototypes v1–v5 (v6 kept);
  - the uv cache;
  - `pipeline cleanup --apply --yes`.

  FLUX.2 klein, BiRefNet, Maya2, Whisper and `models/` are kept.

## 31. YouTube long-form (2026-11-18): architecture and plan
- **Full design:** `docs/LONGFORM_ARCHITECTURE.md`. It covers:
  - vision, architecture diagram and components;
  - agent jobs, execution order with gates, story shape and word budgets;
  - wide visual design with rig tiers, sound, YouTube publishing and long-form analytics;
  - per-part timeline, build plan L1–L12, risks and owner actions.
- **Built and tested:** L1–L3 (format switch, format-aware lint and QA, wide cards).
- **Dashboard (2026-11-18):** long videos now have their own place in the dashboard.
  - New `/long` page, reached from Home and Progress: each Kanda's Part 1 and Part 2 against the plan in `profiles/longform.json`, with status, languages and length.
  - An "About this long video" card on the episode page: format and target, length per language (from the video or the script estimate), chapters, and the puppet scene counts from `rig.json`.
  - Results put long videos in their own section; long videos don't count toward the Shorts episode goal; labels read "Bala Kanda · Part 1".
  - A **Puppets** step for every engine-v3 video (Ep10 onward), done once `<lang>/rigqa/summary.json` passes.
  - Tests: `tests/test_dashboard_long.py`.
- **Next:**
  - L4, L5 and L12, then the Bala Kanda Part 1 scripts to G1.
  - Then L6–L9 (owner A/B for music, L7) before production.
  - L10 before the first long-form G3.

## Progress log
| Date | Work | Decisions |
|---|---|---|
| 2026-11-15 | Pilot C0002 stages 1–4 (research, audience, strategy, hooks + scripts EN/HI) → stopped at G1 | Topic B chosen with evidence; Hindi written originally; Rama shown from behind; Brahma symbolic rule kept |
| 2026-11-15 | Built foundation (§19) | Keep existing engines; add a thin `pipeline/` layer + SQLite; agents for judgement, Python for deterministic steps; no third-party skills installed; macOS voices excluded (licence); slot experiments instead of fixed posting times |
