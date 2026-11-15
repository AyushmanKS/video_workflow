# Open-source image, character-consistency and animation tools for a 16 GB Apple Silicon short-video pipeline (as of Nov 2026)

Context: current pipeline uses Z-Image Turbo (4-bit, mflux 0.24) at 768x1344, a custom Python stroke-reveal chalk animator, Ken Burns, ffmpeg. Pain points: character drift, unwanted borders/text, unrequested figures, static images. Constraint: zero cost, local, commercial use, MacBook Air M5 16 GB.

Research ran on 2026-11-16 with about 17 searches and fetches. Many 2026 model facts come from secondary blogs, so treat them as needing verification against the official LICENSE file before adoption. Licenses matter most here, because several 2026 releases moved away from Apache 2.0.

## Q1. Image models usable on 16 GB Mac (mflux / MLX / Draw Things) and their commercial licenses

### Takeaway
Two models are both commercially clean and practical on 16 GB: Z-Image (Turbo and Base) and FLUX.2 [klein] 4B, both Apache 2.0. FLUX.2 klein 4B adds native multi-reference editing, so it is the strongest single upgrade for character consistency. Many 2026 newcomers in mflux carry licenses that are non-commercial or capped by revenue: FLUX.2 klein 9B, Qwen-Image 2.1, Krea 2 and FLUX 3 Image Klein. Each needs a license check before use.

