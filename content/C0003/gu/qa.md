# QA report: C0003-gu.mp4

**Verdict: WARN** · 2026-11-16T17:46:15+0530 · report #46

File sha256: `90107c5ac95fdc9504ce9edfde21c71fb11aef3e42d455e0f4a2eb1634f79999`

- **Story** 45/100 NOT PASSED · warn: lint_duration, lint_hook, lint_scene_count, lint_scene_length, lint_edition, lint_silences
- **Visual** 67/100 NOT PASSED · warn: safe_zones
- **Audio** 60/100 NOT PASSED · warn: narration_asr, music_under_speech
- **Final** 87/100 PASS · warn: duration, duration_target

- ⚠️ **lint_duration** (story/warn) {"estimate_s": 108.72, "basis": "letters", "exempt": "back-catalogue: en/hi published before the 60 s rule; gu/te mirror them scene by scene"}
    - estimated 108.7 s > 57 s (rate 2.111 w/s, 202 words, pauses 4.8 s, lead/tail 1.15 s)
- ⚠️ **lint_hook** (story/warn) {"exempt": "back-catalogue: en/hi published before the 60 s rule; gu/te mirror them scene by scene"}
    - hook scene spoken 7.7 s > 3.0 s
- ⚠️ **lint_scene_count** (story/warn) {}
    - 13 scenes (target 8–11)
- ⚠️ **lint_scene_length** (story/warn) {}
    - scene 2 spoken 8.2 s (target 2.5–7.0 s)
    - scene 6 spoken 11.2 s (target 2.5–7.0 s)
    - scene 7 spoken 7.2 s (target 2.5–7.0 s)
    - scene 8 spoken 7.9 s (target 2.5–7.0 s)
    - scene 9 spoken 8.9 s (target 2.5–7.0 s)
    - scene 10 spoken 9.3 s (target 2.5–7.0 s)
    - scene 11 spoken 9.3 s (target 2.5–7.0 s)
    - scene 13 spoken 9.8 s (target 2.5–7.0 s)
- ✅ **lint_keywords** (story/warn) {}
- ✅ **lint_digits** (story/warn) {}
- ✅ **lint_quote_src** (story/warn) {}
- ✅ **lint_sources** (story/warn) {}
- ⚠️ **lint_edition** (story/warn) {}
    - scene 9: verse card has no edition label (scene or script 'edition')
    - script has no 'edition' (which text edition the sources cite)
- ⚠️ **lint_silences** (story/warn) {}
    - 13 planned silences (pause ≥0.3 s); target 2–3
- ✅ **lint_visual_parity** (story/warn) {}
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 108.5}
- ⚠️ **duration** (final/warn) {"seconds": 108.5, "exempt": "back-catalogue: en/hi published before the 60 s rule; gu/te mirror them scene by scene"}
    - duration 108.50 s ≥ 60.0 s
- ⚠️ **duration_target** (final/warn) {"seconds": 108.5}
    - duration 108.50 s outside 35–55 s
- ✅ **loudness** (final/reject) {"lufs": -14.6, "true_peak_dbfs": -1.4, "lra": 2.3}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.0021, "t0.5": 0.1352} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["QA cache (wav hash)"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 4: CER 0.206 length ratio 0.94 (warn) — listen and regenerate if mispronounced
    - scene 5: CER 0.222 length ratio 0.94 (warn) — listen and regenerate if mispronounced
    - scene 6: CER 0.385 length ratio 0.69 (warn) — listen and regenerate if mispronounced
    - scene 8: CER 0.217 length ratio 0.89 (warn) — listen and regenerate if mispronounced
    - scene 9: CER 0.212 length ratio 0.83 (warn) — listen and regenerate if mispronounced
    - scene 10: CER 0.204 length ratio 0.81 (warn) — listen and regenerate if mispronounced
    - scene 11: CER 0.241 length ratio 0.78 (warn) — listen and regenerate if mispronounced
    - scene 13: CER 0.263 length ratio 0.77 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.819}
- ✅ **speaker_consistency** (audio/reject) {"windows": 62, "window_median": 0.699, "window_min": 0.529, "scene_min": 0.718, "median_f0": 179, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ⚠️ **music_under_speech** (audio/warn) {"median_db": 10.8, "p10_db": 3.0, "voice_gain": 1.0, "frames": 199}
    - speech-band narration only 10.8 dB above the bed (target ≥12 dB)
- ✅ **captions** (final/warn) {"groups": 77}
- ✅ **caption_overflow** (final/reject) {"widest_px": 794, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 26}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 13}
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 8: stroke energy in the caption zone (bottom 25%) 2.15 > p90 1.519
    - scene 10: stroke energy in the title zone (top 12%) 0.12 > p90 0.111
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0003/gu/C0003-gu.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
