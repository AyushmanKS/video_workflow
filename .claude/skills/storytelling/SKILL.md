---
name: storytelling
description: Templates, hook rubric and script schema for writing short-form (60-90 s, 9:16) narrated videos in any language and genre — mythology, history, science, mystery, technology, biography, story entertainment. Use whenever writing or reviewing a script for shorts-studio.
---

# Storytelling for Shorts

## Principles
1. **Hook in ≤2 s** — a concrete, surprising, emotionally loaded line. No greetings, no "in this video".
2. **Open loops** — every 2 scenes either answer a question or open a new one.
3. **Show-able sentences** — each scene's narration must be drawable as one image; 1–2 sentences, 8–22 words (or equivalent spoken length).
4. **Specifics beat adjectives** — names, numbers, places, sensory detail (verified).
5. **Emotional arc** — curiosity → stakes → turn → payoff → hook to next.
6. **Endings** — payoff + a forward question that sets up the next episode; one genuine engagement prompt.
7. **Accuracy is part of quality** — distinguish source text / tradition / scholarship in wording ("the text says", "by tradition", "historians think").

## Pick a template (templates/)
- `mythology.md` — epics, scripture-based episodes (Valmiki Ramayana default)
- `history.md` · `science.md` · `mystery.md` · `technology.md` · `biography.md` · `story.md`

## Hook rubric (score 1–5 each; keep total and notes in hooks.json)
| Criterion | 5 means |
|---|---|
| Curiosity gap | viewer must keep watching to resolve it |
| Emotional stake | grief, awe, danger, injustice, wonder is felt immediately |
| Specificity | concrete image/name/number, not vague |
| Speed | understandable in under 2 seconds spoken |
| Audience resonance | uses this language audience's frame of reference (see audience.md) |
| Accuracy | fully true to sources; no clickbait distortion |
Write ≥6 hooks across types: question, bold claim, in-medias-res moment, contrast ("not with a war, but with tears"), number, forbidden/unknown detail. Select the highest total; ties → higher accuracy, then resonance.

## Script schema (`content/<ID>/<lang>/script.json`)
```json
{"title": "...", "topic": "...", "style": "chalk", "language": "hi", "character": "",
 "scenes": [{"narration": "spoken text = subtitle text", "visual": "image prompt (primary language file only; others reuse)",
   "emphasis": "on-screen title or empty", "keywords": ["highlighted", "words"], "pause": 0.3,
   "sfx": [{"name": "river"}, {"name": "arrow", "word": "तीर", "offset": -0.35}], "melody": "intro|calm|love|grief|rise", "swell": false,
   "kind": "verse|shloka (optional text scene)", "tone": "awe", "pacing": "slow"}],
 "description": "...", "hashtags": ["..."], "thumbnail": {"scene": 7, "devanagari": "...", "title": "...", "series": "...", "episode": "...", "subtitle": "..."},
 "sources": ["Valmiki Ramayana 1.2.15", "https://..."], "estimated_seconds": 80}
```
Available sfx: wind, birds, river (beds) · arrow, cry, bell (one-shots). Text scenes: `kind: verse` with `devanagari` lines + `source`; `kind: shloka` with from/to words and labels.

## Script review checklist (before the human gate)
- [ ] Hook scored and chosen; alternatives recorded
- [ ] Every factual line has a source; later-tradition material labelled or excluded
- [ ] Reads aloud naturally in this language (no translated structure)
- [ ] 60–90 s estimate; scene count 9–14
- [ ] Ending sets up the next piece
