# Animated video generation on this Mac (Ayodhya Kanda anime chapter)

Research date: **2026-11-17**. Every timing below was measured on this machine: MacBook Air, Apple M5, 16 GB unified memory, macOS 27. During the tests Android Studio, an emulator and a simulator were also open, holding about 4.6 GB of wired memory. All work is in `data/anim_lab/`, which is gitignored. Neither the production venv nor the pipeline code was changed.

## 1. Verdict

| Rank | Model and runtime | Status | Use |
|---|---|---|---|
| 1 | **LTX-2.3 int4, distilled two-stage, run with `ltx-2-mlx --low-ram`** | Two finished clips; real motion; style held | **Production model** for AI shots |
| 2 | Wan 2.2 TI2V-5B q8, run with `mlx-video` | Partial: 8 of 20 steps, then stopped for the Ep09 renders | Cleanest licence (Apache-2.0), but about 2–3× slower per clip than LTX |
| – | FastWan 2.2 TI2V-5B (DMD, 3 steps, Apache-2.0) | Weights downloaded; sampler patched in the lab clone; **not run** | Next candidate if Wan speed matters |
| ✗ | AnimeGen-I2V-A14B (Apache-2.0, anime fine-tune) | Not run | About 43 GB peak according to its card, so it cannot run on 16 GB |
| ✗ | LTX-2.5 packs | Not run | 47–120 GB downloads |
| ✗ | FramePack and HunyuanVideo; CogVideoX | Not run | Territory-restricted licence; CogVideoX needs registration |

A hybrid is needed. AI clips take 12–22 min per 4 s, so they should cover the 4–6 key shots of an episode: character acting, crowds, camera moves through a scene. The remaining shots should use a cheap procedural or 2.5D move such as a Ken Burns push, a parallax move or a cross-fade.

## 2. Measured results (same test for each model)

The keyframes came from the existing `mflux-generate-z-image-turbo --model models/z-image-turbo-4bit` at 576×1024 with 9 steps. Each took about 44 s, with a peak RSS of 2.3 GB. They are in `data/anim_lab/keyframes/courtyard.png` and `king.png`.

| Clip | Model | Output | Wall time | Phase times | Peak memory footprint (RSS) | Swap growth | Result |
|---|---|---|---|---|---|---|---|
| Courtyard I2V | LTX-2.3 q4 distilled, `--low-ram --no-audio` | 576×1024, 97 frames, 24 fps (4.04 s) | **21 min 58 s** | Gemma encode 151 s (memory pressure from the other apps), stage 1 8×~51 s, stage 2 3×~215 s, then decode | 8.13 GB (2.12 GB RSS) | +7.9 GB | Good |
| King I2V | same | same | **11 min 39 s** | encode 68.5 s, stage 1 3 min 49 s (8×~28 s), stage 2 3×113 s, decode 41.6 s | 8.44 GB (1.84 GB RSS) | +5.6 GB | Good motion; crown details drift |
| Courtyard I2V | Wan 2.2 TI2V-5B q8 (T5 re-quantized to q8, sequential CFG), unipc, 20 steps, guidance 5 | 576×1024, 97 frames, 24 fps | **Stopped at step 8 of 20** after 15 min 28 s of denoising | T5 encode 34.9 s, image encode 4.6 s, **113–132 s per step** | process about 11–12 GB | +6.8 GB | Estimated 38–44 min per clip plus decode |
| Courtyard I2V | Wan 2.2 TI2V-5B q8, stock batched CFG (B=2) | same | aborted after 81 s | – | 13 GB | +8.9 GB (abort rule) | Does not fit 16 GB as shipped |

The two LTX runs differ mainly because of memory pressure. During the courtyard run, other apps plus a download in progress pushed the encode and denoise phases into swap. **Plan on 12–22 min per 4 s clip**, about 17 min on average.

