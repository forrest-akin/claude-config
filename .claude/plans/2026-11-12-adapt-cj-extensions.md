# Plan: adapt recent cj-claude-extensions changes

Date: 2026-11-12. Source repo: `/Users/forakin1/gitlab.cj.dev/ai/cj-claude-extensions` at
`def0c006`. Branch `adapt-cj-extensions` from `main` (9f32e62). Three installments, run in order,
one implementer each. No push.

## Decisions

- Forrest, 2026-11-12: the stop conditions widen on both points (commit 9).
- Forrest, 2026-11-12: an unattended implementer lands an unanswerable no-test change and reports
  it skipped with the reason (commit 8).
- `disable-model-invocation` (commit 10): the reason "a side effect outside the worktree" becomes
  "a side effect outside the worktree that cannot be a dry run first". `disk-space-reclamation`
  already works that way: it deletes outside the worktree, is model-invocable, and dry-runs by
  default.
- `user-invocable: false` stays as documented here. code.claude.com/docs/en/skills.md, read
  2026-11-12: "Set to `false` when only Claude should invoke the skill".

## Rules for every commit

- Read the source with `git -C /Users/forakin1/gitlab.cj.dev/ai/cj-claude-extensions show <sha>`.
  Adapt the technique, not the text. No CJ tool or plugin names (Jira, GitLab, Kibana, file-todos,
  learn, `/workflows:work`, review-panel).
- Fewest words that carry the rule. State how things are, never how they changed.
- This plugin's skills are not loaded in the session: read `skills/design-rubric/SKILL.md` and
  `skills/doc-drift/SKILL.md` once and apply them before each commit.
- Script changes are red-green: write the failing test, watch it fail for the right reason, then
  implement.
- A touched skill passes `skills/extension-authoring/bin/lint-extension <path>` and
  `bash test/lint-skills.test.sh`. A touched script's suite passes.
- Plain Conventional Commits, no attribution footer, explicit paths staged. README changes land in
  the commit that makes them true. The first commit also stages this plan.
- One commit per numbered row. A row that turns out to need two reviewable commits is split; a row
  whose premise is false is skipped and reported with the evidence.

## Installment 1: skill prose

| # | Subject | Source | Change |
|---|---|---|---|
| 1 | `feat(skills): subagent-model-tiering names a model for every row` | ebb98ca8 | `skills/subagent-model-tiering/SKILL.md:18` "Unsure" row becomes `opus` at `high`, say why. Add: never omit `model` or `effort`; an omitted model runs the dispatcher's. Align the description, `references/platform.md` and `skills/workflow-design/SKILL.md:31` if they still allow omitting. |
| 2 | `feat(skills): subagent-model-tiering keeps brief and structural misses off the escalation path` | 3e1e154b, 645831b5 | "Escalate on a signal": first, a missing input (asked for a file, guessed a path) means fix the prompt, same model and effort. A structural miss (widened signature, rule left unenforced, duplicated decision) means same model and effort, and the rule becomes an invariant test. |
| 3 | `feat(skills): subagent-model-tiering tiers haiku by turns` | ec821b5b | Under the tier table: turns set cost and death risk, not token price. Reword or drop lines 52-53, which coach multi-step `haiku`. |
| 4 | `feat(skills): commit-sequencing gives a mechanical change its own commit` | 939f6082 | "Cutting": a mechanical change (formatting, file move, regenerated files, lockfile or dependency bump) or a preparatory refactor is its own earlier commit, never mixed with behaviour. |
| 5 | `fix(skills): commit-sequencing red flag allows expand-first commits` | dd2d272d | Line 37 "code unreachable after its commit" contradicts "Safe: … new components not yet wired" (:48-49). Flag code no later commit in the stack calls. Check `bin/stack-check` and its tests for the same wording. |
| 6 | `feat(skills): tdd keeps behaviour and structure in separate steps` | 66095bf6 | `skills/tdd/SKILL.md`: never add behaviour and restructure in one step; a rename that tempts mid-red is reverted until green. |
| 7 | `feat(skills): tdd tidies a forbidden shape before the first red` | f62cdc15 | `skills/tdd/SKILL.md`: a function about to be extended whose shape a rule or an invariant test's docstring forbids is brought into line first, as its own behaviour-preserving commit. An invariant breach is a red test or a stop, never a tidy. `skills/interface-design/templates/interface-draft.md:42-44` says "has a shape the invariants forbid" where it says "breaks an invariant"; keep `example.md`, the `converged.md` fixture and `bin/interface-check` consistent. |
| 8 | `feat(skills): tdd lands an unanswerable no-test change and reports it` | 1aa59c2d | `skills/tdd/SKILL.md:32-35`: where nobody can answer, land it with the rationale in the commit body and report the step skipped with the reason. |
| 9 | `feat(skills): implementers stop on a changed public answer or a changed assertion` | 6d3951a0 | First condition widens to: an existing public function would answer differently from today, or from another public entry point, for the same inputs, unless the plan names that change. Third widens to: an existing test's assertion would be weakened, narrowed, skipped, worked around or changed; when the behaviour change is the task and the test follows it, say so in one line of the report. Six files carry the text: `test/stop-conditions.test.sh` (change first, watch it fail), `skills/workflow-design/SKILL.md`, `skills/workflow-design/templates/implementer-block.md`, `skills/interface-design/example.md`, `skills/interface-design/templates/interface-draft.md`, `skills/interface-design/tests/fixtures/converged.md`. |

