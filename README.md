# Skills for WordPress plugin work

[![skills.sh](https://skills.sh/b/aminurislamarnob/claude-plugins)](https://skills.sh/aminurislamarnob/claude-plugins)

Agent skills I use when building and shipping WordPress plugins: client-facing docs with real screenshots, one isolated Herd site per git worktree, and proof that a change works in a real browser, as a walkthrough page or a narrated video.

They are small, composable, and work in Claude Code, Codex, and any other harness that reads the [Agent Skills](https://skills.sh) format. Hack on them and make them your own.

## Quickstart (30-second setup)

1. Run the skills.sh installer:

```bash
npx skills@latest add aminurislamarnob/claude-plugins
```

2. Pick the skills you want, and which coding agents you want to install them on. **Make sure you select `/setup-aminurislamarnob-skills`**.

3. Run `/setup-aminurislamarnob-skills` in your agent. It will:
   - Find the local WordPress site the plugin runs on (URL, WordPress root) and ask how to log in as an administrator
   - Ask where the client-facing docs live (when you installed `plugin-docs`)
   - Check which tools the skills need are installed (WP-CLI, Herd, Playwright, FFmpeg, HyperFrames) and tell you what's missing

4. Bam - you're ready to go. Ask your agent in plain words ("write the user docs for this plugin"), or type a skill's name as a slash command (`/plugin-docs`, `/wp-worktree`, `/browser-walkthrough`, `/feature-video`).

## Install as a Claude Code plugin

Prefer a plug-and-play install you don't maintain by hand? The skills also ship as a native [Claude Code plugin](https://code.claude.com/docs/en/plugins): a managed, read-only bundle that updates when a new version ships, instead of editable copies in your repo.

Inside Claude Code:

```
/plugin marketplace add aminurislamarnob/claude-plugins
/plugin install aminurislamarnob-skills@aminurislamarnob
```

Or from your shell:

```bash
claude plugin marketplace add aminurislamarnob/claude-plugins
claude plugin install aminurislamarnob-skills@aminurislamarnob
```

Then run `/setup-aminurislamarnob-skills` once per repo, exactly as in the quickstart above.

Update later with `/plugin marketplace update aminurislamarnob`.

To offer the plugin to everyone working in a repo, commit this to the repo's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "aminurislamarnob": {
      "source": { "source": "github", "repo": "aminurislamarnob/claude-plugins" }
    }
  },
  "enabledPlugins": {
    "aminurislamarnob-skills@aminurislamarnob": true
  }
}
```

Two ways to install, two philosophies:

- **[skills.sh](https://skills.sh)** copies the skills into your project so you can hack on them.
- **The plugin** keeps them as a read-only, always-current bundle you don't edit.

> Upgrading from the old per-skill plugins (`plugin-docs@aminurislamarnob-plugins` and friends)? Those names are gone. Add the marketplace and install `aminurislamarnob-skills` once; see [CHANGELOG.md](./CHANGELOG.md).

## Why these skills exist

Shipping a WordPress plugin is more than the code. Each of these skills removes a chore that sits between "it works on my branch" and "the client can use it", and each one ends with something you can hand over.

### The docs are always behind

Client docs explain the plugin to a site owner who clicks and never reads code. They need real screenshots of realistic data, and labels that match the screen exactly. [`plugin-docs`](./skills/wordpress/plugin-docs/SKILL.md) agrees a page map with you, reads the code and the live screens, seeds believable demo content, captures and reviews every screenshot, and writes MDX pages in the [StoreSuite docs](https://storesuite.dev/docs) format.

### Parallel branches fight over one site

Several worktrees, or several agents, pointed at one WordPress install share a database and a domain, so a migration on one branch breaks the other. [`wp-worktree`](./skills/wordpress/wp-worktree/SKILL.md) gives each git worktree its own Laravel Herd site at `https://<site>--<worktree>.test`, a cloned database, and WP-CLI wired so plain `wp` commands hit the right site.

### "It works" needs proof

A diff is not evidence that a feature works. [`browser-walkthrough`](./skills/browser/browser-walkthrough/SKILL.md) runs every step of a change in your real Chrome, screenshots each one, checks the server agrees with the screen, and publishes a private walkthrough page with the findings. [`feature-video`](./skills/browser/feature-video/SKILL.md) records the same kind of run with Playwright, cuts it into a captioned film with [HyperFrames](https://hyperframes.heygen.com), and narrates it with an ElevenLabs voice.

## Reference

Skills split on one axis: who can invoke them. **User-invoked** skills are reachable only when you type them. **Model-invoked** skills can be invoked by you _or_ reached for automatically by the agent when the task fits. Each skill has a docs page saying what to have ready and what you get back.

### WordPress

Skills for the plugin and its development environment. Bucket: [`skills/wordpress`](./skills/wordpress/README.md).

**User-invoked**

- **[setup-aminurislamarnob-skills](./skills/wordpress/setup-aminurislamarnob-skills/SKILL.md)** — Configure this repo for the skills (site URL, WordPress root, admin login, docs location, tooling check). Run once per repo before using the other skills. [Docs](./docs/wordpress/setup-aminurislamarnob-skills.md)

**Model-invoked**

- **[plugin-docs](./skills/wordpress/plugin-docs/SKILL.md)** — Write client-facing docs for a WordPress plugin, with real screenshots captured from a running site, in the StoreSuite docs format (MDX pages, `meta.json`, images). [Docs](./docs/wordpress/plugin-docs.md)
- **[wp-worktree](./skills/wordpress/wp-worktree/SKILL.md)** — One isolated Laravel Herd site, with its own cloned database, per git worktree, so parallel branches and AI agents never collide. [Docs](./docs/wordpress/wp-worktree.md)

### Browser

Skills that run a change in a real browser and turn the run into a deliverable. Bucket: [`skills/browser`](./skills/browser/README.md).

**Model-invoked**

- **[browser-walkthrough](./skills/browser/browser-walkthrough/SKILL.md)** — Check a feature or PR end to end in your real Chrome, screenshot every step, verify the server agrees, and publish a private walkthrough page with findings. [Docs](./docs/browser/browser-walkthrough.md)
- **[feature-video](./skills/browser/feature-video/SKILL.md)** — Record a feature working in a real browser, edit the takes into a captioned walkthrough video with HyperFrames, and narrate it with an ElevenLabs voice. [Docs](./docs/browser/feature-video.md)

## Contributing

`AGENTS.md` holds the repo's rules (buckets, what must be listed where, docs pages, invocation). Every user-visible change gets a changeset (`npx changeset`); the release workflow opens a version PR. Run `claude plugin validate . --strict` after touching a manifest.
