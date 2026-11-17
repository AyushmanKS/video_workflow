# Rama's Crown Was Ready | Ramayana · Ayodhya Kanda Ep 1 (AK01)

- Status: **DRAFT for review**, not linted, not in the pipeline (no `pipeline new`, no manifest). Lint and the reviewer's Story QA come before G1.
- Language: en (English), voice Kokoro `af_heart`. 11 shots · **112 words** · hand estimate **about 45 s** (en 2.81 w/s speech + 1.15 s lead and tail + pauses). `python -m pipeline lint` is the arbiter.
- Style: Ayodhya Kanda "Pahari Gold" animated look (`docs/KANDA_VISUAL_IDENTITIES.md`), characters from `profiles/characters/ayodhya_kanda.json`. Rama and Sita are shown with faces (owner decision 2026-11-17).
- Edition: Valmiki Ramayana, vulgate (southern recension), numbered as on valmikiramayan.net (accessed 2026-11-17). Critical Edition numbers not checked; no `[CE]` tags.
- Beat: the aged king's wish and the joyful assembly (2.1–2.2), the Pushya day (2.3), the premonition and "tomorrow" (2.4), the fast and the decorated city (2.5–2.6), Manthara on the terrace (2.7.1–2).
- Loop type: **composition.** Frame 0 is Dasharatha at a high window looking down over the city; shot 11 is Manthara on a high terrace looking down over the same city, mirrored.
- Silences: 0.5 s after shot 6 (before the Turn), 0.4 s after shot 8 (before the payoff), 0.3 s after shot 10 (before Next).
- Engagement line (A4, share prompt, 5 words): on-screen title of shot 10, "Who was away that day?" Answer in the text: Bharata (shot 8; 2.1.1–2, 2.4.25).
- Next card: "Next: Manthara's Whisper" (Manthara goes down to Kaikeyi, 2.7.12–13).

## Why this moment
AK01 opens a new Kanda and a new look, so it needs one complete, visually rich arc that viewers can follow without Bala Kanda. Sargas 2.1–2.7.2 give it: a joyful decision, a city celebrating, and a quiet fear inside the joy, which is all in the text (2.4.17–25), then the first glimpse of the person who will turn it. It ends before any word from Manthara, so nothing about Kaikeyi is shown or implied before the text gets there (in 2.7.31–35 Kaikeyi first rejoices).

## Hook: selected

**Rama's crown was ready. His father was afraid.** (contrast, 8 words, about 2.8 s; 28/30)

| # | Hook | Type | C | E | S | Sp | R | A | Total |
|---|---|---|---|---|---|---|---|---|---|
| 1 ✔ | Rama's crown was ready. His father was afraid. | contrast | 5 | 4 | 4 | 5 | 5 | 5 | 28 |
| 2 | Crown him before my mind changes, said the king. | forbidden detail (2.4.20) | 5 | 4 | 4 | 3 | 4 | 3 | 23 (reads as doubt of Rama; risky framing) |
| 3 | Why did the king rush Rama's coronation? | question | 4 | 3 | 3 | 5 | 4 | 5 | 24 |
| 4 | One night before his coronation, the omens turned. | in medias res | 4 | 4 | 3 | 4 | 3 | 3 | 21 (timeline of the omens is not "one night") |
| 5 | Ayodhya roared like peacocks greeting the rain. | sensory | 3 | 4 | 4 | 4 | 4 | 5 | 24 |
| 6 | The whole city decorated. One woman watched from above. | contrast | 4 | 3 | 3 | 2 | 3 | 5 | 20 |

Rubric: Curiosity, Emotion, Specificity, Speed, Resonance, Accuracy (storytelling skill). The hook's fear is in the text: dreadful dreams, meteors and hostile planets, and a fear that minds change (2.4.17–20, 2.4.24).

## Narration

1. Rama's crown was ready. His father was afraid.
2. Old King Dasharatha longed to rest from ruling Ayodhya.
3. So before kings and citizens, he proposed Rama as crown prince.
4. The hall roared, like peacocks greeting a rain cloud.
5. Truthful, gentle, dark as a blue lotus, the people said.
6. The king embraced Rama and named the star: Pushya.
7. Then he called Rama back. He had seen dreadful dreams.
8. Be crowned tomorrow, he urged, while Bharata is still away.
9. That night, Rama and Sita kept the sacred fast. Ayodhya rose to decorate.
10. Banners on rooftops, flowers on the royal road, lamps for the night.
11. And from a palace rooftop, Kaikeyi's maid Manthara watched it all.

