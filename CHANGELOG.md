# aminurislamarnob-skills

## 1.0.0

### Major Changes

- Ship every skill as **one Claude Code plugin**, `aminurislamarnob-skills`, in the layout of [mattpocock/skills](https://github.com/mattpocock/skills): skills in bucket folders under `skills/` (`wordpress/`, `browser/`), an explicit `skills` array in `.claude-plugin/plugin.json`, a single-plugin marketplace named `aminurislamarnob`, a docs page per skill under `docs/`, `agents/openai.yaml` beside every `SKILL.md` for Codex, and changeset-driven releases.

  The four per-skill plugins (`plugin-docs`, `wp-worktree`, `browser-walkthrough`, `feature-video`, all `@aminurislamarnob-plugins`) are gone; install the one plugin instead:

  ```
  /plugin marketplace add aminurislamarnob/claude-plugins
  /plugin install aminurislamarnob-skills@aminurislamarnob
  ```

  The skills themselves are unchanged: **plugin-docs**, **wp-worktree**, **browser-walkthrough**, **feature-video**.
