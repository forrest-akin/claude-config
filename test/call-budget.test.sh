#!/bin/bash
# Feeds hooks/call-budget.sh hook JSON naming fixture transcripts and checks its exact output.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
hook="$(dirname "$here")/hooks/call-budget.sh"
fails=0
root="$(mktemp -d)"; trap 'rm -rf "$root"' EXIT
check() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: expected '$2' got '$3'"; fails=$((fails+1)); fi; }

# transcript <file> <first-prompt content as JSON> <tool calls>
transcript() {
  mkdir -p "$(dirname "$1")"
  jq -cn --argjson c "$2" '{type:"user",message:{role:"user",content:$c}}' > "$1"
  echo '{"type":"api-request","message":{"content":[{"type":"tool_use","id":"x","name":"Bash"}]}}' >> "$1"
  i=0
  while [ "$i" -lt "$3" ]; do
    echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"t"},{"type":"tool_use","id":"t'"$i"'","name":"Bash","input":{}}]}}' >> "$1"
    echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t'"$i"'","content":"ok"}]}}' >> "$1"
    i=$((i+1))
  done
}
run() { jq -cn --arg t "$1" --arg a "${2:-}" '{hook_event_name:"PostToolUse",tool_name:"Bash",transcript_path:$t} + (if $a == "" then {} else {agent_id:$a} end)' | bash "$hook" 2>&1; }
said() { echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"additionalContext\":\"Tool calls so far: $1 of budget $2.\"}}"; }

about='"Do the work. About 10 calls; stop at the budget."'
for n in 7 8 9 10 12; do transcript "$root/about$n.jsonl" "$about" "$n"; done
check "below 80% says nothing" "" "$(run "$root/about7.jsonl")"
check "at 80% says the count" "$(said 8 10)" "$(run "$root/about8.jsonl")"
check "between 80% and 100% says nothing" "" "$(run "$root/about9.jsonl")"
check "at 100% says the count" "$(said 10 10)" "$(run "$root/about10.jsonl")"
check "over budget says the count" "$(said 12 10)" "$(run "$root/about12.jsonl")"

hard='[{"type":"text","text":"Brief."},{"type":"text","text":"Hard budget: 12 tool calls."}]'
transcript "$root/hard9.jsonl" "$hard" 9
transcript "$root/hard10.jsonl" "$hard" 10
check "text blocks, 80% rounds up: 9 of 12 says nothing" "" "$(run "$root/hard9.jsonl")"
check "text blocks, 10 of 12 says the count" "$(said 10 12)" "$(run "$root/hard10.jsonl")"

transcript "$root/tool44.jsonl" '"About 55 tool calls; report at the budget."' 44
check "About N tool calls is a budget" "$(said 44 55)" "$(run "$root/tool44.jsonl")"

tab="$(printf '\t')"; k=0
while IFS="$tab" read -r phrase n; do
  k=$((k+1)); prompt="$(jq -n --arg p "$phrase" '$p')"
  if [ -n "$n" ]; then
    transcript "$root/phrase$k.jsonl" "$prompt" "$n"
    check "'$phrase' is a budget of $n" "$(said "$n" "$n")" "$(run "$root/phrase$k.jsonl")"
  else
    transcript "$root/phrase$k.jsonl" "$prompt" 50
    check "'$phrase' is no budget" "" "$(run "$root/phrase$k.jsonl")"
  fi
done < "$here/fixtures/budget-phrasings.txt"

transcript "$root/none.jsonl" '"No budget here."' 50
check "no budget says nothing" "" "$(run "$root/none.jsonl")"

check "missing transcript says nothing" "" "$(run "$root/missing.jsonl")"
check "missing transcript exits 0" 0 "$(run "$root/missing.jsonl" >/dev/null; echo $?)"

transcript "$root/session.jsonl" '"Main session, no budget."' 3
transcript "$root/session/subagents/workflows/wf_1/agent-abc.jsonl" "$about" 10
check "subagent counts its own transcript" "$(said 10 10)" "$(run "$root/session.jsonl" abc)"
check "subagent handed its own transcript" "$(said 10 10)" "$(run "$root/session/subagents/workflows/wf_1/agent-abc.jsonl" abc)"

[ "$fails" -eq 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