**Motion quality**, judged from 5-frame contact sheets and frame-difference statistics:
- **Courtyard (LTX).** The camera moves forward through the scene with real parallax. Crowd figures walk away from the camera with coherent legs and saris, and petals drift. The banners sway only slightly. The painterly cel look of the keyframe holds, with slight softening. There are no cuts or flicker: mean frame difference is 6.0, the largest is 7.35, and the spike ratio is 1.2. This is real environment and character motion, not warping.
- **King (LTX).** The king really turns his head (to profile and back), and the smile at the end is clear. The face reads as the same person, and the tilak and beard stay consistent. **Drift:** the crown gains a red cap when the head turns, and its jewel pattern changes. He turned away and back rather than toward the camera as prompted. There is no single-frame jump; the high frame differences (around 15) come from the fast turn. This is acceptable for anime, but character sheets and reference conditioning will be needed (§6).
- **Ken Burns baseline** (`data/anim_lab/kenburns/`) took seconds to make and holds the keyframe exactly, but nothing moves inside the frame.

Artifacts:
- `data/anim_lab/ltx23_q4_distilled/courtyard.mp4`, `king.mp4`, `*_sheet.png`, `*_1080_lanczos.mp4`
- `data/anim_lab/kenburns/*.mp4`
- `data/anim_lab/logs/*.log` and `*.mem.tsv` (per-run log and swap/memory trace)
- No Wan mp4 exists, because the run was stopped before decode.

## 3. Setup

The steps below are reproducible.

```
data/anim_lab/ltx-2-mlx      git clone dgrauet/ltx-2-mlx @747b30e (2026-11-01), MIT
data/anim_lab/venv-ltx       uv sync, Python 3.12
data/anim_lab/mlx-video      git clone Blaizzy/mlx-video @87db56a (2026-05-13), MIT
data/anim_lab/venv           uv venv + pip install -e mlx-video
data/anim_lab/bin/           lock.sh (data/heavy.lock), run2.sh (time -l + swap watchdog, abort at +8 GB),
                             ltx_run.sh, wan_run.sh, sheet.sh, tstats.py, t5_q8.py
```

The LTX command, run under `LTX2_SPLIT_TEXT_ENCODE=1`:

```
ltx-2-mlx generate --distilled --model data/anim_lab/models/ltx-2.3-mlx-q4 --low-ram --no-audio \
  --image keyframe.png -p "<motion prompt>" -H 1024 -W 576 -f 97 --frame-rate 24 --seed 42 -o out.mp4
```

**Local patches.** These were made only in the lab clones, not in the pipeline.
1. `ltx-2-mlx` `utils/blocks.py`, behind the `LTX2_SPLIT_TEXT_ENCODE` env var. Stock code loads Gemma 3 12B 4-bit (8 GB) and the 6.3 GB bf16 text connector together, which pushed swap up 9.5 GB in 30 s and tripped the abort. The patch encodes with Gemma, frees it, and only then loads the connector. **This is required on 16 GB.**
2. `mlx-video` `wan_2/utils.py`, behind `WAN_T5_Q8`. Stock code upcasts the 11.4 GB umT5 to **float32**, which needs about 22 GB. `bin/t5_q8.py` re-quantizes it to an 8-bit file of 6.0 GB in 10 s.
3. `mlx-video` `wan_2/generate.py`:
   - `WAN_SEQ_CFG` runs the cond and uncond passes one after the other instead of as a B=2 batch.
   - `WAN_DMD` adds the FastWan 3-step sampler (the DMD distilled schedule). It is untested.

Disk used:

| Item | Size | Keep? |
|---|---|---|
| LTX q4 (selected files) | 19 GB | Keep |
| `mlx-community/gemma-3-12b-it-4bit` in the HF cache | 7.5 GB | Keep |
| Wan TI2V-5B q8 with the q8 T5 | 24 GB | Optional; delete only with the owner's OK |
| FastWan DiT | 9.3 GB | Optional; delete only with the owner's OK |
| venvs | 1.3 GB | Keep |

Free disk is now 57 GB. Deleting both Wan folders frees about 33 GB.

## 4. Licences (weights)

