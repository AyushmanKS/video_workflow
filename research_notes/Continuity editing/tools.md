# Continuity editing: free tools for the local pipeline

Research date: 2026-11-17. Target: automated continuity editing of AI-animated 9:16 Shorts (1080×1920, 30 fps, about 50 s, 11 shots of 4–5 s) on a MacBook Air M5, 16 GB, fanless.

**Status labels**
- **Verified**: read from the official LICENSE (GitHub API), the HF model card or API, the official docs, or the locally installed docs.
- **Measured**: timed on this machine today. Scratch outputs are in `/private/tmp/claude-501/.../scratchpad/ct`. No project clip was modified.
- **Reported**: secondary source.
- **Unverified**: prior knowledge only.

## 0. What already exists (reuse first)

**AK01 assembly.** `data/anim_lab/AK01/scripts/assemble.py` reads every clip with OpenCV. The clips are 576×1024 at 24 fps, 97–121 frames. Per frame it:
- retimes the clip with `clip_frame`, a linear blend of two frames at a rate clamped to 0.75–1.25×
- applies `deflicker`, an HSV V-gain on dark frames
- upscales with PIL Lanczos and an unsharp mask
- for the transitions in `XFADE`, hand-rolls a crossfade or a dip
- composites titles, the verse and captions with PIL/raqm
- pipes rgb24 frames into `ffmpeg libx264 crf 17`, with two-pass `loudnorm` on `mix.wav`

Audio comes from `studio.duck_v2` (numpy ducking), the procedural `chalk` music/SFX and `studio.lufs`.

So the pipeline is already a **numpy frame compositor with ffmpeg as the encoder**. The cheapest wins are numpy/OpenCV analysis plus the ffmpeg filters, not a new NLE.

**Installed now.**
- **ffmpeg 9.0.1** (Homebrew).
  - Build flags: `--enable-gpl --enable-version3`, so it is **GPLv3**. VideoToolbox and AudioToolbox are enabled.
  - **Missing:** `drawtext`, `vidstab` (no libvidstab), `subtitles`/`ass`, `rubberband`, `zscale`.
  - **Present:** `xfade`, `acrossfade`, `afade`, `sidechaincompress`, `sidechaingate`, `minterpolate`, `framerate`, `tblend`, `scdet`, `zoompan`, `lut3d`, `haldclut`, `haldclutsrc`, `colortemperature`, `eq`, `curves`, `gblur`, `avgblur`, `loudnorm`, `v360`.
- **`.venv` (Python 3.12; no pip inside, use `uv`):** av 19.0.2, opencv-python 5.0.0.93, pillow 13.0.0, numpy 2.5.4, scipy 1.18.1, torch 2.15.0 (MPS available: True), torchvision 0.29.2, timm 1.0.31, transformers 5.23.0, kornia 0.9.1, mlx 0.32.4, mflux 0.24.0, onnxruntime 1.32.0, soundfile, matplotlib, faster_whisper, speechbrain.
- **Not installed:** moviepy, scikit-image, colour-science, scenedetect, vidgear, librosa, pyloudnorm, pedalboard, open_clip, sox, blender, melt.
- **DaVinci Resolve 21.1.2** is installed in `/Applications`. Edition (Free or Studio) was not determined, because the app was not launched.
- `docs/TOOLS_AND_SKILLS_RESEARCH.md` already settles these points:
  - Sonniss GDC 2026 and Freesound CC0 for SFX
  - pyloudnorm (MIT)
  - pedalboard rejected (GPL-3)
  - Practical-RIFE (MIT)
  - FILM archived
  - Q-DDL LUTs CC BY 4.0, no CC0 pack found
  - PySceneDetect as an optional QA helper

## 1. Local smoke tests (Measured, M5 Air, 2026-11-17)

