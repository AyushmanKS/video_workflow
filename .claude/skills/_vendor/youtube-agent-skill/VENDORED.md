# Vendored: youtube-agent-skill

- **Source:** https://github.com/Jakeschincariol/youtube-agent-skill
- **Commit:** a2feb21 (2026-09-16). **License:** MIT (copy in this folder).
- **Vetted 2026-11-16:** instruction-only skills; Python helpers use only the standard library, with no network, subprocess or file deletion; no hooks or MCP servers.

**Copied into `.claude/skills/`:** yt-script, yt-package, yt-retention, yt-viral, yt-seo, yt-plan, yt-audit, yt-comment.

**Not copied:** yt-edit, yt-shorts, yt-chapters. They are built for long recorded videos, not our generated Shorts.

**Integration:**
- scriptwriter runs `yt-script/hookscore.py` on English hooks as a second scorer.
- publishing-manager runs `yt-package/title.py` on titles and thumbnail text.
- performance-analyst runs `yt-retention/retention.py` on the CSV from `python -m pipeline retention-csv`.
- trend-researcher uses the `yt-viral/swipe.py` outlier-multiple method when per-channel medians are available.

**Limitations:**
- The word lists are English-only, so Hindi/Indic hooks get partial scores; use our storytelling rubric for those.
- The helpers' own notes say low scores mean "look again", and high scores promise nothing.

**Update policy:** re-vet the diff before pulling a newer commit.
