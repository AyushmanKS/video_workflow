# C0013 "The Newborn Commander" (Ep12): Story QA before G1 (en, hi, gu, te, mr)

Reviewer: independent `reviewer` agent (read-only; saved by the main session).

**Verdict:** all five scripts can go to G1 once the three must-fixes are done: F1 (te wording), V1 and V2 (two image prompts).

- **Sensitivity plan.** Sound, and it holds in every language and in every title and caption.
  - No womb, embryo, conception or feeding wording in any narration, `emphasis` title, thumbnail headline or Next card.
  - The Ganga is always `ganga_light`, a river of light (in scene 3 the sky-river).
  - The Krittikas are always `krittika_stars`.
  - One drawn child with one head (`kumara_light`).
  - Rudra and Uma are named only; no `rudra_symbol` and no Uma figure in any of the 5 × 11 visuals.
  - The one wording that can read as pregnancy is te scene 5 మోయలేనంది (F1).
- **Accuracy.** Clean against 1.37.1–31; nothing from later traditions (no Tarakasura, Kama, Sati or Parvati; no spear, peacock or Saravana pond).
  - The एकाह्ना reading in scene 10 is defensible; softening recommended (F2).
  - "Silver" and "Rudra's radiance" are acceptable as written.
- **Verse card.** 1.37.15 text and pāda split correct.
- **Language review.** gu, te and mr are `unreviewed-language`; notes on them are not native-level.

## Lint (2026-11-23 23:03, main session; all `warn`, hook only)
| Lang | Estimate | Hook | Card starts | Main loop closes |
|---|---|---|---|---|
| en | 52.91 s | 2.66 s | 17.3 s | 90% |
| hi | 51.10 s | 2.78 s | 17.4 s | 91% |
| gu | 52.03 s | 2.75 s | 17.8 s | 91% |
| te | 52.74 s | 2.36 s | 18.8 s | 92% |
| mr | 53.52 s | 2.48 s | 18.0 s | 91% |

Every hook ≤3.0 s; every script inside 35–55 s. mr's rate is calibrated from one render.

## Scores (before fixes)
| Lang | Score | Flow | Hook | Accuracy | Sensitivity |
|---|---|---|---|---|---|
| en | 89 | 5/5 | 5/5 | 4/5 | 5/5 |
| hi | 87 | 4/5 | 5/5 | 4/5 | 5/5 |
| gu | 86 | 4/5 | 5/5 | 4/5 | 5/5 |
| te | 82 | 4/5 | 5/5 | 4/5 | 3/5 |
| mr | 85 | 4/5 | 5/5 | 4/5 | 5/5 |

Accuracy is 4/5 everywhere only because of the contested एकाह्ना reading (F2). Visual prompt direction 84, about 91 after V1–V2.

- **Flow:** en reads as one flowing, rhythmic telling; hi, gu, te and mr are natural and compact (idiom points F4–F8).
- **Hook:** "The gods' commander was a newborn child" is a true contradiction (जातमात्रस्य 1.37.24, सुकुमारवपुः 1.37.29, अभ्यषिञ्चन् 1.37.30), pays off the Ep11 card and leads on wonder. Frame 0 reads without sound.
- **Hindi commas:** no line has more than two.

## Accuracy judgements
1. **एकाह्ना, scene 10 (1.37.29):** an instrumental of time that can govern अजयत् as well as गृहीत्वा क्षीरम्, so "in one day he routed the demons" is legitimate. Word order and valmikiramayan.net tie it to the milk-taking, and the scriptwriter's own rubric scored the same claim accuracy 3 as a hook. सुकुमारवपुः ("still tender") is unambiguous and costs no time (F2). If kept, record it at G1 as an accepted reading.
2. **हिरण्यम् as "silver" (1.37.19): keep.** Traditional gloss beside काञ्चनम्; credit the gloss in metadata (F10).
3. **"Rudra's radiance", scene 4: keep.** Continuity with 1.36.17–18; the card says "such fire", avoiding a clash with तेजस्तव (1.37.15).

## Sensitivity check by language
- **en:** clean ("hold", "entrust", "set the blaze down", "born", "nurtured"); optional F5.
- **hi:** clean (सौंपो, न सँभलेगा, उतारा, जन्मा, पाला-पोसा).
- **gu:** clean (સોંપો, નહીં ઝિલાય, ઉતારી, ઉછેર્યો).
- **te:** scene 5 మోయలేనంది uses the verb for carrying a child → F1 (must-fix). Rest clean (ఇమ్మని, దించింది, పెంచగా).
- **mr:** clean (पेलवणार नाही, ठेवली, वाढवले); optional F7.
- **Titles, cards, thumbnails:** clean in all five.

**Six faces: recommend A (keep "six-faced").** षडाननः is the text's own epithet and a familiar devotional name; B puts the maternal context back beside the Krittikas and repeats scene 9; C drops a stated detail for no needed time.

