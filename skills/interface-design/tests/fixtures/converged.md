# Interface: access

## 1. Signatures and types

One line of contract per signature or type. No bodies.

- `authorize(request: AccessRequest): AccessDecision` — total over every request — Ada, 2026-11-01

## 2. Invariants

1. Every entry point returns the decision `authorize` returns for the same request — Ada, 2026-11-01
2. A revoked grant denies on every path — Ada, 2026-11-01

## 3. Throwaway callers

Two callers written against the signatures for two different uses.

- HTTP middleware: `authorize(fromHttp(req))`; awkward to write: nothing — Ada, 2026-11-01
- Batch export: `rows.filter(r => authorize(fromRow(r)).allowed)`; awkward to write:
  nothing — Ada, 2026-11-01

## 4. Precedence

- An explicit deny wins over a role grant when both match — Ada, 2026-11-01

## 5. Frozen paths

- `src/access/index.ts` — Ada, 2026-11-01

## 6. Stop conditions

Stop conditions: an existing public function would answer differently from today, or from another
public entry point, for the same inputs, unless the plan names that change; two written rules
conflict and no precedence settles it; an existing test's assertion would be weakened, narrowed,
skipped, worked around or changed, unless the behaviour change is the task and the test follows it
(say so in one line of the report). In system-level work, a change on the breaking list in
`commit-sequencing` ("What forces expand/contract") is the first.

Still open:

- Whether service accounts get their own request type — Ada, 2026-11-01

## 7. Standing rules

- Old code is not an example.
- A function with a shape the invariants forbid is brought into line first, as its own
  behaviour-preserving commit with existing tests green, before it is extended. An invariant
  breach is a red test or a stop, never a tidy.
- Tidy-first outranks smallest diff.
