#!/bin/bash
# Runs lint-extension over every skill in this repo; any finding fails.
# Usage: lint-skills.test.sh [skills dir]  (defaults to this repo's skills/)
set -u
here="$(cd "$(dirname "$0")" && pwd)"
repo="$(dirname "$here")"
dir="${1:-$repo/skills}"
if python3 "$repo/skills/extension-authoring/bin/lint-extension" "$dir"; then
  echo "ok   lint-extension ${dir#"$repo"/}"
else
  echo "FAIL lint-extension ${dir#"$repo"/}"
  exit 1
fi
