"""Build an interactive case-study page (index.html) and its files map (files.json) from case.json.

Run: python3 -I build_page.py <work-dir> [--standalone] [--check]

<work-dir> holds case.json, optionally the stats.json that git_stats.py wrote, any diagram SVGs,
and the images it names (img/...). Without --standalone the page is a fragment (title, fonts,
style, body, script), which is what Claude's Artifact tool wraps in its own document.
--standalone writes standalone.html, a full document for opening locally or any static host.
--check only validates case.json against the compact rules and prints what it would cut.

Text fields accept a little inline markup: **bold**, *accent*, `code` and [text](https://url).
Everything else is escaped. Raw markup is accepted only from an SVG file.

case.json (every key optional unless marked; see examples/case.json):

{
  "title": "StoreSuite case study",                       # required: browser tab and gallery name
  "lang": "en",
  "kicker": "StoreSuite · Case study",
  "headline": "From Next.js to **Astro 6:** a *97-PageSpeed* docs site.",   # required
  "lede": "Two or three sentences: what it is, my part, where it lives.",   # required
  "back": {"label": "Portfolio", "href": "https://example.com/portfolio"},
  "live": {"label": "Live at storesuite.dev", "href": "https://storesuite.dev"},
  "pill": "Next.js → Astro 6",
  "actions": [{"label": "Visit storesuite.dev", "href": "https://storesuite.dev", "primary": true},
              {"label": "Hire me", "href": "mailto:me@example.com"}],
  "hero": {
    "desktop": {"src": "img/home-desktop.webp", "w": 1440, "h": 900, "alt": "...", "url": "storesuite.dev",
                "full": "img/home-full.webp"},                # "full": what the lightbox opens
    "phone":   {"src": "img/home-phone.webp", "w": 600, "h": 1299, "alt": "..."},
    "chips": [{"mark": "ok", "text": "Pagefind docs search"}, {"mark": "check", "text": "100 SEO"},
              {"text": "Mobile LCP **1.8 s**"}]              # at most three
  },
  "kpis": [{"label": "My commits", "value": 96, "unit": "", "icon": "git-commit-horizontal"}],  # 2-4
  "facts": [{"label": "My role", "value": "Sole developer", "icon": "user"}],                 # 3-5
  "theme": {"light": {"accent": "#5925fb"}, "dark": {"accent-ink": "#9d78ff"},
            "stage": ["#5925fb", "#1e1460", "#0f0a33", "#18104d"],
            "fonts": {"url": "https://fonts.googleapis.com/css2?family=...", "display": "Barlow",
                      "text": "DM Sans", "mono": "JetBrains Mono"}},
  "sections": [ ...at most six, see SECTION TYPES... ],
  "next": {"href": "...", "kicker": "Astro · Cloudflare", "title": "weLabs Official", "summary": "...",
           "img": {"src": "img/next.webp", "w": 1440, "h": 900, "alt": "..."},
           "all": {"label": "All projects →", "href": "..."}},
  "cta": {"heading": "Need a store that **ships this fast?**", "text": "...",
          "action": {"label": "Hire me", "href": "mailto:..."}},
  "sources": "Where every number came from, in one paragraph."
}

SECTION TYPES. Each has "type", "eyebrow" (numbered for you: "01 — Timeline"), "heading" (a fact,
then the twist in **bold**), and an optional "footnote".

  timeline      "hint", "bars" or "from_stats": true (reads stats.json "series"),
                "notes": {"<bar start or label>": "what shipped"}, "quiet": "Quiet: no commits.",
                "unit": "commits", "team": true (stack the team's commits on mine),
                "legend": ["Mine", "Team"], "select": "<start or label>" (default: busiest bar).
                bars: [{"label": "8 Jun", "me": 40, "team": 0, "note": "...", "axis": "Jun"}]
  architecture  "goals": ["Static build, no SSR", ...], "zones": [{"title": "Build",
                "label": "Build pipeline · pnpm build", "boxes": [["MDX collections", "docs/*.mdx"]],
                "body": "what happens here", "flow": true}], "links": ["dist/", "HTTP"],
                "svg": "diagrams/arch.svg" (instead of zones' boxes: groups <g data-zone="0">),
                "aria": "one sentence describing the whole diagram"
  decisions     "cards": [{"tab": "Docs", "when": "Documentation", "title": "...", "body": "...",
                "tag": "Pagefind · ⌘K", "visual": V}], V is one of
                {"log": {"title": "docs", "rows": [["Start", "Docs on Fumadocs"]], "ok": "✓ 18 pages"}}
                {"pivot": {"was": "Next.js 16", "now": "Astro 6", "arrow": "Migrated in eight days ↓",
                           "was_items": [...], "now_items": [...]}}
                {"table": {"head": ["Mode", "URL"], "rows": [["Browsing", "/blog/page/N/"]], "mono": [1]}}
                {"image": {"src": "img/x.webp", "w": 1200, "h": 800, "alt": "..."}}
  results       "text", "labels": ["Before", "After"], "gauge": {"label": "Desktop PageSpeed",
                "before": 69, "after": 100, "max": 100}, "fixes": [{"label": "Hero blur",
                "before": "5 filters", "after": "3 KB", "before_note": "...", "after_note": "..."}],
                "metrics": {"head": "Mobile PageSpeed", "items": [["97", "Performance"]]}
  screens       "cards": [{"src": "img/a.webp", "full": "img/a-full.webp", "w": 1440, "h": 900,
                "alt": "...", "caption": "Home page", "tag": "Desktop", "long": true}],
                "more": [{"full": "img/b.webp", "caption": "Pricing", "long": true}], "text": "...",
                "button": "All {n} screens"
  behind        "pair": {"value": 92, "total": 96, "text": "...", "value_label": "With Claude Code",
                "rest_label": "Solo", "left": {"label": "I directed", "text": "..."},
                "right": {"label": "Claude drafted", "text": "..."}},
                "faq": [["Question or topic", "Two sentences."]], "stack": ["Astro 6",
                {"name": "Acme API", "color": ["#0a5", "#4d9"]}]

Icons are Lucide names from icons.json (ISC licence). Unknown names fall back to none.
"""
import html
import json
import math
import os
import re
import sys

