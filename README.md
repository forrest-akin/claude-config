# claude-config

Personal Claude Code configuration: standing instructions, skills and hooks.

`CLAUDE.md` holds the standing instructions. Linked to `~/.claude/CLAUDE.md`, it loads in every
session.

## Install

```bash
./install.sh
```

Symlinks `CLAUDE.md`, each `skills/*` directory and each `hooks/*.sh` into `~/.claude`. Re-running is safe.
It refuses to replace an existing `~/.claude/CLAUDE.md`, `~/.claude/skills/<name>` or `~/.claude/hooks/<name>.sh`
that is not its own link, and changes nothing when `~/.claude/settings.json` is not valid JSON.
Before linking, it removes each of its own links whose target in this repo is missing and prints
`unlinked <path>`; links elsewhere are left alone.

```bash
bash test/install.test.sh
```

Runs the installer against a fixture repo and a temporary `HOME`.

## Hooks

`install.sh` registers `call-budget.sh` on PostToolUse, `diff-size.sh` on PostToolUse (Edit|Write)
and `bash-prefix.sh` on PreToolUse (Bash) in `~/.claude/settings.json`, adding each entry once.

- `call-budget.sh` tells an agent its tool-call count when it reaches 80% of the budget its first
  prompt names (the phrasings in `test/fixtures/budget-phrasings.txt`) and on every call from 100%.
- `diff-size.sh` tells the model the uncommitted size of the edited file's repo on every Edit or
  Write while it is over 200 lines or 4 files.
- `bash-prefix.sh` denies a Bash command that starts with `NAME=value` or `cd`, quoting
  `CLAUDE.md` "Bash commands".

```bash
bash test/call-budget.test.sh
bash test/bash-prefix.test.sh
bash test/diff-size.test.sh
```

## Stop conditions

`test/stop-conditions.test.sh` checks that each copy of the three stop conditions from
`workflow-design` "Executing a plan" keeps every clause word for word.

```bash
bash test/stop-conditions.test.sh
```

## Extension lint

`test/lint-skills.test.sh` runs `extension-authoring`'s `bin/lint-extension` over `skills/` and
fails on any finding.

```bash
bash test/lint-skills.test.sh
python3 -m unittest discover -s skills/extension-authoring/tests
```

## Skill scripts

`doc-drift`'s `bin/stale-refs` lists facts a diff removed that docs still state.
`commit-sequencing`'s `bin/stack-check BASE` measures each commit of a stack, counting `.claude/`
lines apart, and flags oversize and placeholder commits. `design-rubric`'s `bin/health-delta` lists
functions a diff took past a lizard threshold (the suite needs lizard on `PATH` or installed by
mise), and its `bin/notice` appends a line to `.claude/noticed.md`; `plan-readiness`'s
`bin/noticed-scan <plan>` ranks the entries a plan must dispose of. `workflow-design`'s
`bin/wf-status <run>` reports each agent of a Workflow run and exits 1 when one is over its call
budget, idle or interrupted. `presentation-narrative`'s `scripts/check_timing.py` checks an
outline's timing table against the talk's window. `slide-rubric`'s `scripts/audit_slides.py` audits
a deck, and the `disk-space-reclamation` scripts survey, select and apply a deletion plan.

```bash
python3 -m unittest discover -s skills/commit-sequencing/tests
python3 -m unittest discover -s skills/doc-drift/tests
python3 -m unittest discover -s skills/design-rubric/tests
python3 -m unittest discover -s skills/plan-readiness/tests
python3 -m unittest discover -s skills/workflow-design/tests
python3 -m unittest discover -s skills/presentation-narrative/tests
python3 -m unittest discover -s skills/slide-rubric/tests
for t in skills/disk-space-reclamation/tests/*.sh; do bash "$t"; done
```

## Slidev

The `slidev` skill is upstream's (`slidevjs/slidev`) and is not copied here. Install it into the
presentations repo with the skills CLI:

```bash
npx skills add slidevjs/slidev
```

## Presentations template

`templates/slidev-presentations/` is a starting point for a Slidev presentations repo: a `CLAUDE.md`
with the writing rule and self-check, plus `.claude/` agents, the `/new-presentation` command and
a conventions rule. Copy it into a new repo by hand:

```bash
cp -R templates/slidev-presentations/. /path/to/presentations-repo/
```

Set `author` to your handle in the frontmatter the command writes. `slide-designer`'s arc draws on
`presentation-narrative`, linked by `install.sh`.
