# QA report: C0002-te.mp4

**Verdict: WARN** · 2026-11-16T13:58:10+0530

- ✅ **format** {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 105.27}
- ✅ **loudness** {"lufs": -14.6, "true_peak_dbfs": -1.4, "lra": 2.2}
- ✅ **black_freeze** {"black": 0, "freeze": 0}
- ✅ **silence** {"gaps": 0}
- ⚠️ **narration_asr** {"note": "digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear"}
    - scene 1: CER 0.152 length ratio 1.03 — listen and regenerate if mispronounced
- ✅ **captions** {"groups": 84}
- ✅ **speaker_consistency** {"windows": 61, "window_median": 0.754, "window_min": 0.469, "scene_min": 0.674, "median_f0": 168, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0002/te/C0002-te.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
