# QA report: C0013-hi.mp4

**Verdict: WARN** · 2026-11-24T22:08:58+0530 · report #158

File sha256: `0f7f9ad701b600b6fcf4a04c1d194fab5717f2b7604bee656320a07af71a0e3e`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 33/100 NOT PASSED · warn: chalk_density, safe_zones
- **Audio** 60/100 NOT PASSED · warn: narration_asr, speech_rate
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 51.81, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 54.7}
- ✅ **duration** (final/reject) {"seconds": 54.7}
- ✅ **duration_target** (final/warn) {"seconds": 54.7}
- ✅ **loudness** (final/reject) {"lufs": -14.0, "true_peak_dbfs": -1.9, "lra": 2.9}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2807, "t0.5": 0.3252} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear
    - scene 11: CER 0.192 length ratio 0.92 (warn) — listen and regenerate if mispronounced
- ⚠️ **speech_rate** (audio/warn) {"reference_letters_per_s": 6.114}
    - scene 7: speech rate -32% vs hi reference
- ✅ **speaker_consistency** (audio/reject) {"windows": 25, "window_median": 0.7, "window_min": 0.589, "scene_min": 0.636, "median_f0": 159, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 12.1, "p10_db": 1.0, "voice_gain": 3.652, "frames": 107}
- ✅ **captions** (final/warn) {"groups": 43, "timing": "timeline.json", "engine_version": 3}
- ✅ **caption_overflow** (final/reject) {"widest_px": 712, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 21, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ⚠️ **chalk_density** (visual/warn) {}
    - scene 8: chalk density 47.6% outside 3%–45%
    - scene 11: chalk density 47.4% outside 3%–45%
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 3: stroke energy in the title zone (top 12%) 0.13 > p90 0.111
    - scene 8: stroke energy in the title zone (top 12%) 0.16 > p90 0.111
    - scene 10: stroke energy in the title zone (top 12%) 0.40 > p90 0.111
    - scene 10: stroke energy in the caption zone (bottom 25%) 2.23 > p90 1.519
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0013/hi/C0013-hi.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
