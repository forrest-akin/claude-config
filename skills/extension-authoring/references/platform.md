# Platform facts (checked 2026-11-08)

## Silent failures

Skills:
- Frontmatter is read only when `---` is the first line; otherwise the whole file is body. YAML
  that doesn't parse loads the skill with no fields: `/name` works, auto-triggering doesn't.
  `claude plugin validate <skills dir>` finds parse errors (v2.1.233+).
- Unknown frontmatter keys are ignored without error. Skill keys are hyphenated (except
  `when_to_use`); agent keys are camelCase.
- Only `<skills dir>/<name>/SKILL.md` is discovered; deeper trees are not. A folder named
  `synced` is skipped.
- `paths:` globs are relative to the working directory; files outside it, such as a sibling
  worktree, never match.
- `description` plus `when_to_use` is cut at 1,536 characters. The whole listing gets 1% of the
  context window; past that, the least-used skills lose their descriptions and list as bare
  names.

Agents:
- Skipped without a word in the session when `name` is missing, `---` isn't the first line, the
  YAML doesn't parse, or `description` is missing. Misspelled keys: run `claude --debug` and
  search the log for `does not recognize or apply` (v2.1.296+).
- If no `tools` entry resolves to a tool, the agent fails to launch.
- A `skills:` entry that is missing, disabled or `disable-model-invocation` is skipped with only
  a debug-log warning.
- Subagents load the CLAUDE.md hierarchy (not Explore or Plan) but never the main session's auto
  memory.

Hooks:
- Only exit 2 blocks, and Claude reads its stderr as the reason: say there, in plain text, what
  to do instead. Any other non-zero exit is a non-blocking error and the action proceeds. stderr
  from exit 0 never reaches Claude.
- macOS `/bin/bash` is 3.2: no associative arrays, no `${var,,}`. Use Homebrew bash or python3.

Plugins:
- A `CLAUDE.md` at the plugin root is never loaded; put instructions in a skill.
- A component path that resolves outside the plugin root doesn't load.
- The `CLAUDE_PLUGIN_ROOT` substitution resolves in skill, command and agent bodies, but isn't
  set in the Bash tool's environment.
- A plugin name starting with "claude-" fails `claude plugin validate` as reserved; one
  containing "claude" elsewhere passes with a warning that it reads as Anthropic's own.
- Each validate warning, the root CLAUDE.md one included, fails `--strict` (2.1.319).
- A marketplace added from GitHub installs a cached copy pinned to `version`; one added from
  a local path loads the working tree, unpinned.

Memory and configuration:
- Only the first 200 lines or 25 KB of `MEMORY.md` load; topic files are read on demand, so a
  memory with no index line is invisible.
- The auto-memory directory is derived from the git repository and shared by its worktrees. Find
  it by listing `~/.claude/projects/*/`, not by computing the name.
- MCP servers live in `~/.claude.json` (local and user scope), `.mcp.json` (project scope) or
  `--mcp-config`, not in `settings.json`.

## Rule and import loading

Path-scoped rules load when Claude reads, writes or edits a matching file, including a
single-file Bash read like `cat`; rules without `paths:` load every session. `@` imports load
the whole target along with the importer. `CLAUDE.local.md` is gitignored and exists only in
the worktree that has it.

## Sources

Docs read 2026-10-25 against Claude Code 2.1.310:
[skills](https://code.claude.com/docs/en/skills.md),
[sub-agents](https://code.claude.com/docs/en/sub-agents.md),
[hooks](https://code.claude.com/docs/en/hooks.md),
[memory](https://code.claude.com/docs/en/memory.md),
[mcp](https://code.claude.com/docs/en/mcp.md),
[plugins-reference](https://code.claude.com/docs/en/plugins-reference.md),
[plugin manifest](https://code.claude.com/docs/en/plugins/manifest-reference.md). Observed on
2.1.310 the same day: the base-directory prefix on a loaded skill, and placeholder substitution
and command execution inside code fences.
