---
name: content-pipeline
description: Runbook to take one content piece from idea to the G3 bundle in shorts-studio, orchestrating the five active subagents, the python pipeline CLI (lint, produce, qa, cleanup) and the three human approval gates. Use for "make the next episode", "run the pipeline", "resume <content id>", or analytics passes. Publishing itself is the separate, manually invoked `/publish` skill.
---

# Content pipeline runbook

Always start: read `PROJECT_CONTEXT.md` (§22 status, §23 next steps), then `python -m pipeline status` to find the next pending stage. Resume there. One episode per day, and only when the owner asks.

| # | Stage | Who | Command / output | Gate check |
|---|---|---|---|---|
| 0 | Arc plan (per arc, not per episode) | `series-planner` | `content/series/<series>.md`, profile diffs | owner OKs the arc (lightweight) |
| 1 | Create | main | `python -m pipeline new --topic "…" --series … --episode N --category mythology --style chalk --langs en,hi,gu,te` | — |
| 2 | Sources + hooks + scripts | `scriptwriter` (+ `storytelling` skill) | `research/report.md` (verse table), `<lang>/hooks.json`, `script.json`, `script.md` | — |
| 3 | Visual plan | `creative-director` | positive-only `visual` prompts, `{character}` tokens in the primary `script.json` | — |
| 4 | **Lint** | main | `python -m pipeline lint <ID>`; failures go back to the scriptwriter (max 2 rewrites, then the owner gets the diff) | must pass before G1 |
| 5 | Story QA | `reviewer` | scored review text → main saves `<lang>/review.md` | — |
| G1 | **Script approval** | owner | `python -m pipeline approve <ID> script --langs en,hi,gu,te` (owner runs it; records the `script.json` hashes) | lint pass |
| 6 | Voice | main | `python -m pipeline produce <ID> --lang X --steps voice` | languages sequential |
| 7 | Images | main | `python -m pipeline produce <ID> --lang <primary> --steps images` (others reuse) | never parallel with voice |
| 8 | Render | main | `python -m pipeline produce <ID> --lang X --steps render` | sequential |
| 9 | Automatic QA | main | `python -m pipeline qa <ID> --lang X` → `qa.md`, contact sheet, verdict | — |
| 10 | Visual + Audio QA | `reviewer` | scored review with numbered fixes; fixes routed to scriptwriter / creative-director | — |
| G2 | **Final approval** | owner | `python -m pipeline approve <ID> final --langs …`; waivers: `python -m pipeline waive <ID> --lang L --check <name>\|all-warnings --note "…"` | refused unless the latest QA verdict is pass, or warn with every warning waived (text + who); records the mp4 hash |
| 11 | Metadata | `packager` | `<lang>/publish.json` (`synthetic: true`, Instagram `is_ai_generated: true`); main runs title lint and `python -m pipeline schedule --id <ID> --lang X` and passes the output | — |
| G3 | **Publish approval, per platform** | owner | `python -m pipeline approve <ID> publish --langs … --platform youtube\|instagram --at <ISO>` (or `--at en=<ISO>,hi=<ISO>`, or `now`): one record per platform holding each language's time and the hashes of `publish.json` and the mp4. Rejections: `python -m pipeline reject <ID> <gate> --note "…"` | — |
| 12 | Publish | `/publish` skill (manual only) | `--check-gates-only` first; uploads directly or via `publish-queue`; see `.claude/skills/publish/SKILL.md` | refused unless G3 for that platform, time and hashes match |
| 13 | Analytics | main (deterministic) + daily LaunchAgent at 20:00 | `python -m pipeline analytics` (YouTube + Instagram, labels from `age_h`), `python -m pipeline report <VARIANT>`, weekly `python -m pipeline report --weekly` | — |
| 14 | Optimize | `optimizer` (dormant until ≥30 variants have 7-day data) | `data/reports/recommendations.md` | owner approves changes |

