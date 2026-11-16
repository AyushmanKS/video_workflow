# C0005 Gujarati script review (fallback, non-native)

This review was done by a model, not a native Gujarati speaker, so it is not native-level evidence. It covers grammar, naturalness against Ahmedabad media usage, register, factual drift from `research/report.md`, TTS risks, the scene 8 transliteration, and keywords. A native listen is still required because `profiles/languages/gu.json` has status `draft`.

Automated checks:
- Keywords: every keyword is an exact whitespace token of its scene's narration (0 failures).
- Digits: none in any narration. The `5` in the title and thumbnail and `1.25.18` in the scene 8 `source` appear on screen only and are never spoken.
- Script: all letters are Gujarati. The only other characters are the em dash and the shared danda/double danda (U+0964/U+0965), which is the standard Unicode practice for Gujarati.
- Scene 8 `devanagari`: નૃશંસમનૃશંસં વા / પ્રજારક્ષણકારણાત્। / પાતકં વા સદોષં વા / કર્તવ્યં રક્ષતા સદા॥ matches the verified text of 1.25.18 letter for letter (ૃ, anusvara and the final virama in ણાત્ are all correct). High confidence that it is correct.

| Scene | Issue | Suggested fix | Confidence |
|---|---|---|---|
| 1 | None found. માગતા is the Vidyapith spelling (માંગતા is also common). Calling her રાક્ષસી in the hook is consistent with the EN version and with her cursed form. | No change | high |
| 2 | વચ્ચે ધારામાં reads a little stiff. The usual phrasings are નદીની વચ્ચોવચ or મધધારે. | વિશ્વામિત્ર બંને રાજકુમારોને હોડીમાં ગંગા પાર લઈ ગયા. નદીની વચ્ચોવચ પાણી ગર્જના કરતું હતું. | low |
| 2 | Factual: the boat (હોડી) is not in the report. I believe Valmiki 1.24.2–3 mentions a boat (नौ), but I have not verified it. | Verify, or drop હોડીમાં | low |
| 3 | પ્રદેશ હતા is correct. પ્રદેશો હતા would make the plural clearer. The fronted હતું એક ભયાનક વન works as narrative style. | ...મલદ અને કરૂષ નામના સમૃદ્ધ પ્રદેશો હતા. | low |
| 4 | None found | No change | high |
| 5 | None found | No change | high |
| 6 | None found. The `emphasis` field says બ્રહ્માનું while the narration says બ્રહ્માજીનું. That is fine, because `emphasis` is a separate on-screen title. | No change | high |
| 7 | None found. તેમના is the correct honorific for Agastya. Leaving out Maricha's own curse and Sunda's death is acceptable compression. | No change | high |
| 8 | Factual drift. The narration has only "કઠોર હોય કે કોમળ" and drops the verse's second pair, पातकं वा सदोषं वा ("sinful or flawed"). The EN version keeps it. Also, કોમળ ("gentle") is a loose gloss of अनृशंस ("not cruel"). The verse is on screen, so the explanation should cover the whole verse. | પ્રજાની રક્ષા માટે, કામ ક્રૂર હોય કે ન હોય, તેમાં પાપ હોય કે દોષ, રક્ષકે તે કરવું જ પડે. આ જ સનાતન રાજધર્મ છે. (keywords રક્ષા and રાજધર્મ are kept) | medium |
| 9 | "ધનુષની દોરી ટંકારી" is understandable, but ટંકાર કરવો (or પણછ for the bowstring) is the more standard idiom. I am not sure ટંકારવું is standard as a verb. | ત્યારે રામે ધનુષનો ટંકાર કર્યો. આખું વન ધ્રૂજી ઊઠ્યું, અને તાટકા ગર્જના કરતી દોડી આવી. (keyword ટંકારી. → ટંકાર) | low |
| 10 | તોય is colloquial. Media-register Gujarati would use તેમ છતાં or તોપણ. | તેમ છતાં રામે લક્ષ્મણને કહ્યું — હું તેને મારી નહીં શકું, એ એક સ્ત્રી છે. હું ફક્ત તેને રોકીશ. | medium |
| 11 | "ધૂળનું તોફાન ઉઠાવ્યું" may be a Hindi calque (तूफ़ान उठाया). ધૂળની ડમરી ઉડાડી is the idiomatic Gujarati. | તાટકાએ ધૂળની ડમરી ઉડાડી, પથ્થરોનો વરસાદ કર્યો, અને માયાથી અદૃશ્ય થઈ ગઈ. (keywords are kept) | medium |
| 12 | "સાંજ પડવા આવી છે, ત્યારે રાક્ષસો…": ત્યારે has no clear relative antecedent, so the clause reads awkwardly. Valmiki's point is that rakshasas become stronger at dusk (sandhyā). | ...સાંજ પડવા આવી છે, અને સંધ્યાકાળે રાક્ષસો વધુ બળવાન બની જાય છે. ... | medium |
| 12 | ઋષિ ગર્જ્યા ("roared") is strong for a sage. It also repeats the ગર્જ- root from scenes 2 and 9. The EN version has "cried". | ઋષિ બોલી ઊઠ્યા — બસ કરો આ દયા, રામ! ... | low |
| 12 | Factual compression, shared with the EN version. In 1.26.24–26 Rama blocks the invisible rock-rain by shooting at sound, and then strikes her chest as she charges. "Aimed by sound alone, one arrow" merges these two moments. That is acceptable for a Short. | No change (owner's call) | low |
| 12 | At 153 characters this is the longest scene. Each sentence is under 140, so it is fine if TTS is generated per sentence. | No change | low |
| 13 | "બીજી સવારે" reads like a calque of "next morning". બીજે દિવસે સવારે is the natural form. | ...ફરી ખીલી ઊઠ્યું. બીજે દિવસે સવારે, વિશ્વામિત્ર પાસે રામ માટે એક ભેટ હતી — દિવ્ય અસ્ત્રો. | medium |
| 13 | શાપિત વન ("cursed forest") is accurate as the EN puts it. શાપમુક્ત વન ("forest freed from the curse") would track 1.26.35 more closely. | Optional: શાપમુક્ત વન ફરી ખીલી ઊઠ્યું | low |
| all | TTS risk words for the ASR round-trip: ઋષિ, બ્રહ્માજીનું (હ્મ), અગસ્ત્ય (સ્ત્ય), અદૃશ્ય (દૃ), ઉજ્જડ, લક્ષ્મણને. They are all common, but check them in the CER pass and by listening. | Listen and re-take if needed | medium |
| all | Register: the sage gets plural honorific verbs throughout (લઈ ગયા, કહ્યું with ઋષિએ). Rama also gets the respectful plural (નહોતા માગતા), which is normal in Gujarati narration. These are consistent. | No change | high |

**Overall verdict:** the Gujarati is grammatical and mostly natural, and the scene 8 transliteration is correct. Fix scene 8 (it drops half the verse's meaning) before G1, and preferably apply the medium-confidence idiom fixes in scenes 10, 11, 12 and 13. A native listen is still required.
