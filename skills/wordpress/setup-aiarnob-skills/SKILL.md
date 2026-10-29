---
name: setup-aiarnob-skills
description: Configure this repo for the WordPress skills — record the site URL, WordPress root, admin login and docs location, and check the tooling each skill needs. Run once per repo before first use of the other skills.
disable-model-invocation: true
---

# Setup Aminur Islam's Skills

Scaffold the per-repo configuration the skills assume:

- **WordPress site** — the local site the plugin runs on: its URL, WordPress root, and how to log in as an administrator
- **Docs location** — where client-facing docs live (only when `plugin-docs` is installed)
- **Tooling** — which of the tools the skills call are present, and what is missing

This is a prompt-driven skill, not a deterministic script. Explore, present what you found, confirm with the user, then write.

## Process

### 1. Explore

Look at the current repo and machine to understand the starting state. Read whatever exists; don't assume:

- Which of the skills are installed (`plugin-docs`, `wp-worktree`, `browser-walkthrough`, `feature-video` folders beside this one, or in your available skills). A section for an uninstalled skill is skipped.
- `AGENTS.md` and `CLAUDE.md` at the repo root — does either exist? Is there already an `## Agent skills` section in either?
- `docs/agents/` — does this skill's prior output already exist?
- **WordPress root**: walk up from the repo for `wp-load.php` (a plugin or theme repo sits under `wp-content/`); if the repo is a whole site, the root is the repo. Record the absolute path.
- **Site URL**: `wp option get siteurl` from that root; if `wp` is missing, the Herd convention `https://<folder>.test` for a folder under `~/Herd`.
- **Admin login**: a gitignored env file the project already uses for e2e tests (`tests/e2e/.env`, `.env.e2e`, `playwright/.env`) with `WP_BASE_URL`, `WP_USERNAME`, `WP_PASSWORD`; or `wp user list --role=administrator` for a username to mint cookies for with WP-CLI. Never print a password.
- **Docs**: an existing `content/docs/` with `meta.json` and `public/docs/images/` in this repo or a sibling docs repo; a `.distignore`; a docs build command in `package.json`.
- **Tooling**, by running each check and noting present or missing: `wp --version`, `herd --version`, `node --version` (22+), `ffmpeg -version`, `python3 --version`, Playwright (`npx playwright --version` from the repo), HyperFrames (`npx hyperframes doctor`), the `gh` CLI. The Claude in Chrome extension and the ElevenLabs connector cannot be checked from the shell; list them as "confirm in the session".

### 2. Present findings and ask

Summarise what's present and what's missing. Then take the sections in order — one section, one answer, then the next.

Lead each section with the recommended answer so the user can accept it in a word. Give a one-line explainer only when the choice genuinely branches; skip a section entirely when exploration already settled it, or when no installed skill needs it.

**Section A — WordPress site.** Needed by every skill.

> Explainer: `plugin-docs`, `browser-walkthrough` and `feature-video` open the running site and log in as an administrator; `wp-worktree` clones its database. They need to know the URL, the WordPress root, and where the login comes from.

Propose what exploration found: the root path, the URL, and the login source. The login source is one of:

- **Env file** — a gitignored file with `WP_BASE_URL`, `WP_USERNAME`, `WP_PASSWORD` (recommended when the project already has one)
- **WP-CLI** — no password; skills mint an auth cookie with `wp eval` for a named administrator
- **Other** — the user describes it in one paragraph

**Section B — Docs location.** Skip entirely if `plugin-docs` isn't installed.

Propose the docs tree exploration found, or ask: the folder that holds `content/docs/`, whether the images folder is `public/docs/images/`, the build command if any, and whether the plugin ships to WordPress.org (then the docs folder belongs in `.distignore`).

**Section C — Tooling.** Nothing to ask. Present the table of present and missing tools with the install command for each missing one (`npm i -D playwright && npx playwright install chromium`, `brew install ffmpeg`, `brew install wp-cli`, Herd from herd.laravel.com). Don't install anything; the user decides.

### 3. Confirm and edit

Show the user a draft of:

- The `## Agent skills` block to add to whichever of `CLAUDE.md` / `AGENTS.md` is being edited (see step 4)
- The contents of `docs/agents/wordpress-site.md` and, when `plugin-docs` is installed, `docs/agents/plugin-docs.md`

Let them edit before writing.

### 4. Write

**Pick the file to edit:**

- If `CLAUDE.md` exists, edit it.
- Else if `AGENTS.md` exists, edit it.
- If neither exists, ask the user which one to create — don't pick for them.

Never create `AGENTS.md` when `CLAUDE.md` already exists (or vice versa) — always edit the one that's already there.

If an `## Agent skills` block already exists in the chosen file, update its contents in place rather than appending a duplicate. Don't overwrite user edits to the surrounding sections.

The block:

```markdown
## Agent skills

### WordPress site

[one-line summary: URL, root, login source]. See `docs/agents/wordpress-site.md`.

### Plugin docs

[one-line summary: where the docs live]. See `docs/agents/plugin-docs.md`.

### Tooling

[one line: what is missing, or "all tools present"]. Checked by `/setup-aiarnob-skills` on <date>.
```

Include the `### Plugin docs` sub-block, and write `docs/agents/plugin-docs.md`, only when `plugin-docs` is installed and Section B ran.

Then write the docs files using the seed templates in this skill folder as a starting point:

- [wordpress-site.md](./wordpress-site.md) — site URL, root, login source, roles
- [plugin-docs.md](./plugin-docs.md) — docs tree, build, distribution

Never write a password into either file; name the env file that holds it.

### 5. Done

Tell the user the setup is complete and which skills will now read from these files. Mention they can edit `docs/agents/*.md` directly later — re-running this skill is only necessary when the site moves, the docs move, or they want to re-check tooling.
