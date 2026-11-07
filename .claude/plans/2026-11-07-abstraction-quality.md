# Plan: holding the abstraction bar in agent-written production code

Date: 2026-11-07. Seeded by `.claude/brainstorms/2026-11-07-abstraction-quality.md` (decisions
D1–D7, metrics table). Six commits on branch `abstraction-quality` from `main` (fe54165).

## Context

- `install.sh` links each `skills/*` directory into `~/.claude/skills`; a new skill needs no
  installer change. `bash test/install.test.sh` covers it.
- `claude plugin validate skills` (CLI 2.1.319 on this machine) passes at fe54165. It does not
  reject `: ` inside a description, so the frontmatter check in "Verification" stays.
- Patterns followed: commit bodies `Metric: … Baseline (…): …` then `Gate: …` (55092e0,
  1f460af); new-skill subjects `feat(skills): add <name>` (b6d75f0); dated `Sources` sections
  linking `.md` docs (`workflow-design`, `extension-authoring`).
- New descriptions were checked against all 15 skills in `skills/` and each other: at most two
  shared content words with any of them (`refactoring` 0–1, `tdd` 0–1, `plan-readiness` 2,
  `error-modeling` 2, `commit-sequencing` 1, `doc-drift` 2, `workflow-design` 2, `estimation` 2).

## Planner decisions

- Order re-cut from the brainstorm so each commit names only skills that exist at that commit:
  D2 points into the interview (D4); D6's judge uses `design-rubric` and feeds the interview.
- D5 and D3 are separate commits, and D4 splits into the interview and the default shape: one
  behaviour and one metric row each.
- README gets no line: it lists no skills, and `install.sh` links every skill directory.
- The noticed-ledger rule lives in `design-rubric`, which implementers load before every commit;
  the planning check lives in `plan-readiness`.
- D6's in-the-small line lives in `workflow-design` "Executing a plan", which lists what an
  implementer prompt carries.
- The interface-number gate allows what the plan's task states; otherwise every new public
  function fails it.
- Disagreements outrank the other two interface numbers, from D4's "one evaluation outranks
  narrow interfaces".
- The implementer's first commit in an area writes the `permissions.ask` rules after transcribing
  the frozen files; the main session writes only seeding artifacts.
- CLAUDE.md "Phases" names the interface draft among the artifacts the main session writes.
- `interface-design` carries the report's invariants file and generated agreement test in
  `example.md`, linked from the body.
- A ledger "area" is the set of directories the plan touches.

## Rules for the implementer

- Create branch `abstraction-quality` from `main`. Never push.
- Commands use literal absolute paths; no `cd` or `NAME=value` prefix (CLAUDE.md "Bash commands").
- Stage explicit paths only. Commit 1 also stages
  `.claude/brainstorms/2026-11-07-abstraction-quality.md` and this plan. `.claude/work/` is never
  staged.
- No `Co-Authored-By`, `Claude-Session` or other attribution trailer in any commit message.
- Every edit is by anchor: the old text below occurs verbatim exactly once in the file; the new
  text replaces it. Repo root is `/Users/forrestakin/github.com/forrest-akin/claude-config`.
- Before each commit, load `doc-drift` and run the commit's acceptance checks and both gates
  (`bash test/install.test.sh`, `claude plugin validate skills`).
- Stop and end the installment with a `Blocked:` report (condition, question, options with your
  pick first, proposed diff, commits made) when: an anchor is not found verbatim exactly once; two
  rules in this plan conflict and nothing here settles it; an acceptance check would have to be
  weakened, narrowed, skipped or worked around.
- Commit with the subject and body given. Add a `Deviations:` line only when the commit departs
  from this plan.

## Commit 1 — D1, D7 "Phases"

Subject: `docs: implementers stop on three conditions and the main session relays Blocked questions`

Files: `skills/workflow-design/SKILL.md`, `CLAUDE.md`, plus the brainstorm and this plan.

### `skills/workflow-design/SKILL.md`, "Executing a plan"

Old:

~~~text
- An implementer that meets an open trade-off stops and returns the options, its pick first.
- Every task reports done, failed, or blocked with what it is waiting on, in a form a script can
  parse. A task that reports nothing probably exhausted its context: split it before retrying.
~~~

New:

