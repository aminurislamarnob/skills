Quickstart:

```bash
npx skills add aminurislamarnob/claude-plugins --skill=feature-video
```

Or, as part of the Claude Code plugin: `/plugin install aminurislamarnob-skills@aminurislamarnob`.

[Source](../../skills/browser/feature-video/SKILL.md)

## What it does

`feature-video` records a feature working in a real browser (headed Chrome driven by Playwright, with a visible cursor and click ripples), edits the footage into a captioned walkthrough video with [HyperFrames](https://hyperframes.heygen.com), and narrates it with an ElevenLabs voice, one line per on-screen step.

Captions and voice lines are timed to cues the recorder marks at the moment each step appears, and every cue's frame is checked against its caption before the film is rendered, so the words never say something the screen doesn't show.

## When to reach for it

Type `/feature-video`, or the agent reaches for it automatically when asked for a screen recording, demo video or video walkthrough of an implementation or the current changes, or to add a voiceover to one.

Reach for it when the audience wants to watch rather than read: a client demo, a PR you want to explain, a release announcement. For a page of screenshots a reviewer can scan, use [browser-walkthrough](./browser-walkthrough.md) instead.

## Before you start

- Node.js 22+, FFmpeg, Google Chrome (or Chromium) and Playwright (`npm i -D playwright`).
- HyperFrames, which runs through `npx hyperframes`; `npx hyperframes doctor` checks the setup.
- For WordPress logins, `WP_PATH` set to the site's WordPress root; Claude signs in with WP-CLI, so no passwords are needed.
- For the voiceover, the ElevenLabs connector with credits: about two credits per character of script (a 4–5 minute video is about 5,000).

## Takes and cues

The leading ideas are the **take**, one recorded session per role, and the **cue**, the marked moment inside a take at which a step is on screen. Claude writes a shot list (chapters, takes, steps), records each take in a visible Chrome window, verifies the server state and one frame per cue, builds the film with intro, chapter cards, timed captions, a chapter rail and an outro, fixes captions that lag the screen, writes and generates one voice line per step sized to fit before the next, renders the MP4 and checks its length, frames and audio.

You get a 1080p MP4 (with narration when asked), the HyperFrames project for later edits, the raw takes, and a note of anything still missing.

## Tips

- A Chrome window opens on your screen while it records; let it run.
- The run creates real test data (orders, refunds); Claude lists it at the end.
- "Re-record the refund part only" re-records one take and keeps the rest.
- If the ElevenLabs account runs out of credits, the video still renders with the lines it has; ask for the missing ones after topping up.
- To change wording or timing later, ask for the edit; Claude rebuilds from the saved project without recording again.

## Where it fits

One half of a pair with [browser-walkthrough](./browser-walkthrough.md): both prove a change in a real browser, that one as a page, this one as a film. Record on a [wp-worktree](../wordpress/wp-worktree.md) site when the run will leave orders behind. The whole set is in the [README](../../README.md#reference).
