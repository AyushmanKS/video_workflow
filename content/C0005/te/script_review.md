# C0005 Telugu script review (fallback, non-native)

This review was done by a model, not a native Telugu speaker, so it is not native-level evidence. It covers grammar, naturalness for a neutral AP/Telangana audience, register, factual drift from `research/report.md`, TTS risks, the scene 8 transliteration, and keywords. A native listen is still required because `profiles/languages/te.json` has status `draft`.

Automated checks:
- Keywords: every keyword is an exact whitespace token of its scene's narration (0 failures).
- Digits: none in any narration. The `5` in the title and thumbnail and `1.25.18` in the scene 8 `source` appear on screen only.
- Script: all letters are Telugu. The only other characters are the em dash and the shared danda/double danda (U+0964/U+0965), which is standard.
- Scene 8 `devanagari`: నృశంసమనృశంసం వా / ప్రజారక్షణకారణాత్। / పాతకం వా సదోషం వా / కర్తవ్యం రక్షతా సదా॥ matches the verified 1.25.18 letter for letter (ృ, anusvara and the final pollu/virama in ణాత్ are correct). High confidence that it is correct.

| Scene | Issue | Suggested fix | Confidence |
|---|---|---|---|
| 1 | None found | No change | high |
| 2 | "నీళ్లు గర్జిస్తున్నాయి": in Telugu, హోరు is the usual word for the roar of water, and గర్జించు is more often used for animals or thunder. The present progressive inside a past narrative is acceptable as vivid present. | ...పడవలో గంగ దాటించారు. నది మధ్యలో నీళ్లు హోరెత్తాయి. (keyword గర్జిస్తున్నాయి. → హోరెత్తాయి.) | low |
| 2 | Factual: the boat (పడవ) is not in the report. I believe Valmiki 1.24.2–3 mentions a boat, but I have not verified it. | Verify, or drop పడవలో | low |
| 3 | None found. దేశాలు works for janapadas. | No change | high |
| 4 | None found | No change | high |
| 5 | None found | No change | high |
| 6 | None found | No change | high |
| 7 | None found. ఆయన is the correct honorific for Agastya. | No change | high |
| 8 | Factual drift. "పని కఠినమైనదైనా సరే" keeps only "even if harsh". It drops both the "or not" and the verse's second pair, पातकं वा सदोषं वा ("sinful or flawed"). The EN version keeps it. The verse is on screen, so the explanation should cover the whole verse. | ప్రజలను కాపాడటం కోసం, పని క్రూరమైనదైనా కాకపోయినా, పాపమైనా దోషమైనా, రక్షకుడు చేయక తప్పదు. ఇదే సనాతన రాజధర్మం. (keywords కాపాడటం and రాజధర్మం. are kept) | medium |
| 9 | "వింటి నారిని మోగించాడు": మోగించు is normally used for bells and drums. ధనుష్టంకారం చేశాడు, or వింటి నారిని మీటాడు, is the more idiomatic choice. | అప్పుడు రాముడు ధనుష్టంకారం చేశాడు. అడవంతా వణికిపోయింది, తాటక గర్జిస్తూ దూసుకొచ్చింది. (keyword మోగించాడు. → చేశాడు. or ధనుష్టంకారం) | medium |
| 10 | The structure is English-like. "అన్నాడు —" comes before the quote with no ఇలా. "ఈమె ఒక స్త్రీ" carries a calqued ఒక (English "a"). "కేవలం ఆపుతాను" has no object, so it reads clipped. | అయినా రాముడు లక్ష్మణుడితో ఇలా అన్నాడు — నేను ఈమెను చంపలేను, ఈమె స్త్రీ. ఈమెను అడ్డుకుంటాను, అంతే. (keywords లక్ష్మణుడితో and స్త్రీ. are kept) | medium |
| 11 | None found | No change | high |
| 12 | "గురి పెట్టాడు, ఒకే బాణంతో తాటక నేల కూలింది" is a comma splice with a subject switch. A participle chain is more natural Telugu. నేలకూలు is normally written as one word. | ...రాముడు శబ్దం విని మాత్రమే గురి పెట్టి, ఒకే బాణంతో తాటకను నేలకూల్చాడు. (keywords are kept) | medium |
| 12 | "సంధ్య సమీపిస్తోంది, అప్పుడు రాక్షసులు…": అప్పుడు is loose here. ఆ వేళ is clearer. | సంధ్య సమీపిస్తోంది, ఆ వేళ రాక్షసులు మరింత బలపడతారు. | low |
| 12 | మహర్షి గర్జించారు ("roared") is strong for a sage, and the గర్జ- root also appears in scenes 2 and 9. The EN version has "cried". | చాలు ఈ జాలి, రామా! అని మహర్షి గట్టిగా అన్నారు. | low |
| 12 | Factual compression, shared with the EN version. Sound-shooting (1.26.24–25) and the chest arrow (1.26.26) are two separate moments. This is acceptable for a Short. | No change (owner's call) | low |
| 12 | At 165 characters this is the longest scene. Each sentence is under 140, so it is fine if TTS is generated per sentence. | No change | low |
| 13 | Register inconsistency. "విశ్వామిత్రుడి" uses the plain -డు form, while every other scene uses విశ్వామిత్ర మహర్షి / మహర్షి with honorific plural verbs. "రాముడి కోసం … దగ్గర ఒక కానుక ఉంది" mirrors the English "had a gift for". | మర్నాడు ఉదయం, విశ్వామిత్ర మహర్షి రాముడికి ఒక కానుక సిద్ధం చేశారు — దివ్యాస్త్రాలు. (keyword దివ్యాస్త్రాలు. is kept) | medium |
| 13 | "శాపగ్రస్తమైన అడవి మళ్లీ వికసించింది": వికసించు is mainly used for flowers, and కళకళలాడింది may be more natural. Also, శాపం తొలగిన అడవి would track 1.26.35 more closely. | Optional: శాపం తొలగిన అడవి మళ్లీ కళకళలాడింది (keyword వికసించింది. would need to change) | low |
| all | TTS risk words for the ASR round-trip: బ్రహ్మదేవుడు (హ్మ), లక్ష్మణుడితో, శాపగ్రస్తమైన (స్త), దివ్యాస్త్రాలు (స్త్ర), సాక్షాత్తూ. ధనుష్టంకారం (ష్ట) would be added if the scene 9 fix is taken. | Listen and re-take if needed | medium |
| all | Register: the sage gets plural honorific verbs (దాటించారు, చెప్పారు). Rama uses the standard narrative -డు/-ాడు forms, which suit a young prince. These are consistent apart from scene 13. | No change | high |

**Overall verdict:** the Telugu is grammatical and broadly natural, and the scene 8 transliteration is correct. Fix scene 8 (it drops half the verse's meaning) before G1, and preferably apply the medium-confidence fixes in scenes 9, 10, 12 and 13. A native listen is still required.
