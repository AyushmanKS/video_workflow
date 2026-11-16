# C0001 Gujarati script review (fallback, non-native)

This review was done by a model, not a native Gujarati speaker, so it is not native-level evidence. It checks each scene against the approved en/hi versions for factual drift, plus grammar and matras, naturalness (Hindi or English calques), register, TTS risk, digits, keywords and the verse transliteration. A native listen is still required because `profiles/languages/gu.json` has status `draft`.
The en/hi source is `out/ramayana-ep-01-maharishi-valmiki-the-birth-of-the-ramayana/script.json` and `…/hindi/script.json`. The Gujarati follows the Hindi scene by scene.

Automated checks: no digits in any narration; every keyword is an exact whitespace token of its narration; all letters are in the language's own script (the only other characters are the em dash, ellipsis and danda/double danda).

Scene 9 `devanagari`: મા નિષાદ પ્રતિષ્ઠાં ત્વમ્ / અગમઃ શાશ્વતીઃ સમાઃ। / યત્ ક્રૌઞ્ચમિથુનાદેકમ્ / અવધીઃ કામમોહિતમ્॥ is a letter-for-letter match of the Devanagari 1.2.15 (ઞ્ચ correctly renders ञ्च, and the visarga and final viramas are present). High confidence.
Scene 10 shloka labels: `from` શોક, `to` શ્લોક, `from_label` "શોક · દુઃખ", `to_label` "શ્લોક · છંદ" are correct and match the hi intent. High confidence.

| Scene | Issue | Suggested exact replacement | Confidence |
|---|---|---|---|
| 1 | None found. ઋષિનાં આંસુથી has the correct neuter-plural agreement. | No change | high |
| 2 | ખુદ is Persian-origin. It is common in Gujarati, but પોતે is more native. | Optional: આ કથા રામાયણ પોતે જ કહે છે. વનના એક શાંત આશ્રમમાં રહેતા હતા... મહર્ષિ વાલ્મીકિ. | low |
| 3 | None found. It matches the hi version. | No change | high |
| 4 | None found | No change | high |
| 5 | None found. જોડું … કરતું હતું has the correct neuter agreement. | No change | high |
| 6 | સનનન copies the Hindi सन्न. Gujarati more often uses સૂસવાટા મારતું or સરરર કરતું. The onomatopoeia is also an ASR/TTS risk. | ત્યાં જ... સૂસવાટા મારતું એક તીર આવ્યું! એક શિકારીએ નર પક્ષીને વીંધી નાખ્યું. | low |
| 7 | None found | No change | high |
| 8 | None found. Like the hi version, it omits the EN's "cursed the hunter". The curse itself follows in scene 9. | No change | high |
| 9 | None found. The narration is a translation only and the Sanskrit is not recited, which matches the EN. The hi version recites the shloka, so whether gu should is the owner's call. | No change | low |
| 10 | માપસરનો છંદ looks like a calque of नपा-तुला (માપસર usually means "moderate, of the right size"). લયબદ્ધ or માપબદ્ધ is more natural. | Optional: વાલ્મીકિ ચકિત થઈ ગયા — આ તો લયબદ્ધ છંદ હતો, વીણા પર ગાઈ શકાય એવો! શોકમાંથી જન્મ્યો, એટલે નામ પડ્યું... શ્લોક. | low |
| 11 | None found | No change | high |
| 12 | Agreement error: સૌથી જૂના અંશને (singular object) … જૂના (plural predicate). The hi version has the plural अंश ("parts"), so the object should be plural. | અને આ રીતે રચાયું આદિકાવ્ય — રામાયણ. પરંપરા મુજબ ચોવીસ હજાર શ્લોક. ઇતિહાસકારો તેના સૌથી જૂના અંશોને બે હજાર વર્ષથી પણ જૂના માને છે. | medium |
| 13 | આગળના ભાગમાં is ambiguous. આગળનું/આગલું can mean "previous" in Gujarati (આગલા દિવસે = the day before). The standard series phrasing is આવતા ભાગમાં ("in the coming part"). | પણ... કોણ હતા એ શ્રીરામ, જેમના ગુણ સ્વયં નારદે ગણાવ્યા હતા? જાણીશું... આવતા ભાગમાં. (keyword આગળના → આવતા) | medium |
| all | TTS risk words for the ASR pass: ઋષિનાં, ક્રૌંચ/ક્રૌંચી, ભરદ્વાજ, બ્રહ્માજી (હ્મ), સૃષ્ટિના, શ્લોક. | Listen and re-take if needed | medium |

**Verdict:** the grammar is good and it is faithful to hi. Fix scene 12 (agreement) and scene 13 (ambiguous "next part"). The transliteration and shloka labels are correct. A native listen is still required.
