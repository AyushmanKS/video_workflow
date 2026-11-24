# Strategy: C0013 (scriptwriter)

**Decision:** continue in strict narrative order. Open on 1.37.1 (while Rudra does tapas, the gods led by Agni go to Brahma for a commander) and pay off the Ep11 card ("The Gods' Commander") twice: the hook names the answer (a newborn child), and scene 2 tells the gods' search. Tell all of sarga 37 in eleven scenes, and stop where the sarga stops: the sage's own close, "this is the Ganga's account, and the birth of Kumara" (1.37.31).
- **Card:** "Next: The Childless King" (hi आगे: निःसंतान राजा; gu આગળ: નિઃસંતાન રાજા; te తర్వాత: సంతానం లేని రాజు; mr पुढे: निपुत्रिक राजा). It names what opens sarga 38: Sagara, king of Ayodhya, righteous, longing for children and childless (प्रजाकामः स चाप्रजः, 1.38.2). Sarga 38 was read only to label the card.
- **Not narrated:** anything from sarga 38; the phalashruti (1.37.32).

**Lint estimates** (all pass; only the advisory hook >2.2 s warning remains, as in Ep10–11):

| Lang | Lint | Hook | Card starts | Loop closes |
|---|---|---|---|---|
| en | 53.06 s | 2.66 s | 17.3 s | 90% |
| hi | 51.81 s | 2.78 s | 17.3 s | 90% |
| gu | 51.93 s | 2.75 s | 17.6 s | 90% |
| te | 53.32 s | 2.36 s | 18.5 s | 91% |
| mr | 53.58 s | 2.48 s | 18.0 s | 91% |

These are the figures after the story-review fixes (content/C0013/review.md). Before the fixes they were en 52.91, hi 51.10, gu 52.03, te 52.74 and mr 53.52 s.

- hi (51.81 s) and gu (51.93 s) stay at or below 52 s and leave room for their render overshoot (about 1.5 s per the brief; Ep10 ran hi 52.96 → 55.9 s and gu 53.82 → 55.83 s). Even at Ep10's overshoot they would render near 54.0 s, inside 55 s.
- mr renders shorter than its estimate (Ep10: 54.08 → 52.4 s); its rate is still calibrated from one render. en tracks its estimate within about 1.4 s.

## Why this shape
- **One telling.** Sarga 37 moves from need (the gods without a commander, and without sons), to a plan (Brahma: Agni and the Ganga), to a limit (the Ganga cannot hold the radiance), to wonder (metals, a golden forest, a child of fire), to care (the six stars), to triumph (one day, commander).
- **Turn: the Ganga's refusal (verse card 1.37.15).** "O god, I cannot hold your risen radiance." The plan meets a limit, and the verse carries no sensitive wording, which is why it was chosen over 1.37.12 or 1.37.17 (both say गर्भ). It starts at 17.3–18.5 s, just before or at the opening of A1's 18–25 s window, before the 13 s drop-off grows.
- **Main loop:** how could a newborn be the gods' commander, when Uma's curse left the gods without sons? It closes at the end of scene 10 (anointed commander, 1.37.30), at 90–91% of runtime by lint, at the late edge of the 85–90% guide. Review F3 lengthened the closing line ("blessed birth", धन्यः पुण्यः 1.37.31) in en, hi, gu and te, which brought it from 90–92% to 90–91%.
- **Teaser 1.37.31.** The sage himself closes the Ganga's account and the birth of Kumara; the Next card then names the childless king who opens sarga 38. Ep10's question (the river of three paths) stays open, honestly, for sargas 38–44.

