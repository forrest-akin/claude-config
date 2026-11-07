# Brainstorm: holding the abstraction bar in agent-written production code

Date: 2026-11-07. Converged in dialogue between Forrest and the main session. This file seeds the
planning phase; the planner reads it whole, then `plan-readiness`.

## Source

The report "Abstractions at Agent Speed" (claude.ai artifact `LgNFtA91toyKwEnUMBVKzj`, 5–6 Nov
2026). Local copy for grep:
`/Users/forrestakin/.claude/projects/-Users-forrestakin-github-com-forrest-akin-claude-config/815f5999-7b02-47f1-9daf-c16540a20fd1/tool-results/artifact-9f5cbdcc-1794026659-d2b4.html`
(prose in the HTML body; the invariants file, tests, session prompts and option list are inside the
`<script>` blocks as text and as `window.OPTIONS`). Its "one team's 478 sessions" is Forrest's own
corpus, June–November 2026.

### Findings that drive this work

- Agents see abstraction problems and leave them, because the request did not cover them (scope
  deference). Exhortation ("prioritize high-quality abstractions"), a design-first ritual, a rewrite
  from spec, a stronger model and good neighbouring code all left two public functions enforcing
  different rules (0 of 3 chains each). Unguarded: 15 of 15 chains ended split.
- What held: a test asserting the two entry points agree (3 of 3, no instructions); written
  invariants plus a rule that old code is brought into line first (best structure, drifted 1 of 3
  without a test); both together plus a precedence order and three stop conditions (3 of 3, rated
  level with a clean codebase).
- The function being edited sets the pattern; neighbours do not. Its flags, loose typing and modes
  were copied into new code.
- Field corpus (478 sessions): implementing subagents asked 0 questions; every ask came from the
  main session. ~260 "noticed and left alone" bullets, 1 in 6 sampled acted on later. Restructuring
  was authorized by a user message (6), a plan row (7), a rule (1), a failing test alone (0).
  Tidy-then-feature pairs: ~15 prompted by plan, rule or CI gate; ~1 unprompted.
- Public PRs (5,073): instruction files moved test edits and review attention, not widening or
  duplication. Files with five or more never/must rules went with more widening (6.7% vs 2.6%);
  files with interface/boundary language with less (0.7% vs 3.8%).
- Hidden acceptance tests passed in every arm; only interface numbers separated them: public names,
  parameters per public function, disagreements between entry points.

### Mechanisms verified in Claude Code docs on 2026-11-07