### Cited Findings
- **mflux model roster (README, Nov 2026).** The fetched README lists the following models:
  - Z-Image (6B; distilled and base; LoRA training supported)
  - FLUX.2 (Jan 2026; 4B and 9B; distilled and base; LoRA training; editing). The README calls it the smallest and fastest.
  - FLUX 3 Image Klein (Oct 2026; 5.6B plus a 4B text encoder; up to 10 reference images; 16 steps distilled, 50 base; no LoRA training)
  - Krea 2 (Jun 2026; 12B turbo)
  - Iris-3B (Oct 2026; pixel-space, no VAE; 4 steps turbo)
  - Qwen Image (20B, slower, edit capable)
  - Qwen Image 2.1 (Sep 2026; 7.1B plus an 8B text encoder; 8-step turbo; multi-reference editing, LoRA, RGBA)
  - FIBO 2 (8.1B; edits 1–5 images with masks; 4-step Edit Turbo)
  - Anima (2B anime/illustration)
  - ERNIE-Image, Ideogram 4, Lens, Ming-Image, MOSS-Image, SenseNova-U1.5, Boogu Image
  - SeedVR2 (upscaling) and Depth Pro (depth)
  - FLUX.1 (legacy; Kontext editing)

  [mflux GitHub](https://github.com/filipstrand/mflux)
- **mflux features and precision.** Features include multi-LoRA, LoRA finetuning, LoKr, in-context editing, multi-image editing, ControlNet (Union for Z-Image and Qwen-Image-2.1, depth for Krea 2, Canny for FLUX.1), fill/inpainting, Redux, depth conditioning and SeedVR2 upscaling. The README gives no memory or timing benchmarks. float16 compute (`--compute-precision float16`) is supported for FLUX.2, FLUX 3 Klein, Z-Image, Qwen-Image 2.1 and Anima. [mflux GitHub](https://github.com/filipstrand/mflux)
- **Z-Image licensing and status.** Z-Image and Z-Image-Turbo weights are Apache 2.0. Tongyi's own README still lists Z-Image-Omni-Base and Z-Image-Edit as "To be released". Some aggregators claim Z-Image-Edit shipped, but nothing official backs that up, so treat it as unverified. [Z-Image README (jsdelivr mirror)](https://cdn.jsdelivr.net/gh/Tongyi-MAI/Z-Image@main/README.md); [Tongyi-MAI GitHub issue](https://github.com/Tongyi-MAI/Z-Image/issues/163); conflicting claim at [CometAPI](https://www.cometapi.com/what-is-z-image/)
- **FLUX.2 [klein] licensing and capability.**
  - 4B (distilled and base): Apache 2.0, commercial use allowed.
  - 9B: FLUX Non-Commercial License.
  - Multi-reference editing is native, with up to 4 reference images.
  - VRAM figures conflict: BFL's blog says about 13 GB, while the repo docs say about 8 GB.
  - BFL also says the 9B KV variant is faster for multi-reference editing.

  [HF model card](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B); [BFL blog](https://bfl.ai/blog/flux2-klein-towards-interactive-visual-intelligence); [VentureBeat](https://venturebeat.com/technology/black-forest-labs-launches-open-source-flux-2-klein-to-generate-ai-images-in)
- **FLUX 3 Image Klein** (released 2026-10-15, 5.6B). It uses the FLUX Kommunity License, which secondary sources describe as free commercial use for organisations under $5M annual revenue. The HF weights are gated. The license text was not verified directly. [unite.ai](https://www.unite.ai/new-5-6b-parameter-flux-3-image-klein-debuts-as-open-weights-release/); [eesel.ai](https://www.eesel.ai/blog/flux-3-klein); [mer.vin](https://mer.vin/news/flux-3-klein-open-weights-image-model/)
- **Qwen-Image 2.1** (released 2026-09-20, 7B). It uses the Qwen Research License, which is non-commercial only; commercial use needs a separate agreement. Earlier Qwen-Image releases, including the 2509 and 2511 Edit models, were Apache 2.0. [mixed-news](https://mixed-news.com/en/qwen-image-2-1-transparent-rgba-7b-open-weights-research-licence/); [MarkTechPost](https://www.marktechpost.com/2026/09/21/alibaba-qwen-releases-qwen-image-2-1/); [cellcog](https://cellcog.ai/blog/qwen-image-2-1/)
- **Qwen-Image-Edit-2511** is Apache 2.0, and its model card claims it preserves subject identity across edits. Community mflux and MLX quantizations exist, including mlx-community 8-bit and fcreait 3–8 bit builds. [HF Qwen-Image-Edit-2511](https://huggingface.co/Qwen/Qwen-Image-Edit-2511); [mlx-community 8bit](https://huggingface.co/mlx-community/qwen-image-edit-2511-8bit); [fcreait mflux builds](https://huggingface.co/fcreait/Qwen-Image-Edit-mflux)
- **Krea 2** (12B, June 2026) uses the Krea 2 Community License. Commercial use is reportedly allowed only below $1M trailing annual revenue. The license requires content filtering by deployers and a "Krea" name prefix on derivatives. [HF Krea-2-Turbo](https://huggingface.co/krea/Krea-2-Turbo); [localaimaster](https://localaimaster.com/blog/krea-2-local-guide); [krea2ai clause guide](https://krea2ai.com/blog/krea-2-license-commercial-use)
- **FLUX.1 Kontext [dev]** uses the FLUX.1 [dev] Non-Commercial License. The license text says outputs may be used commercially, but running the model commercially needs a paid BFL license. A v1.1 wording change that seemed to restrict outputs was reverted. [HF model card](https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev); [HF license discussion](https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev/discussions/6); [BFL blog](https://bfl.ai/blog/flux-1-kontext-dev)

### Inferences
- **Recommended commercially clean stack.** Keep Z-Image Turbo for text-to-image. Add FLUX.2 klein 4B (Apache 2.0) for reference-based scene generation and editing, and Qwen-Image-Edit-2511 (Apache 2.0) as a heavier alternative for edits. At 20B, Qwen-Image-Edit-2511 probably needs about 4-bit quantization and is slow on 16 GB. That is an estimate, not a benchmark.
- **Models to avoid or verify first.** Avoid Qwen-Image 2.1, FLUX.2 klein 9B and FLUX.1 Kontext dev, because they are non-commercial for model use. Krea 2 (below $1M) and FLUX 3 Klein (below $5M) are probably usable by a solo creator under their revenue caps. They are not Apache 2.0, however, and they carry gating and acceptable-use obligations, so verify the license text first.
- **Unwanted borders, text and extra figures.** These are prompt and sampler issues more than model issues. Two remedies are reasonable to test, though neither is benchmarked:
  - Use base or CFG-capable variants (Z-Image Base, FLUX.2 klein base), which accept negative prompts. Distilled turbo models typically ignore CFG and negatives.
  - Use editing models to remove artefacts ("remove the border and text") as a cleanup pass.
- **Not covered by this session.** HiDream, Lumina, SD3.5, Chroma, Iris-3B, FIBO 2, ERNIE-Image and Anima licenses were not verified. As background only, unverified here: HiDream-I1 was reportedly MIT, SD3.5 uses the Stability Community License (free under $1M revenue), Chroma was Apache 2.0, and FIBO v1 weights were reportedly non-commercial.

### Gaps
- No measured speed or memory figures for any of these models on a 16 GB M5 were found. The mflux README gives none.
- Draw Things release notes were not checked in this session.
- The exact mflux CLI names for FLUX.2 editing and FLUX 3 Klein multi-reference are in per-model READMEs, which were not fetched.
- Licenses were not verified for Iris-3B, FIBO 2, ERNIE-Image, MOSS-Image, Lens, Ming-Image, Boogu or SenseNova.

## Q2. Character consistency methods available on Mac

### Takeaway
On Mac, the practical route is reference-image conditioning with an edit or multi-reference model, combined with a small character LoRA trained locally in mflux. There is no MLX IP-Adapter or InstantID; mflux offers in-context editing, multi-image editing and Redux instead.

### Cited Findings
- **mflux consistency features.** mflux supports in-context editing, multi-image editing, Redux, and LoRA finetuning including LoKr. LoRA training is listed for Z-Image, FLUX.2, Krea 2, Iris-3B, ERNIE-Image, Anima, FIBO 2 and Qwen Image 2.1. It is not supported for FLUX 3 Klein or legacy FLUX.1. [mflux GitHub](https://github.com/filipstrand/mflux)
- **Training details.** mflux v0.16.0 added base-model training for Z-Image, plus dedicated FLUX.2 and Z-Image training adapters. `mflux-train` documents fine-tuning for flux2-klein-base-4b and 9b. [mflux v0.16.0 release](https://newreleases.io/project/github/filipstrand/mflux/release/v.0.16.0); [mflux docs (algolia)](https://docsearch.algolia.com/mcp/docs/repo/filipstrand/mflux)
- **Reference capacity per model.**
  - FLUX.2 klein 4B: up to 4 reference images. [VentureBeat](https://venturebeat.com/technology/black-forest-labs-launches-open-source-flux-2-klein-to-generate-ai-images-in)
  - FLUX 3 Klein: up to 10 reference images. [mflux GitHub](https://github.com/filipstrand/mflux)
  - Qwen-Image-Edit-2511 claims identity preservation from an input portrait. [HF](https://huggingface.co/Qwen/Qwen-Image-Edit-2511)

### Inferences
Concrete fixes for the bearded vs clean-shaven and adult vs child drift:
1. **Character sheets.** Generate one canonical sheet per character (for example, a front-view sage with a long white beard) with Z-Image. Then generate every scene through FLUX.2 klein 4B using that sheet as a reference image, with a prompt like "same sage as reference, …". This is likely the cheapest large win.
2. **Character LoRA.** Train a small LoRA per recurring character on Z-Image base or FLUX.2 klein base 4B, using 10–20 curated sheet images and `mflux-train`. Run inference with the LoRA on the turbo model. Training time on 16 GB is unknown and needs a pilot run. Training is a heavy model run, so it must run alone (memory rule).
3. **Automated check.** Add a QA step that compares each scene's face or figure crop against the sheet, for example with CLIP or DINO similarity, and flags drift before G2. The CLIP/DINO choice is a suggestion; no source was checked for it.

### Gaps
- No Mac benchmarks for mflux LoRA training time or peak memory were found.
- No reports were found on how well a Z-Image LoRA transfers to a chalkboard style.
- No working IP-Adapter or InstantID equivalent for MLX was found.

## Q3. Image-to-video / animation on 16 GB Apple Silicon

### Takeaway
Image-to-video now runs natively in MLX through ltx-2-mlx (LTX-2.3 and 2.5, q8 with `--low-ram` streaming on 16 GB) and through mlx-video (LTX-2 and Wan 2.2). It is slow: expect roughly 10–15+ minutes per few-second clip on a 16 GB machine. That makes it suitable for 1–3 hero shots per video, not every scene. LTX weights are free for commercial use under $10M revenue (community license). The Wan 2.2 license was not verified this session.

### Cited Findings
- **ltx-2-mlx.**
  - Pure MLX port with MIT code. It supports LTX-2.3 and LTX-2.5 in bf16, int8 and int4.
  - Memory: int8 needs 16 GB with `--low-ram`, which streams transformer blocks from disk; int4 needs 16 GB+.
  - Image-to-video takes multiple anchor images and frame positions.
  - Timing: on an M1 Max, a 576x1024x241-frame distilled I2V render took 701 s, falling to 563 s with `LTX2_COMPUTE_DTYPE=float16`.

  [dgrauet/ltx-2-mlx](https://github.com/dgrauet/ltx-2-mlx)
- **mlx-video (Blaizzy)** supports LTX-2 image-to-video (distilled and dev) with experimental synced audio, and Wan 2.2 I2V and TI2V. [Blaizzy/mlx-video](https://github.com/Blaizzy/mlx-video); [mlx-video Wan2.2 README mirror](https://git.ddq.nl/n0p/mlx-video/raw/branch/main/mlx_video/models/wan_2/README.md)
- **Real-world timings.**
  - Mac M1 16 GB: about 15 minutes for a clip of about 4 seconds. The source is not MLX-specific.
  - GGUF Wan 2.2 on an M1 Max 64 GB: 82 minutes per 2-second clip. FP8 fails on Metal.

  [lilting.ch](https://lilting.ch/en/articles/ltx2-wan22-mac-local-video-gen)
- **Wan 2.2 TI2V 5B on Mac.**
  - MLX q8 on a 64 GB Mac: about 15 minutes for 720p, 41 frames, 20 steps; 32 GB+ recommended.
  - A distilled INT8 build on an M4 Max 36 GB: about 151 s end to end, 9.34 GiB peak.
  - The model is said to run at Q4 GGUF on an M4 24 GB, with no timing given.

  [HF Anes1032 Wan2.2-TI2V-5B-mlx-q8](https://huggingface.co/Anes1032/Wan2.2-TI2V-5B-mlx-q8); [FastMetal article](https://www.besthub.dev/articles/fastmetal-run-text-to-video-locally-on-mac-with-apple-silicon-51de9979fe23); [modelfit.io](https://modelfit.io/video/wan-2-2-5b/)
- **LTX-2 license.**
  - Free commercial self-hosting and fine-tuning below $10M annual revenue, with affiliates counted together. Above that, a paid agreement is required.
  - Sources disagree on wording (ARR vs annual revenue).
  - One vendor claims embedding the weights in a sold product needs a license even below the threshold.

  [Lightricks license page](https://ltx.io/model/license); [LTX-2.3 LICENSE on HF](https://huggingface.co/Lightricks/LTX-2.3/blob/main/LICENSE); [scancode ltx-2-cla-2026](https://scancode-licensedb.aboutcode.org/ltx-2-cla-2026.html)

### Inferences
- **LTX-2.5 q8 via ltx-2-mlx `--low-ram`** is the most credible 16 GB I2V option. A 241-frame clip took about 9–12 minutes on an M1 Max, so a 16 GB Air will be slower and may thermally throttle. Practical use is short 2–4 s motion inserts (wind in hair, flickering fire, drifting smoke) on 1–3 key scenes per video. It needs the existing progress-reporting protocol and must not run alongside the image or voice models.
- **Chalk style risk.** The video model may "realise" the chalk drawing into photoreal motion. Test conditioning with a first and last frame both taken from the chalk still.
- **Wan 2.2 5B** is a second option. Its 32 GB recommendation and slower runtime make it worse than LTX on 16 GB.
- **Not researched this session:** FramePack, HunyuanVideo small variants and AnimateDiff on MPS.

### Gaps
- No verified end-to-end ltx-2-mlx benchmark on a 16 GB Mac.
- Wan 2.2 license not verified this session (believed Apache 2.0 from prior knowledge; unverified here).
- No information on FramePack or HunyuanVideo on MLX.

## Q4. 2D / motion-graphics tooling, vectorization and depth parallax

### Takeaway
Two additions are cheap and Mac-friendly with high impact on static images:
1. **Depth parallax.** Depth Anything V2 **Small** (Apache 2.0; Base, Large and Giant are CC-BY-NC) or mflux's built-in Depth Pro gives a depth map. A 2.5D camera move then turns Ken Burns into real parallax.
2. **True stroke-order drawing.** Vectorize with VTracer (MIT), or with Potrace (GPL, best called as an external CLI), then animate SVG paths in order. This gives real stroke-order chalk drawing instead of mask reveals.

Remotion is free for teams of 3 or fewer people.

### Cited Findings
- **Depth Anything V2 licensing.** The Small checkpoint is Apache 2.0, and Base, Large and Giant are CC-BY-NC-4.0. Roboflow's listing contradicts this by calling Base and Large Apache 2.0; follow the upstream cards. [HF Depth-Anything-V2-Small card](https://huggingface.co/depth-anything/Depth-Anything-V2-Small/raw/main/README.md); [upstream README](https://cdn.jsdelivr.net/gh/depthanything/depth-anything-v2@main/README.md); contradicted by [Roboflow](https://roboflow.com/model/depth-anything-v2)
- **mflux depth.** mflux includes Depth Pro depth estimation, which the README calls very fast, plus depth-map extraction and depth conditioning. [mflux GitHub](https://github.com/filipstrand/mflux)
- **Vectorizer licenses.** VTracer is MIT; Potrace is GPL-2.0-or-later. [Wikipedia raster-to-vector comparison](https://www.wikipedia.org/wiki/Comparison_of_raster_to_vector_conversion_software); [Wikipedia Potrace](https://en.wikipedia.org/wiki/Potrace)
- **Remotion licensing.** Free for individuals, non-profits and for-profits with 3 or fewer employees. Companies of 4 or more need a paid Company License. Functionality is identical across tiers. [Remotion LICENSE](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md); [Remotion license FAQ](https://www.remotion.dev/docs/license/faq)
- **Motion Canvas and Revideo** are described as MIT or Apache engines with no per-seat cost. This is a secondary claim. [Capital & Compute](https://capitalandcompute.net/blog/best-open-source-ai-video-tools/)

### Inferences
- **Depth parallax.** Run Depth Pro (already in mflux) or DA-V2 Small on each 768x1344 still. Separate the image into 2–3 depth layers, inpaint the background behind the foreground (Z-Image or FLUX.2 fill), then animate layer offsets or a mesh-warp camera in Python/ffmpeg. This is a modest engineering job that gives cinematic motion at near-zero runtime cost, and it suits the chalk style better than video diffusion. It is not benchmarked.
- **Stroke order.**
  - Approach: threshold the chalk lines, skeletonize (scikit-image), vectorize with VTracer in centerline or spline mode, sort paths by position, area or semantic region, and draw progressively with the existing chalk texture and SFX.
  - Why VTracer: it is MIT and avoids GPL questions. Running Potrace as a separate executable whose SVG output is used probably creates no copyleft obligation on the pipeline code. That is a reasonable reading, not legal advice.
- **Motion graphics.** Manim Community (believed MIT, unverified here) or Motion Canvas could add diagrams, maps and text callouts. Remotion is fine for a solo owner but would need a license if the team grows past 3. Blender Grease Pencil scripting (Blender is GPL, and rendered outputs are unrestricted, from prior knowledge) is powerful but heavy for a 16 GB Air.
- **Unwanted borders.** An automatic post-step could detect uniform frame borders and auto-crop or outpaint them. No source was checked for this.

### Gaps
- Licenses and maintenance status of Manim Community, Motion Canvas, Revideo, rlottie and Blender were not verified this session.
- No existing open-source chalk or whiteboard animation generator with stroke ordering was identified.
- No parallax-from-still reference implementation was found in searches.
