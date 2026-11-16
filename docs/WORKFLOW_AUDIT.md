# shorts-studio workflow audit

Audit date: 2026-11-16. Scope: the code, configuration and content as they stand at commit `ef038fe` plus the uncommitted working tree. The audit was read-only: no code, manifests, approvals or content were changed, and nothing was generated or published.

**Labels used throughout**
- **[V]** verified fact, with a file, line, command or database query you can re-run.
- **[R]** recommendation or judgement.
- **Priority:** **C** Critical, **H** High, **M** Medium, **L** Low.

Measurements came from `ffprobe` and `ffmpeg ebur128` on the final mp4s, read-only `sqlite3 -readonly data/studio.db` queries (the `runs`, `qa_reports`, `publications`, `decisions`, `hooks` and `analytics_snapshots` tables), the `produce.log` files, and the WAV headers in `content/C0005/*/audio/`.

---

## 0. Headline findings

| # | P | Finding |
|---|---|---|
| 1 | C | [V] **All 20 rendered videos run 74.8 to 111.2 s, so none is under 60 s and none meets the 35–55 s target.** The 60–90 s target is written into `storytelling/SKILL.md` (description and checklist), `scriptwriter.md` step 3, PROJECT_CONTEXT §9 ("60–95 s") and EP05_HANDOFF §4 ("75–95 s"). QA enforces only `max_seconds: 180` (`pipeline/qa.py:11`), so nothing catches it. |
| 2 | H | [V] **A G3 approval is not tied to a platform, a time or the metadata.** `cmd_approve` overwrites the single `gate:publish` entry (`pipeline/__main__.py:123`), and `require()` checks only the status and the language list (`:43-47`). An Instagram G3 has already overwritten the YouTube G3 in C0001 and C0002 (see their `manifest.json` files). `publish --at` and `data/upload_queue.sh` (`now` → now+15 min) can upload at a time the owner never approved. |
| 3 | H | [V] **Publishing never checks QA.** `cmd_publish` and `cmd_approve final` never read the `video_qa` verdict. 28 of the 40 QA reports are `warn` or `fail`, and `warn` videos have shipped. For example, C0005-te has a scene-12 CER of 0.26 and two captions 976/984 px wide. |
| 4 | H | [V] **Instagram reposted the Ep01 Hindi file with the known speaker drift** (PROJECT_CONTEXT §21: 38 of 47 phrases off-voice). See `content/C0001/hi/published.json`, which points at `out/.../valmiki-ramayana-episode-01-hindi.mp4`. Nothing re-runs QA on legacy files before a new platform upload. |
| 5 | H | [V] **The image negative prompt does nothing.** mflux forces guidance to 0.0 for Z-Image Turbo (`mflux/models/z_image/cli/z_image_turbo_generate.py:23`), so `styles.py` `negative` and `--negative-prompt` (`studio.py:316`) have no effect. The workaround of writing "no wings, no horns, not a dragon…" into the *positive* prompt (`content/C0005/en/script.json` scene 1) can prime exactly those concepts. |
| 6 | H | [V] **Character consistency is text only.** No code reads `profiles/characters/ramayana.json`, and `studio.py:306` appends only `script["character"]`. Bible prompts are pasted into `visual` by hand, with no reference image and no automated similarity check. Drift (frontal Rama, a four-armed Tataka, borders, gargoyles) has been caught by eye and fixed by regenerating. |
| 7 | H | [V] **gu and te voices are "approved" without the native-speaker QA that the voice policy requires** (`profiles/voices.json` `_policy`). The language profiles still say `"draft — needs native-speaker review"`, and ASR CER is unreliable for gu/te (normalization is tuned for Hindi, `qa.py:79`). |
| 8 | H | [V] **Analytics is blind.** There are 6 snapshots, all labelled `initial`, and all have `totals` = HTTP 403 because the Analytics API is not enabled. Instagram has no insights collection (`analytics.due` filters `platform='youtube'`, `analytics.py:63`). There are 0 recommendations. There are no `experiments` or `features` tables, so no learning is possible yet. |
| 9 | H | [V] **The snapshot windows are mislabelled.** `due()` takes the first *missing* label even when it is days late (`analytics.py:72-75`), and every query is cumulative from publish to today (`:36-38`). A "24h" row captured on day 5 holds 5 days of data. `schedule.recommend` then ranks slots on raw 48 h views, ignoring language, episode and decay (`schedule.py:27`). |
| 10 | M | [V] **Caches are keyed on whether a file exists, not on its content.** That applies to audio (`studio.py:224`), images (`:299-303`) and shared images (`__main__.py:147`). Editing `narration` or `visual` silently reuses stale assets unless someone deletes the files by hand. That manual step appears in the handoff gotchas. |
| 11 | M | [V] **QA is the largest compute sink.** `video_qa` totals 293 min over 38 runs, against 109 min for images and 103 min for render. Runs take up to 59 min (C0003-hi/te). QA re-runs Whisper on every scene (`qa.py:95-101`), although render already transcribed every scene for word timing (`studio.py:580-622`, cached in `NN.words.json`). |
| 12 | M | [V] **Frame 0 of every chalk video is an empty board.** `chalk.plan` starts scene 1 with draw progress 0 (`chalk.py:241`, checked by extracting frame 0 of C0005-en). The hook image is only fully visible after about 1.6 s, on the platform's most valuable frame. |
| 13 | M | [V] **The agent layer is larger than the work it does.** For C0003–C0005, `strategy.md` has no score table (7–19 lines), `research/` has no evidence file for C0004/C0005, the `research` table holds 3 rows (C0002 only), the `hooks` table stops after C0003, and `recommendations` is empty. Five of the 10 agents are effectively dormant or redundant (§18). |
| 14 | M | [V] **Orchestration has leaked into ad-hoc shell scripts outside the pipeline:** `data/upload_queue.sh`, `data/logs/fix-c0002.sh`, `fix-c0003.sh` and `release-c0003.sh`. The upload queue hit `uploadLimitExceeded` twice (`data/upload_queue.log`), because 4 languages a day plus a backlog exceed the channel's daily upload allowance. |
| 15 | M | [V] **The voice-take tooling and agent docs are stale for Maya 2.** `pipeline takes` refuses anything but Veena (`__main__.py:313`, `takes.py:14-20`). The best-of-N loop actually used for Malini (pitch outlier plus window/scene similarity) is described only in prose (EP05_HANDOFF §5). `language-qa.md` still prescribes Veena takes. `progress.py:46` estimates Maya 2 with the Kokoro rate. |

