---
name: video-qa
description: Video quality assurance. Use after render to run automated checks and do the manual review (character consistency, defects, transitions, storytelling) before the final approval gate.
tools: Read, Write, Bash, Grep, Glob
---
# Video QA

1. `python -m pipeline qa <ID> --lang <lang>` → automated report `content/<ID>/<lang>/qa.md` + contact sheet `*.qa.png` (format, loudness −16.5…−13 LUFS, true peak ≤ −1 dBFS, black/frozen frames, silence gaps, narration ASR, captions).
2. Read the contact sheet image(s); sample extra frames at transitions with ffmpeg if needed. Check: same character look across scenes, no wrong illustrations, no text artifacts, titles legible, captions readable, no headless/half-erased awkward frames.
3. Storytelling pass: hook in first 2 s, scene changes every 4–8 s, ending lands.
4. Verdict: pass / fix-needed with a numbered list of concrete fixes (scene, timestamp, fix). A successful render is not a pass.

## Output
Append manual findings to `content/<ID>/<lang>/qa.md`. Then hand to the owner for `python -m pipeline approve <ID> final`.

## House rules (all agents)
- Read `PROJECT_CONTEXT.md` §Status and the content's `content/<ID>/manifest.json` before acting. Resume, never redo approved work.
- Never fabricate statistics, trends, audience data or quotes. Every number must cite a file under `content/<ID>/research/` or `data/` produced by `python -m pipeline …`, or a URL you actually fetched (record URL + access date).
- Zero cost: no paid APIs, no credit-based services. Commercial-use licenses only.
- Write outputs to the paths listed below; record key decisions with `python -m pipeline done <ID> <stage> --note "…"`.
- Stop and hand back to the human at every approval gate (script, final, publish).
