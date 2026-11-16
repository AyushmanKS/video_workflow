---
name: storytelling
description: Beat framework, timings, per-language word budgets, hook/loop rules, accuracy and citation rules, and the script.json schema for 35–55 s (hard limit under 60 s) 9:16 narrated Shorts in any language and genre — mythology, history, science, mystery, technology, biography, story. Use whenever writing, linting or reviewing a script for shorts-studio.
---

# Storytelling for Shorts (35–55 s)

Target 35–55 s per language, hard limit under 60 s (owner decision O1, 2026-11-16). Why: all 20 renders up to Ep05 ran 74.8–111.2 s (WORKFLOW_AUDIT F01). `python -m pipeline lint <ID>` blocks G1 when any language's estimate exceeds 57 s; final QA rejects ≥60.0 s and warns outside 35–55 s. Source for every rule below: `docs/VIDEO_QUALITY_UPGRADE_PLAN.md` §2.

## Principles
1. **Frame 0 is the hook.** Readable without sound: the episode's most striking image, ≥70% drawn at frame 0 (O5), first caption visible by 0.3 s, impact sound at 0.0 s.
2. **First word by 0.3 s.** No greetings, no "in this video".
3. **Open loops on a clock:** a question opened or answered every 8–12 s.
4. **Pattern interrupt** every 6–8 s (shot size, angle, accent, sound bed or rhythm); change all of them together only at the Turn.
5. **Show-able sentences:** each scene is drawable as one image; 1–2 sentences.
6. **Specifics beat adjectives:** verified names, numbers, places. Build gaps on names the audience already knows ("Rama hesitated", not "Suketu's daughter").
7. **Accuracy is part of quality:** "the text says" / "by tradition" / "historians think".
8. **Cut words, never speed up the voice.** English already sits at the brisk end of audiobook pace.

## Beats
| Beat | Job | Rule |
|---|---|---|
| **H1** Hook-visual | Stop the scroll | Frame 0 already readable, impact at 0.0 s |
| **H2** Hook-line | Open the main loop | Contradiction, specific number or stake; ≤12 EN words; spoken ≤3.0 s (lint warns >2.2 s) |
| **C** Context | Ground the viewer | Who, where, why in ≤2 shots; only the names the story needs |
| **E** Escalation | Raise stakes | Answer one small question, open another; pattern interrupt here |
| **T** Turn | Reversal or reveal | 0.3–0.6 s silence first; verse card goes here if used |
| **P** Payoff | Close the main loop | Fastest cutting, loudest moment, by 85–90% of runtime |
| **N** Next / loop | Cliffhanger + loop | One line opening the next question; final composition matches frame 0 |

## Beat timings (seconds · shots · EN/HI words)
| Beat | 35 s ("anecdote") | 45 s (default) | 55 s (two-beat; dense episodes) |
|---|---|---|---|
| H1+H2 | 0.0–2.0 · 1 · 8–10 | 0.0–2.0 · 1 · 8–10, H2b 2.0–4.5 · 1 · 6–8 | 0.0–2.0 · 1 · 8–10, H2b 2.0–5.0 · 1 · 7–8 |
| C | 2.0–8.0 · 2 · 14–16 | 4.5–12.0 · 2 · 18–20 | 5.0–13.0 · 2 · 20 |
| E | 8.0–18.0 · 3 · 25 | 12.0–22.0 · 3 · 25–28 | E1 13.0–24.0 · 3 · 28 |
| T | 18.0–25.0 · 1–2 · 15 | 22.0–30.0 · 2 · 16–18 | T1 24.0–33.0 · 2 · 20, E2 33.0–43.0 · 3 · 25 |
| P | 25.0–31.0 · 2 · 14 | 30.0–40.0 · 3 · 20–22 | 43.0–50.0 · 2–3 · 18 |
| N | 31.0–35.0 · 1 · 8–10 | 40.0–45.0 · 1 · 10–12 | 50.0–55.0 · 1 · 10–12 |
| Shots / stills | 10–11 / 6–8 | 12–13 / 8–10 | 15–16 / 10–12 |

Shots exceed stills only when the engine supports crops of one still; until then, one scene = one still.

