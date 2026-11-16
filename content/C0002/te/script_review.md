# C0002 Telugu script review (fallback, non-native)

This review was done by a model, not a native Telugu speaker, so it is not native-level evidence. It checks each scene against the approved en/hi versions for factual drift, plus grammar, naturalness (Hindi or English calques), honorifics (sages take the honorific plural), TTS risk, digits, keywords and the verse transliteration. A native listen is still required because `profiles/languages/te.json` has status `draft`.

Automated checks: no digits in any narration; every keyword is an exact whitespace token of its narration; all letters are in the language's own script (the only other characters are the em dash, ellipsis and danda/double danda).

Scene 3 `devanagari`: కో న్వస్మిన్ సామ్ప్రతం లోకే / గుణవాన్ కశ్చ వీర్యవాన్। / ధర్మజ్ఞశ్చ కృతజ్ఞశ్చ / సత్యవాక్యో దృఢవ్రతః॥ matches 1.1.2 letter for letter. High confidence.

| Scene | Issue | Suggested exact replacement | Confidence |
|---|---|---|---|
| 1 | ఒకే ప్రశ్న leans toward "the same / a single question". ఒక ప్రశ్న is the plain hook. Both are acceptable. | No change | low |
| 2 | Consistency: C0001 and hi use దేవర్షి నారదులు / देवर्षि नारद, but here it is నారద మహర్షి. This is not wrong. | Optional: క్రౌంచ పక్షి సంఘటనకు ముందు, దేవర్షి నారదులు వాల్మీకి ఆశ్రమానికి వచ్చారు. అప్పుడు వాల్మీకి మహర్షి ఆయనను ఒక ప్రశ్న అడిగారు. (keyword నారద → నారదులు) | low |
| 3 | None found | No change | high |
| 4 | None found | No change | high |
| 5 | None found | No change | high |
| 6 | None found. The honorific అన్నారు and వినండి are correct. | No change | high |
| 7 | None found | No change | high |
| 8 | None found | No change | high |
| 9 | ఎత్తితే (conditional) with వణికిపోయేవారు (past habitual) is acceptable. ఎత్తినప్పుడు would be smoother. | Optional: …యుద్ధంలో అతను విల్లు ఎత్తినప్పుడు, దేవతలు కూడా వణికిపోయేవారు. | low |
| 10 | None found | No change | high |
| 11 | None found | No change | high |
| 12 | None found | No change | high |
| all | TTS risk words: క్రౌంచ, కృతజ్ఞుడు, ఇక్ష్వాకు, సింహాసనాన్నే, నిషాదరాజు. | Listen and re-take if needed | medium |

**Verdict:** clean, natural and faithful to en/hi, with correct honorifics. No changes are needed. A native listen is still required.
