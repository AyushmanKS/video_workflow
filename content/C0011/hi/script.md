# C0011 · बालकाण्ड भाग 1 (long-form, Hindi)

**Format:** YouTube long-form, 16:9, engine v3 (chalk puppet). This is not a Short, so the 35–55 s rules don't apply. The long-form section of the storytelling skill does.
**Working title:** रामायण · बालकाण्ड भाग 1: वाल्मीकि के पहले श्लोक से राम के पहले युद्ध तक. The packager decides the final title.
**Scope:** VR 1.1–1.30 (vulgate), with the cliff from 1.31.1–19. Same 50 scenes as `en/script.json`. Every field except `narration`, `keywords`, `tts`, `chapter_title` and the part-title `emphasis` is copied unchanged, and the build asserted this field by field.
**Estimate (`pipeline lint`, calibrated hi letter rate 6.114/s):** **606 s ≈ 10 min 6 s**, 1,573 words, 50 scenes, after the review fixes (it was 590 s). English was 566 s before its own review fixes.
- **Word count vs the brief:** 1,573 is above the 1,300–1,400 guide. Hindi postpositions (का, की, ने, से) count as separate words, and lint estimates from letters. On the skill's word budget (1,430 per 10 min at 2.64 w/s), this is about 9.9 min of speech, which matches the letter estimate.
**Lint:** PASS, no warnings, no failures.
**Voice:** Maya 2 Native `maya2:Malini`. `tts` is set only on scenes 15 and 16 (ऋष्यशृंग → "ऋष्य श्रृंग", the respelling already used in C0003). All other names are standard Hindi spellings that the voice has read correctly in Episodes 03–07.

## Cold open (scenes 1–4, about 34 s including the title scene)
> पिता ने कहा था, राम राक्षसों से लड़ने के लिए बहुत छोटे हैं... और छठे दिन, वे आ गए।
> छह दिन, छह रातें, राम और उनके भाई बिना सोए यज्ञ की अग्नि की रखवाली करते रहे, और अब, बरसाती बादलों-से राक्षस वेदी पर टूट पड़े।
> पर पिता जिस बेटे के लिए इतने डरे थे, उनके हाथों में अब वे दिव्य अस्त्र थे, जो देवताओं को भी दुर्लभ हैं।
> *(Title: बालकाण्ड · भाग 1)* लेकिन यह कहानी उस दिन से बहुत पहले, एक शांत नदी के किनारे शुरू होती है, एक कवि, एक सवाल और दो पक्षियों के साथ।

- **First line:** 19 words, estimated 5.7 s, under the 6 s long-form warning. It is stakes-first and was chosen from 3 options in `hooks.json` (rubric 27/30).
- **Bookend:** scene 47 answers it with "जिसे पिता ने युद्ध के लिए बहुत छोटा कहा था…".

## Chapters and timings (estimated)
| # | Chapter title | Scenes | Starts | Length | Re-hook |
|---|---|---|---|---|---|
| – | Cold open + part title | 1–4 | 0:00 | 34 s | the hook |
| 1 | कविता का जन्म | 5–12 | 0:34 | 98 s | "एक पुरुष में ये सब हैं" (0:55); the hunter's arrow (1:20) |
| 2 | राजा का लंबा इंतज़ार | 13–21 | 2:12 | 120 s | the sun afraid of Ravana (2:42); the being from the fire (3:12); ends on the pull "उन्हें क्या पता था कि उनके द्वार पर कौन आने वाला है" |
| 3 | द्वार पर आए महर्षि | 22–30 | 4:12 | 110 s | "राम को मुझे सौंप दो" (4:23); the earth trembles (4:58); ends on the pull toward the Ganga and the ravaged forest |
| 4 | ताटका और दिव्य अस्त्र | 31–39 | 6:02 | 117 s | "इसे मारने का मेरा मन नहीं" (6:40); the weapons bow (7:18) |
| 5 | यज्ञ की छह रातें, closing and end board | 40–50 | 7:59 | 126 s | the sky roars (8:11); Maricha hurled into the sea (8:29) |

