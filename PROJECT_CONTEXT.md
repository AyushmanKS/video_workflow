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
  - `.claude/agents/`: 10 subagents.
  - `.claude/skills/`: storytelling and the content-pipeline runbook.
  - `profiles/`: languages, voices and characters.

## 3. Agents (`.claude/agents/*.md`)
| Agent | Role | Main outputs |
|---|---|---|
| trend-researcher | Evidence for opportunities: YouTube trending/competition, Wikipedia per-language interest, autocomplete, seasonal context | `content/<ID>/research/report.md` |
| audience-localizer | Per-language audience brief; maintains `profiles/languages/*.json` | `content/<ID>/audience.md` |
| content-strategist | 10-factor weighted scoring and slate selection | `content/<ID>/strategy.md` |
| scriptwriter | Hooks (≥6, rubric-scored) + narration + scene plan, written originally per language | `<lang>/hooks.json`, `<lang>/script.json`, `<lang>/script.md` |
| creative-director | Style preset, prompts, character bible, tool evaluation | `visual` fields, `profiles/characters/*.json` |
| (production) | Python pipeline, run by the main session | audio, images, renders |
| language-qa | ASR round-trip, best-of-N regeneration, grammar/register, native-listen gate; owns `profiles/voices.json` | `<lang>/voice_qa.md` |
| video-qa | Automated `pipeline qa` + manual frame/story review | `<lang>/qa.md` |
| publishing-manager | Metadata, slot recommendation, approved upload/schedule | `<lang>/publish.json`, `schedule.json` |
| performance-analyst | Analytics snapshots, per-video and like-for-like comparisons | `data/reports/performance-*.md` |
| optimization-strategist | Evidence-graded recommendations; never auto-changes approved style | `recommendations` table, `data/reports/recommendations.md` |

All agents share house rules: no fabricated data, cite evidence files or URLs, zero cost, and stop at the gates.

## 4. Execution order & gates
The full table is in `.claude/skills/content-pipeline/SKILL.md`. Summary: `new → research → (audience ∥) → strategy → script → G1 → voice → language QA → images → render → video QA → G2 → metadata → schedule → G3 → publish → analytics (24h/48h/7d/14d/30d) → optimize`.
- **Gates** are recorded with `python -m pipeline approve <ID> script|final|publish`.
- `produce` refuses to run without G1, and `publish` refuses without G2 and G3.
- **Parallelism:** research per topic, and per-language script/metadata, can run in parallel through subagents. Heavy models never run in parallel (see §8).

## 5. Claude Skills
| Skill | Location | Purpose |
|---|---|---|
| `storytelling` | `.claude/skills/storytelling/` | Principles, 7 genre templates, hook rubric, script JSON schema, review checklist |
| `content-pipeline` | `.claude/skills/content-pipeline/` | Runbook: stages, commands, agents, memory rules, recovery |
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
| Video | ffmpeg + VideoToolbox | LGPL/GPL | Render is about 1 min per 75–95 s video |
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
- **Memory (16 GB):** never run Qwen, Z-Image, Veena and Whisper-turbo at the same time. Run `ollama stop qwen3:8b` before images or voice. The fanless Air throttles on long runs, so keep it plugged in.
- **Disk:** 92 GB free at the time of writing. `~/.cache/huggingface/hub/models--Tongyi-MAI--Z-Image-Turbo` (~25 GB of bf16 blobs) can be deleted once `models/z-image-turbo-4bit` exists. The owner decides.

## 8b. Progress & ETA reporting
`python -m pipeline progress <ID>` derives progress from the files each step produces (works for runs already in progress):
- per-step status, done/total, measured seconds per unit, time left
- total time left and clock finish time

Use `--watch N --oneline` for periodic updates; the owner wants an update every few minutes during long runs. Rates are learned into `data/rates.json`. Measured so far: Veena best-of-3 about 2 min per scene, Z-Image 768×1344 about 100 s per image, Kokoro about 1 s per scene, render about 1.5 min per video.

## 9. Production standards (defaults)
- **Format:** 1080×1920, 30 fps, H.264 (VideoToolbox, 12 Mb/s), AAC 192 k.
- **Loudness:** −14 LUFS target (loudnorm); QA accepts −16.5 to −13, true peak ≤ −1 dBFS.
- **Duration:** 60–95 s; Hindi runs longer when a Sanskrit verse is recited.
- **Chalk style:** a shared procedural board, a palette limited to white/saffron/gold/green, stroke-by-stroke reveal with chalk stick and dust, whole-board streak-erase transitions, Chalkduster titles with dark halo, word-synced captions with saffron keywords, generated tanpura + bansuri (Bhairavi) score.
- **Chalk SFX gain is permanently reduced: `chalk.CHALK_SFX_GAIN = 0.035`** (30% below the first render). Do not revert. `music_gain` is 0.25.
- **Captions:** grouped by punctuation (including । ॥ —), balanced chunks, `caption_max_chars` per language, no line starting with a Hindi postposition, word timing from Whisper.
- **Presets:** `styles.py` defines pixel, cartoon, whiteboard, papercut, cinematic and chalk.

