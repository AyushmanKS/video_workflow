# QA report: C0004-gu.mp4

**Verdict: WARN** · 2026-11-16T17:54:21+0530 · report #48

File sha256: `325dc14abf5f94af00e4ee9cb29fec84bf685e2757bf104a4ef10b273c4e8a8d`

- **Story** 45/100 NOT PASSED · warn: lint_duration, lint_hook, lint_scene_count, lint_scene_length, lint_edition, lint_silences
- **Visual** 67/100 NOT PASSED · warn: safe_zones
- **Audio** 60/100 NOT PASSED · warn: narration_asr, music_under_speech
- **Final** 87/100 PASS · warn: duration, duration_target

- ⚠️ **lint_duration** (story/warn) {"estimate_s": 95.31, "basis": "letters", "exempt": "back-catalogue: en/hi published before the 60 s rule; gu/te mirror them scene by scene"}
    - estimated 95.3 s > 57 s (rate 2.111 w/s, 186 words, pauses 4.8 s, lead/tail 1.15 s)
- ⚠️ **lint_hook** (story/warn) {"exempt": "back-catalogue: en/hi published before the 60 s rule; gu/te mirror them scene by scene"}
    - hook scene spoken 6.7 s > 3.0 s
- ⚠️ **lint_scene_count** (story/warn) {}
    - 13 scenes (target 8–11)
- ⚠️ **lint_scene_length** (story/warn) {}
    - scene 4 spoken 10.8 s (target 2.5–7.0 s)
    - scene 6 spoken 8.2 s (target 2.5–7.0 s)
    - scene 8 spoken 7.0 s (target 2.5–7.0 s)
    - scene 12 spoken 8.4 s (target 2.5–7.0 s)
    - scene 13 spoken 8.1 s (target 2.5–7.0 s)
- ✅ **lint_keywords** (story/warn) {}
- ✅ **lint_digits** (story/warn) {}
- ✅ **lint_quote_src** (story/warn) {}
- ✅ **lint_sources** (story/warn) {}
- ⚠️ **lint_edition** (story/warn) {}
    - scene 6: verse card has no edition label (scene or script 'edition')
    - script has no 'edition' (which text edition the sources cite)
- ⚠️ **lint_silences** (story/warn) {}
    - 13 planned silences (pause ≥0.3 s); target 2–3
- ✅ **lint_visual_parity** (story/warn) {}
- ✅ **format** (final/reject) {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 93.3}
- ⚠️ **duration** (final/warn) {"seconds": 93.3, "exempt": "back-catalogue: en/hi published before the 60 s rule; gu/te mirror them scene by scene"}
    - duration 93.30 s ≥ 60.0 s
- ⚠️ **duration_target** (final/warn) {"seconds": 93.3}
    - duration 93.30 s outside 35–55 s
- ✅ **loudness** (final/reject) {"lufs": -14.7, "true_peak_dbfs": -1.5, "lra": 2.4}
- ✅ **black_freeze** (final/reject) {"black": 0, "freeze": 0}
- ✅ **silence** (final/warn) {"gaps": 0}
- ✅ **first_frame** (final/warn) {"t0.0": 0.0021, "t0.5": 0.2584} — style decision: warn only
- ⚠️ **narration_asr** (audio/warn) {"transcripts": ["whisper large-v3-turbo"]} — CER is warn-only for this language until Indic ASR is validated
    - scene 1: CER 0.179 length ratio 1.0 (warn) — listen and regenerate if mispronounced
    - scene 4: CER 0.381 length ratio 0.7 (warn) — listen and regenerate if mispronounced
    - scene 12: CER 0.163 length ratio 0.84 (warn) — listen and regenerate if mispronounced
- ✅ **speech_rate** (audio/warn) {"reference_letters_per_s": 5.819}
- ✅ **speaker_consistency** (audio/reject) {"windows": 52, "window_median": 0.718, "window_min": 0.533, "scene_min": 0.73, "median_f0": 168, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}
- ⚠️ **music_under_speech** (audio/warn) {"median_db": 10.5, "p10_db": 3.2, "voice_gain": 1.0, "frames": 170}
    - speech-band narration only 10.5 dB above the bed (target ≥12 dB)
- ✅ **captions** (final/warn) {"groups": 65}
- ✅ **caption_overflow** (final/reject) {"widest_px": 782, "limit_px": 1020}
- ✅ **glyph_coverage** (final/reject) {"texts": 25}
- ⏭️ **text_artifacts** (visual/warn) {} — tesseract binary not installed (brew install tesseract, Apache-2.0); skipped
- ✅ **near_duplicates** (visual/warn) {"images": 13}
- ✅ **chalk_density** (visual/warn) {}
- ⚠️ **safe_zones** (visual/warn) {"calibration": {"top_p90": 0.111, "bottom_p90": 1.519, "n": 243}}
    - scene 8: stroke energy in the title zone (top 12%) 0.16 > p90 0.111
- ⏭️ **character_similarity** (visual/warn) {"model_present": false} — DINOv2 similarity is a human flag only; model not present locally and not downloaded

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0004/gu/C0004-gu.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
