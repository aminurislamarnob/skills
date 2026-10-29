"""Build a walkthrough page (index.html) and its Artifact files map (files.json).

Run: python3 -I build_page.py <work-dir>

<work-dir> holds steps.json and a shots/ folder of screenshots. steps.json:

{
  "title": "Checkout Walkthrough",                  # browser tab / gallery name, 2-4 words
  "eyebrow": "PR #63 · feature/branch",
  "heading": "Stripe checkout, step by step",
  "lede": "One run in a real Chrome window against test mode: ...",
  "facts": ["Site <code>shop.test</code>", "Orders <code>#101</code> <code>#102</code>"],   # HTML allowed
  "sections": [
    {"name": "Setup", "lede": "The admin turns it on.", "steps": [
      {"shot": "01-settings.jpg", "title": "Gateway settings",
       "caption": "Enabled, test mode on, keys saved. The publishable key is masked.",
       "chips": ["§4.1", "ADR-0004"]}
    ]}
  ],
  "notes_title": "Found during the run",            # optional
  "notes": [                                        # optional findings
    {"tag": "cosmetic", "title": "Decline shows twice.", "text": "Under the card form (step 18)."},
    {"tag": "fixed", "title": "...", "text": "..."}
  ]
}

Steps are numbered in order across sections. Tags "fixed" render in the accent colour,
every other tag in the warning colour.
"""
import html
import json
import sys
from pathlib import Path

WORK = Path(sys.argv[1]).resolve()
HERE = Path(__file__).resolve().parent


def esc(s):
    return html.escape(s, quote=True)


spec = json.loads((WORK / "steps.json").read_text())
shots_dir = WORK / "shots"

toc, body, used = [], [], []
n = 0
for si, section in enumerate(spec["sections"], start=1):
    sid = f"s{si}"
    toc.append(f'<a href="#{sid}">{esc(section["name"])}</a>')
    cards = []
    for step in section["steps"]:
        n += 1
        shot = step["shot"]
        if not (shots_dir / shot).exists():
            sys.exit(f"missing screenshot: shots/{shot} (step {n}: {step['title']})")
        used.append(shot)
        chips = "".join(f'<span class="chip">{esc(c)}</span>' for c in step.get("chips", []))
        cards.append(f'''<figure class="step" id="step-{n}">
  <button class="shot" type="button" data-src="shots/{esc(shot)}" aria-label="Enlarge step {n}: {esc(step["title"])}"><img src="shots/{esc(shot)}" alt="{esc(step["title"])}" loading="lazy"></button>
  <figcaption><div class="cap-head"><span class="num">{n:02d}</span><h3>{esc(step["title"])}</h3></div><p>{esc(step["caption"])}</p><div class="chips">{chips}</div></figcaption>
</figure>''')
    body.append(f'''<section id="{sid}"><header class="sec-head"><h2>{esc(section["name"])}</h2><p>{esc(section.get("lede", ""))}</p></header>
<div class="steps">{"".join(cards)}</div></section>''')

notes = ""
if spec.get("notes"):
    items = []
    for note in spec["notes"]:
        cls = "tag fixed" if note.get("tag") == "fixed" else "tag"
        tag = f'<span class="{cls}">{esc(note["tag"])}</span>' if note.get("tag") else ""
        items.append(f'<li>{tag}<b>{esc(note["title"])}</b> {esc(note.get("text", ""))}</li>')
    notes = f'''<aside class="notes">
  <h2>{esc(spec.get("notes_title", "Found during the run"))}</h2>
  <ul>
    {"".join(items)}
  </ul>
</aside>'''

page = (HERE / "template.html").read_text()
for key, value in {
    "{{TITLE}}": esc(spec["title"]),
    "{{EYEBROW}}": esc(spec.get("eyebrow", "")),
    "{{HEADING}}": esc(spec["heading"]),
    "{{LEDE}}": esc(spec.get("lede", "")),
    "{{FACTS}}": "\n".join(f"    <li>{f}</li>" for f in spec.get("facts", [])),
    "{{COUNT}}": str(n),
    "{{TOC}}": "".join(toc),
    "{{BODY}}": "\n".join(body),
    "{{NOTES}}": notes,
}.items():
    page = page.replace(key, value)

(WORK / "index.html").write_text(page)
files = {f"shots/{s}": str(shots_dir / s) for s in used}
(WORK / "files.json").write_text(json.dumps(files, indent=1))
print(f"{n} steps → {WORK / 'index.html'}; files map → {WORK / 'files.json'}")