| Test | Input | Wall time | Note |
|---|---|---|---|
| `xfade=fade` 0.4 s, both clips upscaled to 1080×1920 at 30 fps, libx264 `-preset medium -crf 17` | s01 + s02 (8.63 s out) | **2.66 s** | about 3.2× realtime, including encode |
| `xfade` fadeblack / smoothleft / circleopen / dissolve / hblur / zoomin, `-preset veryfast` | same | 0.95–1.01 s each | all 6 render fine |
| same, with `h264_videotoolbox -b:v 12M` | same | 1.16 s | hardware encode is no faster here; the filter graph dominates |
| `minterpolate` 24→30 fps, `mci/aobmc/bidir/vsbmc` at 576×1024 | s01 (4 s) | **6.25 s** | about 1.5 s per output second at native resolution, CPU only |
| `setpts=2*PTS,minterpolate` (0.5× slow-mo) | s01 | 10.3 s | for an 8 s output |
| `framerate=fps=30` (blend-based) | s01 | 0.13 s | cheap, but it ghosts |
| `scdet` at 270p | crossfade output | score 20.5 at 3.63 s | a 0.4 s fade still registers as a "cut"; the threshold must be tuned |
| `scdet` at 270p | hard concat s01→s02 | score 28.0 at exactly 4.0417 s | reliable hard-cut detector |
| `haldclutsrc=8` → `colortemperature,eq,curves` → `haldclut` | s02 | 0.10 s + 0.51 s | **procedural LUT works with no LUT pack** |
| `tblend=all_mode=average` | s01 | 0.12 s | cheap motion-blur or frame-smear |
| `zoompan` Ken Burns, 150 frames at 1080×1920 from a 2160×3840 still | still | 0.94 s | |
| `sidechaincompress` (music keyed by narration), `acrossfade d=0.3`, `afade` | `work_en/mix.wav`, narration 00/01 | 0.02–0.04 s | trivial |
| OpenCV Farneback flow at 152×270 | s01/s02/s07, 97–121 frames | **2.75–2.89 ms per pair** (0.26–0.35 s per clip) | gives mean (dx, dy) per frame; s02 shows a tail downward drift of +0.14 px/frame |
| OpenCV DIS MEDIUM / FAST at 152×270 | same | 2.2–2.4 / 1.1–1.2 ms per pair | DIS FAST matches Farneback's direction on s02 at 2.5× the speed |
| DINOv2-small (HF, Apache-2.0) on MPS | first and last frames of 11 clips (22 images) | load 13.5 s (incl. download); **embed 0.78 s**; peak RSS 1.07 GB | cut similarities: [0.56, 0.81, 0.27, 0.19, 0.62, 0.54, 0.75, 0.69, 0.36, 0.64]; s03→s04 and s04→s05 are the least similar |
| SigLIP2-base-patch16-224 (Apache-2.0) on MPS | same 22 images | embed 0.90 s; peak RSS 2.47 GB (load 160 s was mostly download) | cut similarities 0.64–0.94, same ranking pattern; less discriminative than DINOv2 for visual continuity |
| scikit-image `match_histograms`, s04 first frame → s03 last frame | 576×1024 | **7 ms** | mean-Lab ΔE2000 25.7 → 0.28; SSIM at 270p 0.154 → 0.215 (SSIM 5 ms) |
| PySceneDetect 0.7.3 `AdaptiveDetector` | 9 s hard-cut concat | 0.07 s | cut found at exactly 4.0417 s |
| librosa 1.0.1 `onset_detect` + `beat_track` | 48 s `mix.wav` | 2.5 s | 217 onsets, about 99 BPM, 78 beats |
| pyloudnorm | `work_en/mix.wav` | — | −14.05 LUFS integrated, which matches the pipeline's −14 target |

The scikit-image/colour/scenedetect/librosa/pyloudnorm tests ran in a throwaway `uv run --no-project --with …` environment, so `.venv` is untouched. The total cold install for that environment was about 90 s.

The HF models were downloaded to a scratch `HF_HOME` (1.5 GB) under the scratchpad; the user's HF cache was not touched.

## 2. Evaluations

### 2.1 DaVinci Resolve (Free)