HIGH = ' fetchpriority="high"'
CURRENT = ' aria-current="true"'
HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = json.load(open(os.path.join(HERE, "icons.json")))
CSS = open(os.path.join(HERE, "page.css")).read()
JS = open(os.path.join(HERE, "page.js")).read()

DEFAULT_FONTS = {
    "url": "https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;600&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=JetBrains+Mono:wght@400;500&display=swap",
    "display": "Barlow", "text": "DM Sans", "mono": "JetBrains Mono",
}
EYEBROWS = {"timeline": "Timeline", "architecture": "Platform", "decisions": "Key decisions",
            "results": "Results", "screens": "Screens", "behind": "Behind the build"}

# Stack chips in their platform's colour: [light, dark]. Matched on the start of the name.
BRANDS = [
    (r"Next\.js", "#000000", "#ffffff"), (r"React", "#087ea4", "#58c4dc"), (r"TypeScript", "#3178c6", "#6aa6e8"),
    (r"JavaScript", "#a08600", "#f0db4f"), (r"Tailwind", "#0284c7", "#38bdf8"), (r"Vue", "#2f9768", "#42b883"),
    (r"Nuxt", "#00a86b", "#00dc82"), (r"Svelte", "#d63a12", "#ff6a3d"), (r"Astro", "#bc52ee", "#cf86f3"),
    (r"MDX", "#c27f00", "#fcb32c"), (r"(Cloudflare|Pages Functions|Turnstile|Workers)", "#e5701b", "#f6913d"),
    (r"Vercel", "#000000", "#ffffff"), (r"Netlify", "#00a7a4", "#32e6e2"), (r"WooCommerce", "#7f54b3", "#a98bd6"),
    (r"WordPress", "#21759b", "#5aa9d6"), (r"PHP", "#777bb4", "#a3a6d6"), (r"Laravel", "#e3342f", "#ff6b66"),
    (r"Node", "#3c873a", "#6cc24a"), (r"Python", "#3572a5", "#6fa8dc"), (r"Go\b", "#00add8", "#5dd6f2"),
    (r"Rust", "#b7410e", "#f0875a"), (r"Docker", "#1d63ed", "#5b93f5"), (r"(AWS|Amazon)", "#c77700", "#ff9900"),
    (r"PostgreSQL", "#336791", "#6b9bc8"), (r"MySQL", "#00758f", "#4fb0c6"), (r"Redis", "#d82c20", "#ff6b5e"),
    (r"(MongoDB|Mongo)", "#13aa52", "#4cd07d"), (r"Supabase", "#249361", "#3ecf8e"), (r"GraphQL", "#c6168d", "#ef5fbe"),
    (r"Stripe", "#635bff", "#8f89ff"), (r"PayPal", "#003087", "#4d8ef0"), (r"Playwright", "#2ead33", "#4cc552"),
    (r"(Claude|Anthropic)", "#c15f3c", "#e5876a"), (r"(OpenAI|ChatGPT|Codex)", "#10a37f", "#3ed1a8"),
    (r"(Gemini|Google)", "#4285f4", "#7aa8f7"), (r"(GitHub|Copilot)", "#24292f", "#e6edf3"),
    (r"Figma", "#a259ff", "#c08bff"), (r"GSAP", "#0a9e35", "#2ee66b"), (r"Shopify", "#5e8e3e", "#95bf47"),
]


def esc(s):
    return html.escape(str(s), quote=True)


def inline(s):
    """Escape, then allow **bold**, *accent*, `code` and [text](https://url)."""
    t = esc(s)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|mailto:[^)\s]+|/[^)\s]*|#[^)\s]*)\)",
               lambda m: f'<a href="{m.group(2)}"{ext(m.group(2))}>{m.group(1)}</a>', t)
    return t


def ext(href):
    return ' target="_blank" rel="noopener"' if str(href).startswith("http") else ""


def icon(name, size=13, cls="i"):
    body = ICONS.get(name or "")
    if not body:
        return ""
    return (f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 24 24" aria-hidden="true" '
            f'focusable="false">{body}</svg>')


def img(o, cls="", loading="lazy", extra=""):
    w, h = o.get("w"), o.get("h")
    size = f' width="{int(w)}" height="{int(h)}"' if w and h else ""
    c = f' class="{cls}"' if cls else ""
    return f'<img src="{esc(o["src"])}"{size} alt="{esc(o.get("alt", ""))}" loading="{loading}" decoding="async"{c}{extra}>'


def fmt_num(v):
    if isinstance(v, int) or (isinstance(v, float) and v.is_integer()):
        return f"{int(v):,}"
    return str(v)


def brand(name):
    for pat, light, dark in BRANDS:
        if re.match(pat, name):
            return light, dark
    return None


