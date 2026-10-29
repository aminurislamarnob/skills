# Voiceover with ElevenLabs

Narration is **one clip per beat**, not one long track: each line starts when its step appears on screen and ends before the next line starts, so the voice stays in sync with the footage however the takes are paced.

## 1. Write the lines to fit

1. Write `vo-lines.json` in the project (format at the top of `build_video.py`): an intro line, one line per chapter card, one line per cue that deserves narration, an outro line. Anchor each to `intro`, `outro`, `chapter:N` or `cue:<take>:<title>`, with a small `offset` (0.3 s after a card or the intro).
2. Run `build_video.py <project> <rec-out> --plan`. Every line prints its window and a word budget at 2.2 words per second. Rewrite any line marked `TOO LONG`; merge a beat into its neighbour when its window is under ~3 s.

Lines are plain, present tense, one or two short sentences, saying what the viewer sees and why it matters ("The bank declines it. The message shows once, and nothing is charged."). Spell out what a voice would stumble on: "fifty dollars", "3D Secure", "seven days".

Done when `--plan` shows no `TOO LONG`.

## 2. Generate

The ElevenLabs connector tools are deferred: load `creative_list_voices`, `creative_create_flow`, `creative_generate_speech` and `creative_get_flow_run_status` in one `ToolSearch` call.

1. **Voice**: `creative_list_voices` with `languages: ["en"]`, `use_cases: ["informative_educational"]` and a search such as "clear narrator explainer". Pick a calm product-walkthrough narrator and tell the user which one; they can switch it on the flow later.
2. **Flow**: `creative_create_flow` once, named after the video; pass its `flow_id` to every generation so all lines live together.
3. **Credits**: a line costs about one credit per character per take, and each call makes two takes by default, so the whole script costs about 2 × its character count. Generate the intro line first, poll it, and read the `credits` it reports; if the account's remaining quota looks short of the total, tell the user the cost before generating the rest.
4. **Generate** every line with `creative_generate_speech` (model `eleven_v4`, the chosen `voice_id`), independent calls in parallel. Never call it twice for the same line to retry: that starts and charges a second generation.

## 3. Collect

Poll `creative_get_flow_run_status` with the lines' first-take `session_ids` (at most 20 per call) until `all_completed` or `has_failures`. Responses with many sessions exceed the tool-output limit and are saved to a file under the session's `tool-results/` folder; that is the convenient path: parse the file instead of copying signed URLs by hand.

```bash
python3 -I - <<'PY'
import glob, json, urllib.request
done = {}
for f in glob.glob('<tool-results dir>/mcp-claude_ai_ElevenLabs-creative_get_flow_run_status-*.txt'):
    for g in json.load(open(f))['generations']:
        if g['status'] == 'completed':
            done.setdefault(g['prompt'], g['content_url'])
for line in json.load(open('vo-lines.json')):
    url = done.get(line['text'])
    if url:
        urllib.request.urlretrieve(url, f"assets/vo/{line['id']}.mp3")
    else:
        print('missing', line['id'])
PY
```

The URLs are signed and expire after about two hours. A failed first take often has a completed second take in the paired session: poll those before declaring a line missing. A line that failed with "exceeds your quota" stays missing until the account has credits: the build skips it, and the rest of the video still renders.

## 4. Check the mix

After rendering, confirm the audio is where the lines are:

```bash
ffmpeg -hide_banner -nostats -ss <line start> -t <line duration> -i out.mp4 -vn -af volumedetect -f null /dev/null 2>&1 | grep mean_volume
```

Narration sits around −23 dB mean; a window with no line reads about −91 dB.