---

## 1. Current video facts [V]

All files are H.264 (VideoToolbox) 1080×1920 at 30/1 fps, about 12.09–12.16 Mb/s video and 12.25–12.35 Mb/s overall, with AAC 48 kHz at 181–194 kb/s. Every one passes the format check.

| Video | Duration s | Over 60 s | Video | Duration s |
|---|---|---|---|---|
| C0001-en (legacy `out/`) | 74.8 | yes | C0001-hi (legacy, drift) | 94.0 |
| C0001-gu | 101.6 | yes | C0001-te | 111.2 |
| C0002-en | 77.5 | yes | C0002-hi | 101.6 |
| C0002-gu | 104.0 | yes | C0002-te | 105.3 |
| C0003-en | 89.5 | yes | C0003-hi | 99.3 |
| C0003-gu | 108.5 | yes | C0003-te | 109.1 |
| C0004-en | 74.8 | yes | C0004-hi | 83.2 |
| C0004-gu | 93.3 | yes | C0004-te | 99.5 |
| C0005-en | 82.0 | yes | C0005-hi | 97.8 |
| C0005-gu | 107.5 | yes | C0005-te | 111.2 |

- **Ranges by language:** en 74.8–89.5 · hi 83.2–101.6 · gu 93.3–108.5 · te 99.5–111.2. **20 of 20 are over 60 s; 0 of 20 are inside 35–55 s.** Shorts accept up to 3 minutes, so these still publish as Shorts, but they miss the owner's target by 20–56 s.
- **Loudness (ebur128 on 9 finals: C0004 ×4, C0005 ×4, C0001-gu):** integrated −15.2 to −14.7 LUFS, true peak −1.5 to −1.4 dBFS, LRA 1.9–2.8 LU. All are inside QA (−16.5…−13). The −14 target ends 0.7–1.2 LU low because single-pass `loudnorm=I=-14:TP=-1.5` runs in dynamic mode (`studio.py:705`). That is harmless.

**Where the time goes in C0005** (scene WAV lengths):

| Lang | Words | Voice s | Rate | Video s |
|---|---|---|---|---|
| en | 214 | 76.1 | 2.81 w/s | 82.0 |
| hi | 257 | 91.8 | 2.80 w/s | 97.8 |
| te | 174 | 105.1 | 1.66 w/s | 111.2 |

- Fixed overhead is about 6–7 s: 0.35 s lead (`studio.py:632`), per-scene `pause` values totalling 4.8 s, and a 0.8 s tail (`:642`).
- Duration is driven by script length (13 scenes, 155–257 words), not by rendering.

**Scenes and images [V]:** 12–13 scenes per video. One scene per episode (two in C0001) is a verse text card, so each episode needs 11–12 diffusion images, generated once in the primary language and copied to the other languages (`share_images`, `__main__.py:136-148`).

**Per-stage timing [V]**

| Step | Measured |
|---|---|
| Z-Image 768×1344, 9 steps | 63 s rising to about 108 s per image (thermal). C0005-en: 12 images in 21.5 min (`content/C0005/en/produce.log`) |
| Kokoro | under 1 s per scene |
| Maya 2 | about 1× real time (C0005-te: 13 scenes in 93 s) |
| Render | median 116 s, p90 367 s. C0005-en: 2,460 frames in 49 s plus 6 s preparation |
| QA | median 115 s, p90 1,000 s, max 3,564 s |
| C0005, G1 → G2 | 78 min wall clock for 4 languages, including 3 voice-scene fixes and 1 image fix (manifest timestamps 10:58 → 12:16) |

---

## 2. Stage-by-stage audit

Each stage lists what **exists**, then its findings.

### 2.1 Research and trends
- **Exists:**
  - `pipeline/research.py`: `yt_trending` (:68), `yt_competition` (:86), `wiki_langlinks/pageviews/interest` (:117-155), `yt_suggestions` (:157, unofficial autocomplete) and `topic_report` (:169), with a cache (6–24 h, `cached` :18) and retries.
  - The `trend-researcher` agent, outlier method via vendored `yt-viral/swipe.py`.
- **Works:** the evidence is real and cached, and the no-fabrication rule is respected. The C0002 `research/evidence-*.json` holds 3 compared candidates.
- **Findings:**
  - **M [V]** Real use stopped after the pilot. C0003 has one evidence file; C0004 and C0005 have none (only `report.md`, which is textual verse verification). There is one trending report (`data/reports/trending-IN-2026-11-15.md`).
  - **M [R]** For a serialized epic, topic choice is fixed by canon order. Market research belongs **once per arc** (which arc next, whether to start a second series, which languages to add), not once per episode. Per-episode "research" is really *source verification*, which is scriptwriting work.
  - **L [R]** Add the YouTube `search.list` competitor snapshot as a scheduled weekly job (Python, ~200 units/language) that writes `data/reports/competition-<date>.md`, so research is available without an agent run.
  - **L [V]** Instagram and TikTok trends are not measurable for free. This is correctly labelled "not measured".

### 2.2 Audience
- **Exists:** 10 profiles in `profiles/languages/*.json` (audience, traditions, localization guidance, `style_overrides`, slot hypotheses, festivals), the `audience-localizer` agent, and `content/<ID>/audience.md`.
- **Works:** the per-language caption fonts and `caption_max_chars` (en/hi 24, gu 22, te 20) are concrete and used by the renderer.
- **Findings:**
  - **H [V]** gu and te profiles are `draft — needs native-speaker review`, yet those languages are in production and published.
  - **M [V]** `audience.md` for C0005 is 26 lines. Most of it is stable per-language guidance that belongs in the profile, not in each episode.
  - **M [R]** Fold per-episode audience notes into the scriptwriter's per-language pass. Keep profile maintenance as an occasional task that is triggered by evidence (analytics by country or language, native review).
  - **[R]** No audience data is possible until analytics works (§2.16). Do not grow the profiles further on judgement alone.

### 2.3 Topic scoring
- **Exists:** a 10-factor weighted rubric in `content-strategist.md`.
- **Findings:**
  - **M [V]** It was used once: the C0002 `strategy.md` has a 13-row table. C0003–C0005 have none.
  - **M [R]** For a series, replace the per-episode slate with a **series bible + episode map** (`content/series/ramayana.md`): canonical sargas per episode, teaser chain, depiction risks. Re-score only at arc boundaries.
  - **L [R]** Several factors are judgement with no data behind them yet ("expected retention" needs ≥5 analysed videos, and none exist). Collapse to 4 factors until data exists: storytelling potential, accuracy risk, production risk, series fit.

