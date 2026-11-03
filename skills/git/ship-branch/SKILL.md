---
name: ship-branch
description: Commit the current work, push it, open a pull request, merge it, and delete the branch locally and on the remote. Every step is skipped when it has already happened, so it is safe to re-run.
disable-model-invocation: true
---

# Ship branch

**Shipping** a branch means taking it from "edited" to "merged and gone" in one go: commit, push, pull request, merge, delete the branch on both sides. The bundled script [scripts/ship.sh](scripts/ship.sh) does the git and GitHub work and **skips any step that is already done**: a clean tree is not committed again, a branch the remote already has is not pushed again, an existing PR is reused, a merged PR is not merged again, a branch already deleted is not deleted again. Your job is the words (commit message, PR title and body) and the report.

Needs `git`, `jq` and a logged-in `gh`. It never bypasses required checks or reviews: when GitHub refuses the merge, it stops and leaves everything in place.

## 1. Look before shipping

Run, and read the output:

```bash
git status --short && git branch --show-current && git log --oneline origin/HEAD..HEAD 2>/dev/null | head
```

- On the **default branch** (`main`/`master`) with changes: the script needs `--branch <name>`. Pick a short kebab-case name that says what the change is (`fix-coupon-rounding`, `docs-install-block`).
- On a **feature branch**: ship it as is.
- Files that should not be committed (secrets, build output, scratch files): the script stages everything with `git add -A`, so stop and tell the user before shipping, or add them to `.gitignore` first.
- `git status` clean and nothing to push: say so and stop. There is nothing to ship.

## 2. Write the words

Only what the current state needs:

- **Commit message**, when the tree is dirty: read the diff (`git diff` and `git diff --cached`, `git status --short` for untracked files) and write one in the repo's style (`git log --oneline -10`). Subject line in the imperative, under 72 characters; a body only when the why is not obvious from the diff.
- **PR title and body**, when no PR exists yet (`gh pr list --head <branch> --state all`): title from the commit subject. Write the body with the `pr` skill from [mattpocock/skills](https://github.com/mattpocock/skills) (invoke it as `/pr`, or `mattpocock-skills:pr` where it is namespaced): a **Summary** as the smallest diagram, diff sketch or tree that makes the point, **Evidence** with a before and after, and **Merge Danger** naming the door (one-way or two-way) and the blast radius. If that skill is not installed, say so and write the same three sections by hand. Put the body in a file in the scratchpad and pass it with `-b`.

Apply any attribution lines the session asks for in commit messages and PR descriptions.

## 3. Ship

```bash
<skill-dir>/scripts/ship.sh -m "<commit message>" -t "<PR title>" -b <body-file> [--branch <name>] [--method merge|squash|rebase]
```

Omit `-m` when the tree is clean, and `-t`/`-b` when a PR already exists; the script ignores what it does not need. The merge method defaults to the first of merge, squash, rebase that the repository allows. The script prints one line per step: what it did, or `skipped:` and why.

## 4. When it stops

The script exits non-zero and says why. Fix the cause, then **re-run the same command**: finished steps are skipped.

- `GitHub refused to merge`: required checks still running, a review required, or a conflict. Report the PR URL and what GitHub wants. Do not force or bypass anything; wait for checks only if the user asks.
- `origin/<branch> has N commit(s) you don't have`: someone pushed to the branch. Pull or rebase, resolve, re-run.
- `on main; pass --branch`: re-run with `--branch <name>`.

## 5. Report

One short message: the PR URL and number, the merge method, the branch that was removed, and which steps were skipped because they were already done. If the script stopped, say at which step, why, and what the user has to do.
