# C0002 Gujarati script review (fallback, non-native)

This review was done by a model, not a native Gujarati speaker, so it is not native-level evidence. It checks each scene against the approved en/hi versions for factual drift, plus grammar and matras, naturalness (Hindi or English calques), register, TTS risk, digits, keywords and the verse transliteration. A native listen is still required because `profiles/languages/gu.json` has status `draft`.

Automated checks: no digits in any narration; every keyword is an exact whitespace token of its narration; all letters are in the language's own script (the only other characters are the em dash, ellipsis and danda/double danda).

Scene 3 `devanagari`: કો ન્વસ્મિન્ સામ્પ્રતં લોકે / ગુણવાન્ કશ્ચ વીર્યવાન્। / ધર્મજ્ઞશ્ચ કૃતજ્ઞશ્ચ / સત્યવાક્યો દૃઢવ્રતઃ॥ matches 1.1.2 letter for letter. High confidence.

| Scene | Issue | Suggested exact replacement | Confidence |
|---|---|---|---|
| 1 | None found | No change | high |
| 2 | None found. It matches hi (the visit is set before the Krauncha incident). | No change | high |
| 3 | પોતાના વ્રતમાં અડગ is fine. વ્રત પર અડગ is an equally common alternative. | No change | low |
| 4 | None found. જાતને જીતી has the correct feminine agreement. | No change | high |
| 5 | None found | No change | high |
| 6 | None found. મલક્યા is good idiomatic Gujarati, and સાંભળો is the correct respectful form for Valmiki. | No change | high |
| 7 | None found | No change | high |
| 8 | None found | No change | high |
| 9 | None found | No change | high |
| 10 | None found. The hi version's "made him his dear friend" becomes "embraced like a dear friend", which is acceptable. | No change | high |
| 11 | None found | No change | high |
| 12 | None found | No change | high |
| all | TTS risk words: ક્રૌંચ, ધર્મજ્ઞ (in the on-screen verse only), કૃતજ્ઞ, ઈર્ષ્યા, ઇક્ષ્વાકુ, લક્ષ્મણ. | Listen and re-take if needed | medium |

**Verdict:** clean, natural and faithful to en/hi. No changes are needed. A native listen is still required.