Chapter 5 breaks down as:
- story: 7:59–9:05 (66 s);
- closing: 9:05–9:49 (44 s);
- end board: 9:49–10:05 (9.8 s of soft narration, then the 6.0 s music hold).

`chapters[].first_scene` is 5, 13, 22, 31, 40, the same as en.

## Full narration
1. पिता ने कहा था, राम राक्षसों से लड़ने के लिए बहुत छोटे हैं... और छठे दिन, वे आ गए।
2. छह दिन, छह रातें, राम और उनके भाई बिना सोए यज्ञ की अग्नि की रखवाली करते रहे, और अब, बरसाती बादलों-से राक्षस वेदी पर टूट पड़े।
3. पर पिता जिस बेटे के लिए इतने डरे थे, उनके हाथों में अब वे दिव्य अस्त्र थे, जो देवताओं को भी दुर्लभ हैं।
4. लेकिन यह कहानी उस दिन से बहुत पहले, एक शांत नदी के किनारे शुरू होती है, एक कवि, एक सवाल और दो पक्षियों के साथ।

### अध्याय 1 · कविता का जन्म
5. बहुत पहले की बात है, महर्षि वाल्मीकि ने देवर्षि नारद से, जिनसे बढ़कर वाणी का धनी कोई न था, एक सवाल पूछा।
6. आज इस संसार में ऐसा कौन है, उन्होंने पूछा, जो गुणवान भी हो और वीर भी, धर्म को जाने, सच बोले, व्रत का पक्का हो, क्रोध को जीत चुका हो, और युद्ध में जिससे देवता भी डरें? *(verse slide: Valmiki Ramayana 1.1.2 (vulgate))*
7. नारद का मन खिल उठा। बोले, ऐसे गुण दुर्लभ हैं, फिर भी एक पुरुष में ये सब हैं; वे इक्ष्वाकु वंश में जन्मे हैं, और लोग उन्हें राम कहते हैं।
8. फिर नारद राम की पूरी कथा सुनाकर आकाश-मार्ग से चले गए, और तमसा के तट पर घूमते हुए वाल्मीकि ने क्रौंच पक्षियों का एक जोड़ा देखा, जो मीठे स्वर में चहकता, पल भर भी एक-दूसरे से अलग न होता।
9. तभी उनकी आँखों के सामने, एक पापी बहेलिये ने नर पक्षी को बाण से गिरा दिया, और उसे धरती पर पड़ा देख उसकी संगिनी दुख से चीख़ उठी।
10. ऋषि का हृदय करुणा से भर गया, और मुख से अपने-आप शब्द फूट पड़े: हे बहेलिये, तुझे अनंत वर्षों तक कभी चैन न मिले, क्योंकि तूने प्रेम में डूबे जोड़े में से एक को मार डाला। *(verse slide: Valmiki Ramayana 1.2.15 (vulgate))*
11. फिर वे अपने ही शब्दों पर चकित हुए, जो चार बराबर चरणों में ढले थे और वीणा पर गाए जा सकते थे, और बोले, शोक से जन्मा यह छंद श्लोक कहलाएगा।
12. बाद में स्वयं ब्रह्मा जी आए और बोले: यह वाणी मेरी ही इच्छा से निकली है, अब राम की पूरी कथा कहो; जब तक पर्वत खड़े हैं और नदियाँ बहती हैं, यह कथा कही जाएगी। और इस तरह एक ऋषि का शोक श्लोक बना, और श्लोक बन गया रामायण।

