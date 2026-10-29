"""Write a HyperFrames index.html from recorded takes: intro, a chapter card before each
chapter, the takes in order inside a browser frame, a caption panel driven by the
recorder's cue marks, a chapter rail, an outro, and (optional) one voiceover clip per beat.

Run:  python3 -I build_video.py <project-dir> <rec-out-dir> [--plan]

<project-dir> is a `hyperframes init` project. The script converts <rec-out-dir>/<take>.webm
to <project-dir>/assets/<take>.mp4 the first time (H.264, 30 fps, trimmed per "trim"), reads
<rec-out-dir>/marks.json, and reads <project-dir>/video.json:

{
  "eyebrow": "PR #63 · Shop",
  "heading": "Card checkout, recorded end to end",
  "intro": "One run in a real Chrome window against test mode: ...",
  "url_label": "shop.test · Stripe test mode",
  "chapters": [
    {"name": "Setup", "short": "Setup", "lede": "The admin turns it on.", "takes": ["01-settings"]}
  ],
  "trim": {"08a-refund": 18.9},                       # seconds to keep, per take (optional)
  "cue_fixes": [{"take": "01-settings", "title": "Payment settings", "t": 4.8}],   # optional
  "extra_cues": [{"take": "02-checkout", "t": 6.0, "title": "Checkout", "text": "..."}],
  "outro_title": "What the run left behind",
  "outro_rows": [["#101", "Paid · payout po_123"]],
  "outro_foot": "feature/branch · abc1234 · 29 Oct 2026"
}

Voiceover (optional) lives in <project-dir>/vo-lines.json, one line per beat:

  [{"id": "B01", "at": "intro", "offset": 0.3, "text": "..."},
   {"id": "B02", "at": "chapter:1", "offset": 0.3, "text": "..."},
   {"id": "B03", "at": "cue:02-checkout:Pay by card", "offset": 0.0, "text": "..."}]

Each line plays assets/vo/<id>.mp3 from its anchor (+ offset); a missing file is skipped.
--plan prints every line's window (time until the next line) and the word budget at
2.2 words/second, so the script can be written to fit before any speech is generated.
"""
import html
import json
import subprocess
import sys
from pathlib import Path

PROJECT = Path(sys.argv[1]).resolve()
REC = Path(sys.argv[2]).resolve()
PLAN = "--plan" in sys.argv
HERE = Path(__file__).resolve().parent

INTRO, CARD, OUTRO = 4.5, 3.4, 7.0
WORDS_PER_SECOND = 2.2

cfg = json.loads((PROJECT / "video.json").read_text())
assets = PROJECT / "assets"
assets.mkdir(exist_ok=True)


def probe(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                         capture_output=True, text=True, check=True).stdout
    return round(float(out), 3)


def esc(s):
    return html.escape(s, quote=True)


def ensure_mp4(take):
    mp4 = assets / f"{take}.mp4"
    if mp4.exists():
        return mp4
    src = REC / f"{take}.webm"
    if not src.exists():
        sys.exit(f"no recording for take {take}: {src}")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(src)]
    if take in cfg.get("trim", {}):
        cmd += ["-t", str(cfg["trim"][take])]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30", "-an",
            "-movflags", "+faststart", str(mp4)]
    subprocess.run(cmd, check=True)
    return mp4


marks = json.loads((REC / "marks.json").read_text())["marks"]
for fix in cfg.get("cue_fixes", []):
    for m in marks:
        if m["take"] == fix["take"] and m["title"] == fix["title"]:
            m["t"] = fix["t"]
marks += cfg.get("extra_cues", [])
marks.sort(key=lambda m: m["t"])

t = INTRO
cards, videos, captions, ticks, labels, tl = [], [], [], [], [], []
anchors = {"intro": 0.0}
chapter_starts = []
step = 0

