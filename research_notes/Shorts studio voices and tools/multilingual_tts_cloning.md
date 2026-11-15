# General-purpose / multilingual open-weight TTS and voice cloning (as of Nov 2026): fitness for Indic and English narration

Context: zero cost, local, commercial/monetized use required, MacBook Air M5 16 GB, no NVIDIA. Baselines: English = Kokoro-82M af_heart (Apache-2.0); Hindi = Veena (kavya). Research done 2026-11-16 with ~17 tool calls; many vendor claims are self-reported.

## Q1. Current status, languages, and Indian-language quality of each model

### Takeaway
Among general-purpose open-weight models, only a few cover Hindi at all: Chatterbox Multilingual V3 (MIT, plus a dedicated Hindi finetune), VoxCPM2 (Apache-2.0), MOSS-TTS v1.5 (reported Apache-2.0), NVIDIA Magpie-TTS Multilingual (NVIDIA Open Model License), and Kokoro (4 weak Hindi voices). Higgs Audio v3 and Voxtral TTS also speak Hindi but are non-commercial. **No general-purpose model in this scope lists Marathi, Bengali, Telugu, Tamil, Gujarati, Kannada, Malayalam or Punjabi as a supported language.** The only exception is OmniVoice's 600+ language claim, and its weights are CC-BY-NC. For those languages, look to the Indic-specialized models covered by other researchers. mlx-audio lists two: Maya2 Native and rumik-oss 1.

### Cited Findings

