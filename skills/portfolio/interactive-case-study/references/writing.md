# Writing the interactive case study

A visitor gives a portfolio page about a minute. The interactive case study is built for that minute. Each section makes one point in its heading, proves it with something the visitor can click, and keeps everything else one tap away in a collapsed row. It is written in the first person, by the person whose work it shows.

## The page

1. **Hero.** A kicker (`<Project> · Case study`), a headline, a lede of two or three sentences (what the project is, your part, where it lives), two buttons (the live site, and a contact link such as "Hire me"), a desktop screenshot in a browser frame with a phone in front, up to three floating chips with proof points ("Mobile LCP **1.8 s**"), and **four figures** that count up (days, commits, pages, a score). Use numbers you can source. A figure without one doesn't belong in the hero.
2. **Facts row.** Three to five: your role, the team, the timeline, the content or scale, the stack. Each fact is a phrase, not a sentence.
3. **Up to six sections.** Pick from the six types below, in this order, and drop any the project has no material for.
4. **Next case study** and a **call to action**. Use them when the person has another case study, or a contact link.
5. **Sources.** One paragraph on where every number came from: branch, window, time zone, filters, tools. Dates, PR numbers and commit hashes may appear here and nowhere else.

## The six sections

Every section has an eyebrow (numbered for you), a heading, its interactive piece, and an optional footnote.

**Headings** follow one formula: a plain fact, then the twist in bold. "96 commits, **two bursts.**" "Static HTML, **islands only where needed.**" "A blur that cost **about 3 s.**" "Five engineers, **one store.**" A heading never names a category ("Architecture") and never makes a claim the section can't back.

| Type | The thing to click | It needs |
| --- | --- | --- |
| `timeline` | A bar per day, week or month. Clicking one shows what shipped then | `stats.json` (or hand-written bars), one short note per busy bar, a quiet note for empty ones |
| `architecture` | Pills (and the zones themselves) that light one zone of the diagram and show its note | The brief as three to five ticks, two to four zones, each with up to three boxes and a two-sentence note |
| `decisions` | A sticky deck: cards stack as you scroll, pills jump to a card and follow the one on top | Three to five cards. Each has a title, two sentences, a tag line and one visual: a `log`, a `pivot` (was → now), a `table` or an `image` |
| `results` | A Before / After switch that flips a gauge and two to four figures | One measured score for the gauge, the fixes that moved it, and optional supporting metrics |
| `screens` | Cards that open a lightbox, with a button for the full set | Up to three cards (the first goes tall), more full pages for the lightbox only |
| `behind` | A square per commit, coloured by who (or what) wrote it | Who directed and who drafted, two to four collapsed detail rows, the stack as chips |

Choose the section's visual by what the evidence is. A sequence of events is a `log`. A replacement is a `pivot`. A comparison of modes is a `table`. A design is an `image`.

## Compact rules

- **At most six sections.** If two sections make the same point, merge them.
- **Two sentences per text block** (about 260 characters). A third sentence belongs in a FAQ row under "behind", or nowhere.
- **One note per timeline bar**, about 12 words: what shipped, not how it felt.
- **Diagram boxes**: a title up to about 28 characters and a subtitle up to about 34 at three zones. Allow fewer at four.
- **No commit hashes, PR or issue numbers, or dates in the copy.** Say "the week of the launch", not "on 12 October in #461". `--check` enforces this.
- **Cut, don't shrink.** A sentence that survives only by being made tiny should go.

## Honesty rules

They carry over from long-form case studies unchanged:

- **Count only the person's commits** as theirs. A teammate's work is credited to "a teammate" or "the team". AI-agent commits made in the person's own sessions count as theirs, and the footnote says so.
- **Every claim traces to a source**: a commit subject, a PR body, a decision record, the spec, a measurement, or the person. Soften or cut anything you inferred.
- **Numbers come from the measurement that produced them.** The footnote names it ("PageSpeed Insights, emulated Moto G Power on slow 4G"). Never round a range into a better single number. Never fill a gauge or a figure with an estimate.
- **Don't explain gaps you can't explain.** A quiet bar's note says "Quiet: no commits." and nothing more.
- **Commit counts measure activity, not effort.** The timeline footnote says so.
- **Private information stays out** unless the person confirms it's public: unreleased clients, revenue, staff names, internal URLs. Screenshots come from public or demo pages.

## Voice

- Plain, active and specific, in short sentences. Write the way the person would explain it to a peer.
- Name things the way a user recognises them, then the term of art once if it matters.
- No em-dash asides, no "not X, but Y", no colon-then-reveal sentences, no superlatives the numbers don't earn.
- Tags and chips are noun phrases joined by " · " ("Astro 6 · React 19 · nanostores").
