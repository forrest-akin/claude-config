# Brainstorm: move each skill's work from prose to deterministic mechanisms

Date: 2026-11-07. Seeds an adversarial review of every skill in `skills/`. Three reviewers, one
batch each; the main session synthesises their reports into redesign proposals.

## Thesis

A skill is software. The LLM's share of it is the part that needs nondeterministic judgment and
nothing else. Everything a tested script, hook, git query, template or checked output format can do
with equal or better fidelity is done that way, so each invocation loads less prose and the model's
context is spent on the judgment that remains. The measure is best result for least tokens.

## Existing patterns in this repo

- `skills/slide-auditor/scripts/audit_slides.py` with `tests/`: the script measures, the model fixes.
- `skills/disk-space-reclamation/bin/*.sh`, `lib/select.sh`, `tests/test-select.sh`: survey, plan
  and apply are scripts; the model reads the plan and decides.
- `hooks/call-budget.sh`, `hooks/bash-prefix.sh` with `test/`: rules that must hold every time run
  as hooks, not as instructions.

## Constraints from CLAUDE.md

- Fewest moving parts that satisfy the stated constraint. A script more complex than the judgment
  it replaces is a loss; say so rather than propose it.
- An extension carries knowledge Claude cannot derive. Prose that restates what the model already
  does is dead weight; delete it.
- Measurement over theory. Evidence is the skill text itself, the scripts and tests already here,
  and transcripts under `~/.claude/projects/`. No evals.
- macOS `/bin/bash` 3.2; prefer python3 or Homebrew bash for anything past trivial.

## Per-skill rubric

Read the whole skill directory, then for every instruction or step in the body:

1. Classify it.
   - **Mechanisable**: a script, hook, test, git query, template or fixed output schema does it.
     Counting, measuring, listing, diffing, locating, enforcing a format, checking a threshold,
     enumerating candidates, and anything the model is asked to "verify" are the usual cases.
   - **Judgment**: needs reasoning over meaning. Say in one line what the model is actually
     deciding.
   - **Dead weight**: the model does this unprompted, or the line restates another line or
     another skill.
2. For each mechanisable item, propose the mechanism: name, inputs, outputs, where it lives
   (`skills/<name>/bin/` or `scripts/`, a hook, a template), how it is tested, and which lines of
   prose it replaces.
3. Attack the skill as written. Where does it rely on the model counting or measuring? Which steps
   can be skipped silently with no trace? Where is the model asked to recall a figure or rule it
   could read? Where does the skill duplicate knowledge held in another skill or in `CLAUDE.md`?
4. State what the model is left doing after the redesign, in a few lines. If that residue is small
   enough that the skill should become a script plus a one-paragraph `SKILL.md`, or should merge
   into another skill, say so.
5. Give the token picture: current body size in characters, rough tokens per load (chars ÷ 4), and
   the projected size after the redesign.
6. Present the redesign as increments from the smallest change that pays, so the sweet spot is a
   choice.

Cite `SKILL.md:<line>` for every claim about the text.

## Batching

| Reviewer | Skills | Why together |
|---|---|---|
| A | tdd, refactoring, commit-sequencing, design-rubric, error-modeling, doc-drift, root-cause-analysis, disk-space-reclamation | Code-process skills whose candidate mechanisms are git, test runners, linters and diff tools. `disk-space-reclamation` is the reference for the target shape. |
| B | workflow-design, subagent-model-tiering, plan-readiness, interface-design, estimation, extension-authoring | Orchestration skills whose candidate mechanisms are hooks, validators of `.claude/` artifacts, templates and frontmatter linters. |
| C | presentation-narrative, slide-svg-figures, slide-auditor | Deck skills whose candidate mechanisms are the existing audit script, SVG geometry checks and layout templates. |

Each reviewer writes `.claude/work/deterministic-skills/<A|B|C>.md` and returns a summary of under
300 words: per skill, the one-line verdict and the top mechanism.

## Output of the phase

The main session merges the three reports into proposals per skill, ordered by tokens saved per
unit of mechanism built, and puts cross-cutting choices to Forrest.

## Synthesis (main session, from `.claude/work/deterministic-skills/{A,B,C}.md`)