## 10. Multilingual & localization strategy
- 10 language profiles in `profiles/languages/` (en, hi, mr, bn, te, ta, gu, kn, ml, pa). Each holds Census 2011 audience size, the regional Ramayana traditions that shape expectations, localization guidance, caption font, slot hypotheses and festivals. **Status:** en/hi in use; the other 8 are drafts that need native-speaker review.
- **Rule:** every language version is written originally (audience brief → fresh script). Sanskrit verses stay in Sanskrit in that script, followed by a natural explanation.
- **Voices:** `profiles/voices.json`. Approved: en (Kokoro af_heart), hi (Veena kavya). The other 8 languages are blocked until Indic Parler-TTS is evaluated (needs HF login) and a native speaker has listened.

## 11. Research & topic selection
- **Evidence:** `python -m pipeline trending`, and `python -m pipeline research <ID> --query … --wiki … --langs …` (cached 6–24 h; about 200 YouTube units per language).
- **Scoring:** 10 weighted factors (`content-strategist`). Every score cites evidence or is labelled as judgement. Topics are not chosen only because they trend.

## 12. Storytelling & hooks
See `.claude/skills/storytelling/SKILL.md`. Write at least 6 hooks per language, score them on the 6-criterion rubric (curiosity, emotion, specificity, speed, resonance, accuracy), and keep them in `hooks.json` with reasoning. Mythology rules: cite book.chapter.verse, never invent verses or dialogue, label later traditions, depict deities symbolically when in doubt.

## 13. Publishing workflow
`publish.json` (metadata) → `pipeline schedule` (slot experiment: explore each candidate IST slot until it has 3 × 48 h samples, then exploit) → **G3** → `pipeline publish` (private upload with `publishAt`, plus playlist and thumbnail; the publication is recorded in the database). Pinned comment and Related-video link are set manually in Studio. Instagram code exists in `publish.py` but **auto-upload is disabled by owner decision** until YouTube is proven.

## 14. Analytics
`python -m pipeline analytics` takes due snapshots per publication at 24h, 48h, 7d, 14d and 30d. Each snapshot stores public counters, totals (views, watch minutes, average view duration and percentage, likes, comments, shares, subscribers), daily series, traffic sources, top countries and the retention curve. `python -m pipeline report <VARIANT>` produces a markdown report with retention insights and comparisons. Only metrics the API returns are recorded.

## 15. Optimization logic
Recommendations carry evidence and a confidence level: low below 5 videos, medium 5–15, high above 15 with a consistent effect. A style or profile change needs medium confidence or better **and** owner approval. Mapping: early drop → hook; mid-video drop → scene pacing or visual; language gap → localizer; slot effects → scheduler.

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
  .claude/agents/*.md   .claude/skills/{storytelling,content-pipeline}/
  profiles/languages/*.json  profiles/voices.json  profiles/characters/*.json
  content/<ID>/  manifest.json brief.md research/ audience.md strategy.md <lang>/{script.json,hooks.json,publish.json,qa.md,...}
  docs/  (BLUEPRINT.md original free-tools research, PUBLISHING.md credentials setup)
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
- **`publish.py`**: OAuth (`google_credentials`, separate upload and analytics tokens), `youtube_upload` (publishAt, playlist, thumbnail, DB record), `instagram_publish` (resumable; disabled by policy).
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
- Instagram auto-upload (deferred by owner).
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
  - **Waiting:** the owner listens to `content/C0003/hi/C0003-hi.mp4`, then G2/G3 for HI.
- **Voice decision (2026-11-16):** Hindi moves from Veena kavya to Maya 2 Malini, chosen via a listening pack (`python -m pipeline voicepack`). Malini is far more accurate and about 6× faster. Voice QA is now per voice: a stored reference centroid plus calibrated thresholds.
- **Other changes:** QA normalizes ज्ञ↔ग्य; the Veena lead-in was reverted; the audio folder records the voice used (`audio/voice.txt`) and QA uses it.
- **Pending:** analytics sign-in; an optional HF token (Indic-Speak comparison); consider re-voicing Episode 01/02 Hindi with Malini (owner decision); the scene 8 image (the divine being didn't render) could be retried.

## 23. Exact next steps
1. G1 for C0003: `python -m pipeline approve C0003 script`. Then produce: EN voice; HI `takes` (best-of-2, primed); images (EN, shared); render en/hi; `qa` (must pass speaker_consistency); manual review; G2.
2. Metadata (lint with yt-package), schedule in the evening window (stagger languages), G3, publish with `--yes`.
3. After the owner provides `HF_TOKEN`, run the adoption plan in `reports/Shorts studio voices and tools.md` §plan: IndicConformer QA first, then Indic-Speak A/B.
4. Analytics snapshots for C0001/C0002 after sign-in.

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

## Progress log
| Date | Work | Decisions |
|---|---|---|
| 2026-11-15 | Pilot C0002 stages 1–4 (research, audience, strategy, hooks + scripts EN/HI) → stopped at G1 | Topic B chosen with evidence; Hindi written originally; Rama shown from behind; Brahma symbolic rule kept |
| 2026-11-15 | Built foundation (§19) | Keep existing engines; add a thin `pipeline/` layer + SQLite; agents for judgement, Python for deterministic steps; no third-party skills installed; macOS voices excluded (licence); slot experiments instead of fixed posting times |