**Next card alternatives (owner's choice at G1):**
- "The Childless King" (chosen: it echoes this episode's theme, gods without sons, and names the stake of 1.38.2 without the name).
- "King Sagara" (names him outright; hi आगे: राजा सगर; gu આગળ: રાજા સગર; te తర్వాత: సగర మహారాజు; mr पुढे: राजा सगर).
- "Sagara's Wish" (प्रजाकामः, 1.38.2).

## Angle and hook
**Contradiction that pays off the card:** the gods' commander was a newborn child (1.37.23–30). It leads on wonder, never on the radiance's passage through Agni and the Ganga.

| Language | Hook | Spoken |
|---|---|---|
| en | "The gods' commander was a newborn child." | 2.66 s |
| hi | "देवों का सेनापति एक नवजात बालक था।" | 2.78 s |
| gu | "દેવોનો સેનાપતિ નવજાત બાળક હતો." | 2.75 s |
| te | "దేవతల సేనాపతి ఓ పసిబిడ్డ." | 2.36 s |
| mr | "देवांचा सेनापती नवजात बाळ होता." | 2.48 s |

- **Frame 0:** a small child of golden light seated among the golden reeds below the glowing white mountain, with the gods' orbs bowed before him on the left. Muted, it reads as "the gods before a radiant child".
- **Rejected hooks:**
  - "One day old, he beat a demon army" (26/30). The strongest gap, but एकाह्ना (1.37.29) may belong to the milk-taking, not the victory; accuracy 3. After review F2 the body does not use "in one day" either.
  - "Even the Ganga could not hold this fire" (26/30). True, but it opens mid-story and the payoff is not in it.
  - "Cursed to have no sons, the gods needed a commander" (23/30). It is over 3.0 s in en, and it leads on the curse.

## Beats (11 scenes)
| Beat | Scene | Content (locator) |
|---|---|---|
| H1/H2 | 1 | the gods' commander was a newborn child (1.37.23–30) |
| C | 2 | while Rudra does tapas the gods ask Brahma for a commander (1.37.1–4); pays off the Ep11 card |
| C/E1 | 3 | Brahma: Uma's curse stands, but Agni and the Ganga will bring one (1.37.5–7) |
| E1 | 4 | on Kailasa the gods bid Agni entrust Rudra's radiance to the Ganga (1.37.10–12); 0.5 s silence |
| T | 5 | verse card 1.37.15: her streams blaze, and she cannot hold such fire (1.37.14–16); 0.5 s silence |
| E2 | 6 | at Agni's word she lays the blaze on Himavat's slope (1.37.16–18) |
| P1 | 7 | the wonder: gold and silver, copper, iron, tin and lead (1.37.18–20) |
| E2 | 8 | reeds and trees turn gold; the child is born, bright as fire (1.37.21–23, 26–27) |
| E2 | 9 | six Krittika stars nurture him; the gods name him Kartikeya (1.37.23–25); 0.3 s silence |
| P | 10 | still tender, the six-faced child routs the demons; the gods anoint him commander (1.37.28–30); main loop closes |
| N | 11 | the sage: that was the Ganga's tale, and Kartikeya's blessed birth (1.37.31) |

## Silences, loop and engagement
- **Silences:** 0.5 s after scene 4, 0.5 s after the verse card and 0.3 s after scene 9 (before the payoff).
- **Loop type:** composition. Scene 11 reuses frame 0's framing at first light: the child large in the lower-right foreground among the golden reeds, and on the left, where the gods' orbs hovered, the six Krittika stars, with the Ganga's river of light far behind.
- **Engagement (A4):** the title card on scene 10 reads "Which metals did the fire make?". The answer, gold, silver, copper, iron, tin and lead, is in scene 7 (1.37.18–20). It is a wonder question with a safe answer, chosen so that replies do not drift to the sensitive verses.
  - hi: उस ज्वाला से कौन-सी धातुएँ बनीं?
  - gu: એ જ્વાળાથી કઈ ધાતુઓ બની?
  - te: ఆ జ్వాల నుంచి ఏ లోహాలు పుట్టాయి?
  - mr: त्या ज्वालेतून कोणते धातू उपजले?
  - **Suggested pinned comment:** the same line, with an optional follow-up fact: "Valmiki says that since that day gold has been called jātarūpa (1.37.22)."

## Extended sensitivity plan (for the owner at G1)
Sarga 37 is more delicate than 36. The text speaks plainly of conception, a womb, and nursing (गर्भ, 1.37.12, 17, 21, 26–27; स्तनजं पयः, 1.37.28). The plan below governs the narration in every language, the visuals and the creative director's prompts. It was written before any narration.

1. **Agni and the Ganga (1.37.7, 11–14).**
   - **Narration:** only as radiance charged and entrusted. Brahma says "Agni and the Ganga would bring one" (1.37.7); the gods bid Agni "entrust Rudra's radiance to the Ganga" (1.37.11); "all her streams blazed" (1.37.14).
   - **Not rendered in any language:** गर्भ, womb, embryo, conceive, impregnate, beget or bear-a-child wording, and the begetting verb of 1.37.7 (जनयिष्यति). The Ganga's divine form and Agni spreading about her (1.37.13) are left out entirely. "Hold" is used instead of "bear" in English, because "bear" can be read as childbirth.
   - **Visual:** the radiance is a small white star inside Agni's flame (scene 4), then a blaze of light at the river's edge (scene 6). The Ganga is always `ganga_light`, a river of light, never a woman or a body; in scene 3 she is the sky-river (आकाशगङ्गा) as a band of starlit light. Nothing anatomical is drawn.
2. **The Ganga cannot bear the blaze and sets it on Himavat's side (1.37.15–18).**
   - **Narration:** "All her streams blazed, and the Ganga said she could not hold such fire"; "Agni bade her lay it on Himavan's slope, and she set the blaze down". It is a river laying down a fire too bright to hold. Her pain (सम्प्रव्यथितचेतना) is carried only by "such fire". en "place it" (review F5), hi उतारी, gu ઉતારી, te దించింది, mr ठेवली. te scene 5 says తాళలేనంది ("could not endure"), not మోయలేనంది, whose verb is also used for carrying a child (review F1, must-fix; native confirmation owed).
   - **Turn:** the verse card is 1.37.15, the one verse of this passage without गर्भ wording.
   - **Visual (scene 6):** a high view of a snowy slope, the river of light curving down it and away from a blaze of white-gold light resting on the rocks.
3. **The metals (1.37.18–22).**
   - **Narration:** the safe wonder beat, used as P1 (scene 7): "Where it touched the earth rose gold and silver, copper, iron, tin and lead"; then "Reeds and trees turned gold" (scene 8).
   - **Engagement:** the share prompt on scene 10 asks about the metals.
   - **Visual (scene 7):** seams of gold, silver, copper, iron and pale tin and lead branching through the rock from the blaze like roots of light. In the rig, the seams light up one colour at a time. Scene 8 shows the whole forest turned gold.
4. **The Krittikas (1.37.23–24, 28).**
   - **Narration:** "Six Krittika stars nurtured him" (hi पाला-पोसा, gu ઉછેર્યો, te పెంచగా, mr वाढवले). No feeding or nursing word in any language. क्षीरसम्भावनार्थाय is rendered as "nurture".
   - **"Son of them all" (पुत्रोऽयमस्माकं सर्वासाम्, 1.37.24):** not narrated for length; it is offered as an optional pinned-comment line.
   - **Visual (scene 9):** `krittika_stars` (new token): six small star-lights in a wide arc above the seated child, with soft beams of starlight falling toward him. They are never women and never touch him.
5. **Six faces (षडाननः, 1.37.28): options for the owner.**
   - **Option A (chosen, confirmed after review):** narrate the epithet once, in the payoff, decoupled from the Krittikas' verse. en "the six-faced child"; hi षडानन, gu ષડાનને, te షణ్ముఖుడు and mr षडाननाने, each a known name of Kartikeya. Draw a single glowing child with one head (`kumara_light`, new token), with the six star-lights standing in for the six faces (scenes 9 and 11). Rigs and image models never see six heads.
   - **Option B:** "the child of six mothers" (from सर्वासाम्, 1.37.24) instead of "six-faced". This is gentler, but "mothers" is a gloss the text does not use; same drawing.
   - **Option C:** omit the epithet. Saves about 0.5 s; the six stars still carry it visually.
   - **Not offered:** drawing six faces or six heads, or a halo with six faces painted in. Every such image is a puppet-rig and image-model risk, and it is figurative deity depiction.
6. **The name Skanda (स्कन्नं, 1.37.26–27).** Omitted. The anatomical gloss ("slipped from the womb's flow") is not usable, and no non-anatomical gloss is faithful. The narration uses only Kartikeya (1.37.25), which the gods name him for the Krittikas; the closing line uses Kartikeya for कुमार (1.37.31).
7. **Rudra and Uma.** They are named only: Rudra's tapas (scene 2), Uma's curse (scene 3) and Rudra's radiance (scene 4). They are not drawn in any scene, so the Ep11 rules (featureless silhouette with no face; Uma plain, unadorned and never touching) are not triggered. If the creative director wants Rudra in scene 2, the `rudra_symbol` token applies as is.
8. **Scope and the hook.**
   - **The hook leads on contradiction and wonder** (a newborn commander), never on the conception.
   - **The demons are not named.** The text says only दैत्यसैन्यगणान् (1.37.29); Tarakasura is Puranic. Visual: dark storm clouds drifting away, not a battle.
   - **No Puranic additions:** no Kama, Sati or Parvati; no spear, peacock or rooster banner; no six babies joined into one, and no Saravana-pond bathing story beyond the text.
   - **The child is a deity:** drawn as light, never figurative. No nudity: he wears a dhoti of light.
   - **Seeds and accents:** seeds are 13001–13011; every scene is `divine`. There are no forest or ashram accents on the blue-white subjects.

## Engine v3 (chalk puppets)
- **Composition.**
  - One main figure, the seated child of light, in three-quarter view, hands on his knees and clear of the body, with open board around the head and halo.
  - Every orb, flame and star is a separate element with open board around it. Flames keep their halos uncut. Peaks stay below the top third.
- **New tokens** (added to `profiles/characters/ramayana.json`):
  - `kumara_light`: a seated child of golden fire-light, with one round head, a featureless face, exactly two arms and a dhoti of light.
  - `krittika_stars`: six star-lights in a loose arc.
  - The creative director may refine both.
- **Rig notes.** The per-scene puppet direction is in each `script.md`. The child only breathes, and lifts or tilts his head ≤3°. The light around him carries the motion: halo pulses, starlight beams, a column of golden light at the anointing that fades out above the halo (review V2), metal seams lighting up in turn.

## Applied learnings (data/reports/latest_insights.json, 2026-11-23T22:46:37+0530)
- **A1** (anecdote, n=25): applied. The stake is in the first line. The episode uses the 55 s two-beat shape, and the card comes at 17.3–18.5 s, just before or at the opening of the 18–25 s window (review F9).
- **A2** (anecdote, n=1): applied. Hooks are 2.36–2.78 s, natively short.
- **A3** (anecdote, n=25): partly applied. The density needs the 55 s shape, so the episode was cut to the owner's 50–53 s target instead of the lower half.
- **A4** (anecdote, n=25): applied on screen. The share prompt on scene 10 is "Which metals did the fire make?", answered in scene 7.

## Risks and checks
- **Hindi speech rate:** lines keep at most two commas (scenes 3 and 7 have two).
- **mr rate:** calibrated from one render.
- **Unreviewed languages:** gu, te and mr are `unreviewed-language`.
- **The child of light (image risk):** check the scene 1, 8, 9, 10 and 11 stills for a single head, a featureless face, a dhoti, and no spear or peacock before rigging. If the model draws a realistic infant, regenerate with the token unchanged; do not add negatives.
- **Scene 7 metal seams:** may come out as abstract colour. If so, the creative director may reduce it to gold and silver seams only; the narration does not change.
- **एकाह्ना (1.37.29), resolved by review F2:** scene 10 now says "still tender" (सुकुमारवपुः) in all five languages; "in one day" is not narrated. The owner can restore it at G1 as an accepted reading (en "In one day, the six-faced child routed the demons…").
- **Reviewer note:** हिरण्यम् is rendered as "silver" following valmikiramayan.net's gloss (paired with काञ्चनम्, gold).

## Story-review fixes applied (content/C0013/review.md, 2026-11-23)
- **Must-fix:**
  - F1: te scene 5 is now గంగ ధారలన్నీ జ్వలించాయి, ఈ తేజస్సు తాళలేనంది ఆమె. The rejected te hook is now తాళలేకపోయింది.
  - V1: scene 9 shows the child full-figure, seated cross-legged on the rock, with his crossed legs and both hands on the knees fully visible and open board below the rock. New seed 13109.
  - V2: scene 10 has a column of golden light that fades out just above the halo, with a band of open board between them; the flame and the orbs form an arc to the left and upper left. New seed 13110.
- **Optional, applied:**
  - F2: scene 10 says "still tender" (en Still tender, hi कोमल बालक, gu કોમળ બાળ, te పసివాడైన, mr कोवळ्या); "in one day" is dropped. The en line is shorter than the reviewer's variant so en stays near 53 s.
  - F3: scene 11 is "blessed birth" in en, hi (पावन), gu (પાવન) and te (పుణ్య); mr is unchanged.
  - F4 (first variant): hi scene 6 is अग्नि के कहने पर गंगा ने वह ज्वाला हिमवान की ढलान पर उतारी। (matches the card's उस ज्वाला).
  - F5: en scene 6 says "place it".
  - F6: hi scene 8 says सोने के हो गए.
  - F7: mr scene 4 सोपवा, scene 5 त्या म्हणाल्या, scene 3 गंगेमुळे, scene 6 सांगण्यावरून.
  - F8: te scene 5 ends …తాళలేనంది ఆమె, and scene 9 is …దేవతలు కార్తికేయుడని పేరు పెట్టారు. The Ganga's honorific stays singular for the native review.
  - F9: A1 wording.
  - V3: `kumara_light` token is now "a divine child", without "short glowing hair", with the arms held a little away from the body.
  - V4: `krittika_stars` is bright white, and scene 9's starlight is pale warm white. `ganga_light` is a shared series token and was left unchanged.
  - V5: scene 6's river enters from the left edge just below the top third. New seed 13106.
  - V6: scene 8's child is drawn small, seated cross-legged. New seed 13108.
  - V8: `krittika_stars` no longer says "Krittika" in the visible prompt.
- **Trims to hold duration:**
  - en: scene 5 "Her streams…", scene 8 "…gold; there…", scene 11 drops "And".
  - hi: scene 9 drops और.
  - gu: scene 2 drops ને.
  - te: scene 2 తపిస్తుండగా.
  - The scene 9 silence is now 0.3 s (was 0.4 s).
- **Not applied:**
  - F10: metadata, which is the packager's.
  - V7: a G2 check on the gu/te card conjunct.
