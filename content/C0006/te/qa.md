# QA report: C0006-te.mp4

**Verdict: WARN** · 2026-11-16T21:26:55+0530 · report #60

File sha256: `81a571019647b56bbfd0c917d9aff9b9ceecc81f7b8157a161c5544faa9d5f49`

- **Story** 100/100 PASS
- **Visual** 33/100 NOT PASSED · warn: chalk_density, safe_zones
- **Audio** 100/100 PASS
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 53.83, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 54.1}
- ✅ **duration** (final/reject) {"seconds": 54.1}
- ✅ **duration_target** (final/warn) {"seconds": 54.1}
- ✅ **loudness** (final/reject) {"lufs": -13.9, "true_peak_dbfs": -1.4, "lra": 3.3}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2643, "t0.5": 0.291} — style decision: warn only
- ✅ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — CER is warn-only for this language until Indic ASR is validated
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.931}
- ✅ **speaker_consistency** (audio/reject) {"windows": 24, "window_median": 0.709, "window_min": 0.542, "scene_min": 0.661, "median_f0": 170, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 12.5, "p10_db": 5.4, "voice_gain": 3.731, "frames": 104}
- ✅ **captions** (final/warn) {"groups": 48, "timing": "timeline.json", "engine_version": 2}
- ✅ **caption_overflow** (final/reject) {"widest_px": 785, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 20, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ⚠️ **chalk_density** (visual/warn) {}
    - scene 2: chalk density 49.9% outside 3%–45%
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 1: stroke energy in the title zone (top 12%) 0.22 > p90 0.111
    - scene 2: stroke energy in the title zone (top 12%) 0.92 > p90 0.111
    - scene 3: stroke energy in the title zone (top 12%) 0.13 > p90 0.111
    - scene 4: stroke energy in the title zone (top 12%) 0.12 > p90 0.111
    - scene 6: stroke energy in the title zone (top 12%) 0.19 > p90 0.111
    - scene 7: stroke energy in the title zone (top 12%) 0.30 > p90 0.111
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0006/te/C0006-te.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
