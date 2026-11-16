# Production roadmap: shorts-studio (RAMAYANA, The Epic in Chalk)

**Date:** 2026-11-16 · **Status:** proposal. Nothing here is approved or implemented.
**Readers:** the owner (decides approvals) and future Claude Code sessions (implement).
**Method:** synthesis only, with no new web research. Every item cites its source document. Where the sources disagree, the conflict is listed in §0.3 rather than resolved silently.

**Source keys**

| Key | Document |
|---|---|
| AUD | `docs/WORKFLOW_AUDIT.md` (§ numbers; "F01–F15" = headline findings in `audit_summary.md`) |
| SUM | `research_notes/Studio upgrade research/audit_summary.md` |
| VQ | `docs/VIDEO_QUALITY_UPGRADE_PLAN.md` ("VQ#n" = item n of its 27-item change list; "VQ §x" = section) |
| TL | `docs/TOOLS_AND_SKILLS_RESEARCH.md` ("TL#n" = row n of its ranked shortlist) |
| MOB | `docs/MOBILE_CONTROL_ARCHITECTURE.md` |
| GRO | `docs/GROWTH_AND_MONETIZATION_STRATEGY.md` |

**Legend used in every table**
- **Class:** **OWNER** = owner decision or changes the approved look, sound, metadata or gate policy (needs a side-by-side sample or an explicit yes) · **SAFE** = engineering with no visible or audible change · **G1** = script content through the normal script gate.
- **Effort:** S = under half a day, M = 1–3 days, L = longer or overnight runs (TL definitions). Hours are quoted only where a source gives them. A `*` marks an estimate made by this roadmap, not by a source.
- **Impact:** H/M/L, taken from the source priority (AUD C/H/M/L, VQ P0–P3, TL "expected gain"). None of it is measured.
- **Free?:** every item is zero-cost unless the cell says otherwise.

**Constraints that apply to every item:** zero cost; commercial-use licences only; MacBook Air M5 16 GB with one heavy model loaded at a time; progress updates every 3–5 min on long runs (`python -m pipeline progress <ID> --oneline`); keep the chalk style and `chalk.CHALK_SFX_GAIN = 0.035`; human gates G1/G2/G3; no auto-publish; do not break the working en/hi pipeline; never regenerate, replace or re-upload a published episode. All OWNER A/B tests render from an existing episode's assets (C0005-en by default) into a scratch directory (VQ §6).

---

## 0. One-page summary

### 0.1 The ten highest-impact changes, in order

| # | Change | Why (evidence) | Class | Effort | Source |
|---|---|---|---|---|---|
| 1 | **Encode the 35–55 s target** (beats, per-language word budgets, 8–11 scenes) in the storytelling skill and agents, and add **`pipeline lint`** to block G1 when the estimated duration is too long | 20 of 20 renders run 74.8–111.2 s; none is under 60 s. The skill still says 60–90 s and QA allows 180 s (`qa.py:11`) | OWNER (adopt target), then SAFE + G1 | S + M | AUD F01 §2.5, VQ D1, VQ#1–2 |
| 2 | **Final QA rejects ≥60.0 s**, caption overflow above W−60 px fails, glyph coverage fails | Nothing catches overlong videos; C0005-te shipped 976/984 px caption lines | SAFE | S* | AUD §19.2, VQ#3 |
| 3 | **G2 requires a QA pass** (or warns with recorded waivers), and **publish requires the QA'd mp4 hash to equal the uploaded hash** | 28 of 40 QA reports are warn or fail, and warn videos shipped; Instagram reposted the drifting Ep01-hi file | SAFE (gate semantics: owner informed) | M | AUD F03, F04 |
| 4 | **Approval records bound to platform, time and hashes**, plus a **fail-closed G3 `PreToolUse` hook** | An Instagram G3 overwrote the YouTube G3 (C0001, C0002); `--at` and `upload_queue.sh` can use unapproved times | OWNER (redesign), then SAFE | M + S–M | AUD F02 §18.1, TL#2, MOB §6.4 |
| 5 | **Make analytics usable**: enable the Analytics API, fix the window labels, write `timeline.json`, add `features` and `experiments` tables | 6 snapshots, all labelled `initial`, all HTTP 403; 0 recommendations; no record of what varied | OWNER (API) + SAFE | M | AUD F08, F09 §20 |
| 6 | **Readable frame 0** (scene 0 instant or ≥70% drawn, impact hit at 0.0 s, audio lead 0.35 → 0.15 s) **and per-scene reveal modes** | Frame 0 is an empty board; the hook image is complete only at about 1.6 s; frame 0 effectively is the Shorts thumbnail | OWNER | S* each | AUD F12, VQ D2 D3, VQ#7–8 |
| 7 | **Compliance fixes**: `synthetic: true`, OFL fonts, Made for Kids = No, an honest About page | Inconsistent AI disclosure across platforms; macOS fonts are not clearly licensed for commercial video; the inauthentic-content policy is the main monetization risk | OWNER | S* (fonts M*) | GRO §0.4 §3.4 §3.5 §5.7 |
| 8 | **Positive-only prompts, border auto-crop, `{character}` tokens** | mflux forces guidance 0 for Z-Image Turbo, so negative prompts do nothing; borders are cropped by hand; the character bible is not wired into code | SAFE | S* each | AUD F05 F06, VQ#4–5 |
| 9 | **Telegram bot MVP** (push notifications, G1/G2/G3 from the phone, bound to nonces and hashes) | The owner approves from a phone; Remote Control alone is not a safe record of G3 | OWNER (create bot) + SAFE | 6–8 h | MOB §9 |
| 10 | **Character reference-conditioning test** (FLUX.2 klein 4B) with a DINOv2 drift flag | Consistency is text-only; drift (frontal Rama, four-armed Tataka) is caught only by eye | OWNER | M (test) | AUD §2.7, VQ#18, TL#3 |

### 0.2 Owner decisions required before starting

