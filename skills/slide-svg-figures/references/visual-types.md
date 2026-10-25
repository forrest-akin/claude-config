# Visual Type Selection and Templates

## Selection Guide

Ask: "What is the ONE thing this figure communicates?" Then match to a type:

| Message pattern | Visual type | Max elements |
|----------------|-------------|-------------|
| "A leads to B leads to C" | Horizontal flow | 5 boxes + 4 arrows |
| "A vs B" or "before/after" | Side-by-side comparison | 2 panels |
| "These N things are related" | Grouped boxes | 6 boxes |
| "This is bigger/more important than that" | Scale or bar | 3-5 items |
| "A contains B contains C" | Nested/concentric | 3 levels max |
| "Here's the breakdown" | Stacked sections | 4 sections max |
| "This is the key number" | Single statistic | Use `fact` layout, no SVG |
| "They said this" | Quote | Use `quote` layout, no SVG |

## Template: Horizontal Flow (3 boxes)

```xml
<!-- LAYOUT PLAN
  Figure purpose: Show three-step process
  Canvas: viewBox="0 0 850 200"
  Element count: 5 (3 boxes + 2 arrows)

  Elements:
    Box A: x=40,  y=60, w=200, h=80 → right: 240
    Box B: x=325, y=60, w=200, h=80 → right: 525 (gap: 85px ✓)
    Box C: x=610, y=60, w=200, h=80 → right: 810 (gap: 85px ✓)
    Arrow A→B: (240,100) to (315,100)
    Arrow B→C: (525,100) to (600,100)
-->
<svg viewBox="0 0 850 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#6B7280"/>
    </marker>
  </defs>

  <rect x="40" y="60" width="200" height="80" rx="8" fill="#2563EB"/>
  <text x="140" y="100" text-anchor="middle" dominant-baseline="central"
        font-family="system-ui, sans-serif" font-size="15" fill="#FFF">Step One</text>

  <line x1="240" y1="100" x2="315" y2="100" stroke="#6B7280" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="325" y="60" width="200" height="80" rx="8" fill="#2563EB"/>
  <text x="425" y="100" text-anchor="middle" dominant-baseline="central"
        font-family="system-ui, sans-serif" font-size="15" fill="#FFF">Step Two</text>

  <line x1="525" y1="100" x2="600" y2="100" stroke="#6B7280" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="610" y="60" width="200" height="80" rx="8" fill="#2563EB"/>
  <text x="710" y="100" text-anchor="middle" dominant-baseline="central"
        font-family="system-ui, sans-serif" font-size="15" fill="#FFF">Step Three</text>
</svg>
```

## Template: Side-by-Side Comparison

```xml
<!-- LAYOUT PLAN
  Figure purpose: Compare two approaches
  Canvas: viewBox="0 0 850 300"
  Element count: 5 (2 boxes + divider line + 2 header labels)

  Elements:
    Left panel:   x=30,  y=60,  w=380, h=220 → right: 410
    Right panel:  x=460, y=60,  w=380, h=220 → left: 460 (gap: 50px ✓)
    Divider:      x=435, y=40 to y=300
    Left label:   x=220, y=40
    Right label:  x=650, y=40
-->
<svg viewBox="0 0 850 300" xmlns="http://www.w3.org/2000/svg">
  <text x="220" y="40" text-anchor="middle" font-family="system-ui, sans-serif"
        font-size="18" font-weight="600" fill="#EF4444">Anti-Pattern</text>
  <rect x="30" y="60" width="380" height="220" rx="8" fill="#FEF2F2" stroke="#FECACA"/>

  <line x1="435" y1="40" x2="435" y2="280" stroke="#E5E7EB" stroke-width="2" stroke-dasharray="6,4"/>

  <text x="650" y="40" text-anchor="middle" font-family="system-ui, sans-serif"
        font-size="18" font-weight="600" fill="#10B981">Pro-Pattern</text>
  <rect x="460" y="60" width="380" height="220" rx="8" fill="#F0FDF4" stroke="#BBF7D0"/>
</svg>
```

## Template: Balance / Scale

Effective for showing "we value X MORE, but Y still has value":

```xml
<!-- LAYOUT PLAN
  Figure purpose: Show weighted balance between two values
  Canvas: viewBox="0 0 850 280"
  Element count: 5 (fulcrum + beam + 2 pans + 2 labels)

  Elements:
    Fulcrum:      triangle at x=425, y=240, base=60
    Beam:         line from (100,140) to (750,180) — tilted left-heavy
    Left pan:     rect x=60, y=80, w=200, h=60
    Right pan:    rect x=590, y=130, w=200, h=60
    Left label:   x=160, y=110
    Right label:  x=690, y=160
-->
```

## Template: Vertical Stack (layered concepts)

```xml
<!-- LAYOUT PLAN
  Figure purpose: Show layered architecture or priority stack
  Canvas: viewBox="0 0 600 350"
  Element count: 4 (4 stacked rectangles)

  Elements:
    Layer 1 (top):    x=100, y=20,  w=400, h=60
    Layer 2:          x=100, y=100, w=400, h=60 (gap: 20px ✓)
    Layer 3:          x=100, y=180, w=400, h=60 (gap: 20px ✓)
    Layer 4 (bottom): x=100, y=260, w=400, h=60 (gap: 20px ✓)
-->
```

## Anti-Patterns: Figures You Should NOT Create

These visual types consistently produce bad results in slides:

- **Full system architecture diagrams** — Too many elements. Show one subsystem at a time.
- **Mind maps** — Branches overlap. Use a simple grouped layout instead.
- **Detailed UML** — Wrong context. Slides support a speaker; UML replaces one.
- **Data tables with 5+ columns** — Use the slide's own markdown table, not SVG.
- **Org charts deeper than 2 levels** — Becomes unreadable at slide scale.
- **Pie charts** — Hard to label cleanly in SVG. Use a horizontal bar instead.
