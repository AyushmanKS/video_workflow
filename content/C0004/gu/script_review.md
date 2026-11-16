# C0004 Gujarati script review (fallback, non-native)

This review was done by a model, not a native Gujarati speaker, so it is not native-level evidence. It checks each scene against the approved en/hi versions for factual drift, plus grammar and matras, naturalness (Hindi or English calques), register, TTS risk, digits, keywords and the verse transliteration. A native listen is still required because `profiles/languages/gu.json` has status `draft`.

Automated checks: no digits in any narration; every keyword is an exact whitespace token of its narration; all letters are in the language's own script (the only other characters are the em dash, ellipsis and danda/double danda).

Scene 6 `devanagari`: ઊનષોડશવર્ષો મે / રામો રાજીવલોચનઃ। / ન યુદ્ધયોગ્યતામસ્ય / પશ્યામિ સહ રાક્ષસૈઃ॥ matches 1.20.2 letter for letter. High confidence.

| Scene | Issue | Suggested exact replacement | Confidence |
|---|---|---|---|
| 1 | None found | No change | high |
| 2 | None found | No change | high |
| 3 | None found. આનંદ સમાતો નહોતો is idiomatic. | No change | high |
| 4 | None found | No change | high |
| 5 | None found | No change | high |
| 6 | Dasharatha uses the honorific તેમનામાં for his own son. That copies the hi उन्हें. A father would more naturally say તેનામાં, but the honorific for Rama is a defensible series choice. | No change (owner's call) | low |
| 7 | મને પોતાને લઈ જાઓ is grammatical but heavy. મને જ લઈ જાઓ is the more natural Gujarati. | Optional: તેમણે આજીજી કરી — મારી સેના લઈ જાઓ. મને જ લઈ જાઓ. | low |
| 8 | ભય વધુ વધી ગયો is slightly redundant, though common in speech. | Optional: …ત્યારે તેમનો ભય ઓર વધી ગયો. | low |
| 9 | None found. ભભૂકી ઊઠ્યા is idiomatic. | No change | high |
| 10 | None found | No change | high |
| 11 | None found | No change | high |
| 12 | None found | No change | high |
| 13 | None found | No change | high |
| all | TTS risk words: વિશ્વામિત્ર (શ્વ), મૂર્છા, વસિષ્ઠે (ષ્ઠ), લક્ષ્મણ, અતિબલા. | Listen and re-take if needed | medium |

**Verdict:** clean, natural and faithful to en/hi. Only optional style tweaks. A native listen is still required.