~~~text
- Every implementer prompt and handoff names three stop conditions: an existing public function
  would change its answers; two written rules conflict and no precedence settles it; an invariant
  test would have to be weakened, narrowed, skipped or worked around. In system-level work, a
  change on the breaking list in `commit-sequencing` ("What forces expand/contract") is the first.
- An implementer that meets a stop condition or an open trade-off ends its installment. Its report
  opens with a `Blocked:` block: the condition, the question, the options with its pick first, the
  proposed diff, and the commits it made before stopping. It commits green work only, nothing for
  the blocked step.
- The main session puts a `Blocked:` question to the human with `AskUserQuestion` and resumes the
  same agent with `SendMessage`. Inside a Workflow a blocked task is terminal; the orchestrator
  re-dispatches it after the answer.
- Every task reports done, failed, or blocked with its `Blocked:` block, in a form a script can
  parse. A task that reports nothing probably exhausted its context: split it before retrying.
~~~

### `CLAUDE.md`, "Phases"

Old:

~~~text
Scout with about five tool calls, then launch on a good-enough design and adjust between runs.
If a design question is still open, launch the smaller first run.
~~~

New:

~~~text
Scout with about five tool calls, then launch on a good-enough design and adjust between runs.
If a design question is still open, launch the smaller first run.

An implementer that stops on a design question returns it as `Blocked:`. The main session puts
it to me with `AskUserQuestion` and resumes that agent with `SendMessage`; it never answers a
design question itself.
~~~

### Acceptance

- `grep -c -F 'weakened, narrowed, skipped or worked around' skills/workflow-design/SKILL.md` → 1
- `grep -c -F 'opens with a `Blocked:` block' skills/workflow-design/SKILL.md` → 1
- `grep -c -F 're-dispatches it after the answer' skills/workflow-design/SKILL.md` → 1
- `grep -c -F 'open trade-off stops and returns' skills/workflow-design/SKILL.md` → 0
- `grep -c -F 'with what it is waiting on' skills/workflow-design/SKILL.md` → 0
- `grep -c -F 'returns it as `Blocked:`' CLAUDE.md` → 1
- `git show --name-only --format= HEAD` lists exactly the four files above.

### Body

