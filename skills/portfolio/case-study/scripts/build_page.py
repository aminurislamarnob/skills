"""Build a case-study page (index.html) and its files map (files.json) from case.json.

Run: python3 -I build_page.py <work-dir> [--standalone]

<work-dir> holds case.json, the stats.json that git_stats.py wrote, and any images it names
(img/...). Without --standalone the page is a fragment (title, style, body content), which is
what Claude's Artifact tool wraps in its own document. --standalone writes a full document with
doctype, charset and viewport, for opening locally or any static host.

Text fields accept a little inline markup: **bold**, `code` and [text](https://url). Everything
else is escaped. Raw HTML is accepted only in "svg" blocks.

case.json:

{
  "title": "Storefront Platform",                     # 2-4 word page name: browser tab, gallery
  "lang": "en",
  "eyebrow": "Case study · Headless commerce",
  "headline": "A fast storefront the owner still runs from WordPress",
  "lede": "Since June I've led ... A demo runs at [demo.example.com](https://demo.example.com).",
  "facts": [["My role", "Team lead and developer"], ["Team", "6 engineers, 2 repositories"]],
  "shots": {                                           # optional hero screenshots
    "main":  {"src": "img/home-desktop.jpg", "w": 1440, "h": 900, "alt": "..."},
    "phone": {"src": "img/home-phone.jpg", "w": 390, "h": 844, "alt": "..."}   # optional
  },
  "shot_note": "The demo store on desktop and a phone. Captured 7 Nov 2026.",
  "theme": {                                           # optional; see DEFAULT_LIGHT / DEFAULT_DARK
    "light": {"accent": "#0A6372", "band": "#0D2A35"},
    "dark":  {"accent": "#5EC7D4"},
    "fonts": {"url": "https://fonts.googleapis.com/css2?family=...", "display": "\"Bricolage Grotesque\"",
              "body": "\"Figtree\"", "mono": "\"JetBrains Mono\""}
  },
  "sections": [
    {"rail": "The months", "when": "22 Jun to 7 Nov", "heading": "What the five months looked like",
     "blocks": [ ...blocks... ]}
  ],
  "footer": {"heading": "Where the numbers come from", "text": "...",
             "stack": ["Next.js", "WooCommerce"], "byline": "Jane Doe, team lead at Example."}
}

Blocks, in the order they should appear in a section:

  {"type": "p", "text": "..."}
  {"type": "h3", "text": "..."}
  {"type": "list", "items": ["**Lead,** rest of the line", "..."]}
  {"type": "defs", "items": [["Term", "What it means here"], ...]}
  {"type": "table", "head": ["Rule", "What it prevents"], "rows": [["...", "..."]], "numeric": [1]}
  {"type": "log", "rows": [["22 Jun", "Plugin, first commit"], ...]}
  {"type": "image", "src": "img/x.jpg", "w": 1440, "h": 900, "alt": "...", "caption": "..."}
  {"type": "svg", "file": "diagrams/arch.svg", "caption": "..."}      # or "svg": "<svg ...>"
  {"type": "chart", "me_label": "My commits", "team_label": "Team commits", "caption": "..."}
  {"type": "totals", "items": [["708 of 1,179", "commits, both repos"], ...]}
  {"type": "ranges", "max": 6, "unit": "s", "before_label": "Before", "after_label": "After",
   "rows": [{"label": "Checkout, first byte", "text": "about 2.5 s → about 20 ms",
             "before": [2.5, 2.5], "after": [0.02, 0.02]}], "caption": "..."}
  {"type": "split", "left": {"title": "What I built", "items": [...]},
                    "right": {"title": "What the team built", "items": [...]}}

"chart" draws stats.json's series (days, weeks or months) as stacked columns, mine under the
team's, to one scale. "ranges" draws before/after bars on one axis from 0 to "max".
"""
import datetime as dt
import html
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

DEFAULT_LIGHT = {
    "paper": "#EDF1F2", "surface": "#FAFCFC", "ink": "#10212A", "muted": "#4C5D65", "rule": "#C4D0D4",
    "accent": "#0A6372", "me": "#0E7D8D", "team": "#C47F00", "before": "#9AA8AE", "note": "#E0EBED",
    "band": "#0D2A35", "band-ink": "#F1F5F4", "band-muted": "#AFC4CA", "band-rule": "#2A4955", "highlight": "#F2B9AA",
}
DEFAULT_DARK = {
    "paper": "#0B171D", "surface": "#13232B", "ink": "#E5EDEF", "muted": "#A0B2B8", "rule": "#2C3F47",
    "accent": "#5EC7D4", "me": "#2AA3B3", "team": "#C08A1E", "before": "#66767C", "note": "#183039",
}
DEFAULT_FONTS = {
    "url": "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800"
           "&family=Figtree:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap",
    "display": '"Bricolage Grotesque"', "body": '"Figtree"', "mono": '"JetBrains Mono"',
}