Verified by the main session: `~/.claude/settings.json` registers neither hook; the budget regex
in `hooks/call-budget.sh:17` matches only `About N calls` and `Hard budget: N`; the stop conditions
in `workflow-design/SKILL.md:101-103` and `interface-design/example.md:28-30` differ; the ERROR
branch in `audit_slides.py:253-260` is unreachable.

### Findings that cut across skills

- The two mechanisms the repo already has do not run. Every rule "moved into a hook" is prose today.
- Three skills are judgment through and through and gain only a line or a template: error-modeling,
  root-cause-analysis, and the core of presentation-narrative. The thesis does not apply to them.
- The largest token sink is platform facts and CLAUDE.md restatements in the bodies of
  workflow-design, extension-authoring, subagent-model-tiering and interface-design: about 6k chars
  of dated facts loaded on every invocation, read only on a failure.
- Thresholds disagree across files wherever the same number lives twice: slide budgets (five
  sources for a 15-minute talk), the SVG gap rule against its own examples, the element budget
  (three values), canvas limits (audit vs reference), notes word counts (three sources).
- The deck skills have never produced a real deck; their mechanisms have no baseline. The audit
  script's tests cover parsing only, which is how seven defects survived.
- Usage: design-rubric loaded once despite "before every commit"; estimation, root-cause-analysis,
  disk-space-reclamation and interface-design never. tdd 52, workflow-design 92.

### Per-skill proposals

Sizes are body chars today → after. Increments are ordered; stop where the payoff stops.

| Skill | Verdict | Increments | Size |
|---|---|---|---|
| doc-drift | Main loop is enumeration and search done by hand | 1 `bin/stale-refs` (tokens from removed diff lines, gone from code, grepped in docs, with last-edit date). 2 `env-drift` and manifest-version set checks | 1.6k → 1.3k; saving is in calls |
| design-rubric | Metric smells judged by eye with no thresholds; invariants counter exists nowhere | 1 `bin/notice`, drop provenance. 2 `bin/health-delta` over lizard, accepted-smell comment as suppression. 3 `co-change`, `public-surface`. 4 settle the invariants counter. 5 commit hook once false-positive rate is known | 7.1k → 4.3k |
| tdd | Mostly judgment; two checks are mutation testing | 1 drop three duplicate lines. 2 replace hand-mutation with `cargo mutants --in-diff` / Stryker at the pre-commit point | 2.4k → 1.7k |
| refactoring | The 4-files/200-lines stop needs a count the model cannot see | 1 drop the duplicate line; one home for characterization tests. 2 `hooks/diff-size.sh` (PostToolUse, shape of call-budget). 3 diff-coverage command line | 2.5k → 2.2k |
| commit-sequencing | Runs at plan time, so thresholds stay prose; check mode is measurable | 1 cut CLAUDE.md restatements; resolve `:24` against "never re-run tests per commit". 2 `bin/stack-check BASE` (size, placeholder subject). 3 migration flags | 2.8k → 2.5k |
| error-modeling | All judgment | 1 one line naming the exhaustiveness and silent-catch lints | unchanged |
| root-cause-analysis | All judgment; output recalled from prose | 1 fixed output skeleton. 2 name `git bisect run` and N-times rerun | unchanged |
| disk-space-reclamation | Half the body restates what scripts enforce; scripts have defects and untested guards | 1 delete restatements. 2 fix survey `node_modules` prune and apply's failed-rm count; test apply and protect-list. 3 `permissions.ask` on `--confirm` plus dry-run stamp. 4 swap diagnosis line. 5 apply-time protection re-check. 6 `runtime-prune.sh` | 4.2k → 2.1k |
| workflow-design | Counts calls by reading transcripts; 2.3k of platform facts every load | 1 register hooks; widen budget regex with fixtures. 2 facts → `references/platform.md`; drop CLAUDE.md duplicates; move escalation lines to tiering. 3 templates (agent preamble, implementer block, Blocked, installment report) plus a stop-condition identity test. 4 `bin/wf-status` for a Monitor until-loop. 5 `wf-estimate` only if summaries keep missing figures | 11.3k → 6.5k |
| subagent-model-tiering | Half platform facts; "check /tasks" has no tool | 1 facts → reference; drop two dead lines. 2 take in workflow-design `:46-48`. 3 `bin/agent-models` comparing requested vs ran | 4.6k → 2.7k |
| plan-readiness | Fidelity, not size: hand-run git counts and silently skipped checks | 1 check-by-check output table. 2 `bin/noticed-scan` (shared with interface-design). 3 artifact homes and templates for spike, decision record, spec. 4 `plan-lint` lister, never a gate. 5 `spike-measure` after the first manual comparative spike | 6.0k → 4.7k |
| interface-design | "Copied as written" and convergence counting are template and validator | 1 drop CLAUDE.md duplicates; fix example drift. 2 `templates/interface-draft.md`. 3 `bin/interface-check`. 4 `bin/protect-paths` and a dated reference | 6.8k → 4.0k |
| estimation | Never triggered; three lines of non-derivable knowledge | 1 drop the Design duplicate; output table. 2 fold into CLAUDE.md "Design" and delete | 1.7k → 1.1k or 0.25k in CLAUDE.md |
| extension-authoring | "Silent failures" is 2.5k of recall-and-check-by-eye | 1 drop doc-drift and web-source duplicates; facts → references. 2 `bin/lint-extension` core plus repo gate test. 3 agent/hook/memory checks, neighbour report, hook-registration check. 4 `bin/lesson-homes`. 5 optional PostToolUse lint on write | 10.5k → 6.0k |
| slide-svg-figures | 70% of body is arithmetic the model self-grades | 1 delete boilerplate and wrapper; settle the gap rule. 2 `deck_constants.json` read by both scripts. 3 `check_svg.py` overlap, gap, margin, text-fits, bounds; drop the layout-plan mandate. 4 crossing, fill-count, contrast | 8.8k (13-18k with refs) → 1.5k |
| slide-auditor | Describes checks the script lacks; blind to overlap | 1 tests then fix the seven defects. 2 body → one paragraph and the command. 3 shared constants with per-layout limits. 4 headmatter fields, fence language, near-palette hint. 5 geometry via `check_svg.py` | 3.4k → 0.7k |
| presentation-narrative | Judgment; the numbers conflict and the references are never read | 1 delete dead weight; one computed slide-budget rule. 2 `check_timing.py` for the timing table. 3 settle the five-act default; trim the reference; constants → data | 5.3k → 2.0k |

