# QA report: audio-only

**Verdict: WARN** · 2026-11-18T13:43:28+0530 · report #112

- **Story** 100/100 PASS
- **Audio** 75/100 NOT PASSED · warn: speech_rate

- ✅ **lint_duration** (story/warn) {"estimate_s": 52.96, "basis": "letters"}
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
- ✅ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)", "whisper large-v3-turbo"]} — digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear
- ⚠️ **speech_rate** (audio/warn) {"reference_letters_per_s": 6.114}
    - scene 4: speech rate -28% vs hi reference
- ✅ **speaker_consistency** (audio/reject) {"windows": 25, "window_median": 0.722, "window_min": 0.604, "scene_min": 0.687, "median_f0": 170, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
