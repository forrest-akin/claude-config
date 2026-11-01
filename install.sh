#!/bin/bash
# Symlinks CLAUDE.md, every skills/* and every hooks/*.sh into ~/.claude. Replaces nothing it did not create.
# Hooks run once registered in ~/.claude/settings.json; README.md shows the entries.
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
[ "$bad" -eq 0 ] || exit 1

for pair in ${pairs[@]+"${pairs[@]}"}; do
  from="${pair%%|*}"; to="${pair##*|}"
  [ -L "$to" ] && continue
  mkdir -p "$(dirname "$to")"
  ln -s "$from" "$to"
  echo "linked $to"
done
