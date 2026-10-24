---
name: wp-worktree
description: "Make WordPress local development environments compatible with git worktrees and concurrent AI agents (Claude Code, Cursor, Antigravity) on Laravel Herd. Use when running multiple git worktrees in parallel, spinning up isolated WordPress sites per worktree, cloning databases for safe migrations, or adopting Claude Code .claude/worktrees sessions."
compatibility: "Targets WordPress with Laravel Herd on macOS. Requires git, bash, WP-CLI, and Herd."
---

# WP Worktree (Multi-Agent Herd Orchestrator)

Orchestrate isolated, fully functioning WordPress development sites for multiple git worktrees and concurrent AI agent sessions using Laravel Herd.

## When to use

Use this skill when:
- An AI agent (Claude Code, Cursor, Antigravity) is assigned to work in a separate git worktree or creates `.claude/worktrees/*`.
- A developer wants to run multiple git worktrees in parallel without port, domain, database, or plugin collisions.
- Running tests, migrations, or database changes on a branch that must not pollute or break the parent site.
- An agent needs native WP-CLI commands (`wp plugin`, `wp option`, `wp eval`) to operate against an isolated worktree.

## Key Capabilities

1. **Dual Topology Support**: Works seamlessly on both **plugin/theme repositories** (nested inside a WordPress site) and **full WordPress site repositories**.
2. **Ephemeral Herd Isolation**: Provisions a distinct, locally trusted HTTPS domain (e.g. `https://<site>--<worktree>.test`) per worktree via `herd link` and `herd secure`.
3. **Database Branching**: Automatically clones the parent database (or shares when specified), isolating schema changes and option modifications per agent session.
4. **Transparent WP-CLI**: Configures `wp-cli.local.yml` inside the worktree so standard `wp` commands target the isolated environment without manual `--path` arguments.
5. **Git Guardrails**: Silently adds ephemeral worktree metadata to `.git/info/exclude` to guarantee clean commits and prevent repository pollution.

## CLI Quick Reference

The companion script `wp-worktree` can be executed directly from PATH or via `${CLAUDE_PLUGIN_ROOT}/skills/wp-worktree/scripts/wp-worktree.sh`:

```bash
# Create a new git worktree + provision Herd site + clone DB
wp-worktree create <name> [--from=<base>] [--db=clone|shared]

# Adopt the current directory (e.g. inside a Claude .claude/worktrees/ session)
wp-worktree setup [--name=<name>] [--db=clone|shared]

# List active worktrees, domains, and databases
wp-worktree list

# Inspect URL and health of the active worktree
wp-worktree status [name]
wp-worktree url [name]

# Teardown Herd site, drop cloned DB, and remove worktree
wp-worktree remove <name> [--keep-db] [--keep-worktree]
```

## Procedure

### Branch 1: Starting a New Agent Session in a Fresh Worktree

When starting a task that should be isolated in a new branch:

1. **Verify Context**: Run `git status` to ensure working directory is clean.
2. **Provision Worktree**:
   ```bash
   wp-worktree create <feature-name>
   ```
   *Completion Criterion*: The command outputs a green confirmation banner showing the live HTTPS URL (e.g. `https://site--feature-name.test`), cloned database, and worktree path.
3. **Switch to Worktree**:
   ```bash
   cd <worktree-path>
   ```
4. **Verify Health**:
   ```bash
   wp-worktree status
   wp core is-installed
   ```

### Branch 2: Adopting an Existing Agent Worktree (Claude Code / Antigravity)

When Claude Code or Antigravity spawns an agent session inside an existing worktree (such as `.claude/worktrees/agent-xyz`):

1. **Navigate to the Worktree Directory**:
   ```bash
   cd <path-to-agent-worktree>
   ```
2. **Run Worktree Setup**:
   ```bash
   wp-worktree setup
   ```
   *Completion Criterion*: The script automatically discovers the parent WordPress install, generates the ephemeral core link, secures the `.test` domain, clones the parent database, and drops `wp-cli.local.yml`.
3. **Verify Environment**:
   ```bash
   curl -k -IL "$(wp-worktree url)"
   wp option get siteurl
   ```

### Branch 3: Verification During Development

Inside any active worktree:
- **Run WP-CLI**: Execute `wp` commands as normal:
  ```bash
  wp plugin status
  wp db query "SELECT count(*) FROM wp_posts;"
  ```
- **Live Browser Preview**: Open `$(wp-worktree url)` or open Herd Studio.
- **Log Inspection**: Check `wp-content/debug.log` in the ephemeral site (`~/.herd-worktrees/<site>--<name>/wp-content/debug.log`).

### Branch 4: Teardown and Cleanup

When the feature is merged or the agent session completes:

1. **Run Teardown**:
   ```bash
   wp-worktree remove <worktree-name>
   ```
   *Completion Criterion*: Herd link is unlinked, SSL certificate is uninstalled, cloned MySQL database is dropped, and the ephemeral site folder is cleaned up.
2. **Confirm Clean Registry**:
   ```bash
   wp-worktree list
   ```

## Guardrails

- **Never commit worktree metadata**: The script automatically appends `wp-cli.local.yml` and `.worktree-meta.json` to `.git/info/exclude`. Do not stage or commit these files.
- **Always use cloned DB for destructive tests**: If the task involves database migrations, WooCommerce updates, or deleting records, ensure `--db=clone` (the default) is active.
- **SSL Verification in curl/node**: Herd uses local certificates signed by Herd CA. Always pass `-k` (in curl) or `NODE_TLS_REJECT_UNAUTHORIZED=0` when making HTTP requests against `.test` domains from automated test runners.

## Progressive Disclosure

For architectural deep-dives and integrations, consult:
- [Architecture & Mechanics](references/architecture.md): Symlink mapping, dynamic `wp-config.php`, and database isolation details.
- [Claude Code Integration](references/claude-code-workflows.md): Running multi-agent parallel sessions with Claude Code.
- [Troubleshooting Guide](references/troubleshooting.md): Resolving database access, Herd socket, and SSL issues.