## Word budgets per language
Formula: `words ≤ rate_eff × (target − 1.0 s tail − verse_card_s)`, planning rates en 2.6, hi 2.6, gu 2.0, te 1.5 w/s (measured C0002–C0005; Malini for hi/gu/te, Kokoro af_heart for en).

| Target | en | hi | gu | te |
|---|---|---|---|---|
| 35 s | 88 | 88 | 68 | 51 |
| 45 s | 114 | 114 | 88 | 66 |
| 55 s | 140 | 140 | 108 | 81 |

- With a 3 s silent verse card, subtract 8 / 8 / 6 / 4.
- Telugu is always the longest: write it natively to its own budget and shorten per scene; never drop scenes (visual parity with the primary language).
- The lint uses speech-only rates (en 2.81, hi 2.80, gu ≈2.3, te 1.66 w/s) plus explicit pauses and 1.15 s lead and tail; it is the arbiter.
- Verse: show it on screen while the narration gives the meaning; full recitation (6–9 s in Hindi) belongs in a separate "Shloka" Short. Optionally recite one pāda (2–3 s) as hook or payoff.

## Scenes
- 8–11 narrated scenes, each 2.5–7 s of narration.
- 2–3 planned silences of 0.3–0.8 s via the scene `pause` field: before the Turn, before the Payoff, optionally before Next.
- No digits in gu/te narration (write numbers as words; `pipeline/numwords.py` handles only en/hi/mr).
- `keywords` are exact tokens as they appear in the narration.

## Hook rubric (score 1–5 each; keep totals and notes in hooks.json)
| Criterion | 5 means |
|---|---|
| Curiosity gap | viewer must keep watching to resolve it |
| Emotional stake | grief, awe, danger, injustice, wonder felt immediately |
| Specificity | concrete image, name or number |
| Speed | understood in under 2 s spoken; ≤3.0 s hard |
| Audience resonance | uses this language audience's frame of reference |
| Accuracy | fully true to sources; no clickbait distortion |

Two added checks: **visual hook** (does frame 0 alone make sense, muted?) and **hook-to-payoff distance** (the main loop closes by 85–90% of runtime; "next episode" never counts as the payoff).
Write ≥6 hooks across types: question, bold claim, in medias res, contrast, number, forbidden or unknown detail. Series-fit types: contradiction ("Rama's first enemy had the strength of a thousand elephants. And he did not want to kill her." 1.24.26, 1.26.12); request with a twist; text versus belief (at most once every 4–5 episodes, respectful); sensory in medias res (0.8 s of image and sound). Select the highest total; ties → accuracy, then resonance.

