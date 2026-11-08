#!/usr/bin/env bash
# Tests for reclaim-apply.sh's fail-closed guards, against a temp HOME and temp trees.

set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPLY="$HERE/../bin/reclaim-apply.sh"

PASS=0; FAIL=0
check() { # check <name> <expected> <actual>
  if [ "$2" = "$3" ]; then PASS=$((PASS+1))
  else FAIL=$((FAIL+1)); printf 'FAIL: %s\n  expected: %s\n  actual:   %s\n' "$1" "$2" "$3"; fi
}

T="$(mktemp -d)"; trap 'chmod -R u+w "$T"; rm -rf "$T"' EXIT
export HOME="$T/home"; mkdir -p "$HOME"
PLAN="$T/plan.tsv"

plan() { # plan <category> <path>... — one delete row per path
  local cat="$1"; shift
  printf 'action\tsize_kb\tcategory\treason\tpath\n' > "$PLAN"
  for p in "$@"; do printf 'delete\t10\t%s\tstale\t%s\n' "$cat" "$p" >> "$PLAN"; done
}
apply() { bash "$APPLY" "$PLAN" --log "$T/log" "$@" 2>&1; }
exists() { [ -e "$1" ] && echo yes || echo no; }

mkdir -p "$T/app/node_modules"
plan bogus "$T/app/node_modules"
out="$(apply --confirm)"
check "unknown category is not deleted" yes "$(exists "$T/app/node_modules")"
check "unknown category is refused" 1 "$(printf '%s\n' "$out" | grep -c "REFUSING unknown category 'bogus'")"

plan build / "$HOME" "$HOME/"
out="$(apply)"
check "root and HOME are refused" 3 "$(printf '%s\n' "$out" | grep -c 'REFUSING unsafe path')"
check "root and HOME are never planned" 0 "$(printf '%s\n' "$out" | grep -c 'would delete')"

plan node_modules "$T/gone/node_modules"
out="$(apply --confirm)"
check "vanished path is skipped" 1 "$(printf '%s\n' "$out" | grep -c 'skipped 1 row')"
check "vanished path is not counted" 1 "$(printf '%s\n' "$out" | grep -c 'deleted 0 dir')"

plan node_modules "$T/app/node_modules"
out="$(apply)"
check "dry run deletes nothing" yes "$(exists "$T/app/node_modules")"
check "dry run names the row" 1 "$(printf '%s\n' "$out" | grep -c "would delete .*$T/app/node_modules")"

out="$(apply --confirm)"
check "confirm deletes a valid row" no "$(exists "$T/app/node_modules")"
check "confirm counts the deletion" 1 "$(printf '%s\n' "$out" | grep -c 'deleted 1 dir')"

mkdir -p "$T/locked/node_modules"; touch "$T/locked/node_modules/f"; chmod 555 "$T/locked"
plan node_modules "$T/locked/node_modules"
out="$(apply --confirm)"
check "failed removal is skipped" 1 "$(printf '%s\n' "$out" | grep -c 'skipped 1 row')"
check "failed removal is not counted" 1 "$(printf '%s\n' "$out" | grep -c 'deleted 0 dir')"
check "failed removal is named" 1 "$(printf '%s\n' "$out" | grep -c "could not remove $T/locked/node_modules")"

printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
