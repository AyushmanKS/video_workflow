# QA report: audio-only

**Verdict: WARN** · 2026-11-18T20:56:55+0530 · report #129

- **Story** 100/100 PASS
- **Audio** 50/100 NOT PASSED · warn: narration_asr, speech_rate

- ✅ **lint_duration** (story/warn) {"estimate_s": 570.29, "basis": "letters"}
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
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["QA cache (wav hash)", "whisper large-v3-turbo"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 8: CER 0.188 length ratio 0.87 (warn) — listen and regenerate if mispronounced
    - scene 10: CER 0.164 length ratio 0.85 (warn) — listen and regenerate if mispronounced
    - scene 12: CER 0.365 length ratio 0.65 (warn) — listen and regenerate if mispronounced
    - scene 16: CER 0.338 length ratio 0.75 (warn) — listen and regenerate if mispronounced
    - scene 18: CER 0.214 length ratio 0.79 (warn) — listen and regenerate if mispronounced
    - scene 19: CER 0.219 length ratio 0.81 (warn) — listen and regenerate if mispronounced
    - scene 20: CER 0.154 length ratio 0.95 (warn) — listen and regenerate if mispronounced
    - scene 21: CER 0.444 length ratio 0.57 (warn) — listen and regenerate if mispronounced
    - scene 23: CER 0.27 length ratio 0.76 (warn) — listen and regenerate if mispronounced
    - scene 25: CER 0.264 length ratio 0.81 (warn) — listen and regenerate if mispronounced
    - scene 28: CER 0.303 length ratio 0.76 (warn) — listen and regenerate if mispronounced
    - scene 29: CER 0.151 length ratio 0.88 (warn) — listen and regenerate if mispronounced
    - scene 30: CER 0.525 length ratio 0.5 (warn) — listen and regenerate if mispronounced
    - scene 32: CER 0.304 length ratio 0.75 (warn) — listen and regenerate if mispronounced
    - scene 35: CER 0.154 length ratio 0.88 (warn) — listen and regenerate if mispronounced
    - scene 36: CER 0.379 length ratio 0.66 (warn) — listen and regenerate if mispronounced
    - scene 37: CER 0.26 length ratio 0.77 (warn) — listen and regenerate if mispronounced
    - scene 38: CER 0.203 length ratio 0.81 (warn) — listen and regenerate if mispronounced
    - scene 39: CER 0.222 length ratio 0.82 (warn) — listen and regenerate if mispronounced
    - scene 47: CER 0.247 length ratio 0.78 (warn) — listen and regenerate if mispronounced
    - scene 48: CER 0.416 length ratio 0.63 (warn) — listen and regenerate if mispronounced
    - scene 49: CER 0.25 length ratio 0.79 (warn) — listen and regenerate if mispronounced
- ⚠️ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.928}
    - scene 2: speech rate +26% vs te reference
- ✅ **speaker_consistency** (audio/reject) {"windows": 360, "window_median": 0.749, "window_min": 0.499, "scene_min": 0.787, "median_f0": 174, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