### अध्याय 2 · राजा का लंबा इंतज़ार
13. यह कथा शुरू होती है सरयू तट पर बसी अयोध्या से, जिसे स्वयं मनु ने बसाया था; वहाँ के राजा दशरथ सत्यवादी थे, ज्ञानी थे, और प्रजा के प्यारे थे।
14. पर इतने महान राजा का वंश आगे बढ़ाने वाला कोई पुत्र नहीं था, और उन्होंने कहा, पुत्र के बिना मुझे कोई सुख नहीं।
15. तब उन्होंने अश्वमेध यज्ञ का निश्चय किया; वसिष्ठ जी और पुरोहितों ने आशीर्वाद दिया, और सरयू के तट पर यज्ञ कराने युवा ऋषि ऋष्यशृंग पधारे।
16. यज्ञ के बाद ऋष्यशृंग ने पुत्र-प्राप्ति के लिए एक और अग्नि जलाई; वहाँ जुटे देवता डरकर ब्रह्मा जी से बोले, वरदान के घमंड में रावण तीनों लोकों को सता रहा है, सूरज भी उसे तपाने से डरता है।
17. उसे वर मिला था कि देवता और दानव उसे मार न सकें, पर मनुष्यों को उसने इतना तुच्छ समझा कि उनका नाम तक न लिया; इसलिए भगवान विष्णु ने मनुष्य बनकर, दशरथ के घर जन्म लेना स्वीकार किया।
18. तब अग्नि से सूर्य-सा तेजस्वी एक दिव्य पुरुष प्रकट हुआ, हाथों में देवताओं की बनाई खीर का सोने का पात्र लिए, और बोला, यह अपनी रानियों को दीजिए, आपको पुत्र होंगे।
19. राजा को लगा, जैसे निर्धन को ख़ज़ाना मिल गया हो; उन्होंने आधी खीर कौशल्या को दी, बची का आधा सुमित्रा को, उसका आधा कैकेयी को, और कुछ सोचकर आख़िरी भाग फिर सुमित्रा को। *(verse slide: Valmiki Ramayana 1.16.27 (vulgate))*
20. फिर चैत्र की नवमी को कौशल्या की गोद में राम का जन्म हुआ; कैकेयी से भरत, सुमित्रा से लक्ष्मण और शत्रुघ्न जन्मे, और सारी अयोध्या गीत और नृत्य से गूँज उठी।
21. चारों राजकुमार विद्या और धनुर्विद्या में निखरते गए, और लक्ष्मण तो जैसे राम के दूसरे प्राण थे; राम उनके बिना सोते तक नहीं थे, और शिकार पर भी लक्ष्मण धनुष लिए साथ चलते। राजकुमार बड़े हो रहे थे, और राजा उनके विवाह की सोच ही रहे थे; उन्हें क्या पता था कि उनके द्वार पर कौन आने वाला है।

