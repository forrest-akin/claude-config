# Handoff: apply the magpi rewrite's lessons to the skills

magpi was rewritten top-down on 2026-10-26, and a comparison of the original and the rewrite
(evidence in `~/github.com/forrest-akin/magpi/.claude/work/redo-main/compare/`, claims confirmed by
an independent refuter) produced lessons the user asked to apply. Each goes into an existing skill,
in its style: one or two lines per rule, present tense, no history, no magpi narrative beyond what a
rule needs to be understood.

## plan-readiness, Plan checks, Blocking

- **Hosted entrypoint.** When the entrypoint runs inside a host (an extension, plugin, hook or
  handler), the plan cites, from the host's own source or docs, how the host loads, runs and
  packages it: runtime, module loading, dependency rules, lifecycle. A probe that loads the host
  into your runtime proves the reverse. Evidence: magpi's original planned Bun and passed a gate
  that imported Pi under Bun; pi loads extensions on Node through jiti and wants Pi as a `*` peer,
  which overturned the runtime, packaging and process design.
- **Destructive steps at the tip.** Every destructive step (delete, overwrite, reset), including one
  carried from a spec, is checked against what its target holds once the whole plan has landed.
  Evidence: the spec's "delete a unit folder without work.json" rule went into C3, and C4 put the
  unit's session transcripts in that folder; a builder's size-cap stop caught it, not a review.

## commit-sequencing, Cutting

- The plan estimates each commit's changed lines (code, tests and docs). Past about 300, or more
  than one behavior a reviewer must hold at once, split before building. This replaces the vague
  "a very large commit" red flag. Evidence: C3 was planned with five behaviors, landed at 539 lines,
  and was rebuilt as three commits at about 10% of the run's agent spend; C4 hit 393 and was split.

## tdd

- A test that passes on its first run proves nothing yet: break the code it pins, watch it fail for
  the stated reason, restore. Evidence: ten tests passed first run because a handler was wired for
  every path at once.
- Before committing, break each new branch once; a break that leaves every test green marks code no
  test demanded: add the test or delete the code. Evidence: nine mutations survived the suite until
  review broke the code.
- A fake of a host API reproduces the host failure modes and lifecycle rules the code depends on
  (an object that throws once replaced, a call that rejects). Evidence: the fake pi context never
  threw after a session switch, so a notify on the stale context passed the tests and would throw
  in pi.

## Constraints

- Edit only those three `SKILL.md` files; leave frontmatter and descriptions unchanged.
- One commit per skill, `docs(skills): …`, explicit paths, no attribution trailers. This handoff
  lands with the first. Never push.
- Run `test/install.test.sh` before the last commit.
