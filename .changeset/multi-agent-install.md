---
"aminurislamarnob-skills": minor
---

Document and verify installs for every agent, not only Claude Code. The README's **Installation** section now has one block per agent: Claude Code and **Codex** install the plugin from this repo's marketplace (`…@aminurislamarnob`), **GitHub Copilot** CLI and VS Code install the same plugin with a one-time `autoUpdate` opt-in, **Gemini CLI** installs each promoted bucket with `gemini skills install --path`, and everything else goes through `npx skills@latest add`. Codex and Copilot read the existing `.claude-plugin/` manifests, so no new files ship. The canonical wording lives in `.agents/install-block.md`.
