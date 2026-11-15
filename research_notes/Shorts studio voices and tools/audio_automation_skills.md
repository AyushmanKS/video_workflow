# Open-source music/SFX generation, trend/publishing/QA automation, and the Claude Code skills ecosystem for a local short-video studio (as of Nov 2026)

Scope note: this pass used about 19 tool calls. Items marked **[unverified]** come from prior knowledge or a single secondary source and were not checked against a primary page in this session. Many search hits were SEO blogs, so findings lean on official repos, model cards and Google docs wherever those were reachable.

## 1. Music and SFX generation models (commercial license, Apple Silicon) and free libraries

### Takeaway
ACE-Step 1.5 (MIT code and weights, outputs explicitly usable commercially, official MLX/macOS path, under 4 GB VRAM claimed) is the only verified, clearly commercial, Mac-native music model found. Most alternatives are non-commercial or carry revenue or territory caps: YuE2 weights, MusicGen weights, MMAudio (indirect evidence), ThinkSound, HunyuanVideo-Foley, DOVER-style S-Lab licenses and the Stability Community License above US$1M revenue. No model documents Indian classical or raga ability, so tanpura/flute beds would need listening tests.

### Cited Findings
- **ACE-Step 1.5, license.** The license is MIT (the LICENSE file reads "Copyright (c) 2026 ACEStep"), and the HF card says users "can strictly use the generated music for commercial purposes." — [HF model card](https://huggingface.co/ACE-Step/Ace-Step1.5); [LICENSE](https://github.com/ace-step/ACE-Step-1.5/blob/main/LICENSE)
- **ACE-Step 1.5, training data.** The card says the training data is "professionally licensed music tracks," public-domain and royalty-free music, and MIDI-to-audio renders. — [HF model card](https://huggingface.co/ACE-Step/Ace-Step1.5)
- **ACE-Step 1.5, architecture.** The language model comes in 0.6B, 1.7B and 4B sizes (Qwen3-based). The DiT comes in base, sft, turbo and turbo-rl variants. The card claims under 4 GB VRAM, prompt adherence in 50+ languages, and "under 2 seconds on an A100 / under 10 s on RTX 3090" per full song. There are no Mac timings. — [HF model card](https://huggingface.co/ACE-Step/Ace-Step1.5)
- **ACE-Step 1.5 on Mac.** The repo lists an MLX backend for Apple Silicon, MPS support, macOS launch scripts (`start_gradio_ui_macos.sh`, `start_api_server_macos.sh`), a macOS portable package and Python 3.11–3.12. For 8–16 GB it recommends the 2B turbo/sft DiT with the 0.6B LM (1.7B for 12–16 GB). It claims "1000+ instruments and styles," with no mention of Indian or world music. — [GitHub repo](https://github.com/ace-step/ACE-Step-1.5)
- **ACE-Step 1.5 XL.** XL was announced on 2026-04-02 as a 4B-parameter DiT (xl-base, xl-sft, xl-turbo) that "requires ≥12GB VRAM (with offload), ≥20GB recommended." It is likely too heavy to run beside anything else on a 16 GB Air. — [GitHub repo](https://github.com/ace-step/ACE-Step-1.5)
- **ACE-Step 1.5, setup and security.** The quick start pipes a remote script into `sh` with no checksum, portable packages come from files.acemusic.ai, and the repo says the "only official website" is its GitHub Pages site. — [GitHub repo](https://github.com/ace-step/ACE-Step-1.5)
- **ACE-Step on 16 GB Macs.** One guide warns that the default model loadout is sized for a 24 GB CUDA card, so smaller LM variants are needed on Macs (secondary source). — [freeaimusictools guide](https://freeaimusictools.com/blog/ace-step-apple-silicon-install/)
- **ACE-Step license conflict.** Some blogs say ACE-Step is "Apache 2.0," which likely confuses it with v1. The official repo and card both say MIT. — [DEV guide](https://dev.to/czmilo/ace-step-15-the-complete-2026-guide-to-open-source-ai-music-generation-522e); [Boppy](https://boppy.me/blog/best-open-source-ai-music-models)
- **Stable Audio Open / Open Small.** These use the Stability AI Community License: free commercial use under US$1M annual revenue, with an enterprise license required above that. Stability updated its license list on 2026-05-21 to add Stable Audio 3.0. The Open Small terms were only confirmed via a third-party HF mirror, and the official repo is gated. — [Stability license page](https://stability.ai/license); [HF mirror](https://huggingface.co/joeriben/stable-audio-open-small); [TechCrunch on Open Small](https://techcrunch.com/2025/05/14/stability-ai-releases-an-audio-generating-model-that-can-run-on-smartphones); [Digital Music News, SA 3.0](https://www.digitalmusicnews.com/2026/05/21/stability-ai-3-0-release/)
- **YuE.** YuE v1 is Apache 2.0 for code and weights, with a requested credit ("YuE by HKUST/M-A-P"). YuE2 keeps Apache-2.0 code but puts its weights under CC BY-NC 4.0 plus a separate creator permission. Sources disagree on whether outputs can be sold. — [YuE repo](https://github.com/multimodal-art-projection/YuE); [Boppy licenses](https://boppy.me/blog/open-source-ai-music-model-licenses); [it-jim](https://www.it-jim.com/blog/best-open-source-ai-music-generator/)
- **DiffRhythm.** The repo says code and DiT weights are Apache 2.0, but one source flags that the HF card metadata also names a Stable Audio community license, apparently inherited from its VAE or components. — [DiffRhythm repo](https://github.com/ASLP-lab/DiffRhythm); [soundgen.ai](https://soundgen.ai/ai-music-models)
- **Video-to-audio (Foley) models.** HunyuanVideo-Foley weights use the Tencent Hunyuan Community License, with territory limits that exclude the EU, UK and South Korea, plus conditions. MMAudio was described as CC-BY-NC-4.0 only in a third-party PR, about fal.ai's hosted endpoint. That same PR calls ThinkSound "research-only." — [Hunyuan LICENSE](https://huggingface.co/tencent/HunyuanVideo-Foley/blob/main/LICENSE); [reeleehq/foley PR #174](https://github.com/reeleehq/foley/pull/174)
- **Pixabay music.** Pixabay music uses the Pixabay Content License (free, no attribution), but some contributors register tracks in Content ID, so claims can still appear. The Pixabay certificate can be used to dispute a claim, but the outcome isn't guaranteed. These are secondary creator-guide sources. — [hellothematic](https://hellothematic.com/thematic-vs-pixabay/); [foximusic](https://www.foximusic.com/blog/need-background-music-that-wont-trigger-content-id/)

### Inferences
- The best fit is a short instrumental ACE-Step 1.5 bed (2B turbo DiT with the 0.6B LM through MLX), prompted with "tanpura drone, bansuri, slow, devotional, no vocals." Run it only when no other model (Veena TTS, image model) is loaded, because CLAUDE.md requires one heavy model at a time. The numpy tanpura could remain the fallback or layer under it. Raga accuracy is unknown, and the model will probably give a "generic Indian" timbre rather than a correct raga.
- Inspect the install script before running it. Prefer `git clone` plus a pinned commit and a manual venv over `curl | sh` or the portable binary.
- Stable Audio Open Small is legally usable while revenue stays under $1M, but the license is revocable or changeable by Stability, and access is gated. That makes it a weaker choice than MIT ACE-Step.
- For SFX (chalk scratches, whooshes), procedural numpy is already fully owned and license-clean. Foley models add license risk for little gain on a chalkboard style.

### Gaps
- No verified primary license text was found for MMAudio weights, ThinkSound, SongBloom, TangoFlux or AudioLDM2 in this pass. **[unverified, from prior knowledge]:** AudioCraft/MusicGen weights are CC-BY-NC 4.0 (non-commercial), and TangoFlux weights were released under a Stability-derived non-commercial or community license. Check these on HF cards before use.
- There are no measured ACE-Step generation times or peak RAM figures for an M-series Air, so a local benchmark is needed.
- The YouTube Audio Library terms and Freesound per-file license rules (CC0 vs CC-BY vs CC-BY-NC mixed on one site) were not fetched. **[unverified]:** Freesound licenses each sound individually, so filter to CC0. YouTube Audio Library tracks may require attribution in the description.

## 2. Trend and topic research (pytrends replacements, free APIs)

### Takeaway
The official Google Trends API is still an invite-only alpha (announced July 2025, still application-only per Oct 2026 sources). pytrends was archived on 2025-04-17, and trendspy is the community fork, but its last release seen was 0.1.6 (Dec 2024). The Reddit Data API now needs approval and is free only for non-commercial use, which likely excludes a monetized channel. Keeping YouTube Data API plus Wikipedia pageviews as the core is still the soundest zero-cost choice.

### Cited Findings
- **pytrends** was archived on 17 April 2025 and is unmaintained. — [cite42.dev](https://www.cite42.dev/blog/google-trends-api); [DEV, alternatives 2026](https://dev.to/reliableapps/google-trends-api-alternatives-in-2026-getting-trends-data-as-json-and-what-to-do-about-429s-2af0)
- **Official Google Trends API.** Sources say the alpha was announced July 2025 and is limited to selected testers, with no published pricing or GA date. These are third-party sources, and the Google page was not fetched. — [DEV, "still invite-only"](https://dev.to/ishemah/googles-trends-api-is-still-invite-only-i-tested-what-the-alternatives-return-5be4); [lilachbullock](https://www.lilachbullock.com/google-trends-api/)
- **trendspy** offers interest_over_time, trending_now, related_queries and suggestions. Its latest PyPI release noted was 0.1.6 (Dec 2024), and it depends on undocumented endpoints. — [DEV alternatives](https://dev.to/reliableapps/google-trends-api-alternatives-in-2026-getting-trends-data-as-json-and-what-to-do-about-429s-2af0); [cite42.dev](https://www.cite42.dev/blog/google-trends-api)
- **Reddit Data API.** The free tier is approved non-commercial use only, at 100 QPM per OAuth client (10 without OAuth). Since 2025-11-11, every new client needs approval. Commercial prices conflict across sources and were not verified. — [data365](https://data365.co/blog/reddit-api-pricing); [apiserpent](https://apiserpent.com/blog/free-reddit-api); [socialcrawl](https://www.socialcrawl.dev/blog/reddit-api-key-limits-alternatives-2026)
- **YouTube search quota.** search.list now has its own roughly 100-call/day bucket (since 2026-06-01, per one guide), separate from the 10,000-unit default. — [Blotato](https://www.blotato.com/blog/youtube-api-pricing)

### Inferences
- Treat trendspy as optional and best-effort. Wrap it so failures (429s, endpoint changes) do not block the trend stage, and pin and inspect its version because it scrapes undocumented endpoints. Apply for the Google Trends alpha. It costs nothing, but there is no guarantee of access.
- Using Reddit data for a monetized channel's topic selection is plausibly "commercial use," so avoid it, or apply for approval and state the use honestly.
- The vendored `yt-viral` skill (outlier ranking vs channel baseline) plus Wikipedia pageviews (per-language) is already a reasonable free stack. The search.list bucket now caps discovery at about 100 searches/day, so cache results.

### Gaps
- The Google Trends alpha page and trendspy GitHub commit activity in 2026 were not checked directly.
- No maintained open-source creator-analytics GitHub project was found that clearly beats the existing in-house code.
- Free news APIs (GDELT, etc.) were not researched in this pass. **[unverified]:** GDELT is free and open.

## 3. YouTube publishing and analytics automation

### Takeaway
As of Nov 2026, Google's live `videos.insert` reference says uploads from unverified API projects are **not** restricted to private mode. That reverses the 2020 rule, though older revision history still contradicts it. Uploads now draw from a separate 100-call/day "Video Uploads" bucket at 1 unit each. engagedViews is an Analytics API core metric, while thumbnail impressions and CTR appear in the bulk Reporting API. No compelling open-source uploader beats the existing in-house `publish.py`. Postiz is AGPL-3.0 and multi-network, but its YouTube support was not confirmed.

### Cited Findings
- **Live `videos.insert` reference.** It reads: "Videos uploaded from unverified API projects are not restricted to private viewing mode." It gives a daily limit of 100 calls and says "A call to this method has a quota cost of 1 unit in the Video Uploads quota bucket." — [Google: videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert)
- **Conflicting reports on the change.** Third-party guides disagree: one dates the reversal to Nov 2026, while others still say audit-less uploads are locked private. Advice is to read back privacyStatus after upload. Quota beyond the default still needs the Audit and Quota Extension form, with no published timeline. — [breakreach](https://www.breakreach.com/developers/youtube-api); [timetopost](https://timetopost.co/blog/how-to-upload-videos-youtube-api/); [clipember](https://clipember.com/guides/youtube-upload-comes-out-private)
- **engagedViews.** It is a core metric in the YouTube Analytics API. Since 2025-03-31, Shorts "views" count every start or replay, while engaged views keep the older definition. — [Analytics revision history](https://developers.google.com/youtube/analytics/revision_history); [Analytics metrics](https://developers.google.com/youtube/analytics/metrics)
- **Impressions and CTR.** `video_thumbnail_impressions` and `video_thumbnail_impressions_ctr` are listed under Reporting API (bulk report jobs) metrics. — [Reporting API metrics](https://developers.google.com/youtube/reporting/v1/reports/metrics)
- **Postiz** (gitroomhq/postiz-app) is AGPL-3.0 per its repo and README, though some listings wrongly say Apache 2.0. It can be self-hosted, and YouTube support was not confirmed in the sources seen. — [Postiz repo](https://github.com/gitroomhq/postiz-app)

### Inferences
- Keep `publish.py`, add a post-upload privacyStatus check, and log quota use per bucket. Add a Reporting API job (create once, then download daily CSVs) to get impressions and CTR, which the Analytics API query path may not provide. This is still zero-cost.
- Postiz needs a Node/Postgres/Redis stack and is AGPL, which is too heavy for a 16 GB Air pipeline whose publishing already works. Inspect it only if multi-platform posting becomes a goal.
- The G3 human gate stays mandatory whatever the tooling.

### Gaps
- Whether Shorts-feed impressions ("shown in feed") are exposed via any API is unconfirmed.
- The Reporting API impressions metric's coverage for Shorts specifically was not verified.
- Well-maintained, YouTube-only open-source uploaders (e.g., older tokland/youtube-upload) were not re-checked. **[unverified]:** tokland/youtube-upload is long unmaintained.

## 4. Video QA tooling

### Takeaway
DOVER's official code is under the non-commercial S-Lab License 1.0, and its weights' license is disputed (MIT on HF vs S-Lab in the repo). Q-Align's repo also ships an S-Lab license file. So learned aesthetic and quality scorers are legally murky for a monetized channel. Classic tools like VMAF and PySceneDetect are permissively licensed and CPU-friendly, but this session did not confirm those licenses.

### Cited Findings
- **DOVER.** The official repo has an S-Lab License 1.0 (non-commercial). An open issue asks whether the weights are MIT (as the HF card says) or S-Lab, and no maintainer reply was seen. — [DOVER issue #43](https://github.com/VQAssessment/DOVER/issues/43); [DOVER repo](https://github.com/VQAssessment/DOVER)
- **Q-Align.** Its repo contains both a LICENSE and an S-Lab-LICENSE file, and it is unclear which governs the weights. The arXiv paper is CC BY-NC-SA 4.0, which covers the paper only. — [Q-Align repo](https://github.com/q-future/q-align); [arXiv](https://arxiv.org/html/2312.17090v1)

### Inferences
- The existing ffmpeg-based QA (loudness, black/freeze, ASR CER, speaker consistency) already covers the defects that matter. Worthwhile zero-risk additions:
  - PySceneDetect: confirm that scene cuts match the planned scene timings.
  - An ffmpeg `signalstats` or blur metric for chalk legibility.
  - A subtitle-timing check against ASR word timestamps.
- Use DOVER or Q-Align only as internal, non-published diagnostic signals, if at all. Q-Align is LMM-sized and would compete for memory.
- VMAF needs a reference video. For generated content it only fits regression checks (re-render vs approved master), not absolute quality.

### Gaps
- **[unverified, prior knowledge]:** PySceneDetect is BSD-3-Clause, Netflix VMAF is BSD-2-Clause-Patent and available in Homebrew ffmpeg builds via libvmaf, and the LAION aesthetic predictor is MIT (it is image-only, scoring single frames). Confirm on each repo.
- No subtitle-QA-specific open-source tool was researched.

## 5. Claude Code skills, plugins and subagent collections

### Takeaway
Anthropic's official sources are `anthropics/skills` (marketplace `anthropic-agent-skills`, with plugins `document-skills` and `example-skills`) and `anthropics/claude-plugins-official`. Remotion publishes official agent skills (`remotion-dev/skills`). The community collections VoltAgent/awesome-claude-code-subagents (MIT, "we do not audit") and wshobson/agents (MIT per mirror, one index says AGPL) are mostly software-engineering agents and add little to a content studio that already has 12 tailored agents and vendored yt-* skills.

### Cited Findings
- **anthropics/skills.** Install with `/plugin marketplace add anthropics/skills`, then `/plugin install document-skills@anthropic-agent-skills` or `example-skills@anthropic-agent-skills`. Categories are Creative & Design, Development, Enterprise, and Document skills. The README says many skills, including docx/pdf/pptx/xlsx, are Apache 2.0, and the skills are "for demonstration and educational purposes." — [anthropics/skills](https://github.com/anthropics/skills)
- **claude-plugins-official.** A separate official directory (`anthropics/claude-plugins-official`) is reported as containing Anthropic-built plus partner and community plugins, and is auto-added in interactive Claude Code. The plugin count (around 300) comes from a secondary source. — [systemprompt guide](https://systemprompt.io/guides/getting-started-anthropic-marketplace); [adyog mirror listing](https://ir.adyog.com/repos/anthropics/claude-plugins-official/)
- **Remotion skills.** These are hosted at `github.com/remotion-dev/skills`. Install with `npx remotion skills add` in a Remotion project, or `npx skills add remotion-dev/skills`, and docs are at remotion.dev/docs/ai/skills. Many look-alike "remotion-best-practices" packages exist from third parties. — [Tella guide](https://www.tella.com/blog/how-to-use-remotion-agent-skills-with-claude-code); [claudemarketplaces](https://claudemarketplaces.com/skills/remotion-dev/skills/remotion-best-practices)
- **VoltAgent/awesome-claude-code-subagents.** MIT (© 2025 VoltAgent), 100+ subagents, and the README states "We do not audit or guarantee the security or correctness of any subagent." — [repo](https://github.com/VoltAgent/awesome-claude-code-subagents); [LICENSE](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/LICENSE)
- **wshobson/agents.** A mirror says MIT, and one index says "Code: AGPL-3, Data: CC BY-SA 4.0" (conflict). It contains plugins and subagents, some of which reference external plugins with their own licenses. — [mirror](https://github.com/mvandermeulen/wshobson-agents); [ecosyste.ms](https://awesome.ecosyste.ms/projects/github.com/wshobson/agents)

### Inferences
- **Fit for this studio:**
  - The studio renders with its own Python/ffmpeg chalk engine, not Remotion (React). Remotion skills only matter if overlays or animations move to Remotion, and that adds a Node toolchain plus Remotion's own license terms (**[unverified]:** Remotion requires a paid company license for larger companies but is free for individuals).
  - From `anthropics/skills`, `skill-creator` and the doc skills are the most useful, and those are already available in this environment via `anthropic-skills:*`.
  - Generic subagent collections (VoltAgent, wshobson) target coding. The project's `trend-researcher`, `scriptwriter`, `video-qa` and `performance-analyst` agents plus the `storytelling` and `yt-*` skills already cover research, hooks, production and analytics more specifically.
- **Security:**
  - Plugins can bundle hooks (shell commands run automatically on tool events) and MCP servers (arbitrary local processes).
  - Before installing, read every `hooks` entry, `.mcp.json`, and any scripts. Pin to a commit SHA, and prefer copying a single SKILL.md (pure markdown) into `.claude/skills/` over installing a whole plugin. This matches how the yt-* skills were vendored.
  - Avoid skills that request YouTube OAuth tokens or post on the owner's behalf, because that would bypass the G3 gate.

### Gaps
- `hesreallyhim/awesome-claude-code` and `travisvn/awesome-claude-skills` (curated lists) were not verified in this pass, so they have no license or maintenance data.
- No community skill was found that is specific to YouTube analytics, Hindi scriptwriting or Indian mythology content.
- The exact contents and count of `claude-plugins-official` were not fetched from the primary repo.
