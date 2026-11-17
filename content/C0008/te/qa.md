# QA report: C0008-te.mp4

**Verdict: WARN** · 2026-11-17T11:25:22+0530 · report #85

File sha256: `82a910a29afbde674d639e1ad8dde801ca390edc80845b0fb9f41f917c8a17a4`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 33/100 NOT PASSED · warn: chalk_density, safe_zones
- **Audio** 80/100 PASS · warn: narration_asr
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 52.98, "basis": "letters"}
- ⚠️ **lint_hook** (story/warn) {}
    - hook scene spoken 2.9 s > 2.2 s
- ✅ **lint_scene_count** (story/warn) {}
- ✅ **lint_scene_length** (story/warn) {}
- ✅ **lint_keywords** (story/warn) {}
- ✅ **lint_digits** (story/warn) {}
- ✅ **lint_quote_src** (story/warn) {}
- ✅ **lint_sources** (story/warn) {}
- ✅ **lint_edition** (story/warn) {}
- ✅ **lint_silences** (story/warn) {}
- ✅ **lint_visual_parity** (story/warn) {}
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 51.83}
- ✅ **duration** (final/reject) {"seconds": 51.83}
- ✅ **duration_target** (final/warn) {"seconds": 51.83}
- ✅ **loudness** (final/reject) {"lufs": -13.9, "true_peak_dbfs": -1.9, "lra": 3.1}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2641, "t0.5": 0.2893} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 1: CER 0.176 length ratio 0.94 (warn) — listen and regenerate if mispronounced
    - scene 4: CER 0.16 length ratio 1.0 (warn) — listen and regenerate if mispronounced
    - scene 8: CER 0.16 length ratio 1.0 (warn) — listen and regenerate if mispronounced
    - scene 9: CER 0.214 length ratio 0.89 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.928}
- ✅ **speaker_consistency** (audio/reject) {"windows": 21, "window_median": 0.771, "window_min": 0.597, "scene_min": 0.627, "median_f0": 179, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 12.2, "p10_db": 5.7, "voice_gain": 3.555, "frames": 99}
- ✅ **captions** (final/warn) {"groups": 44, "timing": "timeline.json", "engine_version": 2}
- ✅ **caption_overflow** (final/reject) {"widest_px": 912, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 21, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ⚠️ **chalk_density** (visual/warn) {}
    - scene 3: chalk density 47.8% outside 3%–45%
    - scene 4: chalk density 47.4% outside 3%–45%
    - scene 5: chalk density 46.5% outside 3%–45%
    - scene 11: chalk density 48.3% outside 3%–45%
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 2: stroke energy in the title zone (top 12%) 0.33 > p90 0.111
    - scene 5: stroke energy in the title zone (top 12%) 0.13 > p90 0.111
    - scene 8: stroke energy in the title zone (top 12%) 0.12 > p90 0.111
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0008/te/C0008-te.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
