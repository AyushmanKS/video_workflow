# QA report: C0005-gu.mp4

**Verdict: WARN** · 2026-11-16T12:08:32+0530

- ✅ **format** {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 107.47}
- ✅ **loudness** {"lufs": -14.7, "true_peak_dbfs": -1.4, "lra": 2.1}
- ✅ **black_freeze** {"black": 0, "freeze": 0}
- ✅ **silence** {"gaps": 0}
- ⚠️ **narration_asr** {"note": "digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear"}
    - scene 1: CER 0.188 length ratio 0.85 — listen and regenerate if mispronounced
    - scene 3: CER 0.163 length ratio 0.96 — listen and regenerate if mispronounced
    - scene 6: CER 0.174 length ratio 1.0 — listen and regenerate if mispronounced
    - scene 7: CER 0.316 length ratio 0.72 — listen and regenerate if mispronounced
    - scene 8: CER 0.212 length ratio 0.81 — listen and regenerate if mispronounced
    - scene 12: CER 0.462 length ratio 0.56 — listen and regenerate if mispronounced
    - scene 13: CER 0.377 length ratio 0.7 — listen and regenerate if mispronounced
- ✅ **captions** {"groups": 78}
- ✅ **speaker_consistency** {"windows": 62, "window_median": 0.718, "window_min": 0.565, "scene_min": 0.723, "median_f0": 178, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0005/gu/C0005-gu.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
