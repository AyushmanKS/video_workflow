# QA report: C0013-gu.mp4

**Verdict: WARN** · 2026-11-24T22:15:28+0530 · report #159

File sha256: `452fefd3c09254cd167eff501fe5a52e44ff8f9887da3ce0de2caab48635955b`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 33/100 NOT PASSED · warn: chalk_density, safe_zones
- **Audio** 80/100 PASS · warn: narration_asr
- **Final** 94/100 PASS · warn: duration_target

- ✅ **lint_duration** (story/warn) {"estimate_s": 51.93, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 55.27}
- ✅ **duration** (final/reject) {"seconds": 55.27}
- ⚠️ **duration_target** (final/warn) {"seconds": 55.27}
    - duration 55.27 s outside 35–55 s
- ✅ **loudness** (final/reject) {"lufs": -14.0, "true_peak_dbfs": -2.0, "lra": 2.5}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2812, "t0.5": 0.3256} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 6: CER 0.269 length ratio 0.88 (warn) — listen and regenerate if mispronounced
    - scene 11: CER 0.167 length ratio 0.92 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.808}
- ✅ **speaker_consistency** (audio/reject) {"windows": 25, "window_median": 0.668, "window_min": 0.57, "scene_min": 0.689, "median_f0": 183, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 13.1, "p10_db": 1.7, "voice_gain": 3.705, "frames": 105}
- ✅ **captions** (final/warn) {"groups": 40, "timing": "timeline.json", "engine_version": 3}
- ✅ **caption_overflow** (final/reject) {"widest_px": 794, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 21, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ⚠️ **chalk_density** (visual/warn) {}
    - scene 8: chalk density 47.6% outside 3%–45%
    - scene 11: chalk density 47.4% outside 3%–45%
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 3: stroke energy in the title zone (top 12%) 0.13 > p90 0.111
    - scene 8: stroke energy in the title zone (top 12%) 0.16 > p90 0.111
    - scene 10: stroke energy in the title zone (top 12%) 0.40 > p90 0.111
    - scene 10: stroke energy in the caption zone (bottom 25%) 2.23 > p90 1.519
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0013/gu/C0013-gu.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
