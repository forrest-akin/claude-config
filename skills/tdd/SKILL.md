---
name: tdd
description: Drives a new behavior or a reproducible bug fix test-first, one failing test at a time, and settles what to do when a change has no behavior to pin. Use when adding behavior with a clear input/output contract, fixing a bug that can be reproduced as a test, or asked for test-first or red-green-refactor. Not for restructuring code under green tests (refactoring), nor for spikes or throwaway scripts.
---

# TDD

## Red

- One failing test at a time. Never write tests in a batch ahead of the code.

## Green

- Pass with a real implementation of the behavior the test names. Special-casing the test's
  inputs (returning the literal the only assertion expects, branching on a fixture value) is a
  faked green and is never written.
- If no honest implementation fits one small step, or a green is taking long, the test asked
  for too much: delete it and write a smaller one.
- If one example cannot pin the general behavior, pick an example that forces the general case
  rather than writing the literal and waiting for a second test.

## Two hats

- Either add behavior (red to green) or restructure (green to green), never both at once. A
  rename that tempts you mid-red is reverted; get green, then rename as its own step.
- While refactoring, don't anticipate: no early next test, and no unifying near-duplicates until a
  test forces the shape.

## When there is nothing to pin

- A change with no behavior to pin (config, wiring, formatting, generated code, runner setup):
  ask before going ahead without a test, and put the no-test rationale in the commit body.
- Characterizing legacy code before changing it is a separate, looser activity: pin what it does
  now, wrong parts included, then drive the change test-first.
- Whenever test-first is skipped, say so and why.
