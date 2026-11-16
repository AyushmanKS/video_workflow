# audit_summary: top 15 findings (machine-oriented)

- source: docs/WORKFLOW_AUDIT.md
- audit date: 2026-11-16
- commit: ef038fe (plus the working tree)
- mode: read-only
- legend: V = verified, R = recommendation; P = priority (C/H/M/L)

| id | P | type | finding | evidence | fix |
|---|---|---|---|---|---|
| F01 | C | V | 20/20 videos are 74.8–111.2 s; 0 within 35–55 s; all ≥60 s. By language: en 74.8–89.5, hi 83.2–101.6, gu 93.3–108.5, te 99.5–111.2 | ffprobe on content/C000*/*/C000*-*.mp4 and out/ramayana-ep-01*/final; qa.py:11 max_seconds=180; storytelling/SKILL.md "60-90 s"; scriptwriter.md step 3; EP05_HANDOFF §4 "75–95 s" | encode 35–55 everywhere; `pipeline lint` with per-voice words/s (en 2.81, hi 2.80, gu ~2.3, te 1.66); final QA rejects ≥60 s; 9–10 scenes; budgets en/hi ~125, gu ~100, te ~75 words |
| F02 | H | V | G3 has no platform, time or metadata binding. An Instagram G3 overwrote the YouTube G3 (C0001, C0002). publish `--at` and upload_queue `now` can use unapproved times | __main__.py:43-47 require(); :123 cmd_approve; content/C0001\|C0002/manifest.json gate:publish; data/upload_queue.sh | gate:publish:<platform> holding {lang: iso_time} + sha256(publish.json, mp4); require() checks all three |
| F03 | H | V | G2 and publish never check the QA verdict. 28/40 QA reports are warn or fail; warn videos shipped (C0005-te CER 0.26, captions 976/984 px) | qa_reports table; __main__.py cmd_publish :225; content/C0005/te/qa.md | approve final requires pass, or warn with waivers; publish requires the QA'd mp4 hash to equal the uploaded hash |
| F04 | H | V | Instagram reposted the Ep01 Hindi file with known speaker drift | content/C0001/hi/published.json; PROJECT_CONTEXT §21 | Instagram publish requires a QA pass on that exact file hash; legacy out/ files blocked |
| F05 | H | V | Z-Image Turbo ignores the negative prompt (guidance forced to 0); positive-prompt negations bloat prompts and may prime unwanted concepts | mflux/models/z_image/cli/z_image_turbo_generate.py:23; studio.py:316; styles.py:48; C0005 scene 1 visual | positive prompts; deterministic border auto-crop; automated visual QA |
| F06 | H | V | Character bible is not wired into code; no reference images; no similarity metric | grep: no use of profiles/characters in studio.py, chalk.py or pipeline/; studio.py:306 | `{character}` tokens expanded in step_images; DINOv2 similarity flag; FLUX.2 klein 4B reference A/B |
| F07 | H | V | gu/te voices are "approved" without the native QA that the voice policy requires; profiles still draft; ASR normalization tuned for Hindi | profiles/voices.json _policy; profiles/languages/gu.json and te.json status; qa.py:79 | native reviewer, or tag as an unreviewed cohort; gu/te CER warn-only |
| F08 | H | V | Analytics unusable: 6 snapshots labelled "initial", Analytics API 403; no Instagram insights; 0 recommendations; no features or experiments tables | analytics_snapshots table; analytics.py:63; recommendations count 0 | enable the API; launchd daily job; Instagram insights; features + experiments tables |
| F09 | H | V | Snapshot window mislabelled (first missing label, even when days late); queries cumulative from publish to today; slot exploit ranks on raw views | analytics.py:36-38, :72-75; schedule.py:27 | store age_h; derive windows from by_day; per-language outlier ratio; freeze slots during experiments |
| F10 | M | V | Caches keyed on file existence, not content: editing narration or visual reuses stale audio or images; shared images never refreshed | studio.py:224, :299-303; __main__.py:147 | hash(narration\|voice) and hash(prompt\|seed\|model) cache keys |
| F11 | M | V | QA is the largest compute sink: 293 min across 38 runs vs images 109, render 103; max 59 min; second Whisper pass per scene | runs table; qa.py:95-101; studio.py:580-622 (words.json cache) | reuse the render-time transcript; per-scene QA cache by WAV hash |
| F12 | M | V | Frame 0 is an empty chalkboard; the hook image is only complete at about 1.6 s | chalk.py:241 plan(); frame 0 of C0005-en extracted | predraw scene 1 to ~70% (owner A/B; style change) |
| F13 | M | V | 10 agents, 5 dormant or redundant: research/strategy used only for the C0002 pilot; hooks table stops at C0003; analyst steps are deterministic; language-qa docs say Veena | content/C000*/strategy.md, research/; hooks table; .claude/agents/*.md | 5 active (series-planner, scriptwriter, creative-director, independent reviewer, packager) + 1 dormant optimizer; deterministic work in Python |
| F14 | M | V | Orchestration leaked into shell scripts; YouTube uploadLimitExceeded hit twice | data/upload_queue.sh, data/upload_queue.log, data/logs/fix-*.sh | `pipeline publish-queue` with a persisted queue, daily cap and backoff |
| F15 | M | V | Best-of-N takes are Veena-only; the Maya 2 retake loop is manual; Malini thresholds loosened (0.45/0.6) without a negative-voice calibration; progress.py uses the Kokoro rate for Maya 2 | __main__.py:313; takes.py:14-20; voices.json _speaker_thresholds; progress.py:46 | generalize takes to voicepack engines and auto-run on QA flags; recalibrate with a different-voice negative set |

## Measured facts

| Measure | Value |
|---|---|
| Format | 1080x1920, 30 fps, H.264 VideoToolbox ~12.1 Mb/s, AAC 48 kHz ~181–194 kb/s |
| Loudness | -15.2 to -14.7 LUFS, true peak -1.5 to -1.4 dBFS, LRA 1.9–2.8 (9 finals: C0004 x4, C0005 x4, C0001-gu) |
| Scenes and images | 12–13 scenes per video; 11–12 diffusion images per episode, shared across languages; 1 verse card (2 in C0001) |
| Image time | Z-Image 768x1344, 9 steps: 63→108 s per image (thermal); C0005-en 12 images in 21.5 min |
| Voice time | Maya 2 about 1x real time; Kokoro under 1 s per scene |
| Render time | median 116 s; C0005-en 2,460 frames in 49 s |
| C0005 wall clock | G1→G2 78 min for 4 languages, including fixes |
| Fixed audio overhead | 0.35 s lead + 4.8 s scene pauses + 0.8 s tail |
| Database rows | contents 5, variants 20, research 3, hooks 24, decisions 25, runs 131, qa_reports 40 (12 pass / 17 warn / 11 fail), publications 14, analytics_snapshots 6, recommendations 0 |
| Tests | 7 pass |

## Doc inconsistency

CLAUDE.md and PROJECT_CONTEXT §10 name Veena kavya as the Hindi voice, but voices.json and PROJECT_CONTEXT §22 say maya2:Malini.
