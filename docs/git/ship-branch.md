Quickstart:

```bash
npx skills@latest add aminurislamarnob/skills --skill=ship-branch
```

Or, as part of the Claude Code plugin: `/plugin install aiarnob-skills@aminurislamarnob`.

[Source](../../skills/git/ship-branch/SKILL.md)

## What it does

`ship-branch` takes the branch you are on from "edited" to "merged and gone": it commits what is in the working tree, pushes, opens a pull request, merges it, and deletes the branch both locally and on GitHub. The agent writes the commit message from the diff and the pull request body with the `pr` skill from [mattpocock/skills](https://github.com/mattpocock/skills) (Summary, Evidence, Merge Danger); a bundled script does the git and GitHub work.

Every step is skipped when it has already happened. A clean tree is not committed, a branch the remote already has is not pushed, an existing pull request is reused, a merged one is not merged twice. That makes the skill safe to re-run after any failure: it picks up at the step that stopped.

## When to reach for it

You invoke this by typing `/ship-branch` — the agent won't reach for it on its own, because pushing and merging are outward-facing actions you decide on.

Reach for it when the change is done and you want it on the default branch without walking through the five commands yourself. For checking the change works before shipping it, use [browser-walkthrough](../browser/browser-walkthrough.md).

## Before you start

- `git`, `jq`, and the GitHub CLI `gh` logged in to an account that can merge in the repository.
- A clone with an `origin` remote on GitHub.
- A `.gitignore` that already excludes what must never be committed: the skill stages everything.
- The `pr` skill from [mattpocock/skills](https://github.com/mattpocock/skills) for the PR body. Without it the agent writes the same sections by hand.

## Shipping

The run prints one line per step: `commit`, `push`, `pull request`, `merge`, `delete branch`, each either done or `skipped:` with the reason. Starting on `main` with changes, the agent creates a feature branch first and ships that. The merge method is the first of merge, squash or rebase the repository allows, unless you name one.

The skill never bypasses branch protection. When GitHub refuses the merge because checks are still running, a review is required, or the branch conflicts, it stops, keeps the branch and the PR in place, and tells you what GitHub wants. Re-running the same command after that finishes the job.

## Tips

- Say the branch name and merge method up front ("ship this as `fix-rounding`, squash") to skip a question.
- If you want to see the PR before it merges, ask for the PR only; the skill is one command, not a review step.
- Secrets or scratch files in the tree: tell the agent, or ignore them first, because the skill commits everything.

## Where it fits

A reach-for-it-anytime standalone that ends a piece of work. It pairs naturally with [browser-walkthrough](../browser/browser-walkthrough.md), which proves the change first, and with [wp-worktree](../wordpress/wp-worktree.md), whose site is removed once the branch it served is gone. The whole set is in the [README](../../README.md#reference).
