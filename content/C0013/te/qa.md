# QA report: C0013-te.mp4

**Verdict: WARN** · 2026-11-24T22:21:12+0530 · report #160

File sha256: `b22db3a4a92ce3008e5dac22d62a1b0247106ae83c3f0fbe35ccee62a412c6f0`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 33/100 NOT PASSED · warn: chalk_density, safe_zones
- **Audio** 80/100 PASS · warn: speech_rate
- **Final** 94/100 PASS · warn: duration_target

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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 56.07}
- ✅ **duration** (final/reject) {"seconds": 56.07}
- ⚠️ **duration_target** (final/warn) {"seconds": 56.07}
    - duration 56.07 s outside 35–55 s
- ✅ **loudness** (final/reject) {"lufs": -14.0, "true_peak_dbfs": -2.0, "lra": 2.9}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2818, "t0.5": 0.3273} — style decision: warn only
- ✅ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — CER is warn-only for this language until Indic ASR is validated
- ⚠️ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.928}
    - scene 7: speech rate -31% vs te reference
- ✅ **speaker_consistency** (audio/reject) {"windows": 26, "window_median": 0.756, "window_min": 0.613, "scene_min": 0.734, "median_f0": 171, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 12.9, "p10_db": 1.2, "voice_gain": 3.56, "frames": 109}
- ✅ **captions** (final/warn) {"groups": 44, "timing": "timeline.json", "engine_version": 3}
- ✅ **caption_overflow** (final/reject) {"widest_px": 954, "limit_px": 1020}
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

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0013/te/C0013-te.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
