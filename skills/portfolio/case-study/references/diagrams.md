# Diagrams

A case study gets one or two diagrams: the architecture, and the one flow that matters most (usually a sequence, such as a payment). Hand-write them as inline SVG in an `svg` block (or a file under `diagrams/`), using the classes the template already styles, so they follow the page's light and dark themes. Never use literal colours.

| Class | Use |
|---|---|
| `d-zone` + `d-z` | a shaded boundary (a server, a platform) and its mono label |
| `d-box` + `d-t` + `d-s` | a component, its name, and a one-line mono subtitle |
| `d-l` (+ `d-dash`) | an ordinary arrow (dashed for a reply or a check) |
| `d-a` + `d-at` | the accent arrow and its label: the one path the reader should follow |
| `d-life` | a lifeline in a sequence diagram |
| `d-check` | the accent-bordered box for a guarantee ("only then is the order paid") |
| `d-m`, `d-ma` | arrowhead fills for `<marker>` paths (ink and accent) |

Rules:

- `viewBox` about 900–1040 wide; the `.scroll` wrapper keeps a 680px minimum and scrolls sideways on phones.
- Give the `<svg>` `role="img"` and an `aria-label` that tells the whole story in sentences.
- Leave 20px inside the viewBox for the outermost labels; keep labels off lines (put them 8px above).
- Marker ids must be unique on the page (`ah`/`aa` for the first diagram, `sh`/`sa` for the second).
- The caption says the one thing the diagram proves, not what it shows.

## Architecture skeleton

```svg
<svg viewBox="0 0 1040 300" role="img" aria-label="...">
  <defs>
    <marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path class="d-m" d="M0 0L8 4L0 8z"/></marker>
    <marker id="aa" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="d-ma" d="M0 0L8 4L0 8z"/></marker>
  </defs>
  <rect class="d-zone" x="20" y="24" width="600" height="250" rx="8"/>
  <text class="d-z" x="36" y="46">Edge worker · app</text>
  <rect class="d-box" x="40" y="70" width="150" height="64" rx="6"/>
  <text class="d-t" x="115" y="98" text-anchor="middle">Pages</text>
  <text class="d-s" x="115" y="116" text-anchor="middle">one model</text>
  <line class="d-l" x1="190" y1="102" x2="229" y2="102" marker-end="url(#ah)"/>
  <line class="d-a" x1="620" y1="102" x2="719" y2="102" marker-end="url(#aa)"/>
  <text class="d-at" x="670" y="92" text-anchor="middle">HTTP</text>
</svg>
```

## Sequence skeleton

Lifelines at x = 90, 330, 570, 810; boxes 36px tall at y = 20; one message every 44px from y = 94; replies dashed.

```svg
<svg viewBox="0 0 900 400" role="img" aria-label="...">
  <defs>
    <marker id="sh" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" orient="auto"><path class="d-m" d="M0 0L8 4L0 8z"/></marker>
    <marker id="sa" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path class="d-ma" d="M0 0L8 4L0 8z"/></marker>
  </defs>
  <line class="d-life" x1="90" y1="56" x2="90" y2="380"/>
  <rect class="d-box" x="30" y="20" width="120" height="36" rx="6"/><text class="d-t" x="90" y="43" text-anchor="middle">Browser</text>
  <line class="d-l" x1="90" y1="94" x2="329" y2="94" marker-end="url(#sh)"/><text class="d-t" x="210" y="86" text-anchor="middle">Place order</text>
  <line class="d-l d-dash" x1="330" y1="138" x2="91" y2="138" marker-end="url(#sh)"/><text class="d-t" x="210" y="130" text-anchor="middle">Confirmation</text>
  <rect class="d-check" x="420" y="160" width="300" height="50" rx="6"/>
</svg>
```
