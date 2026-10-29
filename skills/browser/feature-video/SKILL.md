---
name: feature-video
description: Record a feature or PR working end to end in a real browser, edit the footage into a captioned walkthrough video with HyperFrames, and narrate it with an ElevenLabs voice. Use when asked for a screen recording, demo video or video walkthrough of an implementation or current code changes, or to add a voiceover to one.
---

# Feature video

A **feature video** is real footage of the change working: a headed Chrome driven by Playwright through the live site, one **take** per role, with a drawn cursor and click ripples. HyperFrames turns the takes into one film: an intro, a chapter card before each chapter, captions timed to **cues** the recorder marked the moment each step appeared, a chapter rail, and an outro stating what the run left behind. An ElevenLabs voice reads one line per beat.

Needs: Node.js 22+, FFmpeg, Playwright (`npm i -D playwright`) with Google Chrome or Chromium, HyperFrames (`npx hyperframes`, see the `hyperframes-cli` skill), and for narration the ElevenLabs connector. Scripts live in this skill's `scripts/` folder; work in the scratchpad.

## 1. Script the run

Read the change: the PR body, spec and diff. Write the **shot list**: chapters (setup, the actor's flow, the admin's reaction, edge cases, the other party's view), each made of takes, each take a sequence of steps with the cue title and one-line caption it will carry. Cover the unhappy paths the change handles.

Done when every behaviour in the PR body is a step with a cue.

## 2. Prepare the site

`docs/agents/wordpress-site.md`, when it exists, names the site URL (`BASE_URL`), the WordPress root (`WP_PATH`), the users each role logs in as, and the services to start; read it first. Start what the run depends on and confirm it answers before recording: webhook listeners, queues, test-mode keys, a balance the flow needs. When a CLI's login has expired, prefer the project's own saved test key passed through the environment over asking the user to log in. Confirm the users each take logs in as exist.

## 3. Record

Copy [scripts/example-scenario.cjs](scripts/example-scenario.cjs) to the scratchpad and write the real scenario: one `rec.take()` block per take, `take.mark()` at the moment each step is on screen, `rec.keepNotices` and `rec.masks` to keep the frame on the feature and mask secrets and personal data. The API is documented at the top of [scripts/record.cjs](scripts/record.cjs).

```bash
BASE_URL=https://site.test WP_PATH=/path/to/wordpress \
  node <skill-dir>/scripts/record.cjs scenario.cjs rec-out
```

Run it from a directory where `playwright` resolves. A Chrome window opens on the user's screen; tell them it will. Pass state between takes (an order id) through variables in the scenario.

**Re-record one take** by naming it: `node record.cjs scenario.cjs rec-out 08b-approve`. The other takes and their cues are kept. When a take stalls part-way, keep its good start with `"trim"` in `video.json` and record the rest as a new take.

**Verify** after recording: read the server state each step claims (statuses, amounts, payout ids, webhook responses in the listener log). Extract one frame per cue (`ffmpeg -ss <t> -i take.webm -frames:v 1`), tile them, and look: every cue's frame must show what its caption says.

Done when every take is saved, every cue frame matches its caption, and the server confirms every state change.

## 4. Edit with HyperFrames

1. `npx hyperframes init video --non-interactive --skip-skills --resolution landscape`, then write `video/video.json` (format at the top of [scripts/build_video.py](scripts/build_video.py)).
2. `python3 -I <skill-dir>/scripts/build_video.py video rec-out` converts the takes to MP4 and writes `index.html`.
3. `npx hyperframes check --json`, then fix every error. Then `npx hyperframes snapshot --at <t,…>` at an intro, a chapter card, a few mid-take moments and the outro, and read the contact sheet.
4. Fix **cue drift**: the recorder marks a step after it waits for the page, so a caption can lag its screen. Tile one frame per second of the take (`ffmpeg -vf fps=1,scale=320:-1` then `tile=7x4`), read the second the screen changes, and set it in `cue_fixes`; add a missing step with `extra_cues`. Rebuild.

Done when `check` passes with 0 errors and every snapshot shows the caption matching the footage.

## 5. Narrate

Follow [references/voiceover.md](references/voiceover.md): write the lines to fit their windows, generate them with ElevenLabs, collect the audio into `video/assets/vo/`, rebuild. Skip this step when the user asked for a silent video.

## 6. Render and verify

```bash
cd video && npx hyperframes render --quality delivery --output <name>.mp4
```

Confirm with `ffprobe` that the duration equals the root `data-duration` and that there is an audio stream when narrated; pull a frame from every chapter and read them; measure the narration with `volumedetect` (see the voiceover reference).

Give the user the MP4 path, its length, what the run created on the site (orders, refunds, top-ups) and what is still running (listeners), and any missing voiceover lines with their cost.

## HyperFrames gotchas

- Keep templates outside the project root or name them `*.tpl`: a second root HTML file with `data-composition-id` fails lint (`multiple_root_compositions`).
- Use only fonts the renderer resolves (Helvetica Neue, Arial, Inter, JetBrains Mono, SF Mono, Menlo); an unknown family fails `font_family_without_font_face`.
- Text that sits outside its box fails `text_box_overflow`: keep labels in their own sized container, not hanging off a thin bar.
- `nested_structure_needs_subcomposition` and `line_unread` warnings are acceptable for this layout; errors are not.
