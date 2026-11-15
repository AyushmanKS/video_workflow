# Open-weight Indic TTS models (checked 16 Nov 2026)

How this was checked: Hugging Face model and dataset metadata (license, `gated`, dates and downloads) was pulled from `huggingface.co/api` on 16 Nov 2026, and model cards were read directly. "gated: auto" means you must log in and accept terms, then access is granted automatically. Quality numbers below are the authors' own unless stated otherwise. I found no independent listening test that compares these models with each other.

## Which Indic TTS models exist and are current?

### Takeaway
Since Veena (mid-2025), the field has moved a lot. Three 2026 releases matter most:
- **Indic-Speak** (Bodhan AI / AI4Bharat, Sept 2026). 22 languages and 44 voices. AI4Bharat itself now recommends it over IndicF5 and Indic Parler-TTS. Community MLX ports exist.
- **Maya 2 Native** (Maya Research, the makers of Veena; checkpoint dated Oct 2026). 11 Indic languages plus English, 20 voices, zero-shot cloning, Apache-2.0. It has the strongest published evidence, but officially it runs only on NVIDIA CUDA.
- **SPRINGLab (IIT Madras)**: SPRING_F5 and Indic-Mio.

Sarvam AI has released no open-weight TTS. Its Bulbul is API-only.

