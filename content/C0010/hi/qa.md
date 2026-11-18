# QA report: C0010-hi.mp4

**Verdict: WARN** · 2026-11-18T14:47:51+0530 · report #119

File sha256: `81e066bbd6723befe5014fc6eda606f2abc8bb7728ff4603915d42197c59d1ed`

- **Story** 100/100 PASS
- **Visual** 67/100 NOT PASSED · warn: safe_zones
- **Audio** 60/100 NOT PASSED · warn: speech_rate, music_under_speech
- **Final** 94/100 PASS · warn: duration_target

- ✅ **lint_duration** (story/warn) {"estimate_s": 52.96, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 55.9}
- ✅ **duration** (final/reject) {"seconds": 55.9}
- ⚠️ **duration_target** (final/warn) {"seconds": 55.9}
    - duration 55.90 s outside 35–55 s
- ✅ **loudness** (final/reject) {"lufs": -13.9, "true_peak_dbfs": -2.0, "lra": 3.5}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2776, "t0.5": 0.319} — style decision: warn only
- ✅ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear
- ⚠️ **speech_rate** (audio/warn) {"reference_letters_per_s": 6.114}
    - scene 4: speech rate -28% vs hi reference
- ✅ **speaker_consistency** (audio/reject) {"windows": 25, "window_median": 0.722, "window_min": 0.604, "scene_min": 0.687, "median_f0": 170, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ⚠️ **music_under_speech** (audio/warn) {"median_db": 11.7, "p10_db": 2.6, "voice_gain": 3.687, "frames": 107}
    - speech-band narration only 11.7 dB above the bed (target ≥12 dB)
- ✅ **captions** (final/warn) {"groups": 43, "timing": "timeline.json", "engine_version": 3}
- ✅ **caption_overflow** (final/reject) {"widest_px": 851, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 21, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 8: stroke energy in the caption zone (bottom 25%) 1.88 > p90 1.519
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0010/hi/C0010-hi.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
