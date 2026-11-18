# Chalk puppet (Kathputli-style) animation: tools, licences, feasibility

Date: 2026-11-17. Scope: animate existing 1080x1920 chalk illustrations (Z-Image Turbo, BiRefNet mask, Depth-Anything-V2 depth per scene) with subtle string-puppet motion, locally on a 16 GB M5 MacBook Air, free and commercially usable. Nothing in the project, `.venv` or HF cache was changed. Tests ran with `.venv/bin/python` read-only (numpy, OpenCV 5.0.0, scipy 1.18.1) and in a throwaway venv in the session scratchpad (libigl 2.6.3, mediapipe). Prior project research is reused where it already answered a question: `research_notes/Studio upgrade research/visual_tools.md` and `research_notes/Shorts studio voices and tools/visual_animation_tools.md`.

Evidence tags: **Verified** (read in the primary source or measured here), **Reported** (secondary source), **Unverified** (not checked).

## 1. Verdict in one paragraph

Build the puppet rig directly into the existing numpy/OpenCV compositor. Cut each moving part (head, forearm, staff, sash end) from the still image as a layer and mesh it with scipy Delaunay. Deform it with libigl ARAP or BBW plus linear blend skinning (MPL-2.0), resample with `cv2.remap(..., INTER_CUBIC)`, and fill the small revealed gaps with OpenCV Telea or NS, or with MI-GAN or LaMa for larger ones. Add Kathputli feel with damped-spring pendulum motion on each joint and a whole-body bob. Drive the environment with noise-field warps (flame, water, leaves) and Verlet chains (flags, sashes). This moves the original chalk pixels and never re-renders them, so the grain survives. The test measured a high-frequency energy ratio of 1.01 with cubic resampling. It is deterministic and fast: about 50–80 ms per animated region per 1080x1920 frame on CPU. Every tool in the chain has a permissive or weak-copyleft licence on both code and weights. AI video (LTX-2.3, Wan 2.2) stays an optional hero-shot path, because diffusion VAEs smooth fine grain and flicker texture. Rig authoring is the real cost: automatic keypoint detection on chalk figures is unreliable (MediaPipe found 1 of 3 figures), so a human-confirmed rig file per character pose is needed.

## 2. Local feasibility test (measured on this Mac, 2026-11-17)

Input: `content/C0008/en/img/02_raw.png` (actually 768x1344, upscaled with Lanczos to 1080x1920) and `02_mask.png`. Scripts and outputs: `/private/tmp/claude-501/-Users-ayushman-Desktop-work-shorts-studio/903db0f3-c533-4373-bf89-91d112b3be29/scratchpad/puppet/` (`test_warp.py`, `layered.py`, `igl_test.py`, `pose_crop.py`, `arap_peak_crop.png`, `layered_crop.png`, `fire_peak_crop.png`, `pose_sage.jpg`, `test.mp4`). The scratchpad is temporary.

Motion tested: the sage raises his staff hand by 38 px (scaled), rotating it 0.10 rad, and turns his head 0.07 rad. The fire flickers through a noise-field warp, and the water gets a sine shimmer.

| Step | Time per 1080x1920 frame | Note |
|---|---|---|
| Mesh from mask (contour + 14 px interior samples, scipy Delaunay, keep triangles inside the mask) | 12 ms (once) | 798 vertices, 1,274 triangles |
| **libigl `arap_precomputation`** | 2.2 ms (once) | Verified |
| **libigl `arap_solve`**, 10 iterations | **1.6 ms** | Verified |
| libigl `bbw`, 3 handles, partition of unity | 17 ms (once per rig) | Verified |
| Own pure-Python ARAP (unvectorised loops, 1,976-vertex grid) | 200 ms | Would be about 10 ms vectorised; libigl makes it unnecessary |
| Dense backward map (grid displacement, cubic upsample, 4-step fixed-point inversion) | 7.3 ms | |
| `cv2.remap` full frame, INTER_CUBIC | 1.4–1.5 ms | |
| `cv2.remap` INTER_LINEAR / LANCZOS4 | 4.4 / 13.5 ms | |
| Fire + water noise-field warp (full frame) | 12.3 ms | |
| Telea / NS inpaint of the arm + staff region | 18 / 13 ms | |
| Layered composite (warp fg + alpha, vacated mask, Telea plate, blend) | 48 ms | 14,105 px revealed |

