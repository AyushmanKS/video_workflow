# QA report: C0004-te.mp4

**Verdict: WARN** · 2026-11-16T15:11:04+0530

- ✅ **format** {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 99.47}
- ✅ **loudness** {"lufs": -14.7, "true_peak_dbfs": -1.4, "lra": 2.5}
- ✅ **black_freeze** {"black": 0, "freeze": 0}
- ✅ **silence** {"gaps": 0}
- ⚠️ **narration_asr** {"note": "digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear"}
    - scene 4: CER 0.182 length ratio 0.89 — listen and regenerate if mispronounced
- ✅ **captions** {"groups": 78}
- ✅ **speaker_consistency** {"windows": 55, "window_median": 0.758, "window_min": 0.571, "scene_min": 0.772, "median_f0": 167, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0004/te/C0004-te.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
