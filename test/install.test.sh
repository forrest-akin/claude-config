#!/bin/bash
# Runs install.sh against a fixture repo and a temp HOME. Never touches the real ~/.claude.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
src="$(dirname "$here")/install.sh"
fails=0
root="$(mktemp -d)"; trap 'rm -rf "$root"' EXIT
check() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: expected '$2' got '$3'"; fails=$((fails+1)); fi; }

fixture() {
  tmp="$(mktemp -d "$root/fixture.XXXXXX")"
  repo="$tmp/repo"; home="$tmp/home"
  mkdir -p "$repo/skills/alpha" "$repo/skills/beta" "$home"
  echo a > "$repo/skills/alpha/SKILL.md"; echo b > "$repo/skills/beta/SKILL.md"
  echo c > "$repo/CLAUDE.md"
  cp "$src" "$repo/install.sh"
}
run() { HOME="$home" bash "$repo/install.sh" >"$tmp/out" 2>&1; echo $?; }

fixture
check "first run exits 0" 0 "$(run)"
check "CLAUDE.md linked" "$repo/CLAUDE.md" "$(readlink "$home/.claude/CLAUDE.md")"
check "skill alpha linked" "$repo/skills/alpha" "$(readlink "$home/.claude/skills/alpha")"
check "skill beta linked" "$repo/skills/beta" "$(readlink "$home/.claude/skills/beta")"
check "second run exits 0" 0 "$(run)"
check "second run keeps link" "$repo/skills/alpha" "$(readlink "$home/.claude/skills/alpha")"

fixture
rm "$repo/CLAUDE.md"
check "no CLAUDE.md exits 0" 0 "$(run)"
check "no CLAUDE.md, none linked" "no" "$([ -e "$home/.claude/CLAUDE.md" ] || [ -L "$home/.claude/CLAUDE.md" ] && echo yes || echo no)"

fixture
mkdir -p "$home/.claude/skills/beta"; echo mine > "$home/.claude/skills/beta/SKILL.md"
check "conflict exits non-zero" 1 "$(run)"
check "conflict names the target" 1 "$(grep -c "$home/.claude/skills/beta" "$tmp/out")"
check "conflict leaves existing dir" mine "$(cat "$home/.claude/skills/beta/SKILL.md")"
check "conflict links nothing" "no" "$([ -L "$home/.claude/skills/alpha" ] && echo yes || echo no)"

fixture
mkdir -p "$home/.claude"; echo mine > "$home/.claude/CLAUDE.md"
check "existing CLAUDE.md exits non-zero" 1 "$(run)"
check "existing CLAUDE.md untouched" mine "$(cat "$home/.claude/CLAUDE.md")"

fixture
mkdir -p "$home/.claude/skills"; ln -s /elsewhere "$home/.claude/skills/alpha"
check "foreign symlink exits non-zero" 1 "$(run)"
check "foreign symlink untouched" /elsewhere "$(readlink "$home/.claude/skills/alpha")"

[ "$fails" -eq 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
