# QA report: C0009-te.mp4

**Verdict: WARN** · 2026-11-17T15:13:22+0530 · report #98

File sha256: `7087dfc0b66ea76d467126eef63471b7ad91f2e1ceaa801ab1d678889f3b3e89`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 33/100 NOT PASSED · warn: chalk_density, safe_zones
- **Audio** 100/100 PASS
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 53.15, "basis": "letters"}
- ⚠️ **lint_hook** (story/warn) {}
    - hook scene spoken 2.5 s > 2.2 s
- ✅ **lint_scene_count** (story/warn) {}
- ✅ **lint_scene_length** (story/warn) {}
- ✅ **lint_keywords** (story/warn) {}
- ✅ **lint_digits** (story/warn) {}
- ✅ **lint_quote_src** (story/warn) {}
- ✅ **lint_sources** (story/warn) {}
- ✅ **lint_edition** (story/warn) {}
- ✅ **lint_silences** (story/warn) {}
- ✅ **lint_visual_parity** (story/warn) {}
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 49.1}
- ✅ **duration** (final/reject) {"seconds": 49.1}
- ✅ **duration_target** (final/warn) {"seconds": 49.1}
- ✅ **loudness** (final/reject) {"lufs": -14.0, "true_peak_dbfs": -1.9, "lra": 2.7}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.353, "t0.5": 0.3332} — style decision: warn only
- ✅ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — CER is warn-only for this language until Indic ASR is validated
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.928}
- ✅ **speaker_consistency** (audio/reject) {"windows": 20, "window_median": 0.737, "window_min": 0.671, "scene_min": 0.644, "median_f0": 178, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 13.6, "p10_db": 6.7, "voice_gain": 3.666, "frames": 96}
- ✅ **captions** (final/warn) {"groups": 44, "timing": "timeline.json", "engine_version": 2}
- ✅ **caption_overflow** (final/reject) {"widest_px": 866, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 21, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ⚠️ **chalk_density** (visual/warn) {}
    - scene 1: chalk density 47.6% outside 3%–45%
    - scene 4: chalk density 58.4% outside 3%–45%
    - scene 10: chalk density 52.0% outside 3%–45%
    - scene 11: chalk density 60.0% outside 3%–45%
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 2: stroke energy in the caption zone (bottom 25%) 1.55 > p90 1.519
    - scene 3: stroke energy in the caption zone (bottom 25%) 2.01 > p90 1.519
    - scene 6: stroke energy in the caption zone (bottom 25%) 1.63 > p90 1.519
    - scene 8: stroke energy in the title zone (top 12%) 1.30 > p90 0.111
    - scene 10: stroke energy in the caption zone (bottom 25%) 1.60 > p90 1.519
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0009/te/C0009-te.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
