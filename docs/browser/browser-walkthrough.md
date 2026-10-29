Quickstart:

```bash
npx skills add aminurislamarnob/claude-plugins --skill=browser-walkthrough
```

Or, as part of the Claude Code plugin: `/plugin install aiarnob-skills@aminurislamarnob`.

[Source](../../skills/browser/browser-walkthrough/SKILL.md)

## What it does

`browser-walkthrough` checks a feature or PR end to end in your own Chrome, through the Claude in Chrome extension, screenshots every step, and publishes a private page (an Artifact) with a short caption per step and a list of what the run found.

Every step must prove something. The screenshot shows it, and where money or data moves the server is asked to confirm it, so a step whose database or API state disagrees with the screen is recorded as a finding, not as a step.

## When to reach for it

Type `/browser-walkthrough`, or the agent reaches for it automatically when asked to test, check or verify an implementation "on the real browser" with screenshots, or to turn a browser run into a shareable walkthrough or QA report.

Reach for it when you want proof a change works that a reviewer or a client can read in a minute. For a film of the same run, with captions and a voice, use [feature-video](./feature-video.md) instead.

## Before you start

- The Claude in Chrome extension, installed and connected to the session. If several browsers are connected, Claude asks which one to use.
- The site running, with test-mode keys for any payment provider.
- Anything the flow depends on, such as a webhook listener (`stripe listen …`), started, or let Claude start it.
- Python 3, for building the page.

## One honest run

The leading idea is the **walkthrough**: one honest run of the feature, as a numbered sequence of real screenshots with a caption each. Claude reads the PR, spec and diff and lists the steps, including declines and errors; runs each step in a tab of your Chrome and saves a screenshot, hiding unrelated admin notices and masking keys and emails; checks the server after every state change; looks at every shot and retakes any that shows a loading state or stale notice; then builds and publishes the page.

You get a private link, the findings ranked by severity, and a list of what the run left on the site (test orders, refunds, a still-running listener), with an offer to clean up. The page stays private until you share it from its Share menu.

## Tips

- Chrome tabs open in a group Claude manages; your other tabs are left alone.
- If a browser dialog (OK/Cancel) appears and Chrome stops responding, click it; Claude pre-answers dialogs for the steps it knows about.
- After a fix, ask for "retake step 18 and republish"; the link stays the same.

## Where it fits

One half of a pair with [feature-video](./feature-video.md): both prove a change in a real browser, this one as a page you can read, that one as a film you can watch. Run it on a [wp-worktree](../wordpress/wp-worktree.md) site when the run will create orders or refunds you don't want on the main install. The whole set is in the [README](../../README.md#reference).
