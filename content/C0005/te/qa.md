# QA report: C0005-te.mp4

**Verdict: WARN** · 2026-11-16T11:54:04+0530

- ✅ **format** {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 111.2}
- ✅ **loudness** {"lufs": -14.7, "true_peak_dbfs": -1.4, "lra": 2.5}
- ✅ **black_freeze** {"black": 0, "freeze": 0}
- ✅ **silence** {"gaps": 0}
- ⚠️ **narration_asr** {"note": "digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear"}
    - scene 6: CER 0.167 length ratio 0.87 — listen and regenerate if mispronounced
    - scene 12: CER 0.26 length ratio 0.75 — listen and regenerate if mispronounced
    - scene 13: CER 0.247 length ratio 0.82 — listen and regenerate if mispronounced
- ⚠️ **captions** {"groups": 80}
    - scene 3: caption 'ఉండేవని మహర్షి చెప్పారు.' too wide (976px)
    - scene 13: caption 'దేవతలు జయజయధ్వానాలు' too wide (984px)
- ✅ **speaker_consistency** {"windows": 65, "window_median": 0.768, "window_min": 0.578, "scene_min": 0.77, "median_f0": 164, "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0005/te/C0005-te.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
