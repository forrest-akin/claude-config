---
name: slide-auditor
description: Audits a finished Slidev slides.md for SVG size, font, density, speaker-note and layout problems with a script, then fixes what it reports. Use after generating slides, or when asked to check, validate or audit a Slidev deck. Not for drawing or redrawing a figure (slide-svg-figures).
---

# Slide Auditor

Run the audit, passing the talk's length in minutes:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/audit_slides.py slides.md --timing <minutes>
```

Fix each finding and rerun until none remain. Per finding, choose the remedy: cut words, split
the slide, or move content to the speaker notes. Fix a font-size finding with fewer words, never
a smaller font. viewBox limits per layout are in `slide-svg-figures/references/slidev-canvas.md`.
