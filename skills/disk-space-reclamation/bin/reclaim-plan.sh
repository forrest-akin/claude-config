#!/usr/bin/env bash
# Produce a deletion PLAN on stdout. Deletes nothing.
#
# Output is TSV: action, size_kb, category, reason, path
# Rows with action=keep are retained in the file on purpose — the plan should
# show what was spared and why, so a reviewer can audit the protection logic
# rather than trusting it.
#
# Scope is deliberately narrow: per-project regenerable build artifacts only.
# Shared global caches (~/.m2, ~/.npm, ~/.gradle) are never planned, because they
# cannot be partitioned per-project and any live session may depend on them.

set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../lib/select.sh"

ROOT="$HOME"
MIN_AGE_DAYS=7
DEPTH=7
EXTRA=""
PATTERNS="node_modules target build dist .next out __pycache__ .pytest_cache"

usage() {
  cat <<'USAGE'
usage: reclaim-plan.sh [--root DIR] [--min-age-days N] [--extra FILE]
                       [--patterns "a b c"] [--depth N]

  --root DIR         tree to scan (default $HOME)
  --min-age-days N   keep anything modified within N days (default 7; 0 disables)
  --extra FILE       extra protected paths, one per line — use for a session's
                     known work list it has not written to yet
  --patterns "..."   space-separated dir names to consider (default: build artifacts)
  --depth N          max find depth (default 7)

Output: TSV of action/size_kb/category/reason/path on stdout, summary on stderr.
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --root) ROOT="${2%/}"; shift 2 ;;
    --min-age-days) MIN_AGE_DAYS="$2"; shift 2 ;;
    --extra) EXTRA="$2"; shift 2 ;;
    --patterns) PATTERNS="$2"; shift 2 ;;
    --depth) DEPTH="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[ -d "$ROOT" ] || { echo "reclaim-plan: no such directory: $ROOT" >&2; exit 2; }

PROTECT="$(mktemp)"
trap 'rm -f "$PROTECT"' EXIT

# Build the protection set FIRST. If this fails, refuse to emit a plan at all —
# a plan built without protection would look completely normal and delete a live
# session's working files.
protect_args=(--root "$ROOT")
[ -n "$EXTRA" ] && protect_args+=(--extra "$EXTRA")
if ! "$HERE/protect-list.sh" "${protect_args[@]}" > "$PROTECT"; then
  echo "reclaim-plan: protect-list failed — refusing to emit a plan." >&2
  exit 3
fi
echo "reclaim-plan: protecting $(wc -l < "$PROTECT" | tr -d ' ') path(s) from live sessions" >&2

# find_candidates PATTERN
#   For every pattern except node_modules itself, node_modules subtrees are
#   PRUNED rather than searched. A `build/` or `dist/` inside node_modules is a
#   dependency's own shipped output, not project build output — and pruning also
#   avoids walking tens of thousands of nested directories, which dominated the
#   scan time before.
find_candidates() {
  local pat="$1"
  if [ "$pat" = "node_modules" ]; then
    find "$ROOT" -maxdepth "$DEPTH" -type d -name "$pat" -prune 2>/dev/null
  else
    find "$ROOT" -maxdepth "$DEPTH" \
      -type d -name node_modules -prune -o \
      -type d -name "$pat" -prune -print 2>/dev/null
  fi
}

NOW="$(date +%s)"
del_kb=0; keep_kb=0; del_n=0; keep_n=0

printf 'action\tsize_kb\tcategory\treason\tpath\n'

for pat in $PATTERNS; do
  while IFS= read -r d; do
    [ -n "$d" ] || continue

    # Belt and braces alongside the prune in find_candidates: never plan
    # anything inside an installed dependency tree, whatever the traversal did.
    if in_dependency_tree "$d"; then
      continue
    fi

    # macOS/BSD stat. mtime is read here, at the edge; classify() stays pure.
    mtime=$(stat -f %m "$d" 2>/dev/null) || continue
    size_kb=$(du -sk "$d" 2>/dev/null | cut -f1) || continue

    # Is this actually a build artifact, or just a source directory with an
    # unlucky name? Checked at the edge; artifact_markers() itself stays pure.
    markers="$(artifact_markers "$pat")"
    if [ -n "$markers" ]; then
      parent="$(dirname "$d")"; found=0
      for m in $markers; do [ -e "$parent/$m" ] && { found=1; break; }; done
      if [ "$found" -eq 0 ]; then
        printf 'keep\t%s\t%s\tnot-an-artifact\t%s\n' "${size_kb:-0}" "$pat" "$d"
        keep_kb=$((keep_kb + ${size_kb:-0})); keep_n=$((keep_n + 1))
        continue
      fi
    fi

    # Would deleting this actually free anything? An artifact hard-linked into a
    # shared store reports its full size to `du` but frees almost nothing when
    # removed, so planning it buys a reinstall for no space.
    sl="$(store_linked_marker "$pat")"
    if [ -n "$sl" ] && [ -e "$(dirname "$d")/$sl" ]; then
      printf 'keep\t%s\t%s\tstore-linked\t%s\n' "${size_kb:-0}" "$pat" "$d"
      keep_kb=$((keep_kb + ${size_kb:-0})); keep_n=$((keep_n + 1))
      continue
    fi

    verdict="$(classify "$d" "$mtime" "$NOW" "$MIN_AGE_DAYS" "$PROTECT")"
    action="${verdict%%|*}"; reason="${verdict##*|}"
    printf '%s\t%s\t%s\t%s\t%s\n' "$action" "${size_kb:-0}" "$pat" "$reason" "$d"
    if [ "$action" = "delete" ]; then
      del_kb=$((del_kb + ${size_kb:-0})); del_n=$((del_n + 1))
    else
      keep_kb=$((keep_kb + ${size_kb:-0})); keep_n=$((keep_n + 1))
    fi
  done < <(find_candidates "$pat")
done

{
  printf 'reclaim-plan: %d dir(s) to delete, %.1f GB\n' "$del_n" "$(echo "$del_kb" | awk '{print $1/1048576}')"
  printf 'reclaim-plan: %d dir(s) kept,      %.1f GB\n' "$keep_n" "$(echo "$keep_kb" | awk '{print $1/1048576}')"
  printf 'reclaim-plan: review the plan, then: reclaim-apply.sh <plan> --confirm\n'
} >&2

exit 0
