# Claude Code plugins

Claude Code plugins for WordPress plugin development.

## Install

In Claude Code:

```
/plugin marketplace add aminurislamarnob/claude-plugins
/plugin install plugin-docs@aminurislamarnob-plugins
```

Update later with `/plugin marketplace update aminurislamarnob-plugins`.

To offer it to everyone working in a repo, commit this to the repo's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "aminurislamarnob-plugins": {
      "source": { "source": "github", "repo": "aminurislamarnob/claude-plugins" }
    }
  },
  "enabledPlugins": {
    "plugin-docs@aminurislamarnob-plugins": true
  }
}
```

## Plugins

### plugin-docs

Writes client-facing docs for a WordPress plugin, in the format of the
[StoreSuite docs](https://storesuite.dev/docs): one MDX page per feature, a
`meta.json` sidebar, and real screenshots of realistic data captured from a
running site.

Ask Claude to "write the user docs for this plugin" (or run `/plugin-docs`).
It maps the pages with you, reads the code and the live screens, seeds demo
content, captures and reviews every screenshot, writes the pages, and checks
labels, images and links.

Needs:

- a running WordPress site with the plugin active, and an administrator login
  (`WP_BASE_URL`, `WP_USERNAME`, `WP_PASSWORD`)
- Node.js with [Playwright](https://playwright.dev) and Chromium
  (`npm i -D playwright && npx playwright install chromium`)
- WP-CLI, for seeding demo content

### wp-worktree

Make WordPress local development environments compatible with git worktrees and concurrent AI agents (Claude Code, Cursor, Antigravity) on Laravel Herd.

Provisions isolated HTTPS Herd domains (`https://<site>--<worktree>.test`), clones databases so migrations and tests don't collide across parallel agent sessions, and transparently wires `wp` commands inside worktrees.

Install in Claude Code:
```
/plugin install wp-worktree@aminurislamarnob-plugins
```

Ask Claude to:
- "Create a new worktree for feat-cart and spin up the WordPress environment"
- "Adopt this worktree session with wp-worktree"

Needs:
- macOS with [Laravel Herd](https://herd.laravel.com/)
- Git, Bash, and WP-CLI (`wp`)
- MySQL / MariaDB (bundled with Herd)
