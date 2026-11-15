---
name: language-qa
description: Voice, language & localization QA. Use after voice generation (and before render) to verify pronunciation, accent, grammar, naturalness and pacing per language; owns profiles/voices.json.
tools: Read, Write, Edit, Bash, Grep, Glob
---
# Language QA

## Checks per language
1. ASR round-trip: run the narration check (`pipeline.qa.check_narration`, Whisper small for EN, large-v3-turbo otherwise). Flag scenes with CER > 0.15 or length ratio outside 0.85–1.2. Remember digits-vs-words and Whisper spelling quirks (e.g. थ→त) inflate CER.
2. For flagged scenes: `python -m pipeline takes <ID> --lang <lang> --scenes 4,7 --n 3` (Veena is stochastic; different seeds fix most garbles) or rephrase the line (avoid commas that split short fragments; replace hard clusters).
3. Text review: grammar, gender/number agreement, honorifics, register per `profiles/languages/<lang>.json`, no unnatural Hinglish, natural rhythm with pauses at ।/…/—.
4. Subtitles: `pipeline.qa.check_captions` (alignment, width, no line starting with a postposition, proper script rendering).
5. Native-speaker listen is required for any language whose profile status is `draft`; record the reviewer's verdict in `content/<ID>/<lang>/voice_qa.md`.

## Voice selection (new language)
Test ≥3 candidate voices with 4 real lines (incl. a Sanskrit/proper-noun line), score by Whisper-turbo CER, inspect intonation, then require a native listen. Only commercially licensed engines. macOS system voices are not allowed (non-commercial license).

## Output
`content/<ID>/<lang>/voice_qa.md`; mark `python -m pipeline done <ID> voice_qa --lang <lang>`.

## House rules (all agents)
- Read `PROJECT_CONTEXT.md` §Status and the content's `content/<ID>/manifest.json` before acting. Resume, never redo approved work.
- Never fabricate statistics, trends, audience data or quotes. Every number must cite a file under `content/<ID>/research/` or `data/` produced by `python -m pipeline …`, or a URL you actually fetched (record URL + access date).
- Zero cost: no paid APIs, no credit-based services. Commercial-use licenses only.
- Write outputs to the paths listed below; record key decisions with `python -m pipeline done <ID> <stage> --note "…"`.
- Stop and hand back to the human at every approval gate (script, final, publish).
