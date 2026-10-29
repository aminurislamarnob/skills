# Model-invoked vs user-invoked

Every `SKILL.md` in this repo is a skill. The one axis that splits them is **invocation** — who can reach it:

- **User-invoked** — reachable **only by the human typing its name**. Set `disable-model-invocation: true` in the frontmatter (Claude Code) and `policy.allow_implicit_invocation: false` in `agents/openai.yaml` (Codex). The `description` is **human-facing**: a one-line summary read by a person browsing slash-commands. Strip trigger lists ("Use when the user says…").
- **Model-invoked** — reachable by **model or user**. The default: omit `disable-model-invocation` and the `policy` block from `agents/openai.yaml`. The `description` is **model-facing** and keeps rich trigger phrasing ("Use when asked to…, mentions…") so auto-invocation fires. The test for whether a skill should stay model-invoked: _could the model usefully reach for this autonomously?_

`setup-aminurislamarnob-skills` is user-invoked: it is a run-once bootstrap the human decides to run. Every other skill is model-invoked: each is the natural response to a plain request ("write the user docs", "check this PR in the real browser", "record a demo video", "spin up a worktree site"), so the model should be free to reach for it.

Each harness excludes a user-invoked skill from the model's reach in its own way, so nothing but the human can fire it — no other skill can. A user-invoked skill may invoke model-invoked skills, but it can never reach another user-invoked skill.

Every skill also carries an `agents/openai.yaml` beside its `SKILL.md`. It holds Codex UI metadata — `interface.display_name` and `interface.short_description` for the skill picker — and, for user-invoked skills, the `policy.allow_implicit_invocation: false` that pairs with `disable-model-invocation`. Keep the two in sync: a skill is user-invoked in both harnesses or neither.

Bucket `README.md`s and the top-level `README.md` group entries into **User-invoked** and **Model-invoked**.

## Dependencies between them

Dependencies are expressed as **`/skill`-style prose invocation** ("see the `hyperframes-cli` skill"), not deep `../other-skill/FILE.md` cross-references. Shared reference docs live inside the skill that owns them; other skills reach that material by invoking the skill, not by linking across folders.
