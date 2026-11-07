Quickstart:

```bash
npx skills add aminurislamarnob/skills --skill=case-study
```

Or, as part of the Claude Code plugin: `/plugin install aiarnob-skills@aminurislamarnob`.

[Source](../../skills/portfolio/case-study/SKILL.md)

## What it does

`case-study` writes a portfolio page about your part in a project. It counts your commits in one or more git repositories against the team's, reads every one of your commit subjects, and turns them into a dated engineering log: a hero with screenshots, a commit chart, the brief, the architecture, one section per stretch of work, what you built next to what the team built, and a footer that says where every number came from.

Only your commits count as yours, and every claim on the page traces to a source: a commit, a PR body, a decision record, an issue, or you. Anything the agent inferred is softened or cut before it publishes, and teammates' work is credited to them.

## When to reach for it

Type `/case-study`, or the agent reaches for it automatically when asked to write a case study, a portfolio page or a project write-up from git history, or to make another page like an existing case study.

Reach for it when you want a page you can link from a portfolio or send to a client. It isn't for proving a single change works. For that, use [browser-walkthrough](../browser/browser-walkthrough.md).

## Before you start

- Python 3, for counting commits and building the page.
- The `gh` CLI signed in, if you want pull request and issue counts.
- Playwright with Chromium, only if you want fresh screenshots of a public or demo page.
- The local paths of the repositories, and every email you have committed under.

## Any agent, one page

The skill does its counting, drawing and building with bundled scripts, so it works the same in Claude Code, Codex, Copilot, Gemini CLI, Cursor or any agent that reads skills. The model only writes the words, in a `case.json` file, and a builder turns that into one HTML page that follows the viewer's light or dark theme and works on a phone.

In Claude, the page is published as a private Artifact. In any other agent you get a standalone HTML file and an `img/` folder that you can open locally or put on any static host.

## Tips

- Name your role in your own words up front, and anything to leave out: unreleased clients, internal URLs, colleagues' names.
- Point it at an existing case study to match its sections and look.
- Ask for the "things to check" list at the end before sharing: it names the framing the agent wrote without a source.

## Where it fits

A reach-for-it-anytime standalone, usually at the end of a project or a milestone. It pairs well with [browser-walkthrough](../browser/browser-walkthrough.md), whose screenshots and findings can feed a section of the case study. The whole set is in the [README](../../README.md#reference).
