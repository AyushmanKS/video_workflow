# QA report: C0010-te.mp4

**Verdict: WARN** · 2026-11-18T15:01:31+0530 · report #121

File sha256: `924b1b30ca7b30290155ecb325b9df579d0f3278003344fb81d721c39741f072`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 67/100 NOT PASSED · warn: safe_zones
- **Audio** 80/100 PASS · warn: narration_asr
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 53.65, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 54.57}
- ✅ **duration** (final/reject) {"seconds": 54.57}
- ✅ **duration_target** (final/warn) {"seconds": 54.57}
- ✅ **loudness** (final/reject) {"lufs": -14.0, "true_peak_dbfs": -1.8, "lra": 2.5}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2787, "t0.5": 0.3204} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 1: CER 0.214 length ratio 0.79 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.928}
- ✅ **speaker_consistency** (audio/reject) {"windows": 24, "window_median": 0.738, "window_min": 0.616, "scene_min": 0.64, "median_f0": 185, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 12.9, "p10_db": 0.8, "voice_gain": 3.634, "frames": 107}
- ✅ **captions** (final/warn) {"groups": 46, "timing": "timeline.json", "engine_version": 3}
- ✅ **caption_overflow** (final/reject) {"widest_px": 874, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 21, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 8: stroke energy in the caption zone (bottom 25%) 1.88 > p90 1.519
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0010/te/C0010-te.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
