#!/bin/bash
# Checks that every copy of the three stop conditions carries each clause word for word.
# Usage: stop-conditions.test.sh [file...]  (defaults to the copies in this repo)
set -u
here="$(cd "$(dirname "$0")" && pwd)"
repo="$(dirname "$here")"
fails=0
check() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: expected '$2' got '$3'"; fails=$((fails+1)); fi; }

if [ "$#" -eq 0 ]; then
  set -- "$repo/skills/workflow-design/SKILL.md" \
    "$repo/skills/workflow-design/templates/implementer-block.md" \
    "$repo/skills/interface-design/example.md"
fi

for f in "$@"; do
  text="$(tr '\n' ' ' < "$f" | tr -s ' \t' ' ')"
  for clause in \
    'two public entry points would give different answers for the same inputs' \
    'two written rules conflict and no precedence settles it' \
    'an invariant test would have to be weakened, narrowed, skipped or worked around'; do
    found="$(printf '%s\n' "$text" | grep -c -F "$clause")"
    check "${f#"$repo"/}: $clause" yes "$([ "$found" -ge 1 ] && echo yes || echo no)"
  done
done

[ "$fails" -eq 0 ]
