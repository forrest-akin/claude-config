# Presentations

Version-controlled repository for presentations, built with [Slidev](https://sli.dev).

## Writing rule — no announce-then-say, no ad-copy (HARD CONSTRAINT)

Applies to **all prose written or edited here** — speaker notes, slide bodies, design docs, and chat replies about this work. It is the `cantrillian-talk-writer` skill's Move 11 and Move 6, as a hard rule.

**Never write a clause whose only job is to announce that a meaningful sentence is coming.** Delete the frame; say the payload — the naked sentence is always stronger. Banned openers (non-exhaustive): `Here's the…`, `One frame for…`, `The key insight is`, `The point is`, `What I want to do is`, `Let me be/show/tell/walk you`, `The thing is`, `Bottom line`, `That's the point/invitation`, `Think about it this way`, `The reason X is`, `What's interesting is`.
*Allowed:* a clause pointing at something on screen (`here's the commit`, over a shown commit) and a story setup that withholds a payoff to build tension — those carry content.

**Never buff a line into a parallel/antithetical slogan** (billboard test: if it would fit on a t-shirt or a chapter heading, rewrite it as a plain spoken sentence).

**MANDATORY self-check** — before claiming any notes/slides/prose work is done, run this on each changed file and clear or justify every hit:

```bash
grep -rniE "here'?s (the|what|why|one)|one frame|the (key|whole) (insight|point|thing|frame)|the point is|what i (want|wanted) to|let me (be|show|tell|walk)|the thing is|bottom line|that'?s the (point|invitation|thing|whole)|think about it this way|the reason .* (is|matters)|what'?s interesting is" <file>
```

Not optional. A clean grep (or a one-line justification per allowed hit) is part of "done."

## Repository Structure

```
presentations/
├── presentations/           # Individual presentation directories
│   └── YYYY-MM-DD-title/
│       ├── slides.md        # Slidev source (main entry point)
│       ├── components/      # Vue components (optional)
│       ├── public/          # Static assets (images, etc.)
│       └── package.json     # Per-presentation Slidev config
├── .claude/
│   ├── agents/              # Presentation-specific agents
│   ├── commands/            # Slash commands for slide workflows
│   ├── rules/               # Rules for slide creation conventions
└── CLAUDE.md
```

## Creating a New Presentation

1. Run `/new-presentation` and follow the prompts
2. Or scaffold manually:
   ```bash
   cd presentations
   npm init slidev@latest YYYY-MM-DD-title
   ```

## Slidev Workflow

### Start dev server
```bash
cd presentations/YYYY-MM-DD-title
npx slidev slides.md
```

### Export to PDF
```bash
npx slidev export slides.md --format pdf
```

### Export to HTML
```bash
npx slidev build slides.md
```

## Slide Conventions

### File structure
Each presentation lives in its own directory: `presentations/YYYY-MM-DD-<kebab-title>/`

### Frontmatter (slides.md)
Every `slides.md` starts with a frontmatter block:
```yaml
---
theme: default
title: "Presentation Title"
info: |
  Brief description of the talk.
  Presented at: [Event], [Date]
author: <your-handle>
---
```

### Slide separators
- `---` — new slide

### Speaker notes
Speaker notes are the `<!-- ... -->` comment block at the end of the slide.

### Asset organization
- Images go in `public/` within the presentation directory
- Reference as `/image.png` (Slidev serves `public/` at root)

## Commit Conventions

- `add: YYYY-MM-DD-title` — new presentation
- `update: title - [what changed]` — iterating on a presentation
- `fix: title - [what fixed]` — corrections
- `export: title - PDF/HTML` — exported artifacts (usually not committed)
