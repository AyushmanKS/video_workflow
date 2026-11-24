# QA report: audio-only

**Verdict: WARN** · 2026-11-24T21:17:29+0530 · report #152

- **Story** 91/100 PASS · warn: lint_hook
- **Audio** 75/100 NOT PASSED · warn: speech_rate

- ✅ **lint_duration** (story/warn) {"estimate_s": 53.32, "basis": "letters"}
- ⚠️ **lint_hook** (story/warn) {}
    - hook scene spoken 2.4 s > 2.2 s
- ✅ **lint_scene_count** (story/warn) {}
- ✅ **lint_scene_length** (story/warn) {}
- ✅ **lint_keywords** (story/warn) {}
- ✅ **lint_digits** (story/warn) {}
- ✅ **lint_quote_src** (story/warn) {}
- ✅ **lint_sources** (story/warn) {}
- ✅ **lint_edition** (story/warn) {}
- ✅ **lint_silences** (story/warn) {}
- ✅ **lint_visual_parity** (story/warn) {}
- ✅ **narration_asr** (audio/warn) {"transcripts": ["whisper large-v3-turbo"]} — CER is warn-only for this language until Indic ASR is validated
- ⚠️ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.928}
    - scene 7: speech rate -31% vs te reference
- ✅ **speaker_consistency** (audio/reject) {"windows": 26, "window_median": 0.756, "window_min": 0.613, "scene_min": 0.734, "median_f0": 171, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
