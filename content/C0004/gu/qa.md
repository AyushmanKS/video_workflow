# QA report: C0004-gu.mp4

**Verdict: WARN** · 2026-11-16T15:09:17+0530

- ✅ **format** {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 93.3}
- ✅ **loudness** {"lufs": -14.7, "true_peak_dbfs": -1.5, "lra": 2.4}
- ✅ **black_freeze** {"black": 0, "freeze": 0}
- ✅ **silence** {"gaps": 0}
- ⚠️ **narration_asr** {"note": "digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear"}
    - scene 1: CER 0.179 length ratio 1.0 — listen and regenerate if mispronounced
    - scene 4: CER 0.381 length ratio 0.7 — listen and regenerate if mispronounced
    - scene 12: CER 0.163 length ratio 0.84 — listen and regenerate if mispronounced
- ✅ **captions** {"groups": 63}
- ✅ **speaker_consistency** {"windows": 52, "window_median": 0.718, "window_min": 0.533, "scene_min": 0.73, "median_f0": 168, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0004/gu/C0004-gu.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
