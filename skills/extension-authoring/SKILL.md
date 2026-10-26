---
name: extension-authoring
description: Writes and debugs Claude Code skills, subagents, hooks, rules and memory files so they load, fire on the right prompts and fail loudly, and decides where a lesson from a session should live. Use when writing or rewriting a SKILL.md, agent file, hook or rule, when a skill fires on the wrong prompts or never fires, when an extension silently doesn't load, or when asked to remember or capture what a session learned. Not for Workflow scripts (workflow-design) or a subagent's model (subagent-model-tiering).
---

# Extension authoring

## Descriptions

- The description is the trigger. Lead with what the extension does for the user, in words they
  would type; one use-when clause specific enough that a neighbour won't claim it; at most one
  "Not for X" naming the neighbour that should win.
- Say what it does for the user, never how it is packaged: no mechanics, heritage or dependency
  trivia.
- Shorter when the extension is reached only by name or by preload.
- Write the description before the body, and never let the body deliver less than it promises.
- Before creating a skill, check for collision: the same name, or three or more content words
  shared with an existing description.
- Optional cheap check: show a fresh session only the description and its neighbours' and ask
  which would fire for 5-10 prompts. One session, not an eval suite.

## Invocation

- Default to model-invocable. Set `disable-model-invocation: true` only for a side effect outside
  the worktree, timing the user must control, or a pure router. It takes the description out of
  context, makes the Skill tool refuse Claude, and bars preloading into agents.
- `user-invocable: false` hides a skill from the `/` menu for knowledge no one would run as a
  command.

## Bodies and supporting files

- Keep the body lean and move detail one level deep into files beside `SKILL.md`, each linked
  from the body with what it holds and when to read it.
- Link those files relative to `SKILL.md`: the loader prefixes the body with the skill's base
  directory. A path a shell command runs starts from the `CLAUDE_SKILL_DIR` substitution,
  because commands run in the session's working directory.
- The body loads once and isn't re-read. After compaction only its first 5,000 tokens come back,
  so put what must hold first. A rule that must hold every time belongs in a hook.

## Load-time preprocessing

The body is rewritten when it loads. Argument placeholders (`\$ARGUMENTS`, `\$0`, declared
names) are substituted everywhere, inside inline code and code fences included; a backslash
before the dollar sign escapes one. An exclamation mark followed by a backticked command runs
that command before Claude sees the body, inside a code fence too, and a failing command aborts
the whole invocation. A skill that shows this syntax by example rewrites or runs itself: put
live examples in a supporting file, which Claude reads unprocessed.

## Preload, fork, or neither

- Preload (an agent's `skills:`) only what the agent needs on every dispatch. The full body is
  injected at startup into every agent that lists it, and costs context on every turn.
- Fork (`context: fork`) when the skill is itself an isolated task whose intermediate reads the
  parent doesn't need.
- Otherwise leave the skill model-invocable in the parent.
- Supporting files are never preloaded; the agent reads them on demand, so link each from the
  body.
- A preloaded skill that must not fire standalone needs a description that points standalone
  prompts at the sibling that should win.
- An agent's `tools` list is fixed. An agent that needs Write in one mode refuses it from its
  body in the other.

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

Memory and configuration:
- Only the first 200 lines or 25 KB of `MEMORY.md` load; topic files are read on demand, so a
  memory with no index line is invisible.
- The auto-memory directory is derived from the git repository and shared by its worktrees. Find
  it by listing `~/.claude/projects/*/`, not by computing the name.
- MCP servers live in `~/.claude.json` (local and user scope), `.mcp.json` (project scope) or
  `--mcp-config`, not in `settings.json`.

## Where a lesson lives

At the end of a session or workstream, or when asked to remember something, decide whether
anything is worth keeping and the one place a future session loads it at the moment of need.
Writing nothing is a normal result.

Keep only what cost something to learn, citing the costly turn: a user correction or stated
standing rule; an approach that failed and was changed; a lookup of three or more calls or one
that left the repo; a discovered secret, an only copy, or a home the code or the user
contradicts. The task's own deliverable is never a lesson.

Drop it, without asking, when the place the next reader would look already says it (and this
session didn't miss it with that text in view), when it is general knowledge with no
repo-specific anchor and no observed miss, or when a miss costs no more than the one lookup that
fixes it. Always keep a repeated correction. Keep an irreversible-harm lesson unless an error
naming the fix already blocks the act.

Tag each lesson: durable, point-in-time or stale; scope (file, subtree, repo, user, machine);
trigger (always, on touching files, a named task, rare lookup); claim or procedure; "what" (the
code shows it) or "why/never"; audience (Claude, human, both); ordinary or irreversible.

A home must load in a session with no plugins or extra tools. Take the cheapest that loads at
the trigger:

1. Cut: it already lives somewhere; cite where.
2. Edit an existing home.
3. A one-to-two-line why/never comment at the single anchor. "What" is cut.
4. A path-scoped rule (`.claude/rules/<topic>.md` with `paths:`) for a glob or a file that
   can't hold a comment.
5. Propose a repo skill for a procedure Claude runs.
6. `docs/` for procedures humans run and rare reference; point-in-time records in a dated doc.
7. A root CLAUDE.md line only when needed every session and a miss costs more than the line
   does every session: irreversible, or repeatedly corrected.
8. User-level files only as a proposal to the user.
9. A todo for open items, secrets (location and kind, never the value) and only copies.

- One home per lesson, except that an irreversible never-do also gets a comment where the act
  happens. A critical value lives once, at the earliest-loading layer; other places point to it.
- Point-in-time lessons never enter living homes. A stale lesson is cut, and every living home
  repeating it fixed.
- Dedupe before writing: search the anchor's neighbourhood, CLAUDE.md files and their imports,
  rules, skills, agents, docs, user files, and auto memory. A hit counts only if the lesson's
  audience can see it; untracked and user files reach only the user. If a loaded home already
  said it and the session missed it anyway, raise its prominence or widen its trigger; never cut
  it as a restatement. Same text with a qualifier: cut the new one. Missing qualifier: add it.
  Contradiction: verify against the code and fix every copy.
- After every edit or cut, grep for the old claim and any removed path and fix every hit, except
  in point-in-time records.
- Leave to the user: new skills, docs or sections; files others wrote; anything narrowing a
  global rule; unresolved contradictions; targets outside the repo or ignored by git.

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
Cite docs pages by their `.md` URL and read them with `curl -sL <url>.md`, not WebFetch, which
summarizes.
