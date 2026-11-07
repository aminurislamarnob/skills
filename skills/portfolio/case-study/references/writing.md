# Writing the case study

A **case study** is a portfolio page about one person's part in one project, told as a dated engineering log: a rail on the left says when each piece of work happened, the story runs beside it. It is written in the first person, by the person whose commits it counts, for a hiring manager or client who will skim it in two minutes and read one section closely.

## The shape

Keep this order. Drop a section when the project has nothing for it; don't pad one.

1. **Hero.** Eyebrow (`Case study · <domain>`), a headline that states the outcome in plain words (no slogan), a lede of three to five sentences: what the project is, the person's role, their share of the commits, and where it can be seen. Facts row: role, team size and repositories, window, a milestone (launch, first client), stack. One desktop screenshot plus one phone screenshot when the product has a public face.
2. **The window** (rail: "The months", "The week"). The commit chart, one paragraph that reads it (who carried which stretch, quiet gaps stated without inventing a reason), and a totals row: commits, merged PRs, issues opened, decisions written.
3. **The brief.** What had to be true when the work started: users, constraints, non-negotiables. Only facts from the spec, README, issues or the person.
4. **The platform / starting point.** The architecture in two short paragraphs and one diagram. Say plainly who designed it if it wasn't the person.
5. **Chronological work sections**, one per theme in the order it happened, rail = the theme plus its dates. Each opens with why the work was hard, then what was built. Use a dated `log` block for a dense first stretch, a `defs` list for many small features, a `table` for rules or trade-offs, a diagram for the one flow that matters most, `ranges` for before/after numbers.
6. **The details a visitor never sees.** Accessibility, security, SEO, test infrastructure: a `defs` list.
7. **Leading it** (when the person led). Issues opened, PRs written, decisions written, a `split` of what they built and what the team built, how the team avoided collisions, how AI agents were used and why it worked.
8. **Where it went next / Where it stands.** A milestone, the first client, a link to a related case study, then a `list` of outcomes with bold leads.
9. **Footer: Where the numbers come from.** Exactly which branch, window, filters and tools each number came from, and what each number does not measure.

## Honesty rules

These are what make the page trustworthy, and they are not negotiable.

- **Count only the person's commits** as theirs. Everything the team did is credited to "a teammate" or "the team", never absorbed.
- **Every claim traces to a source**: a commit subject, a PR body, a decision record, an issue, the spec, or the person. Before publishing, re-read each paragraph and soften or cut any sentence you inferred (effects like "which stopped random sign-outs" need a source too).
- **Numbers come from the measurement that produced them**, with its context in the caption ("measured locally against a WooCommerce backend, recorded in PR #461"). Never round a range into a single better number.
- **Don't explain gaps you can't explain.** "The repositories were quiet from 7 August to 5 September" is enough.
- **Commit counts measure activity, not effort.** Say so in the footer; squash merges and branch choices distort them.
- **Private and client information stays out** unless the person confirms it's public: unreleased clients, revenue, staff names, internal URLs, credentials. Screenshots come from public or demo pages, never from a logged-in admin with real data.

## Voice

- Plain, active, specific. Short sentences. Write the way the person would explain it to a peer.
- Name things by what a user recognises ("the owner's settings panel"), then the term of art once if it matters ("the Port").
- No em-dash asides, no "not X, but Y", no colon-then-reveal sentences, no "worth noting", no superlatives the numbers don't earn.
- Headings say what happened ("Payments: the shopper never leaves the checkout"), not a category ("Payments").
- One idea per paragraph; three to six paragraphs or blocks per section.
- Dates as "22 Jun" in rails and logs, "22 June" in prose; one time zone, named in the footer when it matters.

## Gathering material

- `subjects.txt` (from `git_stats.py`) is the spine: read every line once, oldest first, and group them into themes with dates.
- Team PR titles give the "what the team built" half: `gh pr list -R <repo> --state merged --limit 500 --json author,title,createdAt`.
- Decision records, glossary, README and CLAUDE.md/AGENTS.md give the architecture and the vocabulary.
- PR bodies give measured numbers: `gh pr view <n> --json body` and look for "Before/After" tables.
- Ask the person for the two things git can't tell you: their role in their own words, and anything they want left out.
