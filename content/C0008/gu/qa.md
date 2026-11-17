# QA report: C0008-gu.mp4

**Verdict: WARN** · 2026-11-17T11:25:13+0530 · report #84

File sha256: `f106fce0f1a9769bcb6563789b943f720dab7be659b0df4d0407ea46b17a1073`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 33/100 NOT PASSED · warn: chalk_density, safe_zones
- **Audio** 80/100 PASS · warn: narration_asr
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 52.96, "basis": "letters"}
- ⚠️ **lint_hook** (story/warn) {}
    - hook scene spoken 2.8 s > 2.2 s
- ✅ **lint_scene_count** (story/warn) {}
- ✅ **lint_scene_length** (story/warn) {}
- ✅ **lint_keywords** (story/warn) {}
- ✅ **lint_digits** (story/warn) {}
- ✅ **lint_quote_src** (story/warn) {}
- ✅ **lint_sources** (story/warn) {}
- ✅ **lint_edition** (story/warn) {}
- ✅ **lint_silences** (story/warn) {}
- ✅ **lint_visual_parity** (story/warn) {}
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 53.1}
- ✅ **duration** (final/reject) {"seconds": 53.1}
- ✅ **duration_target** (final/warn) {"seconds": 53.1}
- ✅ **loudness** (final/reject) {"lufs": -14.1, "true_peak_dbfs": -1.9, "lra": 3.4}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2583, "t0.5": 0.2823} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 4: CER 0.19 length ratio 1.0 (warn) — listen and regenerate if mispronounced
    - scene 10: CER 0.2 length ratio 0.92 (warn) — listen and regenerate if mispronounced
    - scene 11: CER 0.161 length ratio 0.94 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.808}
- ✅ **speaker_consistency** (audio/reject) {"windows": 23, "window_median": 0.723, "window_min": 0.57, "scene_min": 0.713, "median_f0": 185, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 13.2, "p10_db": 6.3, "voice_gain": 3.893, "frames": 102}
- ✅ **captions** (final/warn) {"groups": 39, "timing": "timeline.json", "engine_version": 2}
- ✅ **caption_overflow** (final/reject) {"widest_px": 820, "limit_px": 1020}
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

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0008/gu/C0008-gu.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
