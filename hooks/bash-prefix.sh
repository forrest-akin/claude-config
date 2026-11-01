#!/bin/bash
# PreToolUse on Bash: denies a command that starts with a NAME=value assignment or cd.
set -u
cmd="$(jq -r 'select(.tool_name == "Bash") | .tool_input.command // empty')"
starts='^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*=|cd([[:space:]]|$))'
[[ $cmd =~ $starts ]] || exit 0
prefix="${BASH_REMATCH[1]%[[:space:]]}"
reason="Command starts with \`$prefix\`. ~/.claude/CLAUDE.md \"Bash commands\": Put literal absolute paths in each command: no \`cd <dir> &&\` prefix and no \`VAR=<path>;\` shorthand."
jq -cn --arg r "$reason" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
