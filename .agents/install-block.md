# The canonical install block

One install story, one wording. `README.md`, `.changeset/*`, and every page under `docs/` must say **this** and nothing else. Change it here first, then propagate.

## Managed installs first

Lead with installs that update themselves. Fall back to skills.sh, labelled "manual updates", only for agents that have no such install. Call a route managed only if it updates without the user running a command. Put any one-time opt-in beside its install command.

Every managed route installs from this repo's own marketplace, `.claude-plugin/marketplace.json` and `plugin.json`. Codex and GitHub Copilot read those same two Claude-format files, so there is no `.codex-plugin/` or Copilot-specific manifest to keep in sync. Those routes reinstall only when the `version` in `plugin.json` changes; the Release workflow copies it from `package.json`, so users get a release when the "chore: version skills" PR merges.

| Agent         | Route                                  | Updates itself?                                                        |
| ------------- | -------------------------------------- | ---------------------------------------------------------------------- |
| Claude Code   | `@aminurislamarnob` marketplace        | Yes, by default                                                        |
| Codex         | `@aminurislamarnob` marketplace        | Yes, at startup, by default                                            |
| Copilot CLI   | `@aminurislamarnob` marketplace        | Yes, after a one-time `autoUpdate: true`                               |
| VS Code       | Chat: Install Plugin From Source       | Yes, daily, by default                                                 |
| Gemini CLI    | `gemini skills install` (copies)       | No. A Gemini extension would need a flat `skills/<name>/` layout       |
| Everyone else | skills.sh                              | No. Run `npx skills@latest update`, and re-run `add` for new skills    |

Verified 2026-10-29: Claude Code (marketplace add + install, all five skills), Copilot CLI 1.0.105 (marketplace add + install, all five skills), Gemini CLI 0.66.0 (both bucket installs, all five skills). Codex is documented from its manifest loader (`codex-rs/core-plugins/src/manifest.rs` falls back to `.claude-plugin/` when there is no `.codex-plugin/`) and from mattpocock/skills, which ships the same layout; nobody has run Codex against this repo yet.

When the plugin is accepted into Anthropic's directory (`claude-plugins-official`, submitted at https://clau.de/plugin-directory-submission), the Claude Code block becomes the one-liner `claude plugin install aiarnob-skills@claude-plugins-official` with no `marketplace add`. Until then, the two-line block below is the route.

## Claude Code

<canonical-block name="claude-code">

```bash
claude plugin marketplace add aminurislamarnob/skills
claude plugin install aiarnob-skills@aminurislamarnob
```

Updates itself by default.

</canonical-block>

## Codex

<canonical-block name="codex">

```bash
codex plugin marketplace add aminurislamarnob/skills
codex plugin add aiarnob-skills@aminurislamarnob
```

Updates itself at startup.

</canonical-block>

## GitHub Copilot (CLI and VS Code)

Use the marketplace, not `copilot plugin install aminurislamarnob/skills`. Copilot has deprecated direct repo installs, and they can't auto-update. `marketplace add` writes the `extraKnownMarketplaces` entry itself; the one-time edit only adds `autoUpdate: true`.

<canonical-block name="copilot">

```bash
copilot plugin marketplace add aminurislamarnob/skills
copilot plugin install aiarnob-skills@aminurislamarnob
```

Then, once, add `"autoUpdate": true` to the marketplace entry in `~/.copilot/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "aminurislamarnob": { "source": { "source": "github", "repo": "aminurislamarnob/skills" }, "autoUpdate": true }
  }
}
```

In VS Code, run **Chat: Install Plugin From Source** and enter `https://github.com/aminurislamarnob/skills`. It updates daily.

</canonical-block>

## Gemini CLI

Gemini doesn't read `.claude-plugin`, and `--path` takes one folder. One install per promoted bucket gives exactly the promoted set.

<canonical-block name="gemini">

```bash
gemini skills install https://github.com/aminurislamarnob/skills.git --path skills/wordpress
gemini skills install https://github.com/aminurislamarnob/skills.git --path skills/browser
```

Re-run both commands to update.

</canonical-block>

## Every other agent, or editable files (skills.sh)

`-a` preselects the agent. Prefer skills.sh to an agent's own repo installer, because those also pull in any `in-progress/` bucket. `npx skills update` skips skills added upstream since `add`, so the block tells users to re-run `add`.

<canonical-block name="other-agents">

```bash
npx skills@latest add aminurislamarnob/skills -a <agent>  # cursor, opencode, devin, windsurf, amp, pi; omit -a to choose
```

When the installer asks which skills to take, include `setup-aiarnob-skills`. To update, run `npx skills@latest update`, and re-run `add` to pick up new skills.

</canonical-block>

Use the single-skill form wherever one skill is named on its own, as the `docs/` pages do.

<canonical-block name="skills-sh-one-skill">

```bash
npx skills@latest add aminurislamarnob/skills --skill=<name>
```

```bash
npx skills@latest update <name>
```

</canonical-block>

`skills@latest` is the pinned spelling everywhere.

## The two routes are exclusive

The plugin is a managed, read-only bundle you subscribe to. skills.sh writes files you own and edit. Installing both leaves the user with every skill twice: always say "pick one".
