# C0003 Telugu script review (fallback, non-native)

This review was done by a model, not a native Telugu speaker, so it is not native-level evidence. It checks each scene against the approved en/hi versions for factual drift, plus grammar, naturalness (Hindi or English calques), honorifics (sages take the honorific plural), TTS risk, digits, keywords and the verse transliteration. A native listen is still required because `profiles/languages/te.json` has status `draft`.

Automated checks: no digits in any narration; every keyword is an exact whitespace token of its narration; all letters are in the language's own script (the only other characters are the em dash, ellipsis and danda/double danda).

Scene 9 `devanagari`: కౌసల్యాయై నరపతిః / పాయసార్ధం దదౌ తదా। / అర్ధాదర్ధం దదౌ చాపి / సుమిత్రాయై నరాధిపః॥ matches 1.16.27 letter for letter. High confidence.

| Scene | Issue | Suggested exact replacement | Confidence |
|---|---|---|---|
| 1 | None found | No change | high |
| 2 | None found | No change | high |
| 3 | None found. రాజు … చేసేవారు is honorific and consistent. | No change | high |
| 4 | None found | No change | high |
| 5 | None found. ఋష్యశృంగ మహర్షిని is honorific. | No change | high |
| 6 | చంపలేరు (present) inside a past narrative is acceptable as a general truth about the boon. చంపలేకపోయేవారు would be stricter. | No change | low |
| 7 | None found. మానవుడిగా (singular) with కుమారులుగా (plural) mirrors the en/hi. | No change | high |
| 8 | None found | No change | high |
| 9 | None found | No change | high |
| 10 | None found | No change | high |
| 11 | None found | No change | high |
| 12 | None found | No change | high |
| 13 | None found | No change | high |
| all | TTS risk words: ఋష్యశృంగ, అశ్వమేధ, బ్రహ్మదేవుడి, శ్రీమహావిష్ణువు, శత్రుఘ్నుడు, లక్ష్మణుడు. | Listen and re-take if needed | medium |

**Verdict:** clean, natural and faithful to en/hi. No changes are needed. A native listen is still required.
