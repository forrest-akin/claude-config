# Interface design example

An access-control module from the report "Abstractions at Agent Speed" (5–6 November 2026), with
two public functions, `can()` and `api.handle_check()`, that other services call. The report's
final arm ran with these sections plus rules for old code; 3 of 3 chains finished with both
functions enforcing all five rules.

## Invariants, precedence and stop conditions

```markdown
## Design invariants for access control

1. **One evaluation.** Every question about access (may they? why? what may they do?) is answered by the same evaluation. No rule is written down twice.
2. **Decisions are values.** Evaluation returns a decision that carries its reason. Booleans are derived from a decision at the edge, never the reverse.
3. **Inputs are explicit.** Evaluation depends only on its arguments. It reads no clock, settings, or module state. Defaults such as the current time are resolved in `api.py` and passed in.
4. **The boundary translates.** `api.py` turns request dicts into domain types and decisions back into dicts. Domain code never handles request dicts.
5. **Narrow interfaces.** No boolean or mode parameters on functions that new code calls. When a function wants a fourth argument, the arguments want to become a type.

## When agreements collide

- Invariant 1 outranks invariant 5. If keeping every public entry point on the one evaluation means an entry point needs more inputs, give those inputs a type; do not leave the entry point behind.
- `tests/test_doors_agree.py` and `tests/scenarios.py` hold invariant 1. Every new request field and every new rule gets examples in `REQUESTS`. Do not keep examples out of that list, and do not narrow that test.

## Stop and ask

Do not settle these yourself. Leave the work in a state that passes the tests, and put the question at the top of your summary:

- an existing public function would end up giving a different answer from another public function for the same user, resource and action;
- two agreements conflict and the order above does not settle it;
- an invariant test would have to be weakened, skipped or worked around.
```

## Agreement test with generated cases

```python
# tests/test_doors_agree_generated.py
"""Invariant: one answer to "may this user do this?", whichever public function is asked.

The cases are generated, not listed, so nobody chooses which ones count.
"""
import itertools

import pytest

from workspace.access import can
from workspace.api import handle_check

NOW = 1_800_000_000
ROLES = ["admin", "editor", "viewer", "guest"]
ACTIONS = ["read", "write", "delete", "share"]
GRANT = {"user_id": "u1", "resource_id": "r1", "actions": ACTIONS, "expires_at": NOW + 60}

# Once you have decided what each old flag should mean for the new rules,
# add the flags to this product as well. Nothing here covers them yet.


def requests():
    for role, suspended, owner, locked, blocked, grants, action in itertools.product(
        ROLES, [False, True], [None, "u1", "u2"], [False, True], [[], ["u1"]], [[], [GRANT]], ACTIONS
    ):
        yield {
            "user": {"id": "u1", "role": role, "suspended": suspended},
            "resource": {"id": "r1", "owner_id": owner, "locked": locked, "blocked_user_ids": blocked},
            "action": action,
            "grants": grants,
            "now": NOW,
        }


@pytest.mark.parametrize("request_", requests())
def test_every_door_gives_the_same_answer(request_):
    answer = handle_check(request_)["allowed"]
    asked_directly = can(
        request_["user"], request_["action"], request_["resource"],
        grants=request_["grants"], now=request_["now"],
    )
    assert asked_directly is answer
```
