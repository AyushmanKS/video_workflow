# CLAUDE.md — shorts-studio

**Read `PROJECT_CONTEXT.md` first, all of it.** It is the source of truth for the architecture, decisions, current status (§22) and exact next steps (§23). Then run `python -m pipeline status` and resume from the next pending stage. Do not redo approved work.

## Non-negotiables
- **Zero cost.** No paid APIs, subscriptions or credits. Commercial-use licenses only, so macOS system voices are excluded.
- **Human gates.** The owner approves at three points: script (G1), final video (G2, needs a QA pass or recorded waivers), and publish with video + metadata + time per platform (G3). Never publish or schedule without explicit approval; agents never run `pipeline approve` or `pipeline publish`, and publishing runs only through the manual `/publish` skill.
- **Analytics checkup (workflow).** Before each new episode's scripts: `python -m pipeline analytics` (if the last snapshot is >12 h old) and `python -m pipeline insights`; the scriptwriter applies `data/reports/latest_insights.json`, and the learnings are shown with the scripts at G1 (no extra approval).
- **Progress reporting.** During any long run (voice, images, render), post an update every 3–5 minutes using `python -m pipeline progress <ID> --oneline`. Each update covers the current step, its time left, total time left and finish time.
- **Approved style.** Keep the approved chalkboard style and the reduced chalk SFX (`chalk.CHALK_SFX_GAIN = 0.035`).
- **Chalk-puppet animation from Episode 10 (approved 2026-11-18).**
  - New episodes are engine v3. Each scene is drawn in chalk, then comes alive as a Kathputli-style puppet, rigged with `content/<ID>/rig.json`.
  - Chalk sound is at ×0.12 (`chalk.PUPPET_CHALK_SFX_SCALE`).
  - Verse slides keep verse-only time.
  - `python -m pipeline rig-qa` must pass before render. See PROJECT_CONTEXT §30.
- **YouTube long-form (owner, 2026-11-18).**
  - **What:** 2 videos per Kanda (Bala Kanda first), each a new continuous story, 8–12 min, horizontal 16:9, in en, hi and te, using the chalk-puppet engine.
  - **Shorts continue unchanged.**
  - **Duration rule:** the 35–55 s rule applies to Shorts only.
  - **Gates:** same three gates.
  - **Details:** PROJECT_CONTEXT §23.0.
- **AK01 is on hold.** The approved Ayodhya Kanda sample (`data/anim_lab/AK01_puppet/AK01-puppet-{en,hi}.mp4`) is scheduled or published only when the series reaches that chapter. Raise it then; never before.
- **Hindi voice.** Use Maya 2 Native `maya2:Malini` (also gu and te; Veena kavya is retired, 2026-11-16). QA must pass `speaker_consistency`, which checks that the whole narration is one voice.
- **Duration.** Target 35–55 s per language, hard limit under 60 s. Run `python -m pipeline lint <ID>` before G1; it blocks estimates above 57 s. See the `storytelling` skill.
- **AI disclosure.** New episodes set YouTube `synthetic: true` and Instagram `is_ai_generated: true`; Made for Kids = No. See `docs/PUBLISHING.md`.
- **No fabrication.** Never invent analytics, trends or audience data; cite the evidence files.
- **Memory (16 GB MacBook Air).** Never run two heavy models at once; heavy steps hold `data/heavy.lock`. See `.claude/skills/content-pipeline/SKILL.md`.
- **Disk.** `python -m pipeline cleanup` previews removable files; `--apply` only with the owner's OK for model caches.
- **Code style.** No code comments.
- **Git.**
  - The remote is `AyushmanKS/video_workflow` and uses a repo-local identity and credential helper (see PROJECT_CONTEXT §17).
  - Before each commit, scan staged files for secrets or media.
  - Never commit `secrets/`, `data/`, `models/`, `out/` or media files.
- **Privacy.** Keep the owner's personal details out of requests to external services.

## Where things are
| What | Where |
|---|---|
| Engines | `studio.py`, `chalk.py`, `styles.py`, `publish.py`, `instagram.py`, `veena.py` (legacy Veena backend) |
| Orchestration | `python -m pipeline …` (`pipeline/`) |
| Agents | `.claude/agents/` (series-planner, scriptwriter, creative-director, reviewer, packager; optimizer dormant) |
| Skills | `.claude/skills/` (`content-pipeline`, `storytelling`, `audio-mix`, `publish`, vendored `yt-*`) |
| Profiles | `profiles/` |
| Content | `content/<ID>/` |
| Credentials setup | `docs/PUBLISHING.md` |
