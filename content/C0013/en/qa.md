# QA report: C0013-en.mp4

**Verdict: WARN** · 2026-11-24T21:58:38+0530 · report #155

File sha256: `6ae37dc37f3a755a3bec9a4eef2182383ec300bf320acd5ae6ef43401935e46a`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 33/100 NOT PASSED · warn: chalk_density, safe_zones
- **Audio** 80/100 PASS · warn: music_under_speech
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 53.06, "basis": "letters"}
- ⚠️ **lint_hook** (story/warn) {}
    - hook scene spoken 2.7 s > 2.2 s
- ✅ **lint_scene_count** (story/warn) {}
- ✅ **lint_scene_length** (story/warn) {}
- ✅ **lint_keywords** (story/warn) {}
- ✅ **lint_digits** (story/warn) {}
- ✅ **lint_quote_src** (story/warn) {}
- ✅ **lint_sources** (story/warn) {}
- ✅ **lint_edition** (story/warn) {}
- ✅ **lint_silences** (story/warn) {}
- ✅ **lint_visual_parity** (story/warn) {}
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 53.03}
- ✅ **duration** (final/reject) {"seconds": 53.03}
- ✅ **duration_target** (final/warn) {"seconds": 53.03}
- ✅ **loudness** (final/reject) {"lufs": -14.0, "true_peak_dbfs": -1.7, "lra": 2.9}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.282, "t0.5": 0.3268} — style decision: warn only
- ✅ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 12.04}
- ✅ **speaker_consistency** (audio/reject) {"windows": 24, "window_median": 0.753, "window_min": 0.605, "scene_min": 0.784, "median_f0": 194, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ⚠️ **music_under_speech** (audio/warn) {"median_db": 10.2, "p10_db": -0.4, "voice_gain": 3.652, "frames": 92}
    - speech-band narration only 10.2 dB above the bed (target ≥12 dB)
- ✅ **captions** (final/warn) {"groups": 47, "timing": "timeline.json", "engine_version": 3}
- ✅ **caption_overflow** (final/reject) {"widest_px": 897, "limit_px": 1020}
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

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0013/en/C0013-en.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
