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