| # | Decision | Options | Blocks | Source |
|---|---|---|---|---|
| O1 | **Adopt the 35–55 s target**, with a hard limit under 60 s | (a) adopt outright from the next episode; (b) run it as experiment 1 (35–55 s against the current length, alternating odd and even episodes) | A1–A3, D4 experiment design | AUD §20.2, VQ §2, GRO §1.3 (see conflict C1) |
| O2 | **YouTube AI disclosure: set `synthetic: true`?** | Yes (GRO recommends it: under-disclosure risks YPP suspension, and over-disclosure has no documented penalty) / keep false and record the reasoning in `docs/PUBLISHING.md` (AUD §2.13) | D6 | GRO §3.5, AUD §2.13 |
| O3 | **Replace macOS fonts with SIL-OFL fonts** (Chalkduster, Chalkboard SE, Kohinoor, ITF Devanagari, Sangam MN → Noto Sans/Serif Devanagari, Gujarati, Telugu plus an OFL chalk display face). This is a **style change** | Switch after a side-by-side; or get written confirmation that the current fonts are licensed for commercial video | D6, any licensing deal, YPP application | GRO §5.7 §7 Phase 0 |
| O4 | **Approval-record redesign**: `gate:publish:<platform>` holding `{lang: iso_time}` plus sha256 of `publish.json` and the mp4; `script.json` hash at G1; mp4 hash at G2; `approve` interactive by default; `--yes` only with `STUDIO_OWNER_APPROVED=<ID>`; Claude never records G3 | Accept / amend | A10, A11, B7, C1 | AUD §2.14 §18.1, MOB §6.4 |
| O5 | **Frame-0 and reveal-mode style change** | Instant frame 0 / predraw to 70% / hybrid (hold the finished image 0.3 s, then a trace flourish) / keep today's opening | A4, A5 | VQ#7–8, AUD §2.8 |
| O6 | **Telegram bot** (project data sits on Telegram's cloud; `protect_content` on) and **Remote Control** setup | Yes / no | Phase C | MOB §1 §6.5 |
| O7 | **Dashboard licence**: Tailscale Personal says "only suitable for non-commercial use" | (a) skip the dashboard (default); (b) WireGuard if the home line has a public IP; (c) paid plan (breaks zero cost) | C3 | MOB §4.1 |
| O8 | **Fix the `CLAUDE.md` Hindi voice line**: it says Veena kavya, but `voices.json`, PROJECT_CONTEXT §22 and project memory say `maya2:Malini` | Update `CLAUDE.md` (and PROJECT_CONTEXT §10, `language-qa.md`) | A12 | SUM "Doc inconsistency", TL §6, AUD §6 |
| O9 | **gu/te native review**: the voices are "approved" without the native QA the voice policy requires | Find a native reviewer / tag gu and te as an `unreviewed-language` cohort in the DB | D7, E6 | AUD F07 §2.9 |
| O10 | **Agent consolidation** from 10 to 5 active plus 1 dormant | Accept / amend | B1 | AUD §18.3 |
| O11 | **Studio actions only the owner can take**: enable the YouTube Analytics API; Made for Kids = No; rename the channel to match the series; one serial Shorts show per language; review auto-dubbing | Do / defer | D1, D5, D6 | AUD §2.16, GRO §1.4 §2.4 §7 Phase 0 |

### 0.3 Conflicts between the source documents

| # | Conflict | Proposed handling |
|---|---|---|
| C1 | GRO §1.3 says "Keep 60–95 s unless retention supports longer"; AUD, VQ and the owner's stated target say 35–55 s | GRO predates the duration finding. Follow O1. Fix the GRO line once O1 is decided |
| C2 | The lint block threshold is ">58 s" (AUD §2.5, §19.2) or ">57 s" (VQ §2.4, §3.5) | Use 57 s (stricter); final QA rejects ≥60.0 s in both |
| C3 | Word budgets: AUD gives ~125/125/100/75 (en/hi/gu/te) for 50 s; VQ gives 114/114/88/66 for 45 s and 140/140/108/81 for 55 s | Use the VQ table (it has a formula and three targets); the lint is the arbiter |
| C4 | The ducker constant is quoted as `1 - 0.45·clip(env/0.05)` (VQ D7) and `1 - 0.65·…` (TL §3) | Read `studio.py` step_audio (:660–673) before retuning (B10) |
| C5 | `CLAUDE.md` Veena vs Malini | O8 |

---

## 1. Phase A: immediate quality improvements (next few videos)

Goal: the next produced episode is under 60 s, has a readable frame 0, is loudness-accurate, and cannot reach G2 or publish with known defects. No published episode is touched.

| ID | Item | Why (evidence) | Component | Free? | Requirements | Effort | Impact | Risk | How to test | Depends | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | Encode 35–55 s, the beat table (H1/H2/C/E/T/P/N), word budgets per language, loop and cliffhanger rules, citation edition labels and `quote_src` | All 20 renders are over 60 s; the skill says 60–90 s and "9–14 scenes" | `.claude/skills/storytelling/SKILL.md` (description and checklist → 35–55 s, 8–11 scenes); `.claude/agents/scriptwriter.md` step 3; `creative-director.md` | yes | O1 | S | H | scripts feel rushed if words are cut badly | next script: estimated vs rendered seconds per language, all ≤57 s | O1 | OWNER (target) + G1 per script | AUD F01, VQ#1, VQ §2 |
| A2 | `pipeline lint <ID>`: duration per language (speech rates en 2.81, hi 2.80, gu ≈2.3, te 1.66 w/s, plus pauses and 1.15 s lead and tail), hook ≤3.0 s (warn >2.2), 8–11 scenes of 2.5–7 s each, keywords present, no digits in gu/te, sources and edition, visual parity with the primary language, `quote_src` for every quote, 2–3 planned silences | Defects are found after rendering, or not at all | new `pipeline/lint.py`; `pipeline/__main__.py` `approve script` requires a pass | yes | measured w/s per voice | M | H | rate drift per voice; recalibrate from each new render | lint estimate within ±3 s of the rendered duration on C0004 and C0005, all 4 languages | A1 | SAFE | AUD §2.5 §19.2, VQ#2 |
| A3 | Final QA: duration ≥60.0 s rejects, outside 35–55 s warns; caption width > W−60 px fails, with auto-split in `caption_groups`; glyph coverage (every narration and verse character in the font's cmap) fails; first-frame non-board share warns | QA can fail only on format, loudness, black/freeze and speaker | `pipeline/qa.py` (`STANDARD` :11, `check_captions` :111/:132); `studio.py` `caption_groups` :360 | yes | none | S* | H | false positives on the first-frame metric (so it only warns) | run on all 20 existing renders (read-only): all 20 must fail duration; C0005-te must fail overflow | none | SAFE | AUD §19.2, VQ#3 |
| A4 | Frame-0 rule: scene 0 `instant` or starting ≥70% drawn; `impact` hit at 0.0 s; audio lead 0.35 → 0.15 s so the first word lands at ≤0.3 s; hook captions in 2–3-word groups shown by 0.3 s | Frame 0 is an empty board (`chalk.py:241`); the hook is fully visible only at about 1.6 s | `chalk.plan()` i==0 branch; `studio.py` step_audio lead :631–632; `chalk.sound` | yes | O5 | S* | H | loses the approved "drawing appears" opening (the hybrid option keeps some of it) | non-board pixel share at t=0 ≥ about 5% (today about 0); first word ≤0.3 s from word timestamps; owner A/B on C0005-en | O5 | OWNER | AUD F12, VQ#7, VQ §2.6 |
| A5 | Per-scene `reveal` modes: `draw` (2.0–3.6 s, ≤3 per episode), `fast` (0.5–0.8 s, the default), `instant`, `ghost` | Roughly half of each scene is drawing or erasing; at 45 s with full draws each image would be fully visible for about 1 s | `chalk.plan()` draw duration; `render()` visibility mask | yes | none | S* | H | too many instant reveals dilute the chalk identity (lint caps `draw` at ≤3) | fully-drawn time share per shot, A vs B; owner A/B bundled with A4 | O5 | OWNER | VQ D3, VQ#8, VQ §3.6 |
| A6 | Two-pass linear `loudnorm` plus narration pre-normalisation to −16 LUFS | Single-pass dynamic loudnorm ends at −15.2 to −14.7 LUFS and can pump the bed | `studio.py` step_audio (:630), step_render (:705); `pipeline/qa.py` `check_loudness` (:42) | yes | ffmpeg 9.0.1 (installed) or pyloudnorm (MIT) | S | M | none audible beyond the level change | integrated −14 ±0.5 LUFS on C0005 ×4 (re-encoded to scratch); LRA not reduced further | none | SAFE | AUD §1, VQ#12, TL#1 |
| A7 | Positive-only prompt rewrite (drop negations; Z-Image Turbo ignores `negative`) plus deterministic border auto-crop (edge-band mean luminance > interior + 0.25 → crop; still present → reject) | C0005 scene 1's `visual` is about 110 words, a third of them negations that may prime the concepts they forbid; a manual crop `(24,42,744,1302)` is in the handoff gotchas | `styles.py` chalk `prefix`/`negative` (:46–67); `studio.py` step_images (after generation, :289–321); scriptwriter and creative-director guidance | yes | none | S* | H | the crop could clip a real edge element | re-crop the existing C0001–C0005 raws offline; compare detections with the manual crop list | none | SAFE | AUD F05 §2.6, VQ#4 |
| A8 | `{character}` token expansion from `profiles/characters/ramayana.json` | No code reads the bible; prompts are pasted by hand and drift | `studio.py` step_images prompt build (:304–306) | yes | none | S* | M | none | unit test: the expanded prompt equals the bible text verbatim | none | SAFE | AUD F06, VQ#5 |
| A9 | Character reference-conditioning **measurement** (adoption is B or E): FLUX.2 klein 4B, 768×1344, 4-bit vs 8-bit, text-to-image and edit with 1–2 references, on 4 character scenes from C0004/C0005 | Consistency is text-only; Narada needed a prompt patch | new `scene_with_refs` path in step_images (test branch only); reference sheets in `profiles/characters/refs/<id>/` (media kept out of git, hashes in `ramayana.json`) | yes (Apache-2.0, ungated, re-verified 2026-11-16) | about 4 GB disk (4-bit); owner-approved reference stills (from behind, three-quarter, silhouette); run alone with `/usr/bin/time -l` | M | H | slower images (M1 Max about 52 s per reference edit; Air unmeasured); hair-colour drift seen in that test; style shift away from Z-Image chalk | DINOv2 cosine to the sheet, time per image and peak RSS, owner preference | A8 | OWNER | VQ#18, TL#3, TL §7 |
| A10 | QA gating of G2: `approve final` refuses unless the latest `qa_reports` verdict for the variant is pass, or warn with every warning carrying a recorded waiver (text plus who); `done voice_qa/video_qa` can no longer mark a stage done regardless of the verdict | 28 of 40 reports are warn or fail; all C0005 `voice_qa` marks were written in the same second as bookkeeping | `pipeline/__main__.py` `cmd_approve` (:123), `require()` (:43–47), `done` | yes | none | S* | H | blocks a release on a false-positive warn (the waiver path covers it) | approve a C0005 variant in a test DB with a warn and no waiver → refused | A3 | SAFE (owner informed) | AUD F03 §19.2 |
| A11 | Approval records per platform, time and hash: G1 stores the sha256 of each `script.json`; G2 stores the mp4 sha256; G3 becomes `gate:publish:<platform>` with `{lang: iso_time}` plus sha256 of `publish.json` and the mp4; `require()` rejects any time, metadata or video mismatch; `publish` recomputes hashes; `approve` is interactive (prints hashes, asks for the variant ID); `--yes` only with `STUDIO_OWNER_APPROVED=<ID>`; explicit `--langs`; `--by/--channel/--nonce`; new `reject <ID> <gate> --note`; legacy `out/` files blocked for any new platform upload | G3 has no platform, time or metadata binding; advance approvals were recorded before the gu/te scripts existed; a re-render after G2 keeps the old approval | `pipeline/__main__.py` `cmd_approve`, `require()`, `cmd_publish` (:225); `manifest.json` schema; `decisions` table (`pipeline/db.py`) gains `actor`, `channel`, `artifact_sha256` | yes | O4 | M | H | migration of existing manifests (C0001–C0005 already carry overwritten `gate:publish`) | publish a test variant whose mp4 changed after G2 → refused; an Instagram G3 no longer alters the YouTube record; add a test that agents' tool allowlists exclude `pipeline approve` | O4 | OWNER (redesign) → SAFE | AUD F02 F04 §2.5 §2.14 §18.1, MOB §2 §6.4 |
| A12 | Doc reconciliation: `CLAUDE.md` Hindi voice line, PROJECT_CONTEXT §10, `language-qa.md` (still prescribes Veena takes), EP05_HANDOFF §4 "75–95 s" | Owner-facing confusion; agents follow stale instructions | `CLAUDE.md`; `PROJECT_CONTEXT.md` §9–10; `.claude/agents/language-qa.md` | yes | O8 | S* | M | none | grep shows no "Veena" as the current voice and no "60–90 s" target | O1, O8 | OWNER (`CLAUDE.md`) / SAFE (others) | SUM, AUD §6, TL §6 |
| A13 | Script craft rules at G1: 2–3 planned silences of 0.3–0.8 s (before the Turn and Payoff), engagement line ≤6 words with a real answer, "Next:" card ≤3 words, one loop type per episode, pronunciation respellings via the per-scene `tts` field | No sonic punctuation; pattern interrupts at no word cost | `script.json` `pause` and `tts` fields | yes | A1 | S* | M | none | lint counts the silences of ≥0.3 s | A2 | G1 | VQ#6, VQ §2.7 §2.8 |

---

## 2. Phase B: production workflow

Goal: fewer agents, more deterministic Python, scored QA with thresholds, correct caches, and mechanical gate enforcement. Then the motion upgrades, each behind an owner A/B.

| ID | Item | Why (evidence) | Component | Free? | Requirements | Effort | Impact | Risk | How to test | Depends | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | Agent consolidation, 10 → 5 active + 1 dormant: **series-planner** (merges trend-researcher, content-strategist, audience-localizer; runs per arc), **scriptwriter** (absorbs localization and source verification), **creative-director** (no longer judges its own images), **reviewer** (merges language-qa and video-qa; read-only, scores, never edits), **packager** (metadata only; uploads stay Python); **optimizer** dormant until ≥30 variants have 7-day data | 5 agents are dormant or redundant; research and scoring were used only for the C0002 pilot; the analyst's steps are deterministic | `.claude/agents/*.md`; `.claude/skills/content-pipeline/SKILL.md` | yes | O10 | S | M | handoff gaps during the switch | one full episode run (script → G3 bundle) with the new set; each agent's quality signal recorded (lint pass rate, regenerations per episode, defects caught before the owner) | A2, B4 | OWNER (decision) → SAFE | AUD F13 §18.1–18.3 |
| B2 | Deterministic Python replacements: `pipeline publish-queue` (persisted queue table, daily cap, backoff, priority by publish date; replaces `data/upload_queue.sh` and the `data/logs/fix-*.sh` scripts); weekly launchd research job writing `data/reports/competition-<date>.md`; `pipeline hooks <ID>` loading `hooks.json` into the DB; automatic feature logging at `done script`, `render`, `publish`; Instagram stage keys added to `STAGES` | Orchestration leaked into shell scripts; `uploadLimitExceeded` hit twice; nothing writes to the `hooks` table; `status` ignores Instagram (`__main__.py:11`) | new `pipeline/queue.py`*; `pipeline/research.py`; `pipeline/__main__.py`; `pipeline/db.py` | yes | none | M | M | the queue must respect G3 times exactly (it reads A11 records) | dry-run the queue against the current backlog: no upload before its approved time; daily cap honoured | A11 | SAFE | AUD F14 §2.1 §2.4 §2.15 §18.2 |
| B3 | Generalized best-of-N takes for any `voicepack` engine (keep the first take with no pitch outlier >7 semitones, window similarity ≥ threshold and scene similarity ≥0.6; cap 6; log the take index; save every take as `audio/takes/NN_kK.wav`), auto-run on QA-flagged scenes; recalibrate the Malini thresholds (0.45/0.6) with a negative set (another Maya voice speaking the same lines); fix the Maya 2 rate in `progress.py:46` | The Maya 2 retake loop is manual; the thresholds were loosened without negative calibration | `pipeline/takes.py` (:14–20); `__main__.py` (:313); `profiles/voices.json` `_speaker_thresholds`; `pipeline/progress.py` | yes | voice model loaded alone | S | M | a threshold that is too tight raises retakes | calibration report: separation between the Malini self-similarity and the negative voice; QA `speaker_consistency` still passes | none | SAFE | AUD F15 §2.9, MOB §5 |
| B4 | **QA scoring system**: Story/Visual/Audio/Final families scored 0–100; a family passes only with no auto-reject failure and a score ≥80. New checks: speech rate per scene (±25% warn, ±40% reject); CER en/hi >0.30 reject, >0.15 warn; CER gu/te warn only until Indic ASR is validated; music under speech <12 dB warns; Visual QA on `img/NN_raw.png` with Tesseract OCR (≥3 characters warns), perceptual-hash duplicates (<8 bits warns), chalk density outside 3–45% warns, safe-zone stroke energy warns, DINOv2 character similarity (human flag only); file binding of the QA'd mp4 | QA has no visual, duration, safe-zone, glyph or balance checks; verdicts are not scored | `pipeline/qa.py` | yes | Tesseract (Apache-2.0); DINOv2 (Apache-2.0) | M* | H | false positives (hence warn classes and waivers) | precision on the C0001–C0005 raws against the known fixes; all 20 existing renders scored | A3, A10 | SAFE | AUD §19.2, VQ#19 |
| B5 | QA compute: reuse the render-time Whisper transcript (`NN.words.json`) instead of a second pass; per-scene QA cache keyed by WAV hash; load ECAPA once per run | QA is the largest compute sink: 293 min over 38 runs (images 109, render 103), up to 59 min per run | `pipeline/qa.py` (:95–101); `studio.py` `align_words` (:580–622) | yes | none | S | M | a stale transcript if the audio changes (solved by the hash key) | QA wall time per language before and after on C0005 ×4 (baseline median 115 s, p90 1,000 s) | B6 | SAFE | AUD F11 §6 |
| B6 | Cache invalidation by content hash: audio keyed on hash(narration \| tts \| voice); images on hash(prompt \| seed \| model); shared images refreshed on change | Editing `narration` or `visual` silently reuses stale assets unless files are deleted by hand | `studio.py` (:224, :299–303); `pipeline/__main__.py` `share_images` (:136–148) | yes | none | S* | M | an unnecessary full regeneration if the hash includes volatile fields | edit one scene's narration in a scratch copy → only that scene's audio regenerates | none | SAFE | AUD F10 |
| B7 | **Fail-closed G3 `PreToolUse` hook**: matcher `Bash` with `if` on `python -m pipeline publish*`, `data/upload_queue.sh` (or its B2 replacement) and `pipeline approve .* publish`; `"onFailure": "block"`; the checker exits 2 unless the A11 record matches platform, time and hashes | G3 is an instruction, not a mechanism; hook timeouts fail open by default | new `.claude/settings.json` (none exists today) plus a checker calling `require()` | yes | A11; check the hook JSON schema against the docs first; the owner applies the settings change | S–M | H | a misconfigured hook could block legitimate terminal publishing (test both paths) | a denied command really exits 2; a simulated hook timeout blocks | A11 | SAFE (owner installs) | TL#2 §4.5, MOB §6.4 |
| B8 | `audio-mix` project skill (about 100 lines: two-pass recipe, per-engine stem gains, `licenses.csv` SFX index, QA thresholds); split publishing out of `content-pipeline` into its own skill with `disable-model-invocation: true` | Agents re-derive the mix; the publish step can be auto-invoked | `.claude/skills/audio-mix/SKILL.md`; a new publish skill; `content-pipeline/SKILL.md` | yes | none | S | L–M | none | skill loads; the publish skill is not auto-invoked | A6, B9 | SAFE | TL#8 §4.5 |
| B9 | SFX library: Sonniss GDC 2026 bundle (royalty-free, monetized YouTube allowed, no redistribution, **no AI/ML training**) plus Freesound **CC0 only**, all logged in a mandatory `licenses.csv` (file, source URL, licence); a file loader in `chalk.sound` | Eight procedural SFX only; no real conch, bells or tabla | a gitignored data directory; `chalk.sound` (`chalk.py:624`) | yes | 7.47 GB disk; a free Freesound API token for scripted search | S | M | licence slip (the CSV lint guards it); shehnai has 0 CC0 files | lint: every SFX file used has a CSV row | none | SAFE (library) / OWNER (sounds used) | VQ#20, TL#7 |
| B10 | New procedural SFX (`impact`, `bowstring`, `whoosh`, `rumble`, `rocks`, `conch`, `heartbeat`; beds `fire`, `army`, `sea`) plus the `hit` field; ducking retune to −18 to −22 dB under speech and +4–6 dB in gaps; chalk gain untouched | No sonic punctuation at the hook, turn or payoff | `chalk.sound` dispatch dicts; `studio.py` step_audio duck lines (:660–673); music-under-speech metric in `qa.py` | yes | A6 | S* | M | cheesy or busy (cap about 4 hits per episode); over-ducking pumps | owner listening A/B; SFX peaks 3–6 dB under narration peaks; speech-band minus bed ≥12 dB | A6 | OWNER (sound) / SAFE (metric) | VQ#13–14, VQ §4 |
| B11 | Shot grammar: optional per-scene fields (`shot`, `angle`, `move`, `transition`, `image` + `crop`, `dur_hint`, `overlay`, `music`) with defaults that reproduce today's render; transitions (cut, erase 1–3 per episode, black, flash, dust, whip); moves (push/pull to z 1.20, tilt, truck, shake, Dutch, whip blur); still reuse via crops (12–13 shots from 8–10 stills); validator rules 3–9 in `pipeline lint` | Every shot uses the same grammar; image time scales with the scene count (about 100 s per still saved by reuse) | `chalk.plan()` `vs`/`ds`; `render()` transition branch and camera block; `cam_matrix` (rotation argument); `chalk.sound` erase emission; `step_images` skips reused stills | yes | A5 | M* | H | `black_freeze` false positives on dips; overscan about 10% before board edges show (`clamp_focus`); soft crops beyond 2× of the 768 px source | old scripts render byte-identical; SSIM tear check; corner-pixel edge test; owner A/B bundled with A4/A5 | A5, A2 | OWNER | VQ#9–11, VQ §3.5 §5.2 |
| B12 | **Parallax renderer**: mask-based two-plane parallax first (BiRefNet MIT or SAM 2.1 small Apache-2.0), then three planes with Depth Anything V2 **Small** (Apache-2.0); the board moves with the far plane; thin gaps filled with `cv2.inpaint`; own code (about 150–250 lines), no DepthFlow import | A flat zoom; the procedural board needs no inpainting, so the look is unchanged | new plane compositor in `chalk.py` after `chalk_from_image` (:96); per-plane `cam_matrix` (:311) | yes | BiRefNet about 1 GB, DA-V2 Small about 100 MB; models loaded and unloaded in turn | M | H | tearing; monocular depth on chalk is unvalidated (fall back to masks only) | depth maps on 5 existing stills first; one scene rendered three ways (current, mask, depth) with SSIM between frames; owner A/B | B11 (moves) | OWNER | VQ#16, TL#4–5 §2.3 |
| B13 | **Procedural motion and overlays**: figure-mask breathing (0.5–1% at about 0.25 Hz), `cv2.remap` sway, hair and cloth flutter; embers, smoke, petals, dust storm, god rays and rain via the `Particles` class; sponge-wipe and dust-puff variants beside the approved streak-erase; no blinking | Scenes feel static | `Particles`; `render()` | yes | B12 masks for figure motion | M | M–H | uncanny motion; render time | render time per frame (baseline: C0005-en 2,460 frames in 49 s); owner A/B | B12 | OWNER | VQ#17, TL#6 §2.4 |
| B14 | `step_render` writes `timeline.json` (scene starts and ends, hook end, verse window) | Retention-to-scene mapping is impossible without persisted render timings | `studio.py` step_render | yes | none | S* | M | none | timeline scene boundaries match the rendered cuts on one test render | none | SAFE | AUD §2.16 §20.2 |
| B15 | Per-scene `accent` hues (Lanka crimson ≈ 0–8°, ≤3 hues per frame; default unchanged) | `restrict_palette` snaps every hue to saffron, gold or green, so every world looks the same | `restrict_palette(rgb, hues)`, `chalk_from_image`, `render()`; a world map in `ramayana.json` | yes | none | S* | M | crimson can read as gore or "evil" | owner A/B on one recoloured scene; hue histogram per frame | none | OWNER | VQ#15 §3.2 |

---

## 3. Phase C: mobile management

Goal: the owner runs, reviews and approves from an Android phone, with the same gate records as the CLI. No inbound ports, nothing public, nothing paid.

| ID | Item | Why (evidence) | Component | Free? | Requirements | Effort | Impact | Risk | How to test | Depends | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | Setup: create the bot in BotFather (groups off); `claude remote-control --name shorts-studio` in tmux with both push toggles on; pair the Claude Android app; Telegram two-step verification and app passcode | Remote Control is covered by the existing subscription and is outbound-only | BotFather; tmux; `/config` | yes | O6 | about 30 min | M | Remote Control is free-text, so it is not a G3 record | push received when a test task finishes | O6 | OWNER | MOB §9 Phase 0 |
| C1 | **Telegram bot MVP**: `pipeline/bot.py` (stdlib + `requests`, long polling, owner allowlist, `pair`, `/status`, `/progress`, `/help`); watcher on `runs`, manifests and progress, editing one progress message every 4 min; `remote_actions` table with single-use nonces, expiry and hash binding; G1 (script text + Approve / Request changes / Reject); G2 (540p proxy + QA verdict + mp4 sha256); G3 two-step typed code bound to the mp4, `publish.json` and `schedule.json` hashes per language and platform; launchd plist with `KeepAlive`; tests | Phone approvals must use exactly the gate the CLI uses | `pipeline/bot.py`; `~/Library/LaunchAgents/com.shortsstudio.bot.plist`; `pipeline/db.py`; `secrets/telegram.json` (mode 600) | yes | A11 (`--by/--channel/--nonce`, `reject`) | 6–8 h | H | phone loss (Telegram passcode, `bot lock` panic command); unpublished proxies on Telegram's cloud (`protect_content`) | **MVP done when:** push on render finish, proxy watched, G2 approved, G3 completed with the typed code, and `pipeline audit C000X` shows actor, channel, nonce and sha256 for each gate | C0, A11 | SAFE (after O6) | MOB §4.2 §5 §9 Phase 1 |
| C2 | Review depth: per-scene `review.json` (image and voice ok/redo with hashes; G2 buttons only when every scene is ok or waived); voice-take comparison (needs B3 saved takes); `data/heavy.lock` queue and allowlisted `produce`/`takes`/`qa` verbs; publish-time hash re-check; the hook blocking Claude from recording G3 (shared with B7); Instagram job monitoring, overdue alerts and a printed `pmset schedule wake` hint; a `SubagentStart`/`SubagentStop` hook writing `agent:<name>` runs rows | No per-scene review state; nothing shows which agent is running; heavy jobs could collide on 16 GB | `pipeline/bot.py`; `content/<ID>/<lang>/review.json`; `.claude/settings.json` | yes | C1, B3, B7 | 1–1.5 days | M | over-notification (one edited message per run) | "redo scene" refused while a heavy job holds the lock; a stale nonce is rejected after a re-render | C1, B3, B7 | SAFE | MOB §5 §7 §9 Phase 2 |
| C3 | Optional dashboard: FastAPI on `127.0.0.1` only, server-rendered HTML, same nonce and hash rules, CSRF, identity allowlist | Only if Telegram review proves too cramped | `pipeline/web.py` | Tailscale Personal is free but "non-commercial use only"; WireGuard is free but needs a public IP; a paid plan breaks zero cost | O7 | 1.5–2 days | L | public exposure if misconfigured (never Funnel or quick tunnels) | reachable only on the chosen private path; foreign `Origin` rejected | C2, O7 | OWNER | MOB §4.1 §9 Phase 3 |
| C4 | Analytics push: daily launchd `pipeline analytics` → summary message; weekly optimizer report link. The bot only relays `report` output and generates no numbers | No-fabrication rule; the owner sees data without opening Studio | `pipeline/bot.py`; launchd | yes | D1, D2 | 0.5 day | L–M | none | a message matches `pipeline report` output exactly | D2, C1 | SAFE | MOB §5 §9 Phase 4 |

---

## 4. Phase D: growth and monetization

Goal: real data, a learning loop that cannot fool itself with small samples, clean compliance, series navigation, and readiness for the first revenue tools. **No revenue forecasts** (GRO scope).

| ID | Item | Why (evidence) | Component | Free? | Requirements | Effort | Impact | Risk | How to test | Depends | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D1 | Enable the YouTube Analytics API | Every `totals` field is HTTP 403; no usable data | Google Cloud console (owner); existing OAuth in `secrets/` | yes | owner login | S* (owner) | H | none | `pipeline analytics --force` returns non-403 totals for one published variant | none | OWNER | AUD F08 §2.16 |
| D2 | Fix the analytics windows: store `age_h = captured_at − published_at`; query `startDate=endDate` for the day series; compute windows from `by_day`; label a window only within ±12 h of it, otherwise `age_<n>h`; daily launchd job | A "24h" row captured on day 5 holds 5 days of data; queries are cumulative | `pipeline/analytics.py` (:36–38, :72–75); launchd plist | yes | D1 | S* | H | none | re-label the 6 existing snapshots correctly; the next daily run lands within ±12 h | D1 | SAFE | AUD F09 §2.16 |
| D3 | Instagram insights: Reels plays, reach, saved, shares, `ig_reels_avg_watch_time` via the existing token, stored in `analytics_snapshots` with `platform='instagram'` | No Instagram data at all (`analytics.due` filters YouTube, `:63`) | `pipeline/analytics.py`; `pipeline/instagram.py` | yes | existing token | S* | M | API fields may differ from the doc (verify on first call) | one snapshot per published Reel | D2 | SAFE | AUD §2.15 |
| D4 | **Experiment table and learning loop**: `features` row per variant (duration, scenes, words, w/s, hook type/words/seconds, first-frame type, voice, language, slot, weekday, episode, title pattern, has_verse); `experiments` table (hypothesis, variable, arms, assignment rule, metric, min n per arm, stop rule, status, result). Rules: one experiment at a time; alternate arms by odd and even episode across all languages; **≥6 variants per arm per language before any claim** (fewer = "anecdote"); pre-registered stop rule (e.g. after 12 episodes, or when the interval excludes 1.0); never stop early on one spike; compare within a language by ratio to that language's rolling median, never raw views across languages; freeze slots during content experiments; `schedule.py:27` ranks on the per-language outlier ratio. Order: duration → frame 0 → hook type → slot | No record of what varied; the slot scheduler ranks raw 48 h views across languages | `pipeline/db.py`; `pipeline/schedule.py`; `pipeline/analytics.py`; `recommendations` rows with effect, interval, n per arm and tier | yes | D2, B2 (feature logging), B14 | M | H | confounding with episode decay; small n | a synthetic dataset reproduces the median ratio and bootstrap interval; the optimizer refuses to emit a recommendation below the n rule | D2, B14, O1 | SAFE (design) / OWNER (which variable) | AUD §2.17 §20.2 |
| D5 | Series setup: one **serial Shorts show per language** (not one mixed playlist); translated titles and descriptions; per-language channel sections; related-video chain (link to the previous episode in the same language, switch to the next once live; manual, the API cannot set it); pinned comment (verse citation, real question, "Ep N+1: date"); review auto-dubbing in Studio → Languages after each upload; Instagram language Highlights; rename the channel to match the series brand (check the rename limit first) | Shows can appear under "Recommended shows" and "Continue watching"; a mixed serial would play hi, en, gu versions of one episode in a row; the brands don't match | YouTube Studio and the Instagram app (owner); `publish.json` titles via the packager | yes | advanced features for related links | S* per episode (owner) | M–H | auto-dubs competing with native versions | each language has a serial show; every new Short has a related link and a pinned comment | O11 | OWNER | GRO §1.4 §1.6 §2.4 |
| D6 | **Compliance fixes**: `synthetic: true` on YouTube (matching Instagram `is_ai_generated=true`), with the reasoning in `docs/PUBLISHING.md`; OFL fonts replacing the macOS fonts (side-by-side first); Made for Kids = No on the channel and every video; an About page and descriptions stating the workflow honestly ("illustrations and narration made with AI tools; every script checked against the Valmiki Ramayana"); symbolic violence only, never in the thumbnail or first seconds; never a licensed trending track | Inconsistent disclosure risks YPP suspension; font licence unclear for commercial video; the inauthentic-content policy is the main risk | `publish.py:103`; `content/<ID>/<lang>/publish.json` (new episodes only); `chalk.py` `SCRIPT_FONTS` (:19) and `title_layer`; `styles.py` chalk caption font; YouTube Studio | yes (OFL) | O2, O3 | S* (disclosure), M* (fonts, incl. glyph check) | H | the font change alters the approved look; already-published episodes keep their fonts (no re-upload) | glyph-coverage QA (A3) passes in all 4 scripts with the new fonts; owner side-by-side on C0005-en | O2, O3, A3 | OWNER | GRO §0.4 §3.5 §3.6 §5.7 §7 Phase 0 |
| D7 | gu/te native review, or tag them as an `unreviewed-language` cohort and analyse them separately | Voices approved without the policy's native QA; profiles still "draft"; CER unreliable for gu/te | `profiles/languages/gu.json`, `te.json`; `variants` table flag | yes | O9 | S* | H | publishing pronunciation errors in two languages | every gu/te variant carries the flag or a native sign-off | O9 | OWNER | AUD F07 §2.2 §2.9 |
| D8 | **Long-form Kanda compilations** per language (e.g. "Bala Kanda, part 1: episodes 1–8", 10–15 min) only with real added value: a new spoken introduction and bridges, chapters, full verses with explanation; 16:9, or 9:16 with a designed frame; each Short's related link points to it | Shorts-feed hours do not count toward the 3,000- or 8,000-hour routes; long-form hours do. Compilations of others' clips with little narrative are reused content, and how a channel's compilation of its own Shorts is treated is **unverified** | new compilation path in `studio.py`*; new G1 script for the bridges | yes | a complete Kanda section produced; G1 for new narration | M–L* | H (watch hours) | read as a reused-content compilation if it adds too little | owner G2 on the first compilation; chapters present; new narration share recorded | A1, D5 | OWNER + G1 | GRO §3.1 §3.6 |
| D9 | Fan-funding readiness: Instagram Gifts payout account at 500 followers (India is supported); expanded YPP application when eligible (500 subscribers, 3 uploads in 90 days, 3,000 hours or 3M Shorts views in 90 days); W-8BEN treaty claim in AdSense (India 15% on US-viewer earnings vs 24% of worldwide earnings with no tax info); CA consultation on GST (LUT) and ITR; Amazon.in book links (4.72% on books, 0 on Kindle) in long-form descriptions and link-in-bio; YouTube memberships with low-cost perks, core episodes never paywalled | First revenue tools in GRO order: Gifts → fan funding → book links → sponsorships → ads last | Instagram Professional Dashboard; YouTube Studio Earn tab; AdSense | yes | thresholds reached (tracked, not forecast); D6 done first | S* each (owner) | M | applying before compliance fixes; do not apply during a split (§2.5 sequencing) | checklist items closed in Studio | D6 | OWNER | GRO §3.1 §3.7 §4 §5.2 §5.5 §5.6 |
| D10 | Four-copies mitigation: vary the opening frame and cover per language; watch for cannibalisation (one language normal while others stall across several episodes) | One channel shows four near-identical visuals per episode, the hardest point to argue under the inauthentic-content policy | `script.json` scene 1 per language; Instagram `cover_url`; D4 per-language ratios | yes | D4 data | S* per episode | M | adds per-language image work | per-language opening frames differ on new episodes; cannibalisation check in the weekly report | D4 | G1 / OWNER | GRO §1.5 §3.4 |

---

## 5. Phase E: advanced production

Goal: larger creative upgrades and expansion, each gated by a measured test and an owner verdict, and started only after analytics confidence reaches medium (VQ run order step 5; PROJECT_CONTEXT §15 tiers: low <5, medium 5–15, high >15 videos).

| ID | Item | Why (evidence) | Component | Free? | Requirements | Effort | Impact | Risk | How to test | Depends | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | Chalk-style LoRA (fixes "shaded pastel, not line art"), then per-character LoRAs only if references (A9) are not enough; `mflux-train` on Z-Image base or klein base 4B | Closer to sparse line-art chalk; stable identity | `styles.py` chalk preset LoRA path; overnight solo training run | yes (Apache-2.0 bases; mflux MIT) | training images public-domain or owned only; RAM unknown on Apple Silicon (CUDA reference about 10–10.8 GB) | L | M–H | memory pressure on 16 GB; overfitting | 500–1000-step pilot at 512 px with s/it and RSS logged; owner A/B | A9 | OWNER | VQ#25, TL#10 §7 |
| E2 | Indian painting treatments (at most one per episode, ≤25% of runtime, payoff always detailed chalk): Kalamkari-line chalk for tale-within-tale; Mewar continuous narration for journeys; motion-comic panels for confrontations; cinematic impact frames | Narrative layers become legible | prompt add-ons in `styles.py`; `reveal: ghost`; long-tilt move; panel compositor in `render()` | yes | A5, B11; 4-style × 4-image Z-Image test (about 30 min) | M* | M | dilutes the brand if overused; base-model quality on these styles untested | owner judges the test stills; lint rule 8 | A5, B11 | OWNER + G1 | VQ#22–23 §3.3, TL §7 |
| E3 | LTX-2.3 int8 `--low-ram` hero-shot test: one 4 s first/last-frame clip from a chalk still | A possible "wow" shot | separate venv (ltx-2-mlx, MIT); clip inserted in step_render | yes (LTX-2 Community, free under $10M revenue; **read the licence in full first**, it was read by grep only) | about 26 GB disk plus a Gemma text encoder; 10–15+ min per clip on 16 GB | M–L | unknown | style drift into photoreal; swap pressure | `time -l`, swap check; owner judges one shot | B12, B13 | OWNER | VQ#27, TL#15 §2.6 |
| E4 | Music: ACE-Step 1.5 (MIT) and Magenta RealTime 2 small (Apache-2.0 code, CC-BY-4.0 weights) beds, 3 beds × 2 moods, 30–40 s, looped under the numpy tanpura; leitmotif library on the existing raga engine (Sa = 146.83 Hz constant) | Richer timbres; recognisable characters by ear. The audit ranks this low while duration and consistency are the bottleneck | offline generation passed via `--music` (`studio.py:788`); `chalk.music` `phrases` + `music.leitmotif` | yes | ACE-Step 8–12 GB RAM with the 0.6B LM (skip XL); run alone with progress updates | S each (test) | L–M | Indian timbres unproven; motifs clash with narration | blind owner A/B in 3 moods; pass = preferred in ≥2 of 3, no clash with Sa, no vocals or artifacts; peak RSS logged | A6, B10 | OWNER | VQ#21 #24 §4.4 §4.7, TL#11–12, AUD §2.10 |
| E5 | Z-Image Turbo Fun ControlNet Union 2.1 (canny, pose, depth) for layout consistency between scenes and thumbnails | Consistent composition | `studio.py` step_images (mflux flag) | yes (Apache-2.0) | about 1–3 GB disk (not measured) | S | M | none known | one canny-conditioned regeneration of an existing scene; disk and time measured | A7 | OWNER | TL#9 §7 |
| E6 | New languages, **Tamil next**, then Marathi or Bengali, as "season-only" versions (one Kanda arc or the 10 strongest episodes). Add one only when: each current language has ≥5 episodes of comparable data; a voice passes `speaker_consistency` and a native speaker approves pronunciation (Maya 2 coverage of new languages is untested); a native reviewer is available for G1 and G2; a regional-tradition brief exists (Kamban for Tamil, with scholarly not devotional-only framing); capacity does not slip G2; measure competition first with `pipeline research <ID> --langs …` | Speaker base and platform tool support; Tamil has both Meta translation and YouTube dubbing, so a native version must be clearly better | `profiles/languages/ta.json`; `profiles/voices.json`; `numwords.py` or the digits lint for the new script; `chalk.py` `SCRIPT_FONTS` (OFL Tamil font) | yes | O9-style native reviewer; D4 data | M* per language | M | pronunciation and cultural framing errors | voice QA pass + native sign-off before G1; triggers checklist all true | D4, D7, A2 | OWNER | GRO §0.6 §6.2 §6.4 |
| E7 | Account split triggers: split a language only when **≥2 of 6** triggers hold for **≥5 consecutive episodes** (self-sufficiency, cannibalisation, audience separation, comment confusion, policy pressure such as a YPP rejection citing inauthentic content, capacity), with owner approval; never during the YPP application window; Instagram candidates first are gu and te | Thresholds are per channel, so splitting now divides progress by four | weekly report section in `data/reports/`; owner decision | yes | D4 data, D2 | S* (monitoring) | M | splitting too early resets every threshold | the weekly report lists each trigger with its evidence file | D4 | OWNER | GRO §2.2 §2.5 |
| E8 | Multi-language audio tracks: one unlisted test episode with a language-neutral visual master (no burned-in captions, Sanskrit/Devanagari shloka card), per-language subtitle tracks and length-matched tracks | Would consolidate views on one video and remove the four-copies issue, at the cost of the approved caption style | `studio.py` render variant; YouTube Studio | yes | advanced features; owner approval (style change) | M* | unknown | whether secondary-language viewers get it recommended is unverified | one unlisted test; owner decides | O1, D5 | OWNER | GRO §2.3 |
| E9 | Forced alignment for Indic captions with a **non-NC** aligner (not the MMS checkpoints, which are CC-BY-NC) | Caption timing is ASR timestamps redistributed by character count | `studio.py` `align_words` | yes | a commercially licensed aligner | M* | L–M | licence trap | onset error against hand-marked words on 2 scenes | none | SAFE | VQ#26, AUD §2.11 |
| E10 | Manim Community (MIT) maps, lineage trees and timelines as transparent overlays | Explainer beats (journeys, genealogy) | composite in step_render | yes | pip plus Cairo/Pango via brew | M | L–M (story); M (history) | busy frames on a phone | one map beat on a scratch render; owner A/B | B11 | OWNER | TL#13 |

---

## 6. Dependency graph and the first two weeks

### 6.1 Dependency graph

```
OWNER DECISIONS                 PHASE A                      PHASE B                      PHASE C / D / E
───────────────                 ───────                      ───────                      ───────────────
O1 35–55 s ──────────────► A1 skill/agents ─► A2 lint ─────► B11 shot grammar ──► B12 parallax ─► B13 motion ─► E3 LTX test
                                   │            │  ▲              ▲                                   
                                   ▼            │  │              │                                   
                              A13 G1 rules ─────┘  │         A5 reveal ◄── O5 frame-0 style ──► A4 frame 0
                                                   │
A3 final QA ───────────────► A10 QA gate G2 ──► B4 QA scoring ──► B1 agents 5+1 ◄── O10
                                                   ▲
O4 approval redesign ──────► A11 hash-bound gates ─┼─► B7 G3 hook ──► C2 review depth
                                   │               │                     ▲
                                   ├───────────────┴─► B2 publish-queue  │
                                   │                                     │
O6 Telegram ─► C0 setup ───────────┴──────────────► C1 bot MVP ──────────┘──► C3 dashboard ◄── O7 licence
                                                                         
B6 hash caches ─► B5 QA compute        B3 takes ─► C2                    
A6 loudnorm ─► B10 SFX/ducking ─► E4 music        B9 SFX library ─► B8 audio-mix skill
A7 positive prompts ─► E5 ControlNet
A8 {character} ─► A9 klein test ─► E1 LoRAs
                         
O11 enable API ─► D1 ─► D2 windows ─► D3 IG insights
                         │
B14 timeline.json ───────┼─► D4 features + experiments ─► D10 per-language openings
B2 feature logging ──────┘          │
                                    ├─► E6 Tamil (also needs D7 ◄── O9)
                                    ├─► E7 split triggers
                                    └─► C4 analytics push (also needs C1)

O2 synthetic + O3 fonts ─► D6 compliance (needs A3 glyph check) ─► D9 fan-funding readiness
D5 serial shows (O11) ─► D8 Kanda compilations (also needs A1)
O8 voice line ─► A12 doc reconciliation
```

### 6.2 Suggested order for the first two weeks

The days below are a sequence, not a commitment; the owner's availability for decisions and A/B sessions sets the pace. Production follows the existing rule of one episode per day, next only on request.

| Day | Work | Who | Items |
|---|---|---|---|
| 1 | Owner decision session on O1–O11 (§0.2) | Owner | O1–O11 |
| 1–2 | Duration target in the skill and agents; `pipeline lint`; final QA duration, overflow and glyph checks; doc reconciliation | Claude | A1, A2, A3, A12 |
| 2–3 | Hash-bound approval records, `reject`, interactive `approve`; QA gating of G2; fail-closed G3 hook (owner applies `settings.json`) | Claude, owner installs hook | A11, A10, B7 |
| 3 | Two-pass loudnorm; positive prompts and border auto-crop; `{character}` tokens; `timeline.json` | Claude | A6, A7, A8, B14 |
| 3 | Enable the Analytics API; Made for Kids = No; decide on `synthetic`; start the serial shows | Owner | D1, D5, D6 (metadata part) |
| 4 | One bundled owner A/B session on C0005-en from existing assets: frame 0, reveal modes (VQ suggests bundling VQ#7–11 and #13; B11/B10 can join this session or the next) | Claude prepares, owner judges | A4, A5 (+ B10, B11 if ready) |
| 4–5 | Analytics window fixes and daily job; `features`/`experiments` tables; register experiment 1 if O1 chose option (b) | Claude | D2, D4 |
| 5 | **First episode under Phase A rules**: lint passes at G1, final QA under 60 s, QA-gated G2, platform-bound G3 | Claude + owner gates | A1–A13 in use |
| 6 | Telegram setup and Remote Control | Owner | C0 |
| 6–7 | Telegram bot MVP (6–8 h) | Claude | C1 |
| 8 | Content-hash caches; QA transcript reuse; generalized takes and Malini recalibration | Claude | B6, B5, B3 |
| 9 | FLUX.2 klein measurement run (solo, nothing else loaded, progress updates); DINOv2 similarity on the 4 test scenes | Claude, owner reviews | A9 |
| 10 | Agent consolidation; publish-queue and Instagram stage keys; Instagram insights | Claude | B1, B2, D3 |
| 10 | Font side-by-side (OFL vs current) if O3 is "switch" | Claude prepares, owner judges | D6 (fonts) |
| 11–14 | QA scoring system and visual QA; SFX library with `licenses.csv`; `audio-mix` skill; Telegram review depth if the MVP is in daily use | Claude | B4, B9, B8, C2 |

---

## 7. Resource estimates

Free disk at research time: about 92 GB (TL). "Unmeasured" means no source has an M5 Air figure; measure with `/usr/bin/time -l`, alone, before adopting.

| Component | Disk | RAM peak | Time | Status | Source |
|---|---|---|---|---|---|
| Z-Image Turbo 4-bit (current) | 5.5 GB | 8.3 GB | 63 → about 108 s per image at 768×1344, 9 steps (thermal) | measured on the M5 | TL §2, AUD §1 |
| Maya 2 Malini (current) | not stated | not stated | about 1× real time | measured | AUD §1 |
| Kokoro (current) | not stated | not stated | under 1 s per scene | measured | AUD §1 |
| Render (current) | — | not stated | median 116 s; C0005-en 2,460 frames in 49 s | measured | AUD §1 |
| QA (current) | — | not stated | median 115 s, p90 1,000 s, max 3,564 s | measured | AUD §1 |
| FLUX.2 klein 4B | about 4 GB (4-bit); VQ budgets 4–8 GB | **unmeasured** (conflicting 8–13 GB VRAM claims) | M1 Max: 1024² in 21–32 s; edit with reference 52–53 s; Air slower | unmeasured on M5 | VQ#18, TL#3 §6 |
| BiRefNet | about 1 GB | not stated | seconds per scene, not timed | unmeasured | TL#4 |
| SAM 2.1 small/tiny | not stated | not stated | not timed | unmeasured | TL#4 |
| Depth Anything V2 Small | about 100 MB (25M params) | not stated | not timed | unmeasured | TL#5 |
| DINOv2 (drift flag) | not stated | not stated | not timed | unmeasured | AUD §2.7 |
| Tesseract | not stated | not stated | not timed | unmeasured | VQ#19 |
| Z-Image ControlNet Union 2.1 | about 1–3 GB | not stated | not timed | unmeasured | TL#9 |
| Chalk LoRA training (`mflux-train`) | not stated | **unmeasured** on Apple Silicon; CUDA reference about 10–10.8 GB | overnight pilot | unmeasured | TL#10 |
| ACE-Step 1.5 (2B turbo + 0.6B LM) | not stated | 8–12 GB (README) | no Mac timings | unmeasured | TL#11 |
| Magenta RealTime 2 small (230M) | small, not stated | not stated | real time on Apple Silicon including the Air (claimed) | unmeasured | TL#12 |
| LTX-2.3 int8 `--low-ram` | about 26 GB plus a Gemma text encoder | "16 GB with `--low-ram`" (claimed) | about 15 min per 4 s on a 16 GB M1 | unmeasured on M5 | TL#15 |
| Sonniss GDC 2026 bundle | 7.47 GB | — | — | stated | TL#7 |
| Telegram bot daemon | negligible | under 60 MB | proxy: 150 MB → 11.1 MB in 4.4 s; Opus scene clip about 25 KB | measured | MOB §2 §4.2 §7 |
| Manim Community | not stated | not stated | not timed | unmeasured | TL#13 |

**Worst-case new disk if every Phase B–E model and library is adopted:** about 4–8 (klein) + 1 (BiRefNet) + 0.1 (DA-V2 S) + 1–3 (ControlNet) + 7.47 (Sonniss) + 26 (LTX-2.3, plus an unsized text encoder) ≈ 40–46 GB, with ACE-Step, Magenta, SAM 2.1, DINOv2, Tesseract and Manim unsized. That would take roughly half of the free disk, so delete LTX-2.3 after its single test.

**Memory rule:** every model above runs alone. The bot's `data/heavy.lock` (C2) serializes produce, takes, QA and regenerations (MOB §7).

---

## 8. What we will explicitly not do, and why

| Not doing | Why | Source |
|---|---|---|
| Auto-publish, or let the bot or Claude record G3 or call `publish` without the typed two-step code and a hash match; approve all languages by default from the phone | Human gates are non-negotiable | CLAUDE.md, MOB §6.4 §10 |
| Regenerate, replace or re-upload any published episode (C0001–C0005), including to apply new fonts, durations or disclosure | Constraint; A/B tests render to scratch only | VQ header and §6 |
| Speed the voice up to fit a duration | English is already at the brisk end of audiobook pace; cut words instead | VQ §2.4 |
| Recite full Sanskrit verses in the main Shorts while over budget | A full anuṣṭubh costs about 6–9 s in Hindi; keep it for a separate "Shloka" Short | VQ §2.4, AUD §2.9 |
| Adopt video diffusion (beyond one LTX-2.3 test); Wan 14B, LTX-2.5, FramePack, HunyuanVideo | 10–60+ min per clip on 16 GB, 47–120 GB packs, territory-restricted licences, photoreal drift | TL §2.6, VQ §3.6 |
| Identity adapters: IP-Adapter, InstantID, PuLID, InfiniteYou, LivePortrait as shipped | Non-commercial weights or insightface models; built for photoreal faces | TL §2.2 §5, VQ §3.4 |
| Non-commercial or research models: FLUX.1 dev family, FLUX.2 klein 9B and dev, Depth Pro, ml-sharp, DA-V2/V3 Base/Large/Giant, Qwen-Image 2.1, Anima, FIBO 2, RMBG-2.0, 3D Ken Burns, MusicGen, AudioGen, AudioLDM2, Tango, TangoFlux, MMAudio, YuE2, MMS aligner checkpoints, IndicF5, macOS `say` voices | Licences forbid commercial use | TL §5 |
| Revenue-capped or revocable licences by default: Stable Audio 3, SD 3.5, FLUX 3 Klein, Krea 2, CogVideoX-5B | Under-$1M or under-$5M caps, revocable terms or registration; only if the owner explicitly accepts a cap | TL §5 |
| Import DepthFlow (AGPL) or pedalboard (GPL); use Demucs outputs in published audio | Copyleft linking in a public repo; Demucs weights licence "not clear" | TL §3.3 §5 |
| Pixabay music; YouTube Audio Library tracks in Instagram Reels; BBC SFX; Incompetech; any licensed or trending track on a Short | Content ID exposure, off-platform use not covered, non-commercial, attribution; a claim on a Short over 1 min blocks it | TL §3.2, GRO §3.2 §5.7 |
| Switch caption engines (pycaps, captacity) | Would regress Indic shaping | VQ §5.3, TL §2.5 |
| Upscalers, frame interpolation, LUT packs, anime models, Remotion or other Node stacks, ComfyUI or Draw Things in production | Low value against the chalk texture, against `restrict_palette`, a second runtime, or licence terms (Remotion) | TL §2.1 §2.5, VQ §3.6 |
| Rigged puppets (Spine, Live2D, Inochi2D, Synfig, OpenToonz, AnimatedDrawings) | Paid, manual rigging per character, or archived | TL §2.4 |
| Install external Claude Code plugins, community skills or MCP servers (hyperframes, remotion skills, YouTube upload MCPs, ComfyUI MCPs, ffmpeg MCPs, Blender MCP and its star-farmed look-alikes) | Paid, redundant, add context every turn, can bypass G3, or are malware lures | TL §4.2–4.6 |
| Use the paid or credit-based connectors visible in this environment (xelta, MCP-H/Higgsfield, OpenSEO, Ubersuggest) | Zero-cost rule; they would bypass the local pipeline | TL §4.6 |
| Tailscale Funnel, Cloudflare quick tunnels or port-forwarding for a dashboard; Telegram webhooks; the Claude Code Channels plugin on the studio bot's token; GitHub Issues approvals on the public repo; a shell or file-path verb in the bot; ntfy or Discord as the main channel | Public exposure, inbound endpoints, split update consumers, leaks of unpublished material, or no advantage over Telegram | MOB §3.1 §10 |
| Paid add-ons: Tailscale paid plans, ntfy Pro, a domain for Cloudflare Access, Meta Verified | Zero-cost rule | MOB §10, GRO §4 |
| Per-episode market research and topic scoring | For a serialized epic, topic order is fixed by canon; research belongs once per arc (series-planner) | AUD §2.1 §2.3 |
| Grow the language profiles further on judgement alone | No audience data exists until analytics works | AUD §2.2 |
| Make any claim from fewer than 6 variants per arm per language, compare raw views across languages, or change slots during a content experiment | Small samples and confounding would mislead | AUD §20.2 |
| Split into per-language accounts now, or during a YPP application window | Thresholds are per channel; the §2.5 triggers are not met | GRO §0.1 §2.5 |
| Add a fifth language before each current language has ≥5 episodes of comparable data | Scaling rule | GRO §0.6 §6.2 |
| Engagement bait, bought views or subscribers, Made for Kids = Yes, graphic violence in thumbnails or first seconds, prints of single frames marketed as exclusive art | Monetization blockers; thin copyright in raw AI frames | GRO §3.3 §5.3 §5.7 |
| Invent analytics, forecasts or audience data, in docs, reports or bot messages | No-fabrication rule | CLAUDE.md, GRO scope, MOB §5 |

---

## 9. Success metrics per phase

All metrics are measured from repo artifacts (`data/studio.db`, `qa.json`, manifests, ffprobe), not estimated. Platform outcomes are tracked, never forecast.

| Phase | Metric | Target | Measured by |
|---|---|---|---|
| A | Share of new variants under 60.0 s | 100% | ffprobe in final QA |
| A | Share of new variants inside 35–55 s | 100% if O1 = adopt; per arm if O1 = experiment | final QA warn count |
| A | Lint estimate vs rendered duration | within ±3 s per language | lint report vs ffprobe |
| A | Variants reaching G2 with an auto-reject failure or an unwaived warn | 0 | `qa_reports` joined to `gate:final` |
| A | Frame 0 non-board pixel share (if O5 adopts) | ≥ about 5% | final QA first-frame metric |
| A | First word onset | ≤0.3 s | word timestamps |
| A | Integrated loudness | −14 ±0.5 LUFS, TP ≤ −1.0 dBFS | `check_loudness` |
| A | Manual border crops on new episodes | 0 | handoff notes and regeneration log |
| A | G3 records without platform, time, `publish.json` hash and mp4 hash | 0 | manifest audit |
| A | Uploads whose hash differs from the QA'd file | 0 | publish refusal log |
| B | Active agents | 5 (+1 dormant) | `.claude/agents/` |
| B | QA wall time per language | below the baseline (median 115 s, p90 1,000 s) | `runs` table |
| B | Stale-asset incidents after a script edit | 0 | regenerations not explained by a hash change |
| B | `uploadLimitExceeded` errors | 0 | queue log |
| B | SFX files used without a `licenses.csv` row | 0 | lint |
| B | Every QA family scored with a recorded pass or fail | 100% of new variants | `qa.json` |
| B | Regenerations per episode (creative-director signal) | recorded per episode; trend down | `runs` table |
| B | G3 commands that bypass the hook | 0 (hook tested to exit 2, timeout blocks) | hook test |
| C | MVP acceptance (push on render, proxy, G2, G3 typed code, audit shows actor, channel, nonce, sha256) | all five pass | `pipeline audit C000X` |
| C | Remote gate actions missing actor, channel, nonce or sha256 | 0 | `remote_actions`, `decisions` |
| C | G3 approvals recorded by Claude | 0 | `decisions.channel`/`actor` |
| C | Heavy-job collisions | 0 | `heavy.lock` log |
| D | Snapshots with non-403 Analytics totals | 100% of new snapshots | `analytics_snapshots` |
| D | Window labels within ±12 h of nominal age | 100% | `age_h` |
| D | Variants with a complete `features` row | 100% of new variants | `features` table |
| D | Instagram Reels with insights snapshots | 100% of new Reels | `analytics_snapshots` `platform='instagram'` |
| D | Experiment claims made below 6 variants per arm per language | 0 | `recommendations` |
| D | GRO Phase 0 compliance checklist (synthetic, MFK, fonts, brand, serial shows, auto-dub review, About page) | all closed | owner checklist |
| D | Serial Shorts show per language | 4 of 4 | YouTube Studio |
| D | Thresholds (500 IG followers; fan-funding tier) | tracked weekly, never forecast | Studio, Instagram dashboard |
| E | Each test (klein, LoRA, ControlNet, music, LTX) has measured time, peak RSS and an owner verdict on file | 100% | test logs in `data/reports/` |
| E | New language launched with every scaling-rule condition true | 100% | triggers checklist |
| E | Account split decided with ≥2 triggers for ≥5 consecutive episodes, with evidence files | 100% of split decisions | weekly report |
