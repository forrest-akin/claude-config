# Platform facts (checked 2026-11-07)

Docs read 2026-10-25 against Claude Code 2.1.310:
[workflows](https://code.claude.com/docs/en/workflows.md),
[env-vars](https://code.claude.com/docs/en/env-vars.md),
[errors](https://code.claude.com/docs/en/errors.md),
[sub-agents](https://code.claude.com/docs/en/sub-agents.md).

- Relaunch returns each completed agent's saved result until the first agent whose prompt
  differs; that agent and every agent started after it run again. A failed agent reruns, and so
  does every agent started after it, even completed ones. Before v2.1.305, completed agents in
  `pipeline()`/`parallel()` items that ran several agents each could also rerun.
- A run resumes in the same session, a backgrounded one, or one reopened with `claude --resume`;
  a fresh session starts it over.
- Stall: no output for the agent's `stallMs`, else `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS`
  (default 10 minutes; covers workflow agents from v2.1.286). Time waiting on its own tool calls
  doesn't count. A stalled agent restarts at most five times without its old transcript, then
  `agent()` fails: inside `parallel()`/`pipeline()` the result is `null`, awaited directly the run
  ends. `agent lost its reply on all 6 attempts` is the stream idle watchdog
  (`CLAUDE_STREAM_IDLE_TIMEOUT_MS`); a longer `stallMs` doesn't help.
- `API Error: No response from API` is the first-byte deadline
  (`CLAUDE_STREAM_FIRST_BYTE_TIMEOUT_MS`, v2.1.242+), not a network fault.
- Usage limit (v2.1.271+): the run pauses for the reset only in an interactive claude.ai
  subscription session with `autoContinueAtUsageLimit` on, a reset within 24 hours, and at most
  two waits per run. Anywhere else the agent fails.
- The `Large workflow` warning fires past 25 scheduled agents or 1.5M projected tokens. Up to 16
  agents run concurrently by default; 1,000 agents per run.
- A run's `journal.jsonl` (`<session>/subagents/workflows/wf_<id>/`) holds only `launched`,
  `started` and `result` records; no `agent_complete`, `agent_fail` or `workflow_complete` event
  exists to filter on. Observed 2026-11-01 on 2.1.316 across 50 journals.
- Workflow agents get no mid-run user input, and subagents have no `AskUserQuestion`. Subagents
  nest at most three layers below the main session by default
  (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`).

## Measured budgets

- Call budget per installment: about 55 calls for an agent that builds or folds commits on a 1M
  window, about 30 for any other; no agent runs past 50% of its context window. Measured
  2026-10-26: 42-64 calls peaked at 102-156K tokens of context, with no deaths. Research agents
  died at 75-80 calls (2026-09-10).
- An opus agent at xhigh cost about 155K tokens (2026-09-10); sonnet or low effort costs a
  fraction.
