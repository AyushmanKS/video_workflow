# Tools, models and Claude Code skills for shorts-studio

Research date: **2026-11-16**. This is a synthesis of two research notes, with no new web research:
- `research_notes/Studio upgrade research/visual_tools.md` (visual)
- `research_notes/Studio upgrade research/audio_and_claude_skills.md` (audio and Claude Code)

It was checked against `reports/Shorts studio voices and tools.md` (the earlier report), `PROJECT_CONTEXT.md` §6 (current tools) and `docs/WORKFLOW_AUDIT.md` (audit findings).

Constraints applied throughout:
- Zero cost.
- Licenses must allow commercial use and monetization.
- Hardware is a MacBook Air M5 with 16 GB, fanless, about 92 GB of free disk.
- Never run two heavy models at once.
- Reuse existing components where possible.
- The approved chalk look and `CHALK_SFX_GAIN = 0.035` stay.

**Status labels** (as given in the notes):
- **Verified**: read from the official LICENSE, the official HF card or API metadata, or the official README.
- **Mirror**: license read from a community or Comfy-Org mirror. Verify upstream before use.
- **Unverified**: secondary source or prior knowledge only.

Where the notes recorded a status with no URL, the claim says "Verified (notes)" or similar and has no link.

**Speeds.** No source measured anything on an M5 Air. Every speed below is quoted with its source hardware. Treat each one as an upper bound for the fanless Air.

---

## 1. Summary: ranked shortlist

Abbreviations:
- **Effort**: S = under half a day, M = 1–3 days of glue code, L = longer or overnight runs.
- **Gain**: estimated from the notes, not measured.
- **Account** column: "none stated" means the notes record no gating. Check on first download.

