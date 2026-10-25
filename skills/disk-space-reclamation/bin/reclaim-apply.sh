#!/usr/bin/env bash
# Execute a plan produced by reclaim-plan.sh. THIS IS THE ONLY SCRIPT THAT DELETES.
#
# It refuses to do anything without --confirm, and it will not accept a path that
# was not written by the planner: every row must still parse, still be a
# directory, and still match one of the planner's own category names. That makes
# a hand-edited or truncated plan fail closed rather than delete something
# unexpected.

set -uo pipefail

PLAN=""
CONFIRM=0
LOG=""

usage() {
  cat <<'USAGE'
usage: reclaim-apply.sh PLAN.tsv [--confirm] [--log FILE]

Without --confirm this prints what WOULD be deleted and exits 0 (dry run).
With --confirm it deletes rows whose action is "delete", and nothing else.
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --confirm) CONFIRM=1; shift ;;
    --log) LOG="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) PLAN="$1"; shift ;;
  esac
done

[ -n "$PLAN" ] && [ -f "$PLAN" ] || { echo "reclaim-apply: plan file required" >&2; usage >&2; exit 2; }

VALID_CATEGORIES=" node_modules target build dist .next out __pycache__ .pytest_cache "

free_kb() { df -k / | awk 'NR==2{print $4}'; }

BEFORE="$(free_kb)"
[ -z "$LOG" ] && LOG="${TMPDIR:-/tmp}/reclaim-$(date +%Y%m%d-%H%M%S).log"

n=0; kb=0; skipped=0
while IFS=$'\t' read -r action size_kb category reason path; do
  [ "$action" = "action" ] && continue           # header
  [ "$action" = "delete" ] || continue           # keep rows are audit trail only
  [ -n "$path" ] || continue

  # Fail closed on anything the planner would not have produced.
  case "$VALID_CATEGORIES" in *" $category "*) ;; *)
    echo "reclaim-apply: REFUSING unknown category '$category' for $path" >&2
    skipped=$((skipped+1)); continue ;;
  esac
  if [ ! -d "$path" ]; then
    skipped=$((skipped+1)); continue            # already gone since planning
  fi
  case "$path" in
    /|"$HOME"|"$HOME"/) echo "reclaim-apply: REFUSING unsafe path $path" >&2; skipped=$((skipped+1)); continue ;;
  esac

  if [ "$CONFIRM" -eq 1 ]; then
    rm -rf "$path" && printf '%s\tdeleted\t%s\n' "$(date +%H:%M:%S)" "$path" >> "$LOG"
  else
    printf 'would delete  %8s KB  %s\n' "${size_kb:-?}" "$path"
  fi
  n=$((n+1)); kb=$((kb + ${size_kb:-0}))
done < "$PLAN"

if [ "$CONFIRM" -eq 0 ]; then
  printf '\nDRY RUN — nothing deleted. %d dir(s), %.1f GB would be reclaimed.\n' \
    "$n" "$(echo "$kb" | awk '{print $1/1048576}')"
  printf 'Re-run with --confirm to execute.\n'
  exit 0
fi

AFTER="$(free_kb)"
printf 'deleted %d dir(s); planned %.1f GB\n' "$n" "$(echo "$kb" | awk '{print $1/1048576}')"
printf 'actual free-space delta: %.1f GB\n' "$(echo "$BEFORE $AFTER" | awk '{print ($2-$1)/1048576}')"
[ "$skipped" -gt 0 ] && printf 'skipped %d row(s) — see stderr\n' "$skipped"
printf 'log: %s\n' "$LOG"

# Planned and actual will diverge when hard links are involved: `du` counts a
# linked file once per traversal, so deleting one link frees nothing until the
# last link goes. Trust the free-space delta, not the planned total.
exit 0