## Installment 2: extension-authoring and svg-diagrams

| # | Subject | Source | Change |
|---|---|---|---|
| 10 | `feat(skills): extension-authoring says where the script seam goes` | d0202454 | `skills/extension-authoring/SKILL.md`: a short section. Move a step into a bundled script when its inputs fix its answer. The script emits facts, one row per item with its reason, kept rows included; the model decides. Decision functions are pure; clock, filesystem and git output arrive as arguments. A deleting step is its own subcommand, a dry run by default, re-validating each row on apply. Failed or truncated detection exits non-zero. The skill body says what the script emits and what the model decides, not the script's checks. Line 24 takes the `disable-model-invocation` wording under Decisions. |
| 11 | `feat(skills): extension-authoring routes an invariant to an invariant test` | 1d0d47a0 | Homes list (`SKILL.md:86-99`): an invariant the code must hold becomes a test under `tests/invariants/`, ahead of the comment and rule homes; dedupe against existing ones. |
| 12 | `docs(skills): extension-authoring records worktree-hook behaviour` | git-worktree `SKILL.md` at dfbdf08a | `references/platform.md`: a `WorktreeCreate` hook replaces the harness's file copying, so `.worktreeinclude` is not processed; settings `env` passes `~` and `$HOME` unexpanded; any non-zero exit fails worktree creation. Keep the observed version where the source gives one. |
| 13 | `feat(skills): lint-extension flags a skill directory without SKILL.md` | 08639a8e (`skill-file-missing`) | `bin/lint-extension` `targets()` reports a directory under `skills/` that has no `SKILL.md`. |
| 14 | `feat(skills): lint-extension flags a miscased tool name` | 08639a8e (`tool-name-casing`) | A `tools` or `allowed-tools` entry that differs from a platform tool name only by case. First confirm from code.claude.com docs (`curl -sL <url>.md`) that tool names are case-sensitive in those fields; if the docs don't say, skip the row and report. |
| 15 | `feat(skills): add svg-diagrams` | 42c2d91b | New `skills/svg-diagrams/SKILL.md`, host-neutral, for a diagram committed to a repo as a linked `.svg`: it renders as an `<img>`, which loads no external font or image and runs no script; a media query inside it follows the OS theme, not the host's; system font stack; no `<image>`, `<foreignObject>`, `<script>` or outside `href`; `role="img"`, `aria-label` and `<title>`; own background panel; the `qlmanage` render check on a copy without `width`/`height`. Drop GitLab-only limits unless they hold on GitHub. Description distinguishes it from `slide-rubric` (inline Slidev SVG). README lists it wherever it lists skills. |

## Installment 3: tests

| # | Subject | Source | Change |
|---|---|---|---|
| 16 | `fix(skills): test suites keep git out of an inherited GIT_DIR` | 5059d364 | `skills/commit-sequencing/tests/test_stack_check.py`, `skills/design-rubric/tests/test_health_delta.py`, `skills/design-rubric/tests/test_notice.py`, `skills/doc-drift/tests/test_stale_refs.py`, `skills/plan-readiness/tests/test_noticed_scan.py` build their git environment from a minimal dict, not `os.environ`. Red first: a guard test that sets a decoy `GIT_DIR` and asserts the decoy is untouched. Skills stay self-contained, so no helper shared across skill directories. |
| 17 | `feat(test): one runner discovers every skill suite and fails on an empty one` | 479eb8de | A bash 3.2 script under `test/` that runs every `skills/*/tests` (Python `unittest` directories and `*.sh` tests), exits 1 when any suite fails or ran zero tests, exits 2 when it finds no suite, and prints a total. Its own test sits beside the other `test/*.test.sh`. `README.md:72` and `:89-98` name the runner in place of the per-suite lines. |
| 18 | `fix(skills): design-rubric notice skips an entry already in the ledger` | f167c657 | `skills/design-rubric/bin/notice` skips an entry whose path (line number ignored) and smell are already in `.claude/noticed.md`. Red first in `tests/test_notice.py`. |

## Verification at the tip

After commit 18, in a clean worktree of the tip: the runner from commit 17, every
`test/*.test.sh`, and `claude plugin validate <worktree>`.

## Implementer block

Stop conditions: two public entry points would give different answers for the same inputs; two
written rules conflict and no precedence settles it; an invariant test would have to be weakened,
narrowed, skipped or worked around.

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
