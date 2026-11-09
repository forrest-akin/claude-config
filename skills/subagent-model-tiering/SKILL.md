---
name: subagent-model-tiering
description: Picks the model and effort for each subagent or workflow stage, with tier by kind of work, effort by ambiguity and the cost of a wrong answer, one-step escalation on a weak result, and how to prompt each tier. Use when about to make an Agent call or a fan-out, or when writing per-stage model options into a Workflow script. Not for the main session's own model, or for how many agents to run.
---

# Subagent model tiering

## Tier by the kind of work

Tiers, smallest to largest: `haiku`, `sonnet`, `opus`, `fable`.

| Work | Tier |
|---|---|
| Locate and list, where the dispatcher reads every hit | `haiku` |
| Exactly specified work something downstream checks: transforms, given-text edits, running a gate, routing among named options | `sonnet` |
| Judgment inside one project against a written spec: review, assessment, distilled research, test-first implementation, design-doc authoring, debugging | `opus` |
| Reconciling many independent outputs into one verdict; work across a repo or contract boundary | `fable` |
| Unsure | omit `model` and say why |

- A dispatcher is tiered by its own work, not its children's.
- Never mix models or effort inside a panel whose verdicts are compared.

## Effort by ambiguity and the cost of a wrong answer

- `low` only for one bounded lookup or a one-shot transform.
- Raise it for tool loops, review, research and debugging.
- The top levels are for long open-ended runs and terminal verdicts. Never `max` unless the user
  names it.

## Escalate on a signal, once

Re-run once, the whole panel if its verdicts are compared:

- Lazy (skipped items, stopped early): same model, one effort level up.
- Ignorant (confidently wrong, split verdict): one tier up.
- Schema miss: restate the schema and re-run unchanged.

A retry-prone stage runs cheaper, since every retry pays its effort again. After a stage's
second stall, bound the request and drop its effort: a request that opens with long deliberation
stalls the same way on replay.

## When a model is unavailable

A model-access error: step down one tier and stop requesting that model for the session. An
allowlist that blocks a model substitutes another, with a warning only in interactive sessions;
check `/tasks` for what actually ran.

## Prompting the dispatched model

- Steer depth with `effort`, not wording: asking `haiku` or `sonnet` to think less doesn't reduce
  thinking.
- Tell a low-effort `haiku` in a long prompt to keep going until everything is done and to run a
  real check before reporting; it otherwise stops early or reports unchecked work.
- Give a searching `haiku` today's date.
- State a completion condition for `fable`, which can end on a "Next, I'll..." note that becomes
  the result. Give it the outcome, not steps; ask for targeted edits, and for bugs it finds
  outside the task to be reported, not fixed.
- Ask for the answer you will read, not a memo.

Model resolution order, aliases and effort precedence are in `references/platform.md`. Read it
when a subagent runs a model or effort other than the one requested.
