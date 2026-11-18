# C0011 · బాలకాండ మొదటి భాగం (long-form, Telugu)

**Format:** YouTube long-form, 16:9, engine v3 (chalk puppet). Not a Short: the long-form section of the storytelling skill applies.
**Review status:** Telugu is in the **`unreviewed-language` cohort** (`profiles/languages/te.json`, owner decision O9). No native-speaker reviewer has checked this script yet; CER checks are warn-only for te.
**Working title:** రామాయణం · బాలకాండ మొదటి భాగం: వాల్మీకి తొలి శ్లోకం నుంచి రాముడి తొలి యుద్ధం వరకు (the packager decides the final title).
**Scope:** VR 1.1–1.30 (vulgate), cliff from 1.31.1–18. Same 50 scenes, order, `visual`, `kind`, `devanagari`, `source`, `pause`, `chapter`, `sfx`, `melody`, `segment`, `tone`, `quote_src` as `en/script.json` (checked field by field; `quote_src` re-synced to the English writer's updated locators for scenes 3, 21, 30 and 36). The one deliberate exception is scene 50's `pause`, which is 7.0 s in te (6.0 s in en), as the Story QA asked. Narration written fresh in Telugu.
**Estimate (`pipeline lint`, calibrated letter rate 5.928/s):** **570.3 s ≈ 9 min 30 s**, **853 words**, 50 scenes (after the Story QA fixes). Word-rate cross-check: 853 / 1.563 w/s + 28.65 s pauses + 1.15 s lead/tail ≈ 576 s.
**Lint:** **PASS**, 0 failures, 0 warnings.

## Cold open (scenes 1–4, about 33 s including the title scene)
> రాముడు చిన్నవాడని తండ్రి భయపడ్డారు. ఆరో రోజు, రాక్షసులు రానే వచ్చారు.
> ఆరు రాత్రింబవళ్లు నిద్ర మాని అన్నదమ్ములు యజ్ఞాగ్నిని కాపాడారు. ఇప్పుడు వానమబ్బుల్లా రాక్షసులు వేదికపై విరుచుకుపడ్డారు.
> అయితే తండ్రి భయపడిన ఆ బాలుడి చేతిలో, దేవతలకైనా దుర్లభమైన దివ్యాస్త్రాలు ఉన్నాయి.
> *(Title: బాలకాండ · మొదటి భాగం)* కానీ ఈ కథ అంతకు ఎంతో ముందే, ప్రశాంతమైన నది ఒడ్డున, ఒక కవితో, ఒక ప్రశ్నతో, రెండు పక్షులతో మొదలవుతుంది.

- **First line:** estimated 5.6 s (under the 6 s long-form warning), stakes-first, chosen from 3 options in `hooks.json` (rubric 27/30).
- **Bookend:** scene 47 repeats the hook's own words: చిన్నవాడని తండ్రి భయపడిన ఆ రాకుమారుడు…

## Chapters and timings (estimated)
| # | Chapter title (`chapter_title`) | Scenes | Starts | Length | Sargas |
|---|---|---|---|---|---|
| – | Cold open + part title | 1–4 | 0:00 | 33 s | 1.20, 1.27–1.30, 1.2 |
| 1 | కవిత్వం పుట్టిన వేళ | 5–12 | 0:32 | 88 s | 1.1–1.2 |
| 2 | దశరథుని నిరీక్షణ | 13–21 | 2:00 | 107 s | 1.5–1.18 |
| 3 | ద్వారం వద్ద మహర్షి | 22–30 | 3:46 | 112 s | 1.18–1.23 |
| 4 | తాటక, దివ్యాస్త్రాలు | 31–39 | 5:38 | 110 s | 1.23–1.29 |
| 5 | ఆరు రాత్రుల కాపలా (+ closing, end board) | 40–50 | 7:28 | 120 s | 1.29–1.31 |

Chapter 5 breaks down as story 7:28–8:30 (62 s), closing 8:30–9:12 (41 s) and end board 9:12–9:29 (about 17 s: 10.0 s of soft narration plus the 7.0 s music-only hold). `chapters[].first_scene` is 1-based (5, 13, 22, 31, 40), identical to English. The render adds the chapter number itself, so each title holds only the words.

Re-hooks (same beats as English): నారదుడి సమాధానం (0:49), వేటగాడి బాణం (1:10), సూర్యుడు సైతం జంకే రావణుడు (2:28), తేజోమూర్తి (2:53), రాముడిని నాకు ఇవ్వు (3:55), భూమి కంపించింది (4:31), చంపాలని లేదు (6:13), అస్త్రాలు సేవకులం అనడం (6:49), ఆకాశం గర్జించింది (7:39), మారీచుడు సముద్రంలోకి (7:55).

Chapter pulls: chapter 1 ends on ఆ శ్లోకమే రామాయణమైంది; chapter 2 (scene 21) on the unexpected guest at the gate (1.18.37–39); chapter 3 (scene 30) on the road to the Ganga and the dreadful forest beyond it (1.23.5, 1.24.12); chapter 4 on ఇక్కడే వారిని సంహరించు; chapter 5 on the bow waiting in Mithila.

## Full narration
1. రాముడు చిన్నవాడని తండ్రి భయపడ్డారు. ఆరో రోజు, రాక్షసులు రానే వచ్చారు.
2. ఆరు రాత్రింబవళ్లు నిద్ర మాని అన్నదమ్ములు యజ్ఞాగ్నిని కాపాడారు. ఇప్పుడు వానమబ్బుల్లా రాక్షసులు వేదికపై విరుచుకుపడ్డారు.
3. అయితే తండ్రి భయపడిన ఆ బాలుడి చేతిలో, దేవతలకైనా దుర్లభమైన దివ్యాస్త్రాలు ఉన్నాయి.
4. కానీ ఈ కథ అంతకు ఎంతో ముందే, ప్రశాంతమైన నది ఒడ్డున, ఒక కవితో, ఒక ప్రశ్నతో, రెండు పక్షులతో మొదలవుతుంది. *(title: బాలకాండ · మొదటి భాగం)*

### అధ్యాయం 1 · కవిత్వం పుట్టిన వేళ
5. ఎంతో కాలం క్రితం, వాల్మీకి మహర్షి, మాటలలో మేటి అయిన నారదుడిని ఒక ప్రశ్న అడిగారు.
6. ఈ లోకంలో గుణవంతుడు, వీరుడు, ధర్మజ్ఞుడు, సత్యవాక్కు, కోపాన్ని జయించినవాడు, యుద్ధంలో దేవతలే భయపడేవాడు ఎవరైనా ఉన్నారా? *(verse slide: Valmiki Ramayana 1.1.2 (vulgate))*
7. నారదుడు సంతోషించారు. ఇన్ని గుణాలు అరుదు, కానీ ఇక్ష్వాకు వంశంలో పుట్టిన రాముడు అనే ఒక్కడిలో అవన్నీ ఉన్నాయి అన్నారు.
8. కథంతా చెప్పి నారదుడు ఆకాశంలోకి వెళ్లిపోయారు. తర్వాత తమసా తీరాన, ఒకదాన్నొకటి విడువకుండా తియ్యగా కూస్తున్న క్రౌంచ పక్షుల జంటను వాల్మీకి చూశారు.
9. అంతలోనే ఆయన కళ్ల ముందే, పాపపు మనసున్న వేటగాడు మగ పక్షిని కూల్చాడు. నేలపై పడిన తోడును చూసి ఆడపక్షి దీనంగా విలపించింది.
10. మహర్షి మనసు జాలితో కరిగి, నోట అప్రయత్నంగా మాటలు వెలువడ్డాయి: ఓ వేటగాడా, ప్రేమలో ఉన్న జంటలో ఒకదాన్ని చంపావు, నీకు ఎన్నటికీ ప్రతిష్ఠ దక్కకుండు గాక. *(verse slide: Valmiki Ramayana 1.2.15 (vulgate))*
11. తన మాటలకు తానే ఆశ్చర్యపోతూ, అవి నాలుగు పాదాలుగా పాడేందుకు తగినట్టు వచ్చాయని గమనించి, శోకం నుంచి పుట్టింది కాబట్టి ఇది శ్లోకం అన్నారు.
12. తర్వాత బ్రహ్మదేవుడు వచ్చి, నా సంకల్పంతోనే ఈ వాక్కు పుట్టింది, రాముడి కథంతా చెప్పు, కొండలూ నదులూ ఉన్నంత కాలం అది నిలుస్తుంది అన్నారు. అలా మహర్షి శోకం శ్లోకమైంది, ఆ శ్లోకమే రామాయణమైంది.

### అధ్యాయం 2 · దశరథుని నిరీక్షణ
13. ఆ కథ సరయూ తీరాన మనువే నిర్మించిన అయోధ్యలో మొదలవుతుంది. అక్కడి రాజు దశరథుడు సత్యవంతుడు, ప్రజలందరికీ ప్రియమైనవాడు.
14. కానీ ఆ మహారాజుకు వంశాన్ని నిలిపే కొడుకు లేడు. కొడుకు లేని జీవితంలో సంతోషమే లేదని ఆయన బాధపడ్డారు.
15. అందుకే ఆయన అశ్వమేధ యాగం సంకల్పించారు. వసిష్ఠుడు మొదలైన పురోహితులు ఆశీర్వదించగా, యువముని ఋష్యశృంగుడు యాగం నడిపించారు.
16. పుత్రుల కోసం ఋష్యశృంగుడు మరో యజ్ఞం చేస్తుండగా, దేవతలు బ్రహ్మతో మొరపెట్టుకున్నారు: వరగర్వంతో రావణుడు ముల్లోకాలనూ పీడిస్తున్నాడు, సూర్యుడు సైతం అతనికి జంకుతాడు.
17. దేవదానవుల నుంచి రక్షణ కోరిన రావణుడు, గర్వంతో మనుషులను లెక్కచేయలేదు. అందుకే విష్ణువు దశరథుడి కొడుకుగా, మానవుడిగా పుట్టడానికి అంగీకరించారు.
18. అప్పుడు అగ్ని నుంచి సూర్యుడిలా వెలిగే ఒక తేజోమూర్తి, దివ్య పాయసంతో నిండిన బంగారు పాత్రతో లేచి వచ్చారు. దీన్ని రాణులకు ఇవ్వండి, కొడుకులు పుడతారు అన్నారు.
19. నిధి దొరికిన పేదవాడిలా పొంగిపోయిన రాజు, సగం కౌసల్యకు, మిగిలినదాంట్లో సగం సుమిత్రకు, ఆపై సగం కైకేయికి ఇచ్చి, కాసేపు ఆలోచించి చివరిది మళ్లీ సుమిత్రకే ఇచ్చారు. *(verse slide: Valmiki Ramayana 1.16.27 (vulgate))*
20. చైత్ర మాసం నవమి నాడు కౌసల్యకు రాముడు పుట్టాడు. కైకేయికి భరతుడు, సుమిత్రకు లక్ష్మణ శత్రుఘ్నులు పుట్టారు. అయోధ్య ఆటపాటలతో మారుమోగింది.
21. నలుగురు రాకుమారులూ విద్యలో, విలువిద్యలో ఆరితేరారు. లక్ష్మణుడు రాముడికి మరో ప్రాణం, అతను లేనిదే రాముడు నిద్రించేవాడు కాదు. రాజు వారి పెళ్లిళ్ల గురించి ఆలోచిస్తుండగానే, ఊహించని ఒక అతిథి ద్వారం దగ్గరకు రాబోతున్నారు.

### అధ్యాయం 3 · ద్వారం వద్ద మహర్షి
22. ఆ అతిథి మరెవరో కాదు, విశ్వామిత్ర మహర్షి. దశరథుడు ఆనందంగా ఎదురెళ్లి, ఏది అడిగినా ఇస్తానని మాట ఇచ్చారు.
23. నా వ్రతానికి మారీచ సుబాహులనే రాక్షసులు మాంసం, రక్తం కురిపించి భంగం కలిగిస్తున్నారు. వ్రతంలో శపించకూడదు, అందుకే పది రాత్రులు రాముడిని నాకు ఇవ్వు అన్నారు మహర్షి.
24. రాజు స్పృహ తప్పి పడిపోయారు. తేరుకున్నాక, నా కమలనయనుడు రాముడికి పదహారేళ్లు కూడా నిండలేదు, రాక్షసులతో పోరాడే వయసు కాదు అన్నారు. *(verse slide: Valmiki Ramayana 1.20.2 (vulgate))*
25. నా సైన్యాన్ని తీసుకెళ్లండి, నన్నే తీసుకెళ్లండి, రాముడు లేక క్షణం బతకలేను అని వేడుకున్నారు. ఈ రాక్షసుల వెనుక రావణుడు ఉన్నాడని విని ఆయన భయం రెట్టింపైంది.
26. నెయ్యి పోసిన అగ్నిలా విశ్వామిత్రుడి కోపం భగ్గుమనగా, రఘువంశపు రాజు మాట తప్పడమా అని ఆయన అనగానే భూమి అంతా కంపించింది.
27. గురువు వసిష్ఠుడు రాజుకు ధైర్యం చెప్పారు. ధర్మాన్ని విడవకు, అగ్ని కాపాడే అమృతంలా ఈ మహర్షి రక్షణలో రాముడు క్షేమంగా ఉంటాడు అన్నారు.
28. తల్లి ఆశీస్సులతో, దశరథుడు కొడుకు శిరస్సును ఆఘ్రాణించి మహర్షికి అప్పగించారు. మెల్లగా గాలి వీచింది, ఆకాశం నుంచి పూలవాన కురిసింది, అన్న వెనుకే లక్ష్మణుడు నడిచాడు.
29. సరయూ ఒడ్డున మహర్షి రాముడికి బల, అతిబల అనే మంత్రాలు ఉపదేశించారు, వాటితో అలసట, ఆకలి దరిచేరవు. ఆ రాత్రి అన్నదమ్ములు గడ్డి పరుపుల మీద నిద్రించారు.
30. తెల్లవారుతుండగా మహర్షి లేపారు: కౌసల్యకు సుపుత్రుడివి రామా, తొలిసంధ్య వచ్చింది, లే నరశార్దూలా. పదిహేనో శతాబ్దపు శ్రీ వేంకటేశ్వర సుప్రభాతం ఈ మాటలతోనే మొదలై, ఈనాటికీ తిరుమలలో వినిపిస్తుంది. ఆ ఉదయమే వారు గంగ వైపు సాగారు, ఆవల భయంకరమైన అడవి ఉంది. *(verse slide: Valmiki Ramayana 1.23.2 (vulgate))*

### అధ్యాయం 4 · తాటక, దివ్యాస్త్రాలు
31. గంగ దాటాక, ఒకప్పుడు మలద, కరూష దేశాలు ఉన్న ఆ నేలను వెయ్యి ఏనుగుల బలం ఉన్న తాటక అనే యక్షిణి పాడుచేసిందని మహర్షి చెప్పారు.
32. ఒక యక్షిణికి ఇంత బలం ఎలా అని రాముడు అడిగితే, అది బ్రహ్మ వరం అన్నారు మహర్షి. కొడుకు మారీచుడితో కలిసి అగస్త్యుడిపై దాడి చేసినందుకు, ఆయన శాపంతో ఆమె రాక్షసిగా మారింది.
33. స్త్రీ అని వెనుకాడకు, ప్రజలను కాపాడేవాడు పని క్రూరంగా కనిపించినా చేయక తప్పదు, పాలించేవారికి అదే శాశ్వత ధర్మం అన్నారు మహర్షి. *(verse slide: Valmiki Ramayana 1.25.18 (vulgate))*
34. రాముడు ధనుష్టంకారం చేయగానే తాటక దూసుకొచ్చింది. అప్పుడు కూడా ఆమెను చంపాలని లేదు, అడ్డుకుంటే చాలు అని లక్ష్మణుడితో అన్నాడు.
35. కానీ ఆమె దుమ్ము రేపి, రాళ్ల వాన కురిపించి, మాయతో మాయమైంది. చాలు ఈ జాలి రామా, సంధ్య వస్తోంది, అప్పుడు రాక్షసులను గెలవలేం అని మహర్షి హెచ్చరించారు.
36. శబ్దాన్ని బట్టి గురి చూసి రాముడు బాణాలతో రాళ్ల వానను అడ్డుకున్నాడు, ఆమె మీదకు దూసుకురాగానే ఒకే బాణం వదిలాడు, తాటక నేలకూలింది. దేవతలు పొగిడారు, శాపం పట్టిన అడవి మళ్లీ పచ్చగా విరిసింది.
37. మర్నాడు మహర్షి చిరునవ్వుతో కాలచక్రం, వజ్రం, బ్రహ్మాస్త్రం, అగ్ని, వాయువు, నిద్రాస్త్రం సహా అస్త్రాలన్నీ రాముడికి ఇచ్చారు. అవి చేతులు జోడించి, మేము నీ సేవకులం అన్నాయి.
38. రాముడు వాటిని తాకి, నా మనసులో ఉండండి అన్నాడు. ఇక దేవతలు కూడా నన్ను జయించలేరు, కానీ వీటిని వెనక్కి ఎలా రప్పించాలి అని అడిగాడు. మహర్షి అదీ నేర్పించారు. *(verse slide: Valmiki Ramayana 1.28.2 (vulgate))*
39. చివరికి కొండ పక్కన మేఘంలా కనిపించే సిద్ధాశ్రమానికి చేరారు. ఇక్కడే రాక్షసులు యాగాన్ని పాడుచేస్తారు, నరశార్దూలా, ఇక్కడే వారిని సంహరించు అన్నారు మహర్షి.

### అధ్యాయం 5 · ఆరు రాత్రుల కాపలా
40. ఆ రోజే విశ్వామిత్రుడు మౌనవ్రతం పూనారు. మునుల కోరికపై, ఆరు రాత్రింబవళ్లు నిద్ర లేకుండా రామలక్ష్మణులు ఆయన పక్కనే కాపు కాశారు.
41. ఆరో రోజు, సిద్ధంగా ఉండు అని రాముడు లక్ష్మణుడితో అంటుండగానే, వేదిక మీద అగ్ని భగ్గుమంది, ఆకాశం భయంకరంగా గర్జించింది.
42. వానమబ్బుల్లా రాక్షసులు కమ్ముకొచ్చారు. మారీచ సుబాహులు వేదిక మీద రక్తధారలు కురిపించారు.
43. రాముడు మెరిసే మానవాస్త్రాన్ని సంధించి మారీచుడి గుండెపై వదిలాడు. అది అతన్ని నూరు యోజనాల దూరాన సముద్రంలోకి విసిరేసింది.
44. చూడు లక్ష్మణా, ఈ చల్లని మానవాస్త్రం అతన్ని మూర్ఛపరిచి తీసుకుపోయింది, కానీ ప్రాణం తీయలేదు అన్నాడు రాముడు. *(verse slide: Valmiki Ramayana 1.30.20 (vulgate))*
45. తర్వాత ఆగ్నేయాస్త్రంతో సుబాహుడిని నేలకూల్చాడు, వాయవ్యాస్త్రంతో మిగిలినవారిని తుడిచిపెట్టాడు.
46. యాగం పూర్తయింది. నా పని నెరవేరింది, సిద్ధాశ్రమం పేరును నువ్వు సార్థకం చేశావు అన్నారు విశ్వామిత్రుడు.
47. అలా, చిన్నవాడని తండ్రి భయపడిన ఆ రాకుమారుడు గురువుల మాట నిలబెట్టాడు. ఆరు రోజులు నిద్ర మాని యజ్ఞాగ్నిని కాపాడాడు, యుద్ధంలోనూ ఒకరి ప్రాణం తీయకుండా వదిలాడు.
48. మర్నాడు ఉదయం, విశ్వామిత్రుడిని ముందుంచుకుని మునులు మిథిలలో జనకుడి యజ్ఞం గురించి చెప్పారు. దేవాసురులు, రాక్షసులు ఎవరూ ఎక్కుపెట్టలేని ఒక అద్భుతమైన విల్లు అక్కడ ఉంది, ఇక మనుషుల మాటే లేదు. *(verse slide: Valmiki Ramayana 1.31.9 (vulgate))*
49. ఎందరో రాజులు ప్రయత్నించి ఓడిపోయారు. ఆశ్రమపు జింకలూ పక్షులూ కొంత దూరం వెంట రాగా, విశ్వామిత్రుడు ఉత్తరంగా, ఆ విల్లు ఎదురుచూస్తున్న మిథిల వైపు బయలుదేరారు.
50. బాలకాండలో మొదటి భాగం ఇక్కడ విశ్రమిస్తుంది. యజ్ఞాగ్ని ప్రశాంతంగా వెలుగుతోంది, మిథిలకు దారి తెరుచుకుంది, రాముడి కథ ముందుకు సాగుతుంది.


## Scene table
Visual direction is shared with English (see `en/script.md` scene table); only timing differs.

| # | Ch | Start | Speech s | Pause | Segment/kind | Locator (`quote_src`) |
|---|---|---|---|---|---|---|
| 1 | – | 0:00 | 5.6 | 0.25 | cold_open | VR 1.20.2, 1.20.7, 1.30.7–10 (vulgate) |
| 2 | – | 0:05 | 9.9 | 0.25 | cold_open | VR 1.30.5–6, 1.30.11–12 (vulgate) |
| 3 | – | 0:16 | 6.9 | 0.5 | cold_open | VR 1.19.21, 1.20.2, 1.27.23, 1.28.2 (vulgate) |
| 4 | – | 0:23 | 8.3 | 0.9 | title | VR 1.2.3–9 (vulgate) |
| 5 | 1 | 0:32 | 6.6 | 0.25 |  | VR 1.1.1, 1.2.2 (vulgate) |
| 6 | 1 | 0:39 | 9.4 | 0.5 | verse | VR 1.1.2–4 (vulgate) |
| 7 | 1 | 0:49 | 9.1 | 0.25 |  | VR 1.1.6–8 (vulgate) |
| 8 | 1 | 0:58 | 11.6 | 0.25 |  | VR 1.1 (Narada's summary), 1.2.2–9 (vulgate) |
| 9 | 1 | 1:10 | 9.8 | 0.6 |  | VR 1.2.10–12 (vulgate) |
| 10 | 1 | 1:21 | 12.3 | 0.7 | verse | VR 1.2.13–15 (vulgate) |
| 11 | 1 | 1:34 | 10.6 | 0.25 |  | VR 1.2.16–19 (vulgate) |
| 12 | 1 | 1:44 | 14.3 | 0.9 |  | VR 1.2.22–24, 1.2.31–37, 1.2.40–41 (vulgate) |
| 13 | 2 | 2:00 | 9.9 | 0.25 |  | VR 1.5.5–9, 1.6.1–6 (vulgate) |
| 14 | 2 | 2:10 | 7.6 | 0.25 |  | VR 1.8.1, 1.8.8 (vulgate) |
| 15 | 2 | 2:18 | 9.6 | 0.25 |  | VR 1.8.2–12, sargas 1.9–1.14 (vulgate) |
| 16 | 2 | 2:28 | 13.0 | 0.25 |  | VR 1.15.1–10 (vulgate) |
| 17 | 2 | 2:41 | 11.5 | 0.5 |  | VR 1.15.13–14, 1.16.3–8 (vulgate) |
| 18 | 2 | 2:53 | 11.8 | 0.25 |  | VR 1.16.11–20 (vulgate) |
| 19 | 2 | 3:05 | 12.3 | 0.5 | verse | VR 1.16.23, 1.16.27–29 (vulgate) |
| 20 | 2 | 3:18 | 11.0 | 0.25 |  | VR 1.18.8–14, 1.18.17–19 (vulgate) |
| 21 | 2 | 3:29 | 16.7 | 0.9 |  | VR 1.18.29–31, 1.18.36–39 (vulgate) |
| 22 | 3 | 3:46 | 8.6 | 0.25 |  | VR 1.18.38–58 (vulgate) |
| 23 | 3 | 3:55 | 12.5 | 0.25 |  | VR 1.19.4–9, 1.19.18 (vulgate) |
| 24 | 3 | 4:08 | 10.3 | 0.6 | verse | VR 1.19.21, 1.20.1–2 (vulgate) |
| 25 | 3 | 4:19 | 12.2 | 0.25 |  | VR 1.20.3–9, 1.20.16–25 (vulgate) |
| 26 | 3 | 4:31 | 9.4 | 0.5 |  | VR 1.20.28, 1.21.1–4 (vulgate) |
| 27 | 3 | 4:41 | 10.3 | 0.25 |  | VR 1.21.5–9 (vulgate) |
| 28 | 3 | 4:52 | 12.8 | 0.25 |  | VR 1.22.1–6 (vulgate) |
| 29 | 3 | 5:05 | 12.3 | 0.25 |  | VR 1.22.11–18, 1.22.23–24 (vulgate) |
| 30 | 3 | 5:17 | 19.9 | 0.9 | verse | VR 1.23.1–2, 1.23.5, 1.24.12–28 (vulgate); Venkatesha Suprabhatam opening (later tradition, Wikipedia 'Suprabhatam', accessed 2026-11-18) |
| 31 | 4 | 5:38 | 10.3 | 0.25 |  | VR 1.23.5, 1.24.2–5, 1.24.12–32 (vulgate) |
| 32 | 4 | 5:49 | 13.3 | 0.25 |  | VR 1.25.2, 1.25.5–13 (vulgate) |
| 33 | 4 | 6:02 | 10.3 | 0.6 | verse | VR 1.25.17–19 (vulgate) |
| 34 | 4 | 6:13 | 9.6 | 0.25 |  | VR 1.26.6–8, 1.26.12 (vulgate) |
| 35 | 4 | 6:23 | 11.0 | 0.25 |  | VR 1.26.15–23 (vulgate) |
| 36 | 4 | 6:34 | 14.7 | 0.7 |  | VR 1.26.23–28, 1.26.35 (vulgate) |
| 37 | 4 | 6:50 | 13.0 | 0.25 |  | VR 1.27.1–15, 1.27.22–26 (vulgate) |
| 38 | 4 | 7:03 | 11.6 | 0.6 | verse | VR 1.27.27, 1.28.2–3 (vulgate) |
| 39 | 4 | 7:15 | 12.2 | 0.9 |  | VR 1.28.17–22, 1.29.3–4, 1.29.23 (vulgate) |
| 40 | 5 | 7:28 | 10.1 | 0.25 |  | VR 1.29.26–30, 1.30.4–6 (vulgate) |
| 41 | 5 | 7:39 | 8.9 | 0.25 |  | VR 1.30.7–10 (vulgate) |
| 42 | 5 | 7:48 | 7.1 | 0.5 |  | VR 1.30.11–13 (vulgate) |
| 43 | 5 | 7:55 | 9.1 | 0.6 |  | VR 1.30.16–18 (vulgate) |
| 44 | 5 | 8:05 | 8.4 | 0.6 | verse | VR 1.30.19–20 (vulgate) |
| 45 | 5 | 8:14 | 7.6 | 0.25 |  | VR 1.30.22–23 (vulgate) |
| 46 | 5 | 8:22 | 7.6 | 0.9 |  | VR 1.30.24–26 (vulgate) |
| 47 | 5 | 8:30 | 12.3 | 0.25 | closing | VR 1.20.2, 1.30.5, 1.30.16–20, 1.30.26 (vulgate) |
| 48 | 5 | 8:43 | 15.0 | 0.6 | closing | VR 1.31.1–9 (vulgate) |
| 49 | 5 | 8:59 | 12.2 | 0.9 | closing | VR 1.31.10–11, 1.31.14–18 (vulgate) |
| 50 | 5 | 9:12 | 9.9 | 7.0 | end_board |  |


## Sources (edition-labelled)
- **Text:** VR (vulgate, southern recension), the verified verse table in `content/C0011/research/report.md` (sa.wikisource raw text of sargas 1, 2, 5, 6, 8, 9, 15, 16, 18–23, 31, fetched 2026-11-18; sargas 24–31 reused from C0005–C0007). Every scene keeps its English `quote_src`; `script.json` `sources` and `edition` are identical to English.
- **Re-checked for this script:** VR 1.22.3 (vulgate), स पुत्रं मूर्ध्न्युपाघ्राय राजा दशरथस्तदा, sa.wikisource raw text of sarga 22, fetched 2026-11-18 (basis for శిరస్సును ఆఘ్రాణించి in scene 28).
- **Later tradition (scene 30):** Wikipedia, "Suprabhatam" (https://en.wikipedia.org/wiki/Suprabhatam), fetched 2026-11-18: the Venkatesha Suprabhatam was "composed sometime between 1420 and 1432 CE" and "begins with this very verse" (VR 1.23.2); the M. S. Subbulakshmi rendition "is played daily in many homes and temples (especially Tirumala Tirupati)". The narration therefore says only that it "is still heard at Tirumala" (తిరుమలలో ఈనాటికీ వినిపిస్తుంది), not that a specific ritual recites it.
- **Not checked:** the Critical Edition and Goldman, so no `[CE …]` tags.

## Verse slides (9; meaning narrated, never recited in full)
Scenes 6 (VR 1.1.2), 10 (1.2.15), 19 (1.16.27), 24 (1.20.2), 30 (1.23.2), 33 (1.25.18), 38 (1.28.2), 44 (1.30.20), 48 (1.31.9), all vulgate, `devanagari` and `source` unchanged from English. Scene 30 quotes only the opening phrase in Telugu paraphrase (కౌసల్యకు సుపుత్రుడివి రామా); the verse itself stays on the slide.

## Accuracy and sensitivity notes
- **No invented dialogue or verses.** All speech is reported without quotation marks (Telugu reported speech with అన్నారు/అన్నాడు), within the verses cited in each scene's `quote_src`.
- **No digits** in narration; numbers are words (ఆరు, ఆరో, పది, పదహారేళ్లు, వెయ్యి, నూరు, పదిహేనో శతాబ్దం).
- **Lakshmana and Shatrughna:** "two sons" (1.18.14) rendered as లక్ష్మణ శత్రుఘ్నులు. "కవలలు" (twins), used in the C0003 Telugu Short, is deliberately not used.
- **"Too young":** 1.20.2 (not yet sixteen, not fit to fight rakshasas) and 1.20.7; scene 24 says పదహారేళ్లు కూడా నిండలేదు.
- **"Spared a life" (scene 47):** no motive is given, as in English; 1.30.16–20 only.
- **Scene 38:** వెనక్కి రప్పించాలి (call back) for saṃhāra = withdrawal; సంహారం is not used there. సంహరించు in scene 39 is the sage's "kill them" (1.29.23), correct in sense.
- **Who speaks of Mithila (scene 48):** the sages with Vishvamitra at their head (1.31.5–7).
- **Tataka:** her mutilation (1.26.17–18) is not mentioned; she "falls" (నేలకూలింది) only. Rama stays calm; his anger at 1.30.17 is not narrated. The hunter is వేటగాడు, not బోయవాడు (avoids a community name).
- **Deities:** Brahma, Vishnu and the sages take the honorific (-రు); teenage Rama and Ravana take the plain form, matching the approved Telugu Shorts.

## Scenes where the Telugu telling shifts emphasis slightly
- **Scene 1 (hook):** two short sentences, with రానే వచ్చారు ("came, just as feared") carrying the dread, instead of English's single clause. Same facts.
- **Scene 2:** అన్నదమ్ములు (the brothers) instead of "Rama and his brother"; Rama is named in scene 1 just before, and the shorter word keeps the line in budget.
- **Scene 7:** Narada names Rama directly (రాముడు అనే ఒక్కడిలో) and drops "the people call him Rama"; both are in 1.1.8. Cut for length.
- **Scene 11:** "fit to be sung to the strings" becomes పాడేందుకు తగినట్టు (fit to be sung); the stringed instrument is dropped for length, and the శోకం → శ్లోకం wordplay, which is the text's own (1.2.18, 1.2.40), carries the beat. Now one flowing participial sentence.
- **Scene 16:** "the sun dared not scorch him" becomes సూర్యుడు సైతం అతనికి జంకుతాడు (even the sun shrinks from him), the same idea in idiomatic Telugu (1.15.10).
- **Scene 18:** "made by the gods" becomes దివ్య పాయసం (divine payasa) for length.
- **Scene 21:** the hunting detail (Lakshmana following Rama with his bow, 1.18.31) is dropped to make room for the chapter pull (the king thinking of his sons' marriages, an unexpected guest about to arrive, 1.18.37–39). Scene 22 opens by answering it (ఆ అతిథి మరెవరో కాదు, విశ్వామిత్ర మహర్షి).
- **Scene 28:** "kissed his son's head" becomes శిరస్సును ఆఘ్రాణించి (smelled his son's head), the literal sense of मूर्ध्न्युपाघ्राय (1.22.3, re-checked) and the traditional Telugu idiom for a parent's blessing.
- **Scene 30:** names the Sri Venkateshwara Suprabhatam and Tirumala, labelled as much later (పదిహేనో శతాబ్దపు). "Gently" (మృదువుగా) is dropped to keep the scene under 20 s (19.9 s) after the chapter pull was added.
- **Scene 31:** the crossing and the forest are now told as the sage's account (…పాడుచేసిందని మహర్షి చెప్పారు), because scene 30 already reaches the forest; the facts are unchanged (1.24.2–5, 1.24.12–32).
- **Scene 32:** "man-eating rakshasi" becomes రాక్షసి. Cut for length; the curse itself stays.
- **Scene 37:** "sleep" becomes నిద్రాస్త్రం (the sleep weapon), and the list comes before the verb, as in natural Telugu order.
- **Scene 44:** "this cold arrow of Manu" becomes ఈ చల్లని మానవాస్త్రం, naming the weapon from scene 43 instead of a separate phrase about Manu (1.30.19–20).
- **Scene 49:** the walk north and the destination are folded into one sentence (ఉత్తరంగా, … మిథిల వైపు బయలుదేరారు), with the same facts (1.31.14–18).
- **Scene 50:** a shorter end-board line (10.0 s against 10.7 s in English) that no longer repeats "waiting" from scene 49. With the te-only 7.0 s music hold, the end board is about 17 s, inside the skill's 15–20 s.

## Story QA fixes (review.md, 74/100, provisional, non-native)
- **MUST 1:** the "Full narration" section had been overwritten with the Hindi text. It is regenerated from te/script.json with Telugu chapter headings (అధ్యాయం N · title), along with the scene table. The rest of the file was checked: the only Devanagari left is the quoted Sanskrit of VR 1.22.3.
- **MUST 2:** chapter pulls added in scene 21 (1.18.37–39) and scene 30 (1.23.5, 1.24.12). Scene 30 is 19.9 s.
- **SHOULD, all applied:**
  - **47:** యుద్ధంలోనూ ఒకరి ప్రాణం తీయకుండా వదిలాడు, which can no longer be read as Rama dying.
  - **36:** he stops the rain of stones with sound-aimed arrows, then lets loose one arrow as she charges (1.26.24–26).
  - **50:** pause raised to 7.0, and "waiting" is no longer repeated.
  - **3:** opens with అయితే, so కానీ no longer appears twice in a row.
  - **11, 26, 33:** joined into flowing participial or reported sentences.
  - **18:** the radiant being uses the honorific ఇవ్వండి.
  - **28:** ఆకాశం నుంచి పూలవాన కురిసింది.

## Lint result (`.venv/bin/python -m pipeline lint C0011 --lang te`)
- Verdict **PASS**, 0 findings. Estimate 570.3 s (target 480–720, fail above 780), 853 words, 50 scenes, 5 chapters (88–120 s each), cold open about 31 s of speech, first scene 5.6 s. All keywords are present, there are no digits, every verse card has a locator and an edition, and visual parity with en is intact.

## Applied learnings
Source: `data/reports/latest_insights.json` (generated 2026-11-18T12:45:35+0530). All three actions come from Shorts data; only what transfers to long-form is applied. The storytelling skill's long-form rules and lint come first.
- **A1** (anecdote, n=12, F1), "state the stakes early": **partly applied**. The stake is in the first Telugu line (scene 1) and the cold open lasts about 33 s. The 35 s beat shape is Shorts-only and is not applied.
- **A2** (anecdote, n=1, F2), "first line natively short, not translated": **applied in its long-form form**. Scene 1 is written as two short native Telugu sentences (5.6 s, 9 words), not a translation of the English hook. Frame 0 is the shared guarded-fire image. The 3.0 s Shorts limit does not apply to long-form.
- **A3** (anecdote, n=12, F6), share-prompt engagement line: **not applied in narration**, because long-form has no engagement line or subscribe lines. Pinned-comment suggestion for the packager: తొలి శ్లోకానికి కారణమైన పక్షి ఏది? (answer in the text: క్రౌంచ పక్షి, VR 1.2.10–15).