### 2.4 Story and hooks
- **Exists:**
  - `storytelling` skill: principles, 7 templates, a 6-criterion hook rubric and the script schema.
  - Vendored `yt-script/hookscore.py` as a second opinion.
  - `hooks.json` per language: C0005-en has 6 hooks, selected 29/30 with reasoning.
  - The `hooks` DB table (24 rows, C0002–C0003 only).
- **Works:** hooks are concrete, sourced and pay off the previous teaser. Open loops are explicit in `strategy.md`. Accuracy discipline is strong (verse table with book.chapter.verse).
- **Findings:**
  - **C [V]** The skill encodes 60–90 s and 9–14 scenes (`storytelling/SKILL.md` description and checklist), which guarantees overlong videos (§1).
  - **M [V]** Nothing writes to the `hooks` table any more: it is only populated by agents by hand, and there is no `INSERT INTO hooks` in the code. Hook text is not linked to performance.
  - **M [R]** Make hook data structured and automatic: a `pipeline hooks <ID>` command that loads `hooks.json` into the DB, so the hook type (question, claim, number, in-medias-res…) becomes an experiment variable.
  - **M [R]** The rubric self-scores ("29/30") give little discrimination. Have the *independent reviewer* (§18) score the hooks blind, then show the owner the top 2 at G1.

### 2.5 Scripting and multilingual
- **Exists:**
  - `script.json` per language with the same scene count and shared `visual` fields; narration written fresh per language.
  - `pipeline/numwords.py`, which handles en/hi/mr numbers only (`:14-37`).
  - Verse cards rendered in each language's script (`chalk.text_scene`, `SCRIPT_FONTS` `chalk.py:19`).
- **Works:** original-language writing, verse verification, and one image set shared across 4 languages (large compute saving).
- **Findings:**
  - **C [R]** Add a **deterministic duration lint** before G1: `pipeline lint <ID>`. It computes the estimated seconds for each language from the measured words per second of that voice (en 2.81, hi 2.80, gu ≈2.3, te 1.66 w/s) plus pauses and 1.15 s of lead and tail. It **blocks G1 above 58 s** and warns outside 35–55.
  - **[R] Word budgets for a 50 s video** (≈45 s of speech, pauses trimmed to ≈0.25 s × 9): en ≈125 words, hi ≈125, gu ≈100, te ≈75. Use **9–10 scenes** instead of 13.
  - **H [V]** Equal scene count across languages is enforced only by convention. Telugu fits the same 13 visual beats into 1.66 w/s, which makes te the longest language every time (99.5–111.2 s).
  - **[R]** Allow a language to *merge* adjacent scenes (two visuals over one sentence) instead of padding words. Budget by seconds per scene, not by sentences.
  - **M [V]** gu/te narration must avoid digits by hand (handoff §4). **[R]** Extend `numwords` or lint for digits in non-supported languages.
  - **M [V]** gu/te G1 was "approved in advance … follow approved en/hi scene by scene" (the `decisions` table for C0001–C0004 at 12:23:53, before those scripts existed). **[R]** A gate must approve a concrete artifact. Store the hash of each `script.json` in the gate record.

### 2.6 Creative direction and visual planning
- **Exists:**
  - The `creative-director` agent.
  - The `styles.py` chalk preset (`:46-67`): prompt prefix, negative, 768×1344, `chalkdraw` motion, erase transition, raga music, caption styling.
  - Depiction rules in `profiles/characters/ramayana.json` `rules` (deities symbolic, Ravana symbolic, no Mughal domes, safe zones).
- **Works:** a coherent, distinctive and approved identity. The rules capture real lessons from Ep03–Ep04.
- **Findings:**
  - **H [V]** The negative prompt is ignored (headline finding 5). The prompts have bloated with negations; C0005 scene 1's `visual` is about 110 words, a third of them negations.
  - **[R]** Rewrite the prompts positively ("a silhouette of a rakshasi with two arms and flowing hair, temple-mural style"). Rely on the reference images (§2.7) and an automated image check (§19) instead of negative words.
  - **M [V]** The "full-bleed, no border" instruction is in every prompt, and borders still appear (handoff gotchas: crop `(24,42,744,1302)`). **[R]** Detect borders automatically (edge-band luminance) and crop deterministically in `step_images`. This needs no LLM and no regeneration.
  - **L [R]** Store a per-scene `shot` field (wide, medium, close, silhouette, text) and lint for variety. Today composition variety is left to prose.

### 2.7 Character consistency
- **Exists:** 15 text entries in `ramayana.json` (`rama_teen`, `lakshmana_teen`, `vishvamitra`, `tataka`…), with the rule "Reuse prompts verbatim".
- **Findings:**
  - **H [V]** There is no programmatic link from the bible to the prompts (no reference in `studio.py`, `chalk.py` or `pipeline/`), no reference images, and no consistency metric. The `video-qa` contact sheet is the only check.
  - **H [R]** Two steps:
    1. A character token in `visual` (`{rama_teen}`) expanded from the bible by `step_images`. This is deterministic and prevents copy drift.
    2. A reference-conditioned model for recurring figures: FLUX.2 klein 4B (Apache-2.0, up to 4 reference images, in mflux) per `reports/Shorts studio voices and tools.md` item 5. Gate it with a one-episode A/B; the owner decides on style.
  - **M [R]** Add an automated similarity check per character-bearing scene against a canonical sheet. Use DINOv2 (Apache-2.0) embeddings, flag below a calibrated threshold, and hand the decision to a human (it is subjective). Note: chalk conversion (`chalk_from_image`) changes appearance, so compare raw images.

### 2.8 Image generation and animation/motion
- **Exists:**
  - Z-Image Turbo 4-bit via mflux, 9 steps (`studio.py:289-321`).
  - Procedural chalk renderer (`chalk.render` `:342-434`): connected-component stroke reveal (`reveal_order` :126), chalk stick and particles, camera drift between per-scene zoom targets, streak-erase transitions (`ERASE=0.55`), titles revealed left to right.
