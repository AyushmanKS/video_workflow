# QA report: C0007-hi.mp4

**Verdict: WARN** · 2026-11-16T23:55:30+0530 · report #69

File sha256: `41319529748bba23a0ddce69be8030f705403f8efa22d0cca98ac9fd4ea59378`

- **Story** 91/100 PASS · warn: lint_hook
- **Visual** 67/100 NOT PASSED · warn: safe_zones
- **Audio** 60/100 NOT PASSED · warn: narration_asr, music_under_speech
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 52.18, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 53.07}
- ✅ **duration** (final/reject) {"seconds": 53.07}
- ✅ **duration_target** (final/warn) {"seconds": 53.07}
- ✅ **loudness** (final/reject) {"lufs": -13.9, "true_peak_dbfs": -2.0, "lra": 2.8}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.207, "t0.5": 0.2428} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear
    - scene 10: CER 0.192 length ratio 1.0 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 6.114}
- ✅ **speaker_consistency** (audio/reject) {"windows": 23, "window_median": 0.734, "window_min": 0.588, "scene_min": 0.645, "median_f0": 177, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ⚠️ **music_under_speech** (audio/warn) {"median_db": 12.0, "p10_db": 1.7, "voice_gain": 3.634, "frames": 100}
    - speech-band narration only 12.0 dB above the bed (target ≥12 dB)
- ✅ **captions** (final/warn) {"groups": 43, "timing": "timeline.json", "engine_version": 2}
- ✅ **caption_overflow** (final/reject) {"widest_px": 780, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 20, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 11}
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 1: stroke energy in the caption zone (bottom 25%) 1.67 > p90 1.519
    - scene 3: stroke energy in the title zone (top 12%) 0.12 > p90 0.111
    - scene 4: stroke energy in the title zone (top 12%) 0.18 > p90 0.111
    - scene 5: stroke energy in the title zone (top 12%) 0.35 > p90 0.111
    - scene 6: stroke energy in the title zone (top 12%) 0.27 > p90 0.111
    - scene 9: stroke energy in the title zone (top 12%) 1.12 > p90 0.111
    - scene 11: stroke energy in the caption zone (bottom 25%) 1.62 > p90 1.519
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0007/hi/C0007-hi.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
