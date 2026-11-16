# Audio stack and Claude Code ecosystem: studio upgrade research

Research date: 2026-11-16. Target: MacBook Air M5, 16 GB, zero cost, monetized YouTube Shorts and Instagram Reels in en/hi/gu/te.

This note does not repeat findings that are already in `reports/Shorts studio voices and tools.md` or in `research_notes/Shorts studio voices and tools/audio_automation_skills.md`. It only re-confirms them where a primary source was checked again, and says when it does. Repo metadata (license SPDX, last push, stars) comes from the GitHub API, and weight licenses come from the Hugging Face model API (`cardData.license`). Both were pulled on the research date.

## What the pipeline does today (so the recommendations are concrete)

- `studio.py step_audio`: the music bed is either a file passed with `--music` (tiled, ×0.5) or generated in numpy (raga/tanpura via `chalk.music`, chiptune, or pad). Ducking is a numpy envelope follower (`duck = 1 - 0.65·clip(env/0.05)`), with fades and procedural whoosh/blip SFX.
- Final encode: **single-pass** `loudnorm=I=-14:TP=-1.5:LRA=11` on the finished mix (`studio.py:705`).
- QA (`pipeline/qa.py`) gates integrated loudness at −16.5 to −13 LUFS and true peak at ≤ −1.0 dBFS.
- Local ffmpeg is **9.0.1** and includes `loudnorm`, `sidechaincompress`, `acompressor`, `deesser`, `adynamicequalizer`, `arnndn`, `afftdn`, `anlmdn`, `speechnorm`, `dialoguenhance`, `alimiter` and `ebur128` (checked with `ffmpeg -filters`).

---

# PART A: Audio

## A1. Music generation models (local, commercial use)

| Model | Code / weights license (verified) | Outputs | Fit on a 16 GB Air | Verdict |
|---|---|---|---|---|
| **ACE-Step 1.5** (2B turbo DiT + 0.6B LM) | MIT / MIT (HF `ace-step/Ace-Step1.5`: `mit`); repo pushed 2026-11-08, 14.8k★ | Card says outputs can be used commercially | README table puts 8–16 GB on the 2B turbo/sft DiT with the 0.6B LM (8–12 GB) or 1.7B LM (12–16 GB); macOS scripts use the **MLX** backend. XL (4B DiT, about 9 GB bf16 weights) needs ≥12 GB with offload, so skip it. | **Best full-song or bed option.** Already recommended; this research re-confirms it. No Mac timings are published. |
| **Magenta RealTime 2** (Google, released 2026-06-04) | Code Apache-2.0 (`magenta/magenta-realtime`, pushed 2026-10-02); weights **CC-BY-4.0** (HF `google/magenta-realtime-2`) | Card: "Google claims no rights in outputs you generate." Training data is about 71k h of stock music, mostly instrumental | `mrt2_small` (230M) runs **real-time on any Apple Silicon Mac including Air models**. `mrt2_base` (2.4B) runs offline on any Apple Silicon. `uv pip install "magenta-rt[mlx]"` → `mrt mlx generate --prompt … --duration …` | **New and worth testing.** It is instrumental-first, small and MLX-native, which makes it a good fit for short beds. CC-BY applies to the weights, not to the audio, so no on-video credit appears to be required. A courtesy credit in the description is cheap. Indian timbre quality is unknown. |
| **Stable Audio 3** Small Music / Small SFX (0.6B) / Medium (1.4B) (released 2026-05-20, HF weights 2026-10-06) | Stability AI Community License (HF `license_name: stable-audio-community`), gated. Also includes **Gemma Terms of Use** components | Users own outputs. Free under **US$1M annual revenue**; revocable license | The card says "a few seconds on a MacBook Pro M4". Small models are reported to run on CPU. Training data: about 806k AudioSparx-licensed tracks plus about 473k Freesound CC0/CC-BY/Sampling+ tracks | **Maybe.** Clean training provenance and instrumental-only output, but a revenue cap and a revocable license. Weaker than MIT ACE-Step on licensing. Small-SFX is the more interesting part (see A3). |
| Stable Audio Open 1.0 / Open Small | Community license (HF `other` / `stability-ai-community`), gated | Same <$1M cap | Small runs on-device | Superseded by SA3 Small. Skip. |
| **HeartMuLa-oss-3B** (paper Jan 2026) | Apache-2.0 for the repo and "all related model weights" (heartlib README; HF `apache-2.0`, updated 2026-11-15) | Not stated separately | 4B params in F32 safetensors; reported RTF ≈ 1.0 on GPU; **no Mac/MPS path documented** | **Skip for now.** It is a lyrics-to-song model, it is heavy, and it has no Apple path. |
| **DiffRhythm** v1.2 | Apache-2.0 for code and DiT weights (repo pushed 2025-11-27) | Not stated | Needs ≥8 GB VRAM with `--chunked`. "Can now run on MacOS" (2025-03), but MPS is not mentioned. It has an instrumental mode | **Skip.** It is stale and a song model, and an earlier pass flagged a possible Stable-Audio-licensed VAE component. |
| **YuE** | Repo Apache-2.0; YuE v1 weights `apache-2.0` (e.g. `m-a-p/YuE-s1-7B-anneal-en-cot`) | n/a | 7B-class, song-with-vocals, CUDA-oriented | **Skip.** Too heavy, and vocals are not needed. (YuE2 weights are NC, per the earlier pass.) |
| **MusicGen / AudioGen** | Code MIT (`facebookresearch/audiocraft`); **weights CC-BY-NC-4.0** confirmed on `facebook/musicgen-small`, `musicgen-medium` and `audiogen-medium` | Non-commercial | — | **Excluded** (confirmed). |
| MiniMax-Music3 (open weights) | Community license: commercial use requires showing "MiniMax-Music3" prominently in the product UI, plus a revenue threshold (secondary source only) | — | Not checked | Skip (attribution-in-UI clause, unverified). |
| Tencent SongGeneration (LeVo) | Official HF/GitHub pages were reported unavailable in Oct 2026; re-uploads carry "unknown" licenses (secondary) | — | — | **Avoid.** |

