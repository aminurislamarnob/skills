# Claude Code & Multi-Agent Worktree Workflows

This guide explains how to run concurrent AI agent sessions using Claude Code (or Cursor / Antigravity) alongside `wp-worktree`.

## The Problem

When running multiple AI agent sessions on a single WordPress site:
1. Two agents modifying the same plugin directory overwrite each other's changes.
2. Git checkouts in the main working tree cause race conditions between agent commits.
3. Database changes or migrations performed by Agent A break the test state for Agent B.

## The Solution: Worktree per Agent

Claude Code supports isolated worktrees. When Claude Code or the developer spins up an agent session in a worktree, `wp-worktree` provides an isolated WordPress runtime for each agent.

### Workflow 1: Automatic Adoption of Claude Code Worktrees

When Claude Code creates a worktree in `.claude/worktrees/agent-<hash>`:

1. Inside the Claude Code prompt or session start:
   ```bash
   wp-worktree setup
   ```
2. The agent immediately has:
   - A live, dedicated HTTPS URL: `https://site--agent-<hash>.test`
   - Its own cloned database: `<db>_wt_agent_<hash>`
   - Working WP-CLI commands: `wp plugin list`, `wp eval "..."`

### Workflow 2: Starting Parallel Agents from the Terminal

To launch two parallel agents on two independent features:

```bash
# Terminal 1: Feature Cart
wp-worktree create feat-cart
cd wp-content/plugins/my-plugin--feat-cart
claude

# Terminal 2: Feature Checkout
wp-worktree create feat-checkout
cd wp-content/plugins/my-plugin--feat-checkout
claude
```

Both agents can browse, test, and run PHPUnit/Playwright tests concurrently against their respective URLs:
- Agent 1: `https://mysite--feat-cart.test`
- Agent 2: `https://mysite--feat-checkout.test`

### Adding to Agent System Prompts or CLAUDE.md

To instruct Claude Code to automatically configure its environment when inside a worktree, add the following to `CLAUDE.md` or `AGENTS.md`:

```markdown
## WordPress Worktree Environments
When working in a git worktree or running with `--worktree`:
1. Run `wp-worktree setup` at the beginning of the session.
2. Verify the site is online with `wp-worktree status`.
3. Use the reported URL for testing changes or browser previews.
4. Run `wp` commands normally from within the worktree directory.
```
