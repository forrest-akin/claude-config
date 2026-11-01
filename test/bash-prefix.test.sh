#!/bin/bash
# Feeds hooks/bash-prefix.sh PreToolUse JSON and checks its exact output.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
hook="$(dirname "$here")/hooks/bash-prefix.sh"
fails=0
check() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: expected '$2' got '$3'"; fails=$((fails+1)); fi; }

run() { jq -cn --arg c "$1" '{hook_event_name:"PreToolUse",tool_name:"Bash",tool_input:{command:$c}}' | bash "$hook" 2>&1; }
denied() {
  jq -cn --arg r "Command starts with \`$1\`. ~/.claude/CLAUDE.md \"Bash commands\": Put literal absolute paths in each command: no \`cd <dir> &&\` prefix and no \`VAR=<path>;\` shorthand." \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
}

check "VAR= shorthand denied" "$(denied W=)" "$(run 'W=/x; ls')"
check "cd prefix denied" "$(denied cd)" "$(run 'cd /x && ls')"
check "bare cd denied" "$(denied cd)" "$(run 'cd')"
check "leading whitespace, VAR= denied" "$(denied FOO=)" "$(run ' FOO=1 cmd')"

check "ls allowed" "" "$(run 'ls')"
check "git -C allowed" "" "$(run 'git -C /x status')"
check "assignment in an argument allowed" "" "$(run 'echo a=b')"
check "export allowed" "" "$(run 'export FOO=1')"
check "cdk allowed" "" "$(run 'cdk deploy')"
check "cd on a later line allowed" "" "$(run "$(printf 'ls\ncd /x')")"
check "non-Bash tool allowed" "" "$(jq -cn '{hook_event_name:"PreToolUse",tool_name:"PowerShell",tool_input:{command:"cd /x"}}' | bash "$hook" 2>&1)"

[ "$fails" -eq 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
