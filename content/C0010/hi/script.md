# गंगा और उमा, दो बहनें | रामायण भाग 10

- Language: hi (Hindi) · scenes: 11 · words: 139 · lint estimate **52.96 s** (basis letters; target 35–55 s, hard limit < 60 s; kept at or under about 53 s for flow, as in Ep09)
- Edition: vulgate (southern recension), sa.wikisource; verse numbers cross-checked on valmikiramayan.net (Internet Archive copy)
- Beat: the Ganga's origin as Vishvamitra tells it on the Ganga bank (1.35.13–24): Himavan and Mena's two daughters, the gods' request and Himavan's gift of the Ganga for the three worlds, the Ganga's rise to heaven, Uma's austerity and her marriage to Rudra. Opened by the payoff of the Ep09 question (1.35.12) and closed with the teaser 1.35.23–24.
- Engine: v3 (chalk puppets). Every `visual` is composed for Kathputli-style rigging: 1–3 figures, large, side or three-quarter view, limbs and props clear of the body and the scenery, open board around flames and lights, positive phrasing only, seeds 10xxx. Image prompts remain the creative director's to refine; these strings are the puppet-ready direction and are identical in every language (visual parity).
- Depiction: the Ganga is a river of light (token `ganga_light`), never a woman; the gods are orbs of light (`devas_light`); Rudra is a calm seated silhouette with crescent moon and planted trident (`rudra_symbol`); Uma is a modest young ascetic (`uma`, `uma_girl`); Himavan is a regal mountain king with snowy peaks behind him (`himavan`); Mena a queen in a sari with the end over her head (`mena`). New tokens added to `profiles/characters/ramayana.json`. Rama is seen from behind.
- Loop type: composition (scene 11 reuses frame 0's framing: Uma large in the lower-right foreground with the river of light behind her on the left; now the river rises into the starry sky) · Next card: scene 11 emphasis
- Silences: 0.5 s after scene 5 (before the Turn), 0.5 s after scene 6 (verse card, before the payoff), 0.3 s after scene 10 (before Next); 0.18 s between all other scenes
- Engagement line (A3): on-screen title of scene 10, "दोनों में बड़ी बहन कौन?" (answer in the text: the Ganga, scene 4, 1.35.16); same line suggested as the pinned comment
- Thumbnail: scene 1 image, headline "गंगा की बहन"

Hindi is written natively (Maya 2 Malini voice), not translated. The Ganga takes the honorific plural (थीं, पहुँचीं); the sage's closing words come after a soft lead-in (ऋषि बोले). सगी बहनें rests on 1.35.15, where Mena is the mother of both (तयोर्माता).

## Hook: selected

**गंगा और उमा सगी बहनें थीं।** (contradiction / teaser payoff, spoken 1.96 s, 29/30)

## Hooks (rubric /30: Curiosity, Emotion, Specificity, Speed, Resonance, Accuracy)

| # | Hook | Type | s | C | E | S | Sp | R | A | Total |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 ✔ | गंगा और उमा सगी बहनें थीं। | contradiction / teaser payoff | 1.96 | 5 | 4 | 5 | 5 | 5 | 5 | 29 |
| 2 | पर्वतराज ने अपनी बेटी देवताओं को सौंप दी। | request with a twist (stake) | 3.27 | 4 | 5 | 3 | 1 | 4 | 4 | 21 |
| 3 | गंगा स्वर्ग तक कैसे पहुँचीं? | question (teaser payoff) | 2.13 | 4 | 3 | 3 | 5 | 4 | 5 | 24 |
| 4 | गंगा, हिमालय की बड़ी बेटी थीं। | bold claim | 1.96 | 4 | 3 | 4 | 5 | 4 | 5 | 25 |
| 5 | उमा ने तप को ही अपना धन बना लिया। | forbidden or unknown detail | 2.62 | 3 | 3 | 3 | 5 | 4 | 5 | 23 |
| 6 | एक बहन नदी बनी, दूसरी रुद्र की अर्धांगिनी। | contrast | 3.43 | 5 | 4 | 5 | 1 | 5 | 3 | 23 |

## Narration

1. गंगा और उमा सगी बहनें थीं।
2. राम के पूछने पर, विश्वामित्र गंगा के जन्म की कथा सुनाने लगे।
3. पर्वतराज हिमवान की दो बेटियाँ थीं, जिनके रूप की धरती पर कोई बराबरी न थी।
4. उनकी माँ थीं मेरु की बेटी मेना, और दोनों में बड़ी थीं गंगा, छोटी उमा।
5. फिर सारे देवता, पर्वतराज से बड़ी बेटी गंगा को माँगने आए।
6. और धर्म निभाते हुए हिमवान ने, तीनों लोकों के हित में, अपनी बेटी सौंप दी।
7. तब देवता प्रसन्न मन से गंगा को स्वर्ग ले गए।
8. छोटी बेटी उमा ने कठोर व्रत लिया, और तप को ही अपना धन बना लिया।
9. और हिमवान ने उमा का ब्याह अनुपम रुद्र से कर दिया।
10. ऋषि बोले, यही हैं पर्वतराज की दो बेटियाँ, नदियों में श्रेष्ठ गंगा, और उमा देवी।
11. यूँ तीन पथों वाली गंगा, पहले आकाश की ओर चलीं, और देवलोक जा पहुँचीं।

## Read in one breath (storyteller check)

Read aloud start to finish as one telling before lint. Every scene is one complete sentence that ends at a natural breath, no sentence crosses a scene break, and each scene grows out of the one before (बहनें थीं → राम के पूछने पर → दो बेटियाँ थीं → उनकी माँ → फिर सारे देवता → और धर्म निभाते हुए → देवता प्रसन्न मन से → छोटी बेटी उमा → और हिमवान ने → ऋषि बोले → यूँ). Speech is reported or given a soft lead-in, never a bare quote after a colon or dash, and no scene ends on a bare question.

> गंगा और उमा सगी बहनें थीं। राम के पूछने पर, विश्वामित्र गंगा के जन्म की कथा सुनाने लगे। पर्वतराज हिमवान की दो बेटियाँ थीं, जिनके रूप की धरती पर कोई बराबरी न थी। उनकी माँ थीं मेरु की बेटी मेना, और दोनों में बड़ी थीं गंगा, छोटी उमा। फिर सारे देवता, पर्वतराज से बड़ी बेटी गंगा को माँगने आए। और धर्म निभाते हुए हिमवान ने, तीनों लोकों के हित में, अपनी बेटी सौंप दी। तब देवता प्रसन्न मन से गंगा को स्वर्ग ले गए। छोटी बेटी उमा ने कठोर व्रत लिया, और तप को ही अपना धन बना लिया। और हिमवान ने उमा का ब्याह अनुपम रुद्र से कर दिया। ऋषि बोले, यही हैं पर्वतराज की दो बेटियाँ, नदियों में श्रेष्ठ गंगा, और उमा देवी। यूँ तीन पथों वाली गंगा, पहले आकाश की ओर चलीं, और देवलोक जा पहुँचीं।

## Scene table

| # | Beat | Est. s | Pause | Title card | Locator (vulgate) |
|---|---|---|---|---|---|
| 1 | H1/H2 hook (pays off the Ep09 question) | 1.96 | 0.18 |  | VR 1.35.16, 1.35.22 |
| 2 | C | 4.58 | 0.18 | गंगा के तट पर | VR 1.35.12–13 |
| 3 | C | 5.72 | 0.18 | हिमवान | VR 1.35.14 |
| 4 | E | 4.25 | 0.18 |  | VR 1.35.15–16 |
| 5 | E | 4.25 | 0.5 |  | VR 1.35.17 |
| 6 | T (verse card) | 5.07 | 0.5 |  | VR 1.35.18 (card 1.35.18) |
| 7 | P1 (the Ganga reaches heaven) | 3.76 | 0.18 |  | VR 1.35.19 |
| 8 | E2 | 4.91 | 0.18 | उमा | VR 1.35.20 |
| 9 | E2 | 4.09 | 0.18 |  | VR 1.35.21 |
| 10 | P (main loop closes) | 5.56 | 0.3 | दोनों में बड़ी बहन कौन? | VR 1.35.22 |
| 11 | N (teaser 1.35.23–24) | 4.91 | 0.18 | आगे: तीन पथ | VR 1.35.23–24 (next 1.36.1–3) |

## Puppet direction (engine v3, for the rig)

| # | Figures / elements | Intended motion (small, logical, around the drawn key pose) | Shot | Seed |
|---|---|---|---|---|
| 1 | Uma (seated, large, lower-right foreground, three-quarter); river of light behind on the left | Uma breathes in the torso and lifts her head slightly toward the river; the waterfall shimmers; open board between her and the river so nothing tears | WS | 10200 |
| 2 | Vishvamitra, Rama (seated) | the sage's raised teaching hand nods at the elbow and his head turns a little toward Rama; Rama's head tilts toward him; seated legs stay put | WS | 10001 |
| 3 | Himavan (standing, knees up) | the outstretched arm sweeps a few degrees toward the peaks (elbow-led), head lifts; the right arm hangs free of the robe (open board) and only sways slightly; ore sparkles | MS | 10202 |
| 4 | Mena, the girl Uma (standing); spring of light | Mena's low open hand sinks a little toward the spring and her head bows tenderly; the girl's raised hand lifts toward her mother | WS | 10003 |
| 5 | Himavan; five orbs of light | the orbs drift down one by one (each a separate element with open board); the king's welcoming hand rises at the elbow and he nods | WS | 10004 |
| 6 | verse card | chalk card, no puppet | card |  |
| 7 | Himavan (large, lower-right foreground, three-quarter back view); river of light; orbs | the king's raised farewell hand waves at the elbow against open board and his head tilts up to follow the river; the orbs lead the river upward; godrays | EWS | 10206 |
| 8 | Uma (seated, side view); flame | breathing in the torso only, a slow head bow; the flame flickers in brightness (halo uncut); snowflakes | MS | 10207 |
| 9 | Himavan (large, left foreground), Uma (centre middle ground, standing), Rudra silhouette (seated, higher rock, right) | Himavan's presenting hand extends a little at the elbow; Uma bows from the waist with joined palms held away from the chest; Rudra stays still (calm), only the crescent glints; the trident never moves; no fire in this drawing | WS | 10208 |
| 10 | Himavan; river of light; Uma (seated) | Himavan's open palms turn outward slightly and his head turns from river to daughter; Uma breathes | WS | 10209 |
| 11 | Uma (seated, large, lower-right foreground, as frame 0); river of light rising behind on the left | Uma's head lifts toward the rising river; the river shimmers upward; the golden glow pulses | WS | 10210 |

## Verse card (scene 6)

> ददौ धर्मेण हिमवांस् / तनयां लोकपावनीम्। / स्वच्छन्दपथगां गङ्गां / त्रैलोक्यहितकाम्यया॥
> वाल्मीकि रामायण 1.35.18 (दाक्षिणात्य पाठ)

Meaning (1.35.18): "Himavan, by dharma, gave his daughter, the purifier of the worlds, the Ganga who flows where she wills, wishing the good of the three worlds." The narration gives the meaning while the card is on screen; the verse is not recited. The first line ends हिमवांस् and the second begins तनयां, a pāda split that keeps the sandhi हिमवांस्तनयां letter for letter. Script: Devanagari.

## Teaser (scene 11)

VR 1.35.23–24 (vulgate): एतत् ते सर्वमाख्यातं यथा त्रिपथगामिनी। खं गता प्रथमं तात गतिं गतिमतां वर॥ सैषा सुरनदी रम्या शैलेन्द्रतनया तदा। सुरलोकं समारूढा विपापा जलवाहिनी॥ "I have told you all of how the river of three paths first went to the sky. So this lovely river of the gods, the mountain lord's daughter, sinless, flowing as water, rose to the world of the gods." The word प्रथमं (first) carries the teaser: one path of three is told. Next card: "आगे: तीन पथ" (Rama and Lakshmana ask by what cause she floods three paths, 1.36.1–3; not narrated here).

## Sources (edition: vulgate; sa.wikisource text, numbers cross-checked on valmikiramayan.net)

- VR 1.35.12 (vulgate (sa.wikisource)): Rama: I wish to hear of the Ganga, the river of three paths; how did she pervade the three worlds and reach the lord of rivers? (Ep09 teaser, paid off here)
- VR 1.35.13 (vulgate (sa.wikisource)): urged by Rama's words, the great sage Vishvamitra began to tell the Ganga's birth and growth
- VR 1.35.14 (vulgate (sa.wikisource)): Himavan, lord of mountains (शैलेन्द्र), great mine of ores (धातूनामाकरो महान्), had two daughters unequalled in beauty on earth
- VR 1.35.15 (vulgate (sa.wikisource)): their mother, Meru's daughter, slender-waisted and lovely, Mena by name, Himavan's dear wife
- VR 1.35.16 (vulgate (sa.wikisource)): from her this Ganga was born, Himavan's elder daughter (ज्येष्ठा); Uma by name was his second daughter
- VR 1.35.17 (vulgate (sa.wikisource)): then all the gods, wishing to accomplish the gods' work (देवकार्यचिकीर्षया), asked the mountain lord for his elder daughter, the Ganga, river of three paths
- VR 1.35.18 (vulgate (sa.wikisource)): Himavan, by dharma (धर्मेण), gave his daughter, purifier of the worlds, the Ganga who flows where she wills, wishing the good of the three worlds (verse card)
- VR 1.35.19 (vulgate (sa.wikisource)): receiving her for the sake of the three worlds, the gods, wishers of the worlds' good, took the Ganga and went, their purpose fulfilled
- VR 1.35.20 (vulgate (sa.wikisource)): the other daughter of the mountain, a maiden whose wealth was austerity (तपोधना), took up a stern vow and performed tapas
- VR 1.35.21 (vulgate (sa.wikisource)): the best of mountains gave his daughter Uma, endowed with fierce austerity and honoured by the worlds, to Rudra the peerless (रुद्रायाप्रतिरूपाय)
- VR 1.35.22 (vulgate (sa.wikisource)): these are the mountain king's two daughters, honoured by the worlds: the Ganga, best of rivers, and Uma Devi
- VR 1.35.23 (vulgate (sa.wikisource)): I have told you all of how the river of three paths first (प्रथमं) went to the sky (teaser verse)
- VR 1.35.24 (vulgate (sa.wikisource)): so this lovely river of the gods, the mountain lord's daughter, sinless, flowing as water, rose to the world of the gods (teaser verse)
- VR 1.36.1–3 (vulgate (sa.wikisource)): Rama and Lakshmana ask the sage to tell the elder daughter's story in full: by what cause does she flood three paths? (next episode, not narrated)
- https://sa.wikisource.org/wiki/रामायणम्/बालकाण्डम्/सर्गः_३५ (accessed 2026-11-18)
- https://www.valmikiramayan.net/utf8/baala/sarga35/balasans35.htm (live site returned HTTP 509 on 2026-11-18; read via the Internet Archive copy, accessed 2026-11-18)

## Accuracy notes

- Every narrated fact maps to a verse in `research/report.md`. No dialogue is invented: the telling is the sage's own (1.35.13–24), and the one attributed line (scene 10, 1.35.22) is reported after a soft lead-in. `quote_src` is set on scenes 2, 6, 10 and 11.
- 'Sisters' rests on 1.35.15–16 (Mena is the mother of both, तयोर्माता; the Ganga is the elder, ज्येष्ठा, Uma the second, द्वितीया) and 1.35.22 (the mountain king's two daughters, the Ganga and उमादेवी). 'Younger' renders द्वितीया.
- 'Unmatched on earth' renders रूपेणाप्रतिमं भुवि (1.35.14). Himavan as 'great mine of ores' (धातूनामाकरो महान्) is not narrated, for length; scene 3's visual shows glittering ore in the rocks.
- 'Then all the gods… asked for his elder daughter' renders सुराः सर्वे… शैलेन्द्रं वरयामासुः (1.35.17). Their purpose, देवकार्यचिकीर्षया (to accomplish the gods' work), is not narrated for length; the purpose that is narrated, 'for the good of the three worlds', is the verse card's own (त्रैलोक्यहितकाम्यया, 1.35.18).
- 'True to dharma' renders धर्मेण (1.35.18). The scripts add no feeling for Himavan that the text lacks: no grief, no reluctance.
- 'Glad at heart, the gods carried the Ganga up to heaven' condenses 1.35.19 (गङ्गामादाय तेऽगच्छन् कृतार्थेनान्तरात्मना, 'they took the Ganga and went, their purpose fulfilled within') with the destination from 1.35.23–24 (खं गता; सुरलोकं समारूढा).
- 'Took a stern vow' renders उग्रं सुव्रतमास्थाय (sa.wikisource; valmikiramayan.net reads उग्रं सा व्रतमास्थाय, same sense). 'Made austerity her wealth' renders तपोधना (1.35.20).
- 'Gave her in marriage to Rudra, the peerless one' renders ददौ… रुद्रायाप्रतिरूपाय उमाम् (1.35.21). Giving a daughter (ददौ सुताम्) is the marriage idiom, and valmikiramayan.net glosses it 'gave in marriage'.
- 'The river of three paths' renders त्रिपथगा / त्रिपथगामिनी (1.35.17, 1.35.23). 'Went first to the sky' renders प्रथमं खं गता (1.35.23), as the reviewer asked (F8). The scripts do not name the other two paths: the text does not list them here, and valmikiramayan.net's commentary gives competing explanations, which are not used.
- No later tradition is used. Uma is never called Parvati in narration, and Sati's rebirth, Kama, Bhagiratha and the Ganga in Rudra's locks are out of scope (Puranic or later sargas). Sarga 36 is not narrated.
- hi gives Mena as मेरु की बेटी (1.35.15). 'उमा देवी' renders उमादेवी (1.35.22).
- The CE and Goldman were not checked, so there are no `[CE]` tags.
- Estimated seconds: 52.96 (lint, scene seconds [1.96, 4.58, 5.72, 4.25, 4.25, 5.07, 3.76, 4.91, 4.09, 5.56, 4.91], pauses 2.74 s, lead/tail 1.15 s).

## Applied learnings

Source: `data/reports/latest_insights.json` (generated 2026-11-18T11:17:53+0530). Approved rules (storytelling skill, O1/O5, lint) win; these anecdotes only choose among options the rules allow. `conflicts` ignored.

- **A1** (anecdote, n=12): Prefer the 35 s beat shape (turn T at 18–25 s) unless the story needs 45/55 s, and state the stakes by H2 — viewers currently leave around 12 s; avg watch 7–25 s on 75–111 s videos (instagram 24h) (anecdote, n=12; F1)
  - Applied. The stakes and the wonder are in the first sentence (the Ganga and Uma were sisters, paying off the Ep09 question about the Ganga), and the turn, the verse card where Himavan gives his daughter away for the three worlds, starts at about 22.6 s, inside the 18–25 s window. The 35 s shape is not used: the sarga needs both daughters, the gods' request, the gift, Uma's austerity and her marriage, so the 55 s two-beat shape is used, at about 52.96 s for flow.
- **A2** (anecdote, n=1): Keep the hook ≤3.0 s with the stakes in the first sentence and frame 0 ≥70% drawn; in en, gu, hi write the first line natively short, not translated — C0002-gu avg watch 7.1 s of 104 s (F2), C0003-hi avg watch 7.2 s of 99 s (F4), C0003-en avg watch 7.2 s of 90 s (F3) (instagram 24h) (anecdote, n=1; F2)
  - Applied. The hook is 1.96 s, under the 3.0 s limit, with the stake in the first sentence, written natively short in each language (gu: ગંગા અને ઉમા સગી બહેનો હતાં.). The en hook is 2.66 s, inside the 2.5–2.8 s Kokoro-safe band. Frame 0 is the river of light pouring from the peak with Uma in meditation beside it, which the engine draws at least 70% by frame 0 (O5).
- **A3** (anecdote, n=12): Use the ≤6-word engagement line as a share prompt with a real answer in the text and compare shares/reach next time — shares/reach median 0.4% vs saves/reach 0.5% (instagram 24h) (anecdote, n=12; F6)
  - Applied on screen. Scene 10 carries the share prompt 'दोनों में बड़ी बहन कौन?' (6 words or fewer) as its title card. It is answered in the text in scene 4 (1.35.16): the Ganga was the elder. It is not spoken, because no language has seconds to spare. The same line is suggested as the pinned comment so shares/reach can be compared.

**applied_learnings:** A1 (applied: stakes in the first sentence, turn at about 22.6 s; the 55 s two-beat shape, at about 53 s for flow), A2 (applied: hook 1.96 s, written natively short), A3 (applied on screen, not spoken).
