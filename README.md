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

```bash
bash test/install.test.sh
```

Runs the installer against a fixture repo and a temporary `HOME`.

## Hooks

`install.sh` registers `call-budget.sh` on PostToolUse and `bash-prefix.sh` on PreToolUse
(Bash) in `~/.claude/settings.json`, adding each entry once.

- `call-budget.sh` tells an agent its tool-call count when it reaches 80% of the budget its first
  prompt names (`About N calls`, `Hard budget: N`) and on every call from 100%.
- `bash-prefix.sh` denies a Bash command that starts with `NAME=value` or `cd`, quoting
  `CLAUDE.md` "Bash commands".

```bash
bash test/call-budget.test.sh
bash test/bash-prefix.test.sh
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
