# QA report: C0010-gu.mp4

**Verdict: WARN** · 2026-11-18T14:53:57+0530 · report #120

File sha256: `3ed64e64ba0cc0165cce0974ff138c453dbbfa6854570ef45053a36332604678`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 67/100 NOT PASSED · warn: safe_zones
- **Audio** 80/100 PASS · warn: narration_asr
- **Final** 94/100 PASS · warn: duration_target

- ✅ **lint_duration** (story/warn) {"estimate_s": 53.82, "basis": "letters"}
- ⚠️ **lint_hook** (story/warn) {}
    - hook scene spoken 2.2 s > 2.2 s
- ✅ **lint_scene_count** (story/warn) {}
- ✅ **lint_scene_length** (story/warn) {}
- ✅ **lint_keywords** (story/warn) {}
- ✅ **lint_digits** (story/warn) {}
- ✅ **lint_quote_src** (story/warn) {}
- ✅ **lint_sources** (story/warn) {}
- ✅ **lint_edition** (story/warn) {}
- ✅ **lint_silences** (story/warn) {}
- ✅ **lint_visual_parity** (story/warn) {}
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 55.83}
- ✅ **duration** (final/reject) {"seconds": 55.83}
- ⚠️ **duration_target** (final/warn) {"seconds": 55.83}
    - duration 55.83 s outside 35–55 s
- ✅ **loudness** (final/reject) {"lufs": -14.0, "true_peak_dbfs": -2.0, "lra": 2.5}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.279, "t0.5": 0.3205} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 1: CER 0.154 length ratio 0.85 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.808}
- ✅ **speaker_consistency** (audio/reject) {"windows": 24, "window_median": 0.721, "window_min": 0.504, "scene_min": 0.641, "median_f0": 178, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 13.0, "p10_db": 2.5, "voice_gain": 3.742, "frames": 109}
- ✅ **captions** (final/warn) {"groups": 39, "timing": "timeline.json", "engine_version": 3}
- ✅ **caption_overflow** (final/reject) {"widest_px": 790, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 21, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 8: stroke energy in the caption zone (bottom 25%) 1.88 > p90 1.519
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0010/gu/C0010-gu.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
