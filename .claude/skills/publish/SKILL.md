---
name: publish
description: Upload or schedule an episode that already has the owner's G3 approval for that platform (YouTube private + publishAt, or an Instagram Reel via a launchd job). Manual only - the owner types /publish <ID> <lang> <platform>.
disable-model-invocation: true
---

# Publish an approved episode

Claude cannot invoke this skill on its own (`disable-model-invocation: true`). It runs only when the owner types `/publish …`. Even then, every step below must pass; if one fails, stop and report.

## Preconditions (check all, in order)
1. **G2 recorded** for the variant, and the latest QA verdict is pass (or warn with every warning waived).
2. **G3 recorded for this platform** (`gate:publish:youtube` or `gate:publish:instagram`) that names this language and an approved time. An Instagram G3 never covers YouTube, and the reverse.
3. **Hashes match:** the mp4 and `publish.json` on disk are the ones the owner approved. If either changed after G3, stop: the owner must approve again.
4. **Time matches:** the time passed to `--at` is exactly the approved time. Never pick or shift a time yourself.
5. **Metadata:** YouTube `synthetic: true` for new episodes; Instagram `is_ai_generated: true`; Made for Kids = No. Never edit a published episode's metadata or re-upload a published episode.
6. **Not already published:** check `<lang>/published.json`.

`python -m pipeline publish` enforces 1–4 itself. Run the check first and show the owner its output:
```
python -m pipeline publish <ID> --lang <lang> --platform <youtube|instagram> --at <approved ISO time> --check-gates-only
```
It verifies G2, the platform's G3 record, the approved time and both hashes, without a tunnel or an upload. If it refuses, stop. Never record or alter approvals: `approve`, `reject` and `waive` are owner commands, and `--yes` on them only works when the owner has set `STUDIO_OWNER_APPROVED=<ID>` in their own shell.

## YouTube
```
python -m pipeline publish <ID> --lang <lang> --at <approved ISO time>
```
Uploads private with `publishAt`; YouTube releases it at that time. Without `--at`, the approved YouTube time from the G3 record is used.

Several approved uploads can go through the persisted queue instead: `python -m pipeline publish-queue add <ID> --langs en,hi`, then `publish-queue list`, `publish-queue run --dry-run`, `publish-queue run --once`. The queue re-checks the gates before each upload, keeps the exact approved times and has a daily cap (`--cap`, default 6). Afterwards verify `publishAt` by API read-back, record the URL, and remind the owner that pinned comments and Related-video links are manual in Studio. `uploadLimitExceeded` means stop for the day; do not retry in a loop.

## Instagram
```
python -m pipeline publish <ID> --lang <lang> --platform instagram --dry-run --now
python -m pipeline publish <ID> --lang <lang> --platform instagram --at <approved ISO time> --yes
python -m pipeline ig-jobs
```
- Dry run first (token, tunnel, file limits; posts nothing).
- `--at … --yes` installs a self-removing launchd job; the Mac must be awake and plugged in at post time.
- `--now --yes` posts publicly at once: only if the owner's G3 says "now".
- Cancel with `--cancel`.

`--yes` is passed only because the owner's G3 for that exact platform, language, time and files is on record. It is never a substitute for that record.

## After publishing
- Record the platform IDs and times in PROJECT_CONTEXT §22.
- Analytics snapshots run from the daily read-only job (`python -m pipeline analytics`); check with `python -m pipeline report <VARIANT>`.
- Details on credentials, limits and the tunnel: `docs/PUBLISHING.md`.
