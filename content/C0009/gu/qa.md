# QA report: C0009-gu.mp4

**Verdict: WARN** · 2026-11-17T15:13:11+0530 · report #97

File sha256: `f76c073ed514b380faa768ae3fea1fdec568b1b4373d4b92a206a8f854140374`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 33/100 NOT PASSED · warn: chalk_density, safe_zones
- **Audio** 80/100 PASS · warn: narration_asr
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 52.96, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 53.2}
- ✅ **duration** (final/reject) {"seconds": 53.2}
- ✅ **duration_target** (final/warn) {"seconds": 53.2}
- ✅ **loudness** (final/reject) {"lufs": -14.0, "true_peak_dbfs": -2.1, "lra": 2.8}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.3554, "t0.5": 0.3365} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 1: CER 0.214 length ratio 1.0 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.808}
- ✅ **speaker_consistency** (audio/reject) {"windows": 21, "window_median": 0.688, "window_min": 0.521, "scene_min": 0.741, "median_f0": 191, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 12.6, "p10_db": 6.1, "voice_gain": 3.964, "frames": 103}
- ✅ **captions** (final/warn) {"groups": 40, "timing": "timeline.json", "engine_version": 2}
- ✅ **caption_overflow** (final/reject) {"widest_px": 763, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 21, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ⚠️ **chalk_density** (visual/warn) {}
    - scene 1: chalk density 47.6% outside 3%–45%
    - scene 4: chalk density 58.4% outside 3%–45%
    - scene 10: chalk density 52.0% outside 3%–45%
    - scene 11: chalk density 60.0% outside 3%–45%
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 2: stroke energy in the caption zone (bottom 25%) 1.55 > p90 1.519
    - scene 3: stroke energy in the caption zone (bottom 25%) 2.01 > p90 1.519
    - scene 6: stroke energy in the caption zone (bottom 25%) 1.63 > p90 1.519
    - scene 8: stroke energy in the title zone (top 12%) 1.30 > p90 0.111
    - scene 10: stroke energy in the caption zone (bottom 25%) 1.60 > p90 1.519
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0009/gu/C0009-gu.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
