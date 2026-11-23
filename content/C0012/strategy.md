# Strategy: C0012 (scriptwriter)

**Decision:** continue in strict narrative order. Pay off the Ep10 card ("Three Paths") in scene 2 with Rama's question (1.36.1–4) and the sage's choice to begin with Uma. Tell all of sarga 36 in eleven scenes, and stop where the sarga stops: the sage's own turn to the Ganga (teaser 1.36.27).
- **Card:** "Next: The Gods' Commander" (te తర్వాత: దేవతల సేనాపతి, review F7; hi आगे: देवों का सेनापति; gu આગળ: દેવોના સેનાપતિ; mr पुढे: देवांचा सेनापती). It names the question that opens sarga 37 (1.37.1: the gods, led by Agni, go to Brahma seeking a commander).
- **Not narrated:** sarga 37 and Kartikeya's birth (1.36.19).

**Lint estimates** (all pass; only the advisory hook >2.2 s warning remains, as in Ep10):

| Lang | Lint | Hook |
|---|---|---|
| en | 54.31 s | 2.74 s |
| hi | 51.49 s | 2.45 s |
| gu | 52.10 s | 2.58 s |
| te | 53.32 s | 2.70 s |
| mr | 54.41 s | 2.65 s |

These are the figures after the story-review fixes. Before the fixes they were en 53.39, hi 51.00, gu 51.07, te 52.81 and mr 54.25 s.

- hi and gu are about 1.5–1.7 s below Ep10's estimates (52.96 / 53.82 s), which rendered at 55.9 / 55.83 s. This allows for their render overshoot.
- mr renders shorter than its estimate (Ep10: 54.08 → 52.4 s). en tracks its estimate within about 1.4 s.

## Why this shape
- **One telling.** Sarga 36 moves from fear (the gods), to the plea and Rudra's consent, to the wonder (the Earth, Agni and Vayu, the white mountain and the reed forest), to the cost (Uma's curses), to calm (tapas).
- **Turn: the gods' plea (verse card 1.36.11).** It echoes Ep10's card (त्रैलोक्यहितकाम्यया, 1.35.18) and carries no sensitive wording. It starts at en 17.9 s, hi 16.5, gu 17.1, te 18.3 and mr 18.3 s. This is early for the 55 s shape's 24–33 s T1 window, by design: it lands near the 18–25 s window from A1, before the 13 s drop-off (review F12).
- **Main loop:** why did the gods fear a child, and what became of it? It closes at the end of scene 10 (no son for Uma, none for the Earth), at about 88% of runtime in every language.
- **Teaser 1.36.27.** The sage himself says that Uma's account is done and that the Ganga's comes next. The Ep10 question (three paths) is thereby kept open, honestly.

