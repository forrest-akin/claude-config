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

Stop conditions: two public entry points would give different answers for the same inputs; two
written rules conflict and no precedence settles it; an invariant test would have to be weakened,
narrowed, skipped or worked around. In system-level work, a change on the breaking list in
`commit-sequencing` ("What forces expand/contract") is the first.

Still open:

- Whether service accounts get their own request type — Ada, 2026-11-01

## 7. Standing rules

- Old code is not an example.
- A function that breaks an invariant is brought into line first, as its own
  behaviour-preserving commit with existing tests green, before it is extended.
- Tidy-first outranks smallest diff.
