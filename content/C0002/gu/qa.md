# QA report: C0002-gu.mp4

**Verdict: WARN** · 2026-11-16T17:38:23+0530 · report #44

File sha256: `8eca003f303fcdc92465ec8cf19e9a1cf104c2217b695e1f1606b95828e160c1`

- **Story** 45/100 NOT PASSED · warn: lint_duration, lint_hook, lint_scene_count, lint_scene_length, lint_edition, lint_silences
- **Visual** 67/100 NOT PASSED · warn: safe_zones
- **Audio** 60/100 NOT PASSED · warn: narration_asr, music_under_speech
- **Final** 87/100 PASS · warn: duration, duration_target

- ⚠️ **lint_duration** (story/warn) {"estimate_s": 102.01, "basis": "letters", "exempt": "back-catalogue: en/hi published before the 60 s rule; gu/te mirror them scene by scene"}
    - estimated 102.0 s > 57 s (rate 2.111 w/s, 216 words, pauses 4.45 s, lead/tail 1.15 s)
- ⚠️ **lint_hook** (story/warn) {"exempt": "back-catalogue: en/hi published before the 60 s rule; gu/te mirror them scene by scene"}
    - hook scene spoken 6.5 s > 3.0 s
- ⚠️ **lint_scene_count** (story/warn) {}
    - 12 scenes (target 8–11)
- ⚠️ **lint_scene_length** (story/warn) {}
    - scene 2 spoken 9.3 s (target 2.5–7.0 s)
    - scene 3 spoken 10.7 s (target 2.5–7.0 s)
    - scene 4 spoken 10.0 s (target 2.5–7.0 s)
    - scene 5 spoken 7.7 s (target 2.5–7.0 s)
    - scene 6 spoken 7.2 s (target 2.5–7.0 s)
    - scene 9 spoken 8.2 s (target 2.5–7.0 s)
    - scene 10 spoken 7.4 s (target 2.5–7.0 s)
    - scene 11 spoken 8.6 s (target 2.5–7.0 s)
    - scene 12 spoken 9.6 s (target 2.5–7.0 s)
- ✅ **lint_keywords** (story/warn) {}
- ✅ **lint_digits** (story/warn) {}
- ✅ **lint_quote_src** (story/warn) {}
- ✅ **lint_sources** (story/warn) {}
- ⚠️ **lint_edition** (story/warn) {}
    - scene 3: verse card has no edition label (scene or script 'edition')
    - script has no 'edition' (which text edition the sources cite)
- ⚠️ **lint_silences** (story/warn) {}
    - 12 planned silences (pause ≥0.3 s); target 2–3
- ✅ **lint_visual_parity** (story/warn) {}
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 104.0}
- ⚠️ **duration** (final/warn) {"seconds": 104.0, "exempt": "back-catalogue: en/hi published before the 60 s rule; gu/te mirror them scene by scene"}
    - duration 104.00 s ≥ 60.0 s
- ⚠️ **duration_target** (final/warn) {"seconds": 104.0}
    - duration 104.00 s outside 35–55 s
- ✅ **loudness** (final/reject) {"lufs": -15.0, "true_peak_dbfs": -1.4, "lra": 2.3}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.0021, "t0.5": 0.2298} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["QA cache (wav hash)"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 2: CER 0.278 length ratio 0.8 (warn) — listen and regenerate if mispronounced
    - scene 3: CER 0.323 length ratio 0.73 (warn) — listen and regenerate if mispronounced
    - scene 4: CER 0.241 length ratio 0.76 (warn) — listen and regenerate if mispronounced
    - scene 11: CER 0.22 length ratio 0.84 (warn) — listen and regenerate if mispronounced
    - scene 12: CER 0.25 length ratio 0.8 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.819}
- ✅ **speaker_consistency** (audio/reject) {"windows": 61, "window_median": 0.698, "window_min": 0.463, "scene_min": 0.641, "median_f0": 164, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ⚠️ **music_under_speech** (audio/warn) {"median_db": 9.6, "p10_db": 3.6, "voice_gain": 1.0, "frames": 181}
    - speech-band narration only 9.6 dB above the bed (target ≥12 dB)
- ✅ **captions** (final/warn) {"groups": 80}
- ✅ **caption_overflow** (final/reject) {"widest_px": 791, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 21}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 12}
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 9: stroke energy in the caption zone (bottom 25%) 1.66 > p90 1.519
    - scene 10: stroke energy in the caption zone (bottom 25%) 1.63 > p90 1.519
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0002/gu/C0002-gu.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
