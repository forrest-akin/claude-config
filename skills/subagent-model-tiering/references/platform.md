# Platform facts (checked 2026-11-07)

Docs read 2026-10-25 against Claude Code 2.1.310:
[sub-agents](https://code.claude.com/docs/en/sub-agents.md#choose-a-model),
[model-config](https://code.claude.com/docs/en/model-config.md),
[cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence.md),
the per-model prompting pages for
[Haiku 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5.md),
[Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5.md) and
[Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1.md).

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