class Page:
    def __init__(self, work, case, stats):
        self.work, self.case, self.stats = work, case, stats
        self.files, self.warnings, self.lb = set(), [], 0

    def use(self, path):
        if path and not re.match(r"^(https?:|data:|/)", path):
            self.files.add(path)
            if not os.path.exists(os.path.join(self.work, path)):
                self.warnings.append(f"missing file: {path}")
        return path

    def lb_attrs(self, full, caption, alt="", long=False):
        self.use(full)
        self.lb += 1
        a = f' data-lb="{esc(full)}" data-cap="{esc(caption)}" data-alt="{esc(alt)}"'
        return a + (' data-long="1"' if long else "")

    # ---- hero, facts ----
    def hero(self):
        c = self.case
        meta = []
        if c.get("back"):
            meta.append(f'<a class="cs-mono cs-back" href="{esc(c["back"]["href"])}">← {esc(c["back"]["label"])}</a>')
        if c.get("live"):
            if meta:
                meta.append('<span class="cs-sep" aria-hidden="true"></span>')
            meta.append(f'<a class="cs-mono cs-live" href="{esc(c["live"]["href"])}"{ext(c["live"]["href"])}>'
                        f'<span class="cs-dot" aria-hidden="true"></span>{esc(c["live"]["label"])}</a>')
        if c.get("pill"):
            meta.append(f'<span class="cs-mono cs-pill">{esc(c["pill"])}</span>')
        actions = []
        for a in c.get("actions", [])[:2]:
            primary = a.get("primary")
            cls = "cs-btn cs-btn--primary water water--filled" if primary else "cs-btn cs-btn--ghost water"
            arrow = icon("arrow-up-right" if str(a["href"]).startswith("http") else "arrow-right", 16)
            actions.append(f'<a class="{cls}" href="{esc(a["href"])}"{ext(a["href"])}>{esc(a["label"])}{arrow}</a>')
        kicker = f'<span class="cs-mono cs-h1-kicker">{esc(c["kicker"])}</span>' if c.get("kicker") else ""
        copy = (
            '<div class="cs-hero-copy">'
            + (f'<div class="cs-in cs-hero-meta" style="--d:0ms">{"".join(meta)}</div>' if meta else "")
            + f'<h1 class="cs-in cs-h1" style="--d:80ms">{kicker}{inline(c["headline"])}</h1>'
            + f'<p class="cs-in cs-lede" style="--d:160ms">{inline(c["lede"])}</p>'
            + (f'<div class="cs-in cs-actions" style="--d:320ms">{"".join(actions)}</div>' if actions else "")
            + "</div>"
        )
        return f'<section class="cs-hero">{copy}{self.visual()}</section>'

    def visual(self):
        h = self.case.get("hero", {})
        parts = []
        d, p = h.get("desktop"), h.get("phone")
        if d:
            self.use(d["src"])
            bar = (f'<span class="cs-browser" aria-hidden="true"><i></i><i></i><i></i>'
                   f'<span class="cs-mono">{esc(d.get("url", ""))}</span></span>')
            parts.append(f'<button type="button" class="cs-shot cs-stage-desktop" aria-label="Enlarge: {esc(d.get("alt", "screenshot"))}"'
                         f'{self.lb_attrs(d.get("full", d["src"]), d.get("caption", d.get("url", "")), d.get("alt", ""), d.get("long", False))}>'
                         f'{bar}{img(d, loading="eager", extra=HIGH)}</button>')
        if p:
            self.use(p["src"])
            parts.append(f'<button type="button" class="cs-shot cs-stage-phone cs-float" aria-label="Enlarge: {esc(p.get("alt", "phone screenshot"))}"'
                         f'{self.lb_attrs(p.get("full", p["src"]), p.get("caption", "On a phone"), p.get("alt", ""), p.get("long", False))}>'
                         f'<span>{img(p, loading="eager")}</span></button>')
        for i, chip in enumerate(h.get("chips", [])[:3]):
            mark = {"ok": '<span class="cs-ok">●</span>', "check": '<span class="cs-ok">✓</span>'}.get(chip.get("mark"), "")
            float_cls = "cs-float2" if i % 2 == 0 else "cs-float"
            parts.append(f'<span class="cs-chip cs-mono {float_cls} cs-chip--{i + 1}">{mark}{inline(chip["text"])}</span>')
        stage = ""
        if parts:
            solo = "" if p else " cs-stage--solo"
            stage = (f'<div class="cs-in cs-stage{solo}" style="--d:200ms"><div class="cs-stage-bg" aria-hidden="true"></div>'
                     f'<div class="cs-stage-dots" aria-hidden="true"></div>{"".join(parts)}</div>')
        kpis = self.case.get("kpis", [])[:4]
        row = ""
        if kpis:
            cells = []
            for k in kpis:
                v = k["value"]
                count = f' data-count="{int(v)}"' if isinstance(v, (int, float)) and float(v).is_integer() else ""
                unit = f'<small>{esc(k["unit"])}</small>' if k.get("unit") else ""
                cells.append(f'<div class="cs-kpi" role="listitem"><span class="cs-mono cs-kpi-label">'
                             f'<span class="cs-icon">{icon(k.get("icon"))}</span>{esc(k["label"])}</span>'
                             f'<span class="cs-kpi-value"{count}>{esc(fmt_num(v))}{unit}</span></div>')
            row = (f'<div class="cs-in cs-kpis" style="--d:380ms;--kpis:{len(kpis)}" role="list" aria-label="Project results">'
                   f'{"".join(cells)}</div>')
        return f'<div class="cs-hero-visual">{stage}{row}</div>'

    def facts(self):
        fs = self.case.get("facts", [])
        if not fs:
            return ""
        cells = "".join(
            f'<div class="cs-fact"><dt><span class="cs-icon" aria-hidden="true">{icon(f.get("icon"))}</span>'
            f'{esc(f["label"])}</dt><dd>{inline(f["value"])}</dd></div>' for f in fs)
        return f'<dl class="cs-facts">{cells}</dl>'

    # ---- sections ----
    def section(self, n, s):
        kind = s["type"]
        sid = s.get("id") or kind
        eyebrow = f'{n:02d} — {s.get("eyebrow", EYEBROWS.get(kind, kind.title()))}'
        body = getattr(self, f"s_{kind}")(s)
        foot = f'<p class="cs-footnote">{inline(s["footnote"])}</p>' if s.get("footnote") else ""
        attr = {"timeline": "", "architecture": " data-zones", "decisions": " data-deck", "results": " data-flip"}.get(kind, "")
        return (f'<section id="{esc(sid)}" class="cs-section"{attr}><span class="cs-eyebrow">{esc(eyebrow)}</span>'
                f'<h2 class="cs-h2">{inline(s["heading"])}</h2>{body}{foot}</section>')

    def hint(self, s, default):
        text = s.get("hint", default)
        return f'<p class="cs-hint">{icon("mouse-pointer-click", 15)}{esc(text)}</p>' if text else ""

    def s_timeline(self, s):
        bars = s.get("bars")
        unit = s.get("unit", "commits")
        if not bars and s.get("from_stats"):
            series = (self.stats or {}).get("series")
            if not series:
                raise SystemExit("timeline: from_stats needs stats.json with a series (run git_stats.py)")
            bars = series_bars(series)
        if not bars:
            raise SystemExit("timeline: give bars or from_stats")
        notes = s.get("notes", {})
        quiet = s.get("quiet", f"Quiet: no {unit}.")
        team = s.get("team", any(b.get("team") for b in bars))
        peak = max(1, max(b.get("me", 0) + (b.get("team", 0) if team else 0) for b in bars))
        sel_key = s.get("select")
        sel = 0
        best = -1
        for i, b in enumerate(bars):
            tot = b.get("me", 0) + (b.get("team", 0) if team else 0)
            if sel_key and sel_key in (b.get("start"), b.get("label")):
                sel, best = i, 10 ** 9
            elif tot > best:
                sel, best = i, tot
        cells, head0, note0 = [], "", ""
        for i, b in enumerate(bars):
            me, tm = b.get("me", 0), (b.get("team", 0) if team else 0)
            tot = me + tm
            height = f"{max(4, round(tot / peak * 190))}px" if tot else "0px"
            note = b.get("note") or notes.get(b.get("start", "")) or notes.get(b.get("label", "")) or ("" if tot else quiet)
            if tot and not note:
                self.warnings.append(f"timeline: no note for {b.get('label')}")
            who = f"{me} mine, {tm} team" if team else f"{me}"
            head = f'{b.get("label")} · {who} {unit}' if not team else f'{b.get("label")} · {who}'
            segs = ""
            if tot:
                if tm:
                    segs += f'<span class="cs-seg is-team" style="height:{tm / tot * 100:.1f}%"></span>'
                if me:
                    segs += f'<span class="cs-seg is-me" style="height:{me / tot * 100:.1f}%"></span>'
            if i == sel:
                head0, note0 = head, note
            cells.append(
                f'<button type="button" class="cs-day" aria-pressed="{str(i == sel).lower()}" '
                f'aria-label="{esc(b.get("label"))}: {tot} {esc(unit)}" data-head="{esc(head)}" data-note="{esc(note)}">'
                f'<span class="cs-day-total">{tot or ""}</span><span class="cs-day-bar" style="height:{height}">{segs}</span>'
                f'<span class="cs-day-label">{esc(b.get("axis", ""))}</span></button>')
        legend = ""
        if team:
            lab = s.get("legend", ["Mine", "Team"])
            legend = (f'<div class="cs-legend"><span><i class="is-me"></i>{esc(lab[0])}</span>'
                      f'<span><i class="is-team"></i>{esc(lab[1])}</span></div>')
        return (self.hint(s, f"Pick a bar to see what shipped.")
                + f'<div class="cs-panel" data-timeline>{legend}<div class="cs-days" style="--bars:{len(bars)}" role="group" '
                  f'aria-label="{esc(unit.capitalize())} over time">{"".join(cells)}</div>'
                  f'<div class="cs-day-note" aria-live="polite"><span class="cs-mono" data-note-head>{esc(head0)}</span>'
                  f'<span data-note-body>{esc(note0)}</span></div></div>')

    def s_architecture(self, s):
        goals = "".join(f'<li>{icon("check", 14)}{inline(g)}</li>' for g in s.get("goals", []))
        goals = f'<ul class="cs-goals" aria-label="The brief">{goals}</ul>' if goals else ""
        zones = s.get("zones", [])
        pills = "".join(
            f'<button type="button" class="cs-pill-btn water" data-zone-pill aria-pressed="{str(i == 0).lower()}" '
            f'data-title="{esc(z["title"])}" data-body="{esc(inline(z.get("body", "")))}">'
            f'<span class="cs-mono">{i + 1:02d}</span>{esc(z["title"])}</button>' for i, z in enumerate(zones))
        if s.get("svg"):
            path = os.path.join(self.work, s["svg"])
            svg = open(path).read()
            svg = re.sub(r"<\?xml[^>]*>", "", svg)
            svg = re.sub(r'<g([^>]*?)data-zone="(\d+)"', lambda m: f'<g{m.group(1)}class="cs-zone{" is-dim" if m.group(2) != "0" else ""}" data-zone="{m.group(2)}"', svg)
        else:
            svg = zone_svg(zones, s.get("links", []), s.get("aria", ""))
        note = f'<strong>{esc(zones[0]["title"])}:</strong> {inline(zones[0].get("body", ""))}' if zones else ""
        hint = self.hint(s, "Pick a stage to light it up.") if s.get("hint") else ""
        return (goals + hint + (f'<div class="cs-pills" role="group" aria-label="Stage">{pills}</div>' if pills else "")
                + f'<figure class="cs-figure"><div class="cs-dia">{svg}</div>'
                  f'<figcaption class="cs-zone-note" data-zone-note aria-live="polite">{note}</figcaption></figure>')

    def s_decisions(self, s):
        cards = s["cards"]
        n = len(cards)
        pills = "".join(
            f'<button type="button" class="cs-pill-btn water"{CURRENT if i == 0 else ""}>'
            f'<span class="cs-mono">{i + 1:02d}</span>{esc(c["tab"])}</button>' for i, c in enumerate(cards))
        out = []
        for i, c in enumerate(cards):
            tag = f'<span class="cs-tag">{esc(c["tag"])}</span>' if c.get("tag") else ""
            when = f'<span class="cs-st-when">{esc(c["when"])}</span>' if c.get("when") else ""
            out.append(
                f'<article class="cs-deck-card" style="--i:{i}" aria-label="{i + 1:02d} / {n:02d}: {esc(c["title"])}">'
                f'<div class="cs-st-copy">{when}<h3>{inline(c["title"])}</h3><p>{inline(c["body"])}</p>{tag}</div>'
                f'<div class="cs-st-visual">{self.visual_block(c.get("visual"))}</div></article>')
        return (f'<nav class="cs-deck-nav cs-pills" aria-label="{esc(s.get("eyebrow", "Key decisions"))}">{pills}</nav>'
                f'<div class="cs-deck">{"".join(out)}</div>')

    def visual_block(self, v):
        if not v:
            return ""
        if "log" in v:
            lg = v["log"]
            rows = "".join(f'<span class="cs-logl" style="--i:{j}"><span class="cs-term-time">{esc(a)}</span><span>{esc(b)}</span></span>'
                           for j, (a, b) in enumerate(lg["rows"]))
            ok = f'<span class="cs-logl cs-term-ok" style="--i:{len(lg["rows"])}">{esc(lg["ok"])}</span>' if lg.get("ok") else ""
            return (f'<div class="cs-term"><div class="cs-term-bar"><i></i><i></i><i></i><span>{esc(lg.get("title", ""))}</span></div>'
                    f'<div class="cs-term-body">{rows}{ok}</div></div>')
        if "pivot" in v:
            p = v["pivot"]
            was = "".join(f"<li>{inline(t)}</li>" for t in p.get("was_items", []))
            now = "".join(f"<li>{inline(t)}</li>" for t in p.get("now_items", []))
            arrow = f'<div class="cs-pivot-arrow"><span>{esc(p["arrow"])}</span></div>' if p.get("arrow") else ""
            return (f'<div class="cs-pivot"><div class="cs-pivot-box is-was"><span class="cs-mono">{esc(p["was"])}</span><ul>{was}</ul></div>'
                    f'{arrow}<div class="cs-pivot-box is-now"><span class="cs-mono">{esc(p["now"])}</span><ul>{now}</ul></div></div>')
        if "table" in v:
            return table(v["table"])
        if "image" in v:
            self.use(v["image"]["src"])
            return img(v["image"])
        return ""

    def s_results(self, s):
        labels = s.get("labels", ["Before", "After"])
        toggle = (f'<div class="cs-toggle" role="group" aria-label="Show the figures">'
                  f'<button type="button" data-side="before" aria-pressed="false">{esc(labels[0])}</button>'
                  f'<button type="button" data-side="after" aria-pressed="true">{esc(labels[1])}</button></div>')
        text = f'<p class="cs-p cs-p--sm">{inline(s["text"])}</p>' if s.get("text") else ""
        gauge = ""
        g = s.get("gauge")
        if g:
            mx = g.get("max", 100)
            off = 2 * math.pi * 52 * (1 - min(1, float(g["after"]) / mx))
            gauge = (f'<div class="cs-gauge"><span class="cs-gauge-ring"><svg viewBox="0 0 120 120" aria-hidden="true">'
                     f'<circle class="cs-gauge-track" cx="60" cy="60" r="52"/><circle class="cs-gauge-fill" cx="60" cy="60" r="52" '
                     f'style="stroke-dashoffset:{off:.2f}" data-before="{g["before"]}" data-after="{g["after"]}" data-max="{mx}"/></svg>'
                     f'<span class="cs-gauge-value" aria-live="polite" data-before="{esc(fmt_num(g["before"]))}" data-after="{esc(fmt_num(g["after"]))}">'
                     f'{esc(fmt_num(g["after"]))}</span></span><span class="cs-mono cs-muted">{esc(g["label"])}</span></div>')
        fixes = "".join(
            f'<div class="cs-fix"><span class="cs-mono cs-muted">{esc(f["label"])}</span>'
            f'<span class="cs-fix-value" data-before="{esc(f["before"])}" data-after="{esc(f["after"])}">{esc(f["after"])}</span>'
            f'<span class="cs-fix-note" data-before="{esc(f.get("before_note", ""))}" data-after="{esc(f.get("after_note", ""))}">'
            f'{esc(f.get("after_note", ""))}</span></div>' for f in s.get("fixes", []))
        metrics = ""
        m = s.get("metrics")
        if m:
            items = "".join(f'<div><span class="cs-metrics-value">{esc(a)}</span><span class="cs-mono">{esc(b)}</span></div>' for a, b in m["items"])
            metrics = f'<div class="cs-metrics"><span class="cs-metrics-head">{esc(m.get("head", ""))}</span>{items}</div>'
        return (f'<div class="cs-flip-head">{text}{toggle}</div>'
                f'<div class="cs-flip is-after">{gauge}<div class="cs-fixes">{fixes}</div></div>{metrics}')

    def s_screens(self, s):
        cards, first = [], None
        for i, c in enumerate(s.get("cards", [])[:3]):
            self.use(c["src"])
            if first is None:
                first = self.lb
            full = c.get("full", c["src"])
            tall = " is-tall" if i == 0 and len(s["cards"]) > 2 else ""
            cards.append(
                f'<button type="button" class="cs-shot cs-shot-card{tall}" aria-label="Enlarge: {esc(c["caption"])}"'
                f'{self.lb_attrs(full, c["caption"], c.get("alt", ""), c.get("long", False))}>'
                f'<span class="cs-shot-img">{img(c)}</span>'
                f'<span class="cs-shot-cap"><span>{esc(c["caption"])}</span><span class="cs-mono">{esc(c.get("tag", ""))}</span></span></button>')
        more = []
        for m in s.get("more", []):
            more.append(f'<span{self.lb_attrs(m["full"], m["caption"], m.get("alt", ""), m.get("long", False))}></span>')
        total = len(cards) + len(more)
        button = s.get("button", "All {n} screens").replace("{n}", str(total))
        foot = ""
        if s.get("text") or more:
            text = f'<p class="cs-p cs-p--sm">{inline(s["text"])}</p>' if s.get("text") else "<span></span>"
            btn = (f'<button type="button" class="cs-btn cs-btn--ghost cs-btn--sm water" data-lb-open="{first or 0}">'
                   f'{icon("images", 16)}{esc(button)}</button>') if total > 1 else ""
            foot = f'<div class="cs-shots-foot">{text}{btn}</div>'
        hidden = f'<div hidden>{"".join(more)}</div>' if more else ""
        return f'<div class="cs-shots">{"".join(cards)}</div>{hidden}{foot}'

    def s_behind(self, s):
        out = ""
        p = s.get("pair")
        if p:
            total, value = int(p["total"]), int(p["value"])
            if total > 600:
                self.warnings.append("behind: total over 600, the squares are scaled to 600")
            scale = min(1, 600 / total)
            n, v = round(total * scale), round(value * scale)
            cols = min(48, n)
            dots = "".join('<i class="is-me"></i>' if k < v else "<i></i>" for k in range(n))
            two = ""
            if p.get("left") or p.get("right"):
                cell = lambda side, cls: (f'<div><span class="cs-pair-label"><i class="{cls}"></i>{esc(side["label"])}</span>'
                                          f'<p>{inline(side["text"])}</p></div>')
                two = f'<div class="cs-two">{cell(p["left"], "is-me") if p.get("left") else ""}{cell(p["right"], "is-team") if p.get("right") else ""}</div>'
            legend = ""
            if p.get("value_label"):
                legend = (f'<div class="cs-legend"><span><i class="is-me"></i>{esc(p["value_label"])} ({value:,})</span>'
                          + (f'<span><i class="is-team"></i>{esc(p["rest_label"])} ({total - value:,})</span>' if p.get("rest_label") else "")
                          + "</div>")
            out += (f'<div class="cs-panel cs-pair"><div class="cs-pair-head"><span class="cs-lead-value">{value:,}'
                    f'<span> / {total:,}</span></span><span>{inline(p.get("text", ""))}</span></div>'
                    f'<div class="cs-commits" style="--cols:{cols}" role="img" aria-label="{value:,} of {total:,}">{dots}</div>'
                    f'{legend}{two}</div>')
        if s.get("faq"):
            rows = "".join(f'<details><summary><h3>{inline(q)}</h3>{icon("plus", 20, "i cs-faq-mark")}</summary><p>{inline(a)}</p></details>'
                           for q, a in s["faq"])
            out += f'<div class="cs-faq">{rows}</div>'
        if s.get("stack"):
            chips = []
            for t in s["stack"]:
                name, col = (t["name"], t.get("color")) if isinstance(t, dict) else (t, None)
                col = col or brand(name)
                style = f' style="--brand-light:{col[0]};--brand-dark:{col[1]}"' if col else ""
                chips.append(f"<span{style}>{esc(name)}</span>")
            out += f'<div class="cs-stack">{"".join(chips)}</div>'
        return out

    # ---- tail ----
    def tail(self):
        c, out = self.case, ""
        nx = c.get("next")
        if nx:
            imgs = ""
            if nx.get("img"):
                self.use(nx["img"]["src"])
                imgs = f'<span class="cs-next-img">{img(nx["img"])}</span>'
            allp = f'<a href="{esc(nx["all"]["href"])}">{esc(nx["all"]["label"])}</a>' if nx.get("all") else ""
            out += (f'<section class="cs-next-wrap"><div class="cs-next-head"><span>Next case study</span>{allp}</div>'
                    f'<a class="cs-next" href="{esc(nx["href"])}"{ext(nx["href"])}><span class="cs-next-copy">'
                    f'<span class="cs-mono">{esc(nx.get("kicker", ""))}</span><span class="cs-next-title">{esc(nx["title"])}'
                    f'{icon("arrow-up-right", 48)}</span><span class="cs-next-summary">{inline(nx.get("summary", ""))}</span></span>{imgs}</a></section>')
        cta = c.get("cta")
        if cta:
            a = cta.get("action")
            btn = (f'<a class="cs-btn cs-btn--primary water water--filled" href="{esc(a["href"])}"{ext(a["href"])}>'
                   f'{esc(a["label"])}{icon("arrow-right", 16)}</a>') if a else ""
            text = f'<p>{inline(cta["text"])}</p>' if cta.get("text") else ""
            out += f'<section class="cs-cta"><div><h2>{inline(cta["heading"])}</h2>{text}</div>{btn}</section>'
        if c.get("sources"):
            out += f'<footer class="cs-sources"><p class="cs-footnote">{inline(c["sources"])}</p></footer>'
        return out

    def lightbox(self):
        if not self.lb:
            return ""
        return ('<dialog class="cs-lb" aria-label="Screens"><div class="cs-lb-stage"><img alt=""></div>'
                '<div class="cs-lb-bar"><span data-lb-cap></span><span data-lb-count></span></div>'
                f'<button type="button" class="cs-lb-close" aria-label="Close">{icon("x", 20)}</button>'
                f'<button type="button" class="cs-lb-prev" aria-label="Previous">{icon("chevron-left", 20)}</button>'
                f'<button type="button" class="cs-lb-next" aria-label="Next">{icon("chevron-right", 20)}</button></dialog>')

    def render(self):
        c = self.case
        sections = "".join(self.section(i + 1, s) for i, s in enumerate(c.get("sections", [])))
        body = (f'<div class="cs"><div class="cs-progress" aria-hidden="true"><span></span></div><main class="cs-wrap">'
                f'{self.hero()}{self.facts()}<div class="cs-sections">{sections}</div>{self.tail()}</main>{self.lightbox()}</div>')
        return body


