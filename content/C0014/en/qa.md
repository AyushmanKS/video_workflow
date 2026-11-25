# QA report: C0014-en.mp4

**Verdict: WARN** · 2026-11-25T07:51:57+0530 · report #173

File sha256: `382cb69d9245e95ba41acb1425c18bbd215b8c93dd6a84d7c13dccbace2bd5b5`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 33/100 NOT PASSED · warn: near_duplicates, safe_zones
- **Audio** 80/100 PASS · warn: music_under_speech
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 53.51, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 52.3}
- ✅ **duration** (final/reject) {"seconds": 52.3}
- ✅ **duration_target** (final/warn) {"seconds": 52.3}
- ✅ **loudness** (final/reject) {"lufs": -13.9, "true_peak_dbfs": -1.6, "lra": 2.0}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.1732, "t0.5": 0.2151} — style decision: warn only
- ✅ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 12.04}
- ✅ **speaker_consistency** (audio/reject) {"windows": 25, "window_median": 0.757, "window_min": 0.661, "scene_min": 0.747, "median_f0": 198, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ⚠️ **music_under_speech** (audio/warn) {"median_db": 10.9, "p10_db": 2.6, "voice_gain": 3.88, "frames": 89}
    - speech-band narration only 10.9 dB above the bed (target ≥12 dB)
- ✅ **captions** (final/warn) {"groups": 45, "timing": "timeline.json", "engine_version": 3}
- ✅ **caption_overflow** (final/reject) {"widest_px": 861, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 19, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ⚠️ **near_duplicates** (visual/warn) {"images": 9}
    - scenes 1 and 9: perceptual hash distance 6 bits (< 8)
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 1: stroke energy in the title zone (top 12%) 0.98 > p90 0.111
    - scene 2: stroke energy in the title zone (top 12%) 0.97 > p90 0.111
    - scene 2: stroke energy in the caption zone (bottom 25%) 1.98 > p90 1.519
    - scene 3: stroke energy in the title zone (top 12%) 0.17 > p90 0.111
    - scene 3: stroke energy in the caption zone (bottom 25%) 1.93 > p90 1.519
    - scene 4: stroke energy in the title zone (top 12%) 0.86 > p90 0.111
    - scene 5: stroke energy in the title zone (top 12%) 0.86 > p90 0.111
    - scene 6: stroke energy in the title zone (top 12%) 0.53 > p90 0.111
    - scene 7: stroke energy in the title zone (top 12%) 0.12 > p90 0.111
    - scene 7: stroke energy in the caption zone (bottom 25%) 1.67 > p90 1.519
    - scene 8: stroke energy in the title zone (top 12%) 1.14 > p90 0.111
    - scene 9: stroke energy in the title zone (top 12%) 0.86 > p90 0.111
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0014/en/C0014-en.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