TTS respellings (the `tts` field; `narration` keeps the correct spelling for captions): Raama, Dasharatha → "Dusha-ratha", Pushya → "Push-ya", Bharata → "Bha-ruh-ta", Seetaa, Kaikeyi → "Kai-kay-ee", Manthara → "Mun-tha-raa". Check by ear on the first take.

### Read in one breath
> Rama's crown was ready. His father was afraid. Old King Dasharatha longed to rest from ruling Ayodhya. So before kings and citizens, he proposed Rama as crown prince. The hall roared, like peacocks greeting a rain cloud. Truthful, gentle, dark as a blue lotus, the people said. The king embraced Rama and named the star: Pushya. Then he called Rama back. He had seen dreadful dreams. Be crowned tomorrow, he urged, while Bharata is still away. That night, Rama and Sita kept the sacred fast. Ayodhya rose to decorate. Banners on rooftops, flowers on the royal road, lamps for the night. And from a palace rooftop, Kaikeyi's maid Manthara watched it all.

Shots 5 and 8 are reported speech with a soft tag ("the people said", "he urged"), with no quotation marks, so no `quote_src` is needed. They paraphrase 2.2.29–53 and 2.4.22–25.

## Shot list

Timings are hand estimates for en (2.81 w/s, 0.18 s default gap). Every shot is designed for image-to-video from one keyframe: one clear action, at most 2 characters in close or medium shots, crowds distant. "Hero" marks the 3–4 shots recommended for full image-to-video under the hybrid plan; the others can be 2.5D (parallax plus procedural motion).

| # | Beat | Time (s) | Shot · angle | Camera move | What MOVES | Characters | Caption / title card | Music · SFX |
|---|---|---|---|---|---|---|---|---|
| 1 **Hero** | H1/H2 | 0.0–3.0 | MCU, three-quarter back, high window | slow push-in | Dasharatha's eyes lift to the sky and his brow tightens; a pale meteor streaks across the daytime sky; banners far below stir | {dasharatha} | **Ayodhya Kanda** (title card, Chalkduster gold) | impact + low drum at 0.0, single bell; tanpura starts with the hit; `dasharatha` motif after the hook line |
| 2 | C | 3.2–6.4 | WS, eye level, throne hall | slow tilt down from the white parasol to the king | the parasol fringe flutters; two attendants' white chamara fans sway in the background; the king slowly lowers his head | {dasharatha} (+2 distant attendants) | — | tanpura; soft reed phrase (`ayodhya`, quiet) |
| 3 | C | 6.6–10.5 | WS, low angle, assembly hall | slow pull-back revealing the hall | the king rises and extends an open palm; seated kings remain still in distant rows | {dasharatha} + {citizens} (distant) | "Crown prince: Rama" | reed phrase continues; murmur bed fades in |
| 4 **Hero** | E | 10.7–13.9 | Insert, MS, carved palace parapet | static, slight push | two peacocks lift their heads and spread their trains; a dark rain cloud rolls in; first raindrops; marigold petals tossed up from below | none (visual simile) | — | crowd roar swell (new `crowd` or re-tuned `army` bed) + distant thunder (`rumble`, low) |
| 5 **Hero** | E | 14.1–17.7 | MCU, eye level, lotus courtyard | slow push-in | Rama turns his head towards the camera and lowers his eyes modestly; blue lotuses sway on the pond; his saffron shawl lifts in the breeze | {rama} | "Dark as a blue lotus" | `rama` leitmotif (exists), melody resolves |
| 6 | E | 17.9–21.1 | MS two-shot, eye level, palace terrace | gentle push | Dasharatha draws Rama towards him, hands on his shoulders; Rama bows his head; a lamp flame and the parasol fringe move | {dasharatha}, {rama} | "Pushya" | warm swell; `dasharatha` motif; pause 0.5 s after |
| 7 | T | 21.6–25.4 | CU, low lamp light, royal chamber | static, then snap push | the oil-lamp flame bends and shudders; shadows on the wall stretch; the king's eyes open wide | {dasharatha} | — | `drop`: melody and drums out together; drone + `heartbeat` 64 bpm + `wind` |
| 8 | T/P | 25.6–29.2 | MS two-shot, window behind | slow push | the king grips Rama's forearm and leans in; through the window, an empty road winds west to distant hills, dust drifting on it | {dasharatha}, {rama} | verse overlay: श्व एव पुष्यो भविता श्वोऽभिषेच्यस्तु मे सुतः (VR 2.4.2, vulgate) | `kaikeyi` tension motif, very quiet; pause 0.4 s after |
| 9 **Hero** | P | 29.6–34.2 | MS, eye level, shrine | very slow push | the sacred fire flickers and smoke rises; Rama and Sita, seated on a kusha-grass mat with folded hands, close their eyes | {rama}, {sita} | "The sacred fast" | `sages`-style bell + bansuri `calm`; `fire` bed |
| 10 | P2 | 34.4–38.9 | EWS, high angle crane-up over the royal road | crane up / tilt up | saffron banners unfurl along rooftops; petals drift onto the road; flames catch on tall lamp-trees; tiny distant citizens | {citizens} (distant) | **Who was away that day?** | celebration bed: `ayodhya` motif + procedural nagada pulse + `conch`; pause 0.3 s after |
| 11 **Hero** | N | 39.2–43.3 | MS, three-quarter back, white palace terrace (mirror of shot 1) | slow push towards her back | Manthara slowly turns her head; the end of her sari stirs in the wind; the decorated city glitters below | {manthara} | **Next: Manthara's Whisper** | `unresolved` motif ending on Re; hard cut to the 0.5 s chalk end sting |

