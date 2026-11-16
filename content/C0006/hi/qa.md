# QA report: C0006-hi.mp4

**Verdict: WARN** · 2026-11-16T21:26:35+0530 · report #58

File sha256: `5d08a8e8c70a55855f9274441d02c83f20f6c1a1fe6aa3270fd8af4fe34da061`

- **Story** 100/100 PASS
- **Visual** 33/100 NOT PASSED · warn: chalk_density, safe_zones
- **Audio** 80/100 PASS · warn: speech_rate
- **Final** 94/100 PASS · warn: duration_target

- ✅ **lint_duration** (story/warn) {"estimate_s": 53.51, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 56.03}
- ✅ **duration** (final/reject) {"seconds": 56.03}
- ⚠️ **duration_target** (final/warn) {"seconds": 56.03}
    - duration 56.03 s outside 35–55 s
- ✅ **loudness** (final/reject) {"lufs": -14.0, "true_peak_dbfs": -2.0, "lra": 2.9}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2614, "t0.5": 0.2905} — style decision: warn only
- ✅ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear
- ⚠️ **speech_rate** (audio/warn) {"reference_letters_per_s": 6.151}
    - scene 10: speech rate -26% vs hi reference
- ✅ **speaker_consistency** (audio/reject) {"windows": 26, "window_median": 0.723, "window_min": 0.557, "scene_min": 0.618, "median_f0": 176, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 12.1, "p10_db": 3.2, "voice_gain": 3.687, "frames": 108}
- ✅ **captions** (final/warn) {"groups": 49, "timing": "timeline.json", "engine_version": 2}
- ✅ **caption_overflow** (final/reject) {"widest_px": 723, "limit_px": 1020}
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

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0006/hi/C0006-hi.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