def series_bars(series):
    """stats.json series -> bars, with a short label and an axis mark at each new month."""
    import datetime as dt
    gran, rows, out, last_month = series["granularity"], series["rows"], [], None
    for r in rows:
        d = dt.date.fromisoformat(r["start"])
        mon = d.strftime("%b")
        if gran == "day":
            label, axis = f"{d.day} {mon}", d.strftime("%a")[:2]
        elif gran == "week":
            label, axis = f"Week of {d.day} {mon}", mon if mon != last_month else ""
        else:
            label, axis = d.strftime("%B %Y"), mon if d.month != 1 or not out else d.strftime("%Y")
        last_month = mon
        out.append({"start": r["start"], "label": label, "axis": axis, "me": r["me"], "team": r["team"]})
    return out


def table(t):
    mono = set(t.get("mono", []))
    head = "".join(f"<th>{esc(h)}</th>" for h in t["head"])
    rows = "".join("<tr>" + "".join(
        f'<td class="cs-mono">{esc(v)}</td>' if j in mono else f"<td>{inline(v)}</td>" for j, v in enumerate(r)) + "</tr>"
        for r in t["rows"])
    return f'<div class="cs-table"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'


def zone_svg(zones, links, aria):
    """Two to four zones side by side, each a stack of boxes, joined by labelled arrows."""
    n = max(1, len(zones))
    gap = 80
    w = (1000 - 40 - gap * (n - 1)) / n
    rows = max([len(z.get("boxes", [])) for z in zones] + [1])
    zh = 42 + rows * 66 + 12
    H = zh + 48
    cx = lambda i: 20 + i * (w + gap)
    parts = ['<defs><marker id="cs-ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
             '<path class="d-m" d="M0 0L8 4L0 8z"/></marker><marker id="cs-aa" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" '
             'markerHeight="7" orient="auto-start-reverse"><path class="d-ma" d="M0 0L8 4L0 8z"/></marker></defs>']
    mid = 24 + zh / 2
    for i, z in enumerate(zones):
        x = cx(i)
        g = [f'<rect class="d-zone" x="{x:.0f}" y="24" width="{w:.0f}" height="{zh:.0f}" rx="8"/>',
             f'<text class="d-z" x="{x + 16:.0f}" y="46">{esc(z.get("label", z["title"]))}</text>']
        boxes = z.get("boxes", [])
        for j, b in enumerate(boxes):
            by = 66 + j * 66
            t, sub = (b[0], b[1] if len(b) > 1 else "") if isinstance(b, list) else (b, "")
            g.append(f'<rect class="d-box" x="{x + 18:.0f}" y="{by}" width="{w - 36:.0f}" height="52" rx="6"/>')
            ty = by + (22 if sub else 31)
            g.append(f'<text class="d-t" x="{x + w / 2:.0f}" y="{ty}" text-anchor="middle">{esc(t)}</text>')
            if sub:
                g.append(f'<text class="d-s" x="{x + w / 2:.0f}" y="{by + 40}" text-anchor="middle">{esc(sub)}</text>')
            if z.get("flow", True) and j < len(boxes) - 1:
                g.append(f'<line class="d-l" x1="{x + w / 2:.0f}" y1="{by + 52}" x2="{x + w / 2:.0f}" y2="{by + 65}" marker-end="url(#cs-ah)"/>')
        dim = "" if i == 0 else " is-dim"
        parts.append(f'<g class="cs-zone{dim}" data-zone="{i}">{"".join(g)}</g>')
        if i < n - 1:
            x1, x2 = x + w - 18, cx(i + 1) - 2
            parts.append(f'<line class="d-a" x1="{x1:.0f}" y1="{mid:.0f}" x2="{x2:.0f}" y2="{mid:.0f}" marker-end="url(#cs-aa)"/>')
            if i < len(links) and links[i]:
                parts.append(f'<text class="d-at" x="{(x1 + x2) / 2:.0f}" y="{mid - 10:.0f}" text-anchor="middle">{esc(links[i])}</text>')
    return f'<svg viewBox="0 0 1000 {H:.0f}" role="img" aria-label="{esc(aria)}">{"".join(parts)}</svg>'


