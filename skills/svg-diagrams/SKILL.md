---
name: svg-diagrams
description: Draws a diagram or figure committed to a repo as a hand-authored SVG file that reads the same in a host's light and dark themes. Use when adding or fixing a diagram linked from a README or docs page. Not for a figure inline in a Slidev slide (slide-rubric).
---

# SVG diagrams

A committed diagram is an `.svg` file beside the Markdown page that links it:
`![alt saying what it shows](name.svg)`.

## How it renders

- A linked `.svg` renders as an `<img>`, which loads no external font or image and runs no script.
- A media query inside it follows the OS theme, not the host's.

## Rules

- The first element is a white `rect` with a 1-px border covering the whole `viewBox`: the figure
  carries its own background into a dark theme.
- System font stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif`.
- No `<image>`, `<foreignObject>`, `<script>`, web font, or `href` outside the file.
- `role="img"` and `aria-label` on the root, and a `<title>` saying what the figure shows.

## Render before committing

On macOS, render a copy with the root's `width` and `height` removed, then Read the PNG:

```bash
qlmanage -t -s 1400 -o <tmp dir> <copy>.svg
```

`qlmanage` crops a figure that carries `width` and `height`. Fix text that overflows its box or
overlaps a line, and render again.