for ci, ch in enumerate(cfg["chapters"], start=1):
    anchors[f"chapter:{ci}"] = t
    chapter_starts.append((t, ch.get("short", ch["name"])))
    cid = f"card-{ci}"
    cards.append(f'''<section id="{cid}" class="clip card" data-start="{t:.3f}" data-duration="{CARD:.3f}" data-track-index="3">
  <div class="card-num">{ci:02d}</div><div class="card-name">{esc(ch["name"])}</div><div class="card-lede">{esc(ch.get("lede", ""))}</div>
</section>''')
    tl += [
        f'tl.fromTo("#{cid} .card-num", {{opacity: 0, y: 24}}, {{opacity: 1, y: 0, duration: 0.45, ease: "power3.out"}}, {t + 0.05:.3f});',
        f'tl.fromTo("#{cid} .card-name", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.5, ease: "power3.out"}}, {t + 0.15:.3f});',
        f'tl.fromTo("#{cid} .card-lede", {{opacity: 0}}, {{opacity: 1, duration: 0.5}}, {t + 0.35:.3f});',
        f'tl.to("#{cid}", {{opacity: 0, duration: 0.35}}, {t + CARD - 0.35:.3f});',
    ]
    t += CARD

    for take in ch["takes"]:
        d = probe(ensure_mp4(take))
        vid = f"v-{take}"
        videos.append(f'<video id="{vid}" class="clip shot" src="assets/{take}.mp4" data-start="{t:.3f}" data-duration="{d:.3f}" data-track-index="0" muted playsinline></video>')
        tl.append(f'tl.fromTo("#{vid}", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {t:.3f});')

        cues = [m for m in marks if m["take"] == take]
        for i, m in enumerate(cues):
            anchors[f"cue:{take}:{m['title']}"] = t + max(0.0, m["t"] - 0.3)
            # The first caption covers the page load too, so the panel is never empty.
            start = t if i == 0 else t + max(0.0, m["t"] - 0.3)
            end = t + (cues[i + 1]["t"] - 0.3 if i + 1 < len(cues) else d)
            if end - start < 1.0:
                continue
            step += 1
            cap = f"cap-{step}"
            captions.append(f'''<div id="{cap}" class="clip cap" data-start="{start:.3f}" data-duration="{end - start:.3f}" data-track-index="2">
  <div class="cap-chapter">{ci:02d} · {esc(ch["name"])}</div>
  <div class="cap-title"><span class="cap-step">{step:02d}</span>{esc(m["title"])}</div>
  <p class="cap-text">{esc(m.get("text", ""))}</p>
</div>''')
            tl += [
                f'tl.fromTo("#{cap} .cap-title", {{opacity: 0, x: 18}}, {{opacity: 1, x: 0, duration: 0.4, ease: "power2.out"}}, {start + 0.02:.3f});',
                f'tl.fromTo("#{cap} .cap-text", {{opacity: 0, y: 8}}, {{opacity: 1, y: 0, duration: 0.45, ease: "power2.out"}}, {start + 0.15:.3f});',
            ]
        t += d

outro_start = t
anchors["outro"] = outro_start
TOTAL = round(outro_start + OUTRO, 3)

# Voiceover: one clip per beat at its anchor.
audio, plan = [], []
vo_file = PROJECT / "vo-lines.json"
if vo_file.exists():
    lines = json.loads(vo_file.read_text())
    for line in lines:
        if line["at"] not in anchors:
            sys.exit(f"voiceover {line['id']}: unknown anchor {line['at']!r}; anchors are intro, outro, chapter:N, cue:<take>:<title>")
        line["start"] = anchors[line["at"]] + line.get("offset", 0.0)
    lines.sort(key=lambda l: l["start"])
    for i, line in enumerate(lines):
        window = (lines[i + 1]["start"] if i + 1 < len(lines) else TOTAL) - line["start"]
        f = assets / "vo" / f"{line['id']}.mp3"
        dur = probe(f) if f.exists() else None
        plan.append((line, window, dur))
        if dur is None:
            print(f"voiceover {line['id']} missing, skipped")
            continue
        if dur > window:
            print(f"WARNING voiceover {line['id']} runs {dur:.1f}s into a {window:.1f}s window: shorten its text")
        audio.append(f'<audio id="vo-{line["id"]}" class="clip" src="assets/vo/{line["id"]}.mp3" data-start="{line["start"]:.3f}" data-duration="{dur:.3f}" data-track-index="5" data-volume="1"></audio>')

