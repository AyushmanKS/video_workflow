# shorts-studio

A zero-cost, local-first, multi-agent studio for researching, writing, producing, publishing and measuring 9:16 short videos for Indian language audiences. Built for a MacBook Air with Claude Code, open models and free APIs.

**Start here → [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)**: architecture, agents, setup, standards, status and exact next steps.

```bash
source .venv/bin/activate
python -m pipeline status            # where every content item stands
python -m pipeline trending          # YouTube India trending evidence
python -m pytest -q tests            # unit tests
```

- **Production engines:** `studio.py`, `chalk.py`, `veena.py`
- **Orchestration:** `pipeline/`
- **Agents:** `.claude/agents/`
- **Skills:** `.claude/skills/`
- **Profiles:** `profiles/`
- **Credentials setup:** [docs/PUBLISHING.md](docs/PUBLISHING.md). Secrets live only in `secrets/` and are never committed.
