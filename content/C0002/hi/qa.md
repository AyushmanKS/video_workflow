# QA report: C0002-hi.mp4

**Verdict: PASS** · 2026-11-16T00:21:43+0530

- ✅ **format** {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 94.9}
- ✅ **loudness** {"lufs": -15.4, "true_peak_dbfs": -1.4, "lra": 2.4}
- ✅ **black_freeze** {"black": 0, "freeze": 0}
- ✅ **silence** {"gaps": 0}
- ✅ **narration_asr** {"note": "digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear"}
- ✅ **captions** {"groups": 83}

Contact sheet: `/Users/ayushman/Desktop/work/shorts-studio/content/C0002/hi/C0002-hi.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English

## Manual review (video-qa / language-qa)
- Same visual fixes as EN. Hindi thumbnail regenerated (a voice-takes overwrite bug had reverted it; the bug is fixed in pipeline/takes.py).
- Sanskrit verse (scene 3): pronunciation hint with pauses plus 5 takes; take 4 kept for the clearest Sanskrit. Whole-scene CER is dominated by the Hindi half, so the take was selected by ear-proxy review of the verse portion.
- Caption checker false positives (sentence-initial पर = "but", Sanskrit को = "who") fixed in pipeline/qa.py.
- Verdict: **pass**. A native Hindi listen by the owner is recommended (profile status: in use).
