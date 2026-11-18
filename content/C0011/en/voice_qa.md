# QA report: audio-only

**Verdict: PASS** · 2026-11-18T20:27:16+0530 · report #123

- **Story** 100/100 PASS
- **Audio** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 586.77, "basis": "letters"}
- ✅ **lint_hook** (story/warn) {}
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
- ✅ **speaker_consistency** (audio/reject) {"windows": 348, "window_median": 0.756, "window_min": 0.637, "scene_min": 0.858, "median_f0": 197, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
