# QA report: C0003-gu.mp4

**Verdict: WARN** · 2026-11-16T15:18:42+0530

- ✅ **format** {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 108.5}
- ✅ **loudness** {"lufs": -14.6, "true_peak_dbfs": -1.4, "lra": 2.3}
- ✅ **black_freeze** {"black": 0, "freeze": 0}
- ✅ **silence** {"gaps": 0}
- ⚠️ **narration_asr** {"note": "digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear"}
    - scene 4: CER 0.206 length ratio 0.94 — listen and regenerate if mispronounced
    - scene 5: CER 0.222 length ratio 0.94 — listen and regenerate if mispronounced
    - scene 6: CER 0.385 length ratio 0.69 — listen and regenerate if mispronounced
    - scene 8: CER 0.217 length ratio 0.89 — listen and regenerate if mispronounced
    - scene 9: CER 0.212 length ratio 0.83 — listen and regenerate if mispronounced
    - scene 10: CER 0.204 length ratio 0.81 — listen and regenerate if mispronounced
    - scene 11: CER 0.241 length ratio 0.78 — listen and regenerate if mispronounced
    - scene 13: CER 0.263 length ratio 0.77 — listen and regenerate if mispronounced
- ✅ **captions** {"groups": 77}
- ✅ **speaker_consistency** {"windows": 62, "window_median": 0.699, "window_min": 0.529, "scene_min": 0.718, "median_f0": 179, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0003/gu/C0003-gu.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
