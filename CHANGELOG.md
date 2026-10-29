# aiarnob-skills

## 1.1.0

### Minor Changes

- [`5e6deb4`](https://github.com/aminurislamarnob/skills/commit/5e6deb4f032bd48b9e83f95b15bda570d2a0f767) Thanks [@aminurislamarnob](https://github.com/aminurislamarnob)! - Document and verify installs for every agent, not only Claude Code. The README's **Installation** section now has one block per agent: Claude Code and **Codex** install the plugin from this repo's marketplace (`…@aminurislamarnob`), **GitHub Copilot** CLI and VS Code install the same plugin with a one-time `autoUpdate` opt-in, **Gemini CLI** installs each promoted bucket with `gemini skills install --path`, and everything else goes through `npx skills@latest add`. Codex and Copilot read the existing `.claude-plugin/` manifests, so no new files ship. The canonical wording lives in `.agents/install-block.md`.

- [`82c1c56`](https://github.com/aminurislamarnob/skills/commit/82c1c56b3e3e72ed12a45149259ff293668e09e7) Thanks [@aminurislamarnob](https://github.com/aminurislamarnob)! - Rename the plugin from `aminurislamarnob-skills` to **`aiarnob-skills`**, and the setup skill from `setup-aminurislamarnob-skills` to **`setup-aiarnob-skills`**. The marketplace name stays `aminurislamarnob`. Anyone on the old name uninstalls it and installs `aiarnob-skills@aminurislamarnob`; repos that already ran setup keep their `docs/agents/` config unchanged.

- [`70c344c`](https://github.com/aminurislamarnob/skills/commit/70c344c496ba43d4af6224daf0d8eb63d888e387) Thanks [@aminurislamarnob](https://github.com/aminurislamarnob)! - Add **`setup-aiarnob-skills`**, a user-invoked, run-once-per-repo setup skill, so the install process matches [mattpocock/skills](https://github.com/mattpocock/skills): install with `npx skills add` or the Claude Code plugin, then run `/setup-aiarnob-skills`. It finds the local WordPress site (URL, root, admin login source), asks where the client docs live when `plugin-docs` is installed, checks the tooling the skills need, and writes `docs/agents/wordpress-site.md` and `docs/agents/plugin-docs.md` plus an `## Agent skills` block in `CLAUDE.md` or `AGENTS.md`. `plugin-docs`, `browser-walkthrough` and `feature-video` now read that config first and fall back to asking.

### Patch Changes

- [`48abbf0`](https://github.com/aminurislamarnob/skills/commit/48abbf003f335e7f72ba621bb3f952f68db7f233) Thanks [@aminurislamarnob](https://github.com/aminurislamarnob)! - The repository moved from `aminurislamarnob/claude-plugins` to **`aminurislamarnob/skills`**. GitHub redirects the old URL, so existing installs and clones keep working; new installs use `claude plugin marketplace add aminurislamarnob/skills` and `npx skills@latest add aminurislamarnob/skills`.

## 1.0.0

### Major Changes

- Ship every skill as **one Claude Code plugin**, `aiarnob-skills`, in the layout of [mattpocock/skills](https://github.com/mattpocock/skills): skills in bucket folders under `skills/` (`wordpress/`, `browser/`), an explicit `skills` array in `.claude-plugin/plugin.json`, a single-plugin marketplace named `aminurislamarnob`, a docs page per skill under `docs/`, `agents/openai.yaml` beside every `SKILL.md` for Codex, and changeset-driven releases.

  The four per-skill plugins (`plugin-docs`, `wp-worktree`, `browser-walkthrough`, `feature-video`, all `@aminurislamarnob-plugins`) are gone; install the one plugin instead:

  ```
  /plugin marketplace add aminurislamarnob/skills
  /plugin install aiarnob-skills@aminurislamarnob
  ```

  The skills themselves are unchanged: **plugin-docs**, **wp-worktree**, **browser-walkthrough**, **feature-video**.