Total about 43.3 s of picture + 1.0 s tail ≈ **44–45 s**. The Turn starts at about 21.6 s (A1: turn at 18–25 s). The main loop ("why afraid?") closes at about 29 s.

### Keyframe direction (for the creative director; positive-only, `{id}` tokens from `profiles/characters/ayodhya_kanda.json`, Kanda `style_prefix` prepended)

1. {dasharatha} standing at a tall carved sandstone window high in the palace, seen three-quarter from behind, looking up at a pale daytime sky where a bright meteor streaks, the golden city of Ayodhya with saffron banners far below, warm light on his white beard and gold crown.
2. {dasharatha} seated on a carved golden throne beneath a large round white royal parasol with a gold fringe, two distant attendants holding white yak-tail fans, pillared sandstone hall in warm morning light.
3. {dasharatha} standing before his throne with one open palm extended, a vast pillared assembly hall with {citizens} seated in distant rows, lapis-blue sky through tall openings.
4. two peacocks on a carved sandstone palace parapet with their trains spread wide, heads raised towards a dark rain cloud, marigold petals in the air, the golden city below.
5. {rama} standing in a palace courtyard beside a pond of blue lotuses, three-quarter view, eyes gently lowered, soft morning light, carved pillars behind.
6. {dasharatha} and {rama} on a palace terrace, the old king's hands resting on Rama's shoulders, Rama's head gently bowed, the white parasol behind, warm golden light.
7. close-up of {dasharatha} in a dark royal chamber lit by a single oil lamp, deep indigo shadows on the wall, his eyes wide and troubled.
8. {dasharatha} and {rama} beside a tall window, the king's hand on Rama's forearm, through the window an empty road winding west into distant hills under a pale sky.
9. {rama} and {sita} seated side by side on a mat of kusha grass before a small sacred fire in a stone shrine, hands folded, eyes closed, thin smoke rising, a carved lamp niche behind.
10. high view of the royal road of Ayodhya strewn with marigold petals, saffron and red banners on every rooftop, tall branching lamp-trees with small flames, {citizens} far below.
11. {manthara} standing on a moon-white palace terrace, seen three-quarter from behind, looking down at the decorated golden city with banners and lamp-trees, her sari end stirring in the wind.

## Sources (edition: vulgate, numbered as on valmikiramayan.net, accessed 2026-11-17)

