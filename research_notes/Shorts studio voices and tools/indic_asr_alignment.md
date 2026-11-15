# Open ASR, forced alignment and pronunciation QA for Indian languages (as of Nov 2026)

Scope: free, local, commercially usable tools for (a) TTS pronunciation verification (transcribe narration, compare to script) and (b) word-level timestamps for burned-in subtitles, on a MacBook Air M5 16 GB (no NVIDIA GPU). Languages: hi, mr, bn, te, ta, gu, kn, ml, pa, Sanskrit verses, English. Baseline: faster-whisper large-v3-turbo (hi) / small (en).

## Q1. Best Indic ASR options: accuracy, licenses, Apple Silicon feasibility

### Takeaway
For Indic verification ASR, the strongest commercially usable open options are AI4Bharat IndicConformer-600M-multilingual (MIT, 22 languages, CTC+RNNT) and the newer Bodhan AI / AI4Bharat Indic-Transcribe-core (Canary-1B-v2 based, 25 languages incl. Sanskrit, custom "Indic Open Model License" that allows commercial use with conditions). Both beat Whisper by a wide margin on independent Indic benchmarks. IISc SraVaani-1.0 (MIT, 65 languages, Aug 2026) is a promising third option. Meta Omnilingual ASR is Apache-2.0 but much weaker on Indic than IndicConformer. Sarvam's ASR models are API-only (not open), and the NVIDIA Parakeet Indic variant is under a restrictive NVIDIA license.

