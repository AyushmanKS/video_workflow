# C0003 Gujarati script review (fallback, non-native)

This review was done by a model, not a native Gujarati speaker, so it is not native-level evidence. It checks each scene against the approved en/hi versions for factual drift, plus grammar and matras, naturalness (Hindi or English calques), register, TTS risk, digits, keywords and the verse transliteration. A native listen is still required because `profiles/languages/gu.json` has status `draft`.

Automated checks: no digits in any narration; every keyword is an exact whitespace token of its narration; all letters are in the language's own script (the only other characters are the em dash, ellipsis and danda/double danda).

Scene 9 `devanagari`: કૌસલ્યાયૈ નરપતિઃ / પાયસાર્ધં દદૌ તદા। / અર્ધાદર્ધં દદૌ ચાપિ / સુમિત્રાયૈ નરાધિપઃ॥ matches 1.16.27 letter for letter, including the Sanskrit spelling કૌસલ્યા. High confidence.

| Scene | Issue | Suggested exact replacement | Confidence |
|---|---|---|---|
| 1 | None found. ઊજવે uses the standard long ઊ. | No change | high |
| 2 | None found | No change | high |
| 3 | None found | No change | high |
| 4 | None found | No change | high |
| 5 | None found. યજ્ઞનું સંચાલન is a fair rendering of "lead the sacred fire". | No change | high |
| 6 | None found | No change | high |
| 7 | None found | No change | high |
| 8 | None found. The honorific પ્રગટ થયા / તેમના for the divine being is acceptable. | No change | high |
| 9 | Narration uses કૌશલ્યા while the verse card has કૌસલ્યા. That is fine, because કૌશલ્યા is the common Gujarati and Hindi spelling. બાકીનીમાંથી is a little compressed, and બાકી રહેલીમાંથી is smoother. | Optional: રાજાએ અડધી ખીર કૌશલ્યાને આપી, બાકી રહેલીમાંથી અડધી સુમિત્રાને, તેમાંથી અડધી કૈકેયીને, અને છેલ્લો ભાગ ફરી સુમિત્રાને. | low |
| 10 | None found. ચૈત્ર મહિનાની નોમ and કૂખે are idiomatic. | No change | high |
| 11 | None found | No change | high |
| 12 | None found | No change | high |
| 13 | None found | No change | high |
| all | TTS risk words: ઋષ્યશૃંગને (ષ્ય, શૃ), અશ્વમેધ, બ્રહ્માજીના, શત્રુઘ્ન (ઘ્ન), લક્ષ્મણ. | Listen and re-take if needed | medium |

**Verdict:** clean, natural and faithful to en/hi. No changes are needed. A native listen is still required.
