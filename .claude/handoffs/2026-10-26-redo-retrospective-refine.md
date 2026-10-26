# Handoff: refine the redo-retrospective commits

Review of `1bd051e..f9217e0` (seeded by `2026-10-26-redo-retrospective.md`) upheld the fixes
below. Fold each into the commit named; all five are local only (`main` is ahead of
`origin/main` by 5), so rewriting them needs no force push. Do not push.

## User decisions, 2026-10-26

- The call budgets live in CLAUDE.md "Subagents": about 55 calls for an agent that builds or folds
  commits on a 1M window, about 30 for any other agent or installment. `workflow-design` keeps
  only the dated measurement.
- After a user revision, the plan re-judge covers only the sections it touched and does not count
  toward the two-pass cap. The cap's own wording stays.

## Fixes by commit

| Commit | File | Fix |
| --- | --- | --- |
| f6cc514 | CLAUDE.md "Commits" | The compile check after a rebase or fold runs at every commit the rebase replays (`git rebase --exec '<check>'`), not only at commits a fold changed. Stage this handoff here too. |
| 2f2281c | CLAUDE.md "Subagents" | State the budgets per the decision above. The merge test sums the extra cache read over all of the merged agent's calls. In "Batch to get there", "Keep apart only what" becomes "Also keep apart what", so it doesn't contradict the merge test. |
| 2f2281c | `skills/workflow-design/SKILL.md` "Failure model" | The budget bullet becomes the dated measurement only and points to CLAUDE.md "Subagents" for the budgets. It lands here so both files agree at this commit; at f9217e0, keep this version of the bullet. |
| f60d44f | `skills/plan-readiness/SKILL.md` | Define "one rule fix": three or more findings that break one plan-wide rule the same way are reported as one finding naming the rule the plan should state once. Add the re-judge decision above to the re-judge bullet. |
| f9217e0 | `skills/workflow-design/SKILL.md` "Executing a plan" | Batch sizing also counts each commit's skill loads and `doc-drift` search. Each implementer reports its deviations from the plan and its known defects; merge that into the bullet where the orchestrator reads them. |

## Commit messages

- Subjects of f60d44f and f9217e0 shrink to the repo's usual length (90 characters or fewer).
- Every body follows CLAUDE.md "Commits" as it reads at f6cc514. Replace "Tupletstorm redo retrospective <section numbers>:" with plain words, e.g. "In the tupletstorm Phase 0 redo:".
- f9217e0's body says two commits each had their conflicts resolved 3 times, not one.
- Name the deviations from the first handoff: at 2f2281c, the budgets sit in CLAUDE.md and it edits `workflow-design`'s budget bullet; at f9217e0, the start cost and budgets are stated only in CLAUDE.md, and "the call-count proxy for the 50% context target" is dropped.

## Second pass

A check of the refined commits (`1bd051e..3d647b7`) found three more. Replace the quoted text exactly.

| Commit | File | From | To |
| --- | --- | --- | --- |
| 9389671 | CLAUDE.md "Commits", fold recipe | `` `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash --autostash <base>` `` | `` `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash --autostash --exec '<check>' <base>` `` |
| a3595ea | CLAUDE.md "Subagents", "Batch to get there" | "into one agent until the budget is reached" | "into one agent while the merge test holds, up to the budget" |
| a3595ea | same paragraph | "If the whole work-list fits one agent, it is not a fan-out." | "If the whole work-list fits one agent and the merge test holds, it is not a fan-out." |
| 3d647b7 | commit body | " and a fold broke a later commit's compile" | (deleted; 9389671 addresses the break) |
