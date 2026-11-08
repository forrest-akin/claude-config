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
  mkdir -p "$repo/skills/alpha" "$repo/skills/beta" "$repo/hooks" "$home"
  echo a > "$repo/skills/alpha/SKILL.md"; echo b > "$repo/skills/beta/SKILL.md"
  echo g > "$repo/hooks/gamma.sh"; echo cb > "$repo/hooks/call-budget.sh"; echo bp > "$repo/hooks/bash-prefix.sh"; echo ds > "$repo/hooks/diff-size.sh"
  echo c > "$repo/CLAUDE.md"
  cp "$src" "$repo/install.sh"
}
run() { HOME="$home" bash "$repo/install.sh" >"$tmp/out" 2>&1; echo $?; }
entries() { jq -c --arg e "$1" '.hooks[$e]' "$home/.claude/settings.json" 2>&1; }
entry() { echo "{\"matcher\":\"$1\",\"hooks\":[{\"type\":\"command\",\"command\":\"\$HOME/.claude/hooks/$2\"}]}"; }

fixture
check "first run exits 0" 0 "$(run)"
check "CLAUDE.md linked" "$repo/CLAUDE.md" "$(readlink "$home/.claude/CLAUDE.md")"
check "skill alpha linked" "$repo/skills/alpha" "$(readlink "$home/.claude/skills/alpha")"
check "skill beta linked" "$repo/skills/beta" "$(readlink "$home/.claude/skills/beta")"
check "hook gamma linked" "$repo/hooks/gamma.sh" "$(readlink "$home/.claude/hooks/gamma.sh")"
check "hook gamma with no row named unregistered" 1 "$(grep -c -x 'unregistered: gamma.sh' "$tmp/out")"
check "call-budget and diff-size (Edit|Write) registered on PostToolUse" "[$(entry "" call-budget.sh),$(entry "Edit|Write" diff-size.sh)]" "$(entries PostToolUse)"
check "bash-prefix registered on PreToolUse for Bash" "[$(entry Bash bash-prefix.sh)]" "$(entries PreToolUse)"
check "second run exits 0" 0 "$(run)"
check "second run keeps link" "$repo/skills/alpha" "$(readlink "$home/.claude/skills/alpha")"
check "second run registers call-budget and diff-size once" "[$(entry "" call-budget.sh),$(entry "Edit|Write" diff-size.sh)]" "$(entries PostToolUse)"
check "second run registers bash-prefix once" "[$(entry Bash bash-prefix.sh)]" "$(entries PreToolUse)"

fixture
mkdir -p "$home/.claude"
notify='{"matcher":"","hooks":[{"type":"command","command":"$HOME/.claude/hooks/claude-notify.sh"}]}'
echo "{\"model\":\"opus\",\"hooks\":{\"Notification\":[$notify]}}" > "$home/.claude/settings.json"
check "existing settings exits 0" 0 "$(run)"
check "existing Notification entry kept" "[$notify]" "$(entries Notification)"
check "unrelated key kept" opus "$(jq -r .model "$home/.claude/settings.json")"
check "existing settings gains call-budget and diff-size" "[$(entry "" call-budget.sh),$(entry "Edit|Write" diff-size.sh)]" "$(entries PostToolUse)"
real="$tmp/dotfiles-settings.json"; mv "$home/.claude/settings.json" "$real"; ln -s "$real" "$home/.claude/settings.json"; touch -t 202001010000 "$real"
check "linked settings exits 0" 0 "$(run)"
check "linked settings stays a link" "$real" "$(readlink "$home/.claude/settings.json")"
check "settings with nothing to add is not rewritten" 202001010000 "$(stat -f %Sm -t %Y%m%d%H%M "$real")"

fixture
run >/dev/null; rm -r "$repo/skills/beta"; ln -s /elsewhere "$home/.claude/skills/foreign"
check "removed skill exits 0" 0 "$(run)"
check "removed skill's link removed" no "$([ -L "$home/.claude/skills/beta" ] && echo yes || echo no)"
check "removed skill's link printed" 1 "$(grep -c -x "unlinked $home/.claude/skills/beta" "$tmp/out")"
check "dead link outside the repo kept" /elsewhere "$(readlink "$home/.claude/skills/foreign")"
check "live link left alone" 0 "$(grep -c "alpha" "$tmp/out")"

fixture
mkdir -p "$home/.claude"; echo '{not json' > "$home/.claude/settings.json"
check "invalid settings exits non-zero" 1 "$(run)"
check "invalid settings untouched" '{not json' "$(cat "$home/.claude/settings.json")"
check "invalid settings named" 1 "$(grep -c "$home/.claude/settings.json" "$tmp/out")"

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

fixture
mkdir -p "$home/.claude/hooks"; echo mine > "$home/.claude/hooks/gamma.sh"
check "existing hook exits non-zero" 1 "$(run)"
check "existing hook untouched" mine "$(cat "$home/.claude/hooks/gamma.sh")"

[ "$fails" -eq 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