**LTX-2.3: LTX-2 Community License Agreement.** Dated 2026-01-05; read in full from the `LICENSE` shipped in `dgrauet/ltx-2.3-mlx-q4`, verbatim from [Lightricks LICENSE-2](https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2). The HF repo is not gated.
- **Grant (§2).** A worldwide, royalty-free licence to use, reproduce, modify and distribute "for any purpose". The exception is **entities with annual revenue of at least $10M, counted together with all affiliates**: they must get a paid commercial licence. Using it above that threshold without one triggers double fees as liquidated damages. This channel is far below $10M, so use is free. Re-check if revenue ever approaches the threshold.
- **Outputs (§5).** Lightricks claims no rights in outputs. You are responsible for your outputs, and outputs must not break the use restrictions.
- **Attachment A** applies to outputs too. The items that matter here:
  - **#5:** you must not publish generated content "without expressly and intelligibly disclaiming that the information and/or content is machine generated". The project already sets YouTube `synthetic: true` and Instagram `is_ai_generated: true`; **keep a visible AI notice** as well, for example in the description.
  - **#7:** no impersonation or deepfakes of real people. Mythological figures are fine.
  - **#18:** for commercial use, outputs must not be used to train other models.
  - **#20:** no product that competes with Lightricks.
  - There are also the usual bans on illegal, harmful and military uses, plus a referenced Acceptable Use Policy.
- **Other terms:**
  - §6: Lightricks may "restrict (remotely or otherwise)" usage that violates the licence, and asks users to make reasonable efforts to use the latest version.
  - §7: sanctions and export compliance.
  - §3: redistributing the weights requires passing on this licence. We do not redistribute.
  - Disputes go to New York law and ICC arbitration, and the licence ends on breach.

**Gemma 3 12B** is the text encoder required by LTX-2.3 (`mlx-community/gemma-3-12b-it-4bit`; the HF tag is `license:gemma` and the repo is not gated). It is under the Gemma Terms of Use, which allow commercial use subject to Google's Prohibited Use Policy. The terms are not reproduced here: **Unverified** in full this session, so read them before production.

**Wan 2.2 TI2V-5B** is **Apache-2.0**. This is verified from the official HF card ("We claim no rights over your generated contents") and from the `LICENSE` and `NOTICE` in `Anes1032/Wan2.2-TI2V-5B-mlx-q8`. **FastWan2.2-TI2V-5B** (FastVideo, plus the `lBroth` MLX conversion) is tagged Apache-2.0 on HF, verified from API metadata.

**Code licences:**
- `ltx-2-mlx`: MIT
- `mlx-video`: MIT
- Real-ESRGAN repo: **BSD-3-Clause**, verified from the GitHub API. The release weights (`realesr-animevideov3`) have no separate licence statement; they ship in the same BSD-3 repo's releases (status: Unverified for the weights).

## 5. Upscaling to 1080×1920 and per-episode budget

**Upscaling:**
- **ffmpeg Lanczos** from 576×1024 takes 2–5 s per clip (`courtyard_1080_lanczos.mp4`, `king_1080_lanczos.mp4`). The result is soft but clean, and the cel-shaded style tolerates it well. **Recommended default.**
- **Real-ESRGAN ncnn-vulkan, `realesr-animevideov3`.** The macOS binary from the v0.2.5.0 release runs on the M5 GPU. It upscaled a 288×512 test frame 4× and produced a valid output; it was only tested on that one still. It was not timed on video, because the Ep09 renders had priority. Use it as an optional sharpening pass: extract frames, run x2, then re-encode. Expect minutes per clip.

**Episode budget.** A 45 s episode has about 10–12 shots.

| Shot mix | Time at ~17 min average per AI clip | Range at 12–22 min per AI clip |
|---|---|---|
| All 12 shots as LTX clips | ~3.4 h | 2.4–4.4 h |
| Hybrid: 5 AI hero shots + 7 procedural shots | **~1.5 h** | – |

- Visuals are shared across the five languages, so this cost is paid once per episode.
- Runs must be serial (one heavy model at a time) and hold `data/heavy.lock`, so they cannot overlap with voice or render work.
- Closing the emulator and simulator should make runs land nearer the 12-minute figure.
- Clips can be 4 s (97 frames) or 5 s (121 frames, slower). Generation should stay at 576×1024, then be upscaled.

