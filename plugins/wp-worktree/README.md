# wp-worktree

A Claude Code plugin to make WordPress local development environments compatible with git worktrees and concurrent AI agent sessions using **Laravel Herd**.

## What it does

- **Dual Topology Support**: Works seamlessly on both **plugin/theme repositories** (nested inside a WordPress site) and **full WordPress site repositories**.
- **Ephemeral Herd Domains**: Provisions a distinct, locally trusted HTTPS domain (e.g. `https://<site>--<worktree>.test`) per worktree via `herd link` and `herd secure`.
- **Database Branching**: Automatically clones the parent database (or shares when specified), isolating schema changes and option modifications per agent session.
- **Transparent WP-CLI**: Configures `wp-cli.local.yml` inside the worktree so standard `wp` commands target the isolated environment without manual `--path` arguments.
- **Git Guardrails**: Silently adds ephemeral worktree metadata to `.git/info/exclude` to guarantee clean commits and prevent repository pollution.

## Install

In Claude Code:

```
/plugin marketplace add aminurislamarnob/claude-plugins
/plugin install wp-worktree@aminurislamarnob-plugins
```

To enable it for everyone working in a repository, add this to `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "aminurislamarnob-plugins": {
      "source": { "source": "github", "repo": "aminurislamarnob/claude-plugins" }
    }
  },
  "enabledPlugins": {
    "wp-worktree@aminurislamarnob-plugins": true
  }
}
```

## Usage

### In Claude Code

Ask Claude to:
- "Create a new worktree for feat-cart and spin up the WordPress environment"
- Or when running inside a Claude worktree session: "Run wp-worktree setup to wire this session to Herd"

### Direct Script Usage

```bash
# Create a new git worktree + provision Herd site + clone DB
wp-worktree create feat-cart [--from=main] [--db=clone|shared]

# Adopt the current directory (e.g. inside a Claude .claude/worktrees/* session)
wp-worktree setup

# Check status and health
wp-worktree status

# Print the active https:// URL
wp-worktree url

# List all active worktrees
wp-worktree list

# Teardown Herd site, drop cloned DB, and remove worktree
wp-worktree remove feat-cart
```

## Requirements

- macOS with [Laravel Herd](https://herd.laravel.com/) (Pro or Free).
- Git, Bash, and WP-CLI (`wp`).
- MySQL / MariaDB (bundled with Herd).
