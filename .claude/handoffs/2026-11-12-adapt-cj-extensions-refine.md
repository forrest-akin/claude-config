# Handoff: fold review findings into `adapt-cj-extensions`

Date: 2026-11-12. Branch `adapt-cj-extensions`, 18 commits on `main` (9f32e62), tip 17053f9,
unpushed. Plan: `.claude/plans/2026-11-12-adapt-cj-extensions.md`. Each fix below folds into the
commit that introduced it (`git commit --fixup <sha>`, then one autosquash rebase). No new commits
survive on the branch; it ends with the same 18 subjects. No push.

## Fixes

| Fold into | File | Fix |
|---|---|---|
| a9cc09c | `skills/subagent-model-tiering/SKILL.md:20` | "an omitted `model` runs the dispatcher's" contradicts `references/platform.md:12-13` (frontmatter and `CLAUDE_CODE_SUBAGENT_MODEL` come first). Line reads: "Never omit `model` or `effort`: an omitted `model` can fall through to the dispatcher's." This fixup also stages this handoff. |
| b7093c2 | `skills/subagent-model-tiering/SKILL.md:21-22` | Drop the trailing ", so `haiku` gets single-pass work only"; the tier table already places `haiku`. |
| 227ea11 | `skills/tdd/SKILL.md:10-12` | "Before the first red, a function … is brought into line first": drop the second "first". |
| 6809a3d | six copies of the stop conditions and `test/stop-conditions.test.sh` | The third condition's carve-out reads as a fourth item and never says the planned case is not a stop. Third condition reads: "an existing test's assertion would be weakened, narrowed, skipped, worked around or changed, unless the behaviour change is the task and the test follows it (say so in one line of the report)". Change the pinned clause in the test first and watch it fail. `skills/interface-design/tests/test_interface_check.py` locates its edit by this text; keep it finding it. |
| f5868a4 | `skills/extension-authoring/SKILL.md:118` | Rewrap the 114-character line to the file's width. |
| d1a15dc | `skills/extension-authoring/references/platform.md:33` | The bullet above says only exit 2 blocks. Open the new bullet with "Unlike other hooks, a `WorktreeCreate` hook fails worktree creation on any non-zero exit." |
| 02fc5f0 | `skills/extension-authoring/bin/lint-extension` `tool_casing_findings`, `tests/test_lint_extension.py` | `tools: Read, Grep  # read only, no edit` reports `read` and `edit` as miscased. Red first: add that input to the tool-casing test. Then strip a trailing YAML comment from the value before tokenizing. |
| ec8b9e1 | commit body only | The body says the health-delta suite "fails the same tests as before this change". Without lizard it fails those plus its own guard, whose exit-code assertion needs the suite green. Reword the body to say so. |
| 17053f9 | `skills/design-rubric/tests/test_notice.py` | `test_existing_ledger_gains_one_line` goes back to its form at 36d2864; only the new tests use `repo_with_ledger`. |
| 17053f9 | `skills/design-rubric/SKILL.md:95-96`, `README.md:80` | Both say `notice` appends a line. State that an entry whose path and smell are already in the ledger is not appended, in one clause each. |

## Mechanics

- Make the fixups in table order, then run once:
  `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash --autostash --exec 'bash test/lint-skills.test.sh' main`.
  Three commits touch `skills/subagent-model-tiering/SKILL.md` (a9cc09c, 77a481c, b7093c2), so the
  folds there can conflict: resolve to the text each commit should hold, keeping later commits'
  additions intact.
- The body reword is `git commit --fixup=reword:ec8b9e1` (an `amend!` commit the same autosquash
  consumes), with the message supplied through `GIT_EDITOR` since no editor runs here.
- If the rebase cannot be completed cleanly, `git rebase --abort`, leave the fixups on the branch,
  and report. The pre-refine tip is 17053f9.
- After the rebase, at the tip: `bash test/run-skill-suites.sh` (expect only `design-rubric` to
  fail, on lizard), every `test/*.test.sh`, `skills/extension-authoring/bin/lint-extension skills`,
  `claude plugin validate .`. Then `git log --oneline main..HEAD` shows 18 commits with the
  original subjects and no `fixup!` or `amend!`, and `git diff 17053f9 HEAD --stat` shows only the
  files in the table.

## Stop conditions

An existing public function would answer differently from today, or from another public entry
point, for the same inputs, unless the plan names that change; two written rules conflict and no
precedence settles it; an existing test's assertion would be weakened, narrowed, skipped, worked
around or changed, unless the behaviour change is the task and the test follows it (say so in one
line of the report).

If you meet a stop condition or an open trade-off, end your installment. Your report opens with a
`Blocked:` block: the condition, the question, the options with your pick first, the proposed diff,
and the commits you made before stopping. Commit green work only, nothing for the blocked step.

Your report's first line is `Status: done`, `Status: failed` or `Status: blocked`, followed for
blocked by the `Blocked:` block.

```
Blocked:
- Condition: <stop condition or open trade-off>
- Question: <one question for the human>
- Options: <my pick first, labelled as mine>; <other options>
- Proposed diff: <diff or path>
- Commits made: <short SHAs and subjects, or none>
```
