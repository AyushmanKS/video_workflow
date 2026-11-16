# QA report: C0001-gu.mp4

**Verdict: WARN** · 2026-11-16T12:54:53+0530

- ✅ **format** {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 101.63}
- ✅ **loudness** {"lufs": -14.7, "true_peak_dbfs": -1.4, "lra": 2.8}
- ✅ **black_freeze** {"black": 0, "freeze": 0}
- ✅ **silence** {"gaps": 0}
- ⚠️ **narration_asr** {"note": "digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear"}
    - scene 1: CER 0.188 length ratio 0.9 — listen and regenerate if mispronounced
    - scene 3: CER 0.192 length ratio 0.85 — listen and regenerate if mispronounced
    - scene 10: CER 0.231 length ratio 0.85 — listen and regenerate if mispronounced
    - scene 11: CER 0.184 length ratio 0.92 — listen and regenerate if mispronounced
    - scene 12: CER 0.333 length ratio 0.86 — Whisper wrote digits where the script has number words; likely a false positive
- ✅ **captions** {"groups": 75}
- ✅ **speaker_consistency** {"windows": 58, "window_median": 0.685, "window_min": 0.55, "scene_min": 0.744, "median_f0": 173, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0001/gu/C0001-gu.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
