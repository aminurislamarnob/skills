Skills are organized into bucket folders under `skills/`:

- `wordpress/` — WordPress plugin work: user docs, per-worktree dev sites
- `browser/` — run a feature in a real browser and turn the run into a deliverable (walkthrough page, video)
- `in-progress/` — drafts not yet ready to ship (create when needed)
- `deprecated/` — no longer used (create when needed)

Every skill in `wordpress/` or `browser/` (the **promoted** buckets) must have a reference in the top-level `README.md` and an entry in `.claude-plugin/plugin.json`'s `skills` array (the Claude Code plugin ships exactly the promoted set). Skills in `in-progress/` and `deprecated/` must not appear in either.

The repo is also its own single-plugin Claude Code marketplace: `.claude-plugin/marketplace.json` lists the one `aminurislamarnob-skills` plugin. Releases go through changesets: every user-visible change gets a `.changeset/*.md`, and the release workflow opens a version PR. `.claude-plugin/plugin.json`'s `version` must equal `package.json`'s — Claude uses the plugin `version` to decide when installed users see an update — and `scripts/sync-plugin-version.mjs` copies it across after `changeset version`. Run `claude plugin validate . --strict` after touching either manifest. Why one plugin with bucketed skills, rather than one plugin per skill, lives in [.agents/adr/0001-single-plugin-with-bucketed-skills.md](./.agents/adr/0001-single-plugin-with-bucketed-skills.md).

Each skill entry in the top-level `README.md` must link the skill name to its `SKILL.md`.

Each bucket folder has a `README.md` that lists every skill in the bucket with a one-line description, with the skill name linked to its `SKILL.md`. The promoted buckets' `README.md`s and the top-level `README.md` group entries into **User-invoked** and **Model-invoked**; a group with no skills is omitted.

Skills in the promoted buckets also have a human-facing docs page at `docs/<bucket>/<skill-name>.md` (the docs tree mirrors the promoted bucket folders under `skills/`). When you add, rename, or change the behaviour of a promoted skill, create or re-sync its docs page following [.agents/writing-docs.md](./.agents/writing-docs.md). Skills in `in-progress/` and `deprecated/` get **no** docs page.

Every `SKILL.md` is either user-invoked (`disable-model-invocation: true` plus `policy.allow_implicit_invocation: false` in `agents/openai.yaml`, reachable only by the human) or model-invoked (model- or user-reachable). See [.agents/invocation.md](./.agents/invocation.md).

A skill's scripts and reference files live inside the skill's own folder and are referenced relative to it (`scripts/…`, `references/…`, or "this skill's base directory"), so a skill can move between buckets without edits. The one exception is a `${CLAUDE_PLUGIN_ROOT}` path, which encodes the bucket; grep for it after a move.

Claude Code loads this file through `.claude/CLAUDE.md`, which is a one-line `@../AGENTS.md` import; a `CLAUDE.md` at the repo root would trip `claude plugin validate --strict`, so keep the rules here.

To (re)link every skill into the local harness skill directories (`~/.claude/skills`, `~/.agents/skills`), run `scripts/link-skills.sh`. Each entry is a symlink into this repo, so a `git pull` keeps installed skills current; re-run the script after adding, removing, or renaming a skill.