- `permissions.ask` takes `Edit(<glob>)` in gitignore syntax; Edit rules cover Write. An ask rule
  prompts in auto mode and even when a PreToolUse hook returned allow
  (`https://code.claude.com/docs/en/permissions.md`, "Read and Edit", "Precedence among rules,
  hooks, and mods").
- Foreground and background subagents surface permission prompts in the main session, naming the
  subagent; Esc denies one call without stopping it (`sub-agents.md`, "Run subagents in foreground
  or background"). Subagents never get `AskUserQuestion`. A launched subagent treats a `SendMessage`
  from its launcher as task direction, so a blocked agent is resumed with context intact.
- Workflow agents get no mid-run user input (already in `workflow-design`).
- `SubagentHandback` delivers a subagent's final report in auto mode (`tools-reference.md`).

## Decisions

The human drives design. Claude interviews, gathers evidence, records answers; it does not propose
a design. Production code only: not spikes, not prototypes, except that prototypes are a tool of
design (D6).

### D1. Stop conditions and a resume path for implementers

- Three stop conditions in every implementer prompt and handoff: an existing public function would
  change its answers; two written rules conflict and no precedence settles it; an invariant test
  would have to be weakened, narrowed, skipped or worked around. For system-level work the breaking
  list in `commit-sequencing` ("What forces expand/contract") is the same condition.
- On a stop the implementer ends its installment with a report whose first block is
  `Blocked:` naming the condition, the question, the options with its pick first, the proposed
  diff, and what it committed before stopping (green work only; nothing for the blocked step).
- The main session relays the question to the human with `AskUserQuestion`, then resumes the same
  agent by `SendMessage`. Inside a Workflow the blocked task is terminal; the orchestrator
  re-dispatches after the answer.
- Homes: `workflow-design` ("An implementer that meets an open trade-off stops..." and the
  done/failed/blocked report line); CLAUDE.md "Phases" (one line: the main session relays a
  `Blocked:` question and resumes the agent; it never answers a design question itself).

### D2. Protected interface paths as a tripwire

- Per repo, `permissions.ask` rules on interface files, invariant tests and committed surface
  reports. A prompt firing during implementation means the interview (D4) missed something; the
  response is deny and reopen the interview, not approve the diff.
- Convention: an area's interface lives in its own file. Table the skill carries (Rust and
  TypeScript first, JVM second; nothing else):

  | Stack | Interface file | Committed surface report |
  | - | - | - |
  | Rust | `lib.rs` / `mod.rs` pub items, or an `-api` crate | `cargo public-api` listing |
  | TypeScript | `src/<area>/index.ts` | API Extractor `etc/*.api.md` |
  | JVM | an `-api` module or `api/` package | Kotlin ABI dump `api/*.api` |
  | System boundary | `proto/**`, `openapi.yaml`, `schemas/**`, migrations | the files themselves |

  Plus `tests/invariants/**` and `docs/invariants/*.md`. Rules anchor with `/path` (settings-source
  relative). Edit rules do not catch a script that opens files itself: a guard for cooperating
  agents, not a boundary.
- Not a hook. The `hooks/` directory is untouched by this work.

### D3. A committed ledger of what the agent noticed, with triage at touch

- `.claude/noticed.md`, tracked, bucket 2 in CLAUDE.md "Git staging". Entry: path and line, the
  smell or invariant, the curing move, date. The implementer appends in its own commit.
- Triage is at touch, never a sweep: `plan-readiness` gets a blocking check that a plan disposes of
  every ledger entry in the files it touches, as a tidy-first task or a deferral with a reason.
- Ranking by where work happens, CodeScene's hotspot rule: file commit count over the last year
  from `git log`, a documented one-line command, no script. An entry whose file has no commits in a
  year is dropped at the next planning pass in that area.

### D4. `interface-design` skill: the interview, invariants, the single-method default

- The interface phase is an interview in the main session (the only context with a human and the
  question tool). Claude brings each question with the evidence for it (what the code does now,
  prototype results, the interface numbers) and the possible answers with trade-offs; it records the
  human's answer. No recommendation unless asked. Converged when every public signature, every
  invariant, the precedence order and the frozen paths have an answer attributed to the human; open
  items become D1 stop conditions.
- Question set: who calls this, with what, and what two different uses look like; what two entry
  points or two implementations could disagree on (each answer is an invariant); what varies behind
  the surface and what the surface fixes; what fails, who handles it, value or exception
  (`error-modeling`); which rule wins on collision; what is frozen for the implementer and what is
  theirs; what Claude noticed in the current code that bears on the answers (D3 feeds this).
- Invariant criterion: a property two entry points or two implementations could disagree on,
  checkable by one test. The count follows from the surface; no target number. "Per area" means
  per public surface: a module's exported interface in the small, a protocol or service boundary in
  the large. Cases are generated, not curated, and cover every flag an old signature still accepts.
- Output: the interface draft at `.claude/interfaces/<area>.md` (bucket 2): signatures with a
  one-line contract each, the numbered invariants, two throwaway callers, precedence, frozen paths,
  stop conditions. The implementer transcribes it into code under D2 rules.
- Standing rules the draft carries, from the report's final CLAUDE.md: old code is not an example;
  a function that breaks an invariant is brought into line first as its own behaviour-preserving
  commit before it is extended ("make the change easy, then make the easy change"); one evaluation
  outranks narrow interfaces, so an entry point that needs more inputs gets a typed input rather
  than being left behind; tidy-first outranks smallest diff.
- Default interface shape: single-method interfaces. Rules and exceptions:
  - Nominal types always (`trait`, `fun interface`, branded TS types); never a bare function type
    as a capability.
  - Implementer-facing interface is one method; caller convenience lives in derived combinators
    built on it (Iterator, Enumerable).
  - Operations with a cross-operation invariant (begin/commit/rollback, put/get) are bundled as
    dependencies of another single-method interface's implementation: a capability. The invariant
    lives and is tested there. The bundled primitives stay unexported beyond the capability's
    module. Capabilities sit near the application's edge.
  - Inputs and outputs are per-operation sum types (`GetUserRequest`, `GetUserResponse`), never a
    sum shared across operations whose invariants differ. Implementations switch exhaustively.
  - Variants that share no downstream path are separate interfaces, not one method over a sum
    (the disguised mode flag).
  - Closed sums inside a process; versioned or open at a system boundary (`commit-sequencing`
    "Warn: new enum values").
  - Composition root carries coherence and gets its own tests; an area's interfaces are grouped in
    one module, named by verb phrase.
  - Stack notes: Rust and TypeScript ideal; Java needs 21 for exhaustive sealed switches.

### D5. `design-rubric` skill: principles as checks, and the gate

- Each principle operationalized as tell, question, curing move (moves from `refactoring`):
  stubs over mocks; composition over inheritance; single-method interfaces (D4); no nulls; no
  void or empty returns; pure functions; functional core, imperative shell; hexagonal
  architecture; parse, don't validate; make invalid state unrepresentable; one responsibility per
  level of abstraction; effects at the edges; cross-cutting concerns as decorators; rule of three.
- Mechanical smells, from CodeScene's Code Health factors
  (`https://codescene.io/docs/guides/technical/code-health.html`): large and brain methods,
  cyclomatic complexity, nested complexity, bumpy road, complex conditionals, excess arguments,
  primitive obsession, duplication, low cohesion (LCOM4), brain class, large and duplicated
  assertion blocks.
- Gate: the health of a touched file never declines in a commit, and the three interface numbers
  (public names, parameters per public function, disagreements between entry points) never worsen.
  Change coupling (files that keep changing together across commits) is reported as a leaky
  boundary. An accepted smell carries a suppression with rationale and date.
- Loaded by implementers before each commit and by reviewers. The design-rules bullets now in
  CLAUDE.md "How to implement software" move here as checks, leaving a pointer line.

### D6. Comparative spikes, test-driven

- Trigger (extends the spike in `plan-readiness`): plausible approaches differ in something only
  running code reveals (caller awkwardness, dependency behaviour, performance, boundary leaks).
  A known trade-off with no empirical question is a decision record instead.
- Shape: one thin vertical slice, one shared acceptance test written before any arm starts, one
  agent per approach in its own worktree, prompts identical except for the approach, arms kept
  apart (CLAUDE.md "Subagents"). The human names the arms, or Claude asks which candidates to
  build. Arms are built red-green so testability is measured; the winner may be kept.
- Judge columns: the rubric (D5); the interface numbers; diff size against the same slice; setup
  lines per behaviour; count of fakes or stubs and whether any is a mock; core tests run with no
  I/O, clock or environment; whether the acceptance test could be written against the signatures
  before any body; tests changed when the slice is extended by one behaviour; suite time under the
  5–10 s bar. Testability is one column, not the verdict. Results return to the interview (D4) as
  evidence.
- In the small, one implementer-prompt line: when two shapes fit the next test, drive both to green
  and keep the one whose test was easier to write.

### D7. CLAUDE.md edits

- "Design": the options-with-recommendation-first line gains a scope: in a design interview (D4),
  options and evidence per question, a recommendation only when asked.
- "Phases": the `Blocked:` relay line (D1).
- "How to implement software": design-rules bullets replaced by a pointer to `design-rubric`.
- "Git staging": `.claude/noticed.md` and `.claude/interfaces/` added to bucket 2.
- `README.md` lists nothing per skill today; the planner decides whether it needs a line.

Dropped: a bespoke-component-with-oracle rule; a deny hook on protected paths.

## Build order

1. D1 and D7's Phases line, D2 in the skill table form, D6 in `plan-readiness` with the
   implementer-prompt line. Small and unblocking.
2. D5 with D3 and its `plan-readiness` check; the CLAUDE.md pointer.
3. D4, including the D7 Design-line scope.

The planner may re-cut with `commit-sequencing`; each commit deploys alone and names the metric
and baseline below in its body.

## Metrics and baselines

| Change | Metric | Baseline |
| - | - | - |
| D1 | Blocked reports relayed to the human per collision met | 0 implementer asks in 478 sessions, Jun–Nov 2026 |
| D3 | Share of ledger entries disposed of at planning | ~1 in 6 noticed items acted on later |
| D4 tidy-first rule | Tidy-first commits preceding extension of a flagged function | ~15 prompted vs ~1 unprompted in 5 months |
| D4, D5 | Public names, parameters per public function, entry-point disagreements per repo | Report: unguarded 15 of 15 chains split; guarded 3 of 3 whole |
| D6 | Design decisions preceded by a spike with two or more arms | none measured |

## Repo facts

- `install.sh` symlinks `CLAUDE.md`, each `skills/*` directory and each `hooks/*.sh` into
  `~/.claude`; `test/install.test.sh` covers it. New skills need no installer change.
- Skills are `skills/<name>/SKILL.md`, frontmatter `name` and `description`; see
  `extension-authoring` for description rules, body limits (first 5,000 tokens survive compaction)
  and collision checks against neighbours (`tdd`, `refactoring`, `plan-readiness`,
  `error-modeling`, `commit-sequencing`, `doc-drift`).
- The working tree is clean apart from this file and `.claude/work/`, which stays untracked. This brainstorm lands with the first commit of the work it
  seeded.
- Deterministic checks only; no evals. Concision and documentation rules in CLAUDE.md apply to
  every skill body: state how things are, never how they changed.
