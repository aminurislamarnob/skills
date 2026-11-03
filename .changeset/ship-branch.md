---
"aiarnob-skills": minor
---

Add **`ship-branch`**, a user-invoked skill in a new **`git`** bucket. `/ship-branch` commits the current work, pushes, opens a pull request, merges it, and deletes the branch locally and on the remote, in one command, with the PR body written by the `pr` skill from mattpocock/skills (Summary, Evidence, Merge Danger). Each step is skipped when it has already happened (clean tree, branch already pushed, PR already open or merged, branch already gone), so a run that stops at a protected merge can be re-run and finishes from there. Gemini CLI users add a third install: `gemini skills install https://github.com/aminurislamarnob/skills.git --path skills/git`.
