# QA report: C0007-gu.mp4

**Verdict: WARN** · 2026-11-16T23:34:54+0530 · report #64

File sha256: `0ba35c4f012143598126468a9b7463212a5b0879c3774805eb2a45f1095b3151`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 67/100 NOT PASSED · warn: safe_zones
- **Audio** 80/100 PASS · warn: narration_asr
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 53.16, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 52.5}
- ✅ **duration** (final/reject) {"seconds": 52.5}
- ✅ **duration_target** (final/warn) {"seconds": 52.5}
- ✅ **loudness** (final/reject) {"lufs": -14.0, "true_peak_dbfs": -1.9, "lra": 2.9}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.1095, "t0.5": 0.137} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 2: CER 0.222 length ratio 0.93 (warn) — listen and regenerate if mispronounced
    - scene 10: CER 0.231 length ratio 0.96 (warn) — listen and regenerate if mispronounced
    - scene 11: CER 0.176 length ratio 1.03 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.808}
- ✅ **speaker_consistency** (audio/reject) {"windows": 24, "window_median": 0.716, "window_min": 0.519, "scene_min": 0.656, "median_f0": 187, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 13.4, "p10_db": 5.9, "voice_gain": 3.637, "frames": 96}
- ✅ **captions** (final/warn) {"groups": 42, "timing": "timeline.json", "engine_version": 2}
- ✅ **caption_overflow** (final/reject) {"widest_px": 851, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 20, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 1: stroke energy in the title zone (top 12%) 0.14 > p90 0.111
    - scene 1: stroke energy in the caption zone (bottom 25%) 1.92 > p90 1.519
    - scene 3: stroke energy in the title zone (top 12%) 0.12 > p90 0.111
    - scene 4: stroke energy in the title zone (top 12%) 0.18 > p90 0.111
    - scene 5: stroke energy in the title zone (top 12%) 0.35 > p90 0.111
    - scene 6: stroke energy in the title zone (top 12%) 0.27 > p90 0.111
    - scene 9: stroke energy in the title zone (top 12%) 1.20 > p90 0.111
    - scene 11: stroke energy in the caption zone (bottom 25%) 1.62 > p90 1.519
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0007/gu/C0007-gu.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
