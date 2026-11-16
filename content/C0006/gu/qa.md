# QA report: C0006-gu.mp4

**Verdict: WARN** · 2026-11-16T21:26:45+0530 · report #59

File sha256: `f411071601fbb4ec286794513079dc240166301faa5c48878865fe1b32216834`

- **Story** 100/100 PASS
- **Visual** 33/100 NOT PASSED · warn: chalk_density, safe_zones
- **Audio** 80/100 PASS · warn: narration_asr
- **Final** 94/100 PASS · warn: duration_target

- ✅ **lint_duration** (story/warn) {"estimate_s": 54.27, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 55.3}
- ✅ **duration** (final/reject) {"seconds": 55.3}
- ⚠️ **duration_target** (final/warn) {"seconds": 55.3}
    - duration 55.30 s outside 35–55 s
- ✅ **loudness** (final/reject) {"lufs": -14.0, "true_peak_dbfs": -1.9, "lra": 3.4}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2624, "t0.5": 0.2915} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 4: CER 0.222 length ratio 0.89 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.819}
- ✅ **speaker_consistency** (audio/reject) {"windows": 23, "window_median": 0.7, "window_min": 0.522, "scene_min": 0.619, "median_f0": 171, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 13.5, "p10_db": 6.1, "voice_gain": 3.739, "frames": 106}
- ✅ **captions** (final/warn) {"groups": 43, "timing": "timeline.json", "engine_version": 2}
- ✅ **caption_overflow** (final/reject) {"widest_px": 864, "limit_px": 1020}
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

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0006/gu/C0006-gu.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
