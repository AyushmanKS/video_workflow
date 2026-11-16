# QA report: C0001-te.mp4

**Verdict: WARN** · 2026-11-16T13:01:48+0530

- ✅ **format** {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 111.23}
- ✅ **loudness** {"lufs": -14.6, "true_peak_dbfs": -1.4, "lra": 2.7}
- ✅ **black_freeze** {"black": 0, "freeze": 0}
- ✅ **silence** {"gaps": 0}
- ⚠️ **narration_asr** {"note": "digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear"}
    - scene 12: CER 0.28 length ratio 0.77 — listen and regenerate if mispronounced
- ✅ **captions** {"groups": 90}
- ✅ **speaker_consistency** {"windows": 64, "window_median": 0.752, "window_min": 0.584, "scene_min": 0.771, "median_f0": 168, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0001/te/C0001-te.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
