---
name: plugin-docs
description: Write client-facing documentation for a WordPress plugin, with real screenshots captured from a running site, in the StoreSuite docs format (MDX pages + meta.json + images). Use when asked to write, update, or screenshot a plugin's user docs, help pages, or knowledge base.
---

# Plugin docs

Client-facing docs explain the plugin to a **site owner**: someone who clicks, never reads code. Every page is grounded twice, in the code (what the feature really does) and in the running site (what the screen really says), and illustrated with real screenshots of realistic data.

The reference implementation is the [StoreSuite docs](https://storesuite.dev/docs); three of its pages are bundled in [examples/](examples/) (`index.mdx`, `coupons.mdx`, `settings.mdx`). Read them before writing your first page in a session and match their voice exactly. Writing rules live in [STYLE.md](STYLE.md). Read it before drafting.

## 1. Scope

- **Target**: where the docs go. If the plugin has no docs location yet, ask the user (one question, with your recommendation). Output layout:
  - `<docs>/content/docs/<slug>.mdx`: one page per feature area
  - `<docs>/content/docs/meta.json`: `{ "title": "Documentation", "root": true, "pages": [...] }` sidebar order
  - `<docs>/public/docs/images/<name>.jpg`: screenshots, referenced as `/docs/images/<name>.jpg`

  When the docs live inside a plugin repo that deploys to WordPress.org, add the docs folder to `.distignore` so the screenshots don't ship in the plugin zip.
- **Page map**: list the feature areas from the plugin's admin menus, settings tabs, shortcodes, blocks, widgets and frontend views. A full set always has `index` (introduction), `installation`, one page per feature area, `settings` if settings exist, and `faq` last. Show the user the page map before writing when docs are created from scratch. For an update, touch only the pages that changed.

Done when every user-visible feature maps to exactly one page.

## 2. Research each page

For the page's feature, read the code that renders it (admin view templates, settings registration, shortcode attributes, frontend templates) and open the screen on the site. Collect:

- every label, button, column, tab and field **exactly as rendered** (copy it from the page; `mcp__claude-in-chrome__get_page_text` or the screenshot works)
- defaults, required fields, what saving does, where the result appears on the frontend
- requirements and gotchas the UI doesn't say (permalinks, caching, theme overrides)

Done when every field on the screen has a known meaning and default. If code and UI disagree, the UI wins for labels and the code wins for behaviour. Flag real bugs to the user rather than documenting them.

## 3. Seed realistic data

Screenshots show a believable live site, not test fixtures: real-sounding job titles/products/names, filled categories, varied statuses, 8–12 rows per list.

- Check what exists first (`wp post list`, `wp term list`). Leftover test data (random suffixes like `Support Agent ztptbc`, `e2e-admin` authors, `Lorem ipsum`) must not appear in a shot: trash it, filter it out, or hide it with `hide`.
- Create missing content with WP-CLI (run from the WordPress root) or REST. Record every ID you create in the scratchpad, and offer the user its removal at the end.
- Change plugin settings only to show a state, and restore them after the shot.

## 4. Capture screenshots

Use `capture.mjs` from this skill's base directory (the path this skill was loaded from). It logs in, renders at 2× device scale, hides admin notices, and fails on error pages. Run it from a directory where `playwright` resolves: the plugin root, if it has Playwright; otherwise `npm i -D playwright && npx playwright install chromium` in the scratchpad.

It reads the site and an administrator login from `WP_BASE_URL`, `WP_USERNAME` and `WP_PASSWORD`. Take them from the project's e2e config if it has one (often a gitignored `.env`); otherwise ask the user. Keep credentials out of the docs and out of git.

```bash
set -a; . tests/e2e/.env; set +a   # or export the three variables
node <skill-dir>/capture.mjs <scratchpad>/shots.json <scratchpad>/img
```

The shot-spec fields are documented at the top of `capture.mjs`. Choosing shots:

- **One screenshot per screen** a reader lands on: each list, each form, each settings tab, each frontend view. Place it directly under the heading that discusses it.
- **Full screens** (default, 1800px viewport) for admin pages, so the WordPress menu shows where the screen lives. **Element crops** (`selector`, `format: "png"`) for small UI pieces: a modal, a dropdown, a single widget.
- **Frontend** shots with `"loggedIn": false`, in the theme the site actually uses.
- **Editor views** (block editor, Elementor) show the plugin's output at least **1150px wide** inside the canvas: a `[1920, 1200]` viewport, plus a temporary draft page that lifts the theme's content width: the block set to `"align":"wide"`, or an Elementor page on the `elementor_canvas` template with a 1200px boxed container (`elementor_header_footer` draws a bare fallback header on block themes). Select the block/widget with `eval` so its settings panel shows.
- Name files `<area>-<screen>` in kebab-case: `jobs-list`, `job-form`, `settings-appearance`, `listing-design-v2`.

Then **look at every image** with Read. A shot is done only when it shows the intended screen, with realistic data, no notices, no error/empty state (unless documenting one), and no test-data leftovers. Recapture until all pass, then copy them into `<docs>/public/docs/images/`.

## 5. Write

Draft each page per [STYLE.md](STYLE.md), using only labels collected in step 2. Add new pages to `meta.json` in reading order, and add the page to the intro's "What you get" list.

## 6. Verify

Re-read each page against its screenshots and the live screen:

- every **bold** UI label appears verbatim on screen
- every image path exists in `public/docs/images/`
- every `/docs/<slug>#anchor` link resolves to a page and heading
- the frontmatter `description` is one sentence

If the docs site has a build (StoreSuite's is `pnpm build`), run it and confirm it passes. Report the pages written, screenshots captured, and the seeded content still on the site.
