# Visual tools and models for the shorts-studio pipeline (16 GB Apple Silicon, zero cost, commercial use)

Research date: 2026-11-16. Method: GitHub API (license SPDX id, last push, archived flag) for about 80 repos, Hugging Face API (`cardData.license`, gating, lastModified) for about 60 model repos, raw LICENSE texts where the tag was "other" or NOASSERTION, plus web searches for Apple Silicon timings. Builds on `research_notes/Shorts studio voices and tools/visual_animation_tools.md` and corrects it in four places (see "Corrections").

Labels used below:
- **Verified**: read from the official LICENSE file, the official HF card metadata, or the official README.
- **Mirror tag**: license read from a community or Comfy-Org mirror; verify upstream before use.
- **Unverified**: secondary source or prior knowledge only.
- Speeds are quoted only from a named source and hardware. No source measured anything on an M5 Air; the Air is fanless and has less bandwidth than the Max chips most reports use, so treat every number as an upper bound on speed.

Pipeline facts that shape the recommendations (from `PROJECT_CONTEXT.md` and `chalk.py`):
- Stills come from Z-Image Turbo 4-bit (mflux 0.24) at 768x1344, about 100 s each, 8.3 GB peak.
- `chalk.chalk_from_image` subtracts a local luminance floor, restricts the palette and multiplies by a chalk texture, so **the chalk is already an additive layer over a procedural board** (`make_board`). The board never needs inpainting. Layer separation is cheap, and only overlapping elements within the chalk layer need care.
- Motion today is `cam_matrix` (zoom, focus, jitter) via `cv2.warpAffine`, plus the stroke-order reveal from `reveal_order` (connected components plus DFS, not true artist strokes).
- Hard rules: one heavy model at a time; no paid tools; approved chalk look and `CHALK_SFX_GAIN = 0.035` stay.

---

## Corrections to the earlier research

