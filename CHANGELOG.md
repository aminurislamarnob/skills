# aiarnob-skills

## 1.3.0

### Minor Changes

- [#3](https://github.com/aminurislamarnob/skills/pull/3) [`c48de63`](https://github.com/aminurislamarnob/skills/commit/c48de631dd892e96aceac5af757c4df293723991) Thanks [@aminurislamarnob](https://github.com/aminurislamarnob)! - Add **`case-study`**, a model-invoked skill in a new **`portfolio`** bucket. It writes a portfolio case study of your part in a project from your own git commits across one or more repositories, as a single HTML page: a hero with screenshots, a commit chart of your work against the team's, the brief, architecture and flow diagrams, before/after numbers, what you built next to what the team built, and a footer that says where every number came from. The counting (`git_stats.py`), screenshots (`shoot.mjs`) and page building (`build_page.py`) are bundled scripts, so it works the same in any agent. Claude publishes the page as a private Artifact, and other agents get a standalone HTML file. Gemini CLI users add a fourth install: `gemini skills install https://github.com/aminurislamarnob/skills.git --path skills/portfolio`.

- [`f9ec9f0`](https://github.com/aminurislamarnob/skills/commit/f9ec9f0603db444ce660be1d71c174290e9798a0) Thanks [@aminurislamarnob](https://github.com/aminurislamarnob)! - Add **`interactive-case-study`**, a model-invoked skill in the **`portfolio`** bucket. It writes a compact portfolio case study that a visitor clicks through: a hero with the live site, a phone screenshot and four count-up figures, a facts row, and at most six sections, each led by something to click. Those are a commit timeline whose bars say what shipped, an architecture diagram whose zones light up, a sticky deck of key decisions (log, was → now, table or image), a before/after switch over a gauge, a screens lightbox, and a square per commit showing who built it. Details fold into collapsed rows. `build_page.py --check` enforces the compact rules (at most six sections, two sentences per block, no commit hashes, PR numbers or dates in the copy), and the builder writes one dependency-free page that follows light and dark, works at phone width and respects reduced motion. Claude publishes it as a private Artifact, other agents get a standalone HTML file, and `references/porting.md` shows how to move it into your own site as a component.

## 1.2.0

### Minor Changes

- [#1](https://github.com/aminurislamarnob/skills/pull/1) [`1b94d8f`](https://github.com/aminurislamarnob/skills/commit/1b94d8f8dd5cc0eeb6f7763cb6073ec52395de2d) Thanks [@aminurislamarnob](https://github.com/aminurislamarnob)! - Add **`ship-branch`**, a user-invoked skill in a new **`git`** bucket. `/ship-branch` commits the current work, pushes, opens a pull request, merges it, and deletes the branch locally and on the remote, in one command, with the PR body written by the `pr` skill from mattpocock/skills (Summary, Evidence, Merge Danger). Each step is skipped when it has already happened (clean tree, branch already pushed, PR already open or merged, branch already gone), so a run that stops at a protected merge can be re-run and finishes from there. Gemini CLI users add a third install: `gemini skills install https://github.com/aminurislamarnob/skills.git --path skills/git`.

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
