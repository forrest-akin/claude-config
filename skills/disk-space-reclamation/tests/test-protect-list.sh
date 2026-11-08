#!/usr/bin/env bash
# Tests for protect-list.sh's exit codes and too-coarse exclusion.
# Fake ps and lsof on PATH stand in for live claude processes.

set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROTECT="$HERE/../bin/protect-list.sh"

PASS=0; FAIL=0
check() { # check <name> <expected> <actual>
  if [ "$2" = "$3" ]; then PASS=$((PASS+1))
  else FAIL=$((FAIL+1)); printf 'FAIL: %s\n  expected: %s\n  actual:   %s\n' "$1" "$2" "$3"; fi
}

T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export HOME="$T/home"; mkdir -p "$HOME" "$T/bin"
printf '#!/bin/sh\n' > "$T/bin/lsof"
fake_ps() { printf '#!/bin/sh\necho "  PID COMM"\n%s\n' "$1" > "$T/bin/ps"; chmod +x "$T/bin/ps" "$T/bin/lsof"; }
run() { PATH="$T/bin:/usr/bin:/bin" bash "$PROTECT" "$@" 2>"$T/err"; }

fake_ps ':'
run >/dev/null; code=$?
check "no live claude and nothing detected exits 0" 0 "$code"

printf '%s\n' "$T/fleet" "$T/fleet/repo" "$T/elsewhere" > "$T/extra"
out="$(run --root "$T/fleet/" --extra "$T/extra")"; code=$?
check "too-coarse run exits 0" 0 "$code"
check "only paths under the root are emitted" "$T/fleet/repo" "$out"
check "the root itself is reported too coarse" 1 "$(grep -c "scan root: $T/fleet\$" "$T/err")"

printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
