# QA report: C0010-mr.mp4

**Verdict: WARN** · 2026-11-18T15:17:07+0530 · report #122

File sha256: `58b4f13513fa0aa00a3e2c3a46513a5a096b3f1b434203ed01eac504d25b492f`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 67/100 NOT PASSED · warn: safe_zones
- **Audio** 80/100 PASS · warn: narration_asr
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 54.08, "basis": "letters"}
- ⚠️ **lint_hook** (story/warn) {}
    - hook scene spoken 2.6 s > 2.2 s
- ✅ **lint_scene_count** (story/warn) {}
- ✅ **lint_scene_length** (story/warn) {}
- ✅ **lint_keywords** (story/warn) {}
- ✅ **lint_digits** (story/warn) {}
- ✅ **lint_quote_src** (story/warn) {}
- ✅ **lint_sources** (story/warn) {}
- ✅ **lint_edition** (story/warn) {}
- ✅ **lint_silences** (story/warn) {}
- ✅ **lint_visual_parity** (story/warn) {}
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 52.4}
- ✅ **duration** (final/reject) {"seconds": 52.4}
- ✅ **duration_target** (final/warn) {"seconds": 52.4}
- ✅ **loudness** (final/reject) {"lufs": -13.9, "true_peak_dbfs": -2.0, "lra": 2.9}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2784, "t0.5": 0.319} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 2: CER 0.172 length ratio 0.97 (warn) — listen and regenerate if mispronounced
    - scene 4: CER 0.156 length ratio 0.97 (warn) — listen and regenerate if mispronounced
    - scene 10: CER 0.161 length ratio 0.94 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 6.037}
- ✅ **speaker_consistency** (audio/reject) {"windows": 22, "window_median": 0.717, "window_min": 0.589, "scene_min": 0.712, "median_f0": 191, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 13.3, "p10_db": 2.5, "voice_gain": 3.305, "frames": 101}
- ✅ **captions** (final/warn) {"groups": 38, "timing": "timeline.json", "engine_version": 3}
- ✅ **caption_overflow** (final/reject) {"widest_px": 771, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 21, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 8: stroke energy in the caption zone (bottom 25%) 1.88 > p90 1.519
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0010/mr/C0010-mr.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
