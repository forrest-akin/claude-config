#!/bin/bash
# Checks that hooks/hooks.json registers the three hooks with commands that run.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
root="$(dirname "$here")"
json="$root/hooks/hooks.json"
fails=0
check() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: expected '$2' got '$3'"; fails=$((fails+1)); fi; }

triples() { jq -r '.hooks | to_entries[] | .key as $e | .value[] | (.matcher // "") as $m | .hooks[] | "\($e)|\($m)|\(.command | sub(".*/"; ""))"' "$json" 2>&1; }

check "three registrations in order" "$(printf 'PreToolUse|Bash|bash-prefix.sh\nPostToolUse||call-budget.sh\nPostToolUse|Edit|Write|diff-size.sh')" "$(triples)"

commands() { jq -r '.hooks[][].hooks[].command' "$json"; }
resolve() { local c="${1/\$\{CLAUDE_PLUGIN_ROOT\}/$root}"; printf '%s' "${c//\"/}"; }
while read -r c; do
  p="$(resolve "$c")"
  check "$c is an executable file" yes "$([ -f "$p" ] && [ -x "$p" ] && echo yes || echo no)"
done < <(commands)

prefix_cmd="$(commands | grep bash-prefix)"
input='{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"cd /x"}}'
decision="$(cd / && printf '%s' "$input" | env CLAUDE_PLUGIN_ROOT="$root" sh -c "$prefix_cmd" 2>&1 | jq -r .hookSpecificOutput.permissionDecision 2>&1)"
check "bash-prefix runs from / under CLAUDE_PLUGIN_ROOT and denies cd" deny "$decision"

[ "$fails" -eq 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