### अध्याय 3 · द्वार पर आए महर्षि
22. तभी एक दिन महर्षि विश्वामित्र राजमहल आ पहुँचे; दशरथ आनंद से भरकर उनकी अगवानी को निकले, और वचन दिया कि वे जो माँगेंगे, मिलेगा।
23. ऋषि बोले, मैं एक व्रत में हूँ, और मारीच और सुबाहु नाम के दो राक्षस मेरी वेदी पर मांस और रक्त बरसाते हैं; व्रत में मैं शाप भी नहीं दे सकता, सो दस रातों के लिए राम को मुझे सौंप दो।
24. यह सुनते ही राजा अचेत हो गए; होश आया तो बोले, मेरे कमलनयन राम अभी सोलह बरस के भी नहीं हुए, वे राक्षसों से युद्ध के योग्य नहीं हैं। *(verse slide: Valmiki Ramayana 1.20.2 (vulgate))*
25. उन्होंने विनती की, मेरी सेना ले जाइए, मुझे ले चलिए, राम के बिना मैं पल भर नहीं जी सकता; और जब सुना कि इनके पीछे रावण है, तो उनका डर और गहरा गया।
26. तब विश्वामित्र का क्रोध ऐसे धधक उठा, जैसे घी पाकर अग्नि धधकती है; बोले, रघुकुल का राजा, और अपना वचन तोड़े! और सारी धरती काँप उठी।
27. तब कुलगुरु वसिष्ठ ने राजा को सँभाला: आप इक्ष्वाकु वंश के हैं, धर्म मत छोड़िए; इन ऋषि की छाया में राम वैसे ही सुरक्षित हैं, जैसे अग्नि से घिरा अमृत।
28. तब माँ का आशीर्वाद लेकर दशरथ ने बेटे का माथा चूमा और उन्हें ऋषि को सौंप दिया; मंद-मंद हवा चली, आकाश से फूल बरसे, और लक्ष्मण भाई के पीछे-पीछे चल पड़े।
29. सरयू के तट पर ऋषि ने राम को दो मंत्र दिए, बला और अतिबला, कि न थकान उन्हें छुए, न भूख; और उस रात दोनों राजकुमार घास के बिछौने पर सोए।
30. भोर में ऋषि ने उन्हें जगाया: राम, कौशल्या तुम जैसा पुत्र पाकर धन्य हैं, उठो पुरुषसिंह, संध्या का समय है। सदियों बाद रचा गया वेंकटेश सुप्रभातम् इन्हीं शब्दों से शुरू होता है। उसी सुबह वे गंगा की ओर चले, जिसके पार एक भयानक वन था, और उसे उजाड़ने वाली भी वहीं थी। *(verse slide: Valmiki Ramayana 1.23.2 (vulgate))*

### अध्याय 4 · ताटका और दिव्य अस्त्र
31. गंगा पार करके वे उसी वन में पहुँचे, जहाँ कभी मलद और करूष के समृद्ध जनपद थे, पर हज़ार हाथियों जितने बल वाली यक्षिणी ताटका ने सब उजाड़ दिया था।
32. राम ने पूछा, एक यक्षिणी में इतना बल कैसे? ऋषि बोले, यह ब्रह्मा जी का वरदान था; फिर जब उसने पुत्र मारीच के साथ अगस्त्य मुनि पर हमला किया, तो उनके शाप से वह नरभक्षी राक्षसी बन गई।
33. वह स्त्री है, यह सोचकर पीछे मत हटो, ऋषि ने समझाया; प्रजा के रक्षक को कर्तव्य निभाना ही पड़ता है, काम कितना ही कठोर लगे, यही सदा से राजधर्म है। *(verse slide: Valmiki Ramayana 1.25.18 (vulgate))*
34. राम ने धनुष की डोरी टंकारी, और ताटका गरजती हुई दौड़ी; फिर भी राम ने लक्ष्मण से कहा, इसे मारने का मेरा मन नहीं है, मैं बस इसे रोकूँगा।
35. पर उसने धूल का तूफ़ान उठाया, पत्थर बरसाए, और माया से अदृश्य हो गई; तब ऋषि ने पुकारा, राम, बस करो यह दया, साँझ होने को है, और साँझ ढले राक्षस अजेय हो जाते हैं।
36. तब राम ने केवल आवाज़ के सहारे बाण चलाकर पत्थरों की बौछार रोक दी, और जब वह झपटती हुई आई, तो एक ही बाण से वह गिर पड़ी; देवताओं ने जय-जयकार की, और शापित वन फिर से खिल उठा।
37. अगली सुबह ऋषि ने मुस्कुराकर अपने सारे अस्त्र राम को सौंप दिए, कालचक्र, वज्र, ब्रह्मास्त्र, अग्नि, वायु, यहाँ तक कि निद्रा का अस्त्र भी; और वे सब हाथ जोड़कर बोले, हम आपके सेवक हैं।
38. राम ने उन्हें छूकर कहा, मेरे मन में वास करो; फिर ऋषि से बोले, अब देवता भी मुझे हरा नहीं सकते, पर यह भी सिखाइए कि छोड़े हुए अस्त्रों को वापस कैसे बुलाऊँ; और ऋषि ने वह भी सिखा दिया। *(verse slide: Valmiki Ramayana 1.28.2 (vulgate))*
39. आख़िर वे सिद्धाश्रम पहुँचे, जो पर्वत के पास मेघ-सा छाया एक उपवन था; ऋषि बोले, यहीं राक्षस मेरा यज्ञ भंग करते हैं, और यहीं, हे पुरुषसिंह, तुम्हें उनका अंत करना है।