- **Works:** distinctive, deterministic and fast (render ≈1.7× real time on frames). It avoids diffusion video, which is correctly rejected on 16 GB.
- **Findings:**
  - **M [V]** Frame 0 is an empty board (headline finding 12). **[R]** Start scene 1 pre-drawn to about 70% (or hold the finished image for the first 0.3 s, then a quick "trace" flourish). It is a one-line change in `plan()` for scene 0 and needs owner sign-off because it touches the approved style.
  - **M [V]** Image time scales with the scene count: 11–12 diffusion images per episode at 85–108 s each is 17–22 min. **[R]** Moving to 9–10 scenes saves about 4–6 min per episode and shortens the video.
  - **L [V]** Thermal throttling raises per-image time from 63 s to 108 s within one run. **[R]** A 20–30 s cool-down every 4 images is cheaper than throttled steps (measure before adopting).
  - **L [R]** Depth parallax (Depth Anything V2 *Small*, Apache-2.0) is the cheapest "more motion" upgrade. Keep it as an owner-reviewed A/B, not a default.

### 2.9 Voice
- **Exists:**
  - Kokoro af_heart (en, speed 1.04).
  - Maya 2 Native Malini (hi/gu/te) via `pipeline/voicepack.py:14-58`.
  - Veena retired.
  - The speaker guard and reference centroids (`profiles/voices/*_ref.npy`), per-voice thresholds (`voices.json._speaker_thresholds`), and `voicepack` A/B listening packs.
- **Works:** the 2026-11-16 drift incident led to a principled fix (whole-scene generation, ECAPA reference, calibrated 2.5 s windows). One narrator across hi/gu/te gives the series an identity. Maya 2 is about 6× faster than Veena.
- **Findings:**
  - **H [V]** Native-speaker review is absent for gu/te (headline finding 7). **[R]** Until a native listener exists, mark gu/te videos `unreviewed-language` in the DB and treat their analytics as a separate cohort.
  - **M [V]** Best-of-N for Maya 2 is a manual loop (headline finding 15). **[R]** Generalize `takes.best_of` to any `voicepack` engine:
    - keep the first take with no pitch outlier over 7 semitones, window similarity at or above the threshold and scene similarity of at least 0.6;
    - cap at 6 takes;
    - log the take index;
    - **auto-run it on scenes flagged by QA.**
  - **M [V]** The Malini thresholds were loosened to window 0.45 / scene 0.6 (`voices.json`), and C0005-hi passed with `window_min 0.525`, `scene_min 0.684`, against Veena's 0.5/0.7. **[R]** Re-calibrate with a negative set (another Maya voice, e.g. Vaidehi, speaking the same lines) so the threshold has known separation, not only self-similarity.
  - **L [R]** A Sanskrit verse voice is not used: verses are displayed but not recited. That is fine for a short runtime; don't add recitation while duration is over budget.

### 2.10 Music and SFX
- **Exists:** procedural tanpura + bansuri in Bhairavi (`chalk.music` :488), `chalk.sound` (chalk, erase, birds, river, wind, arrow, cry, bell; `CHALK_SFX_GAIN = 0.035` :16), voice-envelope ducking (`studio.py` `step_audio`), `music_gain` 0.25.
- **Works:** zero copyright risk, consistent identity, and an approved reduced chalk gain.
- **Findings:**
  - **L [V]** LRA is 1.9–2.8 LU, which is very compressed. That suits phone speakers. Nothing measures the music-to-voice ratio.
  - **L [R]** Add a QA metric: the median speech-band level minus the music bed in voice-free segments, with a warning band. It is objective and cheap.
  - **L [R]** ACE-Step 1.5 (MIT) is optional. Don't adopt it while the bottleneck is duration and consistency.

### 2.11 Editing, transitions and captions
- **Exists:**
  - Erase transitions.
  - Word-synced captions: `caption_groups` (`studio.py:360`), timing from `align_words` (Whisper word timestamps plus difflib mapping, `:580-622`).
  - A postposition rule (`POSTPOSITIONS` :357), `caption_max_chars` splitting, 4 words per group, captions at y = 0.75, saffron keywords.
- **Works:** script-aware captions in 4 scripts, keyword colouring, and Indic line-break rules.
- **Findings:**
  - **M [V]** Caption overflow is only a warning: C0005-te shipped with 976/984 px lines against the 960 px budget (`qa.py:132`). **[R]** Fail above W−60 px and auto-split instead.
  - **M [R]** Caption timing comes from ASR timestamps redistributed by character count. Forced alignment against the known script (CTC) is more exact for Indic languages (voices report item 2). Watch the trap that MMS aligner checkpoints are CC-BY-NC.
  - **L [R]** No safe-zone check exists for the Shorts/Reels UI overlays. Add a deterministic overlay test that renders the platform UI mask onto the contact sheet.

### 2.12 Automated video and audio QA
See §19 for the full current-versus-proposed design. Summary:
- [V] 7 checks exist (`qa.py:23-178`), but only `format`, `loudness`, `black_freeze` and `speaker_consistency` can fail (`qa.py:201`).
- Duration is not checked against the target.
- No visual-content checks exist.
- QA re-transcribes audio that was already transcribed.

### 2.13 Metadata and thumbnails
- **Exists:**
  - `publish.json` per language (YouTube title, description, tags, playlist, category 27, language, `synthetic`, pinned comment; Instagram caption, `thumb_offset_ms` and extras).
  - Vendored `yt-package/title.py` lint and `yt-seo` guidance.
  - `chalk.thumbnail` (`chalk.py:664`).
- **Works:** good descriptions (hook, story, verse with transliteration and translation, series navigation, question, source).
- **Findings:**
  - **M [V]** `containsSyntheticMedia: false` (`publish.py:103`) is consistent with YouTube's rule for clearly stylized content. Instagram sets `is_ai_generated` (C0001 extras). **[R]** Record the reasoning once in `docs/PUBLISHING.md`, so the two platforms' choices don't look contradictory.
  - **M [V]** Custom thumbnails are uploaded for Shorts (`publish.py:131-138`), but YouTube may not show them in the Shorts feed. The real "thumbnail" is frame 0, which is blank (§2.8).
  - **L [R]** Lint titles automatically in `pipeline lint`: run `title.py` on every `publish.json` and fail above 100 characters (already enforced at `publish.py:79`), warning above 60.

### 2.14 YouTube publishing and scheduling
- **Exists:**
  - `publish.youtube_upload` (`publish.py:75-139`): resumable upload, private + `publishAt`, read-back verification of privacy and `publishAt`, playlist, thumbnail.
  - DB record; `pipeline/schedule.py` slot explore/exploit.
