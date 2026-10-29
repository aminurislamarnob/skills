---
"aiarnob-skills": minor
---

Add **`setup-aiarnob-skills`**, a user-invoked, run-once-per-repo setup skill, so the install process matches [mattpocock/skills](https://github.com/mattpocock/skills): install with `npx skills add` or the Claude Code plugin, then run `/setup-aiarnob-skills`. It finds the local WordPress site (URL, root, admin login source), asks where the client docs live when `plugin-docs` is installed, checks the tooling the skills need, and writes `docs/agents/wordpress-site.md` and `docs/agents/plugin-docs.md` plus an `## Agent skills` block in `CLAUDE.md` or `AGENTS.md`. `plugin-docs`, `browser-walkthrough` and `feature-video` now read that config first and fall back to asking.