if PLAN:
    print(f"total {TOTAL:.1f}s")
    for line, window, dur in plan:
        words = len(line["text"].split())
        budget = int((window - 0.6) * WORDS_PER_SECOND)
        flag = "  TOO LONG" if words > budget else ""
        have = f"{dur:.1f}s" if dur else "—"
        print(f"{line['id']:5} {line['start']:7.2f}s  window {window:5.1f}s  words {words:2}/{budget:2}  audio {have}{flag}")
    sys.exit(0)

for s, name in chapter_starts:
    pct = s / TOTAL * 100
    ticks.append(f'<div class="tick" style="left:{pct:.3f}%"></div>')
    labels.append(f'<span class="chapter-label" style="left:{pct:.3f}%">{esc(name)}</span>')

tl += [
    f'tl.fromTo("#rail-fill", {{width: "0%"}}, {{width: "100%", duration: {TOTAL:.3f}, ease: "none"}}, 0);',
    'tl.fromTo("#intro .intro-eyebrow", {opacity: 0, y: 16}, {opacity: 1, y: 0, duration: 0.5, ease: "power3.out"}, 0.2);',
    'tl.fromTo("#intro h1", {opacity: 0, y: 28}, {opacity: 1, y: 0, duration: 0.6, ease: "power3.out"}, 0.35);',
    'tl.fromTo("#intro .intro-sub", {opacity: 0}, {opacity: 1, duration: 0.6}, 0.8);',
    f'tl.to("#intro", {{opacity: 0, duration: 0.4}}, {INTRO - 0.4:.3f});',
    f'tl.fromTo("#outro .outro-row", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.45, stagger: 0.18, ease: "power2.out"}}, {outro_start + 0.3:.3f});',
]

rows = "\n".join(f'        <div class="outro-row"><b>{esc(a)}</b><span>{esc(b)}</span></div>' for a, b in cfg.get("outro_rows", []))
page = (HERE / "video.tpl").read_text()
for key, value in {
    "{{TOTAL}}": f"{TOTAL:.3f}", "{{INTRO}}": f"{INTRO:.3f}",
    "{{OUTRO_START}}": f"{outro_start:.3f}", "{{OUTRO}}": f"{OUTRO:.3f}",
    "{{URL_LABEL}}": esc(cfg.get("url_label", "")), "{{EYEBROW}}": esc(cfg.get("eyebrow", "")),
    "{{HEADING}}": esc(cfg["heading"]), "{{INTRO_TEXT}}": esc(cfg.get("intro", "")),
    "{{OUTRO_TITLE}}": esc(cfg.get("outro_title", "What the run left behind")), "{{OUTRO_ROWS}}": rows,
    "{{OUTRO_FOOT}}": esc(cfg.get("outro_foot", "")),
    "{{CARDS}}": "\n".join(cards), "{{VIDEOS}}": "\n".join(videos), "{{AUDIO}}": "\n".join(audio),
    "{{CAPTIONS}}": "\n".join(captions), "{{TICKS}}": "\n".join(ticks), "{{LABELS}}": "\n".join(labels),
    "{{TIMELINE}}": "\n      ".join(tl),
}.items():
    page = page.replace(key, value)

(PROJECT / "index.html").write_text(page)
print(f"total {TOTAL:.1f}s, {step} captions, {len(videos)} takes, {len(audio)} voiceover lines")
