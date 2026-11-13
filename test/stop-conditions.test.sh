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
    "$repo/skills/interface-design/example.md" \
    "$repo/skills/interface-design/templates/interface-draft.md"
fi

for f in "$@"; do
  text="$(tr '\n' ' ' < "$f" | tr -s ' \t' ' ')"
  for clause in \
    'an existing public function would answer differently from today, or from another public entry point, for the same inputs, unless the plan names that change' \
    'two written rules conflict and no precedence settles it' \
    "an existing test's assertion would be weakened, narrowed, skipped, worked around or changed, unless the behaviour change is the task and the test follows it (say so in one line of the report)"; do
    found="$(printf '%s\n' "$text" | grep -c -F "$clause")"
    check "${f#"$repo"/}: $clause" yes "$([ "$found" -ge 1 ] && echo yes || echo no)"
  done
done

[ "$fails" -eq 0 ]
