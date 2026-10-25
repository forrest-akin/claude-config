# claude-config

Personal Claude Code configuration: skills and, once present, standing instructions.

## Install

```bash
./install.sh
```

Symlinks `CLAUDE.md` (if present) and each `skills/*` directory into `~/.claude`. Re-running is safe.
It refuses to replace an existing `~/.claude/CLAUDE.md` or `~/.claude/skills/<name>` that is not its own link.

```bash
bash test/install.test.sh
```

Runs the installer against a fixture repo and a temporary `HOME`.

## Slidev

The `slidev` skill is upstream's (`slidevjs/slidev`) and is not copied here. Install it into the
presentations repo with the skills CLI:

```bash
npx skills add slidevjs/slidev
```
