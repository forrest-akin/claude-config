# claude-config

A Claude Code plugin of skills and hooks. `CLAUDE.md` is Forrest's personal standing instructions;
the plugin does not install it. It reaches `~/.claude/CLAUDE.md` by a symlink you create:
`ln -s /path/to/repo/CLAUDE.md ~/.claude/CLAUDE.md`.

## Install

```bash
claude plugin marketplace add forrest-akin/claude-config
claude plugin install fakin-claude-config@forrest-akin
```

Skills load as `/fakin-claude-config:<skill>`.

## Update

An install is a cached copy pinned to `version` in `.claude-plugin/plugin.json`, so a release
bumps it and is pushed to `main`. Then:

```bash
claude plugin marketplace update forrest-akin
claude plugin update fakin-claude-config@forrest-akin
```

## Develop

```bash
claude plugin validate .
```

Run it without `--strict`: the plugin name warning and the root `CLAUDE.md` warning fail it.

A marketplace added from a local path loads the working tree, unpinned:
`claude plugin marketplace add /path/to/repo`.

## Hooks

`hooks/hooks.json` registers `call-budget.sh` on PostToolUse, `diff-size.sh` on PostToolUse
(Edit|Write) and `bash-prefix.sh` on PreToolUse (Bash).

- `call-budget.sh` tells an agent its tool-call count when it reaches 80% of the budget its first
  prompt names (the phrasings in `test/fixtures/budget-phrasings.txt`) and on every call from 100%.
- `diff-size.sh` tells the model the uncommitted size of the edited file's repo on every Edit or
  Write while it is over 200 lines or 4 files.
- `bash-prefix.sh` denies a Bash command that starts with `NAME=value` or `cd`
  and asks for literal absolute paths.

```bash
bash test/hooks-json.test.sh
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
```

## Skill scripts

`doc-drift`'s `bin/stale-refs` lists facts a diff removed that docs still state.
`commit-sequencing`'s `bin/stack-check BASE` measures each commit of a stack, counting `.claude/`
lines apart, and flags oversize and placeholder commits. `design-rubric`'s `bin/health-delta` lists
functions a diff took past a lizard threshold (the suite needs lizard on `PATH` or installed by
mise), and its `bin/notice` appends a line to `.claude/noticed.md` unless one with the same path
and smell is already there; `plan-readiness`'s `bin/noticed-scan <plan>` ranks the entries a plan
must dispose of. `workflow-design`'s `bin/wf-status <run>` reports each agent of a Workflow run and
exits 1 when one is over its call budget, idle or interrupted. `presentation-narrative`'s
`scripts/check_timing.py` checks an outline's timing table against the talk's window.
`slide-rubric`'s `scripts/audit_slides.py` audits a deck, and the `disk-space-reclamation` scripts
survey, select and apply a deletion plan. `interface-design`'s `bin/interface-check <draft>` checks
an interface draft against its template.

`test/run-skill-suites.sh` runs every `skills/*/tests` suite, its `test*.py` files by unittest
discovery and each `*.sh` file as one test, and prints the total. It exits 1 when a suite fails or
runs no test, and 2 when it finds no suite.

```bash
bash test/run-skill-suites.sh
bash test/run-skill-suites.test.sh
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
`presentation-narrative` from this plugin, as `fakin-claude-config:presentation-narrative`.
