# QA report: valmiki-ramayana-episode-01-english.mp4

**Verdict: WARN** · 2026-11-15T22:46:24+0530

- ✅ **format** {"video": "h264", "audio": "aac", "fps": 30.0, "seconds": 74.8}
- ✅ **loudness** {"lufs": -15.4, "true_peak_dbfs": -1.5, "lra": 2.0}
- ✅ **black_freeze** {"black": 0, "freeze": 0}
- ✅ **silence** {"gaps": 0}
- ⚠️ **narration_asr** {"note": "digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear"}
    - scene 12: CER 0.276 length ratio 0.81 — listen and regenerate if mispronounced
- ⚠️ **captions** {"groups": 59}
    - scene 3: caption 'The wandering sage Narada' too wide (984px)
    - scene 4: caption 'with his disciple Bharadvaja.' too wide (1001px)
    - scene 5: caption 'birds were singing together,' too wide (991px)
    - scene 11: caption 'Brahma the creator appeared,' too wide (1063px)
    - scene 12: caption 'twenty-four thousand verses,' too wide (1059px)

Contact sheet: `out/ramayana-ep-01-maharishi-valmiki-the-birth-of-the-ramayana/final/valmiki-ramayana-episode-01-english.qa.png`

Manual review still required: character consistency, visual defects / wrong illustrations, storytelling quality, native-speaker listen for non-English