**Texture preservation.** This is the Laplacian standard deviation of the warped arm/head region compared with the source, measured at the peak pose.

- INTER_LINEAR: **0.82**. The grain is visibly softened, so do not use it.
- INTER_CUBIC: **1.01**. Grain is preserved, and this is the recommended setting.
- LANCZOS4: **1.035**. Slight ringing or over-sharpening, and 9x slower.

Visual check: chalk strokes on the moved hand, staff and face stay crisp and keep their direction relative to the limb. No smoothing or "digital art" look appears.

**Failures observed, and the fix each one teaches.**

1. **Whole-image warp drags the background.** Warping the whole frame made a visible bulge in the river bank behind the raised arm (`arap_peak_crop.png`). Fix: always use layers. Warp only the part's pixels and alpha, then composite over a plate (`layered_crop.png` has no bulge).
2. **Rigid props bend.** The staff curved like rubber under ARAP. Fix: a prop gets one rigid affine transform parented to the hand, not mesh deformation.
3. **Telea fill smears.** The fill is faintly visible as a soft smear under the elbow. It is acceptable for a strip a few pixels wide in motion. For larger reveals, use MI-GAN or LaMa, or better, generate a clean background plate (see §6).
4. **BiRefNet masks are too coarse for part cut-outs.** The mask cropped the staff tip and merges overlapping figures (the sage and the boy in front). Part masks need SAM 2.1 clicks or hand-drawn polygons.
5. **MediaPipe Pose found only 1 of 3 figures.**
   - The sage, seen from the front, gave sensible face, shoulder and hand landmarks (mean visibility 0.80).
   - Both boys, seen from behind, gave 0 detections.
   - Inverting the left boy's crop gave a pose (visibility 0.63) of unknown quality.
   - Full-frame detection gave 0 poses.
   - Keypoint detectors are therefore a suggestion tool only.
6. **RTMPose/DWPose (rtmlib) was not tested.** Its model download from the OpenMMLab server stalled after about 70 MB in 4 minutes, so it was abandoned and its cache deleted.

**Throughput estimate.** A 50 s Short at 30 fps is 1,500 frames. Two or three animated parts plus environment noise take about 60–100 ms per frame, so about 1.5–2.5 min of CPU per language video on top of the current render. No GPU or heavy model is needed at render time, so `data/heavy.lock` is not needed. This is an estimate extrapolated from the per-frame timings above, not a full render.

## 3. Comparison by approach