**Next card alternatives (owner's choice at G1):**
- "Born of Fire" (अग्निसम्भवः, 1.36.19).
- "Kartikeya" (names the payoff outright).

"The Gods' Commander" was chosen because the gods who were just cursed to have no sons now need a leader, which links the two episodes without narrating sarga 37.

## Angle and hook
**Contradiction / forbidden detail:** the all-powerful gods were afraid of a child not yet born (1.36.7–8). It leads on the fear, not on the union or the curse.

| Language | Hook | Spoken |
|---|---|---|
| en | "The gods once feared a child not yet born." | 2.74 s |
| hi | "देवता अजन्मे बालक से डरते थे।" | 2.45 s |
| gu | "દેવો અજન્મા બાળકથી ડરતા હતા." | 2.58 s |
| te | "పుట్టని బిడ్డకు దేవతలు జడిశారు." | 2.70 s |
| mr | "देव एका अजन्म्या बाळाला घाबरले." | 2.65 s |

- **Frame 0:** Rudra's calm silhouette on a night summit, with the orbs of the gods hovering, dimmed, at a distance. Muted, it reads as "the gods before a great power".
- **Rejected hook:** "Goddess Uma once cursed all the gods" (27/30). It was rejected because it would use the curse as bait.

## Beats (11 scenes)
| Beat | Scene | Content (locator) |
|---|---|---|
| H1/H2 | 1 | the gods feared a child not yet born (1.36.7–8) |
| C | 2 | Rama asks of the three paths; the sage begins with Uma (1.36.1–5, 27) |
| C | 3 | Rudra and Uma wed, and dwell as one for a hundred years of the gods (1.36.5–6) |
| E1 | 4 | no son; the gods wonder who could withstand the child to come (1.36.7–8); 0.5 s silence |
| T | 5 | verse card 1.36.11: hold your power within, for the three worlds (1.36.9–11); 0.5 s silence |
| E2 | 6 | Rudra agrees but asks who will bear what has stirred (1.36.12–14) |
| E2 | 7 | the gods choose the Earth; the power spreads over hills and woods (1.36.15–16) |
| P1 | 8 | Agni and the Wind enter it: the white mountain and the reed forest (1.36.17–18) |
| P | 9 | denied the son she longed for (निवारिता), Uma curses the gods: their wives will bear no child (1.36.20–22) |
| P | 10 | and the Earth: never to know a son's joy (1.36.23–24); main loop closes; 0.3 s silence |
| N | 11 | Rudra goes with Uma to Himavan for tapas; "now hear the Ganga's tale" (1.36.25–27) |

## Silences, loop and engagement
- **Silences:** 0.5 s after scene 4, 0.5 s after the verse card and 0.3 s after scene 10.
- **Loop type:** composition. Scene 11 reuses frame 0's framing: the orbs on the left are replaced by Uma seated in meditation, far from Rudra.
- **Engagement (A4, review F3):** the title card on scene 10 reads "What did Agni and Wind create?". The answer, the white mountain and the reed forest, is in scene 8 (1.36.18). It replaces "Who first held Rudra's power?", which could invite anatomical replies.
  - hi: अग्नि और वायु ने क्या रचा?
  - gu: અગ્નિ અને વાયુએ શું સર્જ્યું?
  - te: అగ్ని, వాయువు ఏమి సృష్టించారు?
  - mr: अग्नी आणि वायूने काय घडवले?
  - Suggested pinned comment: the same line.

## Sensitivity plan (for the owner at G1)
Sarga 36 holds the most delicate material in the Bala Kanda so far. The plan below governs narration, visuals and the creative director's prompts.

1. **The union (1.36.5–6).**
   - **Narration:** only "Rudra and Uma were wed, and dwelt as one for a hundred years of the gods" (hi दिव्य सौ बरस वे साथ रहे; gu દિવ્ય સો વરસ સાથે રહ્યાં; te దివ్యమైన వంద ఏళ్లు కలిసి ఉన్నారు; mr दिव्य शंभर वर्षे ते सोबत राहिले).
   - **Not rendered:** the verb of 1.36.5b.
   - **Visual (scene 3):** two soft round glows, silver and golden, resting well apart on Himavan's summit, with an arc of moon phases marking the years. There are no figures in this scene.
   - **Scene 11:** the two are seated far apart in meditation, never touching.
2. **The gods' fear and the तेजः (1.36.7–18).**
   - **Narration:** always "his power" / तेज / తేజస్సు ("power" doubles as "energy" in the bible text).
   - **Never used:** the commentary's anatomical gloss.
   - **Visuals:** a soft blaze of white light gathering above the peak (scene 6); a column of white light descending gently onto a landscape and settling outward over hills and forests as a haze (scene 7, review V3); a glowing white mountain with a golden reed forest, a flame (Agni) and wind ribbons (Vayu) (scene 8). Nothing anatomical is drawn.
3. **Uma's curse (1.36.20–24).**
   - **Narration:** told as the text gives it, with dignity. She was stopped when she longed for a son (निवारिता… पुत्रकाम्यया), so she curses as one denied that son, "in anger" (समन्युः). This keeps her a wronged mother-to-be, not a capricious goddess (review F1).
   - **Not drawn:** her reddened eyes (क्रोधसंरक्तलोचना).
   - **Visual (scene 9):** Uma stands grave and sorrowful with lowered eyes and one open palm extended and turned a little downward in a gesture of pronouncement, not blessing (review V5), the orbs dimming at a distance. There is no sensational title card.
   - **The Earth's curse:** reduced to "never to know a son's joy". बहुभार्या ("wife of many") and the insult सुदुर्मेधे are left out.
4. **Rudra.**
   - **Depiction:** always the `rudra_symbol` silhouette, a calm, featureless dark-grey seated shadow with a crescent moon in the topknot, hands on the knees and the trident planted upright beside him.
   - **Never shown:** a face, a third eye, blue skin or multiple arms.
   - **Motion:** he never gestures. The only motion is a slight breath, one ≤3° nod (scene 6) and a crescent glint.
   - **Token update:** after Ep10 G2 fix 1 (a featured face had to be edited out), the token now also asks for "one flat solid dark grey shadow shape like a shadow puppet, the head a smooth rounded shadow".
5. **Uma.**
   - **Depiction:** the `uma` token, a modest young ascetic in an ochre sari with the end over both shoulders and a high topknot visible, never glamorous.
   - **Token update:** after Ep10 G2 fix 5 (drift to a low bun, earrings, bangles, bindi and jasmine), the token now states "ears, wrists and forehead plain and unadorned, the hair in one high topknot".
6. **The gods and the Earth.**
   - **The gods:** orbs of light (`devas_light`); Brahma is a lotus of light (`brahma_light`); Agni is a flame (`agni_light`, new) and Vayu ribbons of wind (`vayu_wind`, new).
   - **The Earth:** a broad landscape (`prithvi_land`, new), never a woman or goddess. The visible prompts say only "a broad landscape seen from high above" (review V4). In scene 10 her "many forms" are shown as varied terrain.
7. **Scope.**
   - **Left out:** Kartikeya's birth (1.36.19), which belongs to the next episode.
   - **No Puranic additions:** Kama, Sati, Tarakasura.
   - **Name:** Uma is not called Parvati.

## Engine v3 (chalk puppets)
- **Composition.** Each drawing has 1–2 large figures in side or three-quarter view, with arms and props clear of the body and the scenery.
  - Heads, topknots and crescents are drawn against open board, below the peaks.
  - Flames and orbs have open board around them, and no hand is near another figure.
  - Scene 2 has the sage plus the two princes, seen from behind and spaced apart.
- **Accent.** Scenes with Rudra, Uma on Himavan or the gods use `divine`. Scene 2 also uses `divine` (Ep10 G2 fix 4: the forest accent turned the river green). The two landscape scenes use `default`.
- **Seeds and phrasing.** Seeds are 12001–12011; phrasing is positive only, and the frame conventions are kept.
- **Tokens.** New tokens (full bible text in `profiles/characters/ramayana.json`): `agni_light`, `vayu_wind`, `prithvi_land` and `shvetaparvata_sharavana`. `uma` and `rudra_symbol` were tightened, as described in the plan above.
- **Rig notes.** The per-scene puppet direction is in each `script.md`.

## Applied learnings (data/reports/latest_insights.json, 2026-11-23T16:19:55+0530)
- **A1** (anecdote, n=25): applied. The stake is in the first line. The episode uses the 55 s two-beat shape, and the card comes early by design, at about 16–18 s (review F12).
- **A2** (anecdote, n=1): applied. Hooks are 2.45–2.74 s, natively short; en sits inside the Kokoro band.
- **A3** (anecdote, n=25): partly applied. The density needs the 55 s shape, so the episode was cut to the owner's 50–53 s target instead of the lower half.
- **A4** (anecdote, n=25): applied on screen. The share prompt on scene 10 is "What did Agni and Wind create?", answered in scene 8.

## Risks and checks
- **Hindi speech rate:** lines keep at most two commas.
- **mr rate:** it was calibrated from 1 render.
- **Unreviewed languages:** gu, te and mr are `unreviewed-language`.
- **Rudra's face (image risk):** check the scene 1, 6 and 11 stills before rigging.
- **Scene 2:** three figures. If rigging struggles, Lakshmana can stay fully still. The bows and quiver lie flat on the sand (review V2).
- **Native review still open:** te F6 (whether పుట్టని reads clearly) and F9 (Uma's honorific). Both need a native Telugu speaker.

## Story-review fixes applied (content/C0012/review.md, 2026-11-23)
- **Must-fix applied:** F1, F2, F3, V1, V2 and V3.
- **Optional applied:** F4, F5, F7, F8 (mr stays at 54.41 s), F10, F11, F12, V4 and V5.
- **Skipped:** F6 and F9 (they need a native speaker).
- **New seeds:** 12102, 12106, 12107, 12109 and 12110 for scenes 2, 6, 7, 9 and 10.
- **N1 (series-planner):** sarga 37 needs an extended sensitivity plan before Ep12 is written, and Ep12 should open on 1.37.1.