### Cited Findings
**AI4Bharat IndicConformer-600M-multilingual**
- License MIT; covers 22 scheduled Indian languages; hybrid CTC + RNNT Conformer; called as `model(wav, "hi", "ctc")` or `"rnnt"`; loads via `transformers` `AutoModel.from_pretrained(..., trust_remote_code=True)`, needs torchaudio, example pins onnxruntime 1.20.1; 16 kHz mono; HF repo is gated (accept terms + login). Card reports Hindi WER 13.2 on ARTPARK-IISc Vaani-Benchmark-V1.0. Card now recommends "Indic-Transcribe" as higher quality. — [HF model card](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual); MIT also listed by [AI4Bharat GitHub](https://github.com/AI4Bharat/IndicConformerASR) and [AIKosh](https://aikosh.indiaai.gov.in/home/models/details/aibharat_indicconformer_600m_multi.html)
- On the Voice of India benchmark (JoshTalks + AI4Bharat + IIT Madras; 15 languages, 536 h of unscripted telephonic speech, private test set), IndicConformer scored OI-WER Hindi 8.2, Urdu 8.1, Bengali 10.7; weakest Malayalam 25.9, Maithili 24.7, Telugu 23.7. It was described as competitive with proprietary APIs on hi/bn/ur; Sarvam's API models hold most best scores. Whisper large-v3 was not on the leaderboard. — [Voice of India blog, Apr 2026](https://voiceofindiablogs.ai.joshtalks.com/)
- A CoreML conversion (RNNT heads for hi, bn, mr, te, ta, ml, kn; MIT tag) exists for macOS local inference; fixed 1024-mel-frame encoder windows (must chunk), mostly no punctuation, no language ID, no timestamp support mentioned, no speed numbers published. — [phequals CoreML conversion](https://huggingface.co/phequals/indic-conformer-600m-multilingual-coreml-rnnt)
- Third-party Hindi fine-tune of IndicConformer reports 12.09% avg WER with 5-gram KenLM (14.14% greedy) across read/noisy/broadcast/conversational/rural Hindi; licensed Apache-2.0 by its uploader (not official). — [Abhay-Verma031/indic-conformer-600m](https://huggingface.co/Abhay-Verma031/indic-conformer-600m)

**Indic-Transcribe-core (Bodhan AI, credits AI4Bharat), released 5 Sep 2026**
- Base nvidia/canary-1b-v2 (FastConformer encoder + Transformer decoder), ~1.2B params; 25 languages: Indian English, as, bn, brx, doi, gu, hi, kn, ks, kok, mai, ml, mni, mr, ne, or, pa, **sa (Sanskrit)**, sat, sd, ta, te, ur, Bhojpuri, Bhili. Runs via plain torch/transformers (`IndicTranscribe` class shipped in repo) or NeMo; 16 kHz mono; single pass limited to 45 s (chunked helper for longer). No timestamp output mentioned. — [HF card](https://huggingface.co/bodhan-ai/indic-transcribe-core)
- License: "Indic Open Model License v1.0", gated; card says "ready for commercial use"; conditions include attribution, share-alike for derivatives, written approval before offering as a hosted API, and a separate license above 500M MAU / $250M revenue; base Canary license terms also apply. — [HF card](https://huggingface.co/bodhan-ai/indic-transcribe-core)
- Vendor-reported OI-WER on Voice of India: average 8.7 (vs Saaras V3 10.7, Indic-Transcribe-flex 11.3). Per language: hi 3.5, bn 4.3, mr 5.7, ur 5.0, kn 7.4, pa 8.3, ta 9.0, gu 9.2, te 11.4, ml 11.5. — [HF card](https://huggingface.co/bodhan-ai/indic-transcribe-core) (vendor claim, not independently verified)
- A sibling "Indic-Transcribe-flex" is also described as commercially usable. — [HF](https://huggingface.co/spark-ux/indic-transcribe-flex)

**SraVaani (ARTPARK / IISc)**
- SraVaani-1.0: ~430M params, FastConformer encoder with hybrid TDT + CTC decoder, 65 Indian languages/dialects (incl. hi, bn, kn, mr, ta, te; not Urdu/Kashmiri), ~31k h transcribed fine-tuning data; MIT on HF but gated; paper arXiv 2608.08235 (Aug 2026). Best accuracy on 10 of 17 compared languages and lowest mean WER on that set (tables not reproduced in the article). — [LetsDataScience news, Aug 2026](https://letsdatascience.com/news/iisc-team-releases-sravaani-asr-for-65-indian-languages-a6aa9c5b)
- SraVaani-0.5-live: streaming cache-aware FastConformer CTC, 63 Indian languages incl. Sanskrit, loads with transformers `trust_remote_code=True`. — [HF](https://huggingface.co/ARTPARK-IISc/SraVaani-0.5-live)

**AI4Bharat IndicWhisper (Vistaar)**
- Vistaar repo states MIT license covering all fine-tuned models. IndicWhisper had lowest WER on 39 of 59 benchmarks (avg -4.1 WER). Per-language average WER ranges from 13.6 (Hindi) to 48 (Sanskrit); overall ~24.6 (table column alignment in extracted text was unclear). Benchmarks are from 2023 (older). — [Vistaar GitHub](https://github.com/AI4Bharat/vistaar); [Vistaar paper arXiv 2305.15386](https://arxiv.org/pdf/2305.15386)

**Whisper fine-tunes**
- vasista22/whisper-hindi-large-v2: Apache-2.0; model-index WER 10.98 on FLEURS hi_in; Collabora blog claims ~5% on FLEURS (conflicting; eval setups differ). A derived fine-tune reports the base at 23.52% WER on IndicVoices-R Hindi. Telugu and Tamil siblings exist. CT2 int8 conversion exists for faster-whisper. — [HF card](https://huggingface.co/vasista22/whisper-hindi-large-v2/blob/main/README.md); [Collabora](https://www.collabora.com/news-and-blog/news-and-events/breaking-language-barriers-20-moving-closer-production-ready-hindi-asr.html); [CT2 int8](https://huggingface.co/digikar/vasista22-whisper-hindi-large-v2-ct2-int8/tree/main)
- An HF discussion reports poor performance of this model under whisper.cpp / faster-whisper. — [HF discussion](https://huggingface.co/vasista22/whisper-hindi-large-v2/discussions/6)

**Meta Omnilingual ASR (Nov 2025)**
- Apache-2.0 code and models (data CC-BY); 1,600+ languages; 78% of languages CER < 10%. — [Meta AI blog](https://ai.meta.com/blog/omnilingual-asr-advancing-automatic-speech-recognition/); [VentureBeat](https://venturebeat.com/ai/meta-returns-to-open-source-ai-with-omnilingual-asr-models-that-can)
- Variants: CTC 300M/1B/3B/7B (+v2), LLM 300M–7B (+v2), "LLM Unlimited v2" for long audio; CTC/LLM accept only < 40 s audio; VRAM at 30 s BF16 on A100: CTC ~2 GiB (300M) to ~15 GiB (7B); no CPU/MPS guidance; no timestamp/alignment feature documented; language codes like `eng_Latn`. — [GitHub](https://github.com/facebookresearch/omnilingual-asr)
- On Voice of India, OmniASR LLM 7B: Hindi 13.7, Bengali 22.8, Telugu 50.7, Malayalam 52.0, Odia 72.6 OI-WER — far behind IndicConformer. Google Gemma E4B (open) scored Hindi 11.2 but Malayalam 47.6. — [Voice of India blog](https://voiceofindiablogs.ai.joshtalks.com/)

**NVIDIA / Sarvam / others**
- NVIDIA Parakeet RNNT 1.1B collection includes an "Indic" variant (4 Indic languages), governed by the NVIDIA AI Foundation Models Community License (not a standard open license). — [NGC collection](https://catalog.ngc.nvidia.com/orgs/nvidia/collections/parakeet-1-1b-rnnt-multilingual)
- Sarvam Saaras V4 (22 languages) is API-only (paid per minute after free credits); Sarvam's open weights are its 30B/105B LLMs, not ASR. Sarvam + AI4Bharat released Indic DiarBench dataset (CC BY 4.0). — [Sarvam blog](https://www.sarvam.ai/blogs/introducing-saaras-v4); [CIOL](https://www.ciol.com/news/sarvam-launches-open-weight-ai-models-built-for-multilingual-india-11189014); [NewsBytes](https://www.newsbytesapp.com/news/science/sarvam-ai-launches-indic-diarbench-an-open-benchmark-dataset/story)
- Public FLEURS rankings do not reliably predict Voice of India performance; Tamil/Malayalam/Telugu/Kannada error rates are 2–4x Hindi across almost all systems. — [Voice of India blog](https://voiceofindiablogs.ai.joshtalks.com/)

### Inferences
- For TTS QA of clean studio narration (much easier than telephonic speech), IndicConformer CTC (600M, MIT) is the safest default: unambiguous license, all 9 target Indic languages, small enough for CPU/MPS on 16 GB, and its CTC head can double as a forced aligner (see Q2). Indic-Transcribe-core is likely more accurate (and covers Sanskrit) but its share-alike/hosted-API conditions should be read in full before adoption; for internal QA use it appears permissible.
- Because these models are trained on Indic speech with native orthography, they should confuse aspirated pairs (थ/त, ध/द) less than Whisper; this is an expectation, not measured for TTS audio. A small local A/B on existing Veena narrations vs. scripts is the right check.
- Running on Apple Silicon: the PyTorch paths should run on CPU (and possibly MPS) at 600M–1.2B params within 16 GB; must be run sequentially with TTS per the memory rule. No published M-series speed numbers were found.
- Keep faster-whisper small/turbo for English; Indic-Transcribe-core also covers Indian-accented English.

### Gaps
- No independent WER for IndicConformer on clean read/TTS speech per language; no M-series RTF measurements for any Indic model.
- SraVaani-1.0 per-language WER tables (arXiv 2608.08235) not retrieved.
- Bhashini model licensing not researched (no reliable source found within budget).
- Whether NVIDIA released an openly licensed (CC-BY) Indic Parakeet/Canary on HF in 2026 not confirmed; Nemotron 3.5 ASR (OpenMDW license) claim came from a non-authoritative blog.
- MLX ports of Indic models: none found.

## Q2. Forced alignment for exact word timing with a known script

### Takeaway
Use CTC forced alignment (Viterbi over a CTC model's log-probs given the script) rather than ASR word timestamps. The popular default model (MMS-300M forced aligner / torchaudio MMS_FA) is CC-BY-NC, so it is not allowed under the commercial constraint. Commercially clean routes: ctc-forced-aligner (BSD code) or NeMo Forced Aligner driven by a permissively licensed Indic CTC model (IndicConformer CTC head, MIT; Omnilingual CTC 300M, Apache-2.0; or SraVaani CTC, MIT). WhisperX only ships Indic align models for hi/te/ml/ur.

### Cited Findings
- ctc-forced-aligner package code is BSD-licensed, but its default model is CC-BY-NC 4.0; the HF checkpoint `MahmoudAshraf/mms-300m-1130-forced-aligner` is cc-by-nc-4.0. The tool accepts a custom `--alignment_model` with native vocabulary. — [PyPI](https://pypi.org/project/ctc-forced-aligner/); [GitHub](https://www.github.com/MahmoudAshraf97/ctc-forced-aligner); [HF checkpoint](https://huggingface.co/MahmoudAshraf/mms-300m-1130-forced-aligner)
- A CoreML port of MMS-FA inherits Meta's MMS non-commercial terms and recommends a commercial alternative for production. — [chordai CoreML MMS-FA](https://huggingface.co/chordai/mms-fa-aligner-coreml)
- torchaudio `functional.forced_align` was deprecated in 2.8 with removal announced for 2.9 as torchaudio moves to maintenance; 2.9.0 docs still show it with a deprecation warning (actual removal status unclear). Replacement points to `Wav2Vec2FABundle`, which calls the same code path. — [torchaudio 2.8 forced_align](https://docs.pytorch.org/audio/2.8.0/generated/torchaudio.functional.forced_align.html); [2.9 multilingual tutorial](https://docs.pytorch.org/audio/2.9.0/tutorials/forced_alignment_for_multilingual_data_tutorial.html)
- NeMo Forced Aligner (NFA) produces token-, word- and segment-level timestamps from CTC log-probs via Viterbi; an Indian-language dataset paper used NFA with IndicConformer models and noted alignment degrades on very long sequences. — [arXiv 2411.04699](https://arxiv.org/pdf/2411.04699)
- WhisperX default align models: en → torchaudio WAV2VEC2_ASR_BASE_960H; hi → `theainerd/Wav2Vec2-large-xlsr-hindi`; te → `anuragshas/wav2vec2-large-xlsr-53-telugu`; ml → `gvs/wav2vec2-large-xlsr-malayalam`; ur → `kingabzpro/...Urdu`. No defaults for mr, bn, ta, gu, kn, pa. — [whisperX alignment.py](https://raw.githubusercontent.com/m-bain/whisperX/main/whisperx/alignment.py)
- Parseh `aligner-hi`: CTC network derived from AI4Bharat IndicWav2Vec Hindi that aligns known Hindi caption text to 16 kHz audio and outputs word/char spans (license not confirmed). — [HF](https://huggingface.co/parseh/aligner-hi)
- Omnilingual ASR CTC 300M (Apache-2.0) is listed by a third-party subtitle tool as an alignment model option for 1600+ languages (not verified on Meta's page); Omnilingual's own repo documents no alignment feature and a 40 s input cap. — [MioSub docs](https://gemini-subtitle-pro.vercel.app/en/docs/guide/alignment); [Omnilingual GitHub](https://github.com/facebookresearch/omnilingual-asr)
- A 2026 paper on multilingual word-level forced alignment compares against MFA and CTC-based MMS alignment (on English data). — [arXiv 2606.10675](https://arxiv.org/pdf/2606.10675)

### Inferences
- Recommended stack: run IndicConformer (or SraVaani) in CTC mode to get frame log-probs, then align the script's tokenization with `torchaudio.functional.forced_align` (pin torchaudio ≤ 2.9 if needed) or NFA / ctc-forced-aligner's alignment utilities using that model's vocabulary. Per-segment alignment (one subtitle scene or sentence at a time, < 30–40 s) avoids long-sequence degradation and fits the existing scene structure.
- For English, the WhisperX torchaudio wav2vec2 base model is fine (torchaudio pipelines for WAV2VEC2_ASR_BASE_960H are generally BSD/MIT-trained on LibriSpeech; license not re-verified here).
- WhisperX's Hindi/Telugu/Malayalam community xlsr models have unverified licenses and are older; treat as fallback only.
- Number handling: normalise script digits to spoken words (indic-numtowords) before alignment so tokens match the audio, then map back to display text for subtitles.

### Gaps
- Montreal Forced Aligner Indic acoustic models/dictionaries and aeneas (TTS-based alignment) were not researched within budget; aeneas is believed to be AGPL (unverified).
- No accuracy comparison (ms error) of Indic CTC aligners was found.
- License of `theainerd/Wav2Vec2-large-xlsr-hindi` and IndicWav2Vec not confirmed here.

## Q3. Pronunciation scoring beyond CER (phoneme-level, aspiration-sensitive)

### Takeaway
No off-the-shelf open Indic TTS pronunciation-assessment model was found. The practical approach is: (1) fix metric inflation via Indic-aware normalization (number words, nukta, matras) or AI4Bharat's open OI-WER lattice metric; (2) add a phoneme/character-level check using a universal phoneme recognizer (wav2vec2-xlsr-53-espeak-cv-ft, IPA output) or the CTC posteriors of an Indic model aligned to the script (Goodness-of-Pronunciation style) to flag specific aspirated/retroflex substitutions.

### Cited Findings
- The same number can validly appear as words, Arabic digits or Devanagari digits; standard WER treats them as different. AI4Bharat's OI-WER scores against a lattice of valid variants (spellings, nukta on/off, numerics, code-mixing); open source at github.com/AI4Bharat/OIWER-Orthographically-Informed-Benchmarking-for-ASR. — [Voice of India blog](https://voiceofindiablogs.ai.joshtalks.com/)
- Whisper's default text normalizer is flawed for Indic scripts: stripping matras and virama inflates word counts and distorts WER. — [arXiv 2409.02449](https://arxiv.org/pdf/2409.02449v4.pdf)
- `indic-numtowords` (PyPI) converts numbers to words for Indian languages and English; used as a normalization convention in a 2026 voice pipeline paper. A separate `hindi-normalize` library maps Hindi number words to digits. — [arXiv 2609.20504](https://arxiv.org/pdf/2609.20504); [DEV Community post](https://dev.to/tushar9802/whisper-transcribes-spoken-hindi-numbers-as-words-not-digits-so-i-made-a-library-to-convert-them-3m95)
- facebook/wav2vec2-xlsr-53-espeak-cv-ft: XLSR-53 fine-tuned on multilingual Common Voice with eSpeak phoneme labels, outputs IPA, from "Simple and Effective Zero-shot Cross-lingual Phoneme Recognition". License reported as Apache-2.0 by one aggregator and MIT by another (official card not confirmed). — [HF](https://huggingface.co/facebook/wav2vec2-xlsr-53-espeak-cv-ft); [paper](https://ar5iv.labs.arxiv.org/html/2109.11680); [PromptLayer](https://www.promptlayer.com/models/wav2vec2-xlsr-53-espeak-cv-ft)
- A 2026 multilingual dysarthric-speech assessment paper uses this universal phone recognizer plus language-specific phonemic contrast modeling — the same pattern applicable to aspiration contrasts. — [arXiv 2601.21205](https://arxiv.org/pdf/2601.21205)
- Dhvani: weakly supervised phonemic error detection for Hindi targeting retroflex, aspirated and nasalized consonants (22 learners, significant gains, p = 0.0022). — [Moonlight review](https://www.themoonlight.io/review/dhvani-a-weakly-supervised-phonemic-error-detection-and-personalized-feedback-system-for-hindi)
- Aspirated vs unaspirated plosives differ chiefly in aspiration / voice onset time; acoustic-phonetic features beat cepstral features for assessing Hindi aspirated consonants (COLING 2012 workshop). — [ACL W12-5803](https://preview.aclanthology.org/moar-dois/W12-5803.pdf)

### Inferences
- Much of the baseline's "error" (digits vs words) is metric artefact; normalizing both script and hypothesis (numtowords on both sides, nukta folding) or adopting OI-WER-style variant lists will cut false alarms before any model change.
- Aspiration-sensitive check design: align script to audio with an Indic CTC model, then for each aspirated grapheme (ख घ छ झ ठ ढ थ ध फ भ) compare the log-posterior of the scripted character vs. its unaspirated twin over the aligned frames; flag when the twin wins. This uses only MIT models and needs no new training. The espeak IPA recognizer can serve as an independent second opinion (eSpeak's Hindi G2P converts the script to expected IPA).
- Evaluate with a confusion-pair report (थ→त, ध→द/ज, etc.) rather than raw CER, so the QA gate targets real mispronunciations.

### Gaps
- Allosaurus license and Indic accuracy not researched (believed GPL-3.0, unverified).
- No published open Indic pronunciation-assessment (GOP) model or TTS-specific Indic evaluation found.
- Dhvani code/model availability and license unknown.

## Q4. Sanskrit ASR / alignment

### Takeaway
Sanskrit is the weakest language for all ASR (IndicWhisper 48% WER in Vistaar). Open options covering Sanskrit: Indic-Transcribe-core (`sa`), SraVaani-0.5-live (Sanskrit in its 63 languages), IndicWhisper Sanskrit (MIT, older), and a research Whisper adaptation (15.42% WER on Vaksancayah). For verses, forced alignment against the known shloka text is more reliable than free transcription.

### Cited Findings
- IndicWhisper/Vistaar Sanskrit WER 48 (worst of 12 languages). — [Vistaar paper](https://arxiv.org/pdf/2305.15386)
- Indic-Transcribe-core supports Sanskrit (`sa`) with native-script output; commercial use allowed with conditions; gated. — [HF](https://huggingface.co/bodhan-ai/indic-transcribe-core)
- SraVaani-0.5-live lists Sanskrit among 63 languages (CTC head, usable for alignment). — [HF](https://huggingface.co/ARTPARK-IISc/SraVaani-0.5-live)
- Whisper adapted to Sanskrit: 15.42% WER on Vaksancayah (arXiv 2501.10024). Adiga et al. (ACL Findings 2021) released a 78 h Sanskrit ASR corpus. Community whisper "sanskasr" checkpoints exist but appear unfinished. — [arXiv 2501.10024](https://arxiv.org/abs/2501.10024v1); [arXiv 2106.05852](https://arxiv.org/abs/2106.05852v2); [HF whisper-small-sanskasr](https://huggingface.co/bvkbharadwaj/whisper-small-sanskasr/tree/main)

### Inferences
- For Sanskrit verses in videos, use CTC forced alignment with SraVaani (CTC, MIT) or a Hindi Devanagari CTC model (IndicConformer hi) as fallback — Devanagari character inventories overlap heavily; for pronunciation QA rely on alignment confidence per syllable rather than ASR CER, which will be noisy.
- Chanted/metered recitation differs from training speech; test on actual Veena output before trusting any score.

### Gaps
- No Sanskrit-specific WER for Indic-Transcribe-core or SraVaani found; license of the arXiv 2501.10024 model not checked.