`approve` needs `--langs`, and publish approvals also need `--platform` and a time (`--at`; YouTube can fall back to `schedule.json`). The optional flags are `--by`, `--channel` and `--note`. Approvals are interactive. `--yes` works only when the owner has set `STUDIO_OWNER_APPROVED=<ID>` in their own shell, and then needs `--channel`. Check `--help` before first use. If a command does not exist, tell the owner instead of improvising a substitute.

## Learning loop (D4)
- The `features` row per variant is written at script, render and publish (`python -m pipeline features <ID>` or `--all` to backfill). It includes duration, scenes, words, w/s, hook, first frame (from `timeline.json` when present), voice, slot, weekday, title pattern, verse and engine version.
- Experiments: `python -m pipeline experiment add|list|start|close`.
  - One active at a time.
  - Arms alternate by odd/even episode across all languages.
  - At least 6 variants per arm per language before any claim, else "anecdote".
  - Compare within a language by ratio to its rolling median, never raw views across languages.
  - Pre-registered stop rule; 95% bootstrap interval.
- Experiment #1 (duration) is registered as `planned` and is observational before/after: C0001–C0005 are the legacy arm, and every new episode is 35–55 s per O1. Its legacy arm can never reach n = 6, so it stays "anecdote".
- `python -m pipeline schedule` ranks slots on the per-language outlier ratio and keeps the last slot while a content experiment is active.
- The weekly report (`python -m pipeline report --weekly` → `data/reports/weekly-<date>.md`) covers per-language medians, top and bottom ratios, experiments with n per arm, the D10 cannibalisation check and the E7 split triggers. Never quote numbers that are not in it.

**Agents never run `python -m pipeline approve` or `python -m pipeline publish`.** The reviewer and packager have no Bash at all; the main session runs deterministic commands for them and saves their returned text.

## Durations (owner decision O1)
Target 35–55 s per language, hard limit under 60 s. Lint blocks G1 above a 57 s estimate; final QA rejects ≥60.0 s. Details in the `storytelling` skill.

## Languages
en and hi are reviewed languages. gu and te are the `unreviewed-language` cohort (owner decision O9; `review_status` in `profiles/languages/gu.json`, `te.json`) until a native reviewer signs off: say so in every G1/G2 bundle, keep their CER checks warn-only, and analyse them separately.

## Progress reporting (required during long runs)
- Before production, show the plan with estimates: `python -m pipeline progress <ID>`.
- While voice, images or render run, post an update every 3–5 minutes: `python -m pipeline progress <ID> --oneline` (or `--watch 240 --oneline` in a monitor). Each update covers the current step, its time left, steps done, total time left and finish time.
- Rates are learned into `data/rates.json` after each run.

## Memory rules (MacBook Air 16 GB)
- Never run two heavy models at once: Qwen (5 GB), Z-Image 4-bit (8.3 GB peak), Maya 2 (Malini), Kokoro, Whisper large-v3-turbo (~1.5 GB), ECAPA. Stop Ollama models first (`ollama stop qwen3:8b`).
- Heavy steps take the lock file `data/heavy.lock`. If it exists, another heavy job is running: wait for it (check `python -m pipeline progress`), never delete the lock while that process is alive. A stale lock (its process gone) is removed only after confirming with `ps`.

## Disk
- `python -m pipeline cleanup` previews what can be removed (safe intermediates; `--models` unused model caches; `--tools` tool caches). `--apply` deletes; every deletion is logged in `data/cleanup_log.jsonl` with its restore command. Policy: `docs/PRODUCTION_ROADMAP.md` §7b.
- `produce` warns below 20 GB free and removes only the safe tier below 10 GB. Ask the owner before `--apply` with `--models`.

## Recovery
- Re-run any `produce` step: finished scene assets are cached; only missing or deleted ones regenerate.
- Regenerate one scene image: delete `content/<ID>/<lang>/img/NN_raw.png` (optionally set `"seed"` on that scene).
- Regenerate one narration: delete `audio/NN.wav` and `audio/NN.words.json`, or `python -m pipeline takes <ID> --lang <l> --scenes 4,7 --n 3`.
- Editing `narration` or `visual` after production does not invalidate caches yet: delete the affected files by hand.
- After any stage, update `PROJECT_CONTEXT.md` §22 / progress log.
