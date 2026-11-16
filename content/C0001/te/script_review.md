# C0001 Telugu script review (fallback, non-native)

This review was done by a model, not a native Telugu speaker, so it is not native-level evidence. It checks each scene against the approved en/hi versions for factual drift, plus grammar, naturalness (Hindi or English calques), honorifics (sages take the honorific plural), TTS risk, digits, keywords and the verse transliteration. A native listen is still required because `profiles/languages/te.json` has status `draft`.
The en/hi source is `out/ramayana-ep-01-maharishi-valmiki-the-birth-of-the-ramayana/script.json` and `…/hindi/script.json`. The Telugu follows the Hindi scene by scene.

Automated checks: no digits in any narration; every keyword is an exact whitespace token of its narration; all letters are in the language's own script (the only other characters are the em dash, ellipsis and danda/double danda). Scene 12 is 147 characters, but each sentence is under 140.

Scene 9 `devanagari`: మా నిషాద ప్రతిష్ఠాం త్వమ్ / అగమః శాశ్వతీః సమాః। / యత్ క్రౌఞ్చమిథునాదేకమ్ / అవధీః కామమోహితమ్॥ is a letter-for-letter match of 1.2.15. High confidence.
Scene 10 shloka labels: `from` శోకం, `to` శ్లోకం, "శోకం · దుఃఖం", "శ్లోకం · ఛందస్సు" are correct. The Telugu -ం ending is natural, and the morph still shows only the inserted ల. High confidence.

| Scene | Issue | Suggested exact replacement | Confidence |
|---|---|---|---|
| 1 | None found | No change | high |
| 2 | None found. The honorific ఉండేవారు for Valmiki is correct. | No change | high |
| 3 | None found. దేవర్షి నారదులు … చెప్పారు is correct and honorific. | No change | high |
| 4 | None found | No change | high |
| 5 | ఒకదానిలో ఒకటి మైమరచి mirrors the Hindi एक-दूसरे में मगन. It parallels the existing idiom ఒకరిలో ఒకరు లీనమై, so it is acceptable. | No change | low |
| 6 | None found | No change | high |
| 7 | జోడు mainly means "a pair" (చెప్పుల జోడు). For a bird's mate, తోడు ("companion, mate") is clearer and more idiomatic, especially since the next scene's verse uses జంట for the pair. | రక్తంలో తడిసిన తన తోడును చూసి... ఆడ పక్షి దీనంగా విలపించింది. (keyword జోడును → తోడును) | medium |
| 8 | None found | No change | high |
| 9 | Placing ఎందుకంటే in the middle of a curse is a little English-like. A కాబట్టి clause is more classical. The current form is still common in speech. The Sanskrit is not recited, which matches the EN. | Optional: ఓ వేటగాడా! ప్రేమలో మునిగిన జంటలో ఒకదాన్ని నువ్వు చంపావు కాబట్టి, నీకు యుగయుగాల వరకు శాంతి లభించకుండుగాక. | low |
| 10 | కొలతలున్న ఛందస్సు is a calque of नपा-तुला. లయబద్ధమైన is more natural. దానికి పేరు... శ్లోకం is a verbless dramatic ellipsis, which is acceptable. | Optional: వాల్మీకి ఆశ్చర్యపోయారు — అది లయబద్ధమైన ఛందస్సు, వీణ మీద పాడదగినది! శోకం నుండి పుట్టింది కాబట్టి, దానికి పేరు... శ్లోకం. | low |
| 11 | బ్రహ్మదేవుడు (-డు) with ఆదేశించారు (honorific -ారు) is a mixed register, though it is common in modern speech. | Optional: …బ్రహ్మదేవుడు … ఆదేశించాడు | low |
| 12 | Factual drift: దీని పురాతన భాగాలు ("its ancient parts") loses "oldest" (hi: सबसे पुराने अंश; en: oldest parts). | అలా పుట్టింది ఆదికావ్యం — రామాయణం. సంప్రదాయం ప్రకారం ఇరవై నాలుగు వేల శ్లోకాలు. దీనిలోని అతి పురాతన భాగాలు రెండు వేల ఏళ్లకు పైబడినవని చరిత్రకారుల అభిప్రాయం. (keywords are kept) | medium |
| 13 | None found | No change | high |
| all | TTS risk words: క్రౌంచ, భరద్వాజుడితో, బ్రహ్మదేవుడు (హ్మ), అప్రయత్నంగా, ఛందస్సు, శ్లోకం. | Listen and re-take if needed | medium |

**Verdict:** the Telugu is grammatical and honorifics are consistent. Fix scene 12 (restore "oldest") and scene 7 (జోడు → తోడు). The transliteration and shloka labels are correct. A native listen is still required.
