Quickstart:

```bash
npx skills add aminurislamarnob/skills --skill=interactive-case-study
```

Or, as part of the Claude Code plugin: `/plugin install aiarnob-skills@aminurislamarnob`.

[Source](../../skills/portfolio/interactive-case-study/SKILL.md)

## What it does

`interactive-case-study` writes a portfolio page about one project that a visitor skims in a minute and clicks through in two. It opens with a hero (the live site in a browser frame, a phone in front, four figures that count up) and a facts row. Then come at most six sections, and each one is led by something to click: a commit timeline whose bars say what shipped, an architecture diagram whose zones light up, a sticky deck of key decisions, a before/after switch, a screens lightbox, and a square per commit showing who built it.

Compact beats complete, and every claim still traces to a source. Anything longer than two sentences is folded into a collapsed row or cut. No number is invented to fill a gauge, and commit hashes, PR numbers and dates stay out of the copy. Only the sources footer may cite them.

## When to reach for it

Type `/interactive-case-study`, or the agent reaches for it automatically when asked for an interactive, compact or skimmable case study, a project details page for a portfolio, or to turn a long write-up into one.

Reach for it when the page is for a visitor who won't read paragraphs: a portfolio, a client pitch, a link in a proposal. For the full dated engineering log, with every stretch of work and what the team built next to yours, use [case-study](./case-study.md).

## Before you start

- Python 3, for counting commits and building the page.
- Playwright with Chromium, only if you want fresh screenshots of a public or demo page.
- The local paths of the repositories, and every email you have committed under.
- One measured before/after, if you want the results section: a PageSpeed run, a PR body with timings, your own notes.

## Six sections, one thing to click each

The leading idea is that **each section is led by something to click**. The heading makes one point ("96 commits, **two bursts.**"), and the interactive piece proves it. The timeline proves the rhythm, the zones prove the architecture, the deck proves the decisions and the switch proves the results. The details sit one tap away in collapsed rows. A bundled check enforces the compact rules before the page is built: at most six sections, two sentences per block, and no hashes, PR numbers or dates in the copy.

## Any agent, any host, or your own site

The model only writes the words, in a `case.json` file. Bundled scripts count the commits and build the page, so it works the same in Claude Code, Codex, Copilot, Gemini CLI, Cursor or any agent that reads skills. The page has no dependencies, follows the viewer's light or dark theme, works at phone width and stays still under reduced motion. In Claude it is published as a private Artifact. Elsewhere you get a standalone HTML file and an `img/` folder.

When the case study belongs in your own site, the skill ports it instead: `case.json` becomes the content model, and the page's markup and stylesheet become a component and a shared stylesheet. If your site already has an interactive case study, the skill matches that one.

## Tips

- Hand it your long case study or README if you have one. Compacting a write-up beats starting from commits.
- Name the one number you're proudest of up front, with where it was measured. It becomes the gauge.
- Ask for the "things to check" list before sharing. It names the framing the agent wrote without a source.

## Where it fits

A reach-for-it-anytime standalone, and the short half of a pair with [case-study](./case-study.md), which writes the long log. Many people write the long one first and then make this from it. The whole set is in the [README](../../README.md#reference).
