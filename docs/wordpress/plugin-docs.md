Quickstart:

```bash
npx skills add aminurislamarnob/claude-plugins --skill=plugin-docs
```

Or, as part of the Claude Code plugin: `/plugin install aiarnob-skills@aminurislamarnob`.

[Source](../../skills/wordpress/plugin-docs/SKILL.md)

## What it does

`plugin-docs` writes client-facing documentation for a WordPress plugin: one MDX page per feature area, a `meta.json` sidebar, and screenshots of realistic data captured from a running site, in the format of the [StoreSuite docs](https://storesuite.dev/docs).

Every page is grounded twice, in the code (what the feature really does) and in the running site (what the screen really says), and no label appears in a page unless it was copied from the live screen. Screenshots show a believable site, never test fixtures.

## When to reach for it

Type `/plugin-docs`, or the agent reaches for it automatically when asked to write, update, or re-screenshot a plugin's user docs, help pages, or knowledge base.

Reach for it when a plugin needs docs a site owner can follow, or existing docs need a new page or fresh screenshots. For proof that a change works, rather than docs on how to use it, use [browser-walkthrough](../browser/browser-walkthrough.md).

## Before you start

- The site running with the plugin active.
- An administrator login in `WP_BASE_URL`, `WP_USERNAME` and `WP_PASSWORD` (or in the project's gitignored e2e `.env`); the capture script logs in with it.
- Node.js with Playwright and Chromium where Claude will run it: `npm i -D playwright && npx playwright install chromium`.
- WP-CLI, for seeding demo content.

## The page map

The leading idea is the **page map**: the agreed list of pages, one per user-visible feature area, settled with you before any page is written. A full set is an introduction, installation, one page per feature, settings when settings exist, and an FAQ last. For an update, only the pages that changed are touched.

From there Claude reads the code and the live screen for each page, seeds realistic content with WP-CLI and keeps a list of what it created, captures every screenshot with the bundled `capture.mjs`, looks at each one and retakes bad ones, writes the pages, and checks that every bold label is on screen, every image exists, and every link resolves.

You get the MDX pages, `meta.json`, images in `public/docs/images/`, and a list of seeded content you can ask Claude to remove.

## Tips

- Say where the docs live the first time; Claude asks if it can't tell.
- For a WordPress.org plugin, Claude adds the docs folder to `.distignore` so screenshots stay out of the zip.
- Ask for "the Settings page screenshots again" to retake one page without rewriting the rest.

## Where it fits

A reach-for-it-anytime standalone, usually the last step before a release. Its sibling is [wp-worktree](./wp-worktree.md), because docs are best captured on a worktree site whose seeded demo content can't pollute your main install. The whole set is in the [README](../../README.md#reference).