| # | Approach | Chalk texture | Control / determinism | Automation | Speed (M-series) | Memory | Licence (code / weights) | Verdict |
|---|---|---|---|---|---|---|---|---|
| A | **Own layered mesh rig in numpy/OpenCV + libigl ARAP/BBW/LBS** | Preserved (moves source pixels; cubic HF ratio 1.01, measured) | Full; keyframes in JSON | High once rigged; rig authoring semi-manual | ~50–100 ms/frame (measured parts) | <1 GB | libigl MPL-2.0; scipy BSD; Qhull (scipy Delaunay) permissive; OpenCV Apache-2.0; no weights | **Recommended** |
| B | Meta AnimatedDrawings: reuse only `arap.py` + BVH retarget ideas | Preserved (same pixel-warp idea, but it renders through OpenGL texture mapping) | Good for full-body mocap dances, wrong for subtle seated puppets | Auto-rigs one figure per image | OK | TorchServe + mmdet models | Code, weights and Amateur Drawings dataset are **MIT**; ChildlikeSHAPES CC-BY-4.0; the .mar models were built with Apache-2.0 OpenMMLab (Verified, repo README). Repo **archived 2025-09-03** | Borrow the algorithm only (MIT); do not adopt the pipeline |
| C | Blender 4.x/5.x headless (image-plane meshes + armature, or Grease Pencil v3) | Preserved if the image is used as a texture on a mesh (texture-mapped), with Closest/Cubic sampling | Full | `blender -b -P` scriptable | Unmeasured; EEVEE on Metal likely 0.2–1 s/frame at 1080x1920 (Unverified) | 1–3 GB | Blender GPL, outputs are the user's (Reported, project notes); COA Tools 2 GPL-3.0 (2026-09 activity, Reported) | Fallback only; adds a 1 GB app and a second renderer for no texture gain |
| D | Synfig (Skeleton Deformation layer, CLI `synfig`) | Raster deformation of imported bitmaps keeps texture (Reported, docs) | Manual rigs in the GUI; bone values hard to script (Python plugins operate on .sif files) | Low | OK | low | GPL-3.0, outputs unrestricted | Skip (manual) |
| E | OpenToonz (Plastic tool mesh deformation, `tcomposer` CLI) | Preserved | Manual; ToonzScript does not cover the Plastic tool (not found) | Low | OK | low | BSD-3-Clause (Reported, project notes) | Skip (manual) |
| F | DragonBones | Mesh deformation of bitmaps | Editor (DragonBonesPro) stale; runtimes MIT (DragonBonesJS last push 2025-03-24) | Low; needs a JS/game runtime to render | — | — | Runtimes MIT (Reported) | Skip |
| G | Spine / Moho / Live2D Cubism | Good | Good | — | — | — | Spine and Moho paid. Live2D: the Cubism Editor PRO is paid. The free tier restricts features. The SDK release licence is waived for individuals and small businesses under ¥10M revenue, except Expandable Applications (Reported, live2d.com). | **Exclude** (zero-cost rule / manual) |
| H | Rive | Vector-first; bitmap meshes possible | Editor | — | — | — | Runtimes MIT; **exports moved to paid plans** per Rive's blog (Reported) | Exclude |
| I | Lottie | Vector only; bitmaps only translate/rotate | — | — | — | — | MIT runtimes | Not suitable for chalk raster |
| J | Inochi2D | Mesh puppets | Built for VTubing; no Python renderer (project notes) | Low | — | — | BSD-2-Clause | Skip |
| K | LTX-2.3 I2V from a chalk keyframe (already used in AK01 lab) | **At risk**: VAE re-encode smooths grain, and texture flickers in chunks (Reported: LTX blog on chunked VAE decoding; FreeViS 2025 "over-flattened textures") | Prompt only; non-deterministic | High | 10–15 min per clip on 16 GB (project notes) | heavy | LTX-2 Community Licence: free under **US$10M annual revenue**, no rights claimed in output (Verified earlier, `Studio upgrade research/visual_tools.md`) | Hero shots only |
| L | Wan 2.2 TI2V 5B | Same diffusion risk | Prompt | High | ~15 min per 720p clip, 32 GB+ recommended | heavy | Apache-2.0 (Verified earlier) | Not on 16 GB |
| M | ToonCrafter (DynamiCrafter) | Cartoon interpolation at 512x320; grain lost when upscaled | Two keyframes | Medium | CUDA-oriented | heavy | Apache-2.0 on the model card, but the card calls it "research exploration"; based on DynamiCrafter / SD-family weights (Reported) | Skip |
| N | LivePortrait | Face only; photographic prior | Driving video | Medium | OK on MPS | ~1 GB | Code and weights MIT, but the default face detector is **InsightFace buffalo_l, non-commercial**. Replace it with MediaPipe for commercial use (Reported) | Skip (faces in chalk are tiny; ARAP head-turn is enough) |
| O | AnimateAnything / DrawingSpinUp | DrawingSpinUp rebuilds a 3D model, so texture is re-synthesized | — | — | DrawingSpinUp needs CUDA, tiny-cuda-nn and **Mixamo online** | — | DrawingSpinUp: no licence stated (Verified, repo page) | Skip |

## 4. Licence verdicts per component (code and weights separately)

