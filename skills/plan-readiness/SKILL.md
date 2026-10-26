---
name: plan-readiness
description: Decides whether an idea needs a spike, a decision record, a spec or nothing before planning, and judges whether a plan or spec is ready to hand to a fresh implementer. Use when an idea or brainstorm is about to become a plan, before dispatching an implementation phase from a plan, or when asked whether a plan or spec is ready. Not for writing the plan itself, nor for cutting its commits (commit-sequencing).
---

# Plan readiness

## Before the plan: which design artifact

Run in order; stop at the first that applies.

1. **Spike** (time-boxed investigation) when two or more hold: a specific technical question blocks
   the design; plausible approaches differ materially; a key assumption could be disproven in a few
   days; a prior attempt surprised. Defer the later steps until it reports.
2. **Decision record** when two or more hold: the options are mutually exclusive at project scope;
   the choice is costly to reverse; someone will relitigate it without a written rationale.
3. **Spec** when two or more hold: the work spans several files or modules; error handling must be
   designed before coding; tests alone can't prove production behavior (concurrency, distributed
   state, environment).
4. Otherwise none: go straight to the plan.

- Resume an existing spike or decision record on the same topic instead of starting a new one. A
  finished spike is evidence for the later steps.
- If the user skips a recommended spike, proceed and record the unverified assumptions.
- Unsure between two artifacts: write the smaller.

## Artifact checks

- **Spike**: single-concern questions, each task mapped to a question, a definition of done, a time
  box, and no pre-written outcome.
- **Decision record**: at least one named downside and one rejected alternative.
- **Spec**: ready when a reader new to the project could build from it alone. It needs measurable
  goals, the parts and how data moves between them, each named failure with its handling, and
  something it rules out. Open decisions or questions, references the reader can't resolve, and
  implementation steps (the plan's job) fail it.
- Before handing a spec over, optionally trace each way a user enters, abandons, repeats or races
  the flow; each hole becomes a ranked question with the default you would assume.

## Plan checks

The bar: a context-free implementer makes no design choice.

**Blocking**
- A task leaves a decision open. In anything an implementer acts on (tasks, acceptance checks,
  instructions), a placeholder, a hedge or a verb that hands over the choice counts; background
  and quoted prose don't. Resolve it in the plan or move it upstream into a design artifact.
- A task lacks what changes and where.
- A task's acceptance check isn't an observable state (a file exists, a test passes, output
  matches); a quality adjective fails.
- A stacked commit doesn't deploy on its own (check with commit-sequencing).
- An entrypoint run by a host (extension, plugin, hook, handler) lacks a citation from the host's
  own source or docs of how it loads, runs and packages it: runtime, module loading, dependency
  rules, lifecycle. A probe that loads the host into your runtime proves the reverse.
- A destructive step (delete, overwrite, reset), including one carried from a spec, isn't checked
  against what its target holds once the whole plan has landed.
- The plan drops a constraint the user stated, reframes their goal, or claims something the
  dialogue didn't establish.

**Should fix**
- No existing file or pattern cited as evidence of research.
- No failure behavior for its main components.
- No rationale where a choice isn't obvious.

A stub plan's deliberately empty sections are skipped; everything it does contain is checked.

## Review discipline

- Evaluate every check, even after one fails.
- Report each problem in one sentence that names its section. Nothing to report is a valid result.
- Stop after two passes; when nearly everything blocks, rewrite rather than refine.
