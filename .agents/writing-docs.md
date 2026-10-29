# Writing docs pages

Every skill in a promoted bucket (`wordpress/`, `browser/`) has a human-facing **docs page** at `docs/<bucket>/<skill-name>.md` — the docs tree mirrors the promoted bucket folders under `skills/`. The page is not the skill and not a copy of `SKILL.md`. Skills in `in-progress/` and `deprecated/` ship no docs page.

The job of a docs page is to orient one reader around one skill so they can hold it in their head, know when to reach for it, what to have ready before they do, and what they get back. The top-level `README.md` is the index; each docs page is a node.

Act whenever a promoted skill is added, renamed, or has its behaviour changed: create or re-sync its docs page. A rename moves the file too (`docs/<bucket>/<old>.md` → `docs/<bucket>/<new>.md`); a skill that moves between promoted buckets moves its docs file to the matching folder. A skill moving *out* of `in-progress/` into a promoted bucket gains a page; one moving the other way loses it.

The pages are read on GitHub, so links are **repo-relative** (`../../skills/<bucket>/<name>/SKILL.md`, `./<sibling>.md`). Check that every link resolves from the page's own folder.

There is no H1 — the page takes its title from the file name.

## Page structure

Fill the template below. The **fixed frame** (Quickstart block, source link, `## What it does`, `## When to reach for it`, `## Where it fits`) appears on every page. The **adaptable middle** — `## Before you start` and the free-form substance sections — carries only what this particular skill earns; delete the rest.

<page-template>

Quickstart:

```bash
npx skills add aminurislamarnob/claude-plugins --skill=<name>
```

Or, as part of the Claude Code plugin: `/plugin install aiarnob-skills@aminurislamarnob`.

[Source](../../skills/<bucket>/<name>/SKILL.md)

## What it does

One or two plain-language paragraphs. Lead with the skill's one-sentence job, then state the **defining constraint** — the single fact that makes this skill behave differently from the obvious default (for `browser-walkthrough`: a step whose server state disagrees with the screen is a finding, not a step). Write it as a plain declarative sentence, never a labelled aside. This line is the most valuable on the page; never omit it.

## When to reach for it

Two beats, both effectively always present:

- **Invocation mode.** A user-invoked skill: "You invoke this by typing `/<name>` — the agent won't reach for it on its own." A model-invoked skill: "Type `/<name>`, or the agent reaches for it automatically when a task fits."
- **Trigger boundary.** The index entry: "reach for this when …". Where the skill is confusable with a sibling, add the other half — "for <X> instead, use [<sibling>](./<sibling>.md)."

## Before you start

Optional — include only when the skill needs something in place to be functional; omit the heading entirely otherwise. Covers: tools that must be installed (Playwright, Herd, FFmpeg), connectors (Claude in Chrome, ElevenLabs), credentials and environment variables, and anything that must already be running (the site, a webhook listener). Say what each is for in a few words.

## <free-form middle>

One to three short sections, in the skill's *own vocabulary*, that make it click — what Claude does, what you get back, the one anti-pattern it kills. There is no prescribed heading.

The single non-negotiable: **surface the skill's leading word / defining idea** — a *walkthrough* of honest steps, a *take* per role with *cues*, a *page map*, one *site per worktree*. The reader learns what the skill *is*, and the word they'll later think with to *reach for* it.

## Tips

Optional. A few bullets of things that save a second run: what to say up front, what to do when something stalls, how to ask for a retake or an edit. Omit when there is nothing non-obvious.

## Where it fits

Always present. One or two sentences: whether the skill is a **run-first setup** (`wp-worktree`), a **reach-for-it-anytime standalone**, or one half of a pair (`browser-walkthrough` and `feature-video` both prove a change in a real browser; one gives a page, the other a film). Link the sibling that matters with a because-clause, and point back to the [README](../../README.md#reference) for the whole set.

</page-template>

## Conventions

- Explain the **why**, not the process. The page orients the reader; it never reproduces the `SKILL.md` steps or script flags — a human choosing a tool does not need the runbook.
- Use the skill's **leading words** so the page and the skill speak one language.
- Keep the page itself low-load: no spare headings, no restated links.

## Done when

- The page exists at `docs/<bucket>/<name>.md`, and no stale page survives a rename or bucket move.
- The Quickstart block and source link name the correct bucket and skill.
- `## What it does` states the defining constraint, as plain prose.
- `## When to reach for it` states invocation mode and the trigger boundary.
- `## Where it fits` names the role and links back to the README.
- A prerequisite is stated where one exists, and the section is absent where none does.
- The middle surfaces the leading word.
- Every link is repo-relative, and every one resolves.
