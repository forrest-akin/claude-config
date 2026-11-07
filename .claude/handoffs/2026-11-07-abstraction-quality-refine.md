# Handoff: fold review findings into the `abstraction-quality` commits

Branch `abstraction-quality`, six commits over `main` (fe54165), unpushed. Each edit below folds
into the commit named, with `git commit --fixup <sha>` and one unattended autosquash rebase at
the end. The plan at `.claude/plans/2026-11-07-abstraction-quality.md` is a point-in-time record
and is not edited.

Commits (oldest first):

| Short | Subject |
| - | - |
| 710bb6b | docs: implementers stop on three conditions and the main session relays Blocked questions |
| 9edaa7e | feat(skills): add design-rubric |
| de6ef96 | docs(skills): design-rubric records noticed smells and plan-readiness disposes of them |
| 1e941da | feat(skills): add interface-design |
| 089fe0a | docs(skills): interface-design defaults to single-method interfaces |
| de02092 | docs(skills): plan-readiness runs comparative spikes when only running code can decide |

## Decisions behind the edits

- Stop condition one is the report's wording, "two public entry points would give different
  answers for the same inputs", not "an existing public function would change its answers". The
  second contradicts the tidy-first rule, whose extension step changes a function's answers on
  purpose. `example.md` already has the report's wording.
- A `Blocked:` block keeps the implementer's pick. The main session relays it labelled as the
  implementer's; it adds no pick of its own.
- The rubric gate keeps its judgment thresholds; no counts or coupling command are added.
- CodeScene factor labels follow the page read 2026-11-07
  (`https://codescene.io/docs/guides/technical/code-health.html`): Large Method, Brain Method,
  Complex Method, Nested Complexity, Bumpy Road, Complex Conditional, Primitive Obsession, DRY
  Violations, Low Cohesion, Brain Class, Large Assertion Blocks, Duplicated Assertion Blocks. The
  page's directive examples use `"Complex Method"` and `"Bumpy Road Ahead"`, the smell names its
  virtual code review shows.

## Edits

Each old text occurs once in the file at the branch tip. Line wraps inside a bullet may differ
from the old text shown; match the words.

### Into 710bb6b

`CLAUDE.md`, "Phases":

Old: `An implementer that stops on a design question returns it as `Blocked:`. The main session puts it to me with `AskUserQuestion` and resumes that agent with `SendMessage`; it never answers a design question itself.`

New: `Every implementer prompt and handoff names the three stop conditions in `workflow-design` "Executing a plan"; an implementer that meets one returns it as `Blocked:`. The main session puts the question to me with `AskUserQuestion`, with the options and the implementer's pick labelled as the implementer's, and resumes that agent with `SendMessage`; it never answers a design question itself.`

`skills/workflow-design/SKILL.md`, "Executing a plan":

Old: `names three stop conditions: an existing public function would change its answers; two written rules conflict`

New: `names three stop conditions: two public entry points would give different answers for the same inputs; two written rules conflict`

Also stage this handoff file into 710bb6b.

### Into 9edaa7e

`skills/design-rubric/SKILL.md`:

- Frontmatter `description`, whole value: `Judges a diff's design against principles and code-health smells, and blocks a commit that lowers a touched file's health or worsens its public interface. Use before each commit of production work and in design review of a diff. Not for carrying out the cure (refactoring).`
- Old: `- A smell the commit introduced is cured before the commit lands. Each cure is a named move from `refactoring`.`
  New: `- Each cure is the move this rubric names, carried out per `refactoring`.`
- Old: `  `// @codescene(disable:"Complex Method") <rationale>, <YYYY-MM-DD>`.`
  New: `  `// @codescene(disable:"Complex Method") <rationale>, <YYYY-MM-DD>`. The directive string is the smell name CodeScene's virtual code review shows, such as `Complex Method` or `Bumpy Road Ahead`.`
- Delete the line `Each with its tell, the question to ask, and the curing move.` and the blank line after it.
- Old: `Question: can a test call it with arguments alone? Move: Parameterize Function with the value and resolve it in the caller.`
  New: `Question: can a test call it with arguments alone? Move: Replace Query with Parameter, resolving the value in the caller.`