def theme_css(theme):
    if not theme:
        return ""
    out = []
    light = dict(theme.get("light", {}))
    if theme.get("stage"):
        for k, v in zip(["stage-1", "stage-2", "stage-3", "stage-bar"], theme["stage"]):
            light[k] = v
    f = theme.get("fonts")
    if f:
        for k in ("display", "text", "mono"):
            if f.get(k):
                light[k] = f"'{f[k]}', {DEFAULT_FONTS_FALLBACK[k]}"
    if light:
        out.append(":root{" + ";".join(f"--cs-{k}:{v}" for k, v in light.items()) + "}")
    dark = theme.get("dark", {})
    if dark:
        decl = ";".join(f"--cs-{k}:{v}" for k, v in dark.items())
        out.append("@media (prefers-color-scheme: dark){:root:not([data-theme=\"light\"]){" + decl + "}}")
        out.append(":root[data-theme=\"dark\"]{" + decl + "}")
    return "\n".join(out)


DEFAULT_FONTS_FALLBACK = {"display": "'Helvetica Neue', sans-serif", "text": "system-ui, sans-serif",
                          "mono": "ui-monospace, SFMono-Regular, Menlo, monospace"}


SKIP_KEYS = {"src", "full", "href", "start", "url", "svg", "color", "theme", "sources", "select", "type", "id", "icon", "mark"}
COPY_RULES = [
    (r"\b(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)[0-9a-f]{7,40}\b", "a commit hash"),
    (r"(?<![\w&])#\d{2,6}\b", "a PR or issue number"),
    (r"\b(?:PR|pull request|issue) ?#?\d+", "a PR or issue number"),
    (r"\b20\d\d-\d\d-\d\d\b", "an ISO date"),
    (r"\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* 20\d\d\b", "a full date"),
]