1. **Depth Pro is research-only.** The weights at `apple/DepthPro` and `apple/DepthPro-hf` carry the *Apple Machine Learning Research Model License*: "exclusively for Research Purposes … does not include any commercial exploitation". The GitHub code is under the permissive Apple sample-code license, but the weights are not (Verified: [HF LICENSE](https://huggingface.co/apple/DepthPro/resolve/main/LICENSE), HF API tag `apple-amlr`). mflux's built-in Depth Pro uses these weights, so **do not use `mflux` Depth Pro for published videos.** Use Depth Anything V2 Small or DA3 Small/Base (Apache-2.0) instead. Apple's `ml-sharp` (single image to 3D Gaussians) has the same research-only model license ([LICENSE_MODEL](https://raw.githubusercontent.com/apple/ml-sharp/main/LICENSE_MODEL)).
2. **LTX-2.5 does not fit a 16 GB Mac in practice.** The ltx-2-mlx README lists 2.5 packs at about 120 GB (bf16), 75 GB (int8) and 47 GB (int4). The "q8 fits 16 GB with `--low-ram`" claim is for **LTX-2.3 q8 (about 26 GB on disk)**, and int4 2.3 (about 12 GB) is listed as "16 GB+" (Verified: [ltx-2-mlx README](https://github.com/dgrauet/ltx-2-mlx)). With about 92 GB free on disk, LTX-2.5 is out; LTX-2.3 is the only realistic LTX option.
3. **FramePack runs on HunyuanVideo weights.** The FramePack code is Apache-2.0, but its model (`lllyasviel/FramePackI2V_HY`) is a HunyuanVideo derivative, so the Tencent Hunyuan Community License applies (territory excludes EU/UK/South Korea). The HF card carries no license tag, so this is an inference from the model name and architecture.
4. **Several mflux models are non-commercial.** The mflux README lists Anima and FIBO 2 next to Apache models. Anima (`circlestone-labs/Anima`) is `circlestone-labs-non-commercial-license` (Verified, HF API). FIBO 2 is CC-BY-NC-4.0 (Mirror tag, Comfy-Org/Fibo-2.0).

---

## 1. Text-to-image and image editing (local, MLX)

### Takeaway
Keep Z-Image Turbo. Add **FLUX.2 [klein] 4B** (Apache-2.0) as the reference-locked scene and edit model, and use the **Z-Image Union ControlNet** (Apache-2.0) to lock composition from the previous frame or a sketch. mflux is the runtime. ComfyUI and Draw Things are optional GUIs for exploring, not pipeline components. Identity adapters (IP-Adapter, InstantID, PuLID) are a dead end for this project: they target SDXL or FLUX-dev on CUDA, and InstantID and PuLID depend on insightface face models that are non-commercial and only work on realistic faces.

### Model table

| Model | Weights license (Verified unless noted) | Size / 16 GB fit | Mac speed evidence | Verdict |
|---|---|---|---|---|
| **Z-Image Turbo** (current) | Apache-2.0 ([HF](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo)) | 6B; 4-bit 5.5 GB, 8.3 GB peak (measured locally) | about 100 s at 768x1344 on the M5 Air (measured in this project) | Keep |
| Z-Image (base) | Apache-2.0 | 6B, CFG and negative prompts | none found | For LoRA training and negative prompts |
| Z-Image-Edit / Omni-Base | not released (HF repo returns 404 on 2026-11-16) | — | — | Watch |
| **Z-Image Turbo Fun ControlNet Union 2.1** | Apache-2.0 ([HF](https://huggingface.co/alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1)) | add-on; supported in mflux | none found | Add: canny/pose/depth control keeps layout between scenes |
| **FLUX.2 [klein] 4B** (distilled + base) | Apache-2.0, ungated ([HF](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)) | 4B + Qwen3-4B text encoder; community mflux 4-bit about 4 GB | M1 Max 64 GB, mflux 0.17.5, 4 steps: 1024x1024 in 21.4 s inference / 31.7 s wall; edit with reference 52.4–53.4 s ([lilting.ch](https://lilting.ch/en/articles/flux2-klein-4b-mflux-iris-m1-max)). Peak RAM not reported | **Add.** Up to 4 reference images; edits keep face, hair and outfit, though hair colour drifted in that test |
| FLUX.2 klein 9B, FLUX.2 dev | FLUX Non-Commercial | — | — | Excluded |
| FLUX 3 Image Klein (5.6B, Oct 2026) | FLUX Kommunity License, reportedly free under $5M revenue (Unverified; HF gated) | in mflux 0.23 with 4/6/8-bit, up to 10 references | none found | Optional later; read the license first |
| FLUX.1 schnell | Apache-2.0 (gated=auto click-through) | 12B | — | Superseded by klein 4B |
| FLUX.1 dev / Krea-dev / Kontext dev / Fill dev | FLUX.1-dev Non-Commercial | — | — | Excluded |
| Qwen-Image / Qwen-Image-2512 / Qwen-Image-Edit-2511 | Apache-2.0 | 20B; mflux 4-bit build listed at about 25 GB on disk | M1 Max: 2509-edit 4-bit 4 steps about 2:12 but output collapsed; 8-bit 20 steps about 10:44 (lilting.ch via search) | Too heavy for 16 GB; skip |
| Qwen-Image 2.1 | Qwen Research License, non-commercial (earlier note) | — | — | Excluded |
| Krea 2 | Krea 2 Community License, reportedly < $1M revenue (Unverified) | 12B | — | Skip |
| HiDream-I1 / E1 | MIT ([HF](https://huggingface.co/HiDream-ai/HiDream-I1-Fast)); uses a Llama-3.1-8B text encoder under the Llama license | 17B | none | Too large; skip |
| Chroma1-HD | Apache-2.0 ([HF](https://huggingface.co/lodestones/Chroma1-HD)) | 8.9B (FLUX-schnell derived) | none | No advantage over Z-Image here |
| SD 3.5 Medium | Stability AI Community License (free below $1M annual revenue, registration needed; per earlier note) | 2.5B | — | Revenue cap; skip |
| SDXL + finetunes | CreativeML OpenRAIL++-M (commercial with use restrictions) | 3.5B; ComfyUI SDXL 1024px about 20–40 s on an M4 Pro 24 GB (blog estimates, [heyuan110](https://www.heyuan110.com/posts/ai/2026-02-15-mac-mini-local-image-generation/)) | — | Only for SDXL-only style LoRAs (see section 5); check each finetune's license |
| ERNIE-Image, MOSS-Image, Boogu, Iris-3B | Apache-2.0 (Mirror tag) | various | none | Not needed |
| Ming-Image | MIT (Mirror tag) | — | none | Not needed |
| Anima (anime) | non-commercial (Verified) | 2B | — | Excluded |
| FIBO 2 | CC-BY-NC-4.0 (Mirror tag) | 8.1B | — | Excluded |

### Runtimes

| Runtime | Code license | Status | Fit |
|---|---|---|---|
| **mflux** | MIT | v0.24.0 on 2026-10-27, pushed 2026-11-16 ([releases](https://github.com/filipstrand/mflux/releases)); requires Python 3.11+ and Pillow 13 | Already in use. Python API (`validate/load/generate`) exposed for most models since 0.22. LoRA training via `mflux-train` for Z-Image and FLUX.2 klein base |
| DiffusionKit (Argmax) | MIT | **Archived** (last push 2025-04) | Do not adopt |
| ComfyUI | GPL-3.0 (app; outputs unrestricted) | Very active (pushed 2026-11-16) | PyTorch MPS, reported 2–4x slower than CUDA and about 20% slower than Draw Things ([insiderllm](https://insiderllm.com/guides/stable-diffusion-mac-mlx/), [heyuan110](https://www.heyuan110.com/posts/ai/2026-02-15-mac-mini-local-image-generation/)). Useful for trying workflows, poor for a deterministic Python pipeline |
| Draw Things | free app (license not checked) | — | GUI only; not scriptable from the pipeline |

### Character consistency and style LoRA on Mac
- **Reference editing first.** Make one character sheet per recurring figure (Rama, Sita, Valmiki and others) with Z-Image, store it in `profiles/characters/`, and render scenes with FLUX.2 klein 4B edit, passing the sheet plus the scene prompt. Expect about 1 minute per image on an M1 Max; slower on the Air (inference, not measured).
- **LoRA training second.** `mflux-train` supports flux2-klein-base-4b and Z-Image base ([mflux docs](https://docsearch.algolia.com/mcp/docs/repo/filipstrand/mflux)). No Apple Silicon training time or memory figure was found. A CUDA musubi-tuner benchmark shows klein 4B base at 1024 px using about 10 GB and 2.0–6.4 s/it, and Z-Image base at 512 px about 10.8 GB and 3.7 s/it ([runcomfy 16 GB guide](https://www.runcomfy.com/es/trainer/ai-toolkit/flux-2-klein-16gb-vram-training)). On a 16 GB Mac, expect it to be tight. Pilot one run of 500–1000 steps at 512 px overnight with nothing else loaded. Two LoRA kinds are worth it: a **chalk style LoRA** trained on approved frames, to fix "shaded pastel, not line art", and one **character LoRA** per main figure.
- **Alternative trainers** (CUDA-first; MPS support unverified): ostris/ai-toolkit (MIT, active) and kohya-ss/sd-scripts (Apache-2.0, active).
- **Identity adapters, all not worth it:**
  - IP-Adapter: Apache-2.0 code and weights, SD1.5/SDXL only, last push 2024.
  - InstantID: the README states the insightface face models "are for non-commercial research purposes only" and "our released checkpoints are also for research purposes only" ([README](https://github.com/instantX-research/InstantID)).
  - PuLID: Apache code, but uses insightface and FLUX-dev for PuLID-FLUX.
  - InfiniteYou: weights CC-BY-NC-4.0 (Verified, HF).
  - All four are tuned for photoreal faces, not chalk figures.
- **Automated drift QA:** CLIP or DINOv2 similarity between each scene's figure crop and the sheet. This suggestion is unchanged from the earlier report and not separately verified.

---

## 2. Image-to-video and text-to-video on 16 GB

### Takeaway
Real video diffusion is possible but costs **10–60+ minutes per 3–5 s clip** on 16 GB hardware, needs 12–26 GB of disk per model, and risks turning chalk into photoreal footage. For a 75–95 s short with 12–20 scenes, it is worth at most **one or two hero shots per episode**, and only after the cheap 2.5D and per-element motion (section 3) is in place. LTX-2.3 via ltx-2-mlx is the only candidate with a native MLX path that documents 16 GB.

| Model | Weights license | Mac evidence | Verdict |
|---|---|---|---|
| **LTX-2.3** via **ltx-2-mlx** (MIT, pushed 2026-11-01) | LTX-2 Community License: free for entities with annual revenue below $10M; "Licensor claims no rights in the Output"; acceptable-use policy applies ([LICENSE-2](https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2), Verified by grep of the text) | int8 about 26 GB on disk, "16 GB with `--low-ram`" (block streaming); int4 about 12 GB "16 GB+". Supports first/last-frame guides (`--image PATH FRAME STRENGTH`), IC-LoRA with depth video conditioning. Timing: 2.5 q8 576x1024x241-frame distilled I2V 701 s, 563 s with `LTX2_COMPUTE_DTYPE=float16` on an **M1 Max** ([README](https://github.com/dgrauet/ltx-2-mlx)); a 16 GB M1 took about 15 min for about 4 s ([lilting.ch](https://lilting.ch/en/articles/ltx2-wan22-mac-local-video-gen)) | **Optional hero shots only** |
| LTX-2.5 | LTX-2.x Community License (HF gated=auto) | 47–120 GB packs | Not feasible (disk and RAM) |
| LTX-Video 0.9.x | "other" on HF (older LTXV license); repo Apache-2.0 code | superseded | Skip |
| **Wan 2.1 T2V 1.3B** | Apache-2.0 (Verified, HF) | M1 Pro: about 10 min for only 8 frames at 480p on an MPS fork; Mac 32 GB ComfyUI: 9–11 min for a 5 s 480p I2V clip (variant unclear); FastMetal distilled 1.3B on an **M4 Max** about 110 s, 3.87 GiB peak ([search summary](https://localmodel-run.pages.dev/can-i-run/wan-2-1-t2v-1-3b/apple-m4-16gb), [FastMetal](https://www.besthub.dev/articles/fastmetal-run-text-to-video-locally-on-mac-with-apple-silicon-51de9979fe23)) | T2V only, so no chalk-frame conditioning on 1.3B; 480p. Not worth it |
| **Wan 2.2 TI2V 5B** | Apache-2.0 (Verified, HF; repo pushed 2026-09) | MLX q8 on a 64 GB Mac about 15 min for 720p, 41 frames, 20 steps, "32 GB+ recommended" ([HF](https://huggingface.co/Anes1032/Wan2.2-TI2V-5B-mlx-q8)); distilled INT8 on an M4 Max 36 GB about 151 s, 9.34 GiB peak (FastMetal). Supported in Blaizzy/mlx-video (MIT; last push 2026-05) | Second choice to LTX-2.3; licence is the cleanest |
| Wan 2.x 14B | Apache-2.0 | GGUF Wan 2.2 on an M1 Max 64 GB: 82 min per 2 s clip (lilting.ch) | Not feasible |
| FramePack | code Apache-2.0; model is HunyuanVideo-based (see Corrections) | M4 Max 128 GB: about 22 min per 5 s; M2 Max 64 GB: 2 s in about 10 min; OOM and swapping reports ([techno-edge](https://www.techno-edge.net/article/2025/04/28/4319.html), Reddit) | Excluded (licence, RAM) |
| HunyuanVideo / 1.5 | Tencent Hunyuan Community License; "DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM AND SOUTH KOREA" (Verified, [LICENSE](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5)) | heavy | Excluded |
| CogVideoX-5B / 1.5-5B | CogVideoX License: commercial use requires registering for a free basic commercial license with Zhipu; 2B is Apache-2.0 ([search summary of LICENSE](https://huggingface.co/vdo/CogVideoX-5b/blob/main/LICENSE)) | no Mac numbers found; repo last push 2025-11 | Skip |
| AnimateDiff (SD1.5) / AnimateDiff-Lightning | code Apache-2.0 (repo last push 2024-07); motion modules have no HF licence tag; Lightning is CreativeML OpenRAIL-M | runs on MPS via diffusers (not timed) | Dated look; skip |
| ToonCrafter / DynamiCrafter | code Apache-2.0; weights licence tag missing (Unverified) | CUDA-oriented; last push 2024–2025 | Skip |
| Paints-UNDO (draws an image as a process video) | code Apache-2.0; weights OpenRAIL (HF tag) | SD1.5-based, CUDA-oriented | Interesting for "drawing process" but not worth the integration |

**Worth it compared with 2.5D?** No, as a default. Per-scene cost in the current pipeline is about 100 s (image) plus a share of a 1–1.5 min render. A single 4 s LTX-2.3 clip would cost 10–15+ minutes on the Air, take over memory for the whole run, and need QA for style drift and anatomy. 2.5D and per-element motion cost seconds per scene and keep the approved chalk look pixel-exact. Run one LTX-2.3 first/last-frame test on a single chalk still for the owner to judge. Adopt it only if the owner prefers it, and only for one hero shot.

---

## 3. 2.5D parallax, depth, segmentation, inpainting

### Takeaway
This is the highest-value category, and the chalk architecture makes it cheaper than usual. The board is procedural, so no background inpainting is needed. Only the chalk layer has to be split into foreground and background elements. A self-written numpy/OpenCV multiplane renderer (about 150–250 lines) is preferable to adopting DepthFlow, which is AGPL.

| Tool | Licence (Verified) | Mac fit | Use |
|---|---|---|---|
| **Depth Anything V2 Small** | Apache-2.0 (Base/Large/Giant are CC-BY-NC-4.0) ([HF](https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf)); repo pushed 2026-03 | 25M params; runs through `transformers` on MPS or CPU; seconds per image (not timed) | Depth map per still |
| **Depth Anything 3 Small/Base** | Apache-2.0; Large/Giant CC-BY-NC ([da3-small card](https://huggingface.co/depth-anything/da3-small), PyPI table via search) | small | Alternative; also predicts camera pose (unneeded) |
| Video Depth Anything Small | Apache-2.0 (HF + repo) | small | Only needed if video diffusion is adopted |
| Depth Pro (Apple) | **research-only weights** | — | Excluded (see Corrections) |
| **SAM 2.1** (hiera-small/tiny) | Apache-2.0 code and weights ([HF](https://huggingface.co/facebook/sam2.1-hiera-small)); repo pushed 2026-05 | small checkpoints run on MPS/CPU | Click- or box-prompted masks of the figure in each still, for layer splits and per-element animation |
| SAM 3 | SAM License (custom, royalty-free, commercial allowed, with prohibited uses; Meta may change terms; HF gated=manual) ([LICENSE](https://github.com/facebookresearch/sam3)) | larger | Text-prompted ("the bow", "Rama") masks; optional upgrade, needs HF approval |
| **BiRefNet** | MIT ([HF](https://huggingface.co/ZhengPeng7/BiRefNet)), updated 2026-02 | about 1 GB, MPS | Automatic foreground matting of the main figure, no prompt needed |
| RMBG-2.0 (Bria) | Bria licence, non-commercial without agreement (HF tag `bria-rmbg-2.0`, gated) | — | Excluded |
| LaMa | Apache-2.0 code (repo push 2025-02); training data is Places2, whose terms were not checked | CPU/MPS | Only for inpainting chalk behind a moved figure; OpenCV `cv2.inpaint` is enough for the thin disocclusion strips on a dark board |
| IOPaint | Apache-2.0, **archived** | — | Do not adopt |
| FLUX.2 klein 4B edit | Apache-2.0 | see section 1 | "Remove the figure" to build a clean background plate when overlap is large |
| **DepthFlow** (BrokenSource) | **AGPL-3.0** ([repo](https://github.com/BrokenSource/DepthFlow)); very active (pushed 2026-11-13) | GPU shaders; Mac support not tested here | Good reference for camera presets (dolly, orbit, zoom, vignette). Use it only as a separate CLI, unmodified, if at all. The pipeline repo is on GitHub, so importing it as a library risks AGPL obligations. Writing our own is easy |
| 3D Ken Burns (sniklaus) | **CC BY-NC-SA 4.0** (Verified LICENSE) | — | Excluded |
| 3d-photo-inpainting (VT) | MIT code incl. MiDaS; 2020-era, CUDA, slow | — | Skip |
| ml-sharp (Apple) | research-only model; video render CUDA-only | — | Excluded |

### Recommended design ("multiplane chalk camera")
1. After `chalk_from_image`, compute a figure mask (BiRefNet automatic, or SAM 2.1 with a box from the scene plan) and a DA-V2-Small depth map. Run them sequentially and unload, per the memory rule; both are small.
2. Quantize into 2–3 planes: figure, mid scenery, far scenery. The board stays as plane 0 and moves with the far plane, so the chalk never looks detached from the board.
3. Animate the planes with different `cam_matrix` parameters (for example far 1.00→1.03 zoom, figure 1.00→1.08 plus a 10–20 px lateral drift) and fill the thin gaps with `cv2.inpaint` or a dilated copy of the far plane.
4. The stroke reveal still runs first. Parallax starts once a plane is drawn, which matches how the camera would move after the drawing finishes.
5. QA: SSIM between consecutive frames to catch tearing, plus a visual check at G2.

This keeps the approved look, adds visible depth, costs a few seconds per scene, and needs no new heavy model. Caveat: monocular depth on stylised chalk images is unvalidated. If the depth map is noisy, fall back to mask-only two-plane parallax (figure vs. rest), which needs no depth model at all.

---

## 4. Frame interpolation, upscaling, colour, overlays, captions, transitions

### Frame interpolation
- Practical-RIFE: MIT, active (pushed 2026-08) ([repo](https://github.com/hzwer/Practical-RIFE)).
- rife-ncnn-vulkan: MIT; runs on Mac through MoltenVK (Mac support not tested here); last push 2024.
- FILM (Google): Apache-2.0 but **archived** (TensorFlow).
- **Verdict: not needed.** The renderer already produces every frame at 30 fps procedurally. Interpolation only helps if diffusion clips are adopted. LTX outputs 24 fps; ffmpeg `minterpolate` or RIFE could convert those.

### Upscaling
Images are generated at 768x1344 and resized to the 1080x1920 canvas.

| Tool | Licence | Notes |
|---|---|---|
| Real-ESRGAN | BSD-3-Clause (Verified); last push 2024-08 | The `realesr-animevideov3` / anime models suit line art. The ncnn-vulkan binary (licence tag NOASSERTION) runs on Mac. Weights licence assumed to follow the repo; not separately verified |
| SeedVR2 3B/7B | Apache-2.0 (Verified HF); built into mflux ("best upscaling model") | Heavy (3B+), so it would be another model load per scene |

**Verdict: low value.** `chalk_from_image` blurs and textures the image anyway, so upscaler detail gets overwritten by chalk texture. The cheaper quality fix is to generate at 768x1344, which is already done. Test Real-ESRGAN anime on one scene only if the owner notices softness.

### Colour grading
- ffmpeg `lut3d`, `curves`, `eq` and `colorbalance` are built in.
- The chalk palette is deliberately restricted (`restrict_palette`), so a film LUT would fight the approved look.
- If a grade is wanted (for example a warmer board for a night scene), generate `.cube` files in Python. This is about 20 lines of numpy and has no licence question.
- Free LUT packs:
  - The Q-DDL pack of 800+ LUTs is CC BY 4.0, so attribution is required ([80.lv](https://80.lv/articles/800-free-luts-released)).
  - FreeVisuals packs say "commercial use, no attribution" (site terms only).
  - The PHLEARN and Cinecom free packs restrict commercial or redistribution use.
  - No CC0 LUT pack was found.
- **Verdict: skip packs. Use self-generated LUTs if needed.**

### Particle and VFX overlays
- **Procedural Python is best.** It is licence-free, matches the palette and is already the pattern in `chalk.py`. Good additions:
  - drifting chalk dust motes
  - smoke and fire wisps made from noise-displaced chalk strokes
  - falling petals or arrows as chalk sprites
  - shimmer on divine figures (an animated glow mask)
  - rain or wind lines
- CC0 assets: Poly Haven is CC0 for all assets, per its FAQ ([polyhaven.com/faq](https://polyhaven.com/faq)), and ambientCG is reported CC0 (secondary sources). These are textures and HDRIs, useful only for board or paper textures.
- Pixabay and Pexels video overlay licences were not verified in this session. Pixabay audio is known to trigger Content ID claims (earlier report), so avoid stock overlays.

### Motion graphics and captions

| Tool | Licence (Verified) | Activity | Fit |
|---|---|---|---|
| ffmpeg drawtext/ASS + PIL (current) | LGPL/GPL | — | Already does word-synced captions with Indic shaping via libraqm; keep |
| **Manim Community** | MIT | very active (2026-11-14) | Maps, family trees, timelines, arrows for explainer moments. Render separately to transparent `.mov` and composite. Indic text works through its Pango text (not tested here) |
| MoviePy | MIT | active (2026-08) | Adds nothing over the current numpy + ffmpeg writer; skip |
| pycaps | MIT per README; GitHub "No releases published"; needs a browser renderer ([DEV article](https://dev.to/francozanardi/adding-animated-subtitles-to-videos-with-python-4hml)) | active development | CSS-styled animated captions. The current caption engine already handles Devanagari/Telugu/Gujarati shaping and postposition rules, so switching is risky; skip |
| captacity | MIT | stale (2024-06) | Skip |
| Remotion | Free for individuals and for-profits with **up to 3 employees**; company licence above that; Remotion 5.0 will require a `"free-license"` key in render APIs ([LICENSE.md](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md), [5.0 migration](https://remotion.dev/docs/5-0-migration)) | very active | Allowed for the solo owner, but adds a Node/React toolchain. PROJECT_CONTEXT already lists it as excluded; keep it excluded |
| Motion Canvas / Revideo | MIT / MIT | 2026-07 | Same Node objection; skip |
| PySceneDetect | BSD-3-Clause | very active | QA helper: detect unintended cuts or flashes |

### Transitions
- The approved whole-board streak-erase stays.
- Variety is possible without new tools: ffmpeg `xfade` has about 40 built-in transitions, but most look non-chalk. A better option is procedural chalk transitions in `chalk.py`: a sponge wipe, a chalk-dust puff, and a page-turn of the board.
- **Verdict:** keep it procedural. Nothing to install.

---

## 5. Animation approaches and Indian painting styles

### Rigged 2D puppets and motion comics

| Tool | Licence (Verified) | Activity | Assessment |
|---|---|---|---|
| Spine | paid | — | Excluded |
| Live2D Cubism | proprietary, paid tiers (prior knowledge) | — | Excluded |
| **Inochi2D** (Creator + Session) | BSD-2-Clause | creator 2025-06, session 2025-11 | Live2D-like mesh puppets; built for VTubing. Its format is open, but there is no Python renderer. Too much manual rigging per character for a daily cadence |
| OpenToonz | BSD-3-Clause | very active | Full desktop animation suite; manual |
| Synfig | GPL-3.0 (outputs unrestricted) | very active | Bones and vector tweening; CLI renderer exists (`synfig file.sifz -o out.png`). Manual rigging per character |
| Blender + COA Tools 2 | Blender GPL; coa_tools2 GPL-3.0 (2026-09) | active | Cutout rigs; heavy to run alongside models on 16 GB, but Blender alone renders fine. Manual |
| Meta AnimatedDrawings | MIT | **archived 2025-09** | Auto-rigs a single drawn figure and retargets motion clips. Tested on macOS but uses Docker/TorchServe for detection. Unmaintained |
| LivePortrait | MIT code, but bundles insightface models that are non-commercial ("remove and replace InsightFace's detection models" for commercial use) ([LICENSE](https://github.com/KwaiVGI/LivePortrait)) | 2026-06 | Face reenactment needs realistic faces; poor fit for chalk |

**Recommended: a "motion comic lite" in Python, not puppet rigs.**
1. Use the section-3 masks (SAM 2.1/BiRefNet) to isolate the main figure.
2. Apply cheap procedural motions to it:
   - breathing: 0.5–1% vertical scale at about 0.25 Hz
   - head and arm sway: mesh warp with `cv2.remap` inside a soft mask
   - cloth or hair flutter: noise displacement limited to the top of the mask
   - blinking: skip; chalk eyes are too small
3. Add procedural FX particles (section 4).

This gives "alive" scenes with no rigging per character and no new heavy models. The owner should judge whether the motion reads as charming or uncanny on chalk.

### Anime-style models
- Anima is non-commercial.
- FLUX.2 klein 4B renders anime, but "line art looks like typical AI anime" (lilting.ch).
- The chalk style is the brand, so an anime style is not recommended for this series.

### Traditional Indian painting styles (Madhubani, Pattachitra, Kalamkari, Mughal miniature)
- **Base-model prompting:** Z-Image and FLUX.2 klein 4B know these names at some level; quality was not tested. A 4-style prompt test of 4 images each on Z-Image costs about 30 minutes and is the cheapest evidence.
- **Ready-made LoRAs found:**
  - `rexoscare/bengali-pattachitra-paintings-art-model` and `rexoscare/kalighat-paintings-lora`: SDXL DreamBooth LoRAs on HF; licence not checked.
  - `prithivMLmods/Canopus-Textile-Pattern-adp-LoRA`: SDXL, textile Kalamkari patterns; licence not checked.
  - "IMZ Madhubani Painting Style flux" on Shakker: a **FLUX.1-dev** LoRA, so the FLUX.1-dev non-commercial terms apply to running it. Excluded.

  Sources: [search summary](https://huggingface.co/rexoscare/bengali-pattachitra-paintings-art-model), [Canopus](https://huggingface.co/prithivMLmods/Canopus-Textile-Pattern-adp-LoRA). Using SDXL LoRAs means adding an SDXL runtime (ComfyUI or diffusers MPS), which is a second image stack.
- **Better route:** train our own style LoRA on Z-Image base or klein base 4B with `mflux-train`. Training images must be public-domain or owned:
  - Wikimedia Commons scans of pre-1900 Mughal or Pattachitra works are public domain in most jurisdictions, but check each file's licence.
  - Contemporary Madhubani artists' works are copyrighted and must not be used.
- **Fit with the chalk look:** a folk-art series would be a *new style preset in `styles.py`*, not a change to the approved chalk episodes. Treat it as a G1-level creative decision for the owner.

---

## Ranked shortlist for this pipeline

Install cost: disk and new dependencies. Engineering: rough effort for the Python glue. Quality gain: expected visible improvement, judged against the current chalk renders (an estimate, not measured).

| Rank | Addition | Licence | Install cost | Engineering | Expected quality gain |
|---|---|---|---|---|---|
| 1 | **FLUX.2 klein 4B reference-locked scenes + edit cleanup** (mflux, already installed) | Apache-2.0 | about 4–8 GB disk (4-bit vs 8-bit); no new package | Small: a `scene_with_refs` path in the image step, character sheets in `profiles/` | **High**: fixes character drift (beard/age) and removes stray borders and figures via edit passes |
| 2 | **Mask-based multiplane parallax** (BiRefNet MIT or SAM 2.1 Apache + own numpy renderer) | MIT / Apache | about 1 GB models; `transformers` or `sam2` package | Medium (about 200 lines in `chalk.py`) | **High**: real depth motion instead of flat zoom, chalk look unchanged |
| 3 | **Depth Anything V2 Small** for 3-plane depth splits | Apache-2.0 | about 100 MB | Small on top of #2 | Medium: richer parallax; fall back to masks if depth is noisy on chalk |
| 4 | **Procedural "alive" motion**: breathing and sway on the figure mask, chalk dust, fire and smoke wisps, petals | none (own code) | 0 | Medium | **Medium-high**: scenes stop feeling static; fully on-brand |
| 5 | **Chalk style LoRA** (Z-Image base or klein base 4B via `mflux-train`) trained on approved frames | Apache-2.0 base | 0 new; overnight training run, RAM-tight | Medium (dataset curation, captioning) | Medium-high: closer to sparse line-art chalk, which is the known Z-Image limitation |
| 6 | **Z-Image Union ControlNet 2.1** (canny/depth) for composition continuity between scenes and for thumbnails | Apache-2.0 | about 1–3 GB (not measured) | Small (mflux flag) | Medium: consistent staging; reuse of layouts |
| 7 | **Per-character LoRAs** (after #1, only if references are not enough) | Apache-2.0 base | training time per character | Medium | Medium: stronger identity than reference editing alone |
| 8 | **Manim** inserts for maps, lineage trees and timelines in explainer beats | MIT | pip + LaTeX optional (Cairo/Pango via brew) | Medium | Medium for history and science genres; low for pure story beats |
| 9 | **Procedural chalk transitions** (sponge wipe, dust puff) as variants of streak-erase | own code | 0 | Small | Low-medium: variety without leaving the style |
| 10 | **LTX-2.3 int8 via ltx-2-mlx `--low-ram`**: one first/last-frame hero shot test | LTX-2 Community (free < $10M revenue) | about 26 GB disk + Gemma text encoder; new venv | Medium; long runs with progress reporting | Unknown until tested; risk of style drift; 10–15+ min per clip |

Run order: 1 → 2/3 → 4 → 5. Items 1–4 need no new heavy model running alongside others. Item 5 and item 10 are overnight or solo runs. Every visual change goes to the owner as a side-by-side sample on one existing scene before it touches an episode.

## Explicitly NOT worth it

- **Licence problems:**
  - Depth Pro and ml-sharp: Apple research-only weights.
  - FLUX.1 dev, Krea-dev, Kontext dev, Fill dev; FLUX.2 klein 9B and FLUX.2 dev: non-commercial.
  - Qwen-Image 2.1: research licence.
  - Anima and FIBO 2: non-commercial.
  - InfiniteYou: CC-BY-NC.
  - InstantID and PuLID: insightface research-only face models plus research-only checkpoints.
  - RMBG-2.0: Bria licence.
  - 3D Ken Burns: CC BY-NC-SA.
  - Depth Anything V2/V3 Base, Large and Giant: CC-BY-NC.
  - HunyuanVideo and FramePack: territory-restricted Hunyuan licence.
  - LivePortrait as shipped: insightface.
  - FLUX.1-dev-based Indian-style LoRAs.
- **Revenue-capped or terms to re-read; avoid unless there is a clear gain:**
  - Krea 2: < $1M (Unverified).
  - SD 3.5: < $1M.
  - FLUX 3 Klein: < $5M (Unverified).
  - CogVideoX-5B: registration required.
- **Too heavy for 16 GB:**
  - Qwen-Image / Qwen-Image-Edit 20B: about 25 GB 4-bit build.
  - HiDream 17B.
  - Wan 14B: 82 min per 2 s on an M1 Max 64 GB.
  - LTX-2.5: 47–120 GB packs.
  - FramePack.
- **Low value for chalk:**
  - Real-ESRGAN, SeedVR2 and other upscalers: chalk texture overwrites the detail.
  - RIFE and FILM interpolation: frames are procedural at 30 fps already.
  - Film LUT packs: they fight the restricted palette.
  - Anime models.
  - AnimateDiff: dated, SD1.5.
  - Wan 2.1 1.3B: T2V only, 480p, slow on MPS.
- **Toolchain cost without gain:**
  - Remotion, Motion Canvas, Revideo: a Node stack.
  - MoviePy: nothing new.
  - pycaps and captacity: would regress Indic caption handling.
  - ComfyUI as a pipeline component: GPL app, slower than MLX, and not deterministic glue.
  - DiffusionKit and IOPaint: archived.
  - FILM: archived.
  - AnimatedDrawings: archived.
  - Spine and Live2D: paid.
  - Inochi2D, Synfig, OpenToonz and Blender puppet rigs: manual rigging per character does not fit a daily cadence.
- **AGPL:** DepthFlow. Fine as an unmodified external CLI for experiments, but write our own multiplane renderer instead.

## Gaps and things to measure locally

- No M5 Air measurement exists for any model here. Before adopting #1, time FLUX.2 klein 4B (4-bit and 8-bit) at 768x1344, text-to-image and edit with 1–2 references, and record peak RSS with `/usr/bin/time -l`.
- `mflux-train` speed and memory on 16 GB are unknown. Pilot at 512 px.
- Depth estimation quality on chalk-style stills is unknown. Test DA-V2 Small on 5 existing scene images from C0001–C0005.
- The FLUX 3 Klein (Kommunity) and Krea 2 licence texts were not read directly. SD 3.5's $1M cap is from the earlier report, not re-fetched.
- Licence tags for Real-ESRGAN weights, ToonCrafter weights, AnimateDiff motion modules and the SDXL Indian-style LoRAs were not found on the cards. Treat them as unverified.
- Pixabay and Pexels video licences were not checked.
- The LTX-2 licence was read by grep of key clauses (the $10M threshold, output ownership and the acceptable-use section), not end to end. Read it in full before publishing any LTX output.
