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

### browser-walkthrough

Checks a feature or PR end to end in your real Chrome (Claude in Chrome),
screenshots every step, and publishes a private walkthrough page (an Artifact)
with a short description per step and a list of what the run found.

Install in Claude Code:
```
/plugin install browser-walkthrough@aminurislamarnob-plugins
```

Ask Claude to:
- "Check PR #63 on the real browser, screenshot each step, and make an artifact with a short description for each"
- "Verify the refund flow in Chrome and give me a walkthrough page"

Needs:
- the Claude in Chrome extension, connected to this session
- a running site (local or staging) with test-mode credentials for any payment provider
- Python 3, for building the page

### feature-video

Records a feature working in a real browser (Playwright, headed Chrome, with a
visible cursor), edits the takes into a captioned walkthrough video with
[HyperFrames](https://hyperframes.heygen.com), and narrates it with an
ElevenLabs voice, one line per on-screen step.

Install in Claude Code:
```
/plugin install feature-video@aminurislamarnob-plugins
```

Ask Claude to:
- "Make a screen recording of the full checkout flow with HyperFrames"
- "Record the current changes working in the browser and add an ElevenLabs voiceover"

Needs:
- Node.js 22+, FFmpeg, and [Playwright](https://playwright.dev) with Google Chrome or Chromium (`npm i -D playwright`)
- HyperFrames (`npx hyperframes`)
- the ElevenLabs connector with credits, for the voiceover (about two credits per character of script)
- WP-CLI and `WP_PATH`, when takes log in as WordPress users

## How to use each skill

Every skill starts the same way: install its plugin (see [Install](#install)),
then ask Claude in plain words, or type its name as a slash command
(`/plugin-docs`, `/wp-worktree`, `/browser-walkthrough`, `/feature-video`).

### plugin-docs: write user docs with real screenshots

**Use it when** a plugin needs client-facing docs, or existing docs need new
pages or fresh screenshots.

**Before you start**
- Have the site running with the plugin active.
- Export an administrator login: `WP_BASE_URL`, `WP_USERNAME`, `WP_PASSWORD`
  (or keep them in the project's gitignored e2e `.env`).
- Install Playwright where Claude will run it: `npm i -D playwright && npx playwright install chromium`.

**Ask**
- "Write the user docs for this plugin"
- "Add a docs page for the new Coupons screen, with screenshots"
- "Retake the screenshots for the Settings page"

**What Claude does**
1. Agrees the page map with you (intro, installation, one page per feature, settings, FAQ).
2. Reads the code and the live screen for each page, so labels match the UI exactly.
3. Seeds realistic demo content with WP-CLI and keeps a list of what it created.
4. Captures every screenshot with `capture.mjs`, looks at each one, and retakes bad ones.
5. Writes MDX pages and `meta.json`, then checks labels, images and links.

**You get** one MDX page per feature, a `meta.json` sidebar and images in
`public/docs/images/`, plus a list of seeded content you can ask Claude to remove.

**Tips**
- Say where the docs live the first time; Claude asks if it can't tell.
- For a WordPress.org plugin, Claude adds the docs folder to `.distignore`.

### wp-worktree: one isolated WordPress site per git worktree

**Use it when** you, or several AI agents, work on more than one branch at
the same time and each needs its own site and database.

**Before you start**
- macOS with Laravel Herd, Git, Bash and WP-CLI.
- Run it from a plugin/theme repo inside a WordPress site, or a full-site repo.

**Ask**
- "Create a new worktree for feat-cart and spin up the WordPress environment"
- "Adopt this worktree session with wp-worktree"
- "Tear down the feat-cart worktree"

**What Claude does**
- **Create** (`wp-worktree create <name>`): makes the git worktree, links it in Herd at
  `https://<site>--<worktree>.test` with HTTPS, clones the database, and writes
  `wp-cli.local.yml` so plain `wp` commands hit the worktree's site.
- **Adopt:** runs `wp-worktree setup` inside an existing agent worktree
  (for example `.claude/worktrees/agent-xyz`).
- **Remove** (`wp-worktree remove <name>`): unlinks the site, drops the cloned database and cleans up.

**You get** a working site per branch whose database changes never touch the
parent site. `wp-worktree list` shows them all.

**Tips**
- Keep the default cloned database for migrations and destructive tests.
- Use `curl -k` (or `NODE_TLS_REJECT_UNAUTHORIZED=0`) against `.test` domains from scripts.
- Worktree files are added to `.git/info/exclude` automatically; don't commit them.

### browser-walkthrough: check a feature in the real browser, publish a walkthrough

**Use it when** you want proof a feature or PR works: every step tried in the
browser, a screenshot of each, and a shareable page to review or hand on.

**Before you start**
- Install the Claude in Chrome extension and connect it to the session.
  If several browsers are connected, Claude asks which one to use.
- Have the site running, with test-mode keys for any payment provider.
- Start anything the flow needs, such as a webhook listener (`stripe listen …`),
  or let Claude start it.

**Ask**
- "Check PR #63 on the real browser, take a screenshot of each step and make an artifact with a short description for each"
- "Verify the refund flow in Chrome and give me a walkthrough page"

**What Claude does**
1. Reads the PR, spec and diff, and lists the steps, including declines and errors.
2. Runs each step in a tab of your Chrome and saves a screenshot. Unrelated
   notices are hidden, and keys and emails are masked.
3. Checks the server after every change (database, WP-CLI, Stripe CLI), so a
   screenshot never claims something the server disagrees with.
4. Looks at every shot, retakes bad ones, and notes real bugs as findings.
5. Publishes a private Artifact page: numbered steps, a caption each, and the findings.

**You get** a private link to the walkthrough page, the findings ranked by
severity, and a list of what the run left on the site (test orders, refunds).
The page is private until you share it from its Share menu.

**Tips**
- Chrome tabs open in a group Claude manages; your other tabs are left alone.
- If a browser dialog (OK/Cancel) appears and Chrome stops responding, click it;
  Claude pre-answers dialogs for the steps it knows about.
- Ask for an update after a fix ("retake step 18 and republish"); the link stays the same.

### feature-video: record a narrated walkthrough video

**Use it when** you want a video of the change working, for a client, a PR or
a demo, optionally with a voiceover.

**Before you start**
- Node.js 22+, FFmpeg, Google Chrome (or Chromium) and Playwright (`npm i -D playwright`).
- HyperFrames runs through `npx hyperframes`; `npx hyperframes doctor` checks the setup.
- For WordPress logins, set `WP_PATH` to the site's WordPress root; Claude
  signs in with WP-CLI, so no passwords are needed.
- For the voiceover, connect the ElevenLabs connector and have credits:
  about two credits per character of script (a 4–5 minute video is about 5,000).

**Ask**
- "Make a screen recording of the full checkout flow using HyperFrames"
- "Record the current changes working in the browser and add an ElevenLabs voiceover"
- "Re-record the refund part only" (after a first run)

**What Claude does**
1. Reads the change and writes a shot list: chapters, takes (one per role), steps.
2. Writes a scenario and records it with `record.cjs` in a visible Chrome window,
   with a drawn cursor and click ripples, marking the moment each step appears.
3. Checks the server state and one frame per step, and re-records anything wrong.
4. Builds the film with `build_video.py`: intro, chapter cards, captions timed
   to the footage, a chapter rail and an outro. It runs `hyperframes check` and
   snapshots, and fixes captions that lag the screen.
5. Writes one voice line per step, sized to fit before the next step
   (`--plan`), picks a voice, generates the lines with ElevenLabs and places them.
6. Renders the MP4 and verifies its length, its frames and that the voice is audible.

**You get** a 1080p MP4 (with narration when asked), the HyperFrames project
for later edits, the raw takes, and a note of anything still missing.

**Tips**
- A Chrome window opens on your screen while it records; let it run.
- The run creates real test data (orders, refunds); Claude lists it at the end.
- If the ElevenLabs account runs out of credits, the video still renders with
  the lines it has; ask Claude to add the missing ones after topping up.
- To change wording or timing later, ask for the edit; Claude rebuilds and
  renders from the saved project without recording again.
