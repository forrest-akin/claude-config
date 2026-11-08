# Platform facts (checked 2026-11-07)

## Interface file per stack

| Stack | Interface file | Committed surface report |
| - | - | - |
| Rust | `lib.rs` / `mod.rs` pub items, or an `-api` crate | `cargo public-api` listing |
| TypeScript | `src/<area>/index.ts` | API Extractor `etc/*.api.md` |
| JVM | an `-api` module or `api/` package | Kotlin ABI dump `api/*.api` |
| System boundary | `proto/**`, `openapi.yaml`, `schemas/**`, migrations | the files themselves |

## Ask rules

- An ask rule prompts in auto mode and even after a PreToolUse hook allowed the call. A subagent's
  prompt surfaces in the main session naming the subagent; Esc denies that one call.
- Edit rules do not catch a script that opens files itself. They guard cooperating agents; they
  are not a security boundary.

## Sources

Docs read 2026-11-07: [permissions](https://code.claude.com/docs/en/permissions.md) ("Read and
Edit", "Precedence among rules, hooks, and mods"),
[sub-agents](https://code.claude.com/docs/en/sub-agents.md) ("Run subagents in foreground or
background").
