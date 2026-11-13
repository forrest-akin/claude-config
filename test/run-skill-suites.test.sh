#!/bin/bash
# Runs test/run-skill-suites.sh over fixture trees and checks its exit code and total.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
runner="$here/run-skill-suites.sh"
fails=0
root="$(mktemp -d)"; trap 'rm -rf "$root"' EXIT
check() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: expected '$2' got '$3'"; fails=$((fails+1)); fi; }

# pysuite <tree> <skill> <body>: a unittest file in the skill's tests directory
pysuite() {
  mkdir -p "$root/$1/skills/$2/tests"
  printf 'import unittest\n\n\nclass T(unittest.TestCase):\n%s\n' "$3" > "$root/$1/skills/$2/tests/test_$2.py"
}
# shsuite <tree> <skill> <exit>: a shell test in the skill's tests directory
shsuite() { mkdir -p "$root/$1/skills/$2/tests"; printf 'exit %s\n' "$3" > "$root/$1/skills/$2/tests/test-$2.sh"; }
run() { bash "$runner" "$root/$1" > "$root/$1.out" 2>&1; echo $?; }
total() { tail -n 1 "$root/$1.out"; }
passes='    def test_a(self):\n        pass\n\n    def test_b(self):\n        pass'

pysuite pass py "$(printf "$passes")"; shsuite pass sh 0
check "passing tree exits 0" 0 "$(run pass)"
check "passing tree prints the total" "skill suites: 3 tests in 2 suites, 0 failed" "$(total pass)"

pysuite failpy ok "$(printf "$passes")"
pysuite failpy bad '    def test_a(self):
        self.fail("no")'
check "failing python suite exits 1" 1 "$(run failpy)"
check "failing python suite is counted" "skill suites: 3 tests in 2 suites, 1 failed" "$(total failpy)"

pysuite failsh ok "$(printf "$passes")"; shsuite failsh bad 1
check "failing shell test exits 1" 1 "$(run failsh)"

pysuite empty ok "$(printf "$passes")"; pysuite empty none '    pass'
check "suite that runs zero tests exits 1" 1 "$(run empty)"
check "suite that runs zero tests is counted as failed" "skill suites: 2 tests in 2 suites, 1 failed" "$(total empty)"

mkdir -p "$root/nosuite/skills/a"
check "tree with no suite exits 2" 2 "$(run nosuite)"

[ "$fails" -eq 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
