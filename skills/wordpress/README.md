# WordPress

Skills for the plugin and its development environment.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[setup-aiarnob-skills](./setup-aiarnob-skills/SKILL.md)** — Configure a repo for the skills: site URL, WordPress root, admin login, docs location, tooling check. Run once per repo.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the model can reach for them).

- **[plugin-docs](./plugin-docs/SKILL.md)** — Write client-facing docs for a WordPress plugin, with real screenshots captured from a running site, in the StoreSuite docs format (MDX pages, `meta.json`, images).
- **[wp-worktree](./wp-worktree/SKILL.md)** — One isolated Laravel Herd site, with its own cloned database, per git worktree, so parallel branches and AI agents never collide.