- **Works:** the read-back after upload, the confirmation prompt, and gates enforced in code for G2 and G3.
- **Findings:**
  - **H [V]** Gate semantics (headline finding 2). **[R]** Make it `gate:publish:<platform>`, holding a `{lang: approved_iso_time}` map plus a sha256 of `publish.json` and of the mp4. `require()` rejects a mismatch in time (±0), in metadata hash or in video hash.
  - **H [V]** There is no QA verdict check (headline finding 3). **[R]** `cmd_approve final` refuses unless the latest `qa_reports` verdict for that variant is pass, or a warn whose warnings each carry a recorded human waiver.
  - **M [V]** The upload limit was hit (`data/upload_queue.log`), and the queue lives in `data/upload_queue.sh`. **[R]** Move it into `pipeline publish-queue` with a persisted queue table and backoff. Cap uploads per day, and prioritize by publish date.
  - **M [V]** The `schedule.recommend` exploit step compares raw views across languages and episode numbers (`schedule.py:27`). **[R]** See §20. With 1 video per language per day and 3 candidate slots, the "3 × 48 h samples per slot" rule needs 9+ videos per language before any decision, and the result is still confounded by episode decay.
  - **L [V]** The pinned comment and Related-video link are manual (an API limitation). That is correctly documented.

### 2.15 Instagram publishing
- **Exists:**
  - `instagram.py`: Instagram Login API v27.0, temporary cloudflared tunnel, container poll, publish, permalink.
  - Duplicate guard (`already_published` :204), limit checks (3 s–15 min, 300 MB).
  - launchd one-shot scheduling (`pipeline/igschedule.py`), a 24 h staleness refusal, and a tunnel retry ×4 (`__main__.py:284-289`).
- **Works:** a clever zero-cost workaround for "no direct upload", with a security-conscious tunnel (random path, no listing, closed before publish).
- **Findings:**
  - **H [V]** A legacy defective file was reposted (headline finding 4). **[R]** `publish --platform instagram` must require a `video_qa` pass on *that exact file* (by hash). Legacy `out/` files fail by default.
  - **M [V]** No Instagram insights are collected. **[R]** Add `instagram_insights` (Reels plays, reach, saved, shares, `ig_reels_avg_watch_time`) via the same token, into `analytics_snapshots` with `platform='instagram'`.
  - **M [V]** A scheduled post depends on the Mac being awake, and posts late after wake (documented). **[R]** Keep the 24 h refusal, and add a "late by more than 30 min → ask the owner" rule, since a late post at 02:00 IST is worse than a skipped slot.
  - **L [V]** `stages` gets `instagram_scheduled:*` and `published_instagram:*` keys that are not in `STAGES` (`__main__.py:11`), so `status` and `next_action` ignore Instagram entirely.

### 2.16 Analytics
- **Exists:** `pipeline/analytics.py`: windows 24h/48h/7d/14d/30d (:8); a core metrics list including `engagedViews` (:9); by-day, traffic sources, countries and retention (:39-45); `report()`; `equal_window_table`; retention insights.
- **Works:** honest handling of missing data (`unavailable` is stored, not invented), a retention CSV bridge to `yt-retention`, and a cautionary comparison note.
- **Findings:**
  - **H [V]** No usable data. The YouTube Analytics API is disabled (all `totals` are 403) and no daily job runs. The only data is public counters (C0001-hi 70 views, C0001-en 7 at the snapshot).
  - **H [V]** Window mislabelling and cumulative queries (headline finding 9). **[R]** Fix both:
    - store `captured_at - published_at` as `age_h`;
    - query `startDate=endDate` for the day series;
    - compute window metrics from `by_day`;
    - only label a window when the snapshot happens within ±12 h of it, otherwise label it `age_<n>h`.
  - **M [V]** Scene-level retention mapping is planned (`performance-analyst.md` step 4) but impossible: render timings are not persisted (no `timeline.json`). **[R]** `step_render` should write `timeline.json` (scene starts and ends, hook end, verse window). Then retention-to-scene mapping is a deterministic join.
  - **M [R]** Install the daily launchd analytics job (PROJECT_CONTEXT §20) once the API is enabled. An LLM is not needed to collect.

### 2.17 Optimization
- **Exists:** the `optimization-strategist` agent, the `recommendations` table (0 rows), and confidence tiers (low <5, medium 5–15, high >15 videos).
- **Findings:**
  - **M [V]** Dormant. That is correct given no data.
  - **H [R]** The current design will mislead once data arrives, because there is no record of what *varied* between videos. Add a per-variant `features` row (duration, scenes, words, hook type, hook word count, first-frame type, voice, language, slot, weekday, episode number, title pattern), plus an `experiments` table (§20).
  - **[R]** Until about 30 published variants exist with 7-day data, run the optimizer manually monthly, not per episode.

---

## 3. Multi-agent architecture (§18)

### 18.1 Current set: are the responsibilities distinct? [V]

| Agent | Distinct? | Real use so far | Verdict |
|---|---|---|---|
| trend-researcher | Overlaps with content-strategist (both choose topics) | Pilot only (C0002) | Merge into one series planner, run per arc |
| audience-localizer | Overlaps with scriptwriter (per-language writing) and profiles | 26-line notes per episode | Merge into scriptwriter; profile edits on evidence |
| content-strategist | Overlaps with trend-researcher | Score table only in C0002 | Merge |
| scriptwriter | Distinct | Every episode | Keep |
| creative-director | Distinct, but it writes prompts *and* reviews its own images | Every episode | Keep; move image *verdicts* to the reviewer |
| language-qa | Overlaps with video-qa and `pipeline qa`; docs are stale (Veena) | Notes in the manifest | Merge into reviewer; deterministic parts to Python |
| video-qa | Mostly runs `pipeline qa` plus reads a contact sheet | Every episode | Merge into reviewer |
| publishing-manager | Metadata writing is LLM work; schedule and upload are deterministic | Every episode | Keep as packager; upload stays Python |
| performance-analyst | 100% deterministic steps (run analytics, run report) | No data | Replace with Python (`pipeline analytics/report` + launchd) |
| optimization-strategist | Distinct judgement, but needs data | Dormant | Keep dormant; activate at ≥30 variants with 7d data |

**Handoffs [V].** The handoff medium is files plus `manifest.json` stage marks. That is good: it is inspectable and resumable. But the marks are honor-system:
- `pipeline done <ID> <stage>` can mark `voice_qa`/`video_qa` done regardless of verdict. All C0005 `voice_qa` marks were written at the same second (12:12) as bookkeeping.
- Any agent with Bash can run `pipeline approve`. Nothing distinguishes an owner approval from an agent's call except the free-text note.

