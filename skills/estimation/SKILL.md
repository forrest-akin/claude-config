---
name: estimation
description: Estimates effort and wall-clock time with Claude doing the mechanical work, so cheap work isn't priced at human rates and the simpler option isn't chosen on false cost grounds. Use when asked how long something will take or whether it's worth it, when weighing a simpler approach against a more ambitious one, and before recommending the simpler option on cost. Not for choosing between designs on failure modes or moving parts.
---

# Estimation

Human-only intuitions overprice mechanical work. Correct for it before quoting a number.

## Decompose first

Split the work into four kinds:

- **Mechanical work Claude does**: minutes to hours of tool calls.
- **Human decisions**: minutes to hours of human time each; often the bottleneck.
- **External waits** (CI, access, deploys, approvals): wall-clock time.
- **Slow-feedback debugging**: compresses only partly; pad it and state the uncertainty.

Total is roughly the longest wait, plus the decisions, plus a small share of the mechanical work,
plus the debugging pad. Show the decomposition and its assumptions; never lead with one rolled-up
number.

## Weigh it

- Price mechanical work at Claude's rate. Broad consistent refactors, tests and docs get cheap, so
  design and judgment become the dominant cost.
- Cheap effort is not a licence to add layers. The Design rule in `~/.claude/CLAUDE.md` judges
  options by failure scenarios and moving parts, not effort.

## Push back

Push back once, with the decomposition, when the user's cost reasoning is wrong. Don't push back
when the choice turns on non-cost factors, on human review load, or on API spend and session
length (Claude can't see those), or when the user has already heard the case.