## Loops and cliffhangers
- Close this episode's loop first, then open the next with exactly one line. "Next:" card ≤3 words.
- One loop type per episode: **composition** (last shot reuses frame 0's framing), **sentence** (last line flows into the first; never cut mid-word, which reads as an error in hi/gu/te), or **sound** (music ends on the note the intro starts on).
- Engagement prompt: at most one, ≤6 words, with a real answer in the text ("Which sage cursed her?"); otherwise move it to the pinned comment.

## Accuracy rules (mythology; adapt the principle to other genres)
**Citations, edition-labelled.** The project verifies against the vulgate (southern recension; sa.wikisource, valmikiramayan.net). The Baroda Critical Edition and Goldman's translation number some verses differently (*mā niṣāda* is CE 1.2.14, vulgate 1.2.15).
- Cite `VR <kāṇḍa>.<sarga>.<verse> (vulgate)`; add `[CE x.y.z]` only when checked against the CE or Goldman.
- Record the edition in every `sources` entry: either an object `{"ref": "VR 1.26.12", "edition": "vulgate (sa.wikisource)"}` or a string carrying it, `"VR 1.26.12 (vulgate)"`. URLs are allowed alongside.
- A line absent from the CE: "found in the southern manuscripts", not "Valmiki says".

**No invented quotes.** Reported speech is fine. Every quotation mark in narration needs a `quote_src` locator on that scene (lint rejects it otherwise). Never present TV dialogue or Ramcharitmanas chaupais as Valmiki. Add no motives the text lacks.

**Popular retelling vs Valmiki (summary; full table in VQ §2.8)**
| Popular version | In Valmiki |
|---|---|
| Lakshman Rekha | Absent (Ramcharitmanas mentions it once; TV made it central) |
| Ahalya turned to stone | Unseen, living on air, lying on ash (1.48) |
| Shabari's tasted berries | Roots and fruits as hospitality; no tasting |
| Swayamvara with assembled kings | Sita *vīryaśulkā*; Rama breaks the bow on Vishvamitra's visit |
| Ravana lifts Sita with the earth | He seizes her physically (the earth version is Kamba) |
| Maya Sita | Absent (bhakti retellings) |

Check in the text before using: the squirrel at the setu, Hanuman's gada, "Kodanda", Lanka as a golden city. Frame differences as "In Valmiki's telling…", never "myth busted"; name later traditions respectfully ("Tulsidas, centuries later…"); in gu/te, nod to Giridhar or Molla only where they agree with Valmiki.

**Ravana with depth.** Text anchors: 5.49.17–18 (Hanuman marvels at his form and radiance; "if he were not so strong in adharma…"), 5.18.2–3 (Vedic chanting at dawn in his realm), 3.35.9 and 6.71.27 (ten heads). Show splendour, learning, power and choice: greatness undone by adharma. Do not adopt Ravana-as-hero readings.

**Sensitivity.** Rama calm, never snarky; Sita never sexualised; mutilation and gore off-screen; Hanuman never comic; deities as symbols; no political tie-ins; pilgrimage sites named neutrally.

**Pronunciation.** Use the per-scene `tts` field for respellings the voice needs ("Raama", "Seetaa", "Raavana", "Maareecha"); `narration` stays the correct spelling for captions. Recite Sanskrit with the schwa kept.

## Pick a template (templates/)
`mythology.md` (Valmiki Ramayana default) · `history.md` · `science.md` · `mystery.md` · `technology.md` · `biography.md` · `story.md`. Compress each template's arc into the beats above.

## Script schema (`content/<ID>/<lang>/script.json`)
```json
{"title": "...", "topic": "...", "style": "chalk", "language": "hi", "character": "",
 "scenes": [{"narration": "spoken text = subtitle text", "tts": "optional respelled text for the voice",
   "visual": "positive-only image prompt (primary language file only; others reuse)",
   "emphasis": "on-screen title or empty", "keywords": ["highlighted", "words"], "pause": 0.3,
   "quote_src": "VR 1.26.12 (vulgate), only when narration contains a quotation",
   "sfx": [{"name": "river"}, {"name": "arrow", "word": "तीर", "offset": -0.35}], "melody": "intro|calm|love|grief|rise", "swell": false,
   "kind": "verse|shloka (optional text scene)", "tone": "awe", "pacing": "slow"}],
 "description": "...", "hashtags": ["..."], "thumbnail": {"scene": 7, "devanagari": "...", "title": "...", "series": "...", "episode": "...", "subtitle": "..."},
 "sources": [{"ref": "VR 1.24.26", "edition": "vulgate (sa.wikisource)"}, "https://..."], "estimated_seconds": 45}
```
- `pause` is the silence after the scene (default 0.18 s); planned silences are 0.3–0.8.
- Available sfx: wind, birds, river (beds) · arrow, cry, bell (one-shots). Add new names only when `chalk.sound` supports them (see the `audio-mix` skill).
- Text scenes: `kind: verse` with `devanagari` lines + `source`; `kind: shloka` with from/to words and labels.
- Optional shot fields (`shot`, `move`, `transition`, `reveal`, `image` + `crop`) only once the engine supports them; omitted fields reproduce today's render.

## Script review checklist (before G1)
- [ ] `python -m pipeline lint <ID>` passes for every language (estimate ≤57 s; target 35–55 s)
- [ ] 8–11 scenes of 2.5–7 s; same scene count and `visual` across languages
- [ ] Hook spoken ≤3.0 s, frame 0 readable muted, first word by 0.3 s; alternatives recorded in hooks.json
- [ ] Beats present; main loop closes by 85–90%; one loop type; "Next:" ≤3 words; engagement line ≤6 words with a real answer
- [ ] 2–3 planned silences via `pause`
- [ ] Every factual line has a locator with edition; every quote has `quote_src`; later traditions labelled or excluded
- [ ] Reads aloud naturally in each language (no translated structure); no digits in gu/te
- [ ] gu/te flagged as `unreviewed-language` in script.md until a native reviewer signs off
