---
name: content-pipeline
description: Runbook to take one content piece from idea to published video and analytics in shorts-studio, orchestrating the project subagents, the python pipeline CLI and the three human approval gates. Use for "make the next episode", "run the pipeline", "resume <content id>", or analytics/optimization passes.
---

# Content pipeline runbook

Always start: read `PROJECT_CONTEXT.md` (§Status, §Next steps), then `python -m pipeline status` to find the next pending stage. Resume there.

| # | Stage | Who | Command / output | Parallel? |
|---|---|---|---|---|
| 0 | Create | main | `python -m pipeline new --topic "…" --series … --episode N --category mythology --style chalk --langs en,hi` | — |
| 1 | Research | `trend-researcher` | `pipeline research` → `research/evidence.*`, `research/report.md` | per-topic in parallel |
| 2 | Audience | `audience-localizer` | `audience.md` | per-language in parallel with 1 once topic known |
| 3 | Strategy | `content-strategist` | `strategy.md` (score table) | — |
| 4 | Script | `scriptwriter` (+ `storytelling` skill), `creative-director` for visuals | `<lang>/hooks.json`, `<lang>/script.json`, `<lang>/script.md` | languages in parallel after primary script |
| G1 | **Script approval** | owner | `pipeline approve <ID> script` | — |
| 5 | Voice | main | `pipeline produce <ID> --lang X --steps voice` | languages sequential (memory) |
| 6 | Voice QA | `language-qa` | `<lang>/voice_qa.md`; regenerate flagged scenes | — |
| 7 | Images | main | `pipeline produce <ID> --lang <primary> --steps images` (others reuse) | never parallel with voice (16 GB) |
| 8 | Render | main | `pipeline produce <ID> --lang X --steps render` | sequential |
| 9 | Video QA | `video-qa` | `pipeline qa <ID> --lang X` + manual review | per language |
| G2 | **Final approval** | owner | `pipeline approve <ID> final` | — |
| 10 | Metadata | `publishing-manager` | `<lang>/publish.json` | per language |
| 11 | Schedule | `publishing-manager` | `pipeline schedule --id <ID> --lang X` | — |
| G3 | **Publish approval** (video + metadata + time) | owner | `pipeline approve <ID> publish` | — |
| 12 | Publish | main | `pipeline publish <ID> --lang X` (private + publishAt) | — |
| 13 | Analytics | `performance-analyst` | `pipeline analytics`, `pipeline report <VARIANT>` at 24h/48h/7d/14d/30d | — |
| 14 | Optimize | `optimization-strategist` | `data/reports/recommendations.md` | — |

## Progress reporting (required during long runs)
- Before starting production, show the plan with estimates: `python -m pipeline progress <ID>`. This gives per-step done/total, measured seconds per unit, time left per step, and total time left with finish time.
- While voice, images or render run, post an update to the owner every 3–5 minutes. Use `python -m pipeline progress <ID> --oneline` (or `--watch 240 --oneline` in a monitor). Each update covers the current step, its time left, steps done, total time left and finish time.
- Rates are measured live from produced files and learned into `data/rates.json` after each run, so estimates improve over time.

## Memory rules (MacBook Air 16 GB)
Never run two heavy models at once: Qwen (5 GB), Z-Image 4-bit (8 GB peak), Veena (9.4 GB), Whisper turbo (~1.5 GB). Stop Ollama models before image/voice generation (`ollama stop qwen3:8b`).

## Recovery
- Re-run any `produce` step: finished scene assets are cached; only missing/deleted ones regenerate.
- Regenerate one scene image: delete `content/<ID>/<lang>/img/NN_raw.png` (optionally set `"seed"` on that scene).
- Regenerate one narration: delete `audio/NN.wav` and `audio/NN.words.json`.
- After any stage, update `PROJECT_CONTEXT.md` §Status / §Progress log.
