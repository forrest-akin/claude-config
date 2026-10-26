---
name: workflow-design
description: Designs a multi-agent Workflow script that survives its own failures, with per-agent call budgets, checkpoints, resume-safe prompts, installments, monitoring, harvest after an interruption, and verify tiers. Use before writing or revising any Workflow script, or when a run retries, stalls, runs away or pays twice on resume. Not for script API syntax (workflow-authoring) or for choosing each stage's model (subagent-model-tiering).
---

# Workflow design

## Failure model

- Agents die from transient API errors, so each extra turn is another chance to die. A restarted
  agent starts over from its prompt and pays for its turns again; files it wrote survive.
- CLAUDE.md "Subagents" sets the call budgets. Measured 2026-10-26 on a 1M window: 42-64 calls
  peaked at 102-156K tokens of context, with no deaths. Research agents died at 75-80 calls
  (2026-09-10).
- An open-ended agent re-sends its whole context every turn, so its cost grows faster than its
  turn count. If everything downstream waits on all upstream results, one runaway stalls the run.

## Prompts

- Never spend an agent on an answer a machine can produce (registry lookup, build, grep). The
  orchestrator fetches it and passes the result. Agents are for judgment.
- Every prompt names the cheapest exact source for its facts, a hard call budget, and a
  "return it marked unverified" exit.
- Split by kind of question, not by instance: many instances of one question over shared inputs
  go to one agent.
- Checkpoint: the agent appends results to a file as it goes, reads that file first on start,
  skips what is done, and returns a short summary plus the path. Deliverables are drafted in
  small incremental writes.
- Shared inputs are files named by absolute path, never inlined.
- A missing input is noted and skipped, never waited on.
- No stage assumes its predecessor returned anything.
- After a retry, re-verify anything a gate rests on instead of trusting the agent's checkpoint.
- Check a cheap model's structured output against the set of input IDs before acting on it, and
  drop rows that name no input.

## Approvals

- A subagent never acts on approval relayed through its prompt. Run the gated step in the main
  session, or record the approval in a durable artifact the stage reads.
- A transition that passes only a stable reference (commit SHA plus a written spec) may chain
  behind a deterministic check. One that passes judgment may not.
- Dialogue steps stay in the main session; only non-interactive steps are dispatched.

## Model and effort

Set per stage, never blanket (`subagent-model-tiering`). A retry-prone stage runs cheaper, since
every retry pays its effort again. After a stage's second stall, bound the request and drop its
effort: a request that opens with long deliberation stalls the same way on replay.

## Resume and recovery

- Relaunch replays agents in start order. Keep that order deterministic, and keep each prompt
  byte-identical across runs: pass stable IDs, checkpoint paths, or canonical payloads (sorted
  keys, no prose), never upstream prose that varies between runs.
- A hand-rolled pool that starts agents as others finish orders them by completion time and
  breaks replay.
- Give work items stable IDs at birth and dedupe by ID. Duplication on resume is silent and shows
  only as spend, so count result records per item.
- Recover an interrupted fan-out by harvest, not replay: read the finished results as data,
  write a new script over only the unfinished items, merge at synthesis. Copy finished results
  somewhere durable first; temp directories get purged.

## Shape

- Installments instead of bare caps. Each installment ends with a report: findings, files read
  with a one-line takeaway each, open questions each with what would answer it, next focus. A
  fresh agent seeded by the report continues only on named questions. About three installments
  at most.
- Start downstream work on the first finished upstream items instead of waiting for the phase.
- Independent lanes (repos, services) run as separate workflows, each launched when its own
  previous phase returns. Before launch, write each item's real dependencies (what it consumes,
  from which item); every barrier traces to one, and gates the task that needs the output, not
  the lane that contains it.
- Settle cross-lane contract decisions before forking, and look for hidden shared artifacts:
  two clones of one remote, identical paths, shared config. One working tree implements
  serially; parallel lanes need separate worktrees or repos.
- Before an expensive judgment stage, cluster inputs by shared mechanism. Verify the mechanism
  once, then enumerate its instances deterministically.

## Verify tiers

- Filter findings by severity deterministically before fanning out verifiers. Spend several
  lenses only on findings that block a commit.
- Refute correctness claims. Settle design claims (readability, altitude) by independent
  majority vote: a refuter rejects a true design claim by construction.
- Report what the finders concluded, never only a refutation tally.
- Verify by group (mechanism, commit, subsystem), never one agent per finding. A
  findings-times-lenses shape gets redesigned.

## Executing a plan

- Size an implementer's batch from its files (about three calls each) plus a few calls for each
  task that writes code; end the batch at the call budget or at a commit boundary.
- An implementer that meets an open trade-off stops and returns the options, its pick first.
- Every task reports done, failed, or blocked with what it is waiting on, in a form a script can
  parse. A task that reports nothing probably exhausted its context: split it before retrying.
- A task too large to finish is divided once into a few independent subtasks. If one of those is
  still too large, ask the user.
- Before redispatching a failure, diagnose it; the new attempt gets the evidence and where to
  start, never the raw error. Give up after three attempts.
- A loop that runs outside the session has a fixed iteration cap, named exit states, a fresh
  context each iteration and all its state in a file. After a crash, unfinished items return to
  the queue without spending a retry. The loop is finished when that file lists nothing
  outstanding, never when the logs look finished.

## Launch and monitor

- The launch summary states the batching, each stage's model and effort, agent count and token
  estimate, and flags a run past the large-workflow line. An opus agent at xhigh cost about 155K
  tokens (2026-09-10); sonnet or low effort costs a fraction. The user's usage limit is shared
  with their other work.
- Monitor from launch: poll about once a minute, heartbeat about every five. Alert when an agent
  passes its call budget, on ~20 minutes with agents running but no new result, and on an agent
  transcript that ends in a user interrupt. On an alert, read the transcript tail, then stop and
  relaunch with a tighter prompt, or harvest.

## Platform facts

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
- Workflow agents get no mid-run user input, and subagents have no `AskUserQuestion`. Subagents
  nest at most three layers below the main session by default
  (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`).
