#!/bin/bash
# Feeds hooks/diff-size.sh PostToolUse JSON naming files in temp repos and checks its exact output.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
hook="$(dirname "$here")/hooks/diff-size.sh"
fails=0
root="$(mktemp -d)"; trap 'rm -rf "$root"' EXIT
check() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: expected '$2' got '$3'"; fails=$((fails+1)); fi; }

# repo <name>: a repo with one committed 10-line file, a.txt
repo() {
  r="$root/$1"; mkdir -p "$r"
  git -C "$r" init -q; seq 10 > "$r/a.txt"; git -C "$r" add a.txt
  git -C "$r" -c user.name=t -c user.email=t@t commit -q -m base
}
run() { jq -cn --arg f "$1" '{hook_event_name:"PostToolUse",tool_name:"Edit",tool_input:{file_path:$f}}' | bash "$hook" 2>&1; }
said() { echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"additionalContext\":\"Uncommitted: $1 files, $2 lines.\"}}"; }

repo small; seq 20 > "$root/small/a.txt"
check "10 changed lines says nothing" "" "$(run "$root/small/a.txt")"

repo at200; seq 200 > "$root/at200/b.txt"
check "exactly 200 lines says nothing" "" "$(run "$root/at200/b.txt")"

repo tracked; seq 211 > "$root/tracked/a.txt"
check "over 200 changed lines in a tracked file says the size" "$(said 1 201)" "$(run "$root/tracked/a.txt")"

repo untracked; seq 250 > "$root/untracked/new.txt"
check "untracked lines count" "$(said 1 250)" "$(run "$root/untracked/new.txt")"

repo files; for f in b c d e; do echo x > "$root/files/$f.txt"; done; echo y >> "$root/files/a.txt"
check "five files says the size" "$(said 5 5)" "$(run "$root/files/b.txt")"
check "four files says nothing" "" "$(rm "$root/files/e.txt"; run "$root/files/b.txt")"

mkdir -p "$root/plain"; seq 300 > "$root/plain/x.txt"
check "outside a repo says nothing" "" "$(run "$root/plain/x.txt")"
check "outside a repo exits 0" 0 "$(run "$root/plain/x.txt" >/dev/null; echo $?)"

mkdir -p "$root/empty"; git -C "$root/empty" init -q; seq 300 > "$root/empty/x.txt"
check "repo with no commit says nothing" "" "$(run "$root/empty/x.txt")"
check "no file_path says nothing" "" "$(echo '{"tool_name":"Edit"}' | bash "$hook" 2>&1)"

repo logs; mkdir -p "$root/logs/.claude/work"; seq 300 > "$root/logs/.claude/work/run.log"; echo y >> "$root/logs/a.txt"
check "untracked .claude/ lines do not count" "" "$(run "$root/logs/a.txt")"

[ "$fails" -eq 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
