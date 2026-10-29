---
name: browser-walkthrough
description: Check a feature or PR end to end in the user's real Chrome, screenshot every step, and publish a step-by-step walkthrough page with a short description per step. Use when asked to test, check or verify an implementation "on the real browser" with screenshots, or to turn a browser run into a shareable walkthrough or QA report.
---

# Browser walkthrough

A **walkthrough** is one honest run of the feature in the user's own Chrome (Claude in Chrome), recorded as a numbered sequence of real screenshots, each with a one-or-two-sentence caption, published as a private Artifact page. Every step proves something: the screenshot shows it, and where money or data moves, the server confirms it.

## 1. Scope the run

Read the change before touching the browser: the PR body (`gh pr view <n>`), the spec, and the diff. List the **steps** a person would take to exercise every behaviour the change adds, grouped into sections by role (admin setup, the actor who uses it, the admin reacting, the other party's view). Include the unhappy paths the change handles: declines, errors, edge statuses.

Done when every behaviour in the PR body maps to at least one step.

## 2. Prepare

- Load the Chrome tools in one `ToolSearch` call (`tabs_context_mcp`, `navigate`, `computer`, `find`, `javascript_tool`, `browser_batch`, `read_page`). Call `tabs_context_mcp` first; work in the session's tab group.
- Make a shots folder in the scratchpad and copy [scripts/grab.sh](scripts/grab.sh) beside it.
- Start what the run depends on and confirm it answers: webhook listeners (`stripe listen …`), queues, test-mode keys. Check a background listener's log for its ready line before step 1.
- **Roles**: when the run needs a second user (vendor, customer), log in with test credentials the project already uses (its e2e helpers, seed files). For WordPress, mint auth cookies with WP-CLI (`wp_generate_auth_cookie`) and set them with `document.cookie` after logging the current user out; restore the user's own session at the end.

## 3. Run and capture

For each step, drive the page, then capture with `computer` → `screenshot` with `save_to_disk: true` and `scale: 0.8`, and immediately run `grab.sh <NN-step-name>` so the newest saved screenshot lands in the shots folder under a sortable name. Batch the actions of one step in `browser_batch`.

Before each capture, make the frame honest and clean with `javascript_tool`:

- hide unrelated admin nags (`.notice`, `.update-nag`) but keep the feature's own notices;
- mask secrets and personal data the screen shows: API keys, real emails, tokens. Replace them with placeholders in the DOM, and say so on the page;
- zoom (`computer` → `zoom`, `save_to_disk`) for small UI: a row's actions, an order-notes column.

**Dialogs freeze the extension.** Before clicking anything that may call `confirm()` or `alert()` (delete, release, refund, approve links; grep the code for `confirm(`), run `window.confirm = () => true; window.alert = () => {};` in the page. If a dialog is already open, stop and ask the user to dismiss it.

**Verify server-side** after every state change: read the database or API (`wp db query`, `wp eval`, the Stripe CLI) and confirm the screenshot's claim (status, amount, payout id). A step whose server state disagrees with the screen is a **finding**, not a step.

Done when every step from section 1 has a screenshot in the shots folder, and every state change has been confirmed server-side.

## 4. Look at every shot

Read each image. Recapture any that shows a loading state, a stale notice, an unrelated popup, unmasked data, or the wrong scroll position. Note real bugs as findings: cosmetic (copy, layout), functional (wrong state), or expected-but-surprising (a deferral that is correct behaviour).

## 5. Publish

1. Write `steps.json` (format at the top of [scripts/build_page.py](scripts/build_page.py)): a title, a one-line lede, header facts (site, branch, orders), sections of steps (shot, title, caption, chips), and findings. Captions say what the screen shows and why it matters, in plain words, one or two sentences. Chips cite the spec section, ticket or commit the step proves.
2. Build: `python3 -I <skill-dir>/scripts/build_page.py <work-dir>`. It writes `index.html` and `files.json`.
3. Publish with the Artifact tool: `file_path` = `index.html`, `files` = the map in `files.json`, an `icon`, and a one-sentence `description`. The quickstart and design contract of the Artifact tool apply; the bundled template already follows them.
4. Republishing after fixes: replace the shot, edit the caption or the findings, rebuild, and publish the same `file_path` to keep the URL.

## 6. Report

Give the user the link, the findings ranked by severity, and what the run left behind (test orders, refunds, balance top-ups, a still-running listener), and offer to clean it up. Close the tabs you opened.