- Old: `CodeScene's Code Health factors ([code-health](https://codescene.io/docs/guides/technical/code-health.html)), each with its tell and move.`
  New: `CodeScene's Code Health factors ([code-health](https://codescene.io/docs/guides/technical/code-health.html)). Excess arguments is this rubric's own.`
- Old: `- **Cyclomatic complexity**: many conditional statements`
  New: `- **Complex method**: many conditional statements`
- Old: `- **Duplication**: copied logic that changes together.`
  New: `- **DRY violations**: copied logic that changes together.`

`CLAUDE.md`, "How to implement software":

Old: `**Design rules** are checks in the `design-rubric` skill, each a tell, a question and a curing move. Load it before each commit and when reviewing a design.`

New: `**Design rules** are checks in the `design-rubric` skill. Load it before each commit and when reviewing a design.`

### Into de6ef96

`skills/plan-readiness/SKILL.md`, **Blocking**:

Old: `- An entry in `.claude/noticed.md` for a file the plan touches is neither a tidy-first task nor deferred with a reason. Rank those entries by the file's commits in the last year (`git log --since=1.year --oneline -- <path> | wc -l`), highest first. The plan deletes an entry for a file in the directories it touches that counts zero.`

New: `- An entry in `.claude/noticed.md` for a file the plan touches is neither a tidy-first task nor deferred with a reason, or an entry for a file in the directories the plan touches whose count (`git log --since=1.year --oneline -- <path> | wc -l`) is zero is not deleted. The plan orders its tidy-first tasks by that count, highest first.`

### Into 1e941da

`skills/interface-design/SKILL.md`:

- Frontmatter `description`, whole value: `Interviews the human to settle a public interface before it is built (who calls it, what two entry points could disagree on, which rule wins, what is frozen, and when the builder must stop) and records it as a draft with numbered invariants. Use in the main session before a public function, exported surface, protocol or service API is designed or altered, or when two entry points may give different answers. Not for failure handling (error-modeling).`
- Old: `- One set per public surface: a module's exported interface in the small, a protocol or service boundary in the large.`
  New: `- An area is one public surface with one set of invariants: a module's exported interface in the small, a protocol or service boundary in the large.`
- Old: `if the interface makes the implementation awkward, stop and say what you would change and why;`
  New: `if the interface makes the implementation awkward, end the installment with a `Blocked:` block naming what you would change and why;`

### Into 089fe0a

`skills/design-rubric/SKILL.md`, "Gate":

Old: `disagreements between entry points (inputs on which two public functions give different answers).`

New: `disagreements between entry points (inputs on which two public functions give different answers), counted by the area's agreement test under `tests/invariants/`.`

### Into de02092

`skills/plan-readiness/SKILL.md`, "Comparative spike":

Old: `- A spike builds each approach when plausible approaches differ`

New: `- A step-1 spike builds each approach when plausible approaches differ`

`skills/interface-design/SKILL.md`:

Old: `spikes and prototypes supply evidence to the interview.`

New: `spikes (`plan-readiness` "Comparative spike") and prototypes supply evidence to the interview.`

## Procedure

1. Snapshot `git status --porcelain`; only `.claude/work/` and this handoff should be untracked.
2. For each target commit, oldest first: apply its edits at the branch tip, stage those files
   (and this handoff for 710bb6b), `git commit --fixup <sha>`.
3. `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash --exec 'bash /Users/forrestakin/github.com/forrest-akin/claude-config/test/install.test.sh && claude plugin validate /Users/forrestakin/github.com/forrest-akin/claude-config/skills' main`.
4. At the new tip: `grep -c` → 1 for each new text above; `grep -c` → 0 for `Parameterize Function`, `Cyclomatic complexity`, `each with its tell`, `would change its answers` across `CLAUDE.md` and `skills/`; both new descriptions share at most two content words with any skill description in `skills/*/SKILL.md`; trailer grep over `main..abstraction-quality` → 0; `git log --name-only --format='== %s' main..abstraction-quality` shows the same six subjects with this handoff added to the first.
5. Clean-worktree tip check as the plan's "After commit 6" describes, worktree under the
   scratchpad directory and removed afterwards.

Report: the six new SHAs with subjects, the rebase's exec output summary, each verification
result, and `git status --porcelain`.
