---
name: slide-svg-figures
description: Draws non-overlapping inline SVG diagrams for slides (Slidev, PowerPoint, Google Slides) by planning every element's coordinates before rendering. Use when creating a figure, diagram, flowchart or comparison visual for a slide, or when a slide's SVG overlaps, cramps or runs text outside its boxes. Not for checking a finished deck (slide-auditor).
---

# Slide SVG Figures

Create production-quality SVG diagrams for slide presentations that never overlap, never cramp, and always communicate one idea clearly.

## The Golden Rules

These are non-negotiable. Violating any one of them produces a bad figure.

1. **One idea per figure.** If you can't state what the figure communicates in a single sentence, it's too complex. Split it.
2. **Plan before you render.** ALWAYS write a layout plan comment listing every element's x, y, width, height before writing SVG markup. See the Layout Planning section.
3. At most 7 shapes and connectors per figure; text labels do not count.
4. Spacing has no fixed number. Render the slide and judge legibility and clashes from the
   image: `npx slidev export <slides.md> --format png --range <n> --output <dir>`, then read
   the PNG. Export needs `playwright-chromium` in the deck's devDependencies.
5. **No font below 14px.** If text doesn't fit at 14px, the diagram has too many words — cut words, don't shrink text.
6. **3 words per line maximum inside shapes.** 2 lines maximum per shape. If you need more, the text belongs outside the shape as a label.
7. **The slide already has a title.** Never put a title or heading inside the SVG unless explicitly asked. It wastes vertical space and creates visual competition with the slide's own heading.

## Canvas Dimensions

Before creating any SVG, determine the available space. Read the reference file for target-specific dimensions:

- **Slidev presentations:** See [references/slidev-canvas.md](references/slidev-canvas.md)
- **PowerPoint/PPTX:** viewBox width ≤ 800, height ≤ 400 (safe area within 10×7.5 inch slide)
- **General/unknown:** viewBox width ≤ 850, height ≤ 400

Always declare an explicit `viewBox="0 0 W H"` on the `<svg>` element. Never omit the viewBox.

## Layout Planning (Mandatory)

Before writing ANY SVG markup, write a layout plan as an HTML comment. This is the critical step that prevents overlap.

### The Layout Plan Format

```xml
<!-- LAYOUT PLAN
  Figure purpose: [one sentence describing what this communicates]
  Canvas: viewBox="0 0 850 380"
  Element count: [N] (must be ≤ 7)

  Elements:
    Box "Auth Server":  x=50,  y=80,  w=180, h=70  → right edge: 230
    Box "Client App":   x=320, y=80,  w=180, h=70  → right edge: 500  (gap from prev: 90px ✓)
    Box "Resource API":  x=590, y=80,  w=180, h=70  → right edge: 770  (gap from prev: 90px ✓)
    Arrow A→B:          from (230, 115) to (320, 115)
    Arrow B→C:          from (500, 115) to (590, 115)
    Label "1. Request":  x=275, y=70   (centered above arrow, no overlap with boxes ✓)
    Label "2. Token":    x=545, y=70   (centered above arrow, no overlap with boxes ✓)
-->
```

## SVG Markup Patterns

Note: End the arrow 10px before the target element to prevent the arrowhead from overlapping the shape's border.

## Color Palette

Use these colors consistently across all figures in a deck. Read [references/color-palettes.md](references/color-palettes.md) for the full palette options.

### Default Palette

| Role | Hex | Usage |
|------|-----|-------|
| Primary | `#2563EB` | Main elements, key concepts |
| Accent | `#F59E0B` | Highlighted/emphasized elements |
| Danger | `#EF4444` | Negative, warning, anti-pattern |
| Success | `#10B981` | Positive, correct, pro-pattern |
| Neutral fill | `#F3F4F6` | Background shapes, secondary elements |
| Text on dark | `#FFFFFF` | Text inside Primary/Accent/Danger/Success fills |
| Text on light | `#1F2937` | Text inside Neutral fills or standalone |
| Borders | `#E5E7EB` | Shape outlines |
| Arrows/connectors | `#6B7280` | Lines and arrows |

## Visual Type Reference

Choose the right visual type for the message. See [references/visual-types.md](references/visual-types.md) for templates and when to use each type.

Quick selection guide:
- **Process/sequence** → Horizontal flowchart (3-5 boxes + arrows)
- **Comparison** → Side-by-side boxes or two-column layout
- **Hierarchy** → Top-down tree (max 2 levels)
- **Relationship** → Circles with connecting lines
- **Scale/spectrum** → Horizontal bar with labeled positions
- **Before/after** → Two panels with clear divider
- **Single statistic** → Large number with context label (use `fact` layout, skip SVG)
- **Quote** → Use `quote` layout, skip SVG

## Common Mistakes and Fixes

| Mistake | Why it happens | Fix |
|---------|---------------|-----|
| Text overflows box | Too many words inside shape | Cut to 3 words/line, 2 lines max |
| Labels overlap arrows | Labels placed at same y as arrow | Offset labels 25px above or below arrow |
| Elements crowd edges | No margin from viewBox border | Keep 20px minimum margin on all sides |
| Arrows cross through boxes | Complex layout with crossing paths | Simplify to linear flow, or use curved paths that route around elements |
| Inconsistent sizing | Boxes have different dimensions | Use uniform box sizes unless size encodes meaning |
| Too many colors | Every element has a different fill | Max 3 fill colors per figure + neutral |

### v-click Integration

To reveal SVG elements progressively:

```xml
<svg viewBox="0 0 850 350" xmlns="http://www.w3.org/2000/svg">
  <g><!-- Always visible: first element --></g>
  <g v-click><!-- Appears on click 1 --></g>
  <g v-click><!-- Appears on click 2 --></g>
</svg>
```

Wrap each reveal group in a `<g v-click>` element. Include related elements (box + its label + its incoming arrow) in the same group.
