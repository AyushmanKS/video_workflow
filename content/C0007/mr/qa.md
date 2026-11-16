# QA report: C0007-mr.mp4

**Verdict: WARN** · 2026-11-16T23:35:16+0530 · report #66

File sha256: `bc892be7b86c96bd2c29a8eb34ed338cc782bb61e8ac22e95deda89044e1119b`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 67/100 NOT PASSED · warn: safe_zones
- **Audio** 80/100 PASS · warn: narration_asr
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 53.62, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 53.23}
- ✅ **duration** (final/reject) {"seconds": 53.23}
- ✅ **duration_target** (final/warn) {"seconds": 53.23}
- ✅ **loudness** (final/reject) {"lufs": -13.9, "true_peak_dbfs": -1.5, "lra": 3.4}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.1099, "t0.5": 0.1359} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 2: CER 0.207 length ratio 1.03 (warn) — listen and regenerate if mispronounced
    - scene 10: CER 0.231 length ratio 1.04 (warn) — listen and regenerate if mispronounced
    - scene 11: CER 0.195 length ratio 1.0 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 6.037}
- ✅ **speaker_consistency** (audio/reject) {"windows": 23, "window_median": 0.698, "window_min": 0.54, "scene_min": 0.684, "median_f0": 186, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 13.2, "p10_db": 5.1, "voice_gain": 3.428, "frames": 102}
- ✅ **captions** (final/warn) {"groups": 34, "timing": "timeline.json", "engine_version": 2}
- ✅ **caption_overflow** (final/reject) {"widest_px": 834, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 20, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 1: stroke energy in the title zone (top 12%) 0.14 > p90 0.111
    - scene 1: stroke energy in the caption zone (bottom 25%) 1.92 > p90 1.519
    - scene 3: stroke energy in the title zone (top 12%) 0.12 > p90 0.111
    - scene 4: stroke energy in the title zone (top 12%) 0.18 > p90 0.111
    - scene 5: stroke energy in the title zone (top 12%) 0.35 > p90 0.111
    - scene 6: stroke energy in the title zone (top 12%) 0.27 > p90 0.111
    - scene 9: stroke energy in the title zone (top 12%) 1.20 > p90 0.111
    - scene 11: stroke energy in the caption zone (bottom 25%) 1.62 > p90 1.519
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0007/mr/C0007-mr.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
