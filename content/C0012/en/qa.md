# QA report: C0012-en.mp4

**Verdict: WARN** · 2026-11-23T20:29:54+0530 · report #144

File sha256: `2c8a63c8223fc3b8854866e256678e795e840461da720df082e6263ab0ab166c`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 67/100 NOT PASSED · warn: safe_zones
- **Audio** 80/100 PASS · warn: music_under_speech
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 54.31, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 53.5}
- ✅ **duration** (final/reject) {"seconds": 53.5}
- ✅ **duration_target** (final/warn) {"seconds": 53.5}
- ✅ **loudness** (final/reject) {"lufs": -13.9, "true_peak_dbfs": -1.4, "lra": 2.6}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2161, "t0.5": 0.2474} — style decision: warn only
- ✅ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 12.04}
- ✅ **speaker_consistency** (audio/reject) {"windows": 24, "window_median": 0.724, "window_min": 0.637, "scene_min": 0.708, "median_f0": 199, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ⚠️ **music_under_speech** (audio/warn) {"median_db": 11.8, "p10_db": 4.9, "voice_gain": 3.886, "frames": 89}
    - speech-band narration only 11.8 dB above the bed (target ≥12 dB)
- ✅ **captions** (final/warn) {"groups": 48, "timing": "timeline.json", "engine_version": 3}
- ✅ **caption_overflow** (final/reject) {"widest_px": 869, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 21, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 1: stroke energy in the caption zone (bottom 25%) 1.63 > p90 1.519
    - scene 3: stroke energy in the title zone (top 12%) 0.29 > p90 0.111
    - scene 6: stroke energy in the caption zone (bottom 25%) 2.12 > p90 1.519
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0012/en/C0012-en.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
