# Interface: <area>

## 1. Signatures and types

One line of contract per signature or type. No bodies.

- `<signature or type>` — <one-line contract> — <name>, <YYYY-MM-DD>

## 2. Invariants

1. <invariant> — <name>, <YYYY-MM-DD>

## 3. Throwaway callers

Two callers written against the signatures for two different uses.

- <first use>: <caller>; awkward to write: <anything awkward, or nothing> — <name>, <YYYY-MM-DD>
- <second use>: <caller>; awkward to write: <anything awkward, or nothing> — <name>, <YYYY-MM-DD>

## 4. Precedence

- <rule> wins over <rule> when <they collide> — <name>, <YYYY-MM-DD>

## 5. Frozen paths

- `<path>` — <name>, <YYYY-MM-DD>

## 6. Stop conditions

Stop conditions: an existing public function would answer differently from today, or from another
public entry point, for the same inputs, unless the plan names that change; two written rules
conflict and no precedence settles it; an existing test's assertion would be weakened, narrowed,
skipped, worked around or changed, unless the behaviour change is the task and the test follows it
(say so in one line of the report). In system-level work, a change on the breaking list in
`commit-sequencing` ("What forces expand/contract") is the first.

Still open:

- <open item> — <name>, <YYYY-MM-DD>

## 7. Standing rules

- Old code is not an example.
- A function with a shape the invariants forbid is brought into line first, as its own
  behaviour-preserving commit with existing tests green, before it is extended. An invariant
  breach is a red test or a stop, never a tidy.
- Tidy-first outranks smallest diff.
