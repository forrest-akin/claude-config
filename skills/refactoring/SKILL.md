---
name: refactoring
description: Restructures code without changing behavior, one named move per green step, and picks which smell or misleading name to fix first. Use when extracting, inlining, moving or renaming code, when code smells or a name resists, or when preparing the ground before a feature. Not for adding behavior (tdd), performance work, or cross-module redesign.
---

# Refactoring

## Gate

- Every move starts and ends on a green suite. Red or absent tests: write characterization tests
  first, pinning what the code does now, wrong parts included.
- A red after a move is reverted, never debugged or patched forward.

## Moves

- One named move per green-to-green step (Extract Function, Inline Variable, Move Field, ...).
  The move changes structure only; a logic edit or a second move waits for its own step.
- One kind of move per commit, the subject naming it.
- Replacing a type switch with dispatch needs a test per branch first.
- If the extracted thing won't take a name, the boundary is wrong: inline it and extract
  elsewhere.

## Diagnosis

- Name the smell before moving; fixing it is a separate, test-gated step.
- When two smells match, fix the one whose cure fixes the deeper structure (the oversized class
  over the long method it causes).
- Shotgun surgery and divergent change are cured by a campaign, not a move: give the concept a
  home, then keep moving pieces into it. Don't stop after the first move.
- Slowness is not a smell; that is performance work, measured separately.

## Names

- A reader who hasn't seen the body should predict it from the name, or from the call site read
  aloud.
- Use the caller's vocabulary. Storage, wire format and vendor stay out of public names.
- A name that understates a side effect is a lie (a getter that writes, a validator that mutates):
  split the effect out or rename to the truth.
- A name that won't come means a wrong abstraction: an "and" in a function name, a type that needs
  many words, a parameter you keep calling `data`. Split it or introduce a value type; don't reach
  for a thesaurus. A generic-noun class (`Manager`, `Util`) is usually an oversized one, and
  renaming it without splitting is cosmetic.

## Stop when

- Past about four files or 200 lines since the last commit, the work has become a redesign:
  commit the green part and raise the design question.
- When a feature idea comes up, write it down, finish or revert the current move, then switch.
- With no clearly right next move, go back to diagnosis.