## Verse card (scene 5)
तमुवाच ततो गङ्गा / सर्वदेवपुरोगमम्। / अशक्ता धारणे देव / तेजस्तव समुद्धतम्॥ — identical in all five; four 8-syllable pādas; । and ॥ correct; the only verse in 1.37.12–21 without गर्भ wording. G2: check the gu ગઙ્ગા and te గఙ్గా conjunct (V7).

## Next card, teaser, engagement line, loop
- **Next card: keep "The Childless King"** (1.38.2 प्रजाकामः स चाप्रजः); echoes the theme; "King Sagara" names the answer, "Sagara's Wish" is vague.
- **Teaser:** the sage's close (1.37.31) is accurate.
- **Engagement line "Which metals did the fire make?": keep** (answered in scene 7). hi "उस ज्वाला" has no matching word in the narration (F4).
- **Main loop:** 90–92%, at or just past the 85–90% guide, because of a short closing line (F3).
- **Applied learnings:** A1–A4 tiers and n quoted correctly; wording point F9.

## Numbered fixes
Narration (scriptwriter):
1. **F1 (must-fix), te scene 5:** మోయలేనంది → తాళలేనంది ("గంగ ధారలన్నీ జ్వలించాయి, ఈ తేజస్సు తాళలేనంది గంగ."). Also fix the rejected te hook (మోయలేకపోయింది) in hooks.json. Native confirmation owed.
2. **F2 (optional, recommended), scene 10, all:** replace "in one day" with "still tender" (सुकुमारवपुः).
   - en: "Still a tender child, the six-faced one routed the demons, and the gods anointed him commander."
   - hi: "कोमल बालक षडानन ने दैत्य-सेना जीती, और देवों ने उसे सेनापति बनाया।"
   - gu: "કોમળ બાળ ષડાનને દૈત્યસેના જીતી, ને દેવોએ તેને સેનાપતિ બનાવ્યો."
   - te: "పసివాడైన షణ్ముఖుడు దైత్యసేనను గెలవగా, దేవతలు సేనాపతిని చేశారు."
   - mr: "कोवळ्या षडाननाने दैत्यसेना जिंकली, देवांनी त्याला सेनापती केले."
3. **F3 (optional), scene 11 en/hi/gu/te:** add धन्यः/पुण्यः from 1.37.31 ("…and Kartikeya's blessed birth"; hi पावन जन्म; gu પાવન જન્મ; te పుణ్య జననం). mr unchanged.
4. **F4 (optional), hi scene 6:** "अग्नि के कहने पर गंगा ने वह ज्वाला हिमवान की ढलान पर उतारी।" or change the hi card to "उस तेज से कौन-सी धातुएँ बनीं?"
5. **F5 (optional), en scene 6:** "Agni bade her place it on Himavan's slope…"
6. **F6 (optional), hi scene 8:** "सोने के हुए" → "सोने के हो गए".
7. **F7 (optional, native), mr:** scene 4 सोपव → सोपवा; scene 5 "त्या म्हणाल्या"; scene 3 गंगेतून → गंगेमुळे; scene 6 सांगण्याने → सांगण्यावरून.
8. **F8 (optional, native), te:** scene 5 end "…తాళలేనంది ఆమె"; scene 9 "కార్తికేయుడని పేరు పెట్టారు"; honorific consistency for the Ganga.
9. **F9 (optional):** A1 wording — card starts "just before / at the opening of" the 18–25 s window in en, hi, gu.
10. **F10 (optional), metadata:** "silver (हिरण्य, as traditionally glossed)"; jātarūpa (1.37.22) safe to pin.

Visual (creative director):
11. **V1 (must-fix), scene 9:** "shown full-figure, seated cross-legged on the flat rock, crossed legs and both hands resting on the knees fully visible, open board below the rock"; rig notes "seated cross-legged".
12. **V2 (must-fix), scene 10:** "a gentle column of golden light falling from above and fading out just above his halo, a band of open dark board between the light and the halo"; "{agni_light} at the front of {devas_light} in a wide arc to the left and upper left".
13. **V3 (optional, recommended), `kumara_light`:** "a divine child" instead of "the child Kumara"; drop "short glowing hair"; add "arms held a little away from the body". Keep the still check for scenes 1, 8, 9, 10, 11.
14. **V4 (optional), palette:** "silver-white"/"silver starlight" → "bright white"/"pale warm white" (cool tones drift green).
15. **V5 (optional), scene 6:** river "entering from the left edge just below the top third".
16. **V6 (optional), scene 8:** "drawn small, seated cross-legged at its heart".
17. **V7 (G2 check):** gu/te verse-card conjunct.
18. **V8 (optional), `krittika_stars`:** drop the word "Krittika" from the visible prompt ("six small bright stars… like the Pleiades cluster").

## Waiver requests
None.