## 6. Limitations and next steps

- **Two clips per model is a small sample.** Seeds vary. Expect 1 in 3 or so to need a re-roll, which should be planned into the time budget.
- **Character consistency is the main risk.** The crown drifted within 4 s, and nothing ties a character's look across shots beyond the keyframe. **Next step: reference-conditioned keyframes.** Generate every shot's first frame from a fixed character sheet (Dasharatha, Rama, Sita, Kaikeyi, and so on) using an image model with reference or identity conditioning, so each shot starts on-model. Then use LTX multi-anchor I2V: `--image PATH FRAME STRENGTH`, repeatable, with a `last` frame anchor such as a front-facing frame at strength about 0.7. This pins the face at the end of the shot. The ltx-2-mlx docs report ArcFace similarity rising from 0.42 to 0.55 with such an anchor.
- **Prompt adherence is loose.** "Turns toward the camera" became a turn away and back. Write prompts as simple, single actions.
- **Memory headroom is thin.** Peak footprint is about 8.4 GB and swap grew 5.6–7.9 GB with other apps open. Never run LTX alongside voice or render work. The stock (unpatched) ltx-2-mlx text encode does not fit.
- **Wan was not completed.** No Wan output quality was observed. FastWan's 3-step DMD sampler could bring Wan to a few minutes per clip, but it remains untested.
- **Audio.** LTX can generate audio jointly; the tests used `--no-audio`. The project's audio mix stays authoritative.

## Sources

- ltx-2-mlx README and docs/PIPELINES.md: https://github.com/dgrauet/ltx-2-mlx
- LTX-2.3 MLX q4 weights: https://huggingface.co/dgrauet/ltx-2.3-mlx-q4
- LTX-2 licence: https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2
- Gemma encoder: https://huggingface.co/mlx-community/gemma-3-12b-it-4bit
- mlx-video: https://github.com/Blaizzy/mlx-video
- Wan 2.2 TI2V-5B: https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B
- Wan MLX q8: https://huggingface.co/Anes1032/Wan2.2-TI2V-5B-mlx-q8
- FastWan MLX: https://huggingface.co/lBroth/FastWan2.2-TI2V-5B-MLX
- FastVideo base: https://huggingface.co/FastVideo/FastWan2.2-TI2V-5B-FullAttn-Diffusers
- AnimeGen I2V MLX (43 GB peak): https://huggingface.co/mlx-community/AnimeGen-I2V-A14B-Lightning-int4
- Real-ESRGAN: https://github.com/xinntao/Real-ESRGAN (releases v0.2.5.0)

## 7. AK01 sample production (2026-11-17, in progress)

Status: **sample, not finished, awaiting owner review.** At the laptop's 17:00 close, 5 of 11 shots were animated, and a "first look" cut of 4 shots was made in Hindi and English. Nothing was integrated into the pipeline, published or scheduled. All files are in `data/anim_lab/` (gitignored). The resume steps are in `data/anim_lab/AK01/STATE.md`.

### 7.1 Character consistency method (tested, then locked)

| Method | Result |
|---|---|
| Z-Image Turbo, same prompt and seed, view words changed (`refs/_test/z_*`) | Fails. The crown design, the shawl colour and the face all change between front, three-quarter and profile views. |
| **FLUX.2 klein 4B edit**, conditioned on the character's front anchor (`refs/_test/k_*`) | **Chosen.** The crown, beard, jewellery and costume hold across three-quarter view, full body and expressions. "Profile" requests come out as a strong three-quarter view, not a true profile. |

