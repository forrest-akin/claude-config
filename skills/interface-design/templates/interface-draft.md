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

Stop conditions: two public entry points would give different answers for the same inputs; two
written rules conflict and no precedence settles it; an invariant test would have to be weakened,
narrowed, skipped or worked around. In system-level work, a change on the breaking list in
`commit-sequencing` ("What forces expand/contract") is the first.

Still open:

- <open item> — <name>, <YYYY-MM-DD>

## 7. Standing rules

- Old code is not an example.
- A function with a shape the invariants forbid is brought into line first, as its own
  behaviour-preserving commit with existing tests green, before it is extended. An invariant
  breach is a red test or a stop, never a tidy.
- Tidy-first outranks smallest diff.