- **Free?** Yes. Free Resolve has no watermark.
- **Commercial output.** A Blackmagic support rep answered "Yes" to commercial use of the free version ([forum](https://forum.blackmagicdesign.com/viewtopic.php?p=905205)). This is Reported, because the EULA text itself was not read.
- **Scripting.** The local `Developer/Scripting/README.md` (CHANGELOG "Last Updated: 22 Oct 2026", v21.1.2) is Verified:
  - "In DaVinci Resolve Studio, Preferences > System > General, you can configure: External scripting (None, Local, Network)".
  - "API calls can return False … when the function references a Studio function from the free DaVinci Resolve version".
  - `-nogui` headless mode exists. The render API exists: `AddRenderJob`, `StartRendering`, `SetRenderSettings`, and in 21.1.2 also transition properties, `SetLUT`, `ApplyGradeFromDRX` and `ExportFrame`.
- **Free edition from 21.1.** Puget Systems (2026-09-10) quotes Blackmagic: **"We have moved the ability to script in Python to the Studio version"**, because "the Python API was being used to hack studio features into the free version" ([Puget](https://www.pugetsystems.com/blog/2026/09/10/how-davinci-resolve-free-v21-1-scripting-changes-affect-puget-bench/)). This is Reported, but it is consistent with the README. Even before 21.1, external scripting in Free was unsupported; only the internal Console was ([BMD forum](https://forum.blackmagicdesign.com/viewtopic.php?p=677825)).
- **Conclusion.** **Python automation of Free Resolve is effectively gone from 21.1.** The only paths left are Studio ($295, which breaks zero cost), pinning v21.0, or unofficial FCPXML or UI-automation hacks. All three are rejected.
- **Apple Silicon.** Resolve 21 needs Apple Silicon and macOS 15+. Memory needs: 8 GB minimum, 16 GB for Fusion, 32 GB recommended for background render/AI ([BMD readme](https://www.blackmagicdesign.com/support/content/readme/1dcfa6f38ebc4031a3a8561eea3aeee3); Reported, and the page is inconsistent). The installed `Info.plist` sets `LSMinimumSystemVersion` to 15.0 (Verified).
- **Verdict.** **Do not integrate.** It stays useful as a *manual* owner-side viewer or grader only.

### 2.2 FFmpeg filter graphs (installed)

- **Licence.** This build is GPLv3 (`--enable-gpl --enable-version3`, Verified via `-buildconf`). GPL governs *distributing the ffmpeg binary or linked code*, not the videos it produces. Calling it via subprocess from a private pipeline creates no obligation.
- **`xfade`** (Verified, local `-h filter=xfade`), the full transition list:
  - fades: `fade`, `fadeblack`, `fadewhite`, `fadegrays`, `fadefast`, `fadeslow`, `dissolve`, `distance`
  - wipes: `wipeleft/right/up/down`, `wipetl/tr/bl/br`
  - slides: `slideleft/right/up/down`
  - shapes: `circlecrop`, `rectcrop`, `circleopen/close`, `vertopen/close`, `horzopen/close`, `radial`
  - smooth wipes: `smoothleft/right/up/down`
  - diagonals: `diagtl/tr/bl/br`
  - slices: `hlslice`, `hrslice`, `vuslice`, `vdslice`
  - effects: `pixelize`, `hblur`, `squeezeh/v`, `zoomin`
  - winds: `hlwind`, `hrwind`, `vuwind`, `vdwind`
  - covers and reveals: `coverleft/right/up/down`, `revealleft/right/up/down`
  - `custom` with an `expr`

  Parameters are `duration` and `offset`. For continuity editing only these matter: `fade`, `fadeblack` (dip), `dissolve`, `hblur`, `smooth*` (directional match on motion) and `custom`. The rest read as "template editor".
- **`acrossfade`** (`d`, curves `c1`/`c2`: tri, qsin, esin, log…), **`afade`**, and **`sidechaincompress`**/**`sidechaingate`** (threshold, ratio, attack, release, makeup) all work (Measured). They could replace `duck_v2`, but `duck_v2` already exists and is tuned. Keep it. Use `acrossfade` and `afade` for J/L-cut audio pre-roll.
- **`minterpolate`** (`mi_mode=mci`, `mc_mode=aobmc`, `me_mode=bidir`, `vsbmc=1`). This is motion-compensated interpolation for 24→30 conversion and speed ramps. It costs about 1.5 s per output second at 576p on CPU (Measured). Known warping and halo artefacts on large motion (Unverified for these clips; check visually).
  - **Use:** replace the linear blend in `clip_frame` when the rate is not 1.0, *at 576p before the upscale*.
- **`framerate`**: blend-only, cheap, ghosts. Equivalent to the current `clip_frame`.
- **`tblend`**: frame averaging. Useful for a 1–2 frame motion-blur "whip" on cuts that match on motion.
- **`zoompan`**: Ken Burns on stills. It jitters at sub-pixel zooms unless the source is pre-upscaled (Reported). numpy/cv2 `warpAffine` with float coordinates is smoother and is already in the stack.
- **`lut3d`** (`.cube`/`.3dl`), **`haldclut`** (with `haldclutsrc` for a procedural identity), **`colortemperature`**, **`eq`** and **`curves`** (presets or points) all work. Grading can be fully procedural with no LUT pack (Measured, 0.5 s per clip).
- **`vidstab`: not in this build.** Homebrew core ffmpeg has no libvidstab; libvidstab 1.1.2 (GPL-2.0+ per brew; the upstream repo text says LGPL-2.1+) would need the `homebrew-ffmpeg` tap build (Unverified). AI clips seldom need stabilising. Shot-level jitter can be measured with the OpenCV flow already used in §2.3 and countered with `cv2.warpAffine`.
- **`scdet`**: hard cuts score about 28, a 0.4 s fade about 20 (Measured). Good as a QA "unexpected cut/flash inside a shot" detector at 270p.
- **Maintenance.** Very active; 9.0.1 is installed.
- **Verdict.** **Rank 1 (reuse).**

### 2.3 Python libraries

| Lib | Licence (Verified, GitHub API) | Last push / release | M5 status | Role for continuity |
|---|---|---|---|---|
| **numpy / scipy / Pillow** | BSD / BSD / MIT-CMU (HPND) | active | installed | already the compositor |
| **OpenCV 5.0** | Apache-2.0 | 2026-11-17 | installed; Farneback 2.8 ms and DIS-FAST 1.1 ms per pair at 270p (Measured) | per-shot **motion vector** (mean dx, dy, magnitude, head and tail), screen-direction matching, jitter, `warpAffine` camera moves, flow-warped crossfades |
| **PyAV 19** | BSD-3-Clause | 2026-11-16 | installed | frame-accurate decode with PTS; can replace `cv2.VideoCapture` and the stdin pipe (writes via libav, no subprocess) |
| **scikit-image** | BSD-3-Clause (LICENSE.txt) | 2026-11-17 | not installed; wheel OK (Measured via uv) | `match_histograms` (7 ms, ΔE 25.7 → 0.3), `structural_similarity` for continuity scoring |
| **colour-science 0.4.7** | BSD-3-Clause | release 2025-12-06, push 2026-11-17 | not installed; works (Measured) | ΔE2000 between shot ends, `.cube` write via `colour.io.write_LUT`, CCT estimates |
| **PySceneDetect 0.7.3** | BSD-3-Clause | release 2026-11-08 | not installed; works (Measured, 0.07 s) | QA: flags internal cuts and flashes in generated clips; `scdet` covers the same need |
| **MoviePy 2.2.1** | MIT | release 2025-05-21; push 2026-08-26 | not installed | adds nothing: it wraps ffmpeg plus numpy per frame, which `assemble.py` already does, and it is slower. Skip |
| **vidgear** | Apache-2.0 | 2026-11-15 | not installed | `WriteGear` is just an ffmpeg pipe wrapper (as in the current Popen). Skip |
| **kornia 0.9.1** | Apache-2.0 | installed | MPS (Unverified for every op) | GPU warps and colour ops if numpy becomes the bottleneck. Not needed for 11 clips |

### 2.4 Frame interpolation

- **Practical-RIFE.** Code is MIT (Verified). README: "The content of these links [trained models] is under the same MIT license as this project", and "4.24+ is quite suitable for post-processing of some diffusion model generated videos". The recommended model is 4.25 (2024-09-19). Last push 2026-08-27.
  - Weights are Google Drive links upstream. HF mirrors tagged MIT include `mlx-community/RIFE-4.25` (MLX safetensors, 2026-06-06) and `daydreamlive/RIFE` (`flownet.pkl`), Verified via the HF API. That RIFE runs on Apple Silicon via PyTorch MPS or MLX is Reported, not Measured here.
  - Expected to run at near-realtime at 576×1024 on MPS (Unverified). The model is small (tens of MB), so RAM is fine.
  - **Use:** smooth slow-mo or speed ramps and 24→30 conversion with far fewer warp artefacts than `minterpolate`. **Do not use it to bridge two different shots**: it morphs, which violates the "morph-free" goal.
- **`nihui/rife-ncnn-vulkan`.** MIT, last push 2024-01-02. Runs on Vulkan via MoltenVK. A fallback only.
- **FILM** (google-research/frame-interpolation). Apache-2.0, **archived** (Verified; last push 2024-08-10). TensorFlow. Skip.
- **ffmpeg `minterpolate`.** Zero install; about 1.5 s per output second at 576p (Measured). The fallback.

### 2.5 Shot similarity and semantics

| Model | Weights licence (Verified, HF API/LICENSE) | Measured on M5 MPS | Notes |
|---|---|---|---|
| **DINOv2-small** (`facebook/dinov2-small`) | Apache-2.0, ungated | 0.78 s for 22 frames, 1.07 GB RSS | best for *visual* continuity (layout, colour, subject). Clear separation: 0.19–0.81 across AK01 cuts |
| DINOv2-base | Apache-2.0 | not run | about 2× the cost of small |
| **SigLIP2-base-p16-224** | Apache-2.0, ungated | 0.90 s for 22 frames, 2.47 GB RSS | text-image matching (does the shot match "Rama embraces Dasharatha"?). Narrower spread (0.64–0.94) for visual continuity |
| OpenCLIP (code) | MIT-style (Verified, LICENSE text); repo SPDX shows NOASSERTION | not run | `laion/CLIP-ViT-B-32-laion2B-s34B-b79K` is MIT (Verified HF) |
| `openai/clip-vit-base-patch32` | no licence tag on HF (Verified); the repo was MIT historically (Unverified) | — | prefer SigLIP2 or LAION |
| **DINOv3** | custom "DINOv3 License" (Verified header, 2025-08-19), **not Apache** | — | avoid unless terms are read in full |

All of these fit easily next to nothing else. The heavy-lock still applies: do not run them during FLUX or LTX jobs.

### 2.6 Blender (bpy headless)

- **Licence.** GPL for the application. "What you create with Blender is your sole property … images or movie files" ([blender.org](https://www.blender.org/about/license/), via search, Reported; the direct fetch returned 403).
- **Install.** Homebrew cask `blender` 5.3.0 is available (Verified). It is not installed.
- **Fit.** Feasible on M5 (Metal, Cycles/EEVEE). The VSE plus compositor via `blender -b -P script.py` can do transitions and motion graphics. Render times for 2D comp at 1080×1920 for 50 s are Unverified, probably minutes.
- **Cost.** Adds about 1 GB of app plus a second compositor to maintain, for nothing that numpy/ffmpeg cannot already do.
- **Verdict.** **Skip** (the previous research already rejected it for 2D chalk).

### 2.7 MLT `melt`, Kdenlive, Shotcut, Olive, Natron

- **MLT 7.42.0.** LGPL-2.1 (Verified, brew and GitHub; push 2026-11-17).
  - `melt` renders XML timelines headlessly. The `luma`/`mix` transitions and the `avformat` consumer are documented ([melt docs](https://mltframework.org/docs/melt/), [FAQ](https://www.mltframework.org/faq/)).
  - Kdenlive and Shotcut projects *are* MLT XML, so a script could emit a `.mlt` that the owner opens in Shotcut for manual tweaks.
  - **This is the only real "editable timeline handoff" route that is free and scriptable.**
  - Cost: `brew install mlt` (Qt dependencies), plus a second render path that duplicates `assemble.py`.
  - **Verdict:** optional, later, only if the owner wants to hand-tweak cuts.
- **Kdenlive 26.08.3 / Shotcut 26.9.28.** GPL-3.0 (Verified). Actively maintained. GUI apps, automatable only through MLT XML.
- **Olive.** GPL-3.0, last push 2024-12-05, no GitHub release. **Stalled alpha.** Skip.
- **Natron.** GPL-2.0, last release v2.5.0 on 2022-11-26, although the repo still gets pushes. Effectively in maintenance. Skip.

### 2.8 Audio

- **ffmpeg audio filters** (installed): `acrossfade`, `afade`, `adelay`, `sidechaincompress`, `loudnorm` two-pass (already used). **Reuse.**
- **SoX 14.4.2.** GPL-2.0+/LGPL-2.1+ (brew, Verified). The upstream repo's last push was 2023-11-24, so it is dormant. Not installed. Redundant with ffmpeg plus numpy. Skip.
- **pyloudnorm.** MIT (Verified), push 2026-01-04. Measured −14.05 LUFS on `mix.wav`, consistent with `studio.lufs`. Optional cross-check only.
- **pedalboard.** GPL-3.0 (Verified). Importing it into this public MIT-less repo puts the combined Python program under GPL obligations *if distributed*; output audio is unaffected. Already rejected in `TOOLS_AND_SKILLS_RESEARCH.md`. Keep it rejected.
- **librosa 1.0.1.** ISC (Verified), push 2026-11-16. Measured 2.5 s for onset and beat on 48 s.
  - **Use:** snap cut points to narration phrase onsets or music beats, and place J/L-cut lead-ins at word or phrase boundaries.
  - The pipeline already has word timings (`studio.scene_word_times`, faster-whisper), which are better for narration-led cuts. librosa only adds value for snapping to the *music bed*.
- **Audacity.** GPL; `mod-script-pipe` exists but needs the GUI running (Unverified). Skip.
- **SFX and ambience sources** (cross-checked with `TOOLS_AND_SKILLS_RESEARCH.md` §3, unchanged):
  - Sonniss GDC 2026: royalty-free, monetised YouTube OK, no redistribution, no AI/ML training.
  - Freesound: **CC0 filter only**, because CC-BY-NC and Sampling+ are unusable.
  - Record each file in `licenses.csv`.

### 2.9 Colour

- **OpenColorIO 2.6.0.** BSD-3-Clause (Verified; push 2026-10-01). Overkill for sRGB-only AI clips with no camera log footage. Skip unless an ACES workflow is ever adopted.
- **LUT packs.** No CC0 pack was found in earlier research. Q-DDL is CC BY 4.0 (attribution required; Reported earlier, not re-verified). Commercial "free LUT" packs from vendors usually carry custom licences that need per-pack reading. **Unverified, not recommended.**
- **Recommended: procedural.**
  1. Per-episode "show look" = `colortemperature`/`eq`/`curves` baked into a `haldclutsrc` → `.png` Hald CLUT (Measured), or written as `.cube` with colour-science.
  2. Per-cut shot matching = scikit-image `match_histograms` (or a mean/std Lab transfer in numpy), **blended at about 30–60 % strength** so shots are not flattened. Evaluate it with ΔE2000 from colour-science.

### 2.10 Local AI-assisted editing tools

- **auto-editor.** Unlicense (Verified), push 2026-11-16. Cuts silence and motionless segments and exports to Resolve/Premiere/Shotcut XML. It is for talking-head footage and is irrelevant to narrated, already-timed shots. Skip.
- **TransNetV2.** MIT (Verified), last push 2023-12-04. A neural shot-boundary detector. PySceneDetect and `scdet` already cover the need. Skip.
- **LosslessCut.** GPL-2.0. GUI trimming. Skip.
- **Resolve AI tools** (IntelliSearch, Smart Reframe, etc.): Studio-only or Extras-gated, and the scripting is Studio-only (§2.1). Not free in practice.
- **No genuinely free, commercial-OK, local tool does automatic shot matching or automatic J/L cuts.** Build them from the parts above:
  - **J/L cuts:** move the picture boundary ±3–8 frames relative to the narration onsets the pipeline already computes, plus `acrossfade`/`afade` on the ambience beds.
  - **Shot matching:** DINOv2 cut similarity + OpenCV flow direction + ΔE.

## 3. Ranked recommended toolchain (reuse first)

| Rank | Tool | Status | Job in the continuity pass | Cost to adopt |
|---|---|---|---|---|
| 1 | **numpy + PIL + ffmpeg pipe in `assemble.py`** | installed | stays the compositor; add J/L offsets, motion-matched cut frames, flow-warped or dip transitions | none |
| 2 | **OpenCV 5 (Farneback / DIS)** | installed | per-shot head/tail motion vectors at 270p (about 0.1–0.35 s per clip) → choose the cut frame, the transition type (cut if the motion continues, dip or dissolve if it reverses), screen-direction QA, a jitter metric | none |
| 3 | **ffmpeg filters**: `xfade` (fade/fadeblack/dissolve/hblur/smooth*), `acrossfade`/`afade`, `minterpolate`, `haldclut`/`lut3d`/`eq`/`curves`/`colortemperature`, `scdet`, `tblend` | installed | either in-graph or replicated in numpy; procedural grade CLUT; `scdet` QA; `minterpolate` replaces `clip_frame` blending for retimes | none |
| 4 | **DINOv2-small** via transformers on MPS | transformers/torch installed; weights about 90 MB, Apache-2.0 | rank cut pairs by visual continuity (AK01: s03→s04 at 0.27 and s04→s05 at 0.19 are the weakest); flag pairs that need a dip or reorder; optional SigLIP2 for shot-vs-script text checks | 1 small download |
| 5 | **scikit-image + colour-science** | `uv add` (BSD-3) | per-cut partial histogram match; ΔE2000 before/after as a QA metric; `.cube` writing | about 2 wheels |
| 6 | **PyAV** | installed | frame-accurate decode with PTS (replace `cv2.VideoCapture`); optional direct encode | none |
| 7 | **Practical-RIFE 4.25** (MIT code + weights) | not installed; HF MLX/PyTorch mirrors | only for speed ramps or slow-mo within a shot, never across a cut; fallback is `minterpolate` | about 50 MB weights + glue; M5 speed Unverified |
| 8 | **librosa** (ISC) | `uv add` | snap cuts to music-bed beats; narration cuts keep using the existing word timings | small |
| 9 | **PySceneDetect** (BSD-3) | optional | QA duplicate of `scdet` with a nicer API | small |
| 10 | **MLT `melt` + Shotcut** (LGPL/GPL) | not installed | optional MLT XML export for owner hand-tweaks | brew + Qt; second render path |
| — | **Rejected:** DaVinci Resolve automation (Studio-only Python from 21.1), Blender, MoviePy, vidgear, SoX, pedalboard, OpenColorIO, LUT packs, Olive, Natron, FILM, DINOv3, auto-editor, TransNetV2 | | | |

## 4. Open items

- Edition of the installed Resolve 21.1.2 (Free or Studio). Irrelevant unless Studio is already licensed.
- Resolve EULA text for commercial use (forum confirmation only).
- RIFE 4.25 speed and quality on the M5, MPS vs MLX, at 576×1024. Not run, because the weights are only on Google Drive upstream or in HF mirrors.
- `minterpolate` artefacts on AK01 shots with large motion: needs a visual check by the owner.
- Blender headless render time on the M5: not measured (Unverified).
- libvidstab licence: brew says GPL-2.0+, the upstream README says LGPL-2.1+. Moot, because it is not in the build.

## Sources

- Local: `ffmpeg -buildconf`, `ffmpeg -h filter=xfade`, `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/README.md` and `CHANGELOG.md` (21.1.2), Resolve `Info.plist`, `.venv/lib/python3.12/site-packages`, `brew info`.
- GitHub API (licence, archived flag, pushed_at, latest release), queried 2026-11-17: Zulko/moviepy, PyAV-Org/PyAV, opencv/opencv, scikit-image/scikit-image, colour-science/colour, Breakthrough/PySceneDetect, abhiTronix/vidgear, hzwer/Practical-RIFE (README model-licence line), google-research/frame-interpolation, mlfoundations/open_clip, facebookresearch/dinov2, facebookresearch/dinov3 (LICENSE.md), mltframework/mlt, KDE/kdenlive, mltframework/shotcut, olive-editor/olive, NatronGitHub/Natron, chirlu/sox, librosa/librosa, csteinmetz1/pyloudnorm, spotify/pedalboard, AcademySoftwareFoundation/OpenColorIO, georgmartius/vid.stab, nihui/rife-ncnn-vulkan, WyattBlue/auto-editor, soCzech/TransNetV2, mifi/lossless-cut, ManimCommunity/manim.
- HF API: google/siglip2-base-patch16-224, google/siglip-base-patch16-224, facebook/dinov2-small, facebook/dinov2-base, openai/clip-vit-base-patch32, laion/CLIP-ViT-B-32-laion2B-s34B-b79K, timm/ViT-B-16-SigLIP2, mlx-community/RIFE-4.25, daydreamlive/RIFE.
- Web:
  - [Puget Systems, 2026-09-10](https://www.pugetsystems.com/blog/2026/09/10/how-davinci-resolve-free-v21-1-scripting-changes-affect-puget-bench/)
  - [BMD forum, external scripts in Free](https://forum.blackmagicdesign.com/viewtopic.php?p=677825)
  - [BMD forum, commercial use of Free](https://forum.blackmagicdesign.com/viewtopic.php?p=905205)
  - [BMD Resolve 21 readme](https://www.blackmagicdesign.com/support/content/readme/1dcfa6f38ebc4031a3a8561eea3aeee3)
  - [blender.org licence](https://www.blender.org/about/license/)
  - [Blender FAQ](https://www.blender.org/support/faq/)
  - [MLT melt docs](https://mltframework.org/docs/melt/)
  - [MLT FAQ](https://www.mltframework.org/faq/)
  - [CineD free vs Studio](https://www.cined.com/davinci-resolve-18-6-free-vs-paid-studio-version/)