| Component | Code | Weights / data | Commercial OK? | Source |
|---|---|---|---|---|
| libigl python bindings 2.6.3 (2026-09-01; arm64 wheels cp39–cp312) | MPL-2.0 | — | **Yes** (file-level copyleft only if libigl source files are modified and distributed) | [PyPI libigl](https://pypi.org/project/libigl/) (Verified) |
| scipy `Delaunay` (Qhull) / scipy sparse | BSD-3 / Qhull licence | — | Yes | prior knowledge (Unverified this session) |
| **Triangle (Shewchuk)** | "may not be sold or included in commercial products without a license" | — | **No** without a paid licence; avoid. Also avoid `meshpy` (bundles Triangle and TetGen AGPL) and the `triangle` PyPI wrapper | [cs.cmu.edu/~quake/triangle.html](https://www.cs.cmu.edu/~quake/triangle.html) (Verified) |
| CGAL | GPL/LGPL (commercial licence sold) | — | Avoid; not needed | prior knowledge (Unverified) |
| pytorch3d | BSD | — | Yes, but 3D-oriented and unnecessary | prior knowledge (Unverified) |
| AnimatedDrawings | MIT | MIT (models, Amateur Drawings dataset); OpenMMLab Apache-2.0 | Yes; archived | [GitHub](https://github.com/facebookresearch/AnimatedDrawings) (Verified) |
| SAM 2 / 2.1 | Apache-2.0 | **Apache-2.0** checkpoints | Yes | [sam2 README](https://github.com/facebookresearch/sam2), [Meta blog](https://ai.meta.com/blog/segment-anything-2/) (Reported via search; consistent with HF card checked earlier in project notes) |
| SAM 3 (2025-11-19) | SAM License (custom) | SAM License: royalty-free commercial, use restrictions, Meta may change terms | Allowed but not open; prefer SAM 2.1 | [Roboflow summary](https://roboflow.com/model-licenses/segment-anything-3) (Reported) |
| MobileSAM / EfficientSAM | Apache-2.0 | Apache-2.0 | Likely yes | prior knowledge (Unverified this session) |
| RTMPose / rtmlib / DWPose | Apache-2.0 | Apache-2.0 per mmpose mirrors; training data (COCO-WholeBody, HumanArt) terms unchecked | Probably yes; dataset caveat | [rtmlib](https://github.com/Tau-J/rtmlib), [DWPose ONNX mirror](https://huggingface.co/SceneWorks/dwpose-onnx) (Reported) |
| MediaPipe Pose Landmarker | Apache-2.0 | `.task` bundle licence not stated on the guide; a forum question about it is unanswered; sibling model cards are Apache-2.0 | Probably yes; unconfirmed | [guide](https://ai.google.dev/mediapipe/solutions/vision/pose_landmarker), [forum](https://discuss.ai.google.dev/t/commercial-use-of-mediapipe-pose-landmarker-full/184033) (Reported) |
| bizarre-pose-estimator (anime keypoints) | **AGPL-3.0** | AGPL per HF repackager | Avoid (copyleft reaches pipeline code) | [HF weights](https://huggingface.co/mrpm/ComfyUI-AnimePose-weights) (Reported) |
| LaMa / big-lama | Apache-2.0 | Apache-2.0 per mirrors; trained on Places2 | Yes (Places2 terms unchecked) | [opencv/inpainting_lama](https://huggingface.co/opencv/inpainting_lama) (Reported) |
| MI-GAN (Picsart, ICCV 2023) | MIT | MIT (per ports; Places2 / FFHQ variants) | Yes | [GitHub](https://github.com/Picsart-AI-Research/MI-GAN), [MLX port](https://huggingface.co/mlx-community/MI-GAN-512-places2-fp16) (Reported) |
| OpenCV `inpaint` (Telea, NS) | Apache-2.0 | — | Yes | already in `.venv` |
| Blender | GPL (tool) | outputs owned by the user | Yes | project notes, [blender.org/about/license](https://www.blender.org/about/license/) |
| COA Tools 2 | GPL-3.0 | — | Yes (tool only) | [Aodaruma/coa_tools2](https://github.com/Aodaruma/coa_tools2) (Reported) |
| Synfig / OpenToonz / DragonBones runtimes / Inochi2D | GPL-3 / BSD-3 / MIT / BSD-2 | — | Yes (outputs free) | project notes; [Synfig docs](https://synfig.readthedocs.io/en/latest/layers/skeleton_deformation.html) |
| Spine, Moho, Live2D Cubism Editor PRO, Rive export | paid | — | **Excluded** | [Live2D licence](https://www.live2d.com/en/sdk/license/), [Rive pricing blog](https://rive.app/blog/rive-s-new-9-mo-plan) (Reported) |
| LivePortrait | MIT | MIT, but **InsightFace buffalo_l non-commercial** | Only with the detector swapped | [KwaiVGI HF card](https://huggingface.co/KwaiVGI/LivePortrait), [InsightFace licensing](https://www.insightface.ai/services/models-commercial-licensing) (Reported) |
| ToonCrafter | Apache-2.0 | Apache-2.0 card; "not a commercial product" note | Legally probably yes; practically skip | [HF card](https://huggingface.co/Doubiiu/ToonCrafter) (Reported) |
| LTX-2.x | — | LTX-2 Community Licence, free < US$10M revenue | Yes (already accepted) | project `visual_tools.md` |
| Wan 2.2 | Apache-2.0 | Apache-2.0 | Yes | project `visual_tools.md` |

## 5. How each research question resolves

1. **AnimatedDrawings.**
   - Licences: MIT for code, model weights and the Amateur Drawings dataset. The models were built with OpenMMLab (Apache-2.0).
   - macOS arm64: tested upstream on macOS 13. A contributed `setup_macos.sh` runs TorchServe without Docker, but TorchServe on Apple Silicon is "experimental".
   - Maintenance: the repo is archived (2025-09-03).
   - Its `animated_drawings/model/arap.py` is a small MIT numpy/scipy implementation of the Igarashi two-step ARAP, with pins and a weight of 1000. It takes a caller-supplied triangulation and imports no Triangle library.
   - It is usable as reference code, but libigl's `arap_solve` (1.6 ms) is faster and better tested.
   - Its retargeting maps BVH mocap onto a 2D skeleton with per-limb rotation. That fits dancing children's drawings, not subtle seated Kathputli gestures, so keyframed joint angles are more useful.
2. **Mesh deformation.**
   - libigl (MPL-2.0) exposes `arap_precomputation`/`arap_solve`, `bbw`, `biharmonic_coordinates`, `harmonic`, `lbs_matrix` and `triangulated_grid` (Verified with `dir(igl)`).
   - Use scipy Delaunay on contour + interior samples for meshing (12 ms). Do not use Triangle, `triangle` or `meshpy`.
   - Recommended split:
     - LBS with BBW weights for skeletal parts (arm bones, head on neck).
     - ARAP for soft bends (sash, beard, a hand lifting with the shoulder stretching naturally).
     - A rigid affine transform for props (staff, bow, crown).
3. **Segmentation and keypoints.**
   - SAM 2.1 (Apache-2.0 code and weights) with click or box prompts is the right tool for part masks (forearm, head, staff). The tiny and small checkpoints run on MPS. Run it at rig-authoring time only, with `heavy.lock`.
   - Keypoints: MediaPipe worked on the front-facing sage only. RTMPose/DWPose was untested (download stalled) and is reported to do better on art because of HumanArt training.
   - The anime-specific bizarre-pose-estimator is AGPL, so avoid it.
   - Conclusion: use keypoints to *propose* joints, then have a human confirm them on an overlay.
4. **Blender.**
   - Fully scriptable headless. The image can be a texture on a subdivided plane with an armature and automatic weights, or Grease Pencil v3 (4.3+).
   - It is GPL as a tool, and outputs are the owner's.
   - It is not installed (Homebrew cask 5.3.0 is available per project notes), and render time is unmeasured.
   - It adds nothing for texture fidelity that remap does not already give, and it adds a second renderer and about 1 GB.
   - COA Tools 2 exists (GPL-3.0) but is a GUI cut-out workflow.
5. **2D skeletal tools.**
   - Spine, Moho and Live2D: exclude. Live2D Editor PRO is paid. The SDK is exempt under ¥10M revenue but the workflow is manual.
   - Rive: exports are paid. Lottie: vector only. DragonBones: editor stale.
   - Synfig and OpenToonz: free but manual GUI rigging.
   - None beats an in-house rig for automation.
6. **AI image-to-animation.** All diffusion I2V re-encodes through a VAE. Expect chalk grain to be smoothed, flickering at chunk boundaries and drifting in style. The AK01 lab already showed the style shifting toward an anime look.
   - LivePortrait needs its InsightFace detector replaced before commercial use.
   - ToonCrafter is 512x320 and research-only in spirit.
   - Keep LTX-2.3 for optional hero shots under the existing licence acceptance (free < US$10M revenue).
7. **Inpainting.**
   - Telea and NS take 13–18 ms for an arm-sized region. They are fine for strips under about 10 px wide while moving.
   - MI-GAN (MIT, mobile-sized, MLX/ONNX/CoreML ports) and big-lama (Apache-2.0) suit larger reveals at 512 px tiles. Expected CPU/MPS times are about 0.1–0.5 s per tile (Unverified). Run them once per pose to build a plate, not per frame.
8. **Secondary motion (numpy).**
   - **Kathputli body:** each joint angle θ follows a damped spring, θ'' = −k(θ − θ_target) − cθ', with low damping (ζ ≈ 0.3–0.5) for the floppy string-puppet overshoot. The body root gets a slow vertical bob (2–4 px at about 0.6 Hz) with a slight sway, and hands lead while elbows lag. Feet barely lift for "steps". Optional faint chalk strings from the frame top to the head and hands are a style choice for the owner.
   - **Flags and sashes:** a Verlet chain of 6–12 points pinned at the pole, with gravity, wind = low-frequency noise, and distance constraints in 3–5 iterations. Convert it to a 1-D LBS of the cloth strip.
   - **Trees, leaves, flames and water:** displacement = mask × amplitude × looping noise. The loop comes from cos/sin blending of two noise fields, as tested (12 ms per frame). For trees, weight the amplitude by height above the trunk base and by depth (far = less). For flames, use upward-biased noise.
   - **Falling flowers, birds and clouds:** sprites cut from a chalk image (or generated once in chalk style) moving along spline or boids paths. Clouds can be a horizontal scroll of a masked sky layer.
   - All of this is deterministic given a seed.

## 6. Ranked toolchain recommendation

1. **Puppet layer in `chalk.py` (new module, e.g. `puppet.py`)**:
   - Rig JSON per scene: parts (polygon or SAM mask), parent, pivot, z-order, kind = `lbs|arap|rigid|chain|noise|sprite`, and keyframes in degrees or px synced to narration words.
   - Mesh with scipy Delaunay, deform with libigl `arap_solve` / `bbw` + LBS, and resample with `cv2.remap` INTER_CUBIC.
   - Composite each part's warped colour and alpha over a background plate.
   - Licences: MPL-2.0 / BSD / Apache-2.0 only. Cost about 0.05–0.1 s per frame.
2. **Background plates.**
   - Preferred: at image-generation time, also generate a "same scene, no characters" plate with the same seed and prompt minus subjects, then align it. Unverified whether Z-Image Turbo stays consistent enough; needs a test.
   - Otherwise build the plate per scene with MI-GAN (MIT) or LaMa (Apache-2.0) under the part masks.
   - Telea or NS only for thin per-frame slivers.
3. **Rig authoring helper** (heavy steps, sequential, under `heavy.lock`):
   - SAM 2.1 small (Apache-2.0) for part masks from clicks or boxes.
   - RTMPose via rtmlib (Apache-2.0, test pending) or MediaPipe to propose joints.
   - Write a contact-sheet overlay for human confirmation.
4. **Environment motion presets** (no models): flame, water, leaves, flag, petals, birds and clouds as reusable functions driven by the existing mask and depth.
5. **Optional AI hero shot**: LTX-2.3 (licence already accepted), only where puppet motion cannot sell the beat; flag it at G2.
6. **Fallback**: Blender headless with image-plane + armature, if a shot needs perspective turns that 2D cannot fake.

## 7. Risks

- **The limit of 2D puppetry.** A head "turn" can only rotate or shear a few degrees. A real 3/4 turn needs a second drawing (another chalk generation in the new pose) and a cross-dissolve or swap. That is consistent with the Kathputli aesthetic (wooden puppets have fixed faces) and is a strength if embraced.
- **Hidden geometry.** Raising an arm reveals torso pixels that were never drawn. Keep motions small (under about 40 px at 1080 wide), prefer motions away from the body, or generate an "arm-down/arm-up" pair.
- **Part masks for overlapping figures** (the sage and the boy in front) need manual or SAM work. BiRefNet merges them.
- **Stretch.** ARAP keeps local rigidity, but LBS candy-wrapper artifacts appear at more than 60° joint bends. Puppet motion stays below that.
- **Rig authoring time per scene** is the main cost. 10–14 scenes per episode, 1–3 moving parts each, means roughly 15–30 minutes of human confirmation per episode until a character-level rig library (reused across scenes with the same pose) builds up.
- **The `.task` licence of MediaPipe Pose** and the dataset terms behind DWPose/RTMPose are unconfirmed. They are only needed at authoring time, and outputs (joint guesses) are not distributed, so the risk is low.
- **libigl wheels** cover CPython ≤3.12 abi3. The project `.venv` is 3.12.16, so this is OK, but adding it to `.venv` is an owner decision.

## 8. Needs human input

1. Approve the Kathputli look: how much bob and sway; whether faint chalk strings should be visible; motion per scene (one or two gestures per scene is suggested).
2. Approve adding `libigl` (MPL-2.0) to `.venv`, and optionally `sam2` and `rtmlib` for authoring.
3. Choose the plate strategy: a "no characters" plate generated alongside each scene, or inpainting.
4. Review a 1-scene prototype before any pipeline integration. The test MP4 in the scratchpad (`.../scratchpad/puppet/test.mp4`) is a rough whole-image warp, not the layered version.
5. Read the full libigl MPL-2.0 obligations, the MI-GAN LICENSE file, and the MediaPipe pose model card before shipping (all Reported, not read end to end).

## 9. Sources (accessed 2026-11-17)

- AnimatedDrawings repo and README (archived 2025-09-03): https://github.com/facebookresearch/AnimatedDrawings ; `arap.py`: https://raw.githubusercontent.com/facebookresearch/AnimatedDrawings/main/animated_drawings/model/arap.py ; README mirror: https://cdn.jsdelivr.net/gh/facebookresearch/animateddrawings@main/README.md ; TorchServe Apple Silicon note: https://pytorch.org/serve/hardware_support/apple_silicon_support.html
- libigl on PyPI (2.6.3, 2026-09-01): https://pypi.org/project/libigl/
- Triangle licence: https://www.cs.cmu.edu/~quake/triangle.html
- SAM 2: https://github.com/facebookresearch/sam2 , https://ai.meta.com/blog/segment-anything-2/ ; SAM 3 licence summary: https://roboflow.com/model-licenses/segment-anything-3 , https://github.com/facebookresearch/sam3
- rtmlib: https://github.com/Tau-J/rtmlib ; DWPose ONNX mirror: https://huggingface.co/SceneWorks/dwpose-onnx ; FASHN DWPose: https://hf-proxy-en5.pages.dev/fashn-ai/DWPose
- MediaPipe Pose Landmarker: https://ai.google.dev/mediapipe/solutions/vision/pose_landmarker ; licence question: https://discuss.ai.google.dev/t/commercial-use-of-mediapipe-pose-landmarker-full/184033 ; OpenCV zoo copy: https://huggingface.co/opencv/pose_estimation_mediapipe
- bizarre-pose-estimator paper: https://arxiv.org/pdf/2108.01819 ; weights licence note: https://huggingface.co/mrpm/ComfyUI-AnimePose-weights
- DrawingSpinUp: https://github.com/LordLiang/DrawingSpinUp , https://arxiv.org/abs/2409.08615
- LivePortrait: https://huggingface.co/KwaiVGI/LivePortrait ; https://github.com/kijai/ComfyUI-LivePortraitKJ ; InsightFace licensing: https://www.insightface.ai/services/models-commercial-licensing
- ToonCrafter: https://huggingface.co/Doubiiu/ToonCrafter , https://github.com/ToonCrafter/ToonCrafter
- LaMa: https://huggingface.co/opencv/inpainting_lama ; MI-GAN: https://github.com/Picsart-AI-Research/MI-GAN , https://huggingface.co/mlx-community/MI-GAN-512-places2-fp16
- Synfig skeleton deformation: https://synfig.readthedocs.io/en/latest/layers/skeleton_deformation.html ; OpenToonz CLI: https://morevnaproject.org/2016/11/27/use-opentoonz-cli
- COA Tools 2: https://github.com/Aodaruma/coa_tools2 ; https://blenderartists.org/t/coa-tools-dead/1479623/
- DragonBonesJS (MIT): https://awesome.ecosyste.ms/projects/github.com%2FDragonBones%2FDragonBonesJS
- Live2D SDK licence: https://www.live2d.com/en/sdk/license/
- Rive runtimes (MIT): https://rive.app/runtimes ; exports moved to paid plans: https://rive.app/blog/rive-s-new-9-mo-plan
- Diffusion texture and flicker issues: https://arxiv.org/pdf/2510.01686 (FreeViS), https://arxiv.org/pdf/2306.07954 (Rerender A Video), https://ltx.io/blog/temporal-consistency-in-ai-video
- Prior project research: `research_notes/Studio upgrade research/visual_tools.md`, `research_notes/Shorts studio voices and tools/visual_animation_tools.md`, `research_notes/Continuity editing/tools.md`
