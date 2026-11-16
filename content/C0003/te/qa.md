# QA report: C0003-te.mp4

**Verdict: WARN** · 2026-11-16T17:48:32+0530 · report #47

File sha256: `b36b13b0f14f6a19b9da24a8000993cf5f812c2ad48bb94b16da80f8b1a8b56d`

- **Story** 45/100 NOT PASSED · warn: lint_duration, lint_hook, lint_scene_count, lint_scene_length, lint_edition, lint_silences
- **Visual** 67/100 NOT PASSED · warn: safe_zones
- **Audio** 80/100 PASS · warn: music_under_speech
- **Final** 87/100 PASS · warn: duration, duration_target

- ⚠️ **lint_duration** (story/warn) {"estimate_s": 109.81, "basis": "letters", "exempt": "back-catalogue: en/hi published before the 60 s rule; gu/te mirror them scene by scene"}
    - estimated 109.8 s > 57 s (rate 1.572 w/s, 155 words, pauses 4.8 s, lead/tail 1.15 s)
- ⚠️ **lint_hook** (story/warn) {"exempt": "back-catalogue: en/hi published before the 60 s rule; gu/te mirror them scene by scene"}
    - hook scene spoken 7.6 s > 3.0 s
- ⚠️ **lint_scene_count** (story/warn) {}
    - 13 scenes (target 8–11)
- ⚠️ **lint_scene_length** (story/warn) {}
    - scene 2 spoken 9.4 s (target 2.5–7.0 s)
    - scene 3 spoken 7.1 s (target 2.5–7.0 s)
    - scene 6 spoken 11.6 s (target 2.5–7.0 s)
    - scene 7 spoken 7.2 s (target 2.5–7.0 s)
    - scene 8 spoken 7.9 s (target 2.5–7.0 s)
    - scene 9 spoken 9.4 s (target 2.5–7.0 s)
    - scene 10 spoken 8.3 s (target 2.5–7.0 s)
    - scene 11 spoken 7.9 s (target 2.5–7.0 s)
    - scene 13 spoken 11.1 s (target 2.5–7.0 s)
- ✅ **lint_keywords** (story/warn) {}
- ✅ **lint_digits** (story/warn) {}
- ✅ **lint_quote_src** (story/warn) {}
- ✅ **lint_sources** (story/warn) {}
- ⚠️ **lint_edition** (story/warn) {}
    - scene 9: verse card has no edition label (scene or script 'edition')
    - script has no 'edition' (which text edition the sources cite)
- ⚠️ **lint_silences** (story/warn) {}
    - 13 planned silences (pause ≥0.3 s); target 2–3
- ✅ **lint_visual_parity** (story/warn) {}
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 109.07}
- ⚠️ **duration** (final/warn) {"seconds": 109.07, "exempt": "back-catalogue: en/hi published before the 60 s rule; gu/te mirror them scene by scene"}
    - duration 109.07 s ≥ 60.0 s
- ⚠️ **duration_target** (final/warn) {"seconds": 109.07}
    - duration 109.07 s outside 35–55 s
- ✅ **loudness** (final/reject) {"lufs": -14.4, "true_peak_dbfs": -1.5, "lra": 2.1}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.0021, "t0.5": 0.1378} — style decision: warn only
- ✅ **narration_asr** (audio/warn) {"transcripts": ["whisper large-v3-turbo"]} — CER is warn-only for this language until Indic ASR is validated
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.931}
- ✅ **speaker_consistency** (audio/reject) {"windows": 63, "window_median": 0.734, "window_min": 0.503, "scene_min": 0.735, "median_f0": 183, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ⚠️ **music_under_speech** (audio/warn) {"median_db": 11.3, "p10_db": 4.1, "voice_gain": 0.999, "frames": 201}
    - speech-band narration only 11.3 dB above the bed (target ≥12 dB)
- ✅ **captions** (final/warn) {"groups": 94}
- ✅ **caption_overflow** (final/reject) {"widest_px": 863, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 26}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 13}
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 8: stroke energy in the caption zone (bottom 25%) 2.15 > p90 1.519
    - scene 10: stroke energy in the title zone (top 12%) 0.12 > p90 0.111
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0003/te/C0003-te.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
