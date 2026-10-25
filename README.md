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

## Presentations template

`templates/slidev-presentations/` is a starting point for a Slidev presentations repo: a `CLAUDE.md`
with the writing rule and self-check, plus `.claude/` agents, the `/new-presentation` command and
a conventions rule. Copy it into a new repo by hand:

```bash
cp -R templates/slidev-presentations/. /path/to/presentations-repo/
```

Set `author` to your handle in the frontmatter the command writes. The writing rule draws on the
`cantrillian-talk-writer` skill and `slide-designer`'s arc on `presentation-narrative`, both linked by
`install.sh`.