| # | Tool / change | What it does for us | Free? | Local on M5 16 GB (RAM / disk) | Account / key / HF login | License (weights + code), status | Integration point | Effort | Expected gain | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Two-pass linear `loudnorm` + pre-mix narration normalization** (ffmpeg 9.0.1, optional `pyloudnorm`) | Applies one gain instead of dynamic pumping and lands on −14 LUFS (finals are currently −15.2 to −14.7). Keeps the bed level consistent across voices and languages | Yes | Yes; negligible / 0 | None | ffmpeg LGPL/GPL (already installed); pyloudnorm MIT, Verified ([repo](https://github.com/csteinmetz1/pyloudnorm)) | `studio.py` `step_render` ffmpeg call (`:705`); narration stem in `step_audio` (`:630`); `pipeline/qa.py` `check_loudness` (`:42`) | S | Medium (consistency, no pumping) | **Install** |
| 2 | **Fail-closed G3 `PreToolUse` hook** (`"onFailure": "block"`) | Turns G3 from an instruction into a mechanical block on `python -m pipeline publish*` and `data/upload_queue.sh` | Yes | n/a | None | Claude Code feature, Verified ([hooks docs](https://code.claude.com/docs/en/hooks)) | New `.claude/settings.json` (none exists today) plus a checker that reads the manifest via `pipeline/__main__.py` `require()` (`:43`), `cmd_publish` (`:225`) | S–M | High (safety; addresses audit headline finding 2) | **Install** (build in repo) |
| 3 | **FLUX.2 [klein] 4B**: reference-locked scenes and edit cleanup | Up to 4 reference images per render, so character sheets lock identity. Edit passes remove stray borders and figures | Yes | Community mflux 4-bit about 4 GB disk; peak RAM not reported. M1 Max: 1024² in 31.7 s wall, edit with a reference in 52–53 s ([lilting.ch](https://lilting.ch/en/articles/flux2-klein-4b-mflux-iris-m1-max)) | None (ungated) | Apache-2.0 weights, Verified ([HF](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)); mflux MIT ([repo](https://github.com/filipstrand/mflux)) | `studio.py` `step_images` (`:289`) gets a `scene_with_refs` path; sheets in `profiles/characters/`; bible `profiles/characters/ramayana.json` | M | High (fixes audit H6: text-only consistency; reduces reliance on the ignored negative prompt, H5) | **Test first** |
| 4 | **Mask-based multiplane parallax** (BiRefNet or SAM 2.1 masks plus our own numpy renderer) | Real depth motion instead of a flat zoom; the chalk look is untouched because the board is procedural | Yes | BiRefNet about 1 GB on MPS; SAM 2.1 small/tiny on MPS/CPU; seconds per scene (not timed) | None stated | BiRefNet MIT, Verified ([HF](https://huggingface.co/ZhengPeng7/BiRefNet)); SAM 2.1 Apache-2.0 code and weights, Verified ([HF](https://huggingface.co/facebook/sam2.1-hiera-small)) | `chalk.py`: after `chalk_from_image` (`:96`), per-plane `cam_matrix` (`:311`), board `make_board` (`:47`) moves with the far plane | M (about 150–250 lines) | High | **Test first** |
| 5 | **Depth Anything V2 Small** (or DA3 Small/Base) | Depth map for 2–3 plane splits on top of #4 | Yes | 25M params, about 100 MB | None stated | Apache-2.0 (Small only), Verified ([HF](https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf); [DA3-small](https://huggingface.co/depth-anything/da3-small)) | Same as #4 | S on top of #4 | Medium (unvalidated on chalk; fall back to masks) | **Test first** |
| 6 | **Procedural "alive" motion, FX and chalk transitions** (own code) | Breathing and sway on the figure mask; chalk dust, smoke and fire wisps, petals; sponge-wipe and dust-puff variants of the streak-erase | Yes | Yes / 0 | None | Own code | `chalk.py` render loop and transition code beside the approved streak-erase | M | Medium-high | **Install** (build) |
| 7 | **SFX library: Sonniss GDC 2026 bundle + Freesound CC0** with a `licenses.csv` | Conch, temple bells, tanpura and tabla accents with clean monetization terms | Yes | 7.47 GB disk (Sonniss) | Freesound: free API token for scripted search | Sonniss royalty-free, monetized YouTube explicitly allowed, Verified ([FAQ](https://sonniss.com/gameaudiogdc)); Freesound per-file CC0 filter, Verified ([FAQ](https://freesound.org/help/faq/)) | `chalk.sound` (`chalk.py:624`) / `studio.py` `step_audio`; files kept outside git under a gitignored folder | S | Medium | **Install** |
| 8 | **`audio-mix` project skill** plus `disable-model-invocation: true` on publish skills | Writes down the two-pass recipe, per-engine stem gains, SFX index and QA thresholds so agents stop re-deriving them; blocks auto-invoked publishing | Yes | n/a | None | Claude Code feature, Verified ([skills docs](https://code.claude.com/docs/en/skills)) | `.claude/skills/audio-mix/SKILL.md`; frontmatter of any publish skill | S | Low-medium | **Install** (build) |
| 9 | **Z-Image Turbo Fun ControlNet Union 2.1** | Canny, pose or depth control keeps the layout consistent between scenes and thumbnails | Yes | Add-on in mflux; about 1–3 GB (not measured) | None stated | Apache-2.0, Verified ([HF](https://huggingface.co/alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1)) | `studio.py` `step_images` (mflux flag) | S | Medium | **Test first** |
| 10 | **Chalk style LoRA** via `mflux-train` (Z-Image base or klein base 4B) | Fixes the "shaded pastel, not line art" limitation; trained on approved frames | Yes | RAM-tight. CUDA reference: about 10–10.8 GB ([runcomfy](https://www.runcomfy.com/es/trainer/ai-toolkit/flux-2-klein-16gb-vram-training)); no Mac figure | None | Apache-2.0 base weights, Verified; mflux MIT | `styles.py` chalk preset (LoRA path); training as a solo overnight run | L | Medium-high | **Test first** (pilot 500–1000 steps at 512 px) |
| 11 | **ACE-Step 1.5** (2B turbo DiT + 0.6B LM, MLX) | Generated instrumental bed; the card says outputs can be used commercially | Yes | README: 8–12 GB with the 0.6B LM; skip XL. No Mac timings | None stated | MIT code and weights, Verified ([repo](https://github.com/ace-step/ACE-Step-1.5); [HF](https://huggingface.co/ACE-Step/Ace-Step1.5)) | No code change: generate offline and pass `--music` (`studio.py:788`, tiled ×0.5) | S | Low-medium (audit: not a bottleneck now) | **Test first** |
| 12 | **Magenta RealTime 2 small** (230M, MLX) | Lightest generated bed; runs real-time on Air models; instrumental-first | Yes | Yes; small (exact RAM not stated) | None stated (`uv pip install "magenta-rt[mlx]"`) | Code Apache-2.0, weights CC-BY-4.0, "Google claims no rights in outputs", Verified ([HF](https://huggingface.co/google/magenta-realtime-2); [repo](https://github.com/magenta/magenta-realtime)) | Same as #11 (`--music`) | S | Low-medium; Indian timbres unknown | **Test first** (A/B against #11) |
| 13 | **Manim Community** | Maps, lineage trees and timelines for explainer beats, rendered to transparent `.mov` and composited | Yes | Yes; pip plus Cairo/Pango via brew | None | MIT, Verified (very active 2026-11-14) | Composite in `studio.py` `step_render` | M | Medium for history and science; low for story beats | **Test first** |
| 14 | **Royalty-free beds from the YouTube Audio Library** ("Attribution not required" filter) | Zero Content ID risk on YouTube | Yes | n/a | YouTube Studio login | Google help page, Verified ([help](https://support.google.com/youtube/answer/3376882)); off-YouTube use not covered | `--music` | S | Low | **Test first** (YouTube uploads only, **never Instagram**) |
| 15 | **LTX-2.3 int8 via ltx-2-mlx `--low-ram`**: one hero-shot test | First/last-frame image-to-video for at most 1–2 hero shots | Yes | About 26 GB disk plus a Gemma text encoder; "16 GB with `--low-ram`"; a 16 GB M1 took about 15 min for about 4 s ([lilting.ch](https://lilting.ch/en/articles/ltx2-wan22-mac-local-video-gen)) | Gemma text-encoder terms; gating for 2.3 not recorded | LTX-2 Community License (free under $10M revenue; no claim on output), Verified by grep only ([LICENSE-2](https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2)); ltx-2-mlx MIT ([repo](https://github.com/dgrauet/ltx-2-mlx)) | Separate venv; clip inserted in `step_render` | M–L | Unknown; style-drift risk | **Test first** (one clip, owner judges) |

Recommended order:
1. Items 1, 2, 7 and 8. These cost almost nothing and close audit gaps.
2. Then 3, then 4 and 5, then 6.
3. Then 9 and 10.
4. Then 11 and 12, on the owner's ear.
5. 13 and 15 are optional experiments.

Every visual change goes to the owner as a side-by-side sample on one existing scene before it touches an episode.

---

## 2. Visual tools

Source for this section: `visual_tools.md`. Links and statuses are inline.

The pipeline facts that drive these choices:
- Stills come from Z-Image Turbo 4-bit (mflux 0.24) at 768x1344, about 100 s each, with an 8.3 GB peak (measured locally).
- `chalk_from_image` produces an additive chalk layer over a procedural board (`make_board`), so the board never needs inpainting.
- Motion today is `cam_matrix` (zoom, focus, jitter) plus the `reveal_order` stroke reveal (connected components plus DFS).

### 2.1 Image models

| Model | Weights license (status) | 16 GB fit / Mac evidence | Verdict |
|---|---|---|---|
| Z-Image Turbo (current) | Apache-2.0, Verified ([HF](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo)) | 4-bit 5.5 GB; 8.3 GB peak; about 100 s at 768x1344 on the M5 (measured) | Keep |
| Z-Image base | Apache-2.0, Verified | Supports CFG and **negative prompts**; no Mac timing | Use for LoRA training, and wherever negatives are truly needed |
| Z-Image-Edit / Omni-Base | Not released (HF 404 on 2026-11-16) | — | Watch |
| Z-Image Turbo Fun ControlNet Union 2.1 | Apache-2.0, Verified ([HF](https://huggingface.co/alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1)) | In mflux; no timing | Add (row 9) |
| FLUX.2 [klein] 4B (distilled + base) | Apache-2.0, ungated, Verified ([HF](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)) | 4B plus a Qwen3-4B text encoder; about 4 GB at 4-bit; M1 Max figures in row 3. Hair colour drifted in that test | Add (row 3) |
| FLUX 3 Image Klein (5.6B, Oct 2026) | FLUX Kommunity License, reportedly free under $5M revenue, Unverified; HF gated | In mflux 0.23; up to 10 references | Optional later; read the license first |
| FLUX.1 schnell | Apache-2.0 (gated=auto click-through) | 12B | Superseded by klein 4B |
| Qwen-Image / 2512 / Edit-2511 | Apache-2.0 | 20B; mflux 4-bit about 25 GB on disk. On an M1 Max the 4-bit edit output collapsed (via search) | Too heavy |
| HiDream-I1/E1 | MIT ([HF](https://huggingface.co/HiDream-ai/HiDream-I1-Fast)), plus a Llama-3.1-8B encoder under the Llama license | 17B | Too large |
| Chroma1-HD | Apache-2.0 ([HF](https://huggingface.co/lodestones/Chroma1-HD)) | 8.9B | No advantage |
| SDXL + finetunes | CreativeML OpenRAIL++-M | M4 Pro blog estimate 20–40 s at 1024 px ([heyuan110](https://www.heyuan110.com/posts/ai/2026-02-15-mac-mini-local-image-generation/)) | Only for SDXL-only style LoRAs; would add a second image stack |
| ERNIE-Image, MOSS-Image, Boogu, Iris-3B (Apache-2.0, Mirror); Ming-Image (MIT, Mirror) | — | — | Not needed |

**Runtimes**
- **mflux** (MIT, v0.24.0 on 2026-10-27, [releases](https://github.com/filipstrand/mflux/releases)) stays.
  - It requires Python 3.11+ and Pillow 13.
  - It has exposed a Python API since 0.22.
  - It includes `mflux-train` for Z-Image base and klein base 4B.
- **ComfyUI** (GPL-3.0; PyTorch MPS, reported 2–4x slower than CUDA, [insiderllm](https://insiderllm.com/guides/stable-diffusion-mac-mlx/)) and **Draw Things** are for exploring only.
- **DiffusionKit** is archived. Do not adopt it.

**Negative prompts (audit H5).** mflux forces guidance to 0.0 for Z-Image Turbo, so `styles.py` `negative` and `--negative-prompt` do nothing (`docs/WORKFLOW_AUDIT.md`). The fixes, in order:
1. Write prompts positively.
2. Clean up with klein edit passes.
3. Use Z-Image base only where negatives are essential. It supports CFG, but its speed is not measured.

### 2.2 Character consistency

The audit found (H6) that no code reads `profiles/characters/ramayana.json`, there are no reference images and there is no similarity metric. The plan:

1. **Reference editing.** Make one character sheet per recurring figure with Z-Image and store it in `profiles/characters/`. Render scenes with klein 4B edit, passing the sheet plus the scene prompt. The M1 Max took about 1 min per image; the Air will be slower (not measured).
2. **LoRA second.** `mflux-train` on klein base 4B or Z-Image base. The notes link the mflux docs at an indexer URL ([as recorded](https://docsearch.algolia.com/mcp/docs/repo/filipstrand/mflux); canonical repo [here](https://github.com/filipstrand/mflux)). No Apple Silicon training figure exists. Train one chalk-style LoRA, then per-character LoRAs only if references are not enough.
   - Alternative trainers are CUDA-first, with MPS support unverified: ostris/ai-toolkit (MIT) and kohya-ss/sd-scripts (Apache-2.0).
3. **Drift QA.** Compare each scene's figure crop with the sheet using CLIP or DINOv2 similarity. This carries over from the earlier report and was not re-verified.
4. **Identity adapters are a dead end:**
   - IP-Adapter is SD1.5/SDXL only and was last pushed in 2024.
   - InstantID uses research-only insightface models and research-only checkpoints ([README](https://github.com/instantX-research/InstantID)).
   - PuLID uses insightface plus FLUX-dev.
   - InfiniteYou weights are CC-BY-NC-4.0, Verified.
   - All four are tuned for photoreal faces, not chalk figures.

### 2.3 Parallax, depth and segmentation

| Tool | License (status) | Use / verdict |
|---|---|---|
| Depth Anything V2 Small | Apache-2.0, Verified ([HF](https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf)); **Base, Large and Giant are CC-BY-NC** | Depth per still |
| Depth Anything 3 Small/Base | Apache-2.0; Large/Giant CC-BY-NC ([card](https://huggingface.co/depth-anything/da3-small)) | Alternative |
| Video Depth Anything Small | Apache-2.0 | Only if video diffusion is adopted |
| SAM 2.1 hiera-small/tiny | Apache-2.0, Verified ([HF](https://huggingface.co/facebook/sam2.1-hiera-small)) | Box-prompted figure masks (the box comes from the scene plan) |
| SAM 3 | SAM License: custom, commercial allowed, prohibited-use list, terms changeable by Meta; HF gated=manual ([LICENSE](https://github.com/facebookresearch/sam3)) | Optional text-prompted masks; needs HF approval |
| BiRefNet | MIT, Verified ([HF](https://huggingface.co/ZhengPeng7/BiRefNet)) | Automatic foreground matte, no prompt needed |
| `cv2.inpaint` | OpenCV | Enough for thin disocclusion strips on a dark board |
| LaMa | Apache-2.0 code; Places2 data terms not checked | Only if gaps are large |
| FLUX.2 klein edit | Apache-2.0 | "Remove the figure" to build a clean plate when overlap is large |
| DepthFlow | **AGPL-3.0** ([repo](https://github.com/BrokenSource/DepthFlow)) | Reference for camera presets only; do not import |
| IOPaint | Apache-2.0, archived | Do not adopt |

**Design ("multiplane chalk camera")**
1. Run a mask model (BiRefNet or SAM 2.1) and DA-V2 Small sequentially, unloading each.
2. Quantize into 2–3 planes. The board moves with the far plane.
3. Animate the planes with different `cam_matrix` parameters. Example: far plane 1.00→1.03 zoom; figure 1.00→1.08 plus 10–20 px of drift.
4. Fill the gaps with `cv2.inpaint`.
5. Parallax starts after each plane's stroke reveal.
6. QA checks consecutive-frame SSIM for tearing.

Caveat: monocular depth on chalk is unvalidated. If the depth map is noisy, fall back to mask-only two-plane parallax.

### 2.4 Procedural motion and VFX

- **Motion comic lite.** Apply cheap motion inside the figure mask:
  - breathing: 0.5–1% vertical scale at about 0.25 Hz
  - head and arm sway: `cv2.remap` mesh warp inside a soft mask
  - cloth or hair flutter: noise displacement in the top of the mask
  - blinking: skip, because chalk eyes are too small

  The owner judges whether it reads as charming or uncanny.
- **FX.** Chalk dust motes, noise-displaced smoke and fire wisps, petal and arrow sprites, glow shimmer on divine figures, and rain or wind lines. All are license-free and match the palette.
- **Assets.** Poly Haven is CC0 for all assets ([FAQ](https://polyhaven.com/faq), Verified), useful only for board textures. ambientCG is reported CC0 (Unverified). Pixabay and Pexels video terms were not verified, so avoid stock overlays.
- **Rigged puppets: skip.** Spine and Live2D are paid. Inochi2D (BSD-2), Synfig (GPL), OpenToonz (BSD-3) and Blender with COA Tools all need manual rigging per character. Meta AnimatedDrawings (MIT) has been **archived since 2025-09**. LivePortrait bundles non-commercial insightface models ([LICENSE](https://github.com/KwaiVGI/LivePortrait)).

### 2.5 Transitions, motion graphics, captions, colour, upscaling, interpolation

| Area | Finding | Verdict |
|---|---|---|
| Transitions | ffmpeg `xfade` has about 40 transitions, mostly non-chalk | Keep the approved streak-erase; add procedural sponge-wipe, dust-puff and board page-turn |
| Motion graphics | Manim Community (MIT, very active); MoviePy (MIT) adds nothing; Remotion is free only up to 3 employees and 5.0 needs a `"free-license"` key ([LICENSE.md](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md), [5.0 migration](https://remotion.dev/docs/5-0-migration)); Motion Canvas and Revideo (MIT) are Node | Manim only (row 13) |
| Captions | The current ffmpeg/ASS + PIL + libraqm engine handles Indic shaping. pycaps (MIT, no releases, needs a browser renderer; [DEV](https://dev.to/francozanardi/adding-animated-subtitles-to-videos-with-python-4hml)) and captacity (stale) would regress it | Keep current |
| QA helper | PySceneDetect (BSD-3) detects unintended cuts and flashes | Optional for video-qa |
| Colour | ffmpeg `lut3d`/`curves`/`eq` are built in. LUT packs fight `restrict_palette`. Q-DDL is CC BY 4.0 ([80.lv](https://80.lv/articles/800-free-luts-released)); no CC0 pack was found | Self-generated `.cube` only if needed |
| Upscaling | Real-ESRGAN (BSD-3, Verified; weights unverified); SeedVR2 (Apache-2.0, heavy) | Low value: chalk texture overwrites detail |
| Interpolation | Practical-RIFE (MIT, [repo](https://github.com/hzwer/Practical-RIFE)); FILM is archived | Not needed: frames are already procedural at 30 fps |

### 2.6 Video generation

Real video diffusion costs **10–60+ min per 3–5 s clip** on 16 GB and needs 12–26 GB of disk per model. It also risks photoreal drift. At most it is worth 1–2 hero shots per episode, and only after sections 2.3–2.4 are in place.

| Model | License | Mac evidence | Verdict |
|---|---|---|---|
| **LTX-2.3** via ltx-2-mlx (MIT, pushed 2026-11-01) | LTX-2 Community, under $10M, Verified by grep ([LICENSE-2](https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2)) | int8 about 26 GB, "16 GB with `--low-ram`"; int4 about 12 GB, "16 GB+"; first/last-frame guides; 16 GB M1 about 15 min for about 4 s ([README](https://github.com/dgrauet/ltx-2-mlx)) | One test only (row 15) |
| LTX-2.5 | LTX-2.x Community (gated=auto) | 47–120 GB packs | **Not feasible** |
| Wan 2.2 TI2V 5B | Apache-2.0, Verified | MLX q8 on a 64 GB Mac about 15 min for 41 frames at 720p, "32 GB+ recommended" ([HF](https://huggingface.co/Anes1032/Wan2.2-TI2V-5B-mlx-q8)); FastMetal INT8 on an M4 Max 36 GB about 151 s, 9.34 GiB peak ([FastMetal](https://www.besthub.dev/articles/fastmetal-run-text-to-video-locally-on-mac-with-apple-silicon-51de9979fe23)); mlx-video MIT | Second choice; cleanest license |
| Wan 2.1 T2V 1.3B | Apache-2.0, Verified | T2V only at 480p ([search summary](https://localmodel-run.pages.dev/can-i-run/wan-2-1-t2v-1-3b/apple-m4-16gb)) | No chalk-frame conditioning; skip |
| Wan 14B | Apache-2.0 | 82 min per 2 s on an M1 Max 64 GB | Not feasible |
| FramePack, HunyuanVideo | Hunyuan Community License (excludes EU/UK/KR), Verified ([LICENSE](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5)); FramePack weights are a Hunyuan derivative (inference) | OOM reports | Excluded |
| CogVideoX-5B | Free commercial license requires registration ([LICENSE](https://huggingface.co/vdo/CogVideoX-5b/blob/main/LICENSE), search summary) | none | Skip |
| AnimateDiff, ToonCrafter, Paints-UNDO | Mixed or unverified weights; SD1.5-era, CUDA-oriented | — | Skip |

---

## 3. Audio

Source for this section: `audio_and_claude_skills.md` Part A.

Current pipeline:
- `step_audio` mixes a numpy raga/tanpura bed (`chalk.music`, `chalk.py:488`) or a `--music` file (tiled ×0.5).
- An envelope-follower ducker applies `1 - 0.65·clip(env/0.05)`.
- SFX are procedural chalk sounds.
- The final mix gets single-pass `loudnorm` (`studio.py:705`).
- QA requires −16.5 to −13 LUFS and a true peak at or below −1.0 dBFS.
- The audit measured finals at −15.2 to −14.7 LUFS with an LRA of 1.9–2.8 LU.

### 3.1 Music models

| Model | License (status) | 16 GB fit | Verdict |
|---|---|---|---|
| **ACE-Step 1.5** | MIT / MIT, Verified ([repo](https://github.com/ace-step/ACE-Step-1.5), [HF](https://huggingface.co/ACE-Step/Ace-Step1.5)); outputs commercial per card | 2B turbo + 0.6B LM = 8–12 GB (README); MLX on macOS; XL needs ≥12 GB with offload, so skip it | Best full bed; test (row 11). Clone at a pinned commit |
| **Magenta RealTime 2** | Code Apache-2.0, weights CC-BY-4.0, Verified ([HF](https://huggingface.co/google/magenta-realtime-2), [blog](https://magenta.tensorflow.org/magenta-realtime-2)) | `mrt2_small` 230M real-time on any Apple Silicon incl. Air; `mrt2_base` 2.4B offline | Test (row 12). CC-BY covers the weights, not the audio; a courtesy credit in the description is cheap |
| Stable Audio 3 Small Music / Small SFX / Medium | Stability Community License, gated, **under $1M revenue, revocable**, includes Gemma terms ([HF](https://huggingface.co/stabilityai/stable-audio-3-small-music), [license](https://stability.ai/license)) | "A few seconds on a MacBook Pro M4" (card) | Maybe; Small SFX is the only commercially usable modern SFX generator found |
| Stable Audio Open 1.0 / Small | Community, under $1M | — | Superseded; skip |
| HeartMuLa-oss-3B | Apache-2.0 ([HF](https://huggingface.co/HeartMuLa/HeartMuLa-oss-3B)) | 4B F32, no Mac path | Skip |
| DiffRhythm v1.2 | Apache-2.0 ([repo](https://github.com/ASLP-lab/DiffRhythm)); possible Stable-Audio VAE component | Stale; MPS not mentioned | Skip |
| YuE v1 | Apache-2.0 ([repo](https://github.com/multimodal-art-projection/YuE)); YuE2 is NC | 7B, vocals, CUDA | Skip |
| MusicGen / AudioGen | **Weights CC-BY-NC-4.0**, Verified ([HF](https://huggingface.co/facebook/musicgen-small)) | — | Excluded |
| MiniMax-Music3 | Attribution in the product UI plus a revenue threshold, Unverified ([secondary](https://www.orcarouter.ai/blog/minimax-music3-open-weights)) | — | Skip |
| Tencent SongGeneration | Official pages gone; re-uploads "unknown" | — | Avoid |

No model documents raga, tanpura, sitar or bansuri quality. Keep the numpy tanpura as the drone underlay and audition beds by ear. Generate 30–40 s and loop or crossfade. Example prompt: "slow devotional instrumental, bansuri and soft tanpura drone, no percussion, no vocals".

### 3.2 Libraries and license traps

| Source | Terms (status) | Trap | Verdict |
|---|---|---|---|
| YouTube Audio Library | "Copyright-safe", "won't be claimed", YPP can monetize, Verified ([help](https://support.google.com/youtube/answer/3376882)) | No guidance for use off YouTube; secondary guides say the standard license is YouTube-only | YouTube versions only; **not Instagram Reels** |
| Pixabay music/SFX | Free, no attribution, Verified ([summary](https://pixabay.com/service/license-summary/), [ToS](https://pixabay.com/service/terms/)) | No Content ID integration; contributors can register tracks at any time ([competitor page](https://hellothematic.com/thematic-vs-pixabay/)) | SFX at most; **avoid Pixabay music** |
| Freesound | Per-file CC0 / CC-BY / CC-BY-NC / Sampling+, Verified ([FAQ](https://freesound.org/help/faq/)) | CC-BY-NC forbids earning money; Sampling+ forbids ads | Use the CC0 filter `f=license:"Creative Commons 0"` |
| Sonniss GDC 2026 (347+ files, 7.47 GB) | Royalty-free, no attribution, monetized YouTube allowed, Verified ([FAQ](https://sonniss.com/gameaudiogdc)) | No redistribution (edited versions included); **AI/ML training prohibited** | Download; keep out of git |
| BBC Sound Effects | Personal, educational and research use only, Unverified ([secondary](https://www.diyphotography.net/the-bbc-sound-effects-archive-is-now-free-to-download-with-over-33000-files/)) | Commercial use needs a paid license | Skip |
| Incompetech | CC-BY free tier ([licenses](https://incompetech.com/music/royalty-free/licenses/)) | Per-video credit; overused; historical claims (Unverified) | Skip |
| Free Music Archive | Per-track CC, many NC/ND | Inconsistent filters | Skip unless checked by hand |
| OpenGameArt | Per-item CC0 / CC-BY / GPL | — | Maybe, CC0 only |
| ragajunglism.org tanpuras | No license; unknown origin ([page](https://ragajunglism.org/tanpuras)) | — | Avoid |

Freesound counts for Indian instruments (CC0 only, research date; they include unrelated hits):

| tanpura | tabla | temple bell | harmonium | sitar | bansuri | conch | veena | shehnai |
|---|---|---|---|---|---|---|---|---|
| 179 | 150 | 91 | 59 | 36 | 21 | 14 | 9 | **0** |

Shehnai has no CC0 supply, so generate it or drop it. Keep a `licenses.csv` (file, source URL, license) outside git.

**SFX generators.** All of these are excluded as non-commercial, Verified:
- AudioLDM2: CC-BY-NC-SA ([HF](https://huggingface.co/cvssp/audioldm2))
- Tango 2: CC-BY-NC-SA ([HF](https://huggingface.co/declare-lab/tango2))
- TangoFlux: research-only ([HF](https://huggingface.co/declare-lab/TangoFlux))
- MMAudio: weights CC-BY-NC-4.0 ([HF](https://huggingface.co/hkchengrex/MMAudio))
- HunyuanVideo-Foley: Hunyuan territory license

Keep the procedural chalk SFX and add CC0 or Sonniss accents.

### 3.3 Post-production chain

Everything below is in the local ffmpeg 9.0.1, which was checked with `ffmpeg -filters`.

**Loudness targets.** Neither YouTube nor Meta publishes an official Shorts or Reels loudness spec. −14 LUFS / −1 dBTP is a convention from blogs ([openclip](https://openclip.app/learn/audio-normalization), [DEV](https://dev.to/arthurvalle1_a2586dd2b4bc/mastering-for-reels-tiktok-and-youtube-shorts-the-lufs-14-standard-2ck5)). The current −14 / −1.5 target and the −16.5 to −13 QA band stay. Check a published video with Stats for nerds → content loudness.

| Step | Recipe | Notes |
|---|---|---|
| 1. Narration normalization | Normalize the voice stem (e.g. to −16 LUFS) before mixing, then set the music gain relative to it | Consistent beds across Kokoro and Maya2 and across languages |
| 2. Ducking | Keep the numpy ducker, or use `[music][voice]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[ducked]` then `amix` | The filter only reduces hand-tuned constants; replacing the ducker is not required |
| 3. Voice polish (optional, by ear) | `highpass=f=70`, gentle `deesser` (or `adynamicequalizer` at 6–8 kHz), `acompressor=threshold=-20dB:ratio=3:attack=5:release=80` | TTS is already clean, so over-processing is the risk |
| 4. Two-pass loudnorm | Pass 1: `loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json`. Pass 2: feed back `measured_I/TP/LRA/thresh` and `offset` with `linear=true` | Single-pass is dynamic and can pump; linear mode applies one gain. `pyloudnorm` (MIT) can measure in numpy |
| 5. QA addition (from the audit) | Speech-band level minus bed level in voice-free segments; warn below 12 dB | Cheap and objective; goes in `pipeline/qa.py` |

**Noise reduction.** TTS has no background noise, so this matters only if the owner records audio.
- DeepFilterNet: code and weights MIT/Apache-2.0, Verified ([repo](https://github.com/Rikorose/DeepFilterNet)). The best option if one is ever needed.
- RNNoise: BSD-3 ([repo](https://github.com/xiph/rnnoise)). For ffmpeg `arnndn`, use the xiph default model, not GregorR/rnnoise-models, which has no license file ([repo](https://github.com/GregorR/rnnoise-models)).
- noisereduce: MIT ([repo](https://github.com/timsainb/noisereduce)).
- ClearerVoice-Studio: Apache-2.0, untested ([repo](https://github.com/modelscope/ClearerVoice-Studio)).
- **Resemble Enhance**: MIT code and weights, stale since 2024-12 ([repo](https://github.com/resemble-ai/resemble-enhance)). Maybe: A/B its 24→44.1 kHz bandwidth extension on one Maya2 scene and listen for artifacts on Indic consonants.

**Do not add:**
- **Demucs** (MIT code, [active fork](https://github.com/adefossez/demucs)). Its README says the weights' license "is not clear", so its outputs must not be used in published audio.
- **Spotify pedalboard** (GPL-3.0, [repo](https://github.com/spotify/pedalboard)). It would bring GPL linking into a public repo, and ffmpeg already covers the need.

### 3.4 Voice

- Maya 2 Native (Malini) now runs through mlx-audio at about real time on the M5. It is the current hi/gu/te voice (PROJECT_CONTEXT §6). Kokoro `af_heart` stays for English.
- **Kitten TTS 2** (Apache-2.0, 82.7 MB int8 ONNX, 16 languages including Hindi; [HF](https://huggingface.co/KittenML/kitten-tts-2-mini)) and **MOSS-TTS v1.5** (Apache-2.0, 31 languages including Hindi; [HF](https://huggingface.co/OpenMOSS-Team/MOSS-TTS-v1.5)) have **no Gujarati or Telugu**, so neither changes the plan.
- QA must keep passing `speaker_consistency`.
- The earlier report's ASR items (IndicConformer-600M MIT for Indic QA; avoid MMS_FA, which is CC-BY-NC) were not re-checked in these notes. They stand as given there.

---

## 4. Claude Code skills, plugins and MCP servers

Source for this section: `audio_and_claude_skills.md` Part B, with docs fetched on 2026-11-16.

### 4.1 Official sources

- **`anthropics/skills`** ([repo](https://github.com/anthropics/skills), Verified). It now has 19 skills. **None covers video, audio, YouTube or analytics.** `skill-creator` is already available here as `anthropic-skills:skill-creator`.
- **`anthropics/claude-plugins-official`** (Apache-2.0, [repo](https://github.com/anthropics/claude-plugins-official), Verified). It lists 317 plugins, and there is **no YouTube, ffmpeg or Remotion plugin** among them. The media-adjacent ones all fail the constraints:
  - hyperframes: see 4.2
  - runway-api: paid
  - togetherai-skills: paid API
  - adobe-for-creativity: cloud service
  - cloudinary: SaaS
  - save-to-spotify: off-scope
  - postiz: AGPL, and it bypasses G3
- **Docs facts that matter here** ([skills](https://code.claude.com/docs/en/skills), [hooks](https://code.claude.com/docs/en/hooks), [plugins](https://code.claude.com/docs/en/plugins), Verified):
  - **Skill context.** The skill description plus `when_to_use` stays in context, truncated at 1,536 characters. The body loads on invocation. Keep SKILL.md under 500 lines.
  - **Skill frontmatter** supports `disable-model-invocation`, `allowed-tools`, `disallowed-tools`, `context: fork` with `agent`, `paths`, `hooks` and `model`.
  - **Dynamic context.** `` !`command` `` injects command output; a failing command aborts the invocation. This can inject `python -m pipeline status`.
  - **Blocking hooks.** `PreToolUse` blocks with exit code 2 or `permissionDecision: "deny"`. The `if` field uses permission syntax, e.g. `Bash(python -m pipeline publish*)`.
  - **Timeouts fail open by default.** `"onFailure": "block"` (v2.1.295+) is required for gate enforcement.
  - **Plugin cost.** Every model-invocable skill or agent description from an enabled plugin enters context on every turn, and its MCP servers run in every session.

### 4.2 Community skills and plugins (all Skip)

| Repo | Why skip |
|---|---|
| heygen-com/hyperframes (Apache-2.0, [repo](https://github.com/heygen-com/hyperframes)) | `media-use` SKILL.md sends a usage beacon, pushes HeyGen sign-in, says to use local tools only when asked, and defaults "local" music to **MusicGen (CC-BY-NC)**. Paid Pro plan; Node ≥22. Only the render engine is worth revisiting, and only if overlays move to HTML |
| remotion-dev/skills ([repo](https://github.com/remotion-dev/skills)) | React toolchain; the engine is Python |
| iart-ai/motion-skills (MIT, [repo](https://github.com/iart-ai/motion-skills)) | Advertises a paid MCP. Its only transferable idea is the render-frame → contact-sheet → inspect loop, which video-qa can copy (`qa.py` `contact_sheet` exists, `:181`) |
| affaan-m/ECC `video-editing` ([repo](https://github.com/affaan-m/ECC)) | ElevenLabs and fal.ai (paid); edits real footage |
| AgriciDaniel/claude-video ([repo](https://github.com/AgriciDaniel/claude-video)) | Stale; needs a Google AI key and a Pixabay key |
| renezander030/capcut-cli ([repo](https://github.com/renezander030/capcut-cli)) | CapCut, not used here |
| Alisa0808/vox-director ([repo](https://github.com/Alisa0808/vox-director)) | Paid Atlas Cloud API; its two-gate design mirrors G1/G2 |
| ComposioHQ/awesome-claude-skills ([repo](https://github.com/ComposioHQ/awesome-claude-skills)) | YouTube/Instagram/TikTok directories **do not exist** in the tree; Composio account; posting bypasses G3 |
| travisvn/awesome-claude-skills, hesreallyhim/awesome-claude-code ([1](https://github.com/travisvn/awesome-claude-skills), [2](https://github.com/hesreallyhim/awesome-claude-code)) | Nothing that beats the in-house pipeline |
| Registries (skills.sh, smithery, claude-plugins.dev and others) | ffmpeg-recipe skills; context cost and supply-chain risk |

### 4.3 MCP servers (all Skip)

| Server | Reason |
|---|---|
| ffmpeg MCPs ([video-creator](https://github.com/video-creator/ffmpeg-mcp), [kevinwatt](https://github.com/kevinwatt/ffmpeg-mcp-lite)) | Redundant: Bash and Python already run ffmpeg |
| ComfyUI MCPs ([artokun](https://github.com/artokun/comfyui-mcp), [joenorton](https://github.com/joenorton/comfyui-mcp-server), Pixelle) | A second heavy runtime breaks the one-model rule; artokun bundles 3 hooks that would need review |
| `conorbronsdon/yt-analytics-mcp` (MIT, read-only, 3★, [repo](https://github.com/conorbronsdon/yt-analytics-mcp)) | Maybe at most. `performance-analyst` already calls Analytics v2. Borrow the equal-age "episode race" comparison instead |
| `pauling-ai/youtube-mcp-server` ([repo](https://github.com/pauling-ai/youtube-mcp-server)) | Has upload, comment and thumbnail write tools, so it could publish outside G3 |
| ZubeidHendricks / kirbah YouTube MCPs ([1](https://github.com/ZubeidHendricks/youtube-mcp-server), [2](https://github.com/kirbah/mcp-youtube)) | Duplicate `yt-viral` and `pipeline/research.py` |
| `Audio-Launch/audiolab-mcp-server` | 0★; `ebur128` and `qa.py` already do this |
| Blender MCP ([ahujasid](https://github.com/ahujasid/blender-mcp), now reported as `ahujasid/mcp-for-blender`) | Does not fit 2D chalk. See the security warnings below |

### 4.4 Why nothing external is worth installing now

- The 8 vendored `yt-*` skills (MIT, pinned at `a2feb21`), plus `storytelling`, `content-pipeline` and the project agents, already cover the workflow.
- Every media plugin found falls into at least one of these groups:
  - paid
  - Node/React based
  - redundant with the Python pipeline
  - able to bypass G3
  - adds context on every turn

### 4.5 What to build in-repo instead

1. **Fail-closed G3 `PreToolUse` hook.**
   - **Where:** a new `.claude/settings.json`.
   - **Matcher:** `Bash`, with `if` set to `Bash(python -m pipeline publish*)`. Also cover `data/upload_queue.sh` and any upload script.
   - **Failure mode:** set `"onFailure": "block"`. The checker exits 2 unless the manifest holds a G3 approval.
   - **Prerequisite (audit finding 2):** today one `gate:publish` entry is overwritten per platform (`cmd_approve`, `pipeline/__main__.py:120`). A mechanical gate is only meaningful once approvals record the platform, scheduled time and metadata hash, and the hook checks those fields.
   - **Before committing:** check the exact JSON schema against the [hooks docs](https://code.claude.com/docs/en/hooks), and test that a denied command really exits 2.
2. **`disable-model-invocation: true`** on any skill that publishes or schedules. `content-pipeline` spans every stage. The suggestion is to split the publish step into its own skill with this flag rather than disabling the whole runbook.
3. **`audio-mix` skill** (about 100 lines). It holds the two-pass recipe, the stem gain table per voice engine, the `licenses.csv` SFX index and the QA thresholds.
4. **Vendoring policy.** Pin single reviewed files to a SHA (the `yt-*` precedent). Never enable a plugin that ships hooks or MCP servers without reading them first.

### 4.6 Security warnings

- **Star-farmed blender-mcp look-alikes.** A GitHub search for "blender mcp" returns repos with random-looking owners and about 500★ each, all pushed the same day. Examples: `credoksopho1984/…`, `racdeufindurch198812/…`, `fumbdendade19718/…`. The pattern matches malware lures. **Never install them.**
- **Paid or credit-based connectors** visible in this session must not be used: xelta, MCP-H/Higgsfield, OpenSEO and Ubersuggest. They violate zero cost, and the generation ones would also bypass the local pipeline.
- **Hyperframes sends a usage beacon** (`npx hyperframes events`) that is account-linked when signed in.
- **Composio "automation" skills** are dead links into a third-party platform.

---

## 5. Do not use

| Item | Reason | Source / status |
|---|---|---|
| Depth Pro (incl. mflux built-in), Apple ml-sharp | Apple ML Research Model License: research only, no commercial exploitation | [HF LICENSE](https://huggingface.co/apple/DepthPro/resolve/main/LICENSE), [LICENSE_MODEL](https://raw.githubusercontent.com/apple/ml-sharp/main/LICENSE_MODEL), Verified |
| Depth Anything V2/V3 Base, Large, Giant | CC-BY-NC | [HF](https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf), Verified |
| FLUX.1 dev, Krea-dev, Kontext dev, Fill dev; FLUX.2 klein 9B, FLUX.2 dev | FLUX Non-Commercial | Verified (notes) |
| FLUX.1-dev-based Indian-style LoRAs (e.g. "IMZ Madhubani") | Inherit FLUX.1-dev NC | Verified (notes) |
| Qwen-Image 2.1 | Qwen Research License (NC) | Earlier note |
| Anima | circlestone non-commercial | Verified (HF API) |
| FIBO 2 | CC-BY-NC-4.0 | Mirror |
| InfiniteYou | CC-BY-NC-4.0 | Verified |
| InstantID, PuLID, LivePortrait as shipped | insightface research-only face models | [InstantID](https://github.com/instantX-research/InstantID), [LivePortrait](https://github.com/KwaiVGI/LivePortrait), Verified |
| RMBG-2.0 (Bria) | NC without an agreement; gated | Verified (HF tag) |
| 3D Ken Burns | CC BY-NC-SA 4.0 | Verified |
| HunyuanVideo, HunyuanVideo-Foley, FramePack | Hunyuan Community License excludes EU/UK/KR | [LICENSE](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5), Verified; FramePack by inference |
| MusicGen, AudioGen | Weights CC-BY-NC-4.0 | [HF](https://huggingface.co/facebook/musicgen-small), Verified |
| AudioLDM2, Tango 2, TangoFlux, MMAudio | NC / research-only weights | HF links in 3.2, Verified |
| YuE2 | NC weights | Earlier pass |
| Demucs outputs in published audio | Weights license "not clear" (MusDB research-only) | [repo](https://github.com/adefossez/demucs), Verified |
| MMS-300M / torchaudio MMS_FA aligner | CC-BY-NC | Earlier report |
| macOS `say` voices, IndicF5 | Apple SLA personal use; NC training data | PROJECT_CONTEXT §6 |
| BBC Sound Effects | Non-commercial | Unverified (secondary) |
| Pixabay music | Content ID exposure | 3.2 |
| YouTube Audio Library tracks in Instagram Reels | Off-YouTube use not covered | 3.2 |
| GregorR rnnoise-models, ragajunglism tanpuras | No license | Verified (repo or page) |
| DepthFlow as an imported library | AGPL-3.0 in a public repo | [repo](https://github.com/BrokenSource/DepthFlow), Verified |
| pedalboard | GPL-3.0 linking in a public repo; redundant | [repo](https://github.com/spotify/pedalboard), Verified |
| Revenue-capped (avoid unless a clear gain) | Stable Audio 3/Open and SD 3.5 (under $1M), FLUX 3 Klein (under $5M, Unverified), Krea 2 (under $1M, Unverified), CogVideoX-5B (registration) | Notes |
| Too heavy for 16 GB | Qwen-Image 20B, HiDream 17B, Wan 14B, LTX-2.5, FramePack, ACE-Step XL, HeartMuLa, YuE | Notes |
| Archived | DiffusionKit, IOPaint, FILM, AnimatedDrawings, facebookresearch/demucs | GitHub API |
| Paid | Spine, Live2D, all credit-based claude.ai connectors, runway/together/adobe plugins | Notes |

---

## 6. Corrections to earlier reports

| Earlier claim | Correction | Source |
|---|---|---|
| Earlier report: depth parallax "from mflux's built-in Depth Pro or Depth Anything V2 Small"; ranked row 6 lists "mflux Depth Pro" | Depth Pro **weights are research-only**. Use DA-V2 Small or DA3 Small/Base only | visual_tools.md Correction 1, Verified |
| Earlier report row 10: "LTX-2.5 hero shots" | LTX-2.5 packs are 47–120 GB, so it is infeasible. The "fits 16 GB with `--low-ram`" claim applies to **LTX-2.3 q8** (about 26 GB on disk) | visual_tools.md Correction 2, [ltx-2-mlx README](https://github.com/dgrauet/ltx-2-mlx), Verified |
| Earlier report: "Maya 2 Native … officially runs only on Linux with NVIDIA CUDA", watch list | Superseded. Maya 2 Native (Malini) runs via mlx-audio `maya2` at about real time on the M5, and has been the hi/gu/te voice since 2026-11-16 | PROJECT_CONTEXT §6; audio notes A5 |
| Earlier report lead: A/B Indic-Speak against **Veena kavya** | Veena was retired on 2026-11-16, so any Indic-Speak test should now be against Maya2 Malini. This is an inference from §6; Indic-Speak itself was not re-checked | PROJECT_CONTEXT §6 |
| Earlier report: FLUX.2 klein 4B "VRAM figures conflict (8–13 GB)" | Community mflux 4-bit is about 4 GB on disk, but peak RAM is still unreported. Measure it on the M5 | visual_tools.md §1 |
| Earlier visual notes: FramePack (Apache-2.0) | Its model is HunyuanVideo-based, so the territory-restricted Hunyuan license applies (inference; the card has no tag) | visual_tools.md Correction 3 |
| Earlier visual notes: mflux model list read as all usable | Anima is non-commercial (Verified); FIBO 2 is CC-BY-NC (Mirror) | visual_tools.md Correction 4 |
| MMAudio weights NC (secondary only) | Now confirmed CC-BY-NC-4.0 on HF | audio notes A3, Verified |
| PROJECT_CONTEXT §6 excludes "Wan/LTX video (too slow on the Air)" | Broadly still true. LTX-2.3 int8 `--low-ram` is technically runnable on 16 GB at about 15 min per 4 s, which is worth one owner-judged test, not adoption | visual_tools.md §2 |
| `CLAUDE.md` "Hindi voice: Use Veena kavya with voice-prompt priming" | Conflicts with PROJECT_CONTEXT §6 (Veena retired; Maya2 Malini current) and with project memory. `CLAUDE.md` needs an owner-approved update (not edited here) | PROJECT_CONTEXT §6 |
| Audit §2.10: "ACE-Step 1.5 optional; don't adopt while the bottleneck is duration and consistency" | Not a correction, a priority. Music models rank 11–12 here for that reason | WORKFLOW_AUDIT §2.10 |

---

## 7. Open measurements on the M5 Air

General method for every item:
- Run it alone, with Ollama stopped and nothing else heavy loaded.
- Wrap the command in `/usr/bin/time -l` to get wall time and maximum resident set size.
- Use one existing scene from C0001–C0005 as input.
- Post `python -m pipeline progress <ID> --oneline` updates every 3–5 minutes on long runs.

| Unknown | Cheap test | Decision it feeds |
|---|---|---|
| FLUX.2 klein 4B speed and peak RAM at 768x1344 (4-bit vs 8-bit; text-to-image and edit with 1–2 references) | 2 sizes × 2 modes × 1 seed on one drifting scene (beard/age); `time -l` | Adopt row 3, and which quantization |
| klein identity retention on chalk figures | One sheet → 4 scenes; CLIP/DINOv2 similarity against the sheet plus owner look | Reference editing alone vs LoRA |
| `mflux-train` speed and memory on 16 GB | 500–1000 steps at 512 px overnight; log s/it and RSS | Row 10 feasibility |
| Depth quality of DA-V2 Small on chalk stills | 5 scene images from C0001–C0005; inspect the depth maps | 3-plane vs mask-only parallax |
| BiRefNet and SAM 2.1 mask time and quality on chalk | Same 5 images; time per mask | Row 4 mask source |
| Parallax tearing | Render one scene three ways (current, mask parallax, depth parallax); SSIM between consecutive frames | Owner side-by-side |
| Union ControlNet 2.1 disk size and time | One canny-conditioned regeneration of an existing scene | Row 9 |
| Base-model prompting of Indian painting styles | 4 styles × 4 images on Z-Image (about 30 min) | Whether a folk-art preset in `styles.py` is worth pursuing (a G1-level owner decision) |
| ACE-Step 1.5 speed, RAM and Indian timbre | One 30–40 s devotional bed; `time -l`; mix via `--music`; owner listens | Row 11 |
| Magenta RT2 small vs base on the Air | Same prompt and length as ACE-Step; blind A/B | Row 12 |
| Stable Audio 3 Small SFX (only if the owner accepts the under-$1M cap) | 5 accents (conch, bell, whoosh); time on CPU and MPS | Generator vs CC0 library |
| Two-pass loudnorm effect | Re-encode one final both ways; compare `ebur128` I/TP/LRA with the audit baseline (−15.2 to −14.7 LUFS) | Row 1 default |
| Music-under-speech level | Compute speech-band minus bed in voice-free segments on 9 existing finals | QA warn threshold (12 dB proposed) |
| Resemble Enhance bandwidth extension | One Maya2 scene; listen for Indic consonant artifacts; re-run `speaker_consistency` | Maybe-adopt |
| LTX-2.3 int8 `--low-ram` on the Air | One 4 s first/last-frame clip from a chalk still; `time -l`; check swap | Owner judges one hero shot; likely 10–15+ min per clip |
| G3 hook enforcement | Dry-run a blocked command and confirm exit 2 / deny; simulate a hook timeout and confirm it blocks | Row 2 ready |

**License items not yet read in full:**
- FLUX 3 Klein (Kommunity) and Krea 2 license texts.
- The SD 3.5 $1M cap (from the earlier report, not re-fetched).
- The LTX-2 license, which was read by grep only. Read it end to end before publishing any LTX output.
- Weight license tags for Real-ESRGAN, ToonCrafter, AnimateDiff motion modules and the SDXL Indian-style LoRAs.
- Pixabay and Pexels video terms.
