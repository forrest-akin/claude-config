---
name: subagent-model-tiering
description: Picks the model and effort for each subagent or workflow stage, with tier by kind of work, effort by ambiguity and the cost of a wrong answer, one-step escalation on a weak result, and how to prompt each tier. Use before an Agent call or a fan-out, or when writing per-stage model options into a Workflow script. Not for the main session's own model, or for how many agents to run (CLAUDE.md "Subagents").
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

- A model or effort the user names wins.
- A dispatcher is tiered by its own work, not its children's.
- Never mix models or effort inside a panel whose verdicts are compared.
- Name the model and effort in the line that announces each dispatch.

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

## Platform facts

Docs read 2026-10-25 against Claude Code 2.1.310:
[sub-agents](https://code.claude.com/docs/en/sub-agents#choose-a-model),
[model-config](https://code.claude.com/docs/en/model-config),
[cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence),
the per-model prompting pages for
[Haiku 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5),
[Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5) and
[Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1).

- Model order: the call's `model`, then the agent's frontmatter `model` (`inherit` means the main
  session's), then `CLAUDE_CODE_SUBAGENT_MODEL`, then the dispatcher's model.
- The docs say the fallback is the main conversation's model. Observed instead on 2.1.295 and
  again on 2.1.310: a nested subagent with no `model` runs its parent subagent's model.
- A family alias resolves to the main session's exact model when the main session is in that
  family, `[1m]` context included.
- The call-level `effort` needs v2.1.292+ and beats frontmatter `effort`;
  `CLAUDE_CODE_EFFORT_LEVEL` beats both, and `maxEffortLevel` or an organization cap still
  clamps. A fork takes neither parameter and runs the main session's model.
- `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (v2.1.257+) discards the call's and the frontmatter's
  model.
- An `availableModels` block on an alias runs the newest permitted model in that family, else
  the inherited model.
- Default effort is `high`, except `medium` on Opus 5.5, Sonnet 5.5 and Haiku 5.5 and `xhigh` on
  Opus 4.7.