**[R] H:** make `approve` interactive by default: it prints the artifact hashes and requires typing the variant ID. `--yes` is allowed only when the environment variable `STUDIO_OWNER_APPROVED=<content id>` is set by the owner. Add a test that agents' tool allowlists exclude `pipeline approve`.

### 18.2 Make these deterministic Python, not LLM agents [R]

| Task | Today | Python target |
|---|---|---|
| Duration, word budget, digits, keyword-token, scene-count lint | Agent prose | `pipeline lint <ID>` (blocks G1) |
| Evidence pulls (trending, competition, wiki) | Agent runs CLI | Weekly launchd job |
| Objective QA (all of §19 "auto") | Partly in `qa.py` | `qa.py` + gate enforcement |
| Voice best-of-N on flagged scenes | Manual loop | `pipeline takes` generalized, auto on QA fail |
| Border crop, image sanity | Manual crop | `step_images` post-process |
| Scheduling, upload queue, IG jobs | Shell scripts, agent | `pipeline publish-queue` |
| Analytics collection, reports, retention→scene mapping | Agent | launchd + `timeline.json` join |
| Hooks/features/experiments logging | Manual | Automatic on `done script` / `render` / `publish` |

### 18.3 Recommended agent set: 5 active, 1 dormant [R]

Each agent below is listed with its responsibility, inputs, outputs, tools and skills, handoff, approval point and failure handling.

**1. series-planner** (merges trend-researcher, content-strategist and audience-localizer)
- **Runs:** per arc (about every 8–10 episodes) or on the owner's request.
- **Responsibility:** the next arc, episode map, teaser chain, language plan, and profile updates *with evidence*.
- **Inputs:** research JSON from the weekly job, analytics reports, `profiles/languages/*`.
- **Outputs:** `content/series/<series>.md` (episode map, sargas, depiction risks) and profile diffs.
- **Tools:** Read/Write, WebSearch/WebFetch, Bash for `pipeline research`; skills `yt-viral`, `yt-plan`.
- **Handoff:** the scriptwriter reads the episode row.
- **Approval:** the owner approves the arc plan (lightweight, not a production gate).
- **Failure:** missing evidence goes into the plan as "judgement"; it never blocks an episode.

**2. scriptwriter** (absorbs per-episode localization and source verification)
- **Responsibility:** verify sources, then write the hooks and `script.json` for every language within the per-language word budget.
- **Inputs:** the episode map row, `storytelling` skill (updated to 35–55 s), language profiles, previous episode teaser.
- **Outputs:** `research/report.md` (verse table), `<lang>/hooks.json`, `script.json`, `script.md`.
- **Tools:** Read/Write, WebFetch (wikisource); skills `storytelling`, `yt-script`.
- **Handoff:** `pipeline lint` must pass, then the reviewer.
- **Approval:** G1 (owner).
- **Failure:** a lint failure loops back to the writer automatically (max 2 rewrites), then goes to the owner with the diff.

**3. creative-director**
- **Responsibility:** the visual plan, positive prompts with `{character}` tokens, the character bible and reference sheets, and image regeneration requests.
- **Inputs:** `script.json` (primary), `ramayana.json`, the visual QA report.
- **Outputs:** the `visual`/`seed`/`shot` fields, bible entries, reference sheet images.
- **Tools:** Read/Write/Bash.
- **Handoff:** images are generated, then visual QA (automatic plus reviewer).
- **Approval:** none separately; covered at G2. A style change needs explicit owner approval.
- **Failure:** at most 3 regenerations per scene; after that, the owner chooses among the candidates.

**4. reviewer** (merges language-qa and video-qa; independent of the writer and director)
- **Responsibility:** the *subjective* part of Story QA before G1 (hook strength, clarity, accuracy flags, cultural sensitivity), Visual QA (depiction rules, character consistency on flagged scenes, legibility) and Audio QA (listening to flagged scenes, transcript review). It writes scored verdicts and never edits artifacts.
- **Inputs:** `qa.json` from `pipeline qa`, the contact sheet, the safe-zone overlay, transcripts, scripts.
- **Outputs:** `<lang>/review.md` with scores per §19 and numbered fixes.
- **Tools:** Read and Bash (read-only commands). It has no Write access to scripts or images.
- **Handoff:** fixes go to the scriptwriter or creative-director; a clean report goes to the owner at G2.
- **Approval:** none; it prepares G1 and G2.
- **Failure:** disagreement with an automatic check is recorded as a waiver request for the owner, never as an override.

**5. packager** (the metadata part of publishing-manager)
- **Responsibility:** YouTube and Instagram metadata per language; title/thumbnail lint; the schedule proposal from `pipeline schedule`.
- **Inputs:** script, verse table, `pipeline schedule` output.
- **Outputs:** `publish.json` and the proposed times.
- **Tools:** Read/Write, Bash (lint scripts); skills `yt-package`, `yt-seo`.
- **Handoff:** the G3 bundle to the owner. **The upload itself is the Python queue, never the agent.**
- **Approval:** G3 per platform.
- **Failure:** a lint failure means a rewrite; an upload failure is handled by queue retry with backoff, and the agent is not involved.

**6. optimizer** (dormant)
- **Activate:** when ≥30 published variants have 7d snapshots.
- **Inputs:** the `features`, `experiments` and `analytics_snapshots` tables.
- **Outputs:** `recommendations` rows with effect size, CI and sample size.
- **Approval:** the owner approves any change to style or profile.

This cuts 10 to 5 active agents. Each remaining agent has a distinct artifact and a measurable quality signal:
- **scriptwriter:** lint pass rate, G1 first-pass approval rate;
- **creative-director:** regenerations per episode;
- **reviewer:** defects caught before the owner, and defects the owner found that the reviewer missed;
- **packager:** title lint, later CTR where available;
- **series-planner:** arc completion.

---

## 4. QA system (§19)

### 19.1 Checks that exist today [V]