Locked pipeline:
1. **Style.** Use the owner-approved benchmark look (`keyframes/king.png`): "anime film still, painterly cel-shaded animation …". A first flat storybook pass was rejected in coordinator review and archived in `refs/_flat_v1/`.
2. **Front anchors.**
   - Dasharatha: klein edit of king.png, which keeps its crown, face and beard.
   - Rama: klein portrait using king.png for style only, then a klein skin-tone edit.
   - Manthara: klein portrait using king.png for style only.
   - Sita: Z-Image with the same prefix, seed 11.
   - Two candidates per character were compared. The owner and coordinator approved Dasharatha, Rama and Manthara; Sita was picked by the same criteria.
3. **Every shot keyframe** is a klein edit whose references are the anchors of the characters in the shot plus a locked location plate.
4. **Character shots** add a klein "end anchor" image, an edit of the keyframe showing the end pose. It is passed to LTX as `--image end.png last 0.7`.
5. **Registry.** Paths, sha256 hashes, exact prompts and seeds are recorded in `profiles/characters/ayodhya_kanda.json` under `locked_refs`. This covers the 4 characters, the 5 locations and all 11 AK01 keyframes with their motion prompts.

Results:
- All 10 usable keyframes are on-model across shots: Dasharatha in shots 1, 2, 3, 6, 7 and 8; Rama in 5, 6, 8 and 9; Sita in 9; Manthara in 11.
- The s04 keyframe (peacocks) was rejected because the cloud reads as a smoke plume. Its prompt is fixed in `shots.py`, and it must be regenerated.

### 7.2 Per-step time and memory (M5 Air 16 GB)

The owner's Android emulator, Gradle and Flutter processes were open until about 15:45, which roughly doubled image times.

| Step | Wall time | Peak footprint | Swap growth |
|---|---|---|---|
| Z-Image anchors, 12 at 768×1024 (flat style, superseded) | 16 min | ~2.3 GB RSS | +7.9 GB |
| klein test, 9 images at 768×1024 | 11 min (69–83 s each) | 12.5 GB | +5.2 GB |
| Voice, en (Kokoro) + hi (Maya 2 Malini), 22 lines | 60 s | 6.6 GB | 0 |
| klein cinematic candidates, 5 images | 3.5 min (23–50 s each) | 12.5 GB | +4.8 GB |
| Z-Image cinematic locations, 5 | 8 min | 12.6 GB | +5.9 GB |
| klein shot keyframes, 11 at 576×1024 | 14.7 min (58–123 s each) | 14.5 GB | +6.8 GB |
| klein end anchors, 2 | 2 min | 12.5 GB | +3.3 GB |
| **LTX s01**, 97 frames | **6 min 1 s** | 8.2 GB | +4.2 GB |
| **LTX s10**, 121 frames | **7 min 31 s** | 8.6 GB | +2.2 GB |
| LTX s05, 97 frames (rejected) | 8 min 6 s | 8.6 GB | +2.1 GB |
| **LTX s09**, 121 frames | **10 min 9 s** | 8.7 GB | +9.2 GB |
| **LTX s05r**, 97 frames (retake) | **8 min 41 s** | — | +7.8 GB |
| LTX s06, 97 frames | see `AK01/progress.log` | | |
| First-look render, en + hi | about 1.5 min per language | ~2 GB | — |

- **LTX timing.** With `LTX2_SPLIT_TEXT_ENCODE=1`, `--low-ram` and the emulator closed, LTX-2.3 q4 distilled took **6–10 min per clip**, against 12–22 min in the benchmark.
- **Total heavy-model time so far:** about 2 h 10 min. Wall time from start, including the Ep09 pause and the session restart, was about 2 h 50 min.
- **Cost:** ₹0.
- **Watchdog.** Swap sat at a 15–22 GB baseline from stale emulator pages while 55–66% of RAM was free. An absolute swap cap killed valid runs, so the wrapper (`bin/akrun.sh`) now aborts only on real thrashing: free memory below 8% for three checks in a row, or swap growth above 14 GB.

### 7.3 Shot review (contact sheets in `AK01/clips_raw/*_sheet.png`)

