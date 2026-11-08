---
name: workflow-design
description: Designs a multi-agent Workflow script that survives its own failures, with per-agent call budgets, checkpoints, resume-safe prompts, installments, monitoring, harvest after an interruption, and verify tiers. Use before writing or revising any Workflow script, or when a run retries, stalls, runs away or pays twice on resume. Not for script API syntax (workflow-authoring) or for choosing each stage's model (subagent-model-tiering).
---

# Workflow design

## Failure model

- Agents die from transient API errors, so each extra turn is another chance to die. A restarted
  agent starts over from its prompt and pays for its turns again; files it wrote survive.

## Prompts

- Never spend an agent on an answer a machine can produce (registry lookup, build, grep). The
  orchestrator fetches it and passes the result. Agents are for judgment.
- Every prompt names the cheapest exact source for its facts, a hard call budget, and a
  "return it marked unverified" exit.
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
  majority vote: a refuter rejects a true design claim by construction. Design reviewers judge
  by `design-rubric`.
- Report what the finders concluded, never only a refutation tally.
- Verify by group (mechanism, commit, subsystem), never one agent per finding. A
  findings-times-lenses shape gets redesigned.

## Executing a plan

- Size an implementer's batch from its files (about three calls each) plus a few calls for each
  task that writes code and for each commit's skill loads and `doc-drift` search; end the batch
  at the call budget or at a commit boundary.
- An implementer prompt tells it to load `doc-drift` and `design-rubric` before every commit,
  `error-modeling` when the commit adds a failure path, and `commit-sequencing` when it moves
  code.
- An implementer prompt also says: when two shapes fit the next test, drive both to green and keep
  the one whose test was easier to write.
- Every implementer prompt and handoff names three stop conditions: two public entry points
  would give different answers for the same inputs; two written rules conflict and no precedence
  settles it; an invariant test would have to be weakened, narrowed, skipped or worked around. In
  system-level work, a change on the breaking list in `commit-sequencing` ("What forces
  expand/contract") is the first.
- An implementer that meets a stop condition or an open trade-off ends its installment. Its report
  opens with a `Blocked:` block: the condition, the question, the options with its pick first, the
  proposed diff, and the commits it made before stopping. It commits green work only, nothing for
  the blocked step.
- Inside a Workflow a blocked task is terminal; the orchestrator re-dispatches it after the
  answer.
- Every task reports done, failed, or blocked with its `Blocked:` block, in a form a script can
  parse. A task that reports nothing probably exhausted its context: split it before retrying.
- Each implementer reports its deviations from the plan and its known defects. Before the next
  dispatch, the orchestrator reads them and either carries each into the next prompt or records
  it as a finding.
- A task too large to finish is divided once into a few independent subtasks. If one of those is
  still too large, ask the user.
- Before redispatching a failure, diagnose it; the new attempt gets the evidence and where to
  start, never the raw error. Give up after three attempts.
- A refine agent takes as many target commits as fit its call budget and folds them in one
  `rebase -i` with an edit stop at each. At each stop it re-checks the commit body's claims
  (counts, timings) against the rewritten tree.
- A loop that runs outside the session has a fixed iteration cap, named exit states, a fresh
  context each iteration and all its state in a file. After a crash, unfinished items return to
  the queue without spending a retry. The loop is finished when that file lists nothing
  outstanding, never when the logs look finished.

## Launch and monitor

- The launch summary states each stage's model and effort, agent count and token estimate, and
  flags a run past the large-workflow line (per-agent token costs: `references/platform.md`
  "Measured budgets"). The user's usage limit is shared with their other work.
- Monitor from launch. Poll about once a minute and heartbeat only when an agent passes its call
  budget, ~20 minutes pass with agents running but no new result, or an agent transcript ends in
  a user interrupt. An agent finishing is not a trigger: the Workflow's completion notification
  returns the results. Count each agent's calls from the `tool_use` blocks in its transcript, not
  from the watcher's notifications. On any heartbeat, read the transcript tail, then stop and
  relaunch with a tighter prompt, or harvest.

Platform facts (journal format, resume, limits) are in `references/platform.md`. Read it when a
run stalls, fails or is resumed.
