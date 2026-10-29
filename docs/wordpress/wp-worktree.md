Quickstart:

```bash
npx skills add aminurislamarnob/claude-plugins --skill=wp-worktree
```

Or, as part of the Claude Code plugin: `/plugin install aiarnob-skills@aminurislamarnob`.

[Source](../../skills/wordpress/wp-worktree/SKILL.md)

## What it does

`wp-worktree` gives every git worktree its own working WordPress site on Laravel Herd: a trusted HTTPS domain at `https://<site>--<worktree>.test`, a cloned database, and a `wp-cli.local.yml` so plain `wp` commands target that site without `--path`.

A worktree's database is a clone, so a migration, a WooCommerce update, or a destructive test on one branch never touches the parent site or another agent's branch. It works whether the repo is a plugin or theme nested inside a WordPress install, or a whole site.

## When to reach for it

Type `/wp-worktree`, or the agent reaches for it automatically when running several git worktrees in parallel, spinning up an isolated site per worktree, cloning a database before a migration, or adopting a Claude Code `.claude/worktrees` session.

Reach for it the moment a second branch needs its own site. It is an environment skill; it does not test or document anything itself.

## Before you start

- macOS with [Laravel Herd](https://herd.laravel.com/), which bundles MySQL or MariaDB.
- Git, Bash and WP-CLI (`wp`).
- Run it from a plugin or theme repo inside a WordPress site, or from a full-site repo.

## One site per worktree

Three moves cover the lifecycle. **Create** (`wp-worktree create <name>`) makes the git worktree, links and secures it in Herd, clones the database and writes the WP-CLI config. **Adopt** (`wp-worktree setup`) does the same for a worktree that already exists, such as one an agent session was spawned into. **Remove** (`wp-worktree remove <name>`) unlinks the site, drops the cloned database and cleans up. `wp-worktree list` shows what is active.

The companion script runs from PATH or from the skill's `scripts/` folder, so you can use it outside an agent session too.

## Tips

- Keep the default cloned database for migrations and destructive tests; pass `--db=shared` only when the branch must see live data.
- Use `curl -k` (or `NODE_TLS_REJECT_UNAUTHORIZED=0`) against `.test` domains from scripts; Herd signs them with its own CA.
- Worktree metadata is added to `.git/info/exclude` automatically; don't commit it.

## Where it fits

A run-first setup: the other skills work on whatever site is running, and this one makes sure each branch has its own. [plugin-docs](./plugin-docs.md) and [browser-walkthrough](../browser/browser-walkthrough.md) both seed and change data, which is exactly what a cloned database is for. The whole set is in the [README](../../README.md#reference).