| Shot | Verdict |
|---|---|
| s01 king at the window (hook) | **Good.** Real motion: push-in, the king lifts his gaze to the sky, then a worried brow (end anchor). Crown, beard and costume stable. The meteor is faint. |
| s10 royal road | **Excellent.** Crane up with true parallax, people walking, banners and lamps moving. |
| s09 Rama and Sita at the fire | **Good.** Slow push-in, both close their eyes, fire and smoke animate. Faces stay consistent. |
| s05 Rama close-up, take 1 | **Rejected.** He spins a full turn and the crown morphs during the turn. |
| s05r retake (calm prompt, seed 7, end anchor) | No spin. He lowers his gaze and smiles, hair and cloth move in the breeze. **Flaw:** mid-clip the crown shrinks and changes shape, then the end anchor restores it. Usable for review; retake again (73 frames or another seed) for the final. |

### 7.4 Audio, captions, end card

- **Mix.** Narration is normalised to −16 LUFS. The music is the procedural tanpura and bansuri bed, with Ayodhya motifs added at runtime (`dasharatha`, `ayodhya`, `kaikeyi`) plus a procedural nagada pulse. SFX come from the `chalk.sfx_*` set. Ducking is studio `duck_v2` at −20 dB. Two-pass linear loudnorm gives −14.1 LUFS and TP −1.7/−2.1 dBTP on the full mixes, and −13.9 and −13.8 LUFS on the first looks.
- **Captions.** Studio `Captioner` with the approved chalk caption style: ChalkboardSE for English, Kohinoor for Hindi. Titles are Chalkduster gold with a dark halo. The first look used proportional caption timing, because Whisper word alignment was deferred so it would not run alongside LTX.
- **Opening and end card.** The first shot opens with a 0.6 s chalk-line-to-paint Kanda bridge. The end card is a chalk board with the bow mark, "Next: Manthara's Whisper", and a visible "AI-generated animation" note, because the LTX-2 Community Licence requires disclosure.
- **Voice QA.** `speaker_consistency` has not been run yet. The pipeline check takes `data/heavy.lock` itself, so wrapping it in the lock wrapper deadlocked. Run it directly on resume.

### 7.5 Licences of everything used

| Asset | Licence |
|---|---|
| FLUX.2 klein 4B (`black-forest-labs/FLUX.2-klein-4B`, ungated) and the q8 MLX conversion `mflux-community/flux2-klein-4b-mflux-q8` | Apache-2.0, verified from HF API metadata on 2026-11-17 |
| mflux 0.24.0 | MIT |
| Z-Image Turbo | Apache-2.0 (existing project model) |
| LTX-2.3 q4 | LTX-2 Community Licence (free under USD 10M revenue; outputs must be disclosed as AI-generated) |
| Gemma 3 12B | Gemma Terms |
| ltx-2-mlx | MIT |
| Kokoro-82M | Apache-2.0 |
| Maya 2 Native | Apache-2.0 |
| Music, SFX, fonts | Procedural (own code) for music and SFX; macOS system fonts as already used by the channel |

No Real-ESRGAN: the weights' licence is unclear. Upscaling is Lanczos to 1080×1920 plus a light unsharp mask.

### 7.6 Known limitations

- 6 of 11 shots are not animated yet: 2, 3, 4, 7, 8 and 11. Shot 6 finished at the stop; check its contact sheet.
- s05 has a crown wobble. Rama's crown is nearly as grand as Dasharatha's; a smaller Yuvaraja diadem is recorded as a planned variant in the bible.
- klein does not produce true profiles.
- Character sheets (three-quarter, profile, full body and expressions in the cinematic style) were not regenerated after the style change. Only the fronts are locked.
- First-look captions use estimated timing.

### 7.7 Compared with the chalk style

- **Pros.** Characters and places now visibly act and move: head turns, eyes closing, fire, crowds, a crane move. The look matches the owner-approved benchmark, and faces stay consistent across shots through the locked anchors.
- **Cost.** Chalk renders an episode in minutes. This look needs about 1.5–2 h of serial heavy-model time per episode with the emulator closed, plus occasional retakes; about 1 in 5 clips was rejected here.
- **Brand continuity.** The chalk title fonts, the chalk bridge and the end card keep the Chalk Tales identity.
