Load `doc-drift` and `design-rubric` before every commit, `error-modeling` when the commit adds a
failure path, and `commit-sequencing` when it moves code.

When two shapes fit the next test, drive both to green and keep the one whose test was easier to
write.

Stop conditions: two public entry points would give different answers for the same inputs; two
written rules conflict and no precedence settles it; an invariant test would have to be weakened,
narrowed, skipped or worked around. In system-level work, a change on the breaking list in
`commit-sequencing` ("What forces expand/contract") is the first.

If you meet a stop condition or an open trade-off, end your installment. Your report opens with a
`Blocked:` block: the condition, the question, the options with your pick first, the proposed diff,
and the commits you made before stopping. Commit green work only, nothing for the blocked step.

Your report's first line is `Status: done`, `Status: failed` or `Status: blocked`, followed for
blocked by the `Blocked:` block.
