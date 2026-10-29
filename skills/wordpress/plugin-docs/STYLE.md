# Docs style

The house style of the StoreSuite docs. Copy its voice; when unsure, mirror the bundled pages in [examples/](examples/) or the live page at `https://storesuite.dev/docs/<slug>.md`.

## Voice

- Second person, present tense, active: "Click **Add Coupon**. Only the top three fields are required."
- Talk about outcomes, not implementation. Say "the jobs page lists every open position", not "the shortcode runs a WP_Query". Name a shortcode, hook or option only where the reader types or picks it.
- Confident and short. One idea per sentence, 2–4 sentences per paragraph. Leave out marketing adjectives ("powerful", "seamless").
- Use a plain hyphen with spaces (` - `) as the dash, matching StoreSuite.
- Wrap prose at about 80 columns.

## Page anatomy

```mdx
---
title: Coupons
description: Create and manage WooCommerce discount codes - types, restrictions, usage limits, and status.
icon: Ticket
---

One or two sentences, no heading: what this area is for and where to find it
(**Products** in the sidebar / **WooCommerce → StoreSuite** in wp-admin).

## The coupons list

![The coupons list](/docs/images/coupons-list.jpg)

| Column | What it tells you |
| --- | --- |
| **Code** | The code customers type at checkout |

## Creating a coupon

![The coupon form](/docs/images/coupon-form.jpg)

Click **Add Coupon**. …

### General

- **Coupon Code** *(required)* - or click **Generate coupon code** for a random one.
- **Expiry Date** - the coupon expires at 00:00:00 on that date.

<Callout title="Manual orders too">
Cross-feature tip, linking [the order editor](/docs/orders).
</Callout>
```

- **Frontmatter**: `title` (Title Case, 1–3 words), `description` (one sentence; it is the page subtitle and the search snippet), `icon` (a [Lucide](https://lucide.dev/icons) name in PascalCase: `Briefcase`, `Settings`, `Download`, `LayoutGrid`, `CircleQuestionMark`).
- **Headings** follow the reader's path through the screen: the list → creating → editing → options. `##` for screens or tasks, `###` for sections or tabs within one. Use noun phrases or gerunds ("The jobs list", "Creating a job"), never questions, except on the FAQ.
- **Images** sit directly under the heading they illustrate. Alt text is a short noun phrase: `![The appearance settings tab](…)`.
- Length: 30–140 lines. Split a page past that by sub-feature.

## Patterns

- **UI labels** in bold, verbatim, including capitalisation: **Save Changes**, **Jobs Per Page**.
- **Navigation paths** with `→`: **Jobs → Settings → Appearance**.
- **Fields** as a bullet list: `**Label** *(required)* - what it does, its default, its effect`. Group by the screen's own sections with `###`.
- **List screens** as a `| Column | What it tells you |` table, followed by a short paragraph on search, filters, row actions and bulk actions.
- **Steps** as a numbered list only for real sequences (install, a wizard). Use prose for "click X, then Y".
- **Options with several values** as an inline list: "**Full Time**, **Part Time**, or **Contract**".
- **Code** in backticks only for things the reader types or copies: shortcodes `[jobpress]`, attributes `design="2"`, capabilities `manage_options`. Give shortcode examples a fenced block.
- **Callouts**: `<Callout title="Tip">` (or `type="warn"` for data-loss or breaking caveats). At most two per page, for cross-feature tips, requirements, or "setting up for a client?" advice. Keep core instructions out of callouts.
- **Links**: internal as `/docs/<slug>` or `/docs/<slug>#<heading-id>`, with the heading id as the lowercased, hyphenated heading text. Link the first mention of another feature on a page.

## Required pages

- **index** ("Introduction", icon `Book`): one-paragraph pitch, hero screenshot, `## What you get` (a bulleted list, each item `**[Feature](/docs/slug)** - one line`), `## Requirements` table (WordPress, PHP, dependencies), `## Next steps` linking installation.
- **installation** (icon `Download`): from WordPress.org (numbered), from a zip (numbered), `## What activation does` (pages, tables, options it creates), a requirements callout, a first-check section ("Confirm your jobs page"), `## Troubleshooting 404s` (re-save permalinks).
- **settings** (icon `Settings`): one `##` per tab with its screenshot and field list. Link out to feature pages instead of repeating them.
- **faq** (icon `CircleQuestionMark`): `## Question?` headings, 2–4 sentence answers, linking the feature page. Cover price/licence, requirements, compatibility (themes, builders, caching), data/privacy, uninstall behaviour, and the common 404 fix.
