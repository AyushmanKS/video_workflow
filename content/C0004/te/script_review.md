# C0004 Telugu script review (fallback, non-native)

This review was done by a model, not a native Telugu speaker, so it is not native-level evidence. It checks each scene against the approved en/hi versions for factual drift, plus grammar, naturalness (Hindi or English calques), honorifics (sages take the honorific plural), TTS risk, digits, keywords and the verse transliteration. A native listen is still required because `profiles/languages/te.json` has status `draft`.

Automated checks: no digits in any narration; every keyword is an exact whitespace token of its narration; all letters are in the language's own script (the only other characters are the em dash, ellipsis and danda/double danda).

Scene 6 `devanagari`: ఊనషోడశవర్షో మే / రామో రాజీవలోచనః। / న యుద్ధయోగ్యతామస్య / పశ్యామి సహ రాక్షసైః॥ matches 1.20.2 letter for letter. High confidence.

| Scene | Issue | Suggested exact replacement | Confidence |
|---|---|---|---|
| 1 | None found | No change | high |
| 2 | None found. విచ్చేశారు is an apt honorific. | No change | high |
| 3 | None found | No change | high |
| 4 | The present progressive (చేస్తున్నారు, కావాలి) is used as reported speech inside a past narrative. That is acceptable. | No change | low |
| 5 | None found | No change | high |
| 6 | None found | No change | high |
| 7 | None found | No change | high |
| 8 | None found | No change | high |
| 9 | None found | No change | high |
| 10 | None found. విశ్వామిత్రుల is the honorific plural. | No change | high |
| 11 | None found | No change | high |
| 12 | None found. ఆకలి, అలసట reverses the en/hi order, which is harmless. | No change | high |
| 13 | None found | No change | high |
| all | TTS risk words: విశ్వామిత్ర, మూర్ఛపోయారు, వసిష్ఠ, కమలనయనుడైన, లక్ష్మణుడు. | Listen and re-take if needed | medium |

**Verdict:** clean, natural and faithful to en/hi, with correct honorifics. No changes are needed. A native listen is still required.
