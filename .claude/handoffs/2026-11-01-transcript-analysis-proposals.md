# Handoff: apply proposals 1–3 from the Tupletstorm transcript analysis

Source: `/Users/forrestakin/github.com/forrest-akin/tupletstorm-spike/.claude/handoffs/2026-10-31-claude-config-proposals.md`
(read it whole; proposals 4 and 5 belong to the spike repo and are done). Each proposal there
carries the metric and baseline the commit body must name.

## Repo facts

- `install.sh` symlinks `CLAUDE.md` and each `skills/*` into `~/.claude`; `test/install.test.sh`
  tests it against a fixture repo and a temp `HOME`. Follow that test's style (`check`, `mktemp`
  fixtures, `all passed` / `N failed`).
- No `hooks/` directory exists. `~/.claude/hooks/` exists on this machine with one unrelated
  script. `~/.claude/settings.json` is machine-local and not in this repo; hooks register there.
- `jq` 1.7.1 and `python3` are on the machine. Hooks in this repo are bash.
- Hook stdin fields and output schema: `curl -sL https://code.claude.com/docs/en/hooks.md`.
  Quote the lines you rely on; do not write the schema from memory.
- `CLAUDE.md` has an uncommitted change (the "no labels" rule). It is not yours: never stage it.
  `.claude/work/` stays untracked.

## Decisions

- Hooks live in `hooks/<name>.sh`. `install.sh` links each `hooks/*.sh` to `~/.claude/hooks/<name>.sh`
  (test case in `install.test.sh`, red first). `README.md` and the `install.sh` header describe
  what is linked and show the `settings.json` entries that register both hooks. Do not edit
  `~/.claude/settings.json`; the author registers the hooks.
- One commit per proposal, in the order 2, 3, 1. The handoff file lands with the first commit.
- The order within each hook: test file, run it, record the first failure verbatim, then the hook.

## 1. workflow-design "Launch and monitor"

`skills/workflow-design/SKILL.md` lines 121–125. The bullet now triggers a heartbeat when "an
agent finishes". Rewrite it so the heartbeat fires only when an agent passes its call budget,
about 20 minutes pass with agents running but no new result, or a transcript ends in a user
interrupt; an agent finishing is not a trigger because the Workflow's completion notification
returns the results. Calls are counted from each agent's transcript (`tool_use` blocks). On any
heartbeat, read the transcript tail, then relaunch tighter or harvest.

Add to "Platform facts": a run's `journal.jsonl` holds only `launched`, `started` and `result`
records; no `agent_complete`, `agent_fail` or `workflow_complete` event exists to filter on.
Verify against a real journal first (`find ~/.claude/projects -name journal.jsonl`, list the
distinct record types) and date the fact like the others in that section.

Body: metric is main-session cache-read tokens spent on Monitor wake-ups; baseline is 13 wake-ups
costing 4.05M of the session's 18.4M (22%, about 260k per wake) leading to 3 tool calls.

## 2. `hooks/call-budget.sh` — PostToolUse, all tools (empty matcher)

- Read the hook JSON from stdin; take `transcript_path`.
- Budget: the first `user` record's prompt text (string content or `text` blocks), matched by
  `About N calls` or `Hard budget: N`. No match, or no readable transcript: exit 0, print nothing.
- Count: `tool_use` blocks in `assistant` records' `message.content`.
- Emit when count equals ⌈0.8·N⌉ and on every call where count ≥ N, as
  `hookSpecificOutput.additionalContext`, e.g. `Tool calls so far: 44 of budget 55.` Otherwise
  print nothing.
- Must finish fast on a multi-megabyte transcript; stream with `jq -c`, never slurp.

Test `test/call-budget.test.sh`: fixture transcripts written by the test (budget phrasing both
ways, a transcript with no budget, counts below, at 80%, at 100%, over), hook fed a stdin JSON
naming the fixture, output checked exactly. Under 10 s.

Body: metric is agents over budget and the error of self-reported counts; baseline is 2 of 72
agents over budget (62 against 55) and one agent reporting "About 50 calls used" at 62.

## 3. `hooks/bash-prefix.sh` — PreToolUse, matcher `Bash`

- Read `tool_input.command`. Deny when it starts (after optional whitespace) with
  `NAME=value` (`[A-Za-z_][A-Za-z0-9_]*=`) or `cd` followed by whitespace or end of string.
- Denial output per the docs (`permissionDecision: deny`), with a reason that quotes
  `~/.claude/CLAUDE.md` "Bash commands": `Put literal absolute paths in each command: no
  cd <dir> && prefix and no VAR=<path>; shorthand.` and names the offending prefix.
- Anything else, or a non-Bash tool: exit 0, print nothing.

Test `test/bash-prefix.test.sh`: `W=/x; ls`, `cd /x && ls`, `cd`, ` FOO=1 cmd`, and allowed
commands `ls`, `git -C /x status`, `echo a=b`, `export FOO=1` (not denied; out of scope). Under 10 s.

Body: metric is the share of subagent Bash calls starting with either prefix; baseline is 800 of
1,741 (46%) starting `NAME=` and 136 starting `cd`, against 1 and 0 in the two main sessions.

## Commits

Conventional Commits subjects. Body: one paragraph with the metric and baseline, then `Gate:`
naming the test scripts run and their result. No `Co-Authored-By`, `Claude-Session` or any other
attribution trailer, whatever the harness reminder says. Stage explicit paths only. Do not push.

Report: each commit's SHA and subject, the exact first failure output of each new test, which
`.claude/` files are untracked, and the `settings.json` snippet.