### Cited Findings
**Veena (baseline)**
- `maya-research/Veena`: Apache-2.0, not gated, last modified 2025-10-05. Languages are en and hi only. The dataset field reads "proprietary". — [HF API](https://huggingface.co/api/models/maya-research/Veena)
- It is a 3B autoregressive model on a "Llama architecture backbone" with a SNAC 24 kHz codec. Speakers are kavya, agastya, maitri and vinaya. — [Veena card](https://huggingface.co/maya-research/Veena)
- There is no Veena v2. Maya Research's newer HF models are `maya1` (2026-10-13), `maya2-native` (2026-11-03) and `maya-transcribe`. — [HF author listing](https://huggingface.co/maya-research)
- Community MLX ports exist: `hashvibe007/Veena-mlx-4Bit` (Apache-2.0) and `theNoobCoder01/Veena-MLX-BF16`. GGUF ports also exist (Mungert, tensorblock). — [HF search](https://huggingface.co/models?search=veena)

**Maya 2 Native (new, by Veena's makers)**
- Apache-2.0, not gated. Languages: as, bn, en, gu, hi, kn, ml, mr, or, pa, ta, te. Base model is Qwen3-1.7B-Base. — [HF API](https://huggingface.co/api/models/maya-research/maya2-native)
- 2.50B parameters, about 5.0 GB of BF16 weights, 24 kHz output, streaming. It has 20 built-in voices plus zero-shot and cross-lingual cloning. Checkpoint 1.0 is dated 25 Oct 2026. — [Maya 2 Native card](https://huggingface.co/maya-research/maya2-native)
- Component licenses: Qwen3 is Apache-2.0, Kyutai Mimi codec is CC-BY-4.0, and SpeechBrain ECAPA is Apache-2.0. Training data is described only as "licensed and synthetic speech"; the dataset names are not disclosed. — [card](https://huggingface.co/maya-research/maya2-native)

**AI4Bharat models**
- `ai4bharat/IndicF5`: MIT, gated: auto, card modified 2026-10-06. — [HF API](https://huggingface.co/api/models/ai4bharat/IndicF5)
- `ai4bharat/indic-parler-tts`: Apache-2.0, gated: auto, card modified 2026-10-06. — [HF API](https://huggingface.co/api/models/ai4bharat/indic-parler-tts)
- Both cards now say Indic-Speak (22 languages) is available and recommend it over these models. — [IndicF5 card](https://huggingface.co/ai4bharat/IndicF5); [Indic Parler card](https://huggingface.co/ai4bharat/indic-parler-tts)
- Other AI4Bharat TTS: `ai4bharat/vits_rasa_13` (CC-BY-4.0, 13 languages including sa, Dec 2024) and `ai4bharat/bhili-tts` (MIT, Bhili only, a fine-tune of Indic Parler). — [HF API](https://huggingface.co/api/models/ai4bharat/vits_rasa_13)

**Indic-Speak (Bodhan AI / AI4Bharat)**
- `bodhan-ai/indic-speak`: license "other" (Indic Open Model License), gated: auto. Created 2026-08-31. Base model is meta-llama/Llama-3.2-3B. Covers 23 languages (22 Indic plus en, including sa). — [HF API](https://huggingface.co/api/models/bodhan-ai/indic-speak)
- Release coverage: launched Sept 2026 with NVIDIA, described as a "3.36B stack" with 45 voices and mixed native/Latin script input. The launch date differs between outlets (4 vs 12 Sept). I found no TTS quality benchmark in press coverage. — [Analytics Vidhya](https://www.analyticsvidhya.com/blog/2026/09/bodhan-ai-indic-models/); [Careers360](https://news.careers360.com/iit-madras-suite-of-open-ai-models-for-indic-languages-bodhan-ai)
- Hosted API pricing is ₹6 per 10k characters. That is not relevant here: the weights are free to self-host. — [Analytics Vidhya](https://www.analyticsvidhya.com/blog/2026/09/bodhan-ai-indic-models/)

**Svara (Kenpath; Orpheus-based)**
- `kenpath/svara-tts-v1`: Apache-2.0, not gated, released Oct 2025. Base is `canopylabs/3b-hi-ft-research_release` (Orpheus 3B). It covers 19 languages including sa, bho, mai and Indian English. — [Svara card](https://huggingface.co/kenpath/svara-tts-v1)
- `kenpath/svara-tts-voiceclone-beta`: Apache-2.0, Dec 2025, adds about 10 s reference-audio cloning. — [voiceclone card](https://huggingface.co/kenpath/svara-tts-voiceclone-beta)
- No Svara v2 was found. The newest Kenpath upload is an OpenVINO int4 build (Apr 2026). — [HF author listing](https://huggingface.co/kenpath)

**SPRINGLab (IIT Madras)**
- `SPRINGLab/SPRING_F5`: Apache-2.0, an F5-TTS fine-tune for 23 Indic languages plus English (includes sa). Trained on IndicVoices and Rasa. Updated 2026-11-15. Paper at AACL-IJCNLP 2026 workshop. — [SPRING_F5 card](https://huggingface.co/SPRINGLab/SPRING_F5)
- `SPRINGLab/Indic-Mio`: Apache-2.0, 0.6B (fine-tune of MioTTS-0.6B), 22 languages plus English, 44 kHz, "<0.1 RTF", zero-shot cloning via codec speaker embeddings. Updated May 2026. — [Indic-Mio card](https://huggingface.co/SPRINGLab/Indic-Mio)
- `SPRINGLab/F5-Hindi-24KHz`: CC-BY-4.0, Hindi only, Jan 2025 (older). — [HF API](https://huggingface.co/api/models/SPRINGLab/F5-Hindi-24KHz)

**Sarvam AI**
- None of Sarvam's open models is TTS. Its HF releases are LLMs (sarvam-30b, sarvam-105b, sarvam-m), translate, prism and shuka-1 (audio-to-text). `sarvamai/bulbul` returns not found / private. — [HF author listing](https://huggingface.co/sarvamai)
- Bulbul-V3 appears only as a commercial entry on the VoiceArena Hindi leaderboard. — [Maya 2 Native card citing VoiceArena](https://huggingface.co/maya-research/maya2-native)

**Other / legacy**
- `facebook/mms-tts-hin` and `facebook/mms-tts-mar` are **CC-BY-NC-4.0**, so they are excluded. — [HF API](https://huggingface.co/api/models/facebook/mms-tts-hin)
- SYSPIN VITS/HiFiGAN voices (for example `SYSPIN/tts_vits_coquiai_HindiFemale`) are CC-BY-4.0 and date from 2023. — [HF API](https://huggingface.co/api/models/SYSPIN/tts_vits_coquiai_HindiFemale)
- `Shivam6566/Samskriti-Svara` (VITS/MMS-based Sanskrit-branded model) is **CC-BY-NC-4.0**, so it is excluded. — [card](https://huggingface.co/Shivam6566/Samskriti-Svara)

### Inferences
- For this project, AI4Bharat's "current" model is now Indic-Speak, not IndicF5 or Indic Parler.
- Maya 2 Native is the natural successor to Veena: same team, many more languages, built-in cloning.
- I did not search for Bhashini-hosted models or for separate SPRING-INX TTS checkpoints. SPRINGLab's HF output above is the visible IIT Madras SPRING work.

### Gaps
- No Bhashini-released downloadable TTS weights were checked.
- I did not check the IIT Madras IndicTTS consortium's own FastPitch/HiFiGAN checkpoint licenses directly.
- The Indic-Speak model card itself (gated) could not be read. Its details come from the community MLX port's copy of upstream files.

## License, data, cloning, emotion, quality and Mac feasibility per model

### Takeaway
All the leading candidates allow commercial use of generated audio:
- Apache-2.0: Maya 2 Native, Svara, Indic Parler, SPRING_F5, Indic-Mio.
- MIT: IndicF5.
- Indic Open Model License: Indic-Speak. Self-hosted commercial use is allowed, hosting it for third parties needs approval, and attribution applies when the software is made available.

The main license traps:
1. Llama-3.2-derived models (Indic-Speak, Svara via Orpheus) also carry the Llama 3.2 Community License.
2. Indic-Mio used Expresso, which is CC-BY-NC.
3. IndicVoices-R has a conflicting data license: CC-BY-4.0 on HF vs CC BY-ND 4.0 on AIKosh.

On a 16 GB Mac, the easiest high-quality options are Indic-Speak MLX 4-bit and Svara MLX 4-bit (both about 1.9 GB). Maya 2 Native is officially CUDA-only.

### Cited Findings

**Indic-Speak**
- **License (Indic Open Model License v1.0)**:
  - It grants worldwide, royalty-free rights to "use, reproduce, … sell, deploy, fine-tune" (§1).
  - Its stated intent covers "commercial use at any scale" when self-hosted.
  - The main restriction is giving third parties hosted/API access (§3).
  - Products above 500M MAU or US$250M revenue need a separate license (§14).
  - Prohibited uses include impersonating a real person's voice without consent and disinformation (§10).
  - The attribution notice "Built with [Model Name] from Bodhan AI / AI4Bharat" is required when the Software or a Derivative is Made Available (§2). Attribution is not required for Internal Use.
  - "Output" explicitly includes synthesized audio. You must indemnify the licensor against claims arising from your Output (§11.5).
  - — [License text](https://raw.githubusercontent.com/Bodhan-AI/bodhan-model-info/main/licenses/indic-open-model-license/v1/Indic_Open_Model_License.md)
- **Llama 3.2**: the MLX port notes that the upstream is "built on Llama 3.2 and subject to the Llama 3.2 Community License". — [indic-speak-mlx-4bit card](https://huggingface.co/iniquitous/indic-speak-mlx-4bit)
- **Voices**: 44 first-party voices from the "full Rasa studio roster", one female and one male per language plus a second Hindi female. Every voice can speak every language.
  - Recommended per language: Hindi Kavya/Amit, Marathi Anagha/Chinmay, Bengali Ishita/Sourav, Telugu Sravani/Vamsi, Tamil Anitha/Arun, Gujarati Dhara/Parth, Kannada Deepika/Adarsh, Malayalam Lakshmi/Kiran, Punjabi Kaur/Manpreet, Sanskrit Bharati/Aryaman.
  - The library median rate is about 12 chars/sec.
  - — [voices.md in MLX port](https://huggingface.co/iniquitous/indic-speak-mlx-4bit/raw/main/voices.md)
- **Emotion**: uppercase emotion style tags (ANGER, HAPPY, SAD, FEAR …). Lowercase delivery tags such as "educational lecture" are less reliable. Selection is by `speaker_id` plus `style`, with a seed parameter. — [MLX card](https://huggingface.co/iniquitous/indic-speak-mlx-4bit)
- **Mac**:
  - 4-bit MLX LM weights are 1.8 GB.
  - Speed on an M3 Max: 75–83 tok/s, RTF about 1.0–1.2. Speed drops about 25% when the chip throttles.
  - Quantized variants "tend to stop early or drift on multi-sentence prompts", so use the sentence-chunked `speak_long`.
  - A RoPE config patch is needed if you convert the model yourself.
  - Quality was checked on Hindi only by listening and statistics, not by WER or MOS.
  - — [MLX card](https://huggingface.co/iniquitous/indic-speak-mlx-4bit)
  - ONNX int8 ports also exist (`adidsh/indic-speak-int8-onnx`). — [HF search](https://huggingface.co/models?search=indic-speak)
- **Architecture**: SNAC plus a Bodhan fine-tuned Vocos decoder. This is the same codec family as Veena, so the Veena integration code is likely reusable. — [MLX card](https://huggingface.co/iniquitous/indic-speak-mlx-4bit)

**Maya 2 Native**
- **Quality (authors' benchmark, ASR CER, scorer v1, ASR-1)**: hi 1.52%, mr 1.66%, bn 2.60%, te 2.29%, kn 2.28%, pa 2.51%, ml 3.75%, ta 4.42%. Voice identity is 98–99.6% for most languages. Consensus failure rate is 0.15%, mean ECAPA similarity 0.778. No human MOS study was reported. — [card](https://huggingface.co/maya-research/maya2-native)
- **VoiceArena (as reported on the card, checked 3 Nov 2026)**: #2 for Hindi among real-time models (Elo 1047), ahead of Sarvam Bulbul-V3 (957). It is #7 in the all-model Hindi view. — [card](https://huggingface.co/maya-research/maya2-native); leaderboard: [VoiceArena Hindi](https://voicearena.com/tts-leaderboard/hindi) (not independently re-checked)
- **Cloning**: 3–10 s reference clip plus exact transcript (`register_voice`), mode `icl_spk`. It "approximates" the reference voice; no cloning score is reported. — [card](https://huggingface.co/maya-research/maya2-native)
- **Limits stated by the authors**:
  - Emotion tags ([laughs], [sad], [excited]) are "best effort".
  - 1–2-word prompts are less stable in voice identity.
  - Assamese drifts toward a Bengali-like timbre.
  - Voices: 10 multilingual voices with ≥1 h in bn/en/gu/hi/kn/ml/mr/or/(pa)/ta/te (for example Malini and Vasant are "steady narrator" voices). Several voices are Hindi-only.
  - — [card](https://huggingface.co/maya-research/maya2-native)
- **Hardware**: Linux plus NVIDIA CUDA 12.8 only. One seat needs 7.7 GB steady and 9.2 GB peak. "This card does not establish CPU, Apple MPS or browser inference support." — [card](https://huggingface.co/maya-research/maya2-native)

**IndicF5**
- 0.4B parameters, F32, 11 languages (as, bn, gu, hi, kn, ml, mr, or, pa, ta, te).
- It **requires a reference clip plus its transcript** for every generation. This is the cloning approach, and it is good for keeping one fixed speaker.
- Trained on about 1,417 h from Rasa, IndicTTS, LIMMITS and IndicVoices-R.
- No MOS or CER published on the card.
- Terms: "only clone voices for which you have explicit permission."
- — [IndicF5 card](https://huggingface.co/ai4bharat/IndicF5)

**Indic Parler-TTS**
- 0.9B parameters. Voice and style are set by a text description. 69 named speakers; naming the speaker improves consistency.
- Recommended speakers: Hindi Rohit/Divya, Marathi Sanjay/Sunita, Bengali Arjun/Aditi, Telugu Prakash/Lalitha, Tamil Jaya, Gujarati Yash/Neha, Kannada Suresh/Anu, Malayalam Anjali/Harish, Punjabi Divjot/Gurpreet, Sanskrit Aryan, English Thoma/Mary.
- 12 emotions are officially supported in 10 languages (as, bn, brx, doi, kn, ml, mr, sa, ne, ta).
- Native Speaker Score (finetuned): hi 84.8, mr 77.0, bn 86.2, te 88.5, ta 75.5, gu 75.4, kn 88.2, ml 86.5, sa 99.8.
- Data: GLOBE (535 h), IndicTTS (382 h, CC BY 4.0), LIMMITS (568 h, CC BY 4.0), Rasa (288 h, CC BY 4.0).
- — [Indic Parler card](https://huggingface.co/ai4bharat/indic-parler-tts)
- The GLOBE source dataset (`MushanW/GLOBE`) is CC0-1.0. — [HF API](https://huggingface.co/api/datasets/MushanW/GLOBE)

**Svara**
- About 2000 h from SYSPIN, Rasa, IndicTTS and SPICOR, about 50 speakers.
- Speaker IDs use a "Language (Gender)" format (for example "Marathi (Male)"). This gives only one voice per language and gender.
- Emotion tags go at the end of a sentence (<happy>, <sad>, <anger>, <fear>, <clear>).
- No benchmarks published.
- — [Svara card](https://huggingface.co/kenpath/svara-tts-v1)
- The MLX 4-bit port is about 1.9 GB (down from about 13.2 GB bf16) and runs with mlx-audio. — [mlx-community/svara-tts-v1-4bit](https://huggingface.co/mlx-community/svara-tts-v1-4bit)
- GGUF builds are available (mradermacher, prasanacodes). — [HF search](https://huggingface.co/models?search=svara)

**Indic-Mio**
- Trained on IndicTTS, Rasa and Syspin (Indic), LibriTTS and **Expresso** (English), and SPICOR (Indian English).
- Emotion tags: <happy>, <sad>, <angry>, <disgust>, <fear>, <surprise> for Indic languages. Words can be stressed with *word*.
- — [Indic-Mio card](https://huggingface.co/SPRINGLab/Indic-Mio)
- Expresso is **CC-BY-NC-4.0**. — [HF API](https://huggingface.co/api/datasets/ylacombe/expresso)

**Dataset licenses (HF metadata)**
- Rasa, IndicVoices and IndicVoices-R are listed as CC-BY-4.0, gated: auto. — [HF API Rasa](https://huggingface.co/api/datasets/ai4bharat/Rasa); [indicvoices_r](https://huggingface.co/api/datasets/ai4bharat/indicvoices_r)
- AIKosh lists IndicVoices-R as CC BY-ND 4.0, which conflicts with HF. — [AIKosh](https://aikosh.indiaai.gov.in/home/datasets/details/indicvoices_r.html) (via search result)

**Community comparisons (weak evidence)**
- One Hinglish build log ranked by a single ASR system: Kokoro 3.03 > Indic Parler 2.73 > IndicF5 1.97. The author says listening changed the picture. — [harrrshall blog](https://harrrshall.github.io/hinglish-tts/)
- An aggregator claims Indic Parler MOS 4.5 / WER 5.2%. The method is unverified. — [aiindigo](https://aiindigo.com/blog/indic-parler-tts-review-high-fidelity-voice-synthesis-for-indian-languages)
- No Reddit or real-world reports on Svara, Veena or Indic-Speak were found.

### Inferences
- **Commercial YouTube use**:
  - Publishing generated audio is not "Distributing" or "Hosting" the Software under the Indic Open Model License, so self-hosted Indic-Speak narration on monetized YouTube appears permitted.
  - Adding "Built with Indic-Speak from Bodhan AI / AI4Bharat" to video descriptions costs nothing and avoids ambiguity.
  - The Llama 3.2 license, which applies to Indic-Speak and Svara and possibly to Veena if it was initialized from Llama weights, allows commercial use under 700M MAU. Its obligations mainly bite when you distribute the model.
- **Data licenses**: CC-BY-4.0 training data (Rasa, IndicTTS, LIMMITS, SYSPIN) does not normally restrict the outputs of a trained model. The IndicVoices-R ND conflict is a low but nonzero risk for IndicF5 and SPRING_F5.
- **Indic-Mio**: because it used CC-BY-NC Expresso data, it is the riskiest of the Apache-labelled models for monetized use. Avoid it, or at least avoid its English voices.
- **Running on a 16 GB M5 Air**:
  - Indic-Speak 4-bit MLX: about 1.8 GB LM plus SNAC/Vocos. It should fit easily. A fanless Air will likely sit below the M3 Max's RTF 1.0–1.2, so expect roughly 1.5–2.5× real time. This is an estimate, not measured.
  - Svara MLX: similar to Indic-Speak.
  - IndicF5, SPRING_F5 and Indic Parler: small (0.4–0.9B), PyTorch MPS/CPU feasible.
  - Maya 2 Native: about 5 GB BF16 could fit in memory, but needs an unofficial MPS port of its custom engine. That is risky.

### Gaps
- No independent MOS comparison across Indic-Speak, Maya 2 Native, Svara and IndicF5.
- No measured Apple Silicon speeds for IndicF5, Parler or Maya 2 Native.
- Whether Veena was initialized from Meta Llama weights (which would trigger the Llama license) is not stated on its card.
- Indic-Speak's own benchmark figures are not visible (gated card).

## Which handles Sanskrit/shlokas well?

### Takeaway
Indic Parler-TTS has the only published Sanskrit quality number: Native Speaker Score 99.8%, speaker "Aryan", with Sanskrit emotion support. Indic-Speak has dedicated Rasa Sanskrit voices (Bharati/Aryaman). Svara, SPRING_F5 and Indic-Mio list Sanskrit. Maya 2 Native and IndicF5 do **not** support Sanskrit. No model has a published evaluation of metrical/chanted shloka recitation.

### Cited Findings
- Indic Parler Sanskrit NSS is 99.71 pretrained and 99.79 finetuned, the highest of any language. Recommended speaker is Aryan. Sanskrit is among its officially emotion-supported languages. — [Indic Parler card](https://huggingface.co/ai4bharat/indic-parler-tts)
- Indic-Speak has Sanskrit voices Bharati (F) and Aryaman (M). — [voices.md](https://huggingface.co/iniquitous/indic-speak-mlx-4bit/raw/main/voices.md)
- Svara lists `sa`. — [Svara card](https://huggingface.co/kenpath/svara-tts-v1)
- SPRING_F5 lists Sanskrit. — [SPRING_F5 card](https://huggingface.co/SPRINGLab/SPRING_F5)
- `vits_rasa_13` includes `sa`. — [HF API](https://huggingface.co/api/models/ai4bharat/vits_rasa_13)
- Maya 2 Native's language list has no `sa`. — [card](https://huggingface.co/maya-research/maya2-native)
- IndicF5's 11 languages exclude Sanskrit. — [IndicF5 card](https://huggingface.co/ai4bharat/IndicF5)
- Sanskrit-specific community models found (`rverma0631/Sanskrit_TTS`, `gnumanth/sanskrit-tts-onnx`) have essentially no downloads. Samskriti-Svara is NC. — [HF search](https://huggingface.co/models?search=sanskrit%20tts); [Samskriti-Svara](https://huggingface.co/Shivam6566/Samskriti-Svara)

### Inferences
- The near-perfect Parler NSS score probably reflects read-speech Sanskrit (Rasa/IndicTTS-style recordings). It should not be taken as evidence of chanting with correct meter, svara or pauses at the caesura.
- A practical approach for shlokas inside Hindi narration: generate the verse in a Sanskrit voice (Indic-Speak Aryaman/Bharati, or Parler Aryan) as a separate clip. Alternatively, keep the Hindi narrator voice for both, and let a reference-cloned model carry the narrator's identity into the verse. This needs testing.

### Gaps
- No published test of anusvara/visarga handling, sandhi-heavy compounds or chandas meter for any model.

## Recommendation per language, fallback, and what to test

### Takeaway
1. **Primary candidate to test against Veena for every language:** Indic-Speak (MLX 4-bit, native voice per language). It is AI4Bharat's endorsed successor, covers all target languages plus Sanskrit, uses the same SNAC codec family as Veena, and has a working Apple Silicon port.
2. **First fallback:** IndicF5 for reference-locked speaker identity (11 languages, MIT, small). Svara (MLX) is another fallback for expressive tags.
3. **Watch:** Maya 2 Native. Its published metrics are the best, but it needs CUDA (or a future MPS/MLX port).

### Cited Findings
Each language uses the voice names from the cited cards. CER figures are Maya 2 Native's own benchmark.

| Language | Primary (Indic-Speak voices, F / M) | Fallback | Other evidence |
|---|---|---|---|
| Hindi | Kavya / Amit | Veena kavya (current), IndicF5 with a fixed reference clip | Maya 2 CER 1.52% |
| Marathi | Anagha / Chinmay | IndicF5; Parler Sanjay/Sunita | Parler NSS only 77.0. Maya 2 CER 1.66% |
| Bengali | Ishita / Sourav | IndicF5; Parler Arjun/Aditi | Parler NSS 86.2 |
| Telugu | Sravani / Vamsi | IndicF5; Parler Prakash/Lalitha | Parler NSS 88.5 |
| Tamil | Anitha / Arun | IndicF5; Parler Jaya | Weakest across sources: Parler NSS 75.5, Maya 2 CER 4.42% |
| Gujarati | Dhara / Parth | IndicF5; Parler Yash/Neha | Parler NSS 75.4 |
| Kannada | Deepika / Adarsh | IndicF5; Parler Suresh/Anu | Parler NSS 88.2 |
| Malayalam | Lakshmi / Kiran | IndicF5; Parler Anjali/Harish | Parler NSS 86.5. Maya 2 CER 3.75% |
| Punjabi | Kaur / Manpreet | IndicF5; Parler Divjot/Gurpreet | Parler marks Punjabi as unofficial in one section |
| Indian English | Any Indic-Speak voice cross-lingually | Parler Thoma/Mary; Svara "English (Indian)" | — |
| Sanskrit | Aryaman / Bharati | Parler Aryan (NSS 99.8) | — |

Sources: [voices.md](https://huggingface.co/iniquitous/indic-speak-mlx-4bit/raw/main/voices.md); [Indic Parler card](https://huggingface.co/ai4bharat/indic-parler-tts); [Maya 2 Native card](https://huggingface.co/maya-research/maya2-native); [Svara card](https://huggingface.co/kenpath/svara-tts-v1)

### Inferences
**What to test (an A/B harness that can plug into the existing QA `speaker_consistency` check):**
1. **Speaker drift across 20+ separate calls with the same voice and seed.** Measure ECAPA cosine similarity to a reference clip. Maya reports a mean of 0.778 and 98.6% closed-set identity as a yardstick. Compare Indic-Speak (seeded `speaker_id`), IndicF5 (fixed reference plus transcript) and Veena-with-priming.
2. **Aspirated consonants and first-word onset** (Veena's known weak spot). Use a minimal-pair script (क/ख, ग/घ, च/छ, ज/झ, ट/ठ, ड/ढ, त/थ, द/ध, प/फ, ब/भ). Put the sentence-initial word on an aspirate, and check for clipped first syllables after leading silence is trimmed.
3. **Long-script stability.** The quantized Indic-Speak is known to stop early or drift on multi-sentence input, so always chunk by sentence (। . ! ?) and use repetition penalty 1.2.
4. **Emotion tags.** Test Indic-Speak `style=SAD/HAPPY/FEAR`, Svara <sad>, and Parler descriptions on a dramatic Ramayana passage.
5. **Sanskrit verse.** Use 2–3 shlokas (anusvara, visarga, conjuncts). Compare Indic-Speak Aryaman, Parler Aryan and Svara "Sanskrit".
6. **Throughput on the M5 Air.** Measure RTF and peak RSS one model at a time, per the project memory rule.
7. **Licensing housekeeping.** Accept the gated terms for Indic-Speak, IndicF5 and Parler (requires an HF login). Add the Bodhan attribution line to descriptions if Indic-Speak is adopted. Avoid MMS, Samskriti-Svara and Indic-Mio for monetized output.

**Why not switch to Maya 2 Native now:** it has the best evidence, but it officially requires Linux plus CUDA. Running it on Apple Silicon would mean porting its custom engine (Qwen3 backbone plus 555M depth decoder plus Mimi). That is worth revisiting if an MLX port appears.

### Gaps
- None of the recommendations above has been verified by listening on this hardware. They rest on model cards and coverage, not on comparative audio tests.
- Dialect and accent naturalness within each language (for example Marathi Varhadi vs Puneri, Bengali Kolkata vs Dhaka) is not evaluated by any source found.