files = {}


def esc(s):
    return html.escape(str(s), quote=True)


def inline(s):
    """Escape, then allow **bold**, `code` and [text](https://url)."""
    parts = re.split(r"(`[^`]+`)", str(s))
    out = []
    for p in parts:
        if len(p) > 1 and p.startswith("`") and p.endswith("`"):
            out.append(f"<code>{esc(p[1:-1])}</code>")
            continue
        t = esc(p)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', t)
        out.append(t)
    return "".join(out)


def use_file(work, src):
    if not os.path.exists(os.path.join(work, src)):
        print(f"warning: {src} not found in {work}", file=sys.stderr)
    files[src] = src
    return esc(src)


def img(work, i, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{use_file(work, i["src"])}" width="{int(i["w"])}" height="{int(i["h"])}" '
            f'alt="{esc(i.get("alt", ""))}">')


def figcap(b):
    return f'<figcaption>{inline(b["caption"])}</figcaption>' if b.get("caption") else ""


def nice_axis(v):
    """A top value and tick step with whole-number ticks, three to five of them."""
    v = max(v, 1)
    for step in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 5000, 10000):
        if v / step <= 5:
            return step * math.ceil(v / step), step
    return v, v


def chart(stats, b):
    s = stats.get("series")
    if not s:
        raise SystemExit("a chart block needs stats.json with a series (run git_stats.py first)")
    rows, gran = s["rows"], s["granularity"]
    n = len(rows)
    X0, X1, BASE, H = 52, 806, 236, 192
    top, tick = nice_axis(max((r["me"] + r["team"]) for r in rows))
    k = H / top
    step = (X1 - X0) / n
    cw = step * 0.82
    me_total = sum(r["me"] for r in rows)
    team_total = sum(r["team"] for r in rows)
    out = []
    for i in range(int(top // tick) + 1):
        v = tick * i
        y = BASE - v * k
        label = f"{v:,}"
        out.append(f'<line class="g-grid" x1="{X0-6}" y1="{y:.1f}" x2="{X1}" y2="{y:.1f}"/>'
                   f'<text class="g-ax" x="{X0-12}" y="{y+4:.1f}" text-anchor="end">{label}</text>')
    last_month = None
    for i, r in enumerate(rows):
        d = dt.date.fromisoformat(r["start"])
        x = X0 + i * step + (step - cw) / 2
        m, t = r["me"], r["team"]
        when = {"day": f"{d.day} {d:%b}", "week": f"Week of {d.day} {d:%b}", "month": f"{d:%B %Y}"}[gran]
        out.append(f"<g><title>{when}: {m} mine, {t} team</title>")
        if m:
            out.append(f'<rect class="c-me" x="{x:.1f}" y="{BASE-m*k:.1f}" width="{cw:.1f}" height="{m*k:.1f}"/>')
        if t:
            out.append(f'<rect class="c-team" x="{x:.1f}" y="{BASE-(m+t)*k:.1f}" width="{cw:.1f}" height="{t*k:.1f}"/>')
        if (m + t) and n <= 31:
            out.append(f'<text class="g-v" x="{x+cw/2:.1f}" y="{BASE-(m+t)*k-6:.1f}" text-anchor="middle">{m+t}</text>')
        out.append("</g>")
        if gran == "day":
            out.append(f'<text class="g-m" x="{x+cw/2:.1f}" y="{BASE+22}" text-anchor="middle">{d.day} {d:%b}</text>')
        elif gran == "month":
            out.append(f'<text class="g-m" x="{x+cw/2:.1f}" y="{BASE+22}" text-anchor="middle">{d:%b}</text>')
        elif f"{d:%Y-%m}" != last_month:
            out.append(f'<line class="g-tick" x1="{x:.1f}" y1="{BASE}" x2="{x:.1f}" y2="{BASE+10}"/>'
                       f'<text class="g-m" x="{x:.1f}" y="{BASE+26}">{d:%b}</text>')
            last_month = f"{d:%Y-%m}"
    out.append(f'<line class="g-base" x1="{X0-6}" y1="{BASE}" x2="{X1}" y2="{BASE}"/>')
    unit = {"day": "day", "week": "week", "month": "month"}[gran]
    aria = (f"Commits per {unit} from {s['first']} to {s['last']}: {me_total} mine and {team_total} by the team. "
            f"Busiest {unit}: " + max(rows, key=lambda r: r["me"] + r["team"])["start"] + ".")
    svg = f'<svg viewBox="0 0 820 {BASE+40}" role="img" aria-label="{esc(aria)}">' + "".join(out) + "</svg>"
    me_l = esc(b.get("me_label", "My commits"))
    team_l = esc(b.get("team_label", "Team commits"))
    return (f'<figure><div class="chart"><div class="legend"><span><i style="background:var(--me)"></i>{me_l} ({me_total:,})</span>'
            f'<span><i style="background:var(--team)"></i>{team_l} ({team_total:,})</span></div>'
            f'<div class="in">{svg}</div></div>{figcap(b)}</figure>')


def ranges(b):
    mx = float(b["max"])
    unit = b.get("unit", "")
    rows = []
    for r in b["rows"]:
        bars = []
        for cls, key, word in (("b", "before", "Before"), ("a", "after", "After")):
            lo, hi = r[key]
            bars.append(f'<div class="bar {cls}" title="{word}: {lo:g}–{hi:g} {esc(unit)}" '
                        f'style="left:{lo/mx*100:.2f}%;width:{(hi-lo)/mx*100:.2f}%"></div>')
        rows.append(f'<div><div class="row-h">{inline(r["label"])}<span>{inline(r.get("text", ""))}</span></div>'
                    f'<div class="track">{"".join(bars)}</div></div>')
    axis = "".join(f"<span>{mx*i/4:g} {esc(unit)}</span>" for i in range(5))
    legend = (f'<div class="legend" style="margin:0"><span><i style="background:var(--before)"></i>{esc(b.get("before_label", "Before"))}</span>'
              f'<span><i style="background:var(--me)"></i>{esc(b.get("after_label", "After"))}</span></div>')
    return f'<figure><div class="ranges">{legend}{"".join(rows)}<div class="axis">{axis}</div></div>{figcap(b)}</figure>'


def block(work, stats, b):
    t = b["type"]
    if t == "p":
        cls = ' class="muted"' if b.get("muted") else ""
        return f"<p{cls}>{inline(b['text'])}</p>"
    if t == "h3":
        return f"<h3>{inline(b['text'])}</h3>"
    if t == "list":
        return '<ul class="tight">' + "".join(f"<li>{inline(i)}</li>" for i in b["items"]) + "</ul>"
    if t == "defs":
        return '<dl class="defs">' + "".join(f"<div><dt>{inline(a)}</dt><dd>{inline(d)}</dd></div>" for a, d in b["items"]) + "</dl>"
    if t == "table":
        num = set(b.get("numeric", []))
        head = "".join(f"<th>{inline(h)}</th>" for h in b["head"])
        ncls = ' class="n"'
        body = "".join("<tr>" + "".join(f"<td{ncls if j in num else ''}>{inline(c)}</td>" for j, c in enumerate(r)) + "</tr>"
                       for r in b["rows"])
        return f'<div class="tbl"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
    if t == "log":
        w = max(len(str(a)) for a, _ in b["rows"])
        return "<pre>" + "\n".join(f'<span class="t">{esc(str(a).rjust(w))}</span>{inline(x)}' for a, x in b["rows"]) + "</pre>"
    if t == "image":
        return f"<figure>{img(work, b, 'shot')}{figcap(b)}</figure>"
    if t == "svg":
        svg = b.get("svg")
        if svg is None:
            with open(os.path.join(work, b["file"])) as f:
                svg = f.read()
        return f'<figure><div class="scroll">{svg}</div>{figcap(b)}</figure>'
    if t == "chart":
        return chart(stats, b)
    if t == "totals":
        return '<div class="totals">' + "".join(f"<div><b>{inline(a)}</b><small>{inline(c)}</small></div>" for a, c in b["items"]) + "</div>"
    if t == "ranges":
        return ranges(b)
    if t == "split":
        def side(s, colour):
            sw = f'<i style="background:var(--{colour})"></i>'
            return (f'<div><h3>{sw}{inline(s["title"])}</h3><ul class="tight">'
                    + "".join(f"<li>{inline(i)}</li>" for i in s["items"]) + "</ul></div>")
        return f'<div class="split">{side(b["left"], "me")}{side(b["right"], "team")}</div>'
    raise SystemExit(f"unknown block type: {t}")


def tokens(d):
    return "\n".join(f"  --{k}:{v};" for k, v in d.items())


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    standalone = "--standalone" in sys.argv
    if len(args) != 1:
        raise SystemExit(__doc__)
    work = os.path.abspath(args[0])
    with open(os.path.join(work, "case.json")) as f:
        case = json.load(f)
    stats = {}
    if os.path.exists(os.path.join(work, "stats.json")):
        with open(os.path.join(work, "stats.json")) as f:
            stats = json.load(f)

    theme = case.get("theme", {})
    light = {**DEFAULT_LIGHT, **theme.get("light", {})}
    dark = {**light, **DEFAULT_DARK, **theme.get("dark", {})}
    fonts = {**DEFAULT_FONTS, **theme.get("fonts", {})}

    shots = case.get("shots") or {}
    hero = [f'<header class="hero gutter{"" if shots else " noshots"}"><div class="wrap">']
    if case.get("eyebrow"):
        hero.append(f'<p class="eyebrow">{inline(case["eyebrow"])}</p>')
    hero.append(f'<h1>{inline(case["headline"])}</h1>')
    if case.get("lede"):
        hero.append(f'<p class="lede">{inline(case["lede"])}</p>')
    if case.get("facts"):
        hero.append('<dl class="facts">' + "".join(f"<div><dt>{inline(a)}</dt><dd>{inline(b)}</dd></div>" for a, b in case["facts"]) + "</dl>")
    if shots:
        single = "" if shots.get("phone") else " single"
        hero.append(f'<div class="shots{single}">{img(work, shots["main"])}'
                    + (img(work, shots["phone"], "phone") if shots.get("phone") else "") + "</div>")
    hero.append("</div></header>")

    body = ['<main class="gutter"><div class="wrap">']
    if case.get("shot_note"):
        body.append(f'<p class="shot-note">{inline(case["shot_note"])}</p>')
    for i, s in enumerate(case["sections"]):
        when = f' <span>{inline(s["when"])}</span>' if s.get("when") else ""
        blocks = "".join(block(work, stats, b) for b in s.get("blocks", []))
        body.append(f'<section class="entry{" first" if i == 0 else ""}"><div class="rail">{inline(s["rail"])}{when}</div>'
                    f'<div class="col"><h2>{inline(s["heading"])}</h2>{blocks}</div></section>')
    body.append("</div></main>")

    ft = case.get("footer")
    if ft:
        body.append('<footer class="gutter"><div class="wrap">')
        if ft.get("heading"):
            body.append(f'<h3>{inline(ft["heading"])}</h3>')
        if ft.get("text"):
            body.append(f'<p>{inline(ft["text"])}</p>')
        if ft.get("stack"):
            body.append('<p class="stack" style="margin-top:14px">' + " · ".join(esc(x) for x in ft["stack"]) + "</p>")
        if ft.get("byline"):
            body.append(f'<p style="margin-top:14px">{inline(ft["byline"])}</p>')
        body.append("</div></footer>")

    with open(os.path.join(HERE, "template.html")) as f:
        page = f.read()
    page = (page.replace("{{TITLE}}", esc(case["title"]))
                .replace("{{FONTS_URL}}", esc(fonts["url"]))
                .replace("{{FONT_DISPLAY}}", fonts["display"]).replace("{{FONT_BODY}}", fonts["body"])
                .replace("{{FONT_MONO}}", fonts["mono"])
                .replace("{{TOKENS_LIGHT}}", tokens(light)).replace("{{TOKENS_DARK}}", tokens(dark))
                .replace("{{BODY}}", "\n".join(hero + body)))
    if standalone:
        lang = esc(case.get("lang", "en"))
        page = (f'<!doctype html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n'
                f'<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
                + page.replace("<style>", "<style>\n:root{color-scheme:light}", 1).replace("</style>\n", "</style>\n</head>\n<body>\n", 1)
                + "</body>\n</html>\n")
    name = "standalone.html" if standalone else "index.html"
    with open(os.path.join(work, name), "w") as f:
        f.write(page)
    with open(os.path.join(work, "files.json"), "w") as f:
        json.dump(files, f, indent=2)
    print(f"wrote {work}/{name} ({len(page):,} bytes) and files.json ({len(files)} files)")


if __name__ == "__main__":
    main()