**Practical note on Indian timbres.** No model above documents raga, tanpura, sitar or bansuri quality. The earlier conclusion still holds: keep the numpy tanpura as the drone underlay and audition generated beds by ear. Use prompts like "slow devotional instrumental, bansuri and soft tanpura drone, no percussion, no vocals". Generate 30–40 s and loop or crossfade, since Shorts are 60–90 s.

## A2. Royalty-free music and SFX libraries

| Source | Terms (verified where marked) | Content ID risk | Verdict |
|---|---|---|---|
| **YouTube Audio Library** (Studio only) | Official help page (support.google.com/youtube/answer/3376882): music and SFX are "copyright-safe" and "won't be claimed by a rights holder"; YPP videos can monetize. CC tracks require credit in the description, and an **"Attribution not required" filter** exists. Google gives **no guidance for use off YouTube**. Third-party guides say the *standard* license is restricted to YouTube | Lowest of any source | **Use for the YouTube versions only.** Do **not** reuse standard-license tracks in Instagram Reels; that is a risk flagged by secondary sources and not settled by Google. |
| **Pixabay Music / SFX** | Pixabay Content License (license summary page, verified): free, no attribution required, no standalone redistribution. Neither the summary nor the ToS mentions Content ID. ToS §7B: AI-generated uploads must be labelled as such | **Real.** Pixabay has no Content ID integration (per a competitor's page), and contributors or distributors can register tracks with Content ID at any time. Pixabay says to dispute claims with the license certificate | **Maybe, SFX only.** Avoid Pixabay *music* for monetized Shorts. |
| **Freesound** | FAQ (verified): each sound is CC0, CC-BY, CC-BY-NC, or legacy Sampling+. The "Free Cultural Works" license filter returns only CC0 and CC-BY. CC-BY-NC forbids earning money from the work, and Sampling+ forbids ads | Low for CC0 field recordings | **Worth using with the CC0 filter (`f=license:"Creative Commons 0"`).** A free API token also allows scripted search. |
| **Sonniss GDC bundles** (2026 bundle: 347+ files, 7.47 GB) | sonniss.com/gameaudiogdc FAQ (verified): royalty-free and commercially usable, "No attribution is required", "YouTube videos you monetize" are explicitly allowed, no resale or redistribution as SFX (including edited versions), **AI/ML training prohibited** | None known | **Worth downloading** (one-time, offline library). Keep the files out of git, per the media rule. |
| **BBC Sound Effects** (RemArc) | Only secondary sources were reachable (the BBC site refused automated fetch): personal, educational and research use only, credit required, commercial use needs a paid license (sold via Pro Sound Effects) | n/a | **Skip.** It is non-commercial, and a monetized channel is commercial. |
| **Incompetech / Kevin MacLeod** | Free tier is CC-BY (credit required); the paid Standard License removes attribution (price not shown on the page) | Some MacLeod tracks have historically drawn third-party claims [unverified] | **Skip.** Credit lines are needed per video, and the tracks are heavily overused. |
| **Free Music Archive** | Per-track CC licenses, many of them NC/ND; filter behaviour is reported inconsistently (secondary) | Varies | **Skip** unless a specific track is CC0/CC-BY and checked by hand. |
| **OpenGameArt** | Per-item CC0 / CC-BY / GPL; many all-CC0 audio collections exist (e.g. "CC0 audio uploader" pages) | Low | **Maybe**, for CC0 game-style SFX. |

**Indian instruments.** No verified free CC0 Indian instrument pack was found. Free promo packs (Black Octopus, Noiiz, SampleScience, Crypto Cipher, Looperman loops) carry vendor or per-upload terms that would each need reading. The ragajunglism.org tanpura set (12 keys, Sa-Pa and Sa-ma) states **no license and admits unknown origin**, so avoid it. Freesound, counted on the research date via its search page, is the practical source:

| Query | All licenses | CC0 only |
|---|---|---|
| tanpura | 239 | 179 |
| tabla | 399 | 150 |
| temple bell | 240 | 91 |
| harmonium | 99 | 59 |
| sitar | 132 | 36 |
| bansuri | 45 | 21 |
| conch | 30 | 14 |
| veena | 11 | 9 |
| shehnai | 4 | 0 |

These counts include unrelated hits, so audition each file. Shehnai has effectively no CC0 supply, so generate it or drop it. Conch and temple bells are the most useful mythology accents and have CC0 options. Generated or recorded-by-owner audio is always the cleanest.

## A3. SFX and video-to-audio generation

| Model | Weights license (verified on HF API / README) | Verdict |
|---|---|---|
| **Stable Audio 3 Small SFX** (0.6B) | Stability Community, <$1M, gated | **Maybe.** It is the only commercially usable modern SFX generator found. Use it for whooshes, bells and ambience, and run it alone. |
| Stable Audio Open (1.0 / Small) | Stability Community | Superseded by SA3. |
| **AudioLDM2** (`cvssp/audioldm2`, `audioldm2-music`) | **CC-BY-NC-SA-4.0** | **Excluded.** |
| **Tango 2** (`declare-lab/tango2`) | **CC-BY-NC-SA-4.0** | **Excluded.** |
| **TangoFlux** | README: "checkpoints are for non-commercial research use only" | **Excluded.** |
| **MMAudio** (`hkchengrex/MMAudio`) | Code MIT, **weights CC-BY-NC-4.0** (now confirmed on HF; previously secondary only) | **Excluded.** |
| **HunyuanVideo-Foley** | Tencent Hunyuan Community License (territory exclusions) | **Excluded** (earlier finding stands). |

Conclusion: keep the procedural chalk SFX (`CHALK_SFX_GAIN = 0.035`, approved). Add accents from CC0 Freesound or Sonniss files rather than from a generator, unless SA3's revenue cap is acceptable to the owner.

## A4. Audio post-production

**Loudness targets.** **Neither YouTube nor Meta publishes an official Shorts/Reels loudness spec.** The −14 LUFS integrated / −1 dBTP figure is a widely repeated convention from vendor and tool blogs (OpusClip, OpenClip, DEV), and YouTube only turns loud uploads down, not quiet ones up. The current −14 / −1.5 dBTP target and the QA band of −16.5 to −13 are sensible. You can check the result on a published video with "Stats for nerds" → content loudness.

**Recommended changes (all free, already in ffmpeg 9.0.1):**
1. **Two-pass loudnorm with `linear=true`.** Pass 1 is `loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json`. Pass 2 feeds `measured_I/measured_TP/measured_LRA/measured_thresh/offset` back with `linear=true`. Single-pass mode is dynamic, so it can pump the bed under narration. Linear mode applies one gain, and falls back to dynamic only if the true-peak limit would be exceeded. **pyloudnorm** (MIT, pushed 2026-01) is a pure-Python BS.1770 meter that can do the measurement step and QA in numpy.
2. **Normalize the narration stem before mixing** (for example to −16 LUFS), then set the music gain relative to it. Music-gain choices then stay consistent across languages and voices (Kokoro, Maya2).
3. **Ducking.** The numpy envelope ducker works, and replacing it is not required. If a standard filter is preferred, use `[music][voice]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[ducked]` and then `amix`. Its main advantage is fewer hand-tuned constants.
4. **Voice polish chain (optional, test by ear):** `highpass=f=70`, a gentle `deesser` (or `adynamicequalizer` around 6–8 kHz), and `acompressor=threshold=-20dB:ratio=3:attack=5:release=80`. TTS output is already clean and compressed, so over-processing is the main risk.
5. **Spotify pedalboard** is **GPL-3.0** (verified README, pushed 2026-11-09). It bundles JUCE (GPLv3/commercial), Rubber Band (GPLv2+) and FFTW. Processed audio is not affected by the GPL. The repo is published on GitHub, though, so importing pedalboard means distributing code that links a GPL library. That is fine for a personal pipeline but should be a conscious choice. ffmpeg covers everything needed here, so pedalboard is optional.

**Noise reduction and enhancement.** TTS has no background noise, so these tools only matter for owner-recorded audio.
- **DeepFilterNet**: code **and weights dual MIT/Apache-2.0** (README, verified); repo pushed 2026-11-06. It is the best free denoiser if one is ever needed.
- **RNNoise**: BSD-3 (pushed 2025-02). ffmpeg `arnndn` needs a model file, and the common GregorR/rnnoise-models repo has **no license file** (last push 2018), so use the xiph default model rather than those.
- **noisereduce**: MIT (pushed 2025-08); spectral gating, CPU-light.
- **Resemble Enhance**: MIT for code and weights (`ResembleAI/resemble-enhance`: `mit`), but the repo has been stale since 2024-12. Its bandwidth extension could lift 24 kHz TTS to 44.1 kHz. **Maybe:** A/B it on one Kokoro/Maya2 scene, and listen for artifacts on Indic consonants.
- **ClearerVoice-Studio** (Alibaba/ModelScope): Apache-2.0 (pushed 2025-08); an alternative speech enhancer/separator. Not tested.

**Stem separation.** **Demucs** code is MIT (`facebookresearch/demucs` is **archived**; the active fork is `adefossez/demucs`, pushed 2026-10-26). Its README says the **weights' license "is not clear"**: MusDB is research-only, and htdemucs_6s was trained on Meta internal data where "CC-NC-BY … likely" applies. **Do not use Demucs outputs in published audio.** The pipeline does not need stem separation anyway.

## A5. Voice: newer free commercial TTS (brief, new items only)

- The existing report's line "Maya 2 Native needs CUDA" is **superseded in practice**: the project now runs Maya 2 Native (Malini) through mlx-audio on the M5 (PROJECT_CONTEXT §6).
- **Kitten TTS 2** (Mini 82M / Nano / Pico, released 2026-11-13): Apache-2.0, 16 languages **including Hindi**, int8 ONNX at 82.7 MB, CPU-only. No Gujarati or Telugu. Quality is unknown, but it could be a tiny fallback for English or Hindi only.
- **MOSS-TTS v1.5** (OpenMOSS): Apache-2.0, 31 languages including Hindi; no gu/te.
- Neither model covers gu/te, so **neither changes the voice plan.** Maya2 Malini stays.

## PART A shortlist

**Worth installing / doing**
1. **Two-pass linear loudnorm + pre-mix narration normalization** (ffmpeg, already installed). This is the cheapest quality gain: a consistent bed level and no pumping.
2. **Sonniss GDC 2026 bundle + Freesound CC0** as the SFX/accent library (conch, temple bells, tanpura, tabla). It is free, needs no attribution and is safe for monetized YouTube. Keep a `licenses.csv` (file, source URL, license) alongside the files, outside git.
3. **ACE-Step 1.5 (2B turbo + 0.6B LM, MLX)**: MIT and commercial. It is the best generated bed; run it alone under the progress protocol.
4. **Magenta RealTime 2 small (230M, MLX)**: Apache code, CC-BY weights, Google claims no output rights, runs real-time on an Air. It is the lightest generated-bed option; A/B it against ACE-Step.

**Maybe**
- **YouTube Audio Library** ("Attribution not required" filter) for YouTube uploads only, not Instagram.
- **Stable Audio 3 Small SFX/Music**: clean data, but a <$1M cap, a revocable license and gated access.
- **Resemble Enhance** for 24→44.1 kHz bandwidth extension (an A/B test only).
- **pyloudnorm** for numpy-side loudness QA.
- **sidechaincompress** in place of the numpy ducker (only if simplification is wanted).
- **DeepFilterNet**, only if owner-recorded voice is ever used.

**Skip**
- MusicGen/AudioGen, AudioLDM2, Tango/TangoFlux, MMAudio, HunyuanVideo-Foley: all non-commercial (verified).
- Demucs in published audio (weights license unclear).
- BBC Sound Effects (non-commercial).
- Pixabay *music* (Content ID exposure).
- Incompetech/FMA (attribution and overuse).
- HeartMuLa, DiffRhythm, YuE, SongGeneration (heavy, no Mac path, or unclear status).
- Spotify pedalboard: ffmpeg already does the job, and pedalboard brings GPL into a public repo.

---

# PART B: Claude Code skills, agents, MCP

## B1. Official Anthropic sources

- **`anthropics/skills`** (pushed 2026-11-14, about 196k★, no root SPDX; licenses are per skill). It now has **19 skills**: academy-guide, algorithmic-art, brand-guidelines, canvas-design, claude-api, discernment-nudge, doc-coauthoring, docx, frontend-design, internal-comms, mcp-builder, pdf, pptx, skill-creator, slack-gif-creator, theme-factory, web-artifacts-builder, webapp-testing, xlsx. **None covers video, audio, YouTube or analytics**, which matches the 2026-11-15 review in PROJECT_CONTEXT §5. `skill-creator` is already available through `anthropic-skills`.
- **`anthropics/claude-plugins-official`** (Apache-2.0, pushed 2026-11-16) lists **317 plugins** in `.claude-plugin/marketplace.json`. Filtering names, descriptions and keywords for video/audio/YouTube/media gave the following:
  - **hyperframes** (HeyGen): see B2.
  - **runway-api**: paid Runway API, so skip.
  - **save-to-spotify**: TTS episodes to Spotify; off-scope.
  - **togetherai-skills**: a paid API platform, so skip.
  - **adobe-for-creativity**: Adobe cloud tools, so skip.
  - **cloudinary**: a SaaS media CDN, so skip.
  - **postiz**: a social scheduling CLI. Postiz itself is AGPL and heavy (earlier finding), and it would bypass G3, so skip.
  - There is **no YouTube, ffmpeg or Remotion plugin** in the official marketplace.
- **Claude Code docs, facts relevant here** (code.claude.com/docs, fetched 2026-11-16):
  - Skills: project skills live in `.claude/skills/<name>/SKILL.md`. Only the description stays in context, and it is truncated at 1,536 characters together with `when_to_use`. The full body loads on invocation. Keep SKILL.md under 500 lines.
  - Skill frontmatter supports `disable-model-invocation` (for side-effecting workflows such as publishing), `allowed-tools`, `disallowed-tools`, `context: fork` + `agent`, `paths`, `hooks` and `model`.
  - Skills can embed `` !`command` `` dynamic context; a failed command aborts the invocation. That is useful for injecting `python -m pipeline status`.
  - Hooks: `PreToolUse` can block with exit code 2 or a JSON `permissionDecision: "deny"`. Matchers are exact names or a regex, and the `if` field uses permission syntax (`Bash(python -m pipeline publish*)`).
  - **Timeouts fail open** by default. Set `"onFailure": "block"` (v2.1.295+) for gate enforcement.
  - Hooks can also live in skill or subagent frontmatter, and project hooks follow workspace trust.
  - Plugins: bundle skills, agents, hooks, a hooks module and MCP servers. An enabled plugin puts every model-invocable skill/agent description into context **on every turn**, and its MCP servers run in every session. Install scopes are user, project and local. Official marketplace names are only accepted from `github.com/anthropics/`.

## B2. Community skills and plugins (inspected)

| Repo | What it actually does (from SKILL.md / README) | License, maintenance | Paid or external dependencies | Fit |
|---|---|---|---|---|
| **heygen-com/hyperframes** (in the official marketplace) | HTML/CSS/GSAP compositions rendered to deterministic MP4 via Puppeteer (headless Chrome) + FFmpeg. 9 skills, about 450 catalog blocks (captions, kinetic type, transitions) | Apache-2.0; pushed 2026-11-16; 85k★ | The `media-use` SKILL.md sends a **usage beacon** (`npx hyperframes events`, account-linked when signed in) and tells the agent to push **HeyGen sign-in**. It says "Use local tools only when the person asks, not as a fallback". Its "local" music option is **MusicGen (CC-BY-NC)**. Paid Pro plan for HeyGen models. Needs Node ≥22 | **Skip as a plugin.** The render engine is a legitimate Apache alternative to Remotion with no company-size clause, but the skills steer toward paid services and an NC music model. Revisit the engine only if overlays move to HTML. |
| **remotion-dev/skills** | Remotion best-practice skills | Repo has no SPDX; Remotion itself is under the Remotion License (free for individuals and companies up to 3 employees, commercial use allowed). Pushed 2026-11-16 | Node/React toolchain | **Skip.** The chalk engine is Python. Same conclusion as before. |
| **iart-ai/motion-skills** (19 packs, 56 skills, incl. `tiktok-video-skills`, `manim-skills`) | Motion-graphics recipes with a render→screenshot→verify loop; video skills render via **Remotion or Manim** | MIT; pushed 2026-11-13; 1.6k★ | The README advertises iArt's **paid** remote MCP (Pro plan + API key); the skills themselves are local | **Skip/maybe.** The only transferable idea is the "render a frame → contact sheet → inspect" verify loop, which video-qa can copy without installing anything. |
| **affaan-m/ECC `video-editing`** | Editing *real footage*: FFmpeg cuts, Remotion, **ElevenLabs, fal.ai**, Descript/CapCut | MIT; pushed 2026-11-16 (304k★ collection) | Paid APIs | **Skip.** Wrong problem (footage compression, not generation). |
| **AgriciDaniel/claude-video** | 15 sub-skills: transcoding (NVENC), Whisper captions, Remotion promos from Pixabay stock | MIT; **stale** (2026-04-06); 34★ | `GOOGLE_AI_API_KEY` for TTS, Pixabay key, NVIDIA GPU optional | **Skip.** |
| **renezander030/capcut-cli** | Node CLI/skill that edits CapCut/JianYing project files | MIT; pushed 2026-11-15; 1.2k★ | CapCut app (its own ToS) | **Skip.** The pipeline does not use CapCut. |
| **Alisa0808/vox-director** | Topic → paper-collage explainer with two human gates | MIT; pushed 2026-10-05 | **Atlas Cloud API** (paid) + ffmpeg | **Skip.** It is a paid-API wrapper, though its two-gate design mirrors G1/G2. |
| **ComposioHQ/awesome-claude-skills** "YouTube/Instagram/TikTok Automation" | README links point to `./youtube-automation/` etc., but **those directories do not exist in the repo tree** (checked via the git tree API). They are Composio-platform integrations | No SPDX; pushed 2026-09-18 | Composio account | **Skip.** The links are dead, it depends on a third-party platform, and posting would bypass G3. |
| **travisvn/awesome-claude-skills** | A curated list; no video, audio or YouTube entries apart from a social-image asset generator | No SPDX; pushed 2026-04-28 | — | Nothing to install. |
| **hesreallyhim/awesome-claude-code** | A curated list (pushed 2026-11-16). The media entries found are capcut-cli, motion-skills, vox-director, the NotebookLM MCP and atelier (HTML-to-video recording) | — | — | Nothing that beats the in-house pipeline. |
| Skill registries (skills.sh, smithery, claude-plugins.dev, skillselion, claudeskills.info) | Aggregators listing ffmpeg-video-editor variants (openclaw, sundial-org, aaaaqwq): mostly natural language to ffmpeg command recipes | Mixed | — | **Skip.** Claude already writes ffmpeg; these add context cost and supply-chain risk. |

**Already installed and still the best fit:** the 8 vendored `yt-*` skills (MIT, pinned at a2feb21) plus the project's own `storytelling` and `content-pipeline` skills and 10 agents. Nothing found replaces them.

## B3. MCP servers

| Server | What it does | Free/local? | Verdict |
|---|---|---|---|
| **ffmpeg MCPs** (`video-creator/ffmpeg-mcp` MIT 154★ pushed 2026-05; `kevinwatt/ffmpeg-mcp-lite` MIT 28★; `egoist/ffmpeg-mcp` no license, stale 2025-03) | Wraps ffmpeg CLI operations as MCP tools | Free, local | **Skip.** Claude Code already runs ffmpeg through Bash, and the pipeline calls it from Python. An MCP layer adds a process and context cost for no capability. |
| **ComfyUI MCP** (`artokun/comfyui-mcp` MIT 929★ pushed 2026-11-16; `joenorton/comfyui-mcp-server` Apache-2.0 412★; `ATH-MaaS/Pixelle-MCP` MIT 1.1k★) | Drives a local ComfyUI: workflows, model downloads, image/video/audio generation. artokun's version also ships 42 skills, 4 agents and **3 hooks** | Free and local with ComfyUI installed (Comfy Cloud/RunPod optional) | **Skip.** The studio uses mflux (MLX) directly. ComfyUI on MPS would be a second heavy runtime, which conflicts with the one-heavy-model rule, and artokun's bundled hooks need review. |
| **YouTube Analytics MCP**: `conorbronsdon/yt-analytics-mcp` | 9 tools, **all read-only**, owner-side Analytics API v2 (traffic sources incl. Shorts feed, retention curve, `yt_episode_race` age-normalized comparison) | MIT; pushed 2026-11-10; only 3★ (very new); Node 20 | **Maybe.** It is the cleanest design found (read-only, so it cannot bypass G3), but the pipeline already calls the Analytics API directly (`performance-analyst`). Borrow the "episode race at equal age" idea rather than installing it. |
| `pauling-ai/youtube-mcp-server` | 40 tools incl. Analytics, Reporting API, **upload, comments, thumbnails** | MIT; pushed 2026-10-23; 32★ | **Skip.** Write tools could publish outside G3. |
| `ZubeidHendricks/youtube-mcp-server` | 10 tools: search videos/channels, find creators | MIT; pushed 2026-08; 599★ | Skip. It duplicates `yt-viral` + `pipeline/research.py`. |
| `kirbah/mcp-youtube` | Transcripts (no key) + Data API search | MIT; pushed 2026-11-13 | Skip. |
| **Blender MCP**: `ahujasid/blender-mcp` (GitHub now reports it as `ahujasid/mcp-for-blender`) | Claude controls Blender via an add-on socket | MIT; pushed 2026-11-15; 34.6k★ | **Skip.** It does not fit the 2D chalk style. **Warning:** a GitHub search for "blender mcp" returns several look-alike repos with random-looking owner names, about 500★ each, all pushed the same day (e.g. `credoksopho1984/…`, `racdeufindurch198812/…`, `fumbdendade19718/…`). That pattern matches star-farmed malware lures. Do not install any of them. |
| `Audio-Launch/audiolab-mcp-server` | EBU R128 / true-peak / voice-quality analysis | MIT; 0★; pushed 2026-11-13 | Skip. ffmpeg `ebur128` and `pipeline/qa.py` already do this. |
| Claude.ai connectors visible in this session (xelta, MCP-H/Higgsfield, OpenSEO, Ubersuggest) | Hosted generation and SEO tools | **Credit-based or paid** | **Do not use.** They violate the zero-cost rule. |

## B4. Project-native additions (better value than installs)

1. A **`PreToolUse` hook with `"onFailure": "block"`** on `Bash(python -m pipeline publish*)` (and on any upload script). It checks the manifest for a recorded G3 approval and exits 2 otherwise. This makes the gate a mechanical control rather than only an instruction.
2. **`disable-model-invocation: true`** on any future skill that publishes or schedules.
3. An **`audio-mix` skill** (project-local, about 100 lines) that documents the two-pass loudnorm recipe, the stem gain table per voice engine, the SFX library index (`licenses.csv`) and the QA thresholds, so agents stop re-deriving them.
4. Keep vendoring third-party skills as single reviewed files pinned to a SHA (the yt-* precedent). Never enable a plugin that ships hooks or MCP servers without reading them first.

## PART B shortlist

**Worth installing / doing**
1. Nothing external needs installing. **Build the G3 `PreToolUse` hook** (fail-closed) and the small **`audio-mix` skill**. Both are project-native and free, and they encode existing rules.

**Maybe**
- `conorbronsdon/yt-analytics-mcp` (read-only, MIT). Install it only if the in-house analytics code becomes a maintenance burden. Otherwise copy its equal-age episode comparison into `performance-analyst`.
- The HyperFrames **engine** (Apache-2.0), not its skills, if overlays or kinetic captions ever move to HTML.
- The motion-skills "render a frame → contact sheet → inspect" verify loop, as a pattern for video-qa.

**Skip**
- The HyperFrames plugin (beacon, HeyGen upsell, MusicGen-NC local default).
- Remotion skills (React toolchain).
- ECC video-editing, claude-video, vox-director and iArt MCP (paid APIs).
- Composio social "skills" (dead links, platform lock-in, G3 bypass).
- ffmpeg MCPs (redundant).
- ComfyUI MCPs (second heavy runtime).
- YouTube MCPs with write tools.
- Blender MCP and its malware look-alikes.
- All credit-based claude.ai connectors.

---

## Sources

**Music and SFX models**
- ACE-Step 1.5: https://github.com/ace-step/ACE-Step-1.5 ; https://huggingface.co/ACE-Step/Ace-Step1.5
- Magenta RealTime 2: https://magenta.tensorflow.org/magenta-realtime-2 ; https://huggingface.co/google/magenta-realtime-2 ; https://github.com/magenta/magenta-realtime
- Stable Audio 3: https://huggingface.co/stabilityai/stable-audio-3-small-music ; https://stability.ai/license ; https://blog.dubspot.com/stable-audio-3-review
- HeartMuLa: https://huggingface.co/HeartMuLa/HeartMuLa-oss-3B ; https://github.com/HeartMuLa/heartlib
- DiffRhythm: https://github.com/ASLP-lab/DiffRhythm
- YuE: https://github.com/multimodal-art-projection/YuE
- MusicGen weights: https://huggingface.co/facebook/musicgen-small
- AudioLDM2: https://huggingface.co/cvssp/audioldm2
- Tango 2 and TangoFlux: https://huggingface.co/declare-lab/tango2 ; https://huggingface.co/declare-lab/TangoFlux
- MMAudio: https://huggingface.co/hkchengrex/MMAudio
- Model roundup (secondary): https://www.creativeainews.com/articles/best-open-source-ai-music-models-2026/
- MiniMax-Music3 (secondary): https://www.orcarouter.ai/blog/minimax-music3-open-weights

**Libraries**
- YouTube Audio Library: https://support.google.com/youtube/answer/3376882
- Pixabay: https://pixabay.com/service/license-summary/ ; https://pixabay.com/service/terms/ ; https://hellothematic.com/thematic-vs-pixabay/
- Freesound: https://freesound.org/help/faq/
- Sonniss GDC bundle: https://sonniss.com/gameaudiogdc
- BBC Sound Effects (secondary): https://www.diyphotography.net/the-bbc-sound-effects-archive-is-now-free-to-download-with-over-33000-files/
- Incompetech: https://incompetech.com/music/royalty-free/licenses/
- Tanpura samples: https://ragajunglism.org/tanpuras
- Indian instrument sample roundup: https://loststoriesacademy.com/blogs-and-tutorials/7-sample-libraries-for-indian-instruments-free-paid-in-2025

**Audio post**
- Loudness (secondary): https://openclip.app/learn/audio-normalization ; https://dev.to/arthurvalle1_a2586dd2b4bc/mastering-for-reels-tiktok-and-youtube-shorts-the-lufs-14-standard-2ck5
- pedalboard: https://github.com/spotify/pedalboard
- DeepFilterNet: https://github.com/Rikorose/DeepFilterNet
- RNNoise: https://github.com/xiph/rnnoise ; https://github.com/GregorR/rnnoise-models
- noisereduce: https://github.com/timsainb/noisereduce
- Resemble Enhance: https://github.com/resemble-ai/resemble-enhance
- Demucs: https://github.com/adefossez/demucs
- pyloudnorm: https://github.com/csteinmetz1/pyloudnorm
- ClearerVoice-Studio: https://github.com/modelscope/ClearerVoice-Studio

**TTS**
- Kitten TTS 2: https://huggingface.co/KittenML/kitten-tts-2-mini
- MOSS-TTS v1.5: https://huggingface.co/OpenMOSS-Team/MOSS-TTS-v1.5

**Claude Code**
- Official sources: https://github.com/anthropics/skills ; https://github.com/anthropics/claude-plugins-official
- Docs: https://code.claude.com/docs/en/skills ; https://code.claude.com/docs/en/hooks ; https://code.claude.com/docs/en/plugins
- HyperFrames: https://github.com/heygen-com/hyperframes (skills/media-use/SKILL.md)
- Remotion: https://github.com/remotion-dev/skills ; https://github.com/remotion-dev/remotion/blob/main/LICENSE.md
- Community skills: https://github.com/iart-ai/motion-skills ; https://github.com/affaan-m/ECC ; https://github.com/AgriciDaniel/claude-video ; https://github.com/renezander030/capcut-cli ; https://github.com/Alisa0808/vox-director
- Curated lists: https://github.com/ComposioHQ/awesome-claude-skills ; https://github.com/travisvn/awesome-claude-skills ; https://github.com/hesreallyhim/awesome-claude-code

**MCP servers**
- ffmpeg: https://github.com/video-creator/ffmpeg-mcp ; https://github.com/kevinwatt/ffmpeg-mcp-lite
- ComfyUI: https://github.com/artokun/comfyui-mcp ; https://github.com/joenorton/comfyui-mcp-server
- YouTube: https://github.com/conorbronsdon/yt-analytics-mcp ; https://github.com/pauling-ai/youtube-mcp-server ; https://github.com/ZubeidHendricks/youtube-mcp-server ; https://github.com/kirbah/mcp-youtube
- Blender: https://github.com/ahujasid/blender-mcp
