# QA report: C0002-gu.mp4

**Verdict: WARN** · 2026-11-16T13:56:19+0530

- ✅ **format** {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 104.0}
- ✅ **loudness** {"lufs": -15.0, "true_peak_dbfs": -1.4, "lra": 2.3}
- ✅ **black_freeze** {"black": 0, "freeze": 0}
- ✅ **silence** {"gaps": 0}
- ⚠️ **narration_asr** {"note": "digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear"}
    - scene 2: CER 0.278 length ratio 0.8 — listen and regenerate if mispronounced
    - scene 3: CER 0.323 length ratio 0.73 — listen and regenerate if mispronounced
    - scene 4: CER 0.241 length ratio 0.76 — listen and regenerate if mispronounced
    - scene 11: CER 0.22 length ratio 0.84 — listen and regenerate if mispronounced
    - scene 12: CER 0.25 length ratio 0.8 — listen and regenerate if mispronounced
- ✅ **captions** {"groups": 75}
- ✅ **speaker_consistency** {"windows": 61, "window_median": 0.698, "window_min": 0.463, "scene_min": 0.641, "median_f0": 164, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0002/gu/C0002-gu.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
