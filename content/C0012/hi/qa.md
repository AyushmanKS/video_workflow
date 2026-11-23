# QA report: C0012-hi.mp4

**Verdict: WARN** · 2026-11-23T20:43:16+0530 · report #145

File sha256: `3f7914f41441e90ef7ae3afcbaa9171bb12a080af5c11c9c683c84ab8f798006`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 67/100 NOT PASSED · warn: safe_zones
- **Audio** 100/100 PASS
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 51.49, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 52.3}
- ✅ **duration** (final/reject) {"seconds": 52.3}
- ✅ **duration_target** (final/warn) {"seconds": 52.3}
- ✅ **loudness** (final/reject) {"lufs": -13.9, "true_peak_dbfs": -2.0, "lra": 3.0}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2189, "t0.5": 0.2503} — style decision: warn only
- ✅ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 6.114}
- ✅ **speaker_consistency** (audio/reject) {"windows": 23, "window_median": 0.722, "window_min": 0.505, "scene_min": 0.611, "median_f0": 198, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 12.8, "p10_db": 4.6, "voice_gain": 3.485, "frames": 101}
- ✅ **captions** (final/warn) {"groups": 41, "timing": "timeline.json", "engine_version": 3}
- ✅ **caption_overflow** (final/reject) {"widest_px": 862, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 21, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 1: stroke energy in the caption zone (bottom 25%) 1.63 > p90 1.519
    - scene 3: stroke energy in the title zone (top 12%) 0.29 > p90 0.111
    - scene 6: stroke energy in the caption zone (bottom 25%) 2.12 > p90 1.519
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0012/hi/C0012-hi.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
