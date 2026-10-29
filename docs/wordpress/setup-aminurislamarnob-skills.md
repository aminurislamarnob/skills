Quickstart:

```bash
npx skills add aminurislamarnob/claude-plugins --skill=setup-aminurislamarnob-skills
```

Or, as part of the Claude Code plugin: `/plugin install aminurislamarnob-skills@aminurislamarnob`.

[Source](../../skills/wordpress/setup-aminurislamarnob-skills/SKILL.md)

## What it does

`setup-aminurislamarnob-skills` teaches one repo how the other skills should behave in it: which local WordPress site the plugin runs on, how to log in to it, where the client docs live, and which tools are installed. It records the answers as **config** the other skills read.

It writes config, it does not hard-code behaviour. The answers are discovered from the real repo and machine (the `wp-load.php` above the repo, `wp option get siteurl`, an existing e2e env file, an existing docs tree, `which ffmpeg`) and confirmed with you rather than guessed. No password is ever written; the config names the file that holds it.

## When to reach for it

You invoke this by typing `/setup-aminurislamarnob-skills` — the agent won't reach for it on its own.

Reach for it **once per repo, before the first use of any other skill**. If [plugin-docs](./plugin-docs.md) asks where the docs go, or [browser-walkthrough](../browser/browser-walkthrough.md) asks which site to open, it hasn't been run here yet. Re-run it only when the site or the docs move, or to re-check tooling; day-to-day tweaks are edits to `docs/agents/*.md`.

## The three sections

It leads each with a recommended answer you can accept in a word, and skips what it can already infer or what no installed skill needs:

- **WordPress site** — the URL, the WordPress root, and the login source: a gitignored env file with `WP_BASE_URL`, `WP_USERNAME` and `WP_PASSWORD`, or WP-CLI minting a cookie for a named administrator. Plus the other roles a run may need and the services to start first (a webhook listener, a queue).
- **Docs location** — only when `plugin-docs` is installed: the folder with `content/docs/`, the images folder, the build command, and whether the plugin ships to WordPress.org (then the docs go in `.distignore`).
- **Tooling** — nothing to answer: a table of what is present and what is missing (WP-CLI, Herd, Node 22+, FFmpeg, Playwright, HyperFrames, `gh`), with the install command for each gap. It installs nothing.

The output is `docs/agents/wordpress-site.md`, `docs/agents/plugin-docs.md` when `plugin-docs` is installed, and an `## Agent skills` block pointing to them in whichever of `CLAUDE.md` / `AGENTS.md` the repo already uses.

## It's working if

- `wordpress-site.md` lands under `docs/agents/`, with a URL that answers and a root that holds `wp-load.php`.
- An `## Agent skills` section appears in your `CLAUDE.md` or `AGENTS.md`.
- Afterwards, `plugin-docs` and `browser-walkthrough` open the right site and log in without asking.

## Where it fits

A **run-once setup**, the foundation the other skills stand on. Its neighbours are the skills that read what it writes: [plugin-docs](./plugin-docs.md), because it writes into the docs location configured here, and [browser-walkthrough](../browser/browser-walkthrough.md) and [feature-video](../browser/feature-video.md), because they open and log in to the site configured here. Run it first; everything downstream assumes it has. The whole set is in the [README](../../README.md#reference).