### Order of work by payoff per unit built

1. Prose only: dead weight, CLAUDE.md duplicates, platform facts into dated references. About
   15k chars across the set, no code.
2. Make what exists work: register hooks, widen the budget regex, fix `audit_slides.py` and the
   reclamation scripts test-first.
3. Data and templates: `deck_constants.json`, workflow templates with the identity test,
   interface draft, spike/decision/spec templates, RCA skeleton.
4. Scripts with observed need: `stale-refs`, `lint-extension`, `noticed-scan`, `wf-status`,
   `check_timing.py`, `diff-size.sh`, `health-delta`, `stack-check`, `interface-check`.
5. Build on evidence: `check_svg.py` after the first real deck, `plan-lint`, `spike-measure`,
   `wf-estimate`, commit gate hook, `co-change`, `public-surface`.

### Decisions (Forrest, 2026-11-07)

- `install.sh` registers the two hooks in `~/.claude/settings.json` idempotently; the install test covers it.
- Widen the budget regex: case-insensitive, `Budget: (about|at most)? N (tool )?calls` plus the two current forms, a fixture per observed phrasing.
- health-delta thresholds: NLOC 30, CCN 7, params 3, nesting 2. Missing lizard warns and continues; lizard is installed machine-wide via mise, since this config serves one machine.
- The `tests/invariants/` disagreement counter leaves the design-rubric gate; public names and parameter counts stay.
- The commit hook warns first and blocks once the false-positive rate is known.
- Characterization tests belong to refactoring; tdd points there in one line.
- estimation folds into CLAUDE.md "Design" as about three lines; the skill is deleted.
- Spikes, decision records and specs live in `docs/spikes/`, `docs/decisions/`, `docs/specs/`, each from a template.
- The SVG checker has no spacing threshold. It fails on overlap, out-of-viewBox and text wider than its box, and prints measured gaps with no verdict; the model judges legibility and clash from a rendered PNG of the slide.
- slide-auditor passes `--timing <min>` in the documented command.
- Five acts is one arc among several; the skill asks which shape fits the material.
- slide-svg-figures and slide-auditor merge into one skill: the creator judges by the same rubric the reviewer applies.