**Chatterbox / Chatterbox Multilingual (Resemble AI)**
- Multilingual V3 is the current general-purpose multilingual model: 0.5B parameters, Llama backbone, 23 languages, and Hindi is one of them. V2 remains as a legacy checkpoint. — [HF model card](https://huggingface.co/ResembleAI/chatterbox)
- V3 languages: Arabic, Chinese, Danish, Dutch, English, Finnish, French, German, Greek, Hebrew, Hindi, Italian, Japanese, Korean, Malay, Norwegian, Polish, Portuguese, Russian, Spanish, Swahili, Swedish, Turkish. No other Indic language is listed. — [HF model card](https://huggingface.co/ResembleAI/chatterbox)
- A "Single Language Pack" adds 6 dedicated finetunes, including Hindi (`ResembleAI/Chatterbox-Multilingual-hi`). — [HF model card](https://huggingface.co/ResembleAI/chatterbox); [Resemble V3 post](https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages)
- Resemble's own page claims "stronger language-specific pronunciation and natural delivery in Hindi". This is vendor marketing, with no independent Hindi MOS found. — [Resemble model page](https://resemble.ai/learn/models/chatterbox-multilingual)
- Sources give the language count as 23, 25 (including dialects and language packs) or "20+". — [Resemble V3 post](https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages); [Resemble model page](https://resemble.ai/learn/models/chatterbox-multilingual)
- A community "chatterbox-indic-lora" exists on HF. It is unevaluated and its license was not checked. — [HF](https://huggingface.co/reenigne314/chatterbox-indic-lora)
- mlx-audio supports Chatterbox (v2/v3, 23 languages) natively on Apple Silicon. — [mlx-audio](https://github.com/Blaizzy/mlx-audio)

**Qwen3-TTS (Alibaba Qwen)**
- Apache-2.0, released Jan 2026. Models: 1.7B VoiceDesign, 1.7B CustomVoice, 1.7B Base, 0.6B CustomVoice and 0.6B Base. It offers 3-second cloning and voice design. — [arXiv 2601.15621](https://arxiv.org/abs/2601.15621); [Gigazine](https://gigazine.net/gsc_news/en/20260123-qwen3-tts-family-opensource)
- 10 languages: zh, en, ja, ko, de, fr, ru, pt, es, it. **No Hindi or Indic.** — [Gigazine](https://gigazine.net/gsc_news/en/20260123-qwen3-tts-family-opensource); [arXiv](https://arxiv.org/abs/2601.15621)
- Supported in mlx-audio. — [mlx-audio](https://github.com/Blaizzy/mlx-audio)

**CosyVoice 3 / Fun-CosyVoice3 (Alibaba FunAudioLLM)**
- Covers 9 languages (en, zh, ja, ko, de, es, fr, it, ru) plus 18 Chinese dialects, and is reported as Apache-2.0. **No Hindi.** This comes only from a secondary source (tts.ai) and was not verified on the official repo. — [tts.ai](https://tts.ai/voices/cosyvoice3/)

**IndexTTS2 / IndexTTS-2.5 (bilibili)**
- License is the "bilibili Model Use License Agreement". For commercial use, the repo says to contact indexspeech@bilibili.com, so treat it as **not freely commercial** until the terms are read. — [GitHub](https://github.com/index-tts/index-tts)
- IndexTTS-2.5 (2026-08-10) covers zh, en, ja, es, ar; IndexTTS-2 is zh/en. **No Hindi.** — [GitHub](https://github.com/index-tts/index-tts)
- CV3-Eval zero-shot results for IndexTTS2.5: avg WER 6.75, SS 73.18; en WER 5.12, SS 68.06. The RL variant averages WER 6.00. RTF is 0.21 for 2.5 and 0.33 for v2, both on an RTX 4090. The repo targets CUDA only and does not mention MPS. — [GitHub](https://github.com/index-tts/index-tts)
- The model card advertises emotion and duration control but gives no license field. — [HF](https://huggingface.co/IndexTeam/IndexTTS-2)

**Fish Speech / OpenAudio / Fish Audio S2 / Fish Audio Drama 3**
- Fish Audio S2 Pro is under the "Fish Audio Research License", which allows research and non-commercial use only. Commercial use needs a paid license from Fish Audio, which itself says S2 is "open weights, not open source". — [Fish Audio blog](https://fish.audio/blog/what-we-mean-by-open-source-for-s2/); [arXiv 2603.08823](https://arxiv.org/abs/2603.08823)
- Fish Audio Drama 3 is under a Community License v1.0 that allows free commercial use only if the user and affiliates earn under US$500k a year. — [magica.com](https://magica.com/news/fish-audio-drama-3-open-weights-commercial-limits)
- In mlx-audio, Fish Audio Drama 3 is listed as a 35B mixture-of-experts model covering 83 languages. — [mlx-audio](https://github.com/Blaizzy/mlx-audio)
- S2 Pro is the top open-weight model on the Artificial Analysis Speech Arena (Elo 1121) in an undated snapshot. — [Artificial Analysis](https://artificialanalysis.ai/text-to-speech/leaderboard)

**Higgs Audio v3 (Boson AI)**
- 4B parameters, released 2026-06-04. It covers 100+ languages, Boson reports single-digit WER/CER on 100 of them, and it has zero-shot cloning and inline emotion/prosody tokens. — [HF](https://huggingface.co/bosonai/higgs-audio-v3-tts-4b); [LMSYS blog](https://www.lmsys.org/blog/2026-06-04-higgs-audio-v3-tts)
- License is the **Boson Higgs TTS 3 Research and Non-Commercial License**. Production use or embedding in a product requires a separate commercial license, so it is **excluded**. — [HF](https://huggingface.co/bosonai/higgs-audio-v3-tts-4b); [README](https://cdn.jsdelivr.net/gh/boson-ai/higgs-audio@main/README.md)
- There is an MLX port (`aufklarer/Higgs-TTS-3-4B-MLX-bf16`), and mlx-audio supports Higgs v3 and v2. — [HF](https://huggingface.co/aufklarer/Higgs-TTS-3-4B-MLX-bf16); [mlx-audio](https://github.com/Blaizzy/mlx-audio)

**Voxtral TTS (Mistral, Mar 2026)**
- 4B parameters, 9 languages including Hindi, with `hi_male` and `hi_female` preset voices in mlx-audio. — [HF](https://huggingface.co/mistralai/Voxtral-4B-TTS-2603); [mlx-audio](https://github.com/Blaizzy/mlx-audio)
- Weights are **CC BY-NC 4.0**, inherited from the reference voices, so commercial use goes through Mistral's API or a separate license. It is **excluded**. One source claims Apache-2.0, but that conflicts with the model card. — [HF](https://huggingface.co/mistralai/Voxtral-4B-TTS-2603); [SiliconANGLE](https://siliconangle.com/2026/03/26/mistral-releases-open-weights-speaking-ai-model-voxtral-tts/); contradicted by [enterprisedna](https://enterprisedna.co/resources/news/mistral-voxtral-open-source-voice-ai)
- One outlet reports that Mistral's blind tests rated its Hindi naturalness above ElevenLabs Flash v2.5. This is vendor-reported. — [voice.lapaas.com](https://voice.lapaas.com/mistral-release-new-open-source-speech-model-voxtral-tts)

**VoxCPM2 (OpenBMB)**
- Apache-2.0, "free for commercial use". 2B parameters, tokenizer-free, 48 kHz output. It offers voice design from text, controllable cloning, and "ultimate cloning" from reference audio plus transcript. — [HF](https://huggingface.co/openbmb/VoxCPM2)
- 30 languages, of which **Hindi is the only Indic one**. — [HF](https://huggingface.co/openbmb/VoxCPM2)
- The card claims SOTA or competitive results on Seed-TTS-eval, CV3-eval and the MiniMax Multilingual Test but gives no numbers on the card and no Hindi breakdown. It needs about 8 GB VRAM, runs at RTF 0.30 on an RTX 4090, and lists CUDA as a requirement. mlx-audio supports VoxCPM2. — [HF](https://huggingface.co/openbmb/VoxCPM2); [mlx-audio](https://github.com/Blaizzy/mlx-audio)

**MOSS-TTS v1.5 (OpenMOSS)**
- 31 languages; v1.5 added Hindi along with Cantonese, Dutch, Finnish, Macedonian, Malay, Romanian, Swahili, Tagalog, Thai and Vietnamese. It has explicit pause control and cloning. — [HF mirror of card](https://huggingface.co/niobures/MOSS-TTS-v1.5)
- The Apache-2.0 license is reported only by a third-party blog and is unverified on the official repo. — [blog](https://blog-mushroom.pages.dev/blog/moss-tts-v15-multilingual-voice-clone/)
- In mlx-audio, MOSS-TTS is 8B (31 languages) and MOSS-TTS-Nano covers 20 languages. — [mlx-audio](https://github.com/Blaizzy/mlx-audio)

**OmniVoice (k2-fsa, Apr 2026)**
- 0.6B parameters, 600+ languages (646 tags), zero-shot cloning plus voice design, RTF as low as 0.025. — [HF](https://huggingface.co/k2-fsa/OmniVoice); [arXiv 2604.00688](https://arxiv.org/abs/2604.00688)
- The code is Apache-2.0, but **the pretrained model is CC-BY-NC** because of the Emilia training data, so it is **excluded**. The repo metadata says apache-2.0, which conflicts with the card text. — [HF](https://huggingface.co/k2-fsa/OmniVoice)

**NVIDIA Magpie-TTS Multilingual 357M**
- Released under the NVIDIA Open Model License, which permits commercial use; check the full text. Hindi is listed: sources name 9 languages (en, es, fr, de, zh, vi, it, hi, ja), or 12 after an update. — [HF](https://huggingface.co/nvidia/magpie_tts_multilingual_357m); [NVIDIA FAQ](https://perspectives.nvidia.com/nemotron-speech/task/faq/which-text-to-speech-models-support-more-than-five-languages-with-natural-soundi/); [HF blog](https://huggingface.co/blog/nvidia/magpie-tts-multilingual-voice-agents)
- It ranks third among open weights on Artificial Analysis (Elo 1071, Feb 2026), above Kokoro (Elo 1056). — [Artificial Analysis](https://artificialanalysis.ai/text-to-speech/leaderboard)
- Apple-friendly ports exist: an MLX 4-bit build, a CoreML 8-bit build and a GGUF (magpie-tts.cpp). — [MLX 4bit](https://huggingface.co/aufklarer/Magpie-TTS-Multilingual-357M-MLX-4bit); [CoreML](https://huggingface.co/aufklarer/Magpie-TTS-Multilingual-357M-CoreML-8bit); [GGUF](https://huggingface.co/mudler/magpie-tts.cpp-gguf)

**Kokoro-82M (Hindi voices)**
- 4 Hindi voices: hf_alpha, hf_beta, hm_omega, hm_psi. **All are graded C overall**, each trained on 10–100 minutes, with 1–10 hours of Hindi data in total. Hindi G2P falls back to espeak-ng `hi`. af_heart is graded A. — [Kokoro VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)
- mlx-audio lists HI for Kokoro but has no Hindi language code in its table, which suggests limited support. — [mlx-audio](https://github.com/Blaizzy/mlx-audio)

**Leaderboards (English-centric)**
- Artificial Analysis open-weight top 5 (snapshot undated): Fish Audio S2 Pro 1121, Step Audio EditX 1101, Magpie-Multilingual 357M 1071, Kokoro 82M 1056, Maya1 1050. — [Artificial Analysis](https://artificialanalysis.ai/text-to-speech/leaderboard)
- An August 2026 blog names "Breeze TTS 2" (Elo 1215) as the new open-weight leader. I did not verify this, its license, or its languages. — [Pinggy](https://pinggy.io/blog/best_open_source_self_hosted_text_to_speech_models/)
- Several sources say no open-weight model is in the overall top 10. — [offlinetts](https://offlinetts.com/blog/tts-arena-leaderboard-2026/)

### Inferences
- Commercially usable, locally runnable, general models with Hindi: **Chatterbox V3 / Chatterbox-hi (MIT)**, **VoxCPM2 (Apache-2.0)**, **Magpie Multilingual (NVIDIA OML)**, **MOSS-TTS v1.5 (license to verify)** and Kokoro (weak Hindi).
- The strongest-sounding broad models (Fish S2 Pro, Higgs v3, Voxtral, OmniVoice) all fail the commercial-license test. Fish Drama 3 is legally free below $500k revenue, but as a 35B MoE it is impractical on 16 GB.
- Chatterbox output always carries a PerTh watermark ([HF](https://huggingface.co/ResembleAI/chatterbox)). It is inaudible and fine for YouTube, but worth noting.

### Gaps
- No independent Hindi MOS/CER found for Chatterbox-hi, VoxCPM2, Magpie or MOSS-TTS. A local A/B test against Veena with the project's `speaker_consistency` QA is required.
- Not verified this session, from prior knowledge (2025). **Treat all of these as unverified:**
  - F5-TTS / E2-TTS: weights CC-BY-NC (Emilia), en/zh.
  - XTTS-v2: Coqui Public Model License, non-commercial; Coqui shut down, so no commercial license is obtainable. It supports Hindi.
  - MaskGCT (Amphion): CC-BY-NC.
  - Spark-TTS: CC-BY-NC-SA, en/zh.
  - Orpheus: Apache-2.0, English. A multilingual research release reportedly included Hindi, at lower quality.
  - Dia / Dia2 (Nari Labs): Apache-2.0, English dialogue.
  - Sesame CSM-1B: Apache-2.0, English.
  - Zonos v0.1: Apache-2.0; en, ja, zh, fr, de.
  - MegaTTS3: Apache-2.0, en/zh.
  - Kyutai TTS 1.6B: CC-BY-4.0, en/fr.
  - None of these list Hindi with good quality.
- Not researched: Step Audio EditX, Maya1 and Breeze TTS 2 (licenses and languages).
- The MOSS-TTS license and CosyVoice3 language list were not confirmed on the official repos.

## Q2. License, cloning, emotion control, metrics, size and Apple Silicon feasibility

### Takeaway
On a 16 GB Air, the practical candidates are sub-2B models with MLX support in mlx-audio: Chatterbox V3 (0.5B), Magpie 357M, VoxCPM2 (2B) and Qwen3-TTS (0.6B/1.7B, no Hindi). 4B models (Higgs v3, Voxtral) would fit when quantized but are non-commercial anyway. Published metrics are mostly vendor-reported and English/Chinese-centric.

### Cited Findings
| Model | Weights license | Commercial? | Size | Cloning | Emotion / style | Hindi | Apple path |
|---|---|---|---|---|---|---|---|
| Chatterbox ML V3 (+ hi pack) | MIT ([HF](https://huggingface.co/ResembleAI/chatterbox)) | Yes (watermarked) | 0.5B | Zero-shot ref audio | Exaggeration + CFG knobs | Yes, dedicated finetune | mlx-audio ([link](https://github.com/Blaizzy/mlx-audio)) |
| VoxCPM2 | Apache-2.0 ([HF](https://huggingface.co/openbmb/VoxCPM2)) | Yes | 2B, ~8 GB VRAM | Ref audio (+ transcript) | Text voice design / style guidance | Yes | mlx-audio |
| Magpie-TTS ML 357M | NVIDIA Open Model License ([HF](https://huggingface.co/nvidia/magpie_tts_multilingual_357m)) | Yes (verify text) | 357M | Not confirmed | Not confirmed | Yes | MLX / CoreML / GGUF ports |
| MOSS-TTS v1.5 | Apache-2.0 (unverified, [blog](https://blog-mushroom.pages.dev/blog/moss-tts-v15-multilingual-voice-clone/)) | Likely | 8B (Nano smaller) | Yes | Pause control | Yes | mlx-audio |
| Qwen3-TTS | Apache-2.0 ([arXiv](https://arxiv.org/abs/2601.15621)) | Yes | 0.6B / 1.7B | 3 s ref | Voice design | No | mlx-audio |
| CosyVoice3 | Apache-2.0 (secondary, [tts.ai](https://tts.ai/voices/cosyvoice3/)) | Likely | n/a | Yes | n/a | No | n/a |
| IndexTTS-2 / 2.5 | bilibili Model Use License ([GitHub](https://github.com/index-tts/index-tts)) | Contact bilibili | n/a | Yes | Emotion + duration | No | CUDA only |
| Higgs Audio v3 | Research/Non-Commercial ([HF](https://huggingface.co/bosonai/higgs-audio-v3-tts-4b)) | **No** | 4B | Yes | Inline tags | Yes | MLX port |
| Voxtral TTS | CC BY-NC 4.0 ([HF](https://huggingface.co/mistralai/Voxtral-4B-TTS-2603)) | **No** | 4B | Yes | n/a | Yes | mlx-audio |
| OmniVoice | CC-BY-NC weights ([HF](https://huggingface.co/k2-fsa/OmniVoice)) | **No** | 0.6B | Yes | Voice design | Claimed (600+ langs) | n/a |
| Fish S2 Pro | Fish Audio Research License ([blog](https://fish.audio/blog/what-we-mean-by-open-source-for-s2/)) | **No** (paid) | n/a | Yes | Yes | n/a | n/a |
| Fish Drama 3 | Community License, < $500k revenue ([magica](https://magica.com/news/fish-audio-drama-3-open-weights-commercial-limits)) | Conditional | 35B MoE | Yes | Yes | 83 languages (Hindi unconfirmed) | mlx-audio, but too big |
| Kokoro-82M | Apache-2.0 | Yes | 82M | No (presets) | No | Grade C voices ([VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)) | mlx-audio |

- Chatterbox known issues: if the reference clip's language does not match the language tag, the output inherits the reference's accent (setting CFG to 0 mitigates this). Fast references need cfg around 0.3. Earlier multilingual checkpoints had repetition, unwanted continuation and off-prompt speech, which V3 claims to reduce. — [HF](https://huggingface.co/ResembleAI/chatterbox)
- IndexTTS2.5 CV3-Eval cross-lingual results (zh prompt): avg WER 6.22, SS 68.62. — [GitHub](https://github.com/index-tts/index-tts)

### Inferences
- The Chatterbox accent-leak issue matters for cross-language cloning: an English reference clip used for Hindi output may carry an English accent. Use a same-language reference per language, which defeats a single identical voice, or test CFG=0.
- The Apple feasibility claims come from mlx-audio and port listings. No published M-series speed figures were found for Chatterbox V3, VoxCPM2 or Magpie.

### Gaps
- No M5 / MLX benchmarks (RTF, memory) were found for any candidate.
- No numeric Seed-TTS-eval figures were extracted for VoxCPM2 or Chatterbox V3 (they are in the repos and papers, not the cards).

## Q3. Best picks for (a) English narration beyond Kokoro, (b) Hindi beyond Veena, (c) one cloned narrator across languages

### Takeaway
(a) For English, the most credible commercially usable upgrades to test against Kokoro af_heart are **Chatterbox V3** (expressive, with cloning) and **Magpie Multilingual 357M** (arena Elo 1071 vs Kokoro's 1056). **VoxCPM2** is a third option, with 48 kHz output and voice design. (b) For Hindi, the only general-purpose candidates worth A/B testing against Veena are **Chatterbox-Multilingual-hi**, **VoxCPM2** and **Magpie**. None has independent Hindi evidence of beating Veena. (c) For one cloned narrator across English and Hindi, **Chatterbox V3** and **VoxCPM2** are the only MIT/Apache options that clone across languages including Hindi. Neither covers the other 8 Indian languages.

### Cited Findings
- Kokoro is consistently around Elo 1050–1060, below Fish S2 Pro, Step Audio EditX and Magpie among open weights. — [Artificial Analysis](https://artificialanalysis.ai/text-to-speech/leaderboard); [offlinetts](https://offlinetts.com/blog/tts-arena-leaderboard-2026/)
- Chatterbox claims preference over ElevenLabs in side-by-side evaluations, citing a Podonos evaluation. This is vendor-reported. — [HF](https://huggingface.co/ResembleAI/chatterbox)
- Kokoro's Hindi voices are grade C, which sets a low bar; Veena is the real Hindi baseline. — [VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)
- Of the 9 Indian languages asked about, only Hindi appears in these general models' language lists; OmniVoice, the one 600+ language model, is CC-BY-NC. — [Chatterbox](https://huggingface.co/ResembleAI/chatterbox); [VoxCPM2](https://huggingface.co/openbmb/VoxCPM2); [OmniVoice](https://huggingface.co/k2-fsa/OmniVoice)
- mlx-audio lists Indic-specialized options outside this scope: Maya2 Native (11 Indic languages + English, cloning) and rumik-oss 1 (22 Indic languages + English, 3B). — [mlx-audio](https://github.com/Blaizzy/mlx-audio)

### Inferences
- Recommended test order on the Air (one model at a time, per the memory rule):
  1. Chatterbox V3 plus the Hindi pack, through mlx-audio.
  2. VoxCPM2.
  3. Magpie 357M (MLX 4-bit).
  4. Score each with the existing language-QA and `speaker_consistency` checks against Veena kavya and Kokoro af_heart.
- For one narrator across all target Indian languages, a general-purpose model is unlikely to be the answer in Nov 2026. A practical setup pairs an Indic-specialized model (e.g. one of those listed in mlx-audio) with an English cloner, or uses a voice-conversion pass. Chatterbox ships a voice-conversion script ([HF](https://huggingface.co/ResembleAI/chatterbox)) that could map Indic-model output onto a single timbre. This is untested.

### Gaps
- No blind listening comparisons of Chatterbox-hi, VoxCPM2 or Magpie Hindi against Veena exist in the sources found.
- Licenses for the Indic-specialized models in mlx-audio (Maya2, rumik-oss) are outside this scope and were not checked.
