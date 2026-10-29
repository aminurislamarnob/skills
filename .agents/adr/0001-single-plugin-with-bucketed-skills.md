# Ship one Claude Code plugin with bucketed skills, not one plugin per skill

Until October 2026 this repo was a marketplace of four plugins (`plugin-docs`, `wp-worktree`, `browser-walkthrough`, `feature-video`), each a folder under `plugins/` with its own `.claude-plugin/plugin.json` and a single skill under `skills/`. Each skill was installed, versioned and updated on its own.

We restructured to match [mattpocock/skills](https://github.com/mattpocock/skills): **one plugin** (`aiarnob-skills`) whose `plugin.json` lists the shipped skills explicitly, skills grouped in **bucket folders** under `skills/`, one marketplace entry with `source: "./"`, changeset-driven releases, a docs page per skill, and `agents/openai.yaml` beside each `SKILL.md` so the same tree installs into Codex and other Agent-Skills harnesses via `npx skills add`.

## Why

- **One install, one version.** Users subscribe to the set once (`/plugin install aiarnob-skills@aminurislamarnob`) and get every new skill on update, instead of discovering and installing each plugin by name. The skills are small and belong together; four install commands for four skills was friction with no benefit.
- **Buckets express promotion.** `wordpress/` and `browser/` are shipped; `in-progress/` and `deprecated/` (created when needed) are not, and the `skills` array in `plugin.json` is the single place that says so. A per-skill plugin layout had no home for a draft.
- **Portable skills.** A plain `skills/<bucket>/<name>/SKILL.md` tree is what `skills.sh` and Codex discover, so the same files serve harnesses other than Claude Code without a second copy.
- **Release discipline.** Changesets give a CHANGELOG and a version bump for free, and keep `plugin.json`'s `version` (which Claude uses to offer updates) honest via `scripts/sync-plugin-version.mjs`.

## Consequences

- **Old install names stop working.** `plugin-docs@aminurislamarnob-plugins` and the other three no longer exist; the marketplace is now `aminurislamarnob` and the plugin `aiarnob-skills`. Anyone who installed the old plugins re-adds the marketplace and installs the new plugin once. The README documents this.
- **Everything or nothing.** A user who wants only `wp-worktree` still installs all four skills. Skills are cheap when idle (a one-line description in context until invoked), so this is acceptable; if it stops being so, split a bucket into its own plugin rather than returning to per-skill plugins.
- **`${CLAUDE_PLUGIN_ROOT}` paths encode the bucket.** The one such path (in `wp-worktree`) was updated; `AGENTS.md` tells maintainers to grep for it after any move.
- **Codex plugin deferred.** Codex's `.codex-plugin/plugin.json` takes a single skills path and discovers recursively, so it cannot express "promoted buckets only". `npx skills add` covers Codex today; a native Codex plugin waits until `skills/` holds only promoted skills or Codex supports an include-list.

## Update, 2026-10-29: Codex, Copilot and Gemini

The "Codex plugin deferred" consequence above no longer holds. Codex's plugin loader accepts a `skills` array and falls back to `.claude-plugin/` when there is no `.codex-plugin/`, and GitHub Copilot's CLI reads the same two files. So the one `.claude-plugin/plugin.json` + `marketplace.json` pair is the manifest for Claude Code, Codex and Copilot, with nothing extra to keep in sync. Gemini CLI reads neither; it installs a folder of skills with `gemini skills install --path`, one call per promoted bucket, which is exactly why the buckets hold only promoted skills.

Verified 2026-10-29 against this repo: Claude Code and Copilot CLI 1.0.105 each install `aiarnob-skills@aminurislamarnob` with all five skills. The wording for every route lives in [.agents/install-block.md](../install-block.md).