~~~text
Metric: Blocked reports relayed to the human per collision an implementer meets. Baseline
(Forrest's 478 sessions, June-November 2026): implementing subagents asked 0 questions; every
ask came from the main session.

Gate: bash test/install.test.sh and claude plugin validate skills, all passed.
~~~

## Commit 2 — D5, D7 "How to implement software"

Subject: `feat(skills): add design-rubric`

Files: `skills/design-rubric/SKILL.md` (new), `CLAUDE.md`, `skills/workflow-design/SKILL.md`.

### `skills/design-rubric/SKILL.md` (whole file)

~~~markdown
---
name: design-rubric
description: Judges the structure of a diff against design principles and maintainability factors, each with a tell, a question and a cure, and blocks a commit that lowers a touched file's health or worsens its public interface. Use before each commit of production work and in design review of a diff. Not for carrying out the cure (refactoring).
---

# Design rubric

## Gate

Run before each commit of production code over the files it touches, and in every design review.

- No touched file gains or worsens a smell from "Health factors".
- The three interface numbers never worsen past what the plan's task states: public names,
  parameters per public function, and disagreements between entry points (inputs on which two
  public functions give different answers). Disagreements outrank the other two: an entry point
  that needs more inputs gets one typed input rather than disagree.
- Files that keep changing together across commits mark a leaky boundary: report the pair.
- An accepted smell carries a comment directly above it naming the smell, the rationale and the
  date. Where the repo runs CodeScene, use its directive:
  `// @codescene(disable:"Complex Method") <rationale>, <YYYY-MM-DD>`.
- A smell the commit introduced is cured before the commit lands. Each cure is a named move from
  `refactoring`.

## Principles

Each with its tell, the question to ask, and the curing move.

- **Stubs over mocks.** Tell: a test verifies which calls a collaborator received. Question: would
  the test still pass if the code reached the same result another way? Move: replace the mock
  with a stub or in-memory fake and assert on the result.
- **Composition over inheritance.** Tell: a subclass overrides to change behaviour, or a base
  class exists to share helpers. Question: does the child use the parent, or is it one? Move:
  Replace Subclass with Delegate; Replace Superclass with Delegate.
- **Single-method interfaces.** Tell: an interface whose implementers each write several methods.
  Question: which one method do implementers need, and which are conveniences for callers? Move:
  Extract Interface down to that method; rebuild the conveniences as functions over it.
- **No nulls.** Tell: a nullable field, parameter or return. Question: what does absence mean,
  and must every caller handle it? Move: Introduce Special Case, or two constructors.
- **No void or empty returns.** Tell: a function returns nothing or an empty value and acts
  through a side effect. Question: what did the call decide or produce? Move: return it as a
  value; Separate Query from Modifier.
- **Pure functions.** Tell: a computation reads a clock, the environment, module state or I/O.
  Question: can a test call it with arguments alone? Move: Parameterize Function with the value
  and resolve it in the caller.
- **Functional core, imperative shell.** Tell: decisions and effects interleave in one function.
  Question: which lines decide and which act? Move: Split Phase; the core returns a decision as a
  value and the shell executes it.
- **Hexagonal architecture.** Tell: domain code imports a framework, driver or wire type.
  Question: would the domain compile with the adapter deleted? Move: Extract Interface into a
  port the domain owns; Move Function to put the adapter outside it.
- **Parse, don't validate.** Tell: a check returns a boolean and the unchecked value travels on.
  Question: after the check, does the type say it passed? Move: Replace Primitive with Object
  whose constructor parses or fails.
- **Make invalid state unrepresentable.** Tell: an assertion or comment guards a combination of
  fields, or one nullable field stands for two conditions. Question: which states can the type
  hold that the domain forbids? Move: Replace Type Code with Subclasses or a sum type; two
  conditions that must not be confused get two constructors.
- **One responsibility per level of abstraction.** Tell: a function mixes a policy step with
  mechanism detail, or computes an expression inside an argument list. Question: does every line
  read at one level, with detail one seam down? Move: Extract Function, naming the lower level;
  in an argument list, call a function not yet written instead of writing its code there.
- **Effects at the edges.** Tell: I/O, the clock or logging called deep in the call tree.
  Question: how many modules perform effects? Move: Move Function outward and pass results in,
  until effects sit in as few modules as possible.
- **Cross-cutting concerns as decorators.** Tell: metrics, logging or deprecation headers inside a
  service's implementation. Question: does the implementation know it is measured? Move: a
  decorator that implements the service's interface, wrapped once at the construction site. It
  sees only request and result: collapse a distinction rather than add a lookup to preserve it.
- **Rule of three.** Tell: an abstraction with fewer than three uses, or a reusable helper with
  one caller. Question: which three uses does it serve today? Move: Inline Function or Inline
  Class until the third use exists.

## Health factors

CodeScene's Code Health factors
([code-health](https://codescene.io/docs/guides/technical/code-health.html)), each with its tell
and move.

- **Large method**: many lines in one function. Extract Function.
- **Brain method**: a large, complex function at the centre of its module's behaviour. Extract
  Function per responsibility; Split Phase.
- **Cyclomatic complexity**: many conditional statements (`if`, `for`, `while`) in one function.
  Decompose Conditional; Replace Conditional with Polymorphism.
- **Nested complexity**: an `if` inside another `if` or a loop. Replace Nested Conditional with
  Guard Clauses.
- **Bumpy road**: several separate chunks of nested logic in one function. Extract Function per
  chunk.
- **Complex conditional**: a branch condition joining several `&&` or `||` operators. Decompose
  Conditional into named predicates.
- **Excess arguments**: a function that wants a fourth argument. Introduce Parameter Object.
- **Primitive obsession**: domain values passed as bare strings, integers or floats. Replace
  Primitive with Object.
- **Duplication**: copied logic that changes together. Extract Function at the third copy.
- **Low cohesion**: LCOM4 above 1, a class whose methods form groups that share no fields.
  Extract Class per group.
- **Brain class**: a large module with many functions and at least one brain method. Extract
  Class.
- **Large assertion block**: a long run of consecutive asserts in one test. Extract a named
  assertion function.
- **Duplicated assertion block**: the same asserts copied across tests. Extract a named assertion
  function, or parameterize the test.
~~~

### `CLAUDE.md`, "How to implement software"

This removes rules from an always-loaded file; the acceptance list proves each lands in the rubric.

Old:

~~~text
**Design rules:**
- One responsibility per level of abstraction, and each level keeps its work at its own level.
  Someone wanting more detail drills down through a seam. This is what keeps functions small.
- Pure functions over effects. Run effects at the **edges**, confined to as few modules as
  possible.
- Composition over inheritance.
- A cross-cutting concern (metrics, logging, deprecation headers) goes in a decorator that implements
  the service's interface, wrapped once at the construction site, not in the implementation.
  It sees only request and result: collapse a distinction rather than add a lookup to preserve it.
- **Parse, don't validate.** Design data so illegal states cannot be constructed, rather than
  checking for them later. Two conditions that must not be confused should be two constructors,
  not one nullable field.
- Don't build an abstraction before you can prove you need it. Rule of 3. Avoid code in
  parameter lists — use names of things you have not created yet.
~~~

New:

~~~text
**Design rules** are checks in the `design-rubric` skill, each a tell, a question and a curing
move. Load it before each commit and when reviewing a design.
~~~

### `skills/workflow-design/SKILL.md`

"Verify tiers".

Old:

~~~text
- Refute correctness claims. Settle design claims (readability, altitude) by independent
  majority vote: a refuter rejects a true design claim by construction.
~~~

New:

~~~text
- Refute correctness claims. Settle design claims (readability, altitude) by independent
  majority vote: a refuter rejects a true design claim by construction. Design reviewers judge
  by `design-rubric`.
~~~

"Executing a plan".

Old:

~~~text
- An implementer prompt tells it to load `doc-drift` before every commit, `error-modeling` when
  the commit adds a failure path, and `commit-sequencing` when it moves code.
~~~

New:

~~~text
- An implementer prompt tells it to load `doc-drift` and `design-rubric` before every commit,
  `error-modeling` when the commit adds a failure path, and `commit-sequencing` when it moves
  code.
~~~

### Acceptance

- `grep '^## ' skills/design-rubric/SKILL.md` prints `## Gate`, `## Principles`,
  `## Health factors`, in that order.
- `grep -c '^- \*\*' skills/design-rubric/SKILL.md` → 27 (14 principles, 13 factors).
- Each of these is found by `grep -F` in `skills/design-rubric/SKILL.md`: `construction site`,
  `two constructors`, `**Rule of three.**`, `a function not yet written`,
  `as few modules as possible`, `one seam down`, `**Composition over inheritance.**`,
  `**Parse, don't validate.**`, `**Pure functions.**`.
- `grep -c -F '**Design rules:**' CLAUDE.md` → 0
- `grep -c -F 'checks in the `design-rubric` skill' CLAUDE.md` → 1
- `grep -c -F '`doc-drift` and `design-rubric` before every commit' skills/workflow-design/SKILL.md` → 1
- `grep -c -F 'Design reviewers judge' skills/workflow-design/SKILL.md` → 1

### Body

~~~text
Metric: per repo, public names, parameters per public function and disagreements between entry
points. Baseline (report "Abstractions at Agent Speed", 5-6 Nov 2026): unguarded, 15 of 15
chains ended with two public functions enforcing different rules; guarded by an agreement test,
written invariants and a precedence order, 3 of 3 stayed whole. The design rules in CLAUDE.md
"How to implement software" become rubric checks; CLAUDE.md keeps a pointer.

Gate: bash test/install.test.sh and claude plugin validate skills, all passed.
~~~

## Commit 3 — D3, D7 "Git staging" (ledger)

Subject: `docs(skills): design-rubric records noticed smells and plan-readiness disposes of them`

Files: `skills/design-rubric/SKILL.md`, `skills/plan-readiness/SKILL.md`, `CLAUDE.md`.

### `skills/design-rubric/SKILL.md`

Append after the last line (`  function, or parameterize the test.`), with one blank line before:

~~~text
## Noticed and left alone

- A smell or broken invariant outside the task's change is left alone and recorded in
  `.claude/noticed.md` in the same commit, one line each:
  `- <path>:<line> — <smell or invariant> — <curing move> — <YYYY-MM-DD>`.
- Create the file with the heading `# Noticed and left alone` when it is missing. Plans dispose
  of its entries (`plan-readiness`).
~~~

### `skills/plan-readiness/SKILL.md`, "Plan checks", end of **Blocking**

Old:

~~~text
- The plan drops a constraint the user stated, reframes their goal, or claims something the
  dialogue didn't establish.
~~~

New:

~~~text
- The plan drops a constraint the user stated, reframes their goal, or claims something the
  dialogue didn't establish.
- An entry in `.claude/noticed.md` for a file the plan touches is neither a tidy-first task nor
  deferred with a reason. Rank those entries by the file's commits in the last year
  (`git log --since=1.year --oneline -- <path> | wc -l`), highest first. The plan deletes an
  entry for a file in the directories it touches that counts zero.
~~~

### `CLAUDE.md`, "Git staging"

Old:

~~~text
2. **Seeding artifacts** — `brainstorms/`, `plans/`, `handoffs/`, `qr/`, `stories/`. These land
   with the commit whose work they seeded. Committing the code without the plan that seeded it
   ships half the change.
~~~

New:

~~~text
2. **Seeding artifacts** — `brainstorms/`, `plans/`, `handoffs/`, `qr/`, `stories/`, `noticed.md`.
   These land with the commit whose work they seeded; a `noticed.md` entry lands with the commit
   whose author noticed it. Committing the code without the plan that seeded it ships half the
   change.
~~~

### Acceptance

- `grep '^## ' skills/design-rubric/SKILL.md` ends with `## Noticed and left alone`.
- `grep -c -F 'git log --since=1.year --oneline -- <path> | wc -l' skills/plan-readiness/SKILL.md` → 1
- `grep -c -F '`stories/`, `noticed.md`' CLAUDE.md` → 1

### Body

~~~text
Metric: share of noticed-ledger entries disposed of at planning, as a tidy-first task or a
deferral with a reason. Baseline (Forrest's 478 sessions, June-November 2026): about 260
"noticed and left alone" bullets; about 1 in 6 sampled was acted on later.

Gate: bash test/install.test.sh and claude plugin validate skills, all passed.
~~~

## Commit 4 — D4 interview, D2, D7 "Design"

Subject: `feat(skills): add interface-design`

Files: `skills/interface-design/SKILL.md` (new), `skills/interface-design/example.md` (new),
`CLAUDE.md`.

### `skills/interface-design/SKILL.md` (whole file)

~~~markdown
---
name: interface-design
description: Interviews the human to settle a public interface before it is built (who calls it, what two entry points could disagree on, which rule wins, what is frozen, and when the builder must stop) and records it as a draft with numbered invariants. Use before a public function, exported surface, protocol or service API is added or altered, or when two entry points may give different answers. Not for failure handling (error-modeling).
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
- One set per public surface: a module's exported interface in the small, a protocol or service
  boundary in the large.
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
implementation awkward, stop and say what you would change and why; everything behind the
interface is yours to structure.

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
~~~

### `skills/interface-design/example.md` (whole file)

The two fenced blocks are verbatim from the report's embedded files (`k-constitution` minus its
"Working in old code" section, and `k-test-gen`).

~~~~markdown
# Interface design example

An access-control module from the report "Abstractions at Agent Speed" (5–6 November 2026), with
two public functions, `can()` and `api.handle_check()`, that other services call. The report's
final arm ran with these sections plus rules for old code; 3 of 3 chains finished with both
functions enforcing all five rules.

## Invariants, precedence and stop conditions

```markdown
## Design invariants for access control

1. **One evaluation.** Every question about access (may they? why? what may they do?) is answered by the same evaluation. No rule is written down twice.
2. **Decisions are values.** Evaluation returns a decision that carries its reason. Booleans are derived from a decision at the edge, never the reverse.
3. **Inputs are explicit.** Evaluation depends only on its arguments. It reads no clock, settings, or module state. Defaults such as the current time are resolved in `api.py` and passed in.
4. **The boundary translates.** `api.py` turns request dicts into domain types and decisions back into dicts. Domain code never handles request dicts.
5. **Narrow interfaces.** No boolean or mode parameters on functions that new code calls. When a function wants a fourth argument, the arguments want to become a type.

## When agreements collide

- Invariant 1 outranks invariant 5. If keeping every public entry point on the one evaluation means an entry point needs more inputs, give those inputs a type; do not leave the entry point behind.
- `tests/test_doors_agree.py` and `tests/scenarios.py` hold invariant 1. Every new request field and every new rule gets examples in `REQUESTS`. Do not keep examples out of that list, and do not narrow that test.

## Stop and ask

Do not settle these yourself. Leave the work in a state that passes the tests, and put the question at the top of your summary:

- an existing public function would end up giving a different answer from another public function for the same user, resource and action;
- two agreements conflict and the order above does not settle it;
- an invariant test would have to be weakened, skipped or worked around.
```

## Agreement test with generated cases

```python
# tests/test_doors_agree_generated.py
"""Invariant: one answer to "may this user do this?", whichever public function is asked.

The cases are generated, not listed, so nobody chooses which ones count.
"""
import itertools

import pytest

from workspace.access import can
from workspace.api import handle_check

NOW = 1_800_000_000
ROLES = ["admin", "editor", "viewer", "guest"]
ACTIONS = ["read", "write", "delete", "share"]
GRANT = {"user_id": "u1", "resource_id": "r1", "actions": ACTIONS, "expires_at": NOW + 60}

# Once you have decided what each old flag should mean for the new rules,
# add the flags to this product as well. Nothing here covers them yet.


def requests():
    for role, suspended, owner, locked, blocked, grants, action in itertools.product(
        ROLES, [False, True], [None, "u1", "u2"], [False, True], [[], ["u1"]], [[], [GRANT]], ACTIONS
    ):
        yield {
            "user": {"id": "u1", "role": role, "suspended": suspended},
            "resource": {"id": "r1", "owner_id": owner, "locked": locked, "blocked_user_ids": blocked},
            "action": action,
            "grants": grants,
            "now": NOW,
        }


@pytest.mark.parametrize("request_", requests())
def test_every_door_gives_the_same_answer(request_):
    answer = handle_check(request_)["allowed"]
    asked_directly = can(
        request_["user"], request_["action"], request_["resource"],
        grants=request_["grants"], now=request_["now"],
    )
    assert asked_directly is answer
```
~~~~

### `CLAUDE.md`, "Design"

Old:

~~~text
A decision with no single correct answer (compatibility, latency vs throughput, memory bounds, drop vs crash on overload) is mine: put it to me as options with their trade-offs, recommendation first. When the code, a stated requirement or a convention picks one option, decide and say why.
~~~

New:

~~~text
A decision with no single correct answer (compatibility, latency vs throughput, memory bounds, drop vs crash on overload) is mine: put it to me as options with their trade-offs, recommendation first. In an interface interview (`interface-design`), bring each question with its evidence and options, and recommend only when I ask. When the code, a stated requirement or a convention picks one option, decide and say why.
~~~

### `CLAUDE.md`, "Phases"

Old: `plan, or handoff under `.claude/`.` (one occurrence, line 28 at fe54165)

New: `interface draft, plan, or handoff under `.claude/`.`

### `CLAUDE.md`, "Git staging"

Old (the text commit 3 wrote):

~~~text
2. **Seeding artifacts** — `brainstorms/`, `plans/`, `handoffs/`, `qr/`, `stories/`, `noticed.md`.
   These land with the commit whose work they seeded; a `noticed.md` entry lands with the commit
   whose author noticed it. Committing the code without the plan that seeded it ships half the
   change.
~~~

New:

~~~text
2. **Seeding artifacts** — `brainstorms/`, `plans/`, `handoffs/`, `interfaces/`, `qr/`,
   `stories/`, `noticed.md`. These land with the commit whose work they seeded; a `noticed.md`
   entry lands with the commit whose author noticed it. Committing the code without the plan
   that seeded it ships half the change.
~~~

### Acceptance

- `grep '^## ' skills/interface-design/SKILL.md` prints `## The interview`, `## Questions`,
  `## Invariants`, `## The draft`, `## Protected paths`, `## Sources`, in that order.
- In `skills/interface-design/example.md`, `grep -c -F` gives 1 for each of
  `## Design invariants for access control`, `## When agreements collide`, `## Stop and ask`,
  `test_doors_agree_generated`, and 0 for `## Working in old code`.
- `grep -c -F 'recommend only when I ask' CLAUDE.md` → 1
- `grep -c -F 'interface draft, plan, or handoff under' CLAUDE.md` → 1
- `grep -c -F '`handoffs/`, `interfaces/`, `qr/`' CLAUDE.md` → 1

### Body

~~~text
Metric: tidy-first commits preceding the extension of a function that breaks an invariant.
Baseline (Forrest's 478 sessions, June-November 2026): about 15 tidy-then-feature pairs prompted
by a plan, rule or CI gate against about 1 unprompted in 5 months. Protected paths land here
because the interview names the frozen paths they guard.

Gate: bash test/install.test.sh and claude plugin validate skills, all passed.
~~~

## Commit 5 — D4 default shape

Subject: `docs(skills): interface-design defaults to single-method interfaces`

Files: `skills/interface-design/SKILL.md`, `skills/design-rubric/SKILL.md`.

### `skills/interface-design/SKILL.md`

Insert before the line `## The draft`, followed by one blank line:

~~~text
## Default shape

New interfaces are single-method by default.

- Types are nominal (`trait`, `fun interface`, a branded TypeScript type); a bare function type is
  never a capability.
- The implementer-facing interface has one method. Caller convenience lives in derived
  combinators built on it, as Iterator and Enumerable do.
- Operations with an invariant across them (begin/commit/rollback, put/get) are bundled as the
  dependencies of another single-method interface's implementation: a capability. The invariant
  lives and is tested there. The bundled primitives are not exported beyond the capability's
  module, and capabilities sit near the application's edge.
- Inputs and outputs are per-operation sum types (`GetUserRequest`, `GetUserResponse`), never one
  sum shared by operations whose invariants differ. Implementations switch exhaustively.
- Variants that share no downstream path are separate interfaces, not one method over a sum,
  which is a mode flag in disguise.
- Sums are closed inside a process and versioned or open at a system boundary
  (`commit-sequencing` "What forces expand/contract", Warn: new enum values).
- The composition root carries coherence and has its own tests. An area's interfaces are grouped
  in one module named by a verb phrase.
- Rust and TypeScript express all of this; Java needs version 21 for exhaustive sealed switches.
~~~

### `skills/design-rubric/SKILL.md`, "Principles"

Old:

~~~text
  Extract Interface down to that method; rebuild the conveniences as functions over it.
~~~

New:

~~~text
  Extract Interface down to that method; rebuild the conveniences as functions over it. Full
  rules: `interface-design` "Default shape".
~~~

### Acceptance

- `grep '^## ' skills/interface-design/SKILL.md` prints `## The interview`, `## Questions`,
  `## Invariants`, `## Default shape`, `## The draft`, `## Protected paths`, `## Sources`.
- `grep -c -F 'a mode flag in disguise' skills/interface-design/SKILL.md` → 1
- `grep -c -F 'rules: `interface-design` "Default shape".' skills/design-rubric/SKILL.md` → 1

### Body

~~~text
Metric: per repo, public names, parameters per public function and disagreements between entry
points. Baseline (report "Abstractions at Agent Speed", 5-6 Nov 2026): the function being edited
set the pattern, and in 13 of 24 messy-module chains a new endpoint grew a mode flag copied from
the function beside it. Unguarded, 15 of 15 chains ended split; guarded, 3 of 3 stayed whole.

Gate: bash test/install.test.sh and claude plugin validate skills, all passed.
~~~

## Commit 6 — D6

Subject: `docs(skills): plan-readiness runs comparative spikes when only running code can decide`

Files: `skills/plan-readiness/SKILL.md`, `skills/workflow-design/SKILL.md`.

### `skills/plan-readiness/SKILL.md`

Old:

~~~text
- A rewrite of an existing system starts with a probe inventory of that system's defects and
  untrue docs, and the plan cites it.

## Artifact checks
~~~

New:

~~~text
- A rewrite of an existing system starts with a probe inventory of that system's defects and
  untrue docs, and the plan cites it.

## Comparative spike

- A spike builds each approach when plausible approaches differ in something only running code
  reveals: caller awkwardness, dependency behaviour, performance, boundary leaks. A known
  trade-off with no empirical question is a decision record instead.
- One thin vertical slice and one shared acceptance test, written before any arm starts. One
  agent per approach, each in its own worktree, with prompts identical except for the approach;
  arms never share a context. The human names the arms, or Claude asks which candidates to build.
- Arms are built red-green so their testability can be measured. The winning arm may be kept.
- The judge table has a column for each of: `design-rubric` findings; the three interface
  numbers; diff size for the slice; setup lines per behaviour; fakes and stubs, and whether any
  is a mock; whether core tests run with no I/O, clock or environment; whether the acceptance
  test could be written against the signatures before any body; tests changed when the slice
  gains one behaviour; suite time against the 5–10 s bar.
- No single column decides. The table goes to the human as evidence in the `interface-design`
  interview.

## Artifact checks
~~~

### `skills/workflow-design/SKILL.md`, "Executing a plan"

Old (the text commit 2 wrote):

~~~text
- An implementer prompt tells it to load `doc-drift` and `design-rubric` before every commit,
  `error-modeling` when the commit adds a failure path, and `commit-sequencing` when it moves
  code.
~~~

New:

~~~text
- An implementer prompt tells it to load `doc-drift` and `design-rubric` before every commit,
  `error-modeling` when the commit adds a failure path, and `commit-sequencing` when it moves
  code.
- An implementer prompt also says: when two shapes fit the next test, drive both to green and keep
  the one whose test was easier to write.
~~~

### Acceptance

- `grep '^## ' skills/plan-readiness/SKILL.md` prints `## Before the plan: which design artifact`,
  `## Comparative spike`, `## Artifact checks`, `## Plan checks`, `## Review discipline`.
- `grep -c -F 'No single column decides' skills/plan-readiness/SKILL.md` → 1
- `grep -c -F 'the one whose test was easier to write' skills/workflow-design/SKILL.md` → 1

### Body

~~~text
Metric: design decisions preceded by a spike with two or more arms. Baseline: none measured.

Gate: bash test/install.test.sh and claude plugin validate skills, all passed.
~~~

## Verification

Run at every commit (paths relative to the repo root; commands use the absolute form):

- `bash test/install.test.sh` ends with `all passed`.
- `claude plugin validate skills` prints `✔ Validation passed`.
- Frontmatter of each new skill parses and its description holds no `: ` (which the validator
  accepts):
  `python3 -c "import re,sys; [print(f, 'ok' if re.match(r'---\nname: [a-z-]+\ndescription: [^\n]+\n---\n', open(f).read()) and ': ' not in re.search(r'^description: (.*)$', open(f).read(), re.M).group(1) else 'FAIL') for f in sys.argv[1:]]" skills/design-rubric/SKILL.md skills/interface-design/SKILL.md`
  prints `ok` per file present.
- Each new description matches this plan's text exactly: `grep -c -F '<description line>'` → 1.
- No load-time substitution in the new skills:
  `grep -n -E '\$(ARGUMENTS|[0-9])|!`' skills/design-rubric/SKILL.md skills/interface-design/SKILL.md`
  finds nothing.
- The commit's acceptance checks above.

After commit 6:

- `git log --format=%B main..abstraction-quality | grep -c -i -E 'co-authored-by|claude-session'` → 0
- `git log --name-only --format='== %s' main..abstraction-quality` lists only each commit's
  files above; `git status --porcelain` shows `.claude/work/` untracked.
- In a clean worktree of the tip (`git worktree add --detach <scratchpad>/tip abstraction-quality`),
  run `bash <scratchpad>/tip/test/install.test.sh` and `claude plugin validate <scratchpad>/tip/skills`,
  then `git worktree remove <scratchpad>/tip`.

## Implementer batching

One implementer on a 1M window, two installments of about 30 calls, the same agent resumed by
`SendMessage` so `CLAUDE.md`, `workflow-design`, `plan-readiness` and `design-rubric` are read once.

- Installment 1: commits 1–3. Inputs: `CLAUDE.md` (all three), `workflow-design` (1, 2),
  `design-rubric` (created in 2, extended in 3), `plan-readiness` (3).
- Installment 2: commits 4–6 and the tip check. Inputs: `interface-design` (created in 4, extended
  in 5), `CLAUDE.md` (4), `design-rubric` (5), `plan-readiness` and `workflow-design` (6).
- Each installment ends with a report: commits (short SHA, subject), checks run with results,
  deviations, untracked `.claude/` files.
- Commits 3, 5 and 6 extend files that commits 2 and 4 create, so they revert only newest first.
