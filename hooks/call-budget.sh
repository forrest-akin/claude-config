#!/bin/bash
# PostToolUse: tells an agent its tool-call count at 80% and from 100% of the budget its first prompt names.
set -u
input="$(cat)"
transcript="$(jq -r '.transcript_path // empty' <<<"$input")"
agent="$(jq -r '.agent_id // empty' <<<"$input")"
# In a subagent, transcript_path can name the main session's file (as on SubagentStop); its own is under <session>/subagents/.
if [ -n "$agent" ]; then
  case "$transcript" in
    */agent-"$agent".jsonl) ;;
    *) transcript="$(find "${transcript%.jsonl}/subagents" -name "agent-$agent.jsonl" 2>/dev/null | head -1)" ;;
  esac
fi

budget="$(jq -rn 'first(inputs | select(.type == "user")) | .message.content
  | (if type == "string" then . else map(select(.type == "text").text) | join("\n") end)
  | (capture("(budget: *(about |at most )?|about )(?<n>[0-9]+) (tool )?calls"; "i")
     // capture("hard budget: *(?<n>[0-9]+)"; "i")).n' "$transcript" 2>/dev/null)"
[ -n "$budget" ] || exit 0

count="$(jq -c 'select(.type == "assistant") | .message.content[]? | select(.type == "tool_use") | 0' "$transcript" | wc -l | tr -d ' ')"
[ "$count" -eq $(( (4 * budget + 4) / 5 )) ] || [ "$count" -ge "$budget" ] || exit 0
jq -cn --arg msg "Tool calls so far: $count of budget $budget." '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $msg}}'