| Shot | Claim | Locator | Note |
|---|---|---|---|
| 1 | Preparations complete; dreadful dreams, meteors, hostile planets | VR 2.3.20–21; VR 2.4.17–18 | "Crown was ready" = Vasishtha reports all arrangements made (2.3.21). The meteor is *divolkā*, a meteor by day (2.4.17) |
| 2 | Body worn out under the white parasol; wants rest | VR 2.2.7–9 | 2.2.8: "I desire rest" (*viśrāntim abhirocaye*) |
| 2 | The king is aged | VR 2.1.3, 2.1.35, 2.2.20–21 | — |
| 3 | Kings and leading citizens summoned; proposal of Rama as Yuvaraja | VR 2.1.45–50; VR 2.2.10–12 | 2.2.12 *yauvarājye niyoktāsmi*. Kekaya's king and Janaka were not invited (2.1.46), not used |
| 4 | Kings applaud like peacocks at a raining cloud; the hall seems to tremble | VR 2.2.17–18 | The text says the peacocks cry (*nardantaḥ*), not dance |
| 5 | Truthful, gentle, father-like to citizens; dark as a blue lotus | VR 2.2.29–39; VR 2.2.53 | *rāmam indīvara-śyāmam* (2.2.53) |
| 6 | The king embraces Rama; installation on the Pushya day | VR 2.3.33; VR 2.3.40 | — |
| 7 | He sends for Rama again; dreadful dreams | VR 2.4.3–8; VR 2.4.17 | — |
| 8 | Tomorrow is Pushya; be anointed while Bharata is away | VR 2.4.2, 2.4.21–22; VR 2.4.25 | Verse overlay 2.4.2. **Accuracy guard:** 2.4.26 calls Bharata virtuous and devoted to his elder brother; Dasharatha's worry is that minds change (2.4.20, 2.4.27). Nothing may suggest Bharata plotted |
| 8, 10 | Bharata and Shatrughna at their uncle's | VR 2.1.1–2 | Answer to the engagement line |
| 9 | Rama and Sita fast and sleep on kusha grass in the shrine | VR 2.4.23; VR 2.5.2, 2.5.9–11; VR 2.6.1–4 | — |
| 9–10 | Citizens decorate the city | VR 2.6.10–17; VR 2.5.18 | Banners and flags on houses (2.5.18); flowers and incense on the royal road (2.6.17) |
| 10 | Lamp-trees for the coming night | VR 2.6.18 | *dīpavṛkṣān* |
| 11 | Manthara, Kaikeyi's attendant from her birth home, climbs the moon-white terrace and sees the city | VR 2.7.1–2 | The terrace is "like the moon" (*candrasaṅkāśa*), a white palace. It is daytime in the text, so "moonlit" is not used |
| Next | She learns of the coronation and goes down to Kaikeyi | VR 2.7.11–13 | Teaser only; her words are AK02 |

### Flags (uncertain or to check)
- **Timeline:** the text compresses the night of the fast (2.6.1–5) and the citizens decorating (2.6.10–18) before Manthara hears "tomorrow" (2.7.11). Shot 9's "That night" refers to the fast night ordered in 2.4.23; the reviewer should confirm the wording does not imply a precise clock.
- **Shot 1** shows a daytime meteor at a window as an image of the omens; the text places the omens in Dasharatha's report to Rama (2.4.17–19), not at a particular window.
- **Crown wording:** a Yuvaraja's anointing (*abhiṣeka*) is not a full royal coronation; "crown prince" is used in shot 3, "crown" in the hook as the familiar word. The reviewer may prefer "coronation" in the hook.
- **Rama's skin tone** follows the bible recommendation (dark with a blue-lotus undertone, 2.2.53).
- CE numbering not checked for any locator.

## Applied learnings (`data/reports/latest_insights.json`, generated 2026-11-17 11:40, snapshot age 2.3 h)
- **A1** (anecdote, n=8): stakes stated in the hook itself ("His father was afraid"); 45 s shape kept because a new Kanda needs context, but the Turn is placed at about 21.6 s, inside the 18–25 s window A1 asks for.
- **A2** (anecdote, n=1): hook 8 words, about 2.8 s, stakes in the first sentence; frame 0 is a full keyframe (image-to-video starts from a complete frame, so the ≥70% drawn rule holds).
- **A3** (anecdote, n=8): about 45 s, the lower half of the 35–55 s band.
- **A4** (anecdote, n=8): engagement line as a share prompt with a real answer in the text ("Who was away that day?" → Bharata).
