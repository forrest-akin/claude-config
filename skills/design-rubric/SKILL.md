---
name: design-rubric
description: Judges a diff's design against principles and code-health smells, and blocks a commit that lowers a touched file's health or worsens its public interface. Use before each commit of production work and in design review of a diff. Not for carrying out the cure (refactoring).
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
- An accepted smell carries a comment directly above it naming the smell, the rationale and the date.
- Each cure is the move this rubric names, carried out per `refactoring`.

## Principles

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
  Question: can a test call it with arguments alone? Move: Replace Query with Parameter,
  resolving the value in the caller.
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

Smells with a measured link to defect rates and maintenance cost, from CodeScene's Code Health
research ([code-health](https://codescene.io/docs/guides/technical/code-health.html)); excess
arguments is this rubric's own.

- **Large method**: many lines in one function. Extract Function.
- **Brain method**: a large, complex function at the centre of its module's behaviour. Extract
  Function per responsibility; Split Phase.
- **Complex method**: many conditional statements (`if`, `for`, `while`) in one function.
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
- **DRY violations**: copied logic that changes together. Extract Function at the third copy.
- **Low cohesion**: LCOM4 above 1, a class whose methods form groups that share no fields.
  Extract Class per group.
- **Brain class**: a large module with many functions and at least one brain method. Extract
  Class.
- **Large assertion block**: a long run of consecutive asserts in one test. Extract a named
  assertion function.
- **Duplicated assertion block**: the same asserts copied across tests. Extract a named assertion
  function, or parameterize the test.
