# aminurislamarnob-skills

A collection of agent skills for WordPress plugin work, shipped as one Claude Code plugin and installable into other harnesses with `npx skills add`.

## Language

**Skill**:
One folder holding a `SKILL.md` (frontmatter `name` + `description`, then the procedure), optional `scripts/`, `references/` and `examples/`, and an `agents/openai.yaml` for Codex. Reached by typing `/<name>` or, when model-invoked, by the agent on its own.
_Avoid_: command, plugin (a plugin is the bundle, see below)

**Bucket**:
A folder under `skills/` that groups skills by theme. `wordpress/` and `browser/` are **promoted**; `in-progress/` and `deprecated/` are not.

**Promoted**:
Shipped in the plugin, listed in the top-level README, and given a docs page. Exactly the skills named in `.claude-plugin/plugin.json`'s `skills` array.

**Plugin**:
The one Claude Code bundle, `aminurislamarnob-skills`, defined by `.claude-plugin/plugin.json`. It carries the promoted skills and a `version` Claude uses to offer updates.

**Marketplace**:
The catalogue Claude Code reads to find plugins. This repo is its own single-plugin marketplace, `aminurislamarnob`, defined by `.claude-plugin/marketplace.json`.

**Docs page**:
The human-facing page at `docs/<bucket>/<skill>.md` that says what a skill does, when to reach for it, and what to have ready. Not a copy of `SKILL.md`.

**Walkthrough** (`browser-walkthrough`):
One honest run of a feature in the user's own Chrome, recorded as numbered screenshots with a caption each and published as a private Artifact page. A step whose server state disagrees with its screenshot is a **finding**, not a step.

**Take** and **cue** (`feature-video`):
A take is one recorded Playwright session, one per role. A cue is the moment inside a take at which a step is on screen, marked by the recorder and used to time captions and voice lines.

**Page map** (`plugin-docs`):
The agreed list of docs pages, one per user-visible feature area, settled with the user before any page is written.

**Worktree site** (`wp-worktree`):
The isolated Herd site, `https://<site>--<worktree>.test`, with its own cloned database, that backs one git worktree.

## Relationships

- A **Marketplace** lists one **Plugin**
- A **Plugin** ships every **Promoted** **Skill**
- A **Bucket** holds many **Skills**; only promoted buckets' skills are **Promoted**
- Every **Promoted** **Skill** has one **Docs page**