### अध्याय 5 · यज्ञ की छह रातें
40. उसी दिन विश्वामित्र ने दीक्षा लेकर मौन धारण किया, और ऋषियों के कहने पर, छह दिन और छह रातें, बिना सोए, राम और लक्ष्मण उनका पहरा देते रहे।
41. छठे दिन राम ने लक्ष्मण से कहा, सावधान रहना; उनके इतना कहते ही वेदी की अग्नि धधक उठी, और आकाश में एक भयानक गर्जना गूँजी।
42. बरसाती बादलों की तरह राक्षस घिर आए, और मारीच और सुबाहु ने वेदी पर रक्त की धाराएँ बरसा दीं।
43. राम ने चमचमाता मानवास्त्र धनुष पर चढ़ाकर मारीच की छाती पर छोड़ा, और वह उसे पूरे सौ योजन दूर, उफनते समुद्र में फेंक आया।
44. राम बोले, देखो लक्ष्मण, मनु का यह शीतल बाण इसे अचेत करके दूर ले गया, पर इसके प्राण नहीं लिए। *(verse slide: Valmiki Ramayana 1.30.20 (vulgate))*
45. फिर आग्नेय अस्त्र से उन्होंने सुबाहु को धरती पर गिरा दिया, और वायव्य अस्त्र से बाकी सब राक्षसों को उड़ा दिया।
46. यज्ञ पूरा हुआ, और विश्वामित्र बोले, मेरा प्रयोजन पूरा हुआ, राम, तुमने सिद्धाश्रम का नाम सार्थक कर दिया।
47. और इस तरह, जिसे पिता ने युद्ध के लिए बहुत छोटा कहा था, उस राजकुमार ने गुरुओं की बात रखी, छह दिन बिना सोए ऋषि की अग्नि बचाई, और युद्ध में भी एक शत्रु की जान बख़्श दी।
48. अगली सुबह, विश्वामित्र को आगे करके ऋषियों ने मिथिला में राजा जनक के यज्ञ की बात छेड़ी, और वहाँ रखे उस अद्भुत धनुष की, जिस पर न देवता प्रत्यंचा चढ़ा सकते हैं, न असुर, न राक्षस, मनुष्य तो क्या। *(verse slide: Valmiki Ramayana 1.31.9 (vulgate))*
49. बड़े-बड़े राजकुमार उसे आज़माकर हार चुके थे; तब विश्वामित्र उत्तर की ओर चल पड़े, सिद्धाश्रम के हिरण और पक्षी कुछ दूर साथ आए, और राह मुड़ चली मिथिला की ओर, जहाँ वह धनुष प्रतीक्षा में था।
50. यहाँ बालकाण्ड का पहला भाग विश्राम लेता है। यज्ञ की अग्नि अब शांत जल रही है, और मिथिला की राह खुली है; राम की कथा वहीं से आगे बढ़ेगी।

