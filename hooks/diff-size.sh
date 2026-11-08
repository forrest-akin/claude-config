#!/bin/bash
# PostToolUse (Edit|Write): on every edit while the edited file's repo has over 200 uncommitted lines or 4 files, says the size.
# Untracked files under .claude/ are process logs and do not count.
# Hook facts from `curl -sL https://code.claude.com/docs/en/hooks.md` (2026-11-07): the matcher "Edit|Write" is tested
# against tool_name; tool_input.file_path is absolute for Write and Edit; hookSpecificOutput.additionalContext reaches the model.
set -u
file="$(jq -r '.tool_input.file_path // empty')"
[ -n "$file" ] || exit 0
repo="$(git -C "$(dirname "$file")" rev-parse --show-toplevel 2>/dev/null)" || exit 0
tracked="$(git -C "$repo" diff --numstat HEAD 2>/dev/null)" || exit 0
untracked="$(git -C "$repo" ls-files --others --exclude-standard -- ':(exclude).claude/')"
files=$(( $(printf '%s' "$tracked" | grep -c .) + $(printf '%s' "$untracked" | grep -c .) ))
lines=$(( $(printf '%s\n' "$tracked" | awk '$1 != "-" { n += $1 + $2 } END { print n + 0 }') \
  + $(printf '%s' "$untracked" | tr '\n' '\0' | xargs -0 -I{} cat "$repo/{}" | wc -l) ))
[ "$lines" -gt 200 ] || [ "$files" -gt 4 ] || exit 0
jq -cn --arg msg "Uncommitted: $files files, $lines lines." '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $msg}}'
