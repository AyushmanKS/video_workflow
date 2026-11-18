# QA report: C0011-hi.mp4

**Verdict: WARN** · 2026-11-18T22:31:08+0530 · report #132

File sha256: `bc52cd250f82e3ea21b15d5cd7c3f481976ddad7a60afc6d1a3c58e5813dc130`

- **Story** 100/100 PASS
- **Visual** 33/100 NOT PASSED · warn: near_duplicates, safe_zones
- **Audio** 100/100 PASS
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 606.33, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 600.67}
- ✅ **duration** (final/reject) {"seconds": 600.67}
- ✅ **duration_target** (final/warn) {"seconds": 600.67}
- ✅ **loudness** (final/reject) {"lufs": -14.0, "true_peak_dbfs": -1.4, "lra": 2.9}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2426, "t0.5": 0.275} — style decision: warn only
- ✅ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 6.114}
- ✅ **speaker_consistency** (audio/reject) {"windows": 386, "window_median": 0.74, "window_min": 0.539, "scene_min": 0.733, "median_f0": 167, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 13.0, "p10_db": 6.6, "voice_gain": 3.771, "frames": 1139}
- ✅ **captions** (final/warn) {"groups": 496, "timing": "timeline.json", "engine_version": 3}
- ✅ **caption_overflow** (final/reject) {"widest_px": 893, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 69, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ⚠️ **near_duplicates** (visual/warn) {"images": 50}
    - scenes 19 and 24: perceptual hash distance 6 bits (< 8)
    - scenes 30 and 38: perceptual hash distance 6 bits (< 8)
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 1: stroke energy in the title zone (top 12%) 1.25 > p90 0.111
    - scene 2: stroke energy in the title zone (top 12%) 1.16 > p90 0.111
    - scene 3: stroke energy in the title zone (top 12%) 0.13 > p90 0.111
    - scene 5: stroke energy in the title zone (top 12%) 0.78 > p90 0.111
    - scene 7: stroke energy in the title zone (top 12%) 0.15 > p90 0.111
    - scene 8: stroke energy in the title zone (top 12%) 0.16 > p90 0.111
    - scene 8: stroke energy in the caption zone (bottom 25%) 1.60 > p90 1.519
    - scene 9: stroke energy in the caption zone (bottom 25%) 1.91 > p90 1.519
    - scene 12: stroke energy in the title zone (top 12%) 0.32 > p90 0.111
    - scene 14: stroke energy in the title zone (top 12%) 0.75 > p90 0.111
    - scene 16: stroke energy in the title zone (top 12%) 0.43 > p90 0.111
    - scene 17: stroke energy in the title zone (top 12%) 0.76 > p90 0.111
    - scene 18: stroke energy in the title zone (top 12%) 0.17 > p90 0.111
    - scene 20: stroke energy in the title zone (top 12%) 0.20 > p90 0.111
    - scene 22: stroke energy in the title zone (top 12%) 0.23 > p90 0.111
    - scene 23: stroke energy in the title zone (top 12%) 0.57 > p90 0.111
    - scene 25: stroke energy in the title zone (top 12%) 0.29 > p90 0.111
    - scene 26: stroke energy in the title zone (top 12%) 0.44 > p90 0.111
    - scene 27: stroke energy in the title zone (top 12%) 0.59 > p90 0.111
    - scene 28: stroke energy in the title zone (top 12%) 0.12 > p90 0.111
    - scene 29: stroke energy in the title zone (top 12%) 0.15 > p90 0.111
    - scene 31: stroke energy in the title zone (top 12%) 0.12 > p90 0.111
    - scene 32: stroke energy in the title zone (top 12%) 0.95 > p90 0.111
    - scene 34: stroke energy in the title zone (top 12%) 0.96 > p90 0.111
    - scene 35: stroke energy in the title zone (top 12%) 0.64 > p90 0.111
    - scene 36: stroke energy in the title zone (top 12%) 0.80 > p90 0.111
    - scene 37: stroke energy in the title zone (top 12%) 0.23 > p90 0.111
    - scene 39: stroke energy in the title zone (top 12%) 0.66 > p90 0.111
    - scene 40: stroke energy in the title zone (top 12%) 0.19 > p90 0.111
    - scene 41: stroke energy in the title zone (top 12%) 0.52 > p90 0.111
    - scene 42: stroke energy in the title zone (top 12%) 0.95 > p90 0.111
    - scene 43: stroke energy in the caption zone (bottom 25%) 1.55 > p90 1.519
    - scene 45: stroke energy in the title zone (top 12%) 0.75 > p90 0.111
    - scene 46: stroke energy in the title zone (top 12%) 0.13 > p90 0.111
    - scene 47: stroke energy in the title zone (top 12%) 0.40 > p90 0.111
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0011/hi/C0011-hi.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
