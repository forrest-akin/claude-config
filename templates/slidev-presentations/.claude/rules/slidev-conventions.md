---
paths:
  - "presentations/**/*.md"
---

# Slidev Conventions

## Frontmatter
Every `slides.md` must open with a YAML frontmatter block containing at minimum:
- `theme` (use `default` unless a specific theme is needed)
- `title` (the full presentation title)
- `author` (author handle)

## Slide content principles
- One idea per slide — prefer more slides over dense slides
- Code blocks must specify a language (`ts`, `kotlin`, `java`, `bash`, etc.)
- Use `v-click` for progressive reveals rather than bullet dumping

## Speaker notes
Always add speaker notes for slides that have more than a title and a code block. Speaker notes are the `<!-- ... -->` comment block at the end of the slide.

## Layout choices
- Title slide: `layout: cover`
- Section dividers: `layout: section`
- Two-column content: `layout: two-cols`
- Code-heavy slides: `layout: default` (full width)
- Image showcase: `layout: image-right` or `layout: image-left`

## Naming
- Presentation directory: `presentations/YYYY-MM-DD-<kebab-title>/`
- Main file: always `slides.md`
- Assets: `public/<filename>` (not `assets/`)
