#!/bin/bash
# Symlinks CLAUDE.md, every skills/* and every hooks/*.sh into ~/.claude. Replaces nothing it did not create.
# Registers call-budget.sh on PostToolUse and bash-prefix.sh on PreToolUse (Bash) in ~/.claude/settings.json, adding each entry once.
set -u
repo="$(cd "$(dirname "$0")" && pwd)"
dest="$HOME/.claude"

pairs=()
[ -f "$repo/CLAUDE.md" ] && pairs+=("$repo/CLAUDE.md|$dest/CLAUDE.md")
for dir in "$repo"/skills/*/; do
  [ -d "$dir" ] || continue
  name="$(basename "$dir")"
  pairs+=("$repo/skills/$name|$dest/skills/$name")
done
for file in "$repo"/hooks/*.sh; do
  [ -f "$file" ] || continue
  pairs+=("$file|$dest/hooks/$(basename "$file")")
done

bad=0
for pair in ${pairs[@]+"${pairs[@]}"}; do
  from="${pair%%|*}"; to="${pair##*|}"
  if [ -e "$to" ] || [ -L "$to" ]; then
    [ "$(readlink "$to")" = "$from" ] || { echo "refusing: $to exists and is not a link to $from" >&2; bad=1; }
  fi
done
settings="$dest/settings.json"
if [ -e "$settings" ] && ! jq empty "$settings" 2>/dev/null; then
  echo "refusing: $settings is not valid JSON" >&2; bad=1
fi
[ "$bad" -eq 0 ] || exit 1

for pair in ${pairs[@]+"${pairs[@]}"}; do
  from="${pair%%|*}"; to="${pair##*|}"
  [ -L "$to" ] && continue
  mkdir -p "$(dirname "$to")"
  ln -s "$from" "$to"
  echo "linked $to"
done

# name|event|matcher
hook_events='call-budget.sh|PostToolUse|
bash-prefix.sh|PreToolUse|Bash'
json="$(cat "$settings" 2>/dev/null || echo '{}')"
for file in "$repo"/hooks/*.sh; do
  [ -f "$file" ] || continue
  name="$(basename "$file")"
  row="$(printf '%s\n' "$hook_events" | awk -F'|' -v n="$name" '$1 == n')"
  [ -n "$row" ] || { echo "unregistered: $name"; continue; }
  IFS='|' read -r _ event matcher <<<"$row"
  command="\$HOME/.claude/hooks/$name"
  jq -e --arg e "$event" --arg c "$command" 'any(.hooks[$e][]?.hooks[]?; .command == $c)' <<<"$json" >/dev/null && continue
  json="$(jq --arg e "$event" --arg m "$matcher" --arg c "$command" \
    '.hooks[$e] += [{matcher: $m, hooks: [{type: "command", command: $c}]}]' <<<"$json")"
done
mkdir -p "$dest"
[ "$json" = "$(cat "$settings" 2>/dev/null)" ] || printf '%s\n' "$json" > "$settings"
