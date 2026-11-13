---
name: tdd
description: Drives a new behavior or a reproducible bug fix test-first, one failing test at a time, and settles what to do when a change has no behavior to pin. Use when adding behavior with a clear input/output contract, fixing a bug that can be reproduced as a test, or asked for test-first or red-green-refactor. Not for restructuring code under green tests (refactoring), nor for spikes or throwaway scripts.
---

# TDD

## Red

- Before the first red, a function about to be extended whose shape a rule or an invariant test's
  docstring forbids is brought into line, as its own behavior-preserving commit. An invariant
  breach is a red test or a stop, never a tidy.
- One failing test at a time. Never write tests in a batch ahead of the code.
- A test that passes on its first run proves nothing yet: break the code it pins, watch it fail
  for the stated reason, restore.
- A fake of a host API reproduces the host's failure modes and lifecycle rules the code depends
  on (an object that throws once replaced, a call that rejects).

## Green

- Pass with a real implementation of the behavior the test names. Special-casing the test's
  inputs (returning the literal the only assertion expects, branching on a fixture value) is a
  faked green and is never written.
- If no honest implementation fits one small step, or a green is taking long, the test asked
  for too much: delete it and write a smaller one.
- If one example cannot pin the general behavior, pick an example that forces the general case
  rather than writing the literal and waiting for a second test.
- Before committing, break each new branch once. A break that leaves every test green marks code
  no test demanded: add the test or delete the code.
- Add behavior or restructure, never both in one step. A rename that tempts you mid-red is
  reverted until green, then made as its own step.
- While refactoring, don't anticipate: no early next test, and no unifying near-duplicates until a
  test forces the shape.

## When there is nothing to pin

- A change with no behavior to pin (config, wiring, formatting, generated code, runner setup):
  first check whether the code can move beneath the entrypoint so only the entrypoint remains,
  then ask before landing what remains without a test, and put the no-test rationale in the
  commit body.
- Legacy code with no tests gets characterization tests first (`refactoring`).
