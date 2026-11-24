# QA report: audio-only

**Verdict: WARN** · 2026-11-24T21:21:36+0530 · report #154

- **Story** 91/100 PASS · warn: lint_hook
- **Audio** 50/100 NOT PASSED · warn: narration_asr, speech_rate

- ✅ **lint_duration** (story/warn) {"estimate_s": 51.81, "basis": "letters"}
- ⚠️ **lint_hook** (story/warn) {}
    - hook scene spoken 2.8 s > 2.2 s
- ✅ **lint_scene_count** (story/warn) {}
- ✅ **lint_scene_length** (story/warn) {}
- ✅ **lint_keywords** (story/warn) {}
- ✅ **lint_digits** (story/warn) {}
- ✅ **lint_quote_src** (story/warn) {}
- ✅ **lint_sources** (story/warn) {}
- ✅ **lint_edition** (story/warn) {}
- ✅ **lint_silences** (story/warn) {}
- ✅ **lint_visual_parity** (story/warn) {}
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["QA cache (wav hash)", "whisper large-v3-turbo"]} — digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear
    - scene 11: CER 0.192 length ratio 0.92 (warn) — listen and regenerate if mispronounced
- ⚠️ **speech_rate** (audio/warn) {"reference_letters_per_s": 6.114}
    - scene 7: speech rate -32% vs hi reference
- ✅ **speaker_consistency** (audio/reject) {"windows": 25, "window_median": 0.7, "window_min": 0.589, "scene_min": 0.636, "median_f0": 159, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
