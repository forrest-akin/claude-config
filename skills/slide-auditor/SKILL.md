---
name: slide-auditor
description: Audits a finished Slidev slides.md for SVG size, font, density, speaker-note and layout problems with a script, then fixes what it reports. Use after generating slides, or when asked to check, validate or audit a Slidev deck. Not for drawing or redrawing a figure (slide-svg-figures).
---

# Slide Auditor

Programmatic quality validation for Slidev presentations. Run the audit script after generating slides to catch issues before the user sees them.

## When to Use

- **After generating a slides.md file** — Always audit before presenting the file to the user.
- **When the user reports issues** — Overlapping elements, broken layouts, inconsistent colors.
- **During iteration** — After making fixes, re-audit to confirm the fixes worked.

## Running the Audit

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/audit_slides.py slides.md
```

The script outputs a structured report with issues categorized by severity:

- **ERROR** — Will visibly break the presentation. Must fix.
- **WARNING** — Likely to cause visual problems. Should fix.
- **INFO** — Style inconsistency or suboptimal pattern. Consider fixing.

## What the Audit Checks

### SVG Checks
- viewBox is declared on every `<svg>` element
- viewBox dimensions don't exceed the maximum in `slide-svg-figures/references/slidev-canvas.md`
- No font-size below 14px
- Element count per SVG (warns if > 7)
- Color values match the declared palette
- Text inside shapes uses `text-anchor="middle"` and `dominant-baseline="central"`
- Arrowhead markers are defined in `<defs>` when `marker-end` is used

### Slide Content Checks
- Word count per slide (warns if > 30 words, errors if > 50)
- Consecutive slides with the same layout type
- Missing speaker notes
- Speaker notes length (warns if < 80 words or > 300 words per slide)
- Slide count vs. expected timing

### Structural Checks
- Valid headmatter with required fields
- Proper slide separators (`---`)
- Frontmatter layout values match known Slidev layouts
- No orphaned v-click directives outside SVG/content

## Interpreting Results

After running the audit, address issues in priority order:

1. Fix all ERRORs — these will visually break the presentation
2. Fix WARNINGs that affect SVG layout (overlapping, overflow)
3. Fix WARNINGs about content density (too many words on slide)
4. Address INFOs for polish (color consistency, note length)

## Fixing Common Issues

### "SVG viewBox exceeds canvas limits"
Reduce the viewBox to the sizes in `slide-svg-figures/references/slidev-canvas.md`.

### "Font size below 14px"
Find the `font-size` attributes below 14 and either increase them or reduce the text to fit at 14px. Usually the fix is fewer words, not a smaller font.

### "Too many elements in SVG"
Count boxes, circles, text groups, and arrows. If over 7, ask: "Can this be two figures on two slides?" or "Which elements are secondary and can be removed?"

### "Slide word count exceeds 30"
The slide is trying to say too much. Move content to speaker notes. The slide should be a visual anchor, not a teleprompter.

### "Missing speaker notes"
Every content slide needs speaker notes. Title and end slides can optionally skip them.

### "Inconsistent color values"
Search for hex colors that are close to but don't match the palette. Common: `#3B82F6` instead of `#2563EB`, `#F59E0B` vs `#FBBF24`. Standardize to the declared palette.
