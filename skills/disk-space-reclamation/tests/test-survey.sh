#!/usr/bin/env bash
# Tests for disk-survey.sh's regenerable-artifact table, against a temp root.

set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SURVEY="$HERE/../bin/disk-survey.sh"

PASS=0; FAIL=0
check() { # check <name> <expected> <actual>
  if [ "$2" = "$3" ]; then PASS=$((PASS+1))
  else FAIL=$((FAIL+1)); printf 'FAIL: %s\n  expected: %s\n  actual:   %s\n' "$1" "$2" "$3"; fi
}

T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export HOME="$T/home"; mkdir -p "$HOME"
mkdir -p "$T/root/app/build" "$T/root/app/node_modules/pkg/build"
dd if=/dev/zero of="$T/root/app/node_modules/pkg/build/f" bs=1048576 count=100 2>/dev/null

out="$(bash "$SURVEY" "$T/root" 2>/dev/null)"
row() { printf '%s\n' "$out" | awk -v p="$1" '$1==p {print $2, $3}'; }

check "a dependency's shipped build is not a project build" "0.0G 1" "$(row build)"
check "node_modules still counts its whole tree" "0.1G 1" "$(row node_modules)"

printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