def copy_strings(node, where="case"):
    """Every visible string in case.json, skipping paths, URLs, theme and sources. Timeline
    bar labels and notes keys are axis data, not copy."""
    if isinstance(node, str):
        yield where, node
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from copy_strings(v, f"{where}[{i}]")
    elif isinstance(node, dict):
        for k, v in node.items():
            if k in SKIP_KEYS or (k in ("label", "axis") and "bars" in where):
                continue
            yield from copy_strings(v, f"{where}.{k}")


def check(case):
    """The compact rules. Returns a list of problems; empty means it passes."""
    p = []
    secs = case.get("sections", [])
    if len(secs) > 6:
        p.append(f"{len(secs)} sections: keep at most six")
    known = set(EYEBROWS)
    for i, s in enumerate(secs):
        if s.get("type") not in known:
            p.append(f"section {i + 1}: unknown type {s.get('type')!r}")
        if not s.get("heading"):
            p.append(f"section {i + 1}: no heading")
        if s.get("type") == "decisions" and not 2 <= len(s.get("cards", [])) <= 5:
            p.append(f"section {i + 1}: decisions wants 2 to 5 cards")
        if s.get("type") == "architecture" and not 2 <= len(s.get("zones", [])) <= 4:
            p.append(f"section {i + 1}: architecture wants 2 to 4 zones")
    if len(case.get("kpis", [])) > 4:
        p.append("more than four kpis")
    if len(case.get("lede", "")) > 320:
        p.append("lede over 320 characters: two or three sentences")
    # No commit hashes, PR numbers or dates in the copy (sources may cite them)
    for where, text in copy_strings(case):
        for pat, what in COPY_RULES:
            if re.search(pat, text):
                p.append(f"{where}: holds {what}: {text[:80]!r}")
    for i, s in enumerate(secs):
        for blk in ("body", "text"):
            if len(str(s.get(blk, ""))) > 260:
                p.append(f"section {i + 1}: {blk} over 260 characters, move detail into a faq row")
        for c in s.get("cards", []):
            if len(c.get("body", "")) > 260:
                p.append(f"section {i + 1}: card {c.get('tab')!r} body over 260 characters")
    return p


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__.split("\n\n")[1])
    work = os.path.abspath(args[0])
    case = json.load(open(os.path.join(work, "case.json")))
    for key in ("title", "headline", "lede"):
        if not case.get(key):
            raise SystemExit(f"case.json needs {key!r}")
    problems = check(case)
    if "--check" in sys.argv:
        print("\n".join(problems) or "case.json passes the compact rules")
        sys.exit(1 if problems else 0)
    stats_path = os.path.join(work, "stats.json")
    stats = json.load(open(stats_path)) if os.path.exists(stats_path) else None
    page = Page(work, case, stats)
    body = page.render()
    fonts = {**DEFAULT_FONTS, **case.get("theme", {}).get("fonts", {})}
    head = (f"<title>{esc(case['title'])}</title>\n"
            f'<meta name="description" content="{esc(re.sub(r"[*`]", "", case["lede"]))}">\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="{esc(fonts["url"])}">\n'
            f"<style>\n{CSS}\n{theme_css(case.get('theme'))}\n</style>\n")
    script = f"<script>\n{JS}</script>\n"
    fragment = head + body + "\n" + script
    with open(os.path.join(work, "index.html"), "w") as fh:
        fh.write(fragment)
    if "--standalone" in sys.argv:
        doc = (f'<!doctype html>\n<html lang="{esc(case.get("lang", "en"))}">\n<head>\n<meta charset="utf-8">\n'
               '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
               f"{head}</head>\n<body>\n{body}\n{script}</body>\n</html>\n")
        with open(os.path.join(work, "standalone.html"), "w") as fh:
            fh.write(doc)
    with open(os.path.join(work, "files.json"), "w") as fh:
        json.dump({f: f for f in sorted(page.files)}, fh, indent=2)
    for w in page.warnings + [f"rule: {p}" for p in problems]:
        print("warning:", w, file=sys.stderr)
    print(f"wrote index.html{' and standalone.html' if '--standalone' in sys.argv else ''}, "
          f"{len(page.files)} files in files.json, {len(case.get('sections', []))} sections")


if __name__ == "__main__":
    main()
