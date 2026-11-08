# Plan: move each skill's mechanical work from prose to scripts, hooks, data and templates

Date: 2026-11-07. Seeded by `.claude/brainstorms/2026-11-07-deterministic-skills.md` ("Synthesis",
including Forrest's twelve decisions) and the reviewer reports `.claude/work/deterministic-skills/
{A,B,C}.md`. 43 commits on branch `deterministic-skills` from `main` (8e40ad1), in twelve installments.

## Context

- The reviewer reports were written after 8e40ad1 (reports 16:49-16:50, commit 16:02), so every
  `SKILL.md:<line>` they cite is current at the branch base. Citations below use their shorthand:
  `A:` = reviewer A's per-skill section, and so on; `<skill>:<n>` = `skills/<skill>/SKILL.md` line n.
- `install.sh` links `CLAUDE.md`, each `skills/*` directory and each `hooks/*.sh` into
  `~/.claude` and never removes a link. `~/.claude/settings.json` registers only
  `claude-notify.sh` (`jq '.hooks'`, 2026-11-07).
- Hook host facts, from `curl -sL https://code.claude.com/docs/en/hooks.md`: settings shape
  `{"hooks": {"<Event>": [{"matcher": "<tool regex>", "hooks": [{"type": "command", "command":
  "<path>"}]}]}}` (hooks.md "matcher" example, lines 315-335); the matcher is tested against
  `tool_name`; context goes back as `hookSpecificOutput.additionalContext` (hooks.md 1125-1132).
  `hooks/call-budget.sh` already uses that output and `/usr/bin/jq` (macOS ships jq).
- Slidev renders PNGs with `slidev export --format png` and `--range <n>`, and needs
  `playwright-chromium` as a devDependency of the deck repo
  (`slidevjs/slidev` `docs/guide/exporting.md`, "PNGs and Markdown", "Export with Range").
- `lizard` 1.25.1 (`uvx lizard --help`): `--csv`, `-ENS` counts nested control structures,
  `-T` thresholds. Not installed on this machine.
- `.claude/noticed.md` does not exist in this repo (ls at 8e40ad1), so no ledger entries to
  dispose of.
- Patterns followed: `test/*.test.sh` with a `check` helper and temp `HOME` (`test/install.test.sh`,
  `test/call-budget.test.sh`); `python3 -m unittest` with fixtures
  (`skills/slide-auditor/tests/`); pure-function bash tests (`skills/disk-space-reclamation/tests/
  test-select.sh`); acceptance by `grep -c -F` and commit bodies `Metric: … Baseline: …` then
  `Gate: …` (`.claude/plans/2026-11-07-abstraction-quality.md`).

## Planner decisions

- Line ranges are deleted or moved as the reports cite them; new text is given verbatim below.
  "Moved" means the lines land unchanged under the named heading of the target file.
- Every skill's moved platform facts go to `references/platform.md` in that skill, headed
  `# Platform facts (checked 2026-11-07)` and linked from the body with when to read it. One name
  across skills, so no reader guesses.
- `commit-sequencing:24` keeps the ship-here thought test and drops "test", which CLAUDE.md
  "Verify the claim at the tip" forbids per commit.
- The SVG element count is shapes and connectors without text: `audit_slides.py:245` skips text
  on purpose and the script is the check. `slide-svg-figures:20` and `visual-types.md:9` follow it.
- The slide budget is one content slide per 90 seconds: `audit_slides.py:133` already uses 90 s.
- `--palette custom` disables the off-palette check; the script cannot know the user's colours.
- The merged deck skill is `slide-rubric`: Forrest's reason for the merge is that "the creator
  judges by the same rubric the reviewer applies", and the name pairs with `design-rubric`.
- The PNG for judging spacing comes from `npx slidev export <slides.md> --format png --range <n>
  --output <dir>` read with the Read tool: the decision asks for the rendered slide, which a bare
  SVG rasteriser cannot give.
- `install.sh` merges settings with `/usr/bin/jq`; hook events live in a table in `install.sh`
  (`name|event|matcher`). A hook file with no row is linked and reported `unregistered: <name>`.
- The accepted-smell comment becomes `smell: <factor> — <rationale> — <YYYY-MM-DD>` on the line
  above the function; `health-delta` honours it.
- `wf-status` and `call-budget.sh` share one fixture list of budget phrasings,
  `test/fixtures/budget-phrasings.txt`, so the two parsers cannot drift silently.
- `check_timing.py` tests use a synthetic outline: the real one (`presentations/sagas/outline.md`)
  is talk prose and this repo is public.
- Increments the brainstorm's order does not schedule are listed under "Deferred" with a trigger.

## Open questions

None. Forrest decided on 2026-11-07:

1. `install.sh` removes its own dead links (C16): any link under `~/.claude` whose target is
   inside this repo and missing is removed and printed, with tests.
2. `diff-size.sh` (C39) speaks on every edit while the uncommitted change is over 200 lines or
   4 files, printing the counts; stateless, the same shape as `call-budget.sh` past 100%.

## Machine-level changes (approved by Forrest, 2026-11-07)

- The implementer runs `install.sh` against the real `HOME` at the end of I5 (after C18) and again
  at the end of I9 (after C39, so `diff-size.sh` is registered). This writes
  `~/.claude/settings.json` and relinks `~/.claude/skills`; `call-budget.sh` and `bash-prefix.sh`
  are live for every later installment.
- The implementer runs `mise use -g pipx:lizard` before C41.
- Implementers work in the repo checkout itself on branch `deterministic-skills`, never a separate
  worktree, so links keep pointing at the repo path. The checkout stays on the branch until it is
  merged: checking out `main` earlier leaves `~/.claude/skills/slide-rubric` dangling and
  `estimation`, `slide-auditor` and `slide-svg-figures` unlinked.
- Each run is reported under "Changes outside the repo" in the installment report.

## Rules for the implementer

- Branch `deterministic-skills` from `main` in the repo checkout (I1 creates it). Never push.
- Repo root `/Users/forrestakin/github.com/forrest-akin/claude-config`. Commands use literal
  absolute paths; no `cd` or `NAME=value` prefix (CLAUDE.md "Bash commands").
- Stage explicit paths only. C1 also stages `.claude/brainstorms/2026-11-07-deterministic-skills.md`
  and this plan. `.claude/work/` is never staged.
- No `Co-Authored-By`, `Claude-Session` or other attribution trailer.
- Line ranges in this plan are at 8e40ad1. Read them with `git show 8e40ad1:<path>` and locate
  the same text in the working tree by content; a range that earlier commits have moved is not a
  stop. Text that is not at the cited range at 8e40ad1 is.
- Before every commit load `doc-drift` and `design-rubric`; `error-modeling` when the commit adds
  a failure path; `commit-sequencing` for C18 and whenever a commit is split. Build scripts
  red-green (`tdd`): the test is written and seen failing before the code. When two shapes fit
  the next test, drive both to green and keep the one whose test was easier to write.
- Gates before every commit: `bash test/install.test.sh`, `claude plugin validate skills`, and the
  commit's own tests. A commit that touches an existing test suite runs that suite.
- Scripts: python3 stdlib, or bash that runs on macOS `/bin/bash` 3.2 (no `declare -A`,
  `mapfile`, `${x,,}`).
- Commit body: `Metric:` (what the commit makes measurable or what it saves, with the chars
  before→after for prose cuts), `Gate:` (commands run), and `Deviations:` only when departing
  from this plan.
- Stop conditions (verbatim from `workflow-design` "Executing a plan"):

  > Every implementer prompt and handoff names three stop conditions: two public entry points
  > would give different answers for the same inputs; two written rules conflict and no
  > precedence settles it; an invariant test would have to be weakened, narrowed, skipped or
  > worked around. In system-level work, a change on the breaking list in `commit-sequencing`
  > ("What forces expand/contract") is the first.

  Text that is not at the cited range at 8e40ad1 is the second condition (the plan and the file
  conflict). An acceptance check that would have to be loosened is the third.
- `Blocked:` (verbatim from the same section):

  > An implementer that meets a stop condition or an open trade-off ends its installment. Its
  > report opens with a `Blocked:` block: the condition, the question, the options with its pick
  > first, the proposed diff, and the commits it made before stopping. It commits green work
  > only, nothing for the blocked step.

- Installment report: commits made (short SHA, subject), gates run, deviations, known defects,
  changes outside the repo (command and result), untracked `.claude/` files.

## Phase 1 — prose only

### C1 `docs(skills): tdd defers characterization tests to refactoring and drops duplicates`

Files: `skills/tdd/SKILL.md`, `skills/refactoring/SKILL.md`, the brainstorm, this plan.

- tdd: delete `:30-31` (two hats), `:43`; replace `:41-42` with:

  ~~~text
  - Legacy code with no tests gets characterization tests first (`refactoring`).
  ~~~

- refactoring: delete `:30` (slowness is not a smell). `:10-11` stays the one home for
  characterization tests.
- Acceptance: `grep -c -F 'characterization tests first' skills/tdd/SKILL.md` → 1; the diff
  removes only the cited lines; `git show --name-only --format= HEAD` lists the four files.
- ~10 lines.

### C2 `docs(skills): commit-sequencing drops CLAUDE.md restatements`

Files: `skills/commit-sequencing/SKILL.md`.

- Delete the refactor-with-behavior item from the always-stack list at `:10-12` (CLAUDE.md
  "Commits" owns it); the collapse exception at `:19-20` keeps its wording.
- Replace `:24` with `- At every cut, ask whether trunk could ship right here with nothing after
  it. If not, re-cut.`
- Acceptance: `grep -c -F 'ask whether trunk could ship' skills/commit-sequencing/SKILL.md` → 1;
  `grep -c -F 'Test every cut' skills/commit-sequencing/SKILL.md` → 0. ~4 lines.

### C3 `docs(skills): design-rubric gate counts public names and parameters only`

Files: `skills/design-rubric/SKILL.md`, `skills/plan-readiness/SKILL.md`.

- Replace the interface-numbers bullet at `:13-17` with `- The two interface numbers never
  worsen past what the plan's task states: public names, and parameters per public function.`
  (the `tests/invariants/` counter and the disagreement-precedence sentence go).
- Delete `:20` whole ("Each cure is the move this rubric names, carried out per `refactoring`.";
  the description already says it).
- `plan-readiness:38-39` "the three interface numbers" becomes "the two interface numbers".
- Delete the CodeScene provenance at `:72-74`, keeping the `## Health factors` heading.
- Acceptance: `grep -c 'tests/invariants' skills/design-rubric/SKILL.md` → 0;
  `grep -c -F 'The two interface numbers' skills/design-rubric/SKILL.md` → 1;
  `tr '\n' ' ' < skills/plan-readiness/SKILL.md | tr -s ' ' | grep -c 'three interface numbers'` → 0. ~12 lines.

### C4 `docs(skills): error-modeling names the lints that enforce exhaustiveness and silent catches`

Files: `skills/error-modeling/SKILL.md`.

- After `:33` add:

  ~~~text
  - Lints catch both: clippy `wildcard_enum_match_arm` and `let_underscore_must_use`;
    typescript-eslint `switch-exhaustiveness-check` and `no-floating-promises`; ESLint
    `no-empty`. Turn them on in the project instead of checking by eye.
  ~~~

- Before committing, confirm each rule name on its docs page (`trafilatura -u` on
  rust-lang.github.io/rust-clippy, typescript-eslint.io/rules, eslint.org/docs/latest/rules) and
  quote the hit in the body. A missing rule is a stop (second condition).
- Acceptance: `grep -c -F 'switch-exhaustiveness-check' skills/error-modeling/SKILL.md` → 1. ~2 lines.

### C5 `docs(skills): disk-space-reclamation body stops restating its scripts`

Files: `skills/disk-space-reclamation/SKILL.md`.

- Delete `:10-14` (enforced by `reclaim-plan.sh:61-64`), `:51-55`, `:62-66`.
- Cut the shared-caches bullet `:34-38` to its first sentence plus its runbook pointer.
- Acceptance: body ≤ 2,800 chars (`wc -c`, from 4,156); `bash
  skills/disk-space-reclamation/tests/test-select.sh` passes. ~25 lines.

### C6 `docs(skills): workflow-design moves platform facts to a reference and drops CLAUDE.md duplicates`

Files: `skills/workflow-design/SKILL.md`, `skills/workflow-design/references/platform.md` (new).

- Move `:12-14` (measured budgets) and the `## Platform facts` section `:143-175` to
  `references/platform.md`.
- Delete `:15-16`, `:24-25`, `:42`; at `:110-112` delete the `AskUserQuestion`/`SendMessage`
  sentence and keep "Inside a Workflow a blocked task is terminal; the orchestrator re-dispatches
  it after the answer."; at `:132` delete the clause requiring the batching statement (CLAUDE.md
  "Subagents").
- Add at the end of the body:

  ~~~text
  Platform facts (journal format, resume, limits) are in `references/platform.md`. Read it when a
  run stalls, fails or is resumed.
  ~~~

- Acceptance: `grep -c '^## Platform facts' skills/workflow-design/SKILL.md` → 0; every moved
  line is in the reference (`diff` of removed lines vs reference body); body ≤ 8,500 chars (from
  11,285); stop-condition sentence at `:101-105` unchanged. ~90 lines.

### C7 `docs(skills): subagent-model-tiering moves platform facts out and takes the stall rule`

Files: `skills/subagent-model-tiering/SKILL.md`, `.../references/platform.md` (new),
`skills/workflow-design/SKILL.md`.

- Move `## Platform facts` `:58-83` to the reference; delete `:20`, `:23`.
- From `workflow-design:46-48`, move the two sentences after "Set per stage, never blanket
  (`subagent-model-tiering`)." (a retry-prone stage runs cheaper; after the second stall, bound
  the request and drop its effort) to the end of "Escalate on a signal, once" (`:32-38`).
  `## Model and effort` in workflow-design keeps its heading and the "Set per stage" sentence.
- Acceptance: body ≤ 3,200 chars (from 4,623);
  `grep -c 'second stall' skills/workflow-design/SKILL.md` → 0 and in tiering → 1. ~45 lines.

### C8 `docs(skills): interface-design drops CLAUDE.md duplicates and fixes example drift`

Files: `skills/interface-design/SKILL.md`, `.../example.md`, `.../references/platform.md` (new).

- Delete `:13-16`; `example.md:3-6`.
- Rewrite the stop conditions at `example.md:28-30` to carry these three clauses verbatim:
  `two public entry points would give different answers for the same inputs`;
  `two written rules conflict and no precedence settles it`;
  `an invariant test would have to be weakened, narrowed, skipped or worked around`.
- Move the stack table `:93-99` (`:100`, where invariant tests live, stays), the ask-rule facts `:106-107` and `:110-111`, and `## Sources`
  `:113-118` to the reference; `:108-109` stays.
- Acceptance: each clause → 1 in `example.md` (`grep -c -F`); body ≤ 5,500 chars (from 6,826). ~45 lines.

### C9 `docs(skills): extension-authoring moves silent-failure facts to a reference`

Files: `skills/extension-authoring/SKILL.md`, `.../references/platform.md` (new).

- Move `## Silent failures` `:63-107`, `:160-163` and `## Sources` `:165-176` to the reference.
  In their place:

  ~~~text
  ## Silent failures

  When an extension does not load or fire, read `references/platform.md`.
  ~~~

- Replace `:155-156` with `` - Fix the other files the lesson made wrong with `doc-drift`. ``
- Delete `:177-178` (CLAUDE.md "Reading web sources").
- Acceptance: body ≤ 7,500 chars (from 10,486); `claude plugin validate skills` passes. ~75 lines.

### C10 `docs(skills): plan-readiness reports every check as a row`

Files: `skills/plan-readiness/SKILL.md`.

- Replace `:91` (evaluate every check) with `- Report every Blocking and Should-fix check as a
  row: check, verdict (pass, fail or n/a), one sentence naming the section. A missing row is a
  skipped check.`
- Acceptance: `grep -c -F 'A missing row is a skipped check' skills/plan-readiness/SKILL.md` → 1. ~2 lines.

### C11 `docs(skills): slide-svg-figures judges spacing from the rendered slide`

Files: `skills/slide-svg-figures/SKILL.md`, `.../references/visual-types.md`.

- Delete `:10-12`, the boilerplate snippets `:78-125` (keep `:127`), the Slidev wrapper `:172-199`.
- Replace the 40px rule `:21` and the gap lines of the checklist `:64-74` with:

  ~~~text
  - Spacing has no fixed number. Render the slide and judge legibility and clashes from the
    image: `npx slidev export <slides.md> --format png --range <n> --output <dir>`, then read
    the PNG. Export needs `playwright-chromium` in the deck's devDependencies.
  ~~~

- `:20` becomes `- At most 7 shapes and connectors per figure; text labels do not count.`;
  `visual-types.md:9` becomes 4 boxes and 3 arrows.
- Before committing, confirm `--output` in Slidev's CLI docs
  (`curl -sL https://raw.githubusercontent.com/slidevjs/slidev/main/docs/builtin/cli.md`); a
  missing flag is a stop (second condition).
- Acceptance: `grep -c '40px' skills/slide-svg-figures/SKILL.md` → 0;
  `grep -c -F 'format png' skills/slide-svg-figures/SKILL.md` → 1; body ≤ 5,500 chars (from 8,751). ~95 lines.

### C12 `docs(skills): slide-auditor body is the command and the remedies`

Files: `skills/slide-auditor/SKILL.md`.

- Body after the title becomes exactly:

  ~~~markdown
  Run the audit, passing the talk's length in minutes:

  ```bash
  python3 ${CLAUDE_SKILL_DIR}/scripts/audit_slides.py slides.md --timing <minutes>
  ```

  Fix each finding and rerun until none remain. Per finding, choose the remedy: cut words, split
  the slide, or move content to the speaker notes. Fix a font-size finding with fewer words, never
  a smaller font. viewBox limits per layout are in `slide-svg-figures/references/slidev-canvas.md`.
  ~~~

- Acceptance: `grep -c -F -- '--timing <minutes>' skills/slide-auditor/SKILL.md` → 1; body ≤
  900 chars. ~75 lines.

### C13 `docs(skills): presentation-narrative treats five acts as one arc and budgets slides by time`

Files: `skills/presentation-narrative/SKILL.md`, `.../references/pacing.md`,
`.../references/five-act-structure.md`, `templates/slidev-presentations/.claude/agents/slide-designer.md`.

- Delete `:8-15`, `:100-118`, `pacing.md:78-102`, the slide-count table
  `five-act-structure.md:106-120`, the per-length table `pacing.md:9-16`.
- Replace `:19` with: `Choose the arc that fits the material before outlining. Five acts
  (below) suits a talk that unsettles one belief; a teaching session can be a ladder of versions,
  each fixing the last one's failure; a walkthrough follows the system's own order. Ask the
  presenter when the material does not decide it.`
- The act table `:23-33` loses its slide-count column and the totals row. `:39` becomes
  `- Budget one content slide per 90 seconds: minutes × 60 ÷ 90 (15 minutes → 10).`
- `slide-designer.md:29` becomes:

  ~~~text
  2. **Propose a narrative arc** — the shape that fits the material (`presentation-narrative`); five acts is one option
  ~~~

- Acceptance: `grep -rc '8-12\|10-14\|9-11\|8-13' skills/presentation-narrative` → all 0;
  `grep -c -F 'one content slide per 90 seconds' skills/presentation-narrative/SKILL.md` → 1;
  `grep -c 'five acts' templates/slidev-presentations/.claude/agents/slide-designer.md` → 1. ~120 lines.

## Phase 2 — make what exists work

### C14 `feat(install): install.sh registers the hooks in settings.json`

Files: `install.sh`, `test/install.test.sh`, `README.md`.

- Table in `install.sh`: `call-budget.sh|PostToolUse|` and `bash-prefix.sh|PreToolUse|Bash`.
  For each linked hook with a row, append `{matcher, hooks:[{type:"command",
  command:"$HOME/.claude/hooks/<name>"}]}` (literal `$HOME`, as the existing notify entry) to
  `.hooks[event]` unless an entry in that event already has that command. Missing settings file
  → start from `{}`. Write via a temp file and `mv`. Invalid JSON → exit 1, file untouched,
  message names the file. A hook with no row prints `unregistered: <name>`.
- Tests (red first; fixture hooks renamed to `call-budget.sh`, `bash-prefix.sh`, plus `gamma.sh`
  with no row): fresh HOME gets both entries; second run keeps one of each; existing
  `Notification` entry and unrelated keys survive; invalid JSON exits 1 unchanged; `gamma.sh` is
  linked and named `unregistered`.
- README "Hooks": replace the "A linked hook runs once registered" paragraph and JSON with
  `` `install.sh` registers `call-budget.sh` on PostToolUse and `bash-prefix.sh` on PreToolUse
  (Bash) in `~/.claude/settings.json`, adding each entry once.``; header comment `install.sh:3`
  says the same.
- Acceptance: `bash test/install.test.sh` → `all passed`. ~90 lines.

### C15 `feat(hooks): call-budget reads every budget phrasing in use`

Files: `hooks/call-budget.sh`, `test/call-budget.test.sh`, `test/fixtures/budget-phrasings.txt`
(new), `README.md`.

- Fixture file, one `<phrase>\t<n>` per line: `Budget: 30 tool calls`, `Budget: about 25 tool
  calls`, `Hard budget: 12 tool calls`, `Hard budget: 12`, `Budget: at most 30 tool calls`,
  `About 10 calls`, `about 55 calls`, `About 55 tool calls`; and one non-budget line
  (`called about the budget`) expecting nothing.
- Regex, case-insensitive (`"i"` flag on `capture`): `(budget: *(about |at most )?|about
  )(?<n>[0-9]+) (tool )?calls`, else `hard budget: *(?<n>[0-9]+)`.
- Test loops the fixture at 100% of each budget. README's phrasing list points at the fixture.
- Acceptance: `bash test/call-budget.test.sh` → `all passed`. ~40 lines.

### C16 `feat(install): install.sh removes its own links whose source is gone`

Files: `install.sh`, `test/install.test.sh`, `README.md`.

- Before linking: each symlink at `~/.claude/CLAUDE.md`, `~/.claude/skills/*`,
  `~/.claude/hooks/*.sh` whose `readlink` starts with `$repo/` and does not exist is removed and
  printed `unlinked <path>`. Links elsewhere and non-links are never touched.
- Tests: deleted fixture skill's link is removed; a dead link to `/elsewhere` stays; a live link stays.
- README "Install" gains that sentence. Acceptance: `bash test/install.test.sh` passes. ~35 lines.

### C17 `docs: estimation folds into CLAUDE.md "Design"`

Files: `CLAUDE.md`, `skills/estimation/SKILL.md` (deleted).

- Append to "Design", after the "Decide from measurement" paragraph:

  ~~~text
  Estimate by splitting the work into Claude's mechanical work, human decisions, external waits
  and slow-feedback debugging; the total is roughly the longest wait plus the decisions plus a
  padded debugging share. Price mechanical work at Claude's rate. Push back once, with the
  split, when cost reasoning is wrong, but not when the choice turns on non-cost factors, review
  load or API spend.
  ~~~

- Destructive check: `grep -rn '`estimation`' skills templates README.md CLAUDE.md` → 0 hits after
  the commit (none at 8e40ad1 outside the skill itself).
- Acceptance: `test -e skills/estimation` fails; `grep -c -F 'longest wait' CLAUDE.md` → 1. ~40 lines.

### C18 `feat(skills): merge slide-svg-figures and slide-auditor into slide-rubric`

Files: `skills/slide-rubric/` (from `git mv` of `slide-auditor/scripts`, `slide-auditor/tests`,
`slide-svg-figures/references`), `skills/slide-rubric/SKILL.md` (new), both old `SKILL.md`
deleted, `skills/presentation-narrative/SKILL.md`, `skills/slide-rubric/scripts/audit_slides.py`.

- Frontmatter:

  ~~~yaml
  name: slide-rubric
  description: Draws inline SVG figures for Slidev slides and audits a finished slides.md for SVG size, font, density, speaker-note, timing and layout problems, judging spacing from the rendered slide. Use when drawing or fixing a slide figure, or when checking a deck before presenting it. Not for a talk's arc or outline (presentation-narrative).
  ~~~

- Body: `# Slide rubric`, then `## Figures` (C11's body below its title), then `## Audit` (C12's
  body); `slide-svg-figures/references/` paths become `references/`.
- `presentation-narrative:3` "(slide-svg-figures)" → "(slide-rubric)"; `audit_slides.py:125`
  comment path → `references/slidev-canvas.md`.
- `install.sh` links `skills/slide-rubric` with no change; C16 removes the two old links on the
  next run. README and `templates/` name neither old
  skill (grep at 8e40ad1).
- Acceptance: `grep -rn 'slide-svg-figures\|slide-auditor' skills templates README.md` → 0;
  `python3 -m unittest discover -s skills/slide-rubric/tests` passes; `claude plugin validate
  skills` passes. ~60 lines plus renames.

### C19-C23 audit defects, each test-first in `skills/slide-rubric/tests/test_audit_slides.py`

One behavior each; every test is seen failing before the fix in `scripts/audit_slides.py`. Gate:
`python3 -m unittest discover -s skills/slide-rubric/tests`.

| Commit | Subject | Red test | Fix (C.md "slide-auditor") | Lines |
|---|---|---|---|---|
| C19 | `fix(skills): slide-rubric counts SVG elements as specified` | 12 shapes → ERROR; 8 → WARNING; an arrow `path` with `marker-end` counts; a `path` inside `<marker>` does not; a `polygon` counts | `>10` checked before `>7` (`:253-260`); path filter (`:243`); polygons summed (`:244`, `:249-251`) | ~50 |
| C20 | `fix(skills): slide-rubric parses decimal and comma viewBoxes` | `0 0 850.5 350` and `0,0,800,400` give no missing-viewBox finding | regex `:218` | ~25 |
| C21 | `fix(skills): slide-rubric checks short hex colours` | a 3-digit colour whose 6-digit form is in the palette is not flagged; one whose form is not is flagged | expand 3-digit hex before `:278` | ~25 |
| C22 | `fix(skills): slide-rubric skips the palette check for --palette custom` | `custom` with any colour → no off-palette finding | `:368`, `:381` | ~20 |
| C23 | `fix(skills): slide-rubric excludes code fences from the word count` | 40 words inside a fence + 5 outside → no density finding | `:199-205` | ~25 |

### C24 `test(skills): characterize reclaim-apply guards and protect-list exits`

Files: `skills/disk-space-reclamation/tests/test-apply.sh`, `.../tests/test-protect-list.sh` (new).

- Temp `HOME` and temp trees only. Pin current behavior: unknown category, `/`, `$HOME`, a
  vanished path, dry run deletes nothing; `protect-list.sh` exit 3 and its too-coarse exclusion
  (read the script for the exact conditions). Characterization tests pass on first run.
- Acceptance: both pass. ~90 lines.

### C25 `fix(skills): reclaim-apply reports a failed removal as skipped`

- Red test in `test-apply.sh`: a row whose `rm -rf` fails (parent `chmod 555`) is printed
  skipped and not added to the count or KB (`reclaim-apply.sh:62`). ~20 lines.

### C26 `fix(skills): disk-survey excludes node_modules under build directories`

- New `tests/test-survey.sh`: `disk-survey.sh <tmp root>` with `build/node_modules/<file>` →
  the REGENERABLE size for `build` excludes it. Fix `disk-survey.sh:35-37` with a `-prune`, one
  `find` per pattern. ~40 lines.

## Phase 3 — data and templates

### C27 `feat(skills): slide-rubric reads canvas limits per layout from deck_constants.json`

Files: `skills/slide-rubric/scripts/deck_constants.json` (new), `scripts/audit_slides.py`,
`tests/test_audit_slides.py`, `references/slidev-canvas.md` (deleted), `SKILL.md`.

- JSON: `canvas` per layout from `slidev-canvas.md:5-30`; `thresholds` from `audit_slides.py:125-133`
  (font, words, elements 7/10, notes words, seconds per slide). The script reads it beside itself.
- Red test: a `center` slide with an 850×420 viewBox gives no WARNING.
- The custom-canvas formula (`slidev-canvas.md:36-41`) becomes one line in `## Figures`; the
  wrapper `:43-55` goes (C11 removed its twin). SKILL.md pointer → `scripts/deck_constants.json`.
- Acceptance: unittest passes; `grep -rn 'slidev-canvas' skills` → 0. ~110 lines.

### C28 `feat(skills): slide-rubric keeps one palette in deck_constants.json`

- Palettes with role names move from `audit_slides.py:99-115` into the JSON; the script reads
  them. `references/color-palettes.md` keeps only `:52-65` (contrast, brand mapping); the
  palette table `slide-svg-figures:129-145` (now in `## Figures`) becomes
  `` Fill by role from the palette in `scripts/deck_constants.json`. ``
- Red test: a colour removed from the JSON palette is flagged.
- Acceptance: unittest passes; no hex literal remains in `audit_slides.py` (`grep -c '#[0-9A-Fa-f]\{6\}'` → 0). ~80 lines.

### C29 `feat(skills): workflow-design prompt templates and a stop-condition identity test`

Files: `skills/workflow-design/templates/{agent-preamble,implementer-block,blocked,installment-report}.md`
(new), `skills/workflow-design/SKILL.md`, `test/stop-conditions.test.sh` (new).

- `agent-preamble.md` carries `:22-31` as second-person instructions with `<source>`,
  `Hard budget: <N> tool calls`, `<paths>` placeholders. `installment-report.md` carries `:65-67`.
  `implementer-block.md` carries `:96-109` and the status line of `:113-114`; its stop conditions
  are the three clauses verbatim. `blocked.md` is:

  ~~~text
  Blocked:
  - Condition: <stop condition or open trade-off>
  - Question: <one question for the human>
  - Options: <my pick first, labelled as mine>; <other options>
  - Proposed diff: <diff or path>
  - Commits made: <short SHAs and subjects, or none>
  ~~~

- The body keeps the stop-condition and `Blocked:` sentences (CLAUDE.md points at them) and
  replaces the rest of the cited lines with one line per template naming when to paste it.
- `test/stop-conditions.test.sh` normalises each file by joining lines and squeezing whitespace,
  `tr '\n' ' ' < "$f" | tr -s ' \t' ' '`, then requires `grep -c -F "$clause"` ≥ 1 on the result
  for each of the three clauses in `skills/workflow-design/SKILL.md`,
  `skills/workflow-design/templates/implementer-block.md` and
  `skills/interface-design/example.md`. The sentence C6 keeps unchanged at `:101-105` wraps
  clauses across lines; the normalised form matches it.
- Acceptance: the test passes at this commit, and its SKILL.md check also passes against
  `git show 8e40ad1:skills/workflow-design/SKILL.md`; body shrinks by ≥ 1,000 chars. ~120 lines.

### C30 `feat(skills): interface-design draft template`

Files: `skills/interface-design/templates/interface-draft.md` (new), `SKILL.md`,
`test/stop-conditions.test.sh`.

- Template: the seven sections of `:67-82` in order, each item ending `— <name>, <YYYY-MM-DD>`;
  the standing rules `:77-82` verbatim; the three clauses verbatim. `:67-82` become:

  ~~~text
  Copy `templates/interface-draft.md` to `.claude/interfaces/<area>.md` and fill every
  placeholder. The draft has converged when no item lacks an attribution.
  ~~~

- The identity test gains the template. Acceptance: it passes. ~60 lines.

### C31 `feat(skills): plan-readiness homes and templates for spikes, decision records and specs`

Files: `skills/plan-readiness/templates/{spike,decision-record,spec}.md` (new), `SKILL.md`.

- Templates hold the sections `:48-54` require (spike: questions, task→question map, definition
  of done, time box; decision record: context, decision, downsides, rejected alternatives; spec:
  goals with measures, parts and data flow, failures and handling, out of scope).
- Replace `:22-23` with:

  ~~~text
  - Spikes live in `docs/spikes/`, decision records in `docs/decisions/`, specs in `docs/specs/`,
    each named `YYYY-MM-DD-<topic>.md` and started from `templates/<kind>.md`. List the
    directory and resume one on the same topic instead of starting another.
  ~~~

- Acceptance: three files exist with those headings; `grep -c -F 'docs/decisions/'
  skills/plan-readiness/SKILL.md` → 1. ~60 lines.

### C32 `docs(skills): root-cause-analysis writes a fixed skeleton`

Files: `skills/root-cause-analysis/SKILL.md`.

- Replace `:40-41` with:

  ~~~markdown
  Write the record as:

  - **Symptom**: what was seen, when, impact.
  - **Chain**: table `layer | cause | counterfactual`.
  - **Underlying cause**: one sentence.
  - **Not pursued**: table `cause | counterfactual | independent, coupled or chained`.
  - **Remediation**: table `fix | targets (underlying, or contributing marked tactical)`.
  - **Control boundary**: what was inside and outside the team's control.
  ~~~

- Acceptance: `grep -c -F 'Control boundary' skills/root-cause-analysis/SKILL.md` → 1. ~12 lines.

## Phase 4 — scripts with observed need

Each script: python3 stdlib unless noted, in `skills/<skill>/bin/`, tests in
`skills/<skill>/tests/` with fixtures built in a temp dir (`git init`, `GIT_COMMITTER_DATE` for
dated commits). The body line that names the command replaces the cited prose in the same commit.

Defaults and lookups:

- `stale-refs` and `health-delta`: `BASE` defaults to `HEAD`, comparing the working tree (staged
  and unstaged) with the last commit. Both run before a commit, so `HEAD~1` or the merge-base
  would re-report changes already committed.
- `noticed-scan`: `repo` defaults to `git rev-parse --show-toplevel` of the current directory.
- `wf-status`: a directory argument is used as is; `wf_<id>` resolves by globbing
  `~/.claude/projects/*/*/subagents/workflows/wf_<id>/` (`<session>/subagents/workflows/wf_<id>/`,
  workflow-design "Platform facts", `:170`). Zero or several matches exit 2 naming the count.
- `stack-check`: `BASE` is required.

Failure behaviour (each has a test):

- `stale-refs`, `health-delta`, `stack-check`: outside a git repo or with an unknown `BASE`, print
  `error: <reason>` to stderr and exit 2. Unreadable files go to the `unread:` section.
- `noticed-scan`: no `.claude/noticed.md` prints nothing and exits 0.
- `wf-status`: missing `journal.jsonl` or `subagents/` exits 2 naming the path; a malformed
  JSONL line is reported as `skipped line <n>` and the rest is read.
- `check_timing.py`, `interface-check`, `lint-extension`: unreadable input, or no table or
  heading where one is required, gives one finding naming what is missing and exits 1, as any
  finding does.
- `diff-size.sh`: an edit outside a git repo, or any git error, exits 0 with no output.
- `notice`: an argument count other than three prints usage and exits 2.

| Commit | Subject | Inputs → output | Tests | Prose replaced | Lines |
|---|---|---|---|---|---|
| C33 | `feat(skills): doc-drift lists facts a diff removed that docs still state` | `bin/stale-refs [BASE]` → TSV `token class doc:line last-edited`, then `unread:` | rename, removed env var, bumped version, a token still in code (not reported) | `doc-drift:10-12`, `:20`, `:32` | ~180 |
| C34 | `feat(skills): extension-authoring lints frontmatter and descriptions` | `bin/lint-extension <path>`: `---` first line, `name`/`description`, description + `when_to_use` ≤ 1,536, one "Use when", ≤ 1 "Not for", unknown keys; `test/lint-skills.test.sh` runs it over `skills/` | fixture dir per check | the `## Silent failures` pointer becomes: run `bin/lint-extension <path>`, then read the reference if it passes | ~200 |
| C35 | `feat(skills): lint-extension checks links, preprocessing hazards and bash 3.2` | adds: relative links resolve; unescaped `$ARGUMENTS`, `$0`, `!`+backtick; `#!/bin/bash` with `declare -A`, `mapfile`, `readarray`, `${x,,}`, `${x^^}` | fixture per check | `extension-authoring:42-47` → one line | ~150 |
| C36 | `feat(skills): plan-readiness noticed-scan ranks ledger entries for a plan` | `bin/noticed-scan <plan> [repo]` → `touched-file`/`touched-dir`/`delete` rows with 1-year commit counts, sorted | fixture repo with dated commits | `plan-readiness:77-80`; `interface-design:29` points at it | ~150 |
| C37 | `feat(skills): workflow-design wf-status reports agents past budget or stalled` | `bin/wf-status <session dir or wf_id>` → per agent: label, budget, tool calls, minutes idle, interrupted, result count per label; exit 1 when any heartbeat condition of `:136-139` holds | fixture journal and transcripts (shape copied from a real run, contents synthetic); `test/fixtures/budget-phrasings.txt` | `:57-58` count, `:136-141` → `Monitor` with `until ! wf-status …` | ~200 |
| C38 | `feat(skills): presentation-narrative check_timing.py checks the timing table` | `scripts/check_timing.py <outline> --window <min>` → one line per mismatch, silent on pass | synthetic passing outline + three broken copies (bad duration, gap, wrong total) | the 90 s budget line gains `; scripts/check_timing.py checks the timing table` | ~100 |
| C39 | `feat(hooks): diff-size reports uncommitted size during edits` | PostToolUse `Edit\|Write` (matcher confirmed against hooks.md tool names): `git diff --shortstat HEAD` + untracked lines in the edited file's repo → `additionalContext` `Uncommitted: N files, M lines`; `install.sh` table row; README hook list | `test/diff-size.test.sh` with a temp repo | `refactoring:46-47` → `When diff-size reports 200 lines or 4 files, commit the green part and raise the design question.` | ~110 |
| C40 | `feat(skills): design-rubric bin/notice appends a ledger line` | `bin/notice <path:line> <smell> <move>` → appends the `:104` line dated today, creating the file with its heading | empty and existing ledger | `:102-106` → one command line | ~40 |
| C41 | `feat(skills): design-rubric health-delta reports metric smells a diff worsened` | `bin/health-delta [BASE]`: lizard `--csv -ENS` on BASE blob and working copy per touched file; reports a function when after > threshold and (new, before ≤ threshold, or after > before); thresholds NLOC 30, CCN 7, params 3, nesting 2; skips a function under `smell: <factor> — <rationale> — <YYYY-MM-DD>`; missing lizard → `warning: lizard not found; health-delta skipped` on stderr, exit 0 | Rust and TS before/after fixtures per metric, the suppression case, the missing-lizard case (`PATH` without lizard) | the Large method, Cyclomatic complexity, Nested complexity and Excess arguments lines in `:76-87` → one line naming the command and thresholds; Brain method, Bumpy road and Complex conditional stay as judgment smells, with a clause saying lizard does not measure them; `:19` shows the comment format | ~250 |
| C42 | `feat(skills): commit-sequencing stack-check flags oversize and placeholder commits` | `bin/stack-check BASE` → TSV `sha subject files lines flags`; flags `>300`, `placeholder` (`^(wip\|temp\|tmp\|fixup!\|part [0-9])`, case-insensitive); trailer total and `collapse?` under 100 | temp repo, one commit per flag | `:31-35` in check mode → the command | ~120 |
| C43 | `feat(skills): interface-design interface-check validates a draft` | `bin/interface-check <draft>`: seven headings in order, numbered invariants, every item attributed, standing rules and three clauses identical to the template; lists unattributed items | passing fixture + one per failure | `:18-19` → `interface-check passes when the draft has converged` | ~140 |

Before C41, run `mise use -g pipx:lizard` (approved, see "Machine-level changes"; not committed;
reported under "Changes outside the repo"). C34 and C35: if the linter flags an
existing skill, commit that skill's fix first as its own `fix(skills)` commit. C34's known-key
lists cite `curl -sL https://code.claude.com/docs/en/skills.md` and `.../sub-agents.md` in the
script header.

Commit count: C1-C43 is 43 commits.

## Verification at the tip

In a clean worktree of the branch tip: `bash test/install.test.sh`, `bash test/call-budget.test.sh`,
`bash test/bash-prefix.test.sh`, `bash test/stop-conditions.test.sh`, `bash test/lint-skills.test.sh`,
`bash test/diff-size.test.sh`, `claude plugin validate skills`, every `skills/*/tests/` suite.
Each installment ends with this for the suites its commits touched.

## Installments

Sequential on one branch. Each implementer reads, before anything else: this plan's "Context",
"Planner decisions", "Rules for the implementer", its commits' sections, and the named report.

| Installment | Commits | Reads first | Calls (est.) |
|---|---|---|---|
| I1 | C1-C5 | A.md tdd, refactoring, commit-sequencing, design-rubric, error-modeling, disk-space-reclamation | ~40 |
| I2 | C6-C10 | B.md workflow-design, subagent-model-tiering, interface-design, extension-authoring, plan-readiness | ~45 |
| I3 | C11-C13 | C.md | ~35 |
| I4 | C14-C17 | `install.sh`, `test/install.test.sh`, `hooks/call-budget.sh`, `test/call-budget.test.sh`, README | ~50 |
| I5 | C18-C23, then `install.sh` against the real `HOME`: `jq '.hooks' ~/.claude/settings.json` lists both hooks; `ls -l ~/.claude/skills` shows `slide-rubric` and no dead links | C.md "slide-auditor"; `audit_slides.py`; its tests | ~55 |
| I6 | C24-C28 | A.md "disk-space-reclamation"; the reclamation scripts; C.md "Cross-cutting" | ~50 |
| I7 | C29-C33 | B.md workflow-design, interface-design, plan-readiness; A.md doc-drift, root-cause-analysis | ~50 |
| I8 | C34-C35 | B.md extension-authoring; skills.md and sub-agents.md docs | ~45 |
| I9 | C36-C39, then `install.sh` against the real `HOME`: `jq '.hooks.PostToolUse' ~/.claude/settings.json` lists `diff-size.sh` | B.md plan-readiness, workflow-design "Proposed mechanisms"; C.md presentation-narrative; A.md X1; hooks.md | ~55 |
| I10 | C40-C41, with `mise use -g pipx:lizard` before C41 | A.md design-rubric | ~45 |
| I11 | C42 | A.md commit-sequencing | ~20 |
| I12 | C43, then the tip verification | B.md interface-design | ~30 |

## Deferred (build on evidence)

| Item | Trigger that starts it |
|---|---|
| `check_svg.py` (overlap, out-of-viewBox, text wider than its box; prints measured gaps with no verdict; no spacing threshold) | The first real deck built with `slide-rubric` has its PNG pass find an overlap or overflow the audit missed. |
| `plan-lint` (candidate lister, never a gate) | Two plans pass `plan-readiness` and a later reviewer finds a placeholder, hedge or unchecked destructive step a grep would have listed. |
| `spike-measure` | The first manual comparative spike is run and its judge table shows which columns cost the most time. |
| `wf-estimate` | Three Workflow launch summaries in a row omit the token or agent figure. |
| Commit gate hook (warns first; blocks once the false-positive rate is known) | `health-delta` has run by hand on 20 commits with its false positives counted. |
| `co-change`, `public-surface` | A review finds a leaky boundary or an interface-number increase that the gate missed. |
| Not scheduled by the brainstorm: tdd mutation commands, refactoring diff-coverage line, root-cause-analysis bisect line, `env-drift`, `stack-check` migration flags, `agent-models`, `protect-paths`, `lesson-homes`, lint-extension agent/hook/memory checks, check_svg crossing/fill/contrast, audit headmatter/fence/near-palette checks, notes thresholds from wpm, reclamation `ask` rule, dry-run stamp, swap diagnosis, apply-time re-check, `runtime-prune.sh` | The failure each addresses is observed in a transcript. |
