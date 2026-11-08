# Handoff: refine the deterministic-skills branch from review

Date: 2026-11-07. Branch `deterministic-skills` at ad5b865 (46 commits over `main` 8e40ad1). Findings:
`.claude/work/deterministic-skills/review-{code,prose,commits}.md`. Forrest approved applying the
findings, the ff-merge into `main`, the push and the install run.

## Dispositions

- Apply every **defect** and every **nit** in the three files, with two exceptions below.
- Apply these **proposals**: `notice` rejects an entry without `:<line>` and writes at the git
  toplevel; `lint-extension` treats `#!/bin/bash -…` and `#!/usr/bin/env bash` as bash too;
  `regenerable_dirs` moves to `lib/select.sh` and both reclamation scripts source it; pacing.md
  and runbook pointers name their trigger; slide-rubric drops the gap annotations from the layout
  plan and the non-Slidev canvas limits; the slidev template's package.json adds
  `playwright-chromium`; workflow-design points at the Blocked templates instead of restating them;
  6897e64's body says why fixtures and script land together; `stack-check` counts `.claude/` lines
  in their own column and excludes them from `>300`.
- Skip: the jq-on-PATH proposal (consistency with `call-budget.sh` wins; the Deviations line
  stands) and the `git()` helper nit (leave the three copies).
- Extra defect found at review: `test_health_delta.py` fails when lizard is installed by mise
  but not on PATH. `health-delta` falls back to `mise which lizard` when `shutil.which` finds
  nothing, and the tests pass in a shell without mise on PATH.

## Procedure

Three agents, in order: **code** and **prose** in parallel, then **fold**.

- **code** works in the repo checkout on `deterministic-skills`. For each code finding: write the
  test that pins it, see it fail, fix, then `git commit --fixup <target sha>` staging only the files
  of that fix. A target that predates a rename of the file folds into the rename commit instead
  (slide-rubric scripts: 5258570). Files: `skills/*/bin/*`, `skills/*/scripts/*`, `skills/*/tests/*`,
  `skills/disk-space-reclamation/lib/*`, `hooks/*`, `test/*`, `install.sh`.
- **prose** works in a worktree on branch `ds-prose` from ad5b865. For each prose and commit-body
  finding on a file: edit, then `git commit --fixup <target sha>`. Slide-figure prose whose target
  predates 5258570 (6be05b8, cabc177) folds into 5258570. Files: `skills/*/SKILL.md`,
  `skills/*/references/*`, `skills/*/templates/*`, `README.md`, `CLAUDE.md`,
  `templates/slidev-presentations/**`. README lines that deae8ca added to "Skill scripts" move
  into a fixup for e6a57f1 (the deae8ca hunk is dropped by a fixup that removes them again, or
  the fold agent edits during the rebase).
- **fold** cherry-picks `ds-prose` fixups onto `deterministic-skills`, then runs one
  `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash --exec '<check>' 8e40ad1` where `<check>`
  byte-compiles every Python script, `bash -n`s every shell script, runs `claude plugin validate
  skills`, and amends the subject of HEAD from a sha→subject map (the 17 subjects over 72 chars,
  and the body edits for 6897e64, deae8ca, d946058). Resolves conflicts by hand keeping the later
  commit's intent. At the tip, in a clean worktree, runs every suite (`test/*.sh`, each
  `skills/*/tests`, the four reclamation bash tests), `claude plugin validate skills`,
  `lint-extension skills`, `stack-check main`, `stale-refs 8e40ad1`, `health-delta main`.
  Deletes the `ds-prose` branch and worktree. Reports the new tip and every result.

The main session then ff-merges into `main`, pushes, runs `install.sh`, and reports.
