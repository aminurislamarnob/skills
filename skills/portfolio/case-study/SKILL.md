---
name: case-study
description: Write a portfolio case study of one person's work on a project, from their own git commits across one or more repositories, as a polished single-page HTML artifact (dated engineering log, commit chart, diagrams, before/after numbers, what I built vs what the team built). Use when asked to write a case study, portfolio page, project write-up or "what I did on this project" from git history, or to make another page like an existing case study.
---

# Case study

A **case study** is a portfolio page about one person's part in one project, built from their own commits and laid out as a dated engineering log: a rail on the left says when each piece of work happened, and the story runs beside it. It opens with a commit chart of their work against the team's, and it ends with a footer that says where every number came from. The page is static HTML, so any agent can build it and any host can serve it.

The defining rule: **only the person's commits count as theirs, and every claim traces to a source** (a commit, a PR body, a decision record, an issue, or the person). Inferences get softened or cut before the page is published.

Read [references/writing.md](references/writing.md) before writing a word: it holds the section order, the honesty rules and the voice. Read [references/diagrams.md](references/diagrams.md) before drawing.

## 1. Scope

Settle these with the person, asking only for what the repositories can't answer:

- **Repositories**: local paths (one or several), and the branch that represents shipped work (the default branch unless they say otherwise; a client branch may get its own case study).
- **Identity**: every email or name they commit under (`git shortlog -sne --all` lists them), and their GitHub login.
- **Window**: from the first commit, or a date range; the time zone the dates should read in.
- **Role**, in their words, and **what to leave out** (unreleased clients, internal URLs, people's names).
- **An existing case study** to match, when they have one: read it whole first and keep its section order and visual style.

## 2. Count

```bash
python3 -I <skill-dir>/scripts/git_stats.py --repo <path> [--repo <path>] --author '<email-or-name>' \
  [--ref develop] [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--tz Area/City] \
  [--coauthor claude] [--decisions 'docs/adr/*.md'] [--github --login <gh-login> --exclude-base '<client-branch>'] \
  --out <work-dir>
```

It writes `stats.json` (totals, per repository, and a chart series by day, week or month) and `subjects.txt` (every one of the person's commits, oldest first). `--github` needs the `gh` CLI signed in. The script's docstring lists every flag.

Done when the totals match a quick manual check (`git log <ref> --no-merges --author=<x> --oneline | wc -l`).

## 3. Gather

- Read **all of `subjects.txt`**, and group the commits into themes with their dates. Those themes become the work sections.
- List the team's merged PR titles for the "what the team built" half.
- Read the decision records, the glossary, the README and the agent instructions (`CLAUDE.md`, `AGENTS.md`) for the architecture and its vocabulary.
- Pull measured numbers from PR bodies (`gh pr view <n> --json body`, look for before/after tables) and from the person's notes. Note where each was measured.
- Find who designed what. If a teammate built the foundation, the page says so.

## 4. Screenshots (optional)

Use public or demo pages only, never a logged-in admin with real data. Capture them read-only with [scripts/shoot.mjs](scripts/shoot.mjs), which needs Playwright (run it from a project that has it, or set `PLAYWRIGHT_MODULE`):

```bash
node <skill-dir>/scripts/shoot.mjs shots.json <work-dir>/img
```

A 1440×900 desktop shot and a 390×844 phone shot fill the hero. Look at each image before using it, and drop any that shows personal data, a loading state or a mismatched demo record. Documentation screenshots the project already has (cleaned of private data) can be reused.

## 5. Write

Write `<work-dir>/case.json` in the format at the top of [scripts/build_page.py](scripts/build_page.py), and put diagrams under `<work-dir>/diagrams/`. Follow the section order in `references/writing.md`. Start with a `chart` and `totals` in the first section, give each work section a heading that says what happened, and close with the footer that states sources and caveats. [examples/case.json](examples/case.json) shows every block type with fictional data.

Then **fact-check**: re-read every sentence against its source. Cut or soften anything inferred, check every number against `stats.json` or the PR it came from, and make sure no private name or URL slipped in.

## 6. Build

```bash
python3 -I <skill-dir>/scripts/build_page.py <work-dir>                # index.html: fragment for Claude's Artifact tool
python3 -I <skill-dir>/scripts/build_page.py <work-dir> --standalone   # standalone.html: full document, any host
```

It also writes `files.json`, the map of every image the page uses. The page follows the viewer's light or dark theme, works at phone width, and loads only Google Fonts.

## 7. Publish

Publish privately by default. Use what the harness offers:

- **Claude (Artifact tool available):** publish `index.html` with `files` set to `files.json`'s map, an `icon` such as `chart`, and a one-sentence `description`. Republish the same file path to keep the URL.
- **Any other agent:** open `standalone.html` locally and hand over the folder (`standalone.html` plus `img/`). Deploy it to a static host (GitHub Pages, Netlify, Cloudflare Pages, Vercel) only when the person asks, because that makes it public.

## 8. Report

Give the link or path, the headline numbers, and the list of things the person should check before sharing: framing you wrote without a source, gaps you didn't explain, screenshots with demo data, and anything about other people. Say that a private page stays private until they share it.
