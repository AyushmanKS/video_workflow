# QA report: C0011-te.mp4

**Verdict: WARN** · 2026-11-18T23:10:53+0530 · report #133

File sha256: `4bfa71db32ece72d0cdf99aa376db4d39a9a582431f9f7124872fc38ac119580`

- **Story** 100/100 PASS
- **Visual** 33/100 NOT PASSED · warn: near_duplicates, safe_zones
- **Audio** 60/100 NOT PASSED · warn: narration_asr, speech_rate
- **Final** 100/100 PASS

- ✅ **lint_duration** (story/warn) {"estimate_s": 570.29, "basis": "letters"}
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
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 570.13}
- ✅ **duration** (final/reject) {"seconds": 570.13}
- ✅ **duration_target** (final/warn) {"seconds": 570.13}
- ✅ **loudness** (final/reject) {"lufs": -14.0, "true_peak_dbfs": -1.9, "lra": 3.1}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.2479, "t0.5": 0.2797} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["render-time transcript (heard.json)"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 10: CER 0.164 length ratio 0.85 (warn) — listen and regenerate if mispronounced
    - scene 16: CER 0.234 length ratio 0.86 (warn) — listen and regenerate if mispronounced
    - scene 24: CER 0.016 length ratio 1.26 (warn) — listen and regenerate if mispronounced
    - scene 28: CER 0.211 length ratio 1.25 (warn) — listen and regenerate if mispronounced
    - scene 30: CER 0.042 length ratio 1.58 (warn) — Whisper wrote digits where the script has number words; likely a false positive
    - scene 39: CER 0.222 length ratio 0.82 (warn) — listen and regenerate if mispronounced
    - scene 50: CER 0.119 length ratio 2.0 (warn) — listen and regenerate if mispronounced
- ⚠️ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.928}
    - scene 2: speech rate +26% vs te reference
- ✅ **speaker_consistency** (audio/reject) {"windows": 360, "window_median": 0.749, "window_min": 0.499, "scene_min": 0.787, "median_f0": 174, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ✅ **music_under_speech** (audio/warn) {"median_db": 14.6, "p10_db": 5.9, "voice_gain": 3.654, "frames": 1081}
- ✅ **captions** (final/warn) {"groups": 472, "timing": "timeline.json", "engine_version": 3, "tight_info": ["scene 15: 1001 px"]}
- ✅ **caption_overflow** (final/reject) {"widest_px": 1001, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 69, "fontset": "mac"}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ⚠️ **near_duplicates** (visual/warn) {"images": 50}
    - scenes 19 and 24: perceptual hash distance 6 bits (< 8)
    - scenes 30 and 38: perceptual hash distance 6 bits (< 8)
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 1: stroke energy in the title zone (top 12%) 1.25 > p90 0.111
    - scene 2: stroke energy in the title zone (top 12%) 1.16 > p90 0.111
    - scene 3: stroke energy in the title zone (top 12%) 0.13 > p90 0.111
    - scene 5: stroke energy in the title zone (top 12%) 0.78 > p90 0.111
    - scene 7: stroke energy in the title zone (top 12%) 0.15 > p90 0.111
    - scene 8: stroke energy in the title zone (top 12%) 0.16 > p90 0.111
    - scene 8: stroke energy in the caption zone (bottom 25%) 1.60 > p90 1.519
    - scene 9: stroke energy in the caption zone (bottom 25%) 1.91 > p90 1.519
    - scene 12: stroke energy in the title zone (top 12%) 0.32 > p90 0.111
    - scene 14: stroke energy in the title zone (top 12%) 0.75 > p90 0.111
    - scene 16: stroke energy in the title zone (top 12%) 0.43 > p90 0.111
    - scene 17: stroke energy in the title zone (top 12%) 0.76 > p90 0.111
    - scene 18: stroke energy in the title zone (top 12%) 0.17 > p90 0.111
    - scene 20: stroke energy in the title zone (top 12%) 0.20 > p90 0.111
    - scene 22: stroke energy in the title zone (top 12%) 0.23 > p90 0.111
    - scene 23: stroke energy in the title zone (top 12%) 0.57 > p90 0.111
    - scene 25: stroke energy in the title zone (top 12%) 0.29 > p90 0.111
    - scene 26: stroke energy in the title zone (top 12%) 0.44 > p90 0.111
    - scene 27: stroke energy in the title zone (top 12%) 0.59 > p90 0.111
    - scene 28: stroke energy in the title zone (top 12%) 0.12 > p90 0.111
    - scene 29: stroke energy in the title zone (top 12%) 0.15 > p90 0.111
    - scene 31: stroke energy in the title zone (top 12%) 0.12 > p90 0.111
    - scene 32: stroke energy in the title zone (top 12%) 0.95 > p90 0.111
    - scene 34: stroke energy in the title zone (top 12%) 0.96 > p90 0.111
    - scene 35: stroke energy in the title zone (top 12%) 0.64 > p90 0.111
    - scene 36: stroke energy in the title zone (top 12%) 0.80 > p90 0.111
    - scene 37: stroke energy in the title zone (top 12%) 0.23 > p90 0.111
    - scene 39: stroke energy in the title zone (top 12%) 0.66 > p90 0.111
    - scene 40: stroke energy in the title zone (top 12%) 0.19 > p90 0.111
    - scene 41: stroke energy in the title zone (top 12%) 0.52 > p90 0.111
    - scene 42: stroke energy in the title zone (top 12%) 0.95 > p90 0.111
    - scene 43: stroke energy in the caption zone (bottom 25%) 1.55 > p90 1.519
    - scene 45: stroke energy in the title zone (top 12%) 0.75 > p90 0.111
    - scene 46: stroke energy in the title zone (top 12%) 0.13 > p90 0.111
    - scene 47: stroke energy in the title zone (top 12%) 0.40 > p90 0.111
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0011/te/C0011-te.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
