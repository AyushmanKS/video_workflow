# Strategy: C0010 (scriptwriter)

**Decision:** continue in strict narrative order from 1.35.13. Pay off the Ep09 question in the first line, tell the whole of the sage's account in sarga 35 (1.35.13–24), and stop exactly where the sarga stops:
- the river of three paths has taken her *first* path to the world of the gods (teaser 1.35.23–24);
- the card reads "Next: Three Paths", which names the question that opens sarga 36 (1.36.3).

Sarga 36 is not narrated.

**Lint estimates** (all pass; only the advisory hook >2.2 s warning remains, as in Ep09): en 52.48 s, hi 52.96 s, gu 53.82 s, te 53.65 s and mr 54.08 s, after the story-review fixes. All are inside 35–55 s; gu, te and mr sit up to about 1 s above Ep09's 53 s flow ceiling because of the reviewer's fuller wording (mr F1, F8).

## Why this shape
- **The sarga is one telling.** It moves from two daughters, to two destinies (the elder given to the gods, the younger given to Rudra), to the sage's summary. Splitting it would leave an episode without a turn.
- **The turn is the father's gift (verse card 1.35.18).** It is emotionally real without adding motive: he gives his daughter by dharma, for the three worlds. It starts at about 22.6–24.8 s in every language.
- **Teaser on 1.35.23–24.** प्रथमं ("first") is the text's own cliffhanger: one path of three has been told, so the Ep09 question is only partly answered.

**Next card alternatives:** "Uma's Curse" (1.36.21–23) is verified and stronger, but it would spotlight the most sensitive part of sarga 36 before the owner decides how to handle it. "Three Paths" is accurate and consistent with the closing line. This is for the owner's choice at G1.

## Angle and hook
**Contradiction / teaser payoff:** the Ganga and Uma (Parvati to most viewers, Uma Devi in 1.35.22) were born sisters. Each hook is written natively short:

| Language | Hook | Spoken |
|---|---|---|
| en | "The Ganga and Goddess Uma were sisters." | 2.66 s |
| hi | "गंगा और उमा सगी बहनें थीं।" | 1.96 s |
| gu | "ગંગા અને ઉમા સગી બહેનો હતાં." | 2.24 s |
| te | "గంగ, ఉమ సొంత అక్కాచెల్లెళ్లు." (F7) | 2.36 s |
| mr | "गंगा आणि उमा सख्ख्या बहिणी होत्या." | 2.65 s |

- **Frame 0:** a river of light pours from the snowy peak, with Uma meditating on a ledge beside it. It reads muted as two sisters.

## Beats (11 scenes)
| Beat | Scenes | Content (locator) |
|---|---|---|
| H1/H2 | 1 | the Ganga and Uma were sisters (1.35.16, 22) |
| C | 2–3 | at Rama's asking the sage begins (1.35.12–13); Himavan's two matchless daughters (1.35.14) |
| E | 4–5 | Mena their mother, the Ganga the elder (1.35.15–16); all the gods ask for the elder (1.35.17) |
| T | 6 | verse card 1.35.18: by dharma Himavan gives her, for the three worlds (0.5 s silence before) |
| P1 | 7 | glad at heart, the gods carry the Ganga to heaven (1.35.19, 24) |
| E2 | 8–9 | Uma's stern vow and austerity (1.35.20); Himavan gives her to Rudra (1.35.21) |
| P | 10 | the sage names both daughters, closing the main loop at about 88–91 % (1.35.22) |
| N | 11 | the river of three paths went first to the sky, rising to the world of the gods (teaser 1.35.23–24) |

## Silences, loop and engagement
- **Silences:** 0.5 s after scene 5, 0.5 s after the verse card and 0.3 s after scene 10.
- **Loop type:** composition. Scene 11 reuses frame 0's framing, with the river now rising into the starry sky.
- **Engagement (A3):** the title card on scene 10 asks "Which sister was the elder?" (hi दोनों में बड़ी बहन कौन?, gu બેમાં મોટી બહેન કોણ?, te ఇద్దరిలో అక్క ఎవరు?, mr दोघींत थोरली बहीण कोण?). The answer, the Ganga, is in scene 4 (1.35.16). Suggested pinned comment: the same line.

## Engine v3 (chalk puppets)
- **Composition rules.** Every drawing has 1–3 large figures in side or three-quarter view, with gesturing arms held clear of the body, beard, scenery and other figures. Flames and orbs have open board around them. Props lie flat or stand planted (the staff on the sand, Rudra's trident planted in the rock).
- **Prompts.** Phrasing is positive only, the frame conventions are kept and seeds are 10001–10100.
- **Depiction tokens** (added to `profiles/characters/ramayana.json`): `himavan`, `mena`, `uma`, `uma_girl`, `rudra_symbol`, `ganga_light` and `devas_light`. The deities are symbolic: the gods are orbs of light, Rudra is a calm silhouette with crescent and trident, and the Ganga is a river of light. Uma is a modest ascetic.
- **Rig direction.** The per-scene puppet direction for `rig.json` is in each `script.md`.

## Risks and checks
- **mr lint rate:** it was calibrated from 1 render, so treat 52.8 s as approximate.
- **Payoff timing:** the main loop closes at the end of scene 10, about 88–91 % of runtime; te and mr are a hair past the 85–90 % guide. Scene 10 is already minimal.
- **Unreviewed languages:** gu, te and mr are `unreviewed-language`; there is no native reviewer yet.
- **Next episode:** sarga 36 needs a sensitivity plan (see `research/report.md`).

## Story-review fixes applied (content/C0010/review.md, 2026-11-18)
- **Must-fix:**
  - F1: mr scene 4 now has verbs (होती).
  - V1: scenes 1 and 11 show Uma large in the lower-right foreground, with the river of light behind her on the left. The shot changes from EWS to WS.
  - V2: scene 7 shows Himavan large in the lower-right foreground in three-quarter back view, his farewell arm against open board.
  - V3: scene 9 is staggered in depth: Himavan in the left foreground, Uma in the middle ground, Rudra on a higher rock. The fire is dropped.
- **Optional, applied:**
  - F2/F3: en scenes 4 and 3.
  - F4: mr scene 10.
  - F5: hi scenes 7 and 9.
  - F6: gu varies ને/અને/પછી and uses the honorific મોટાં in scene 5.
  - F7: te hook is "గంగ, ఉమ సొంత అక్కాచెల్లెళ్లు.".
  - F8: scene 11 says "went first to the sky" in every language.
  - F10: "Goddess Uma" is capitalised in both places.
  - F11: relabelled as the 55 s two-beat shape.
  - V4: scene 3's hanging arm is clear of the robe.
  - V5: in the `uma` token, the sari end is over both shoulders with the topknot visible.
- **New seeds:** every scene whose prompt changed, including through the `uma` token, has a new seed: 10200, 10202, 10206, 10207, 10208, 10209 and 10210.
- **F9 not adopted:** "The river Ganga had a sister." scored hookscore 30 against 33 for the current hook, and is spoken in 1.91 s, under the 2.5–2.8 s Kokoro-safe band. It is recorded in en/hooks.json.