| Check | Function (`pipeline/qa.py`) | Threshold | Effect |
|---|---|---|---|
| format | `check_format` :23 | 1080×1920, 30 fps, audio present, **≤180 s** | fail |
| loudness | `check_loudness` :42 | −16.5…−13 LUFS, TP ≤ −1 dBFS | fail |
| black_freeze | `check_black_and_freeze` :58 | black ≥0.3 s; freeze ≥2.5 s | fail |
| silence | `check_silence` :67 | ≥1.6 s below −42 dB | warn |
| narration_asr | `check_narration` :89 | CER >0.15 or length ratio outside 0.85–1.2 (Whisper small en / large-v3-turbo others) | warn |
| captions | `check_captions` :111 | alignment present, width ≤ W−120, no leading postposition | warn |
| speaker_consistency | `check_speaker` :139 | per-voice window/scene similarity vs reference, pitch >7 semitones from median | fail |
| contact sheet | `contact_sheet` :181 | 12 frames | for manual review |
| manual list | `run` :205 | character consistency, visual defects, storytelling, native listen | not tracked |

- **Verdict history [V]:** 40 reports: 12 pass, 17 warn, 11 fail. A warn is publishable, and the gates never read verdicts.
- **Gaps [V]:** no duration-target check, no hook or first-frame check, no image-content checks (border, text artifact, duplicate, character), no safe-zone check, no thumbnail check, no glyph-coverage (tofu) check, no music/voice balance, no per-scene speech rate, no file-hash binding between the QA'd file and the uploaded file.

### 19.2 Proposed scored QA [R]

Each check is classed as **Auto-reject** (objective, blocks the next stage, needs no LLM), **Auto-warn** (objective but with known false positives; needs a waiver note) or **Human** (subjective; the reviewer scores it and the owner decides). Score each family 0–100 as the share of weighted checks passed. **A family passes only if it has no auto-reject failure and a score of at least 80.**

**Story QA** (on `script.json`, before G1, mostly `pipeline lint`)

| Check | Metric | Threshold | Class |
|---|---|---|---|
| Estimated duration per language | words ÷ measured w/s + pauses + 1.15 s | >58 s reject · outside 35–55 warn | Auto-reject |
| Hook length | spoken seconds of scene 1 | >3.0 s reject · >2.2 warn | Auto-reject |
| Scene count and length | scenes; seconds per scene | 8–11 scenes; each scene 2.5–7 s | Auto-warn |
| Keywords present | every `keywords` token is in the narration tokens | any missing | Auto-reject |
| Digits in unsupported languages | regex `\d` in gu/te/ta/… narration | any | Auto-reject |
| Sources | `sources` non-empty; verse `source` matches `\d+\.\d+\.\d+` | missing | Auto-reject |
| Visual parity | same scene count and identical `visual` as primary | mismatch | Auto-reject |
| Hook strength | rubric scored blind by the reviewer | <24/30 | Human |
| Accuracy and labelling of traditions | reviewer against the verse table | any unsourced claim | Human (owner at G1) |
| Cultural/deity depiction plan | reviewer against `rules` | any violation | Human |

**Visual QA** (on `img/NN_raw.png` after images, before render)

| Check | Metric | Threshold | Class |
|---|---|---|---|
| Border/margin | mean luminance of the outer 3% band versus the interior; bright straight edges | band mean > interior + 0.25 → auto-crop; still present → reject | Auto-reject (with auto-fix) |
| Text artifacts | OCR (Tesseract, Apache-2.0) finds ≥3 Latin/Devanagari characters | any | Auto-warn |
| Near-duplicate scenes | perceptual hash distance between scenes | <8 bits | Auto-warn |
| Chalk density | share of `chalk_from_image` pixels | <3% (empty) or >45% (muddy) | Auto-warn |
| Safe zones | stroke energy in the top 12% (title) and bottom 25% (captions) | above calibrated p90 | Auto-warn |
| Character similarity | DINOv2 cosine against the reference sheet, for scenes carrying a `{character}` token | below calibrated threshold | Human (flag only) |
| Depiction rules (deity form, Western demons, domes, frontal Rama) | reviewer | any | Human |

**Audio QA** (on `audio/*.wav` and `mix.wav`)

| Check | Metric | Threshold | Class |
|---|---|---|---|
| Speaker consistency | existing check | per-voice thresholds, calibrated with a negative voice set | Auto-reject (existing) |
| Pitch outlier | existing | >7 semitones | Auto-reject; triggers auto best-of-N |
| ASR CER, normalized, en/hi | reuse `NN.words.json` transcript (no second Whisper pass) | >0.30 reject · >0.15 warn | Auto-reject |
| ASR CER, gu/te | same | >0.15 warn only, until Indic ASR is validated | Auto-warn |
| Speech rate per scene | words ÷ seconds versus the language median | ±25% warn · ±40% reject (garble or stutter) | Auto-reject |
| Clipping / true peak | `mix.wav` peak; final TP | TP > −1.0 dBFS | Auto-reject (existing) |
| Music under speech | speech-band level minus bed level | <12 dB warn | Auto-warn |
| Pronunciation and naturalness | native listener, or the owner for en/hi | owner/native says no | Human |

**Final QA** (on the mp4)

| Check | Metric | Threshold | Class |
|---|---|---|---|
| Duration | ffprobe | **≥60.0 s reject** · outside 35–55 warn | Auto-reject |
| Format, loudness, black/freeze | existing | existing | Auto-reject |
| First frame | non-board pixel share at t=0 (and at 0.5 s) | <5% at t=0.5 s | Auto-warn (style decision) |
| Caption overflow | width > W−60 px | any | Auto-reject |
| Glyph coverage | every narration and verse character is in the chosen font's cmap | any missing | Auto-reject |
| Silence gap | existing | ≥1.6 s | Auto-warn |
| File binding | sha256 of the QA'd mp4 is stored; publish refuses a different hash | mismatch | Auto-reject |
| Overall watchability, pacing, ending | reviewer, then the owner at G2 | — | Human |

**Gate rules [R]**
- `approve script` needs Story QA auto checks passed.
- `approve final` needs Visual, Audio and Final auto checks passed, with every warn either cleared or waived (waiver text plus who). The reviewer's report must exist.
- `publish` needs the QA'd hash to equal the upload hash, plus the platform gate with a matching time and metadata hash.

**Compute [R]:** reusing the render-time Whisper transcript removes one of the two Whisper passes per scene. That is the main reason non-English QA takes about 115–140 s per language, rising to 59 min under contention. Load the ECAPA model once per QA run; it already caches in `speaker.model()`.

---

## 5. Performance-based learning (§20)

### 20.1 What is stored today [V]