## Sources (edition-labelled)
These are the same as `en/script.json` `sources`, copied unchanged. The claim-by-claim verse table is in `content/C0011/research/report.md`.
- **Text:** VR (vulgate, southern recension), sa.wikisource रामायणम्/बालकाण्डम्, raw text fetched 2026-11-18.
- **Cross-checks:** sargas 2 and 23 on valmikiramayan.net via the Internet Archive copy, accessed 2026-11-18.
- **Reused:** sargas 24–31 come from the verified C0005–C0007 tables.
- **Not checked:** the Critical Edition and Goldman, so there are no `[CE]` tags.
- **Later tradition (scene 30 only):** Wikipedia, "Suprabhatam" (https://en.wikipedia.org/wiki/Suprabhatam), accessed 2026-11-18. The Venkatesha Suprabhatam opens with VR 1.23.2.
- **Locators:** every scene keeps its en `quote_src`, and every verse slide keeps its `source` and `edition`.

## Verse slides (9; the meaning is narrated, the verse is never read aloud)
Scenes 6 (1.1.2), 10 (1.2.15), 19 (1.16.27), 24 (1.20.2), 30 (1.23.2), 33 (1.25.18), 38 (1.28.2), 44 (1.30.20) and 48 (1.31.9). All are vulgate, with the same `devanagari` as en.

## Accuracy and language notes
- **Scene 38:** "छोड़े हुए अस्त्रों को वापस कैसे बुलाऊँ" renders the withdrawals (1.28.2, saṃhāra = recalling a released weapon). This follows the review; the earlier "लौटाऊँ" read as "give back". संहार does not appear in the narration.
- **Scene 30, Suprabhatam:** the line is framed as later tradition ("सदियों बाद रचा गया वेंकटेश सुप्रभातम्…"). It names the hymn, following the review's suggestion, but no place. The scene then ends on the chapter pull (VR 1.23.5, 1.24.12) and runs 19.5 s, under the 20 s cap.
- **Scenes 9–10, the hunter:** he is called बहेलिया (a bird-catcher, the occupation), not निषाद. The verse slide keeps मा निषाद in Sanskrit, but the narration avoids any word that could read as caste coding (the en notes ask for no caste coding for the hunter). Using "बहेलिये" as the address in scene 10 is a paraphrase of the verse's meaning, not a quotation.
- **Scene 11:** शोक and श्लोक stand side by side, which follows the text (1.2.18; 1.2.40 शोकः श्लोकत्वमागतः). No folk etymology ("इसलिए…") is claimed.
- **Scenes 30 and 39, "tiger among men" (नरशार्दूल):** rendered as the idiomatic Hindi epithet "पुरुषसिंह". A literal "पुरुषों में बाघ" sounds foreign in Hindi.
- **Scene 28:** "माथा चूमा" is the natural Hindi for the king kissing his son's head (1.22.3).
- **Scene 20:** "सुमित्रा से लक्ष्मण और शत्रुघ्न जन्मे": two sons, not "twins" (1.18.14).
- **Scene 47:** "एक शत्रु की जान बख़्श दी" follows 1.30.20 (the Manava "does not take his life"). It does not say the others were spared (1.30.22–24), and it gives no motive. The golden-deer commentary is not used.
- **Scene 48:** the sages speak, "विश्वामित्र को आगे करके" (1.31.5–7).
- **Sensitivity:**
  - Tataka's mutilation (1.26.17–18) is not mentioned; she simply "गिर पड़ी".
  - Rama is calm throughout; his anger at 1.30.17 is not narrated.
  - Sita does not appear.
  - The blood falls only "वेदी पर".
- **Numbers:** all are written as words (छह, सोलह, दस, सौ, हज़ार). Lint allows digits for hi, but words read better aloud.
- **Speech:** all speech is reported without quotation marks. No dialogue or verse is invented, and paraphrases stay inside each scene's cited verses.
- **Register:** conversational standard Hindi with natural तत्सम words (आश्रम, करुणा, प्रयोजन). There is no Hinglish. Sages take honorific plural verbs.

## Lint result (`.venv/bin/python -m pipeline lint C0011 --lang hi`)
- **Verdict:** PASS, 0 warnings, 0 failures (after the review fixes).
- **Estimate:** 606.33 s (target 480–720 s; fails above 780 s), 1,573 words.
- **Structure:** 50 scenes, with visual parity against en. 5 chapters of 98–126 s. Cold open 34 s. First scene 5.7 s. Longest scene: 30 at 19.5 s.
- **Keywords:** all are present in the narration.

## Review fixes (Story QA 82/100, content/C0011/hi/review.md)
| Item | Level | Change |
|---|---|---|
| Scene 21 → Ch3 pull | MUST | Added "राजकुमार बड़े हो रहे थे, और राजा उनके विवाह की सोच ही रहे थे; उन्हें क्या पता था कि उनके द्वार पर कौन आने वाला है।" (VR 1.18.37–39; `quote_src` is now 1.18.29–32, 1.18.36–39). The hunting clause is shortened to fit. Scene 22 now opens with "तभी एक दिन…". |
| Scene 30 → Ch4 pull | MUST | Ends on "उसी सुबह वे गंगा की ओर चले, जिसके पार एक भयानक वन था, और उसे उजाड़ने वाली भी वहीं थी।" (VR 1.23.5, 1.24.12, added to `quote_src`). To stay at 19.5 s, "प्यार से" and "आज भी मंदिरों में भोर को गाया जाता है" were dropped. Scene 31 now says "उसी वन में", so "भयानक वन" isn't repeated. |
| Scene 38 | MUST | "छोड़े हुए अस्त्रों को वापस कैसे बुलाऊँ"; keyword बुलाऊँ. |
| Scene 36 | SHOULD, applied | Arrows aimed by sound stop the shower of stones (1.26.24–25), then one arrow fells her as she charges (1.26.26). |
| Scene 47 | SHOULD, applied | "एक शत्रु की जान बख़्श दी". |
| Scene 17 | SHOULD, applied | "उसे वर मिला था कि देवता और दानव उसे मार न सकें…". |
| Scenes 3/4 | SHOULD, applied | Scene 4 opens with "लेकिन यह कहानी…". |
| Scene 10 | SHOULD, applied | Curse register: "हे बहेलिये, तुझे… कभी चैन न मिले, क्योंकि तूने…". |
| Scene 24 | SHOULD, applied | "…सोलह बरस के भी नहीं हुए, वे राक्षसों से युद्ध के योग्य नहीं हैं।" |
| Scene 50 | SHOULD, applied | "प्रतीक्षा" removed: "…मिथिला की राह खुली है; राम की कथा वहीं से आगे बढ़ेगी।" |
| Scene 30 hymn name | SHOULD (optional), applied in part | "वेंकटेश सुप्रभातम्". The honorific "श्री" was dropped to keep the scene under 20 s. |

**Note on copied fields:** `quote_src` on scenes 21 and 30 now carries the new pull locators. The en file had not added them yet at the time of this edit. Lint doesn't check `quote_src` for parity, but en should carry the same locators once its pulls are in.

## Applied learnings
Source: `data/reports/latest_insights.json` (generated 2026-11-18T12:45:35+0530). The decisions are the same as en; only the parts that transfer to long-form are applied. Approved rules take precedence.

| Action | Tier · n | Applied? | Where and how |
|---|---|---|---|
| A1: state the stakes early (F1) | anecdote · n=12 | **Partly** | The stake is in the first Hindi sentence (scene 1). The turn ("पर यह कहानी उस दिन से बहुत पहले…") comes at about 24 s. The 35 s shape is Shorts-only. |
| A2: short, stakes-first first line written natively; frame 0 readable (F2) | anecdote · n=1 | **Yes, long-form version** | The first line was written natively in Hindi (not translated): 19 words, 5.7 s, under the 6 s long-form warning. Frame 0 is the shared en direction. |
| A3: engagement line (F6) | anecdote · n=12 | **No** (in narration) | Long-form has no engagement line. Hindi pinned-comment suggestion for the packager: "पहला श्लोक किस पक्षी की मृत्यु से जन्मा?" (answer: क्रौंच, VR 1.2.10–15). |

`script.json` carries these as top-level `learnings`.
