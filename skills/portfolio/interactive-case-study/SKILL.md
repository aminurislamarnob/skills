---
name: interactive-case-study
description: Write a compact, interactive portfolio case study of one project as a single page where every section is led by something to click (a commit timeline, a clickable architecture diagram, a sticky deck of key decisions, a before/after switch, a screens lightbox, who-built-what), with details folded into collapsed rows. Use when asked for an interactive, compact, short or skimmable case study, a project details page for a portfolio, to turn a long case study or write-up into an interactive one, or to make another page like an existing interactive case study.
---

# Interactive case study

An **interactive case study** is a portfolio page about one project that a visitor skims in a minute and plays with for two. It has a hero with screenshots and four headline figures, a facts row, and **at most six sections, each led by something to click** rather than by paragraphs. Anything longer than two sentences goes into a collapsed row.

The defining rule: **compact beats complete, and every claim still traces to a source.** When a detail doesn't fit a clickable piece, fold it into a FAQ row or cut it. Never pad, and never invent a number to fill a gauge. Commit hashes, PR numbers and dates stay out of the copy. Only the sources footer may cite them.

Read [references/writing.md](references/writing.md) before writing a word. It has the six sections, what each one needs, the headline formula and the honesty rules. When the page is going into a site rather than published on its own, also read [references/porting.md](references/porting.md).

## 1. Scope

Settle these with the person, asking only for what the repositories and the live site can't answer:

- **The project**: name, live URL, repositories (local paths) and the branch that represents shipped work.
- **Identity**: every email or name they commit under (`git shortlog -sne --all`), for counting.
- **Role**, in their words, team size, and **what to leave out** (clients, internal URLs, people's names).
- **Source material**: an existing long case study, a README, PR bodies with before/after numbers, Lighthouse or PageSpeed results, design files. A long case study is the best input. Compact it, don't rewrite it.
- **Where it goes**: a page published on its own (a Claude Artifact or a static file), or a page in their site. If their site already has interactive case studies, read one whole and match it. That's what `references/porting.md` is for.

## 2. Count

```bash
python3 -I <skill-dir>/scripts/git_stats.py --repo <path> [--repo <path>] --author '<email-or-name>' \
  [--ref main] [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--tz Area/City] [--coauthor claude] --out <work-dir>
```

It writes `stats.json` (totals, and a series by day, week or month that the timeline draws) and `subjects.txt` (every one of the person's commits, oldest first). `--coauthor claude` counts commits pair-written with an AI agent for the "behind the build" figure. The script's docstring lists every flag. Skip this step only when the project has no git history to count. Then the timeline takes hand-written `bars`, or is dropped.

## 3. Gather

- Read **all of `subjects.txt`** and write one short note per busy bar ("what shipped that week"). Those notes are the timeline.
- Find the **three to five calls** that shaped the project: a migration, a design pivot, an architecture boundary, a performance fix. Each becomes a decision card.
- Find **one before/after**: a score, a load time, a count. It must come from a measurement (a PR body, a PageSpeed run, the person). With no such number, drop the results section.
- Read the README, the decision records and `CLAUDE.md` / `AGENTS.md` for the architecture: the two to four zones a request or build passes through.

## 4. Screenshots

Use public or demo pages only, never a logged-in admin with real data. Capture them read-only with [scripts/shoot.mjs](scripts/shoot.mjs), which needs Playwright (run it from a project that has it, or set `PLAYWRIGHT_MODULE`):

```bash
node <skill-dir>/scripts/shoot.mjs shots.json <work-dir>/img
```

You need a 1440×900 desktop shot and a phone shot (390 wide at 2× DPR, or one the site already has) for the hero, plus up to three cards for the screens section. Full-page captures can go in the lightbox (`"long": true`). Look at every image before using it. Convert to WebP when `cwebp` is around.

## 5. Write

Write `<work-dir>/case.json` in the format documented at the top of [scripts/build_page.py](scripts/build_page.py). [examples/case.json](examples/case.json) with [examples/stats.json](examples/stats.json) uses every section type with fictional data. The usual order is timeline, architecture, decisions, results, screens, behind. Drop what the project has no material for.

Then **check and fact-check**:

```bash
python3 -I <skill-dir>/scripts/build_page.py <work-dir> --check
```

It fails on more than six sections, overlong copy, and commit hashes, PR or issue numbers or ISO dates in the copy. Then re-read every sentence against its source. Cut or soften anything you inferred, and check every number against `stats.json` or the measurement it came from.

## 6. Build

```bash
python3 -I <skill-dir>/scripts/build_page.py <work-dir>                # index.html: fragment for Claude's Artifact tool
python3 -I <skill-dir>/scripts/build_page.py <work-dir> --standalone   # standalone.html: full document for any host
```

It also writes `files.json`, the map of every image the page uses, and prints warnings for missing files and timeline bars without a note. The page has no dependencies. It follows the viewer's light or dark theme (or `data-theme` on `<html>`), works at phone width, stays still under `prefers-reduced-motion`, and loads only Google Fonts. Put brand colours in `theme`: `stage` takes the hero's four gradient colours, and `light` / `dark` override any `--cs-*` token.

Open `standalone.html` and click through every interaction (a timeline bar, each zone pill, each decision pill, the before/after switch, a screen card) in light, dark and phone width before you publish.

## 7. Publish

Publish privately by default. Use what the harness offers:

- **Claude (Artifact tool available):** publish `index.html` with `files` set to `files.json`'s map, an `icon` such as `chart`, and a one-sentence `description`. Republish the same file path to keep the URL.
- **A site of the person's own:** follow `references/porting.md`. `case.json` is the content model, and the page's markup and classes are the component.
- **Any other agent:** hand over `standalone.html` plus `img/`. Deploy it to a static host only when the person asks, because that makes it public.

## 8. Report

Give the link or path, the four headline figures, and a list of things to check before sharing: framing written without a source, numbers rounded or taken from a single run, screenshots with demo data, and anything about other people. Say that a private page stays private until they share it.
