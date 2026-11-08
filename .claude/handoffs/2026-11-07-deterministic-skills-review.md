# Handoff: review of the deterministic-skills branch

Date: 2026-11-07. Branch `deterministic-skills`, 46 commits from `main` at 8e40ad1 to ad5b865,
110 files, +3928/−979. Plan: `.claude/plans/2026-11-07-deterministic-skills.md`. Decisions:
`.claude/brainstorms/2026-11-07-deterministic-skills.md` "Decisions".

Three reviewers, read-only. Each writes `.claude/work/deterministic-skills/review-<name>.md` with
one finding per line: `<file>:<line>` or `<sha>`, severity (defect / proposal / nit), one sentence,
and the commit the fix would fold into. A finding that adds a layer is a proposal, not a defect.

## Reviewer code: scripts, hooks, tests

Files: `skills/*/bin/*`, `skills/*/scripts/*`, `skills/*/tests/*`, `hooks/*.sh`, `test/*.sh`,
`install.sh`. Judge against `design-rubric`, `error-modeling` and `tdd`, and the plan's Phase 4
failure-behaviour notes. Look for: inputs that crash with a traceback instead of the stated error;
tests shaped to the code rather than the behaviour; a test that cannot fail; bash 4 syntax; duplicated
logic between scripts (the element count and palette live in `audit_slides.py` and
`deck_constants.json`); a helper with one caller.

Known defects reported by implementers, to confirm or dismiss:
- `install.sh` rewrites `~/.claude/settings.json` through jq on every run, bumping its mtime.
- `stale-refs` lists a deleted tracked file under `unread:`; a permission-denied file makes
  `git diff` fail with a traceback; only camelCase, CONSTANT_CASE and version tokens are found.
- `noticed-scan`: a root-level file is matched only when the plan names it exactly; an unreadable
  plan or a run outside a repo ends in a traceback.
- `health-delta`: same-named functions in one file collapse to one; lizard skips extensionless
  files, so every `bin/` script passes unmeasured; paths mix root- and cwd-relative from a subdir.
- `lint-extension`: link check does not skip code fences; `readarray` and `^^` share a pattern
  with no test of their own; frontmatter parsing joins indented lines onto the previous key.
- `slide-rubric`: the 3-digit hex pattern can match `url(#abc)` ids.
- `wf-status` reads stall time from the journal's mtime.
- `interface-check` reports "no numbered invariants" on an empty section (unspecified).

## Reviewer prose: skill bodies, references, templates, README, CLAUDE.md

Files: `skills/*/SKILL.md`, `skills/*/references/*`, `skills/*/templates/*`, `README.md`,
`CLAUDE.md`, `templates/slidev-presentations/**`. Judge against CLAUDE.md "Documentation and
comments" and "Concision", `extension-authoring` and the brainstorm decisions. Look for: "no
longer", "previously", "moved" or any description of a change; a body that restates its script's
output or a reference's content; a pointer to a template or reference without the symptom that
should trigger reading it; two statements of one rule (interface-design's convergence rule;
slide-rubric's remaining pixel numbers; the element budget); a skill that still names a deleted
skill or a path that moved; a description that no longer matches its body. Run
`skills/doc-drift/bin/stale-refs 8e40ad1` from the repo root and rule on each hit.

Known from implementers: tdd's "Two hats" heading covers one bullet; error-modeling's "Lints catch
both" reads loosely; slide-rubric keeps a 20px margin, 25px label offset and 10px arrow-end note;
visual-types.md templates use 20px gaps.

## Reviewer commits: the stack

Read `git log --reverse main..deterministic-skills` with `--stat` and each body. Judge against
CLAUDE.md "Commits" and `commit-sequencing`. Look for: a commit that would not deploy alone
(deletion before its replacement, a reference updated in a later commit); a body missing `Metric:`
or `Gate:`; a `Deviations:` line that contradicts the plan's decisions; an attribution trailer; a
refactor mixed with a behaviour change (1c1c146 is meant to be pure); the three unplanned commits
(4833381, 1c1c146, d946058) placed where they deploy alone; subjects over 72 chars or not
Conventional Commits. Run `skills/commit-sequencing/bin/stack-check main` and report its flags.
