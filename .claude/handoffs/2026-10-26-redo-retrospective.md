# Handoff: apply the tupletstorm redo's learnings

Tupletstorm's Phase 0 was rebuilt with these skills and this CLAUDE.md loaded. A retrospective
measured what that bought and cost, and proposed changes. The user approved some of them on
2026-10-26; this session makes those changes.

Source, with each learning's evidence, proposed change and metric:
`/Users/forrestakin/github.com/forrest-akin/tupletstorm/.claude/work/redo-main/retro/retrospective.md`
(section 3). Its inputs (`outcomes.md`, `process.md`, `attribution.md`, `critique.md`) sit beside
it. Read the cited section before editing.

## Approved

| File | Change | Retrospective |
| --- | --- | --- |
| `skills/workflow-design/SKILL.md` | An implementer prompt names `doc-drift` for every commit, `error-modeling` when the commit adds a failure path, and `commit-sequencing` when it moves code | 3.1 |
| same | Replace the call-budget measurement with the 2026-10-26 one, and size a commit-sized installment at about 55 calls | 3.3 |
| same | A refine agent does one `rebase -i` with edit stops for all its target commits | 3.5 |
| same | The orchestrator triages each run's deviations and known-defect notes before the next dispatch | 3.7 |
| same | Heartbeat on state change only; count calls from the transcript | 3.9 |
| same | A refiner re-checks each folded commit's body claims against the rewritten tree | 3.10 |
| `skills/plan-readiness/SKILL.md` | Report three or more findings of one category as one rule fix; after a user revision, re-judge only the sections it touched | 3.4 |
| same | A rewrite of an existing system starts with a probe inventory of that system's defects and untrue docs | 3.8 |
| `skills/tdd/SKILL.md` | Before asking whether code can land untested, check whether it can move beneath the entrypoint | 3.6 |
| `CLAUDE.md` "Subagents" | Size by calls per installment, and weigh cache reads per call against the roughly 42k fixed start cost, replacing "an agent that does one small task is mostly overhead" | 3.3 |
| `CLAUDE.md` "Commits" | After a rebase or fold, run a compile check (`cargo check`, `tsc`) at each rewritten commit; full tests still run only at the tip | 3.5 |
| `CLAUDE.md` "Commits" | A commit body names the gates run and any deviations from the plan, not every test name | 3.10 |

Three items aren't rule changes. They were compliance gaps in that run, so leave the wording
alone: budgets of "about 40" against the skill's 30, heartbeats above the skill's rate, and a
third plan-judging round against plan-readiness's two-pass cap (retrospective §3, opening
paragraph). Retrospective 3.11 also needs no rule change.

## Constraints

- Load `extension-authoring` first; it governs how a skill or rule change is written and checked.
  Measure each change with the deterministic tests in `test/`. No eval runs without the user's
  case-by-case approval.
- `tdd`, `commit-sequencing` and `plan-readiness` changed at `1bd051e`, `4106ac5` and `55d5ea5`
  during the redo. Read the current text, not the retrospective's quotes.
- Commit in small commits, one skill or one CLAUDE.md section each. No attribution trailers, and
  do not push.
