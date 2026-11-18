# QA report: audio-only

**Verdict: WARN** · 2026-11-18T12:17:51+0530 · report #108

- **Story** 91/100 PASS · warn: lint_hook
- **Audio** 75/100 NOT PASSED · warn: narration_asr

- ✅ **lint_duration** (story/warn) {"estimate_s": 54.08, "basis": "letters"}
- ⚠️ **lint_hook** (story/warn) {}
    - hook scene spoken 2.6 s > 2.2 s
- ✅ **lint_scene_count** (story/warn) {}
- ✅ **lint_scene_length** (story/warn) {}
- ✅ **lint_keywords** (story/warn) {}
- ✅ **lint_digits** (story/warn) {}
- ✅ **lint_quote_src** (story/warn) {}
- ✅ **lint_sources** (story/warn) {}
- ✅ **lint_edition** (story/warn) {}
- ✅ **lint_silences** (story/warn) {}
- ✅ **lint_visual_parity** (story/warn) {}
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["QA cache (wav hash)", "whisper large-v3-turbo"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 2: CER 0.172 length ratio 0.97 (warn) — listen and regenerate if mispronounced
    - scene 4: CER 0.156 length ratio 0.97 (warn) — listen and regenerate if mispronounced
    - scene 10: CER 0.161 length ratio 0.94 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 6.037}
- ✅ **speaker_consistency** (audio/reject) {"windows": 22, "window_median": 0.717, "window_min": 0.589, "scene_min": 0.712, "median_f0": 191, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
