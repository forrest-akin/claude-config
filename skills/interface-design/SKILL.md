---
name: interface-design
description: Interviews the human to settle a public interface before it is built (who calls it, what two entry points could disagree on, which rule wins, what is frozen, and when the builder must stop) and records it as a draft with numbered invariants. Use in the main session before a public function, exported surface, protocol or service API is designed or altered, or when two entry points may give different answers. Not for failure handling (error-modeling).
---

# Interface design

The human designs the interface; Claude interviews and records. This is for production code;
spikes and prototypes supply evidence to the interview.

## The interview

- It runs in the main session, the only context with the human and `AskUserQuestion`.
- Each question comes with its evidence (what the code does now, spike or prototype results, the
  interface numbers from `design-rubric`) and the possible answers with their trade-offs. Claude
  recommends only when the human asks.
- Each answer goes into the draft, attributed to the human.
- The interview has converged when every public signature, every invariant, the precedence order
  and the frozen paths have an attributed answer. An item still open becomes a stop condition.

## Questions

1. Who calls this, with what, and what do two different uses look like?
2. What could two entry points or two implementations disagree on? Each answer is an invariant.
3. What varies behind the surface, and what does the surface fix?
4. What fails, who handles it, and is it a value or an exception (`error-modeling`)?
5. Which rule wins when two collide?
6. What is frozen for the implementer, and what is theirs to structure?
7. What in `.claude/noticed.md` or the current code bears on these answers?

## Invariants

- An invariant is a property two entry points or two implementations could disagree on, checkable
  by one test. The surface sets the count; there is no target.
- An area is one public surface with one set of invariants: a module's exported interface in the
  small, a protocol or service boundary in the large.
- Its test generates the cases rather than listing them, and covers every flag an old signature
  still accepts.
- [example.md](example.md) holds a worked set of invariants with precedence and stop conditions,
  and an agreement test that generates its cases. Read it before writing a repo's first invariant
  test.

## The draft

The main session writes `.claude/interfaces/<area>.md` with these sections, in order:

1. Signatures and types, each with a one-line contract. No bodies.
2. Invariants, numbered.
3. Two throwaway callers written against the signatures for two different uses, noting anything
   awkward to write.
4. Precedence: which rule wins when two collide.
5. Frozen paths.
6. Stop conditions: the three in `workflow-design` "Executing a plan", and each item still open.
7. Standing rules, copied as written here:
   - Old code is not an example.
   - A function that breaks an invariant is brought into line first, as its own
     behaviour-preserving commit with existing tests green, before it is extended.
   - One evaluation outranks narrow interfaces: an entry point that needs more inputs gets a typed
     input rather than being left behind.
   - Tidy-first outranks smallest diff.

The implementer prompt names the draft and says: after your first commit, the interface file,
`docs/invariants/<area>.md` and `tests/invariants/` are frozen; if the interface makes the
implementation awkward, end the installment with a `Blocked:` block naming what you would change
and why; everything behind the interface is yours to structure.

## Protected paths

- An area's interface lives in its own file:

  | Stack | Interface file | Committed surface report |
  | - | - | - |
  | Rust | `lib.rs` / `mod.rs` pub items, or an `-api` crate | `cargo public-api` listing |
  | TypeScript | `src/<area>/index.ts` | API Extractor `etc/*.api.md` |
  | JVM | an `-api` module or `api/` package | Kotlin ABI dump `api/*.api` |
  | System boundary | `proto/**`, `openapi.yaml`, `schemas/**`, migrations | the files themselves |

  Invariant tests live in `tests/invariants/**`, written invariants in `docs/invariants/*.md`.
- The implementer's first commit transcribes the draft into the interface file,
  `docs/invariants/<area>.md` and the invariant tests, commits the surface report, and adds a
  `permissions.ask` rule for each of those paths to the repo's `.claude/settings.json`, for
  example `"ask": ["Edit(/src/access/index.ts)", "Edit(/tests/invariants/**)"]`. Rules take
  gitignore syntax anchored with `/` to their settings source; Edit rules cover Write.
- An ask rule prompts in auto mode and even after a PreToolUse hook allowed the call. A subagent's
  prompt surfaces in the main session naming the subagent; Esc denies that one call.
- A prompt during implementation means the interview missed something: deny it and reopen the
  interview with the human. Never approve the diff.
- Edit rules do not catch a script that opens files itself. They guard cooperating agents; they
  are not a security boundary.

## Sources

Docs read 2026-11-07: [permissions](https://code.claude.com/docs/en/permissions.md) ("Read and
Edit", "Precedence among rules, hooks, and mods"),
[sub-agents](https://code.claude.com/docs/en/sub-agents.md) ("Run subagents in foreground or
background").
