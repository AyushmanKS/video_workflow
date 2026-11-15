# CLAUDE.md — shorts-studio

**Read `PROJECT_CONTEXT.md` first, all of it.** It is the source of truth for the architecture, decisions, current status (§22) and exact next steps (§23). Then run `python -m pipeline status` and resume from the next pending stage. Do not redo approved work.

## Non-negotiables
- **Zero cost.** No paid APIs, subscriptions or credits. Commercial-use licenses only, so macOS system voices are excluded.
- **Human gates.** The owner approves at three points: script (G1), final video (G2), and publish with video + metadata + time (G3). Never publish or schedule without explicit approval.
- **Progress reporting.** During any long run (voice, images, render), post an update every 3–5 minutes using `python -m pipeline progress <ID> --oneline`. Each update covers the current step, its time left, total time left and finish time.
- **Approved style.** Keep the approved chalkboard style and the reduced chalk SFX (`chalk.CHALK_SFX_GAIN = 0.035`).
- **Hindi voice.** Use Veena kavya with voice-prompt priming and the speaker guard. QA must pass `speaker_consistency`, which checks that the whole narration is one voice.
- **No fabrication.** Never invent analytics, trends or audience data; cite the evidence files.
- **Memory (16 GB MacBook Air).** Never run two heavy models at once. See `.claude/skills/content-pipeline/SKILL.md`.
- **Code style.** No code comments.
- **Git.**
  - The remote is `AyushmanKS/video_workflow` and uses a repo-local identity and credential helper (see PROJECT_CONTEXT §17).
  - Before each commit, scan staged files for secrets or media.
  - Never commit `secrets/`, `data/`, `models/`, `out/` or media files.
- **Privacy.** Keep the owner's personal details out of requests to external services.

## Where things are
| What | Where |
|---|---|
| Engines | `studio.py`, `chalk.py`, `veena.py`, `styles.py`, `publish.py` |
| Orchestration | `python -m pipeline …` (`pipeline/`) |
| Agents | `.claude/agents/` |
| Skills | `.claude/skills/` (`content-pipeline`, `storytelling`, vendored `yt-*`) |
| Profiles | `profiles/` |
| Content | `content/<ID>/` |
| Credentials setup | `docs/PUBLISHING.md` |
