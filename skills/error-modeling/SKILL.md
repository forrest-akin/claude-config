---
name: error-modeling
description: Decides a module's error model before its code is written - which failures are returned values in the type, which are exceptions, where each is handled, and what a handler may do. Use when about to throw from new code, when a module swallows exceptions or each caller invents its own recovery, when specifying what failures a boundary promises, or when asking "throw or return?". Not for retry and timeout mechanics, log severity, or composing result values.
---

# Error modeling

Decide the model before writing the producer.

## The split

- **Expected**: part of the function's domain; the caller must reason about it. Return it as a
  value the type system tracks (result type, sealed or tagged union).
- **Unexpected**: a broken assumption, a bug, an infrastructure catastrophe. Throw, panic or exit.
- Never the reverse. An exception for an expected failure hides the contract from the signature;
  a returned catastrophe pollutes every signature with cases no caller can handle.
- Modeling a borderline case (a dependency being down) as expected is a commitment that forces
  every caller to handle it. Say so when you make it.

## Variants

- Each variant carries structured, actionable fields, never only a message string. Fields every
  variant needs (a correlation id) live on the base.
- Callers switch on the tag exhaustively. A new variant breaking existing call sites is the point.

## Handling

- Expected errors travel as values through the core and are unwrapped exactly once, at the shell,
  into a response, event, log line or user message.
- Unexpected errors are caught only by a top-level handler that reports and never swallows.
- No silent catch. A handler converts to a modeled value or rethrows toward a layer that does.
  Log-and-continue, an empty catch and default-on-error are defects; a blind rethrow only moves
  the problem.
- Don't convert exceptions to results deep in the core; the producer should have returned the
  result.

## When returned errors are unergonomic

Pick one convention for the module (e.g. checked exceptions for expected, unchecked for
unexpected), write it down at the boundary, and apply it everywhere.
