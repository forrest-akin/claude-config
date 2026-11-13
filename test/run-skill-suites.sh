#!/bin/bash
# Runs every skills/*/tests suite: its test*.py files by unittest discovery, and each *.sh file as
# one test. Usage: run-skill-suites.sh [repo-root]
# Exits 0 when every suite passes, 1 when a suite fails or runs no test, 2 when there is no suite.
set -u
root="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$root" || exit 2

# Python before 3.12 exits 0 from `python3 -m unittest` when no test ran, so the count leaves on fd 3.
discover='
import os, sys, unittest
result = unittest.TextTestRunner().run(unittest.defaultTestLoader.discover(sys.argv[1]))
os.write(3, b"%d" % result.testsRun)
sys.exit(not result.wasSuccessful())
'

# Each runner prints its suite's output on fd 4, the count it ran on stdout, and fails when a test does.
python_tests() {
  ls "$1"/test*.py > /dev/null 2>&1 || { echo 0; return 0; }
  python3 -B -u -c "$discover" "$1" 3>&1 >&4 2>&4
}
shell_tests() {
  ran=0; status=0
  for test in "$1"/*.sh; do
    [ -f "$test" ] || continue
    ran=$((ran + 1))
    bash "$test" >&4 2>&4 || status=1
  done
  echo "$ran"; return "$status"
}

suites=0; failed=0; total=0
exec 4>&1
for dir in skills/*/tests; do
  [ -d "$dir" ] || continue
  suites=$((suites + 1))
  echo "== $dir"
  python_ran=$(python_tests "$dir"); python_status=$?
  shell_ran=$(shell_tests "$dir"); shell_status=$?
  ran=$((${python_ran:-0} + shell_ran))
  total=$((total + ran))
  if [ "$python_status" -ne 0 ] || [ "$shell_status" -ne 0 ] || [ "$ran" -eq 0 ]; then
    failed=$((failed + 1))
    echo "FAILED $dir ($ran tests ran)" >&2
  fi
done

if [ "$suites" -eq 0 ]; then
  echo "run-skill-suites found no skills/*/tests directory under $root" >&2
  exit 2
fi
echo "skill suites: $total tests in $suites suites, $failed failed"
[ "$failed" -eq 0 ]
