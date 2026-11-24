# QA report: audio-only

**Verdict: WARN** · 2026-11-24T21:09:39+0530 · report #149

- **Story** 91/100 PASS · warn: lint_hook
- **Audio** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 53.06, "basis": "letters"}
- ⚠️ **lint_hook** (story/warn) {}
    - hook scene spoken 2.7 s > 2.2 s
- ✅ **lint_scene_count** (story/warn) {}
- ✅ **lint_scene_length** (story/warn) {}
- ✅ **lint_keywords** (story/warn) {}
- ✅ **lint_digits** (story/warn) {}
- ✅ **lint_quote_src** (story/warn) {}
- ✅ **lint_sources** (story/warn) {}
- ✅ **lint_edition** (story/warn) {}
- ✅ **lint_silences** (story/warn) {}
- ✅ **lint_visual_parity** (story/warn) {}
- ✅ **narration_asr** (audio/warn) {"transcripts": ["whisper small"]} — digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 12.04}
- ✅ **speaker_consistency** (audio/reject) {"windows": 24, "window_median": 0.753, "window_min": 0.605, "scene_min": 0.784, "median_f0": 194, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
