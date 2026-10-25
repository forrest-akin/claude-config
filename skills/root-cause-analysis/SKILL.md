---
name: root-cause-analysis
description: Traces a contained incident, regression, flaky test or near-miss from symptom to the underlying cause, with a counterfactual check at every step, and writes the chain as a one-page record. Use when asked why something broke, for an RCA, five whys or post-mortem analysis. Not for live firefighting, reproducing a bug, or a stakeholder post-mortem document.
---

# Root cause analysis

## The test at every step

A proposed cause survives only if its absence would have prevented the observation. Otherwise it
is correlation and is dropped.

## Terms

- **Symptom**: what was observed.
- **Contributing cause**: each one alone would remove or shrink the symptom.
- **Underlying cause**: the one whose absence makes the others insufficient. Usually a decision,
  default or missing safeguard, not an event.

## Depth and breadth

- Keep asking why, for however many steps it takes, until the answer is a system decision or
  falls outside the team's control; state that boundary and the workaround.
- Causality is a graph and the chain is one path through it. Name the sibling causes not pursued,
  each with its counterfactual, and whether they are independent, coupled or chained.
- Never name a person as a cause. Rewrite "X did Y" as "nothing prevented Y" and keep asking;
  stopping at the person is stopping too early. Malicious acts are a security matter, outside this
  frame.
- A near-miss gets the full analysis, including what the safeguard did right, so it isn't weakened
  later.

## Remediation

- Target the underlying cause. A fix aimed at a contributing cause is labelled tactical.
- A good remediation still reads as a system change months later ("validation step added"), never
  as "be careful".

## Output

About a page of prose: the symptom with time and impact; each causal layer with its
counterfactual; the underlying cause; contributors not pursued; remediation; any control boundary.
