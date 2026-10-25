---
name: presentation-narrative
description: Designs a talk's story arc, pacing and slide outline from source material (an article, doc or notes). Use when asked to create a presentation outline, structure a talk about X, design the narrative for a deck, organize slides, or distill content into a presentation. Not for slide code or figures (slide-svg-figures) or speaker-note voice (cantrillian-talk-writer).
---

# Presentation Narrative Design

Transform source material into a compelling presentation narrative. This skill produces a structured slide outline — NOT slide code or visuals. It focuses on what every great talk needs: a story that earns its conclusion.

## When to Use

- Turning an article, document, or set of ideas into a presentation
- Structuring a conference talk, team presentation, or pitch
- Designing the narrative arc before building slides
- Choosing what to cut from dense source material

## Narrative Architecture Framework

Every effective presentation follows a tension-resolution arc. The audience needs to feel a question, a discomfort, or a gap in their understanding — and the presentation progressively resolves it.

### The Five-Act Structure for Technical Talks

Read `references/five-act-structure.md` for the full framework. Summary:

| Act | Purpose | Emotional state | Slides |
|-----|---------|-----------------|--------|
| 1. Provocation | Disrupt a belief the audience holds | Curiosity, mild discomfort | 1-2 |
| 2. Context | Give them the backstory they need | "I didn't know that" | 2-3 |
| 3. Evidence | Build the case with specific proof | Growing conviction | 2-3 |
| 4. Reframe | Show them the new way to think | "Oh, that changes things" | 1-2 |
| 5. Action | Tell them exactly what to do next | Motivated, clear | 1-2 |

Total: 8-12 content slides + title + closing = 10-14 slides.

### Pacing Rules

Read `references/pacing.md` for detailed pacing guidance. Key constraints:

- **90-second rule:** Average ~90 seconds per slide for a talk. For a 15-minute talk, that's 10 content slides max.
- **One takeaway per slide.** If a slide has two ideas, it needs to become two slides (or one idea needs to be cut).
- **The CTA must be earned.** If the call to action could be delivered without the preceding slides, the narrative failed.
- **Vary the energy.** Don't stack three "evidence" slides in a row. Alternate between data, quotes, diagrams, and assertions.

## Workflow

### Step 1: Identify the core argument

Before outlining slides, write one sentence that captures the entire talk:

> "Despite what most teams believe, [common assumption] is wrong because [evidence], and the right response is [action]."

If you can't fill this template, the talk doesn't have a clear argument yet. Work with the user to find one.

### Step 2: Identify the audience's starting belief

What does this audience currently believe? What assumption will the talk challenge? The gap between their starting belief and the talk's conclusion is the narrative engine.

### Step 3: Map the source material to the five acts

Go through the source material and tag each section/idea with an act:
- What provokes? (contradicts the audience's assumption)
- What contextualizes? (history, background)
- What proves? (data, quotes, specific evidence)
- What reframes? (the new mental model)
- What activates? (the specific ask)

### Step 4: Ruthlessly cut

A 15-minute talk can make ONE argument well. Not three. Not five. Identify the single strongest thread through the source material and cut everything that doesn't serve it. Moving content to "appendix" or "Q&A backup" is a good way to let go.

### Step 5: Produce the outline

For each slide, specify:
1. **Slide number and working title**
2. **Key takeaway** — the single sentence the audience remembers
3. **Narrative role** — which act this belongs to and why it exists
4. **On-screen content** — what the audience sees (keep sparse)
5. **Visual concept** — what type of figure supports this slide, or "no figure"
6. **Speaker notes summary** — 2-3 key talking points
7. **Transition** — how this slide connects to the next

After all slides, provide:
- **Narrative arc summary** — one paragraph describing the emotional journey
- **Potential cuts** — which 1-2 slides to drop if time is short
- **Risk flags** — what might not land with this audience

## Visual Concept Guidelines

When specifying visuals for slides, follow these principles:

**Not every slide needs a figure.** Some slides are more powerful as:
- A single quote on a dark background
- A single statistic in large type
- A provocative question in large text
- A simple two-column comparison

**When a figure IS needed, specify:**
- The visual TYPE (flowchart, timeline, comparison, scale/balance, etc.)
- What it communicates in ONE sentence
- The maximum number of elements (aim for 3-5)

**Visual variety across the deck:**
Don't use the same visual type for consecutive slides. Aim for this kind of rhythm:
```
Slide 1: Quote card
Slide 2: Single statistic
Slide 3: Timeline diagram
Slide 4: Text with v-click reveals
Slide 5: Comparison diagram
Slide 6: Quote card
Slide 7: Flowchart
...
```

## Reference Files

- `references/five-act-structure.md` — The complete five-act framework with examples
- `references/pacing.md` — Timing, density, and rhythm guidelines