- **`data/studio.db` schema** (`pipeline/db.py:10-115`): `contents`, `variants`, `research`, `hooks`, `decisions`, `runs`, `qa_reports`, `publications`, `analytics_snapshots`, `recommendations`.
- **Row counts:**

| Table | Rows |
|---|---|
| contents | 5 |
| variants | 20 |
| research | 3 |
| hooks | 24 |
| decisions | 25 |
| runs | 131 |
| qa_reports | 40 |
| publications | 14 (10 YouTube, 4 Instagram) |
| analytics_snapshots | 6 |
| recommendations | 0 |

- **`variants.duration_s`** is filled only for C0001 en/hi. `cmd_produce` never writes it (`__main__.py:192`).
- **`analytics_snapshots.metrics`** is a JSON blob holding public counters, totals, by-day, traffic sources, countries and retention. All 6 rows are labelled `initial`, and their Analytics sections are 403 errors.
- **`data/rates.json`** holds production rates only (`images 85.6`, `voice:veena 99.5`, `voice:kokoro 6.4`).
- **No experiments table, no per-variant feature vector, no Instagram metrics.** The video's own properties (duration, hook type, scene count, slot) would have to be reconstructed from files.

### 20.2 Learning design that works with small samples [R]

1. **Log features automatically** in a `features(variant_id PK, …)` table, written at `done script`, `render` and `publish`. Fields:
   - duration_s, scenes, words, wps;
   - hook_type, hook_words, hook_seconds;
   - first_frame (blank or predrawn), voice, language;
   - slot_ist, weekday, episode, title_pattern, has_verse.
2. **Fix the windows** (§2.16). Use `engagedViews`, average view percentage, and **viewed-versus-swiped-away where the API provides it**. For Shorts, the main early signal is the share of viewers who stay past the first seconds, which needs the retention curve at small elapsed ratios.
3. **Use within-episode comparisons as the main design.** Each episode ships in 4 languages at staggered times, so episode content is held constant. Two consequences:
   - Languages are different audiences, so do **not** compare raw views across languages.
   - Within one language, compare episodes by a *ratio to that language's rolling median* (outlier multiple, the `yt-viral` logic), never by raw views. This controls for channel growth and series decay.
4. **Run one experiment at a time with a pre-registered protocol** in an `experiments` table: `id, hypothesis, variable, arms, assignment_rule, metric, min_n_per_arm, start, stop_rule, status, result`. Rules:
   - **Change one variable for the whole series** (e.g. 50 s versus 85 s), alternating by episode: odd episodes arm A, even episodes arm B, in all languages. That balances episode-content effects over time.
   - **Minimum n:** at least 6 variants per arm per language before *any* claim (about 3 weeks at one episode a day). Report the median ratio and a bootstrap or Mann-Whitney interval. With n < 6 the output is "anecdote" (matches the existing low-confidence tier).
   - **Stop rule:** decide in advance, e.g. after 12 episodes or when the interval excludes 1.0. Never stop early because one video spiked.
   - **Order:** (1) duration 35–55 versus the current length, the highest expected effect and the owner's stated target; (2) frame 0 predrawn versus blank; (3) hook type; (4) slot, only after the rest, because slot effects are small and confounded with weekday.
5. **Slot scheduler:** freeze slots during content experiments. A changing slot is a second variable. Once data exists, rank slots with the per-language outlier ratio, not raw views (`schedule.py:27`).
6. **Optimizer output** is a `recommendations` row with: experiment id, effect (median ratio), interval, n per arm, confidence tier, proposed change, status. Any change to style or profile still needs owner approval (unchanged policy).
7. **Close the loop** with `timeline.json` (§2.16). The `yt-retention` cliffs then map to scenes deterministically, so "scene 7 loses 12%" becomes evidence attached to a scene type (verse card, silhouette, etc.).

---

## 6. Waste and overcomplication summary [V unless marked]

| Area | Waste | Fix |
|---|---|---|
| QA | A second Whisper pass per scene; QA reruns of the whole video after a one-scene fix (C0003-hi: 8 reports) | Reuse `words.json`; per-scene QA cache keyed by WAV hash [R] |
| Images | 11–12 images for a video that should be 9–10 scenes | Shorter scripts [R] |
| Duration | 20–56 s over target in every video. Voice, render, upload and QA all scale with length | Duration lint [R] |
| Agents | 10 agents; 5 dormant or redundant; stale docs (language-qa says Veena) | §18.3 |
| Gate bookkeeping | Honor-system `done` marks; free-text approvals; advance approvals | Hash-bound gates [R] |
| Orchestration | Shell queues and fix scripts in `data/` | `pipeline publish-queue` [R] |
| Docs | PROJECT_CONTEXT §10 still says the approved Hindi voice is Veena kavya; CLAUDE.md says "Hindi voice: Veena kavya" while `voices.json` and §22 say Maya 2 Malini | Reconcile the docs (owner-facing confusion) [R, M] |

## 7. Must stay human-approved
- Hindi/Gujarati/Telugu pronunciation (native ear), the depiction of deities and of Ravana and Tataka, and scriptural accuracy (G1).
- Any change to the chalk style, chalk SFX gain, narrator voice or video length policy.
- Each platform's publish time, metadata and file (G3 per platform).
- Waivers of auto-warn checks.

Everything objective in §19 should be automatic and blocking, so the owner's time at G1, G2 and G3 goes only to the human-only questions.

## 8. Suggested order of work [R]

| Order | Work | Priority | Effort |
|---|---|---|---|
| 1 | Encode 35–55 s everywhere (skill, agent, handoff) and add `pipeline lint` with per-language word budgets. Final QA rejects ≥60 s | C | S |
| 2 | Platform-specific, hash-bound G3; QA verdict required for G2 and publish; QA'd-file hash must equal the uploaded file | H | M |
| 3 | Enable the Analytics API; fix window labels and cumulative queries; launchd daily job; `timeline.json`; `features` table | H | M |
| 4 | Generalized best-of-N takes for Maya 2, auto-run on QA flags; reuse the Whisper transcript in QA | M | S |
| 5 | Border auto-crop; positive prompt rewrite; `{character}` tokens; frame-0 predraw (owner A/B) | H/M | M |
| 6 | Collapse to 5 agents and update the docs (Veena references) | M | S |
| 7 | Native reviewer for gu/te, or label them unreviewed cohorts | H | owner |
| 8 | Reference-conditioned images (FLUX.2 klein 4B) as an A/B | M | L |
| 9 | Instagram insights; `publish-queue` with daily cap | M | M |
