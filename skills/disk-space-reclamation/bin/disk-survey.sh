#!/usr/bin/env bash
# Read-only survey of what is consuming disk. Deletes nothing, ever.
#
# Ordering matters: capacity and the swap diagnosis come first, because they
# tell you whether you are looking at a tidiness problem or at the condition
# that crashes the machine.

set -uo pipefail

ROOT="${1:-$HOME}"

hr() { printf '\n\033[1m%s\033[0m\n' "$1"; }

hr "CAPACITY"
df -h /System/Volumes/Data 2>/dev/null | tail -1 || df -h / | tail -1

hr "SWAP / MEMORY PRESSURE"
# A full disk cannot back swap. When `total` is 0 while the volume is near
# capacity, memory pressure has nowhere to spill and the machine will hard-crash
# rather than page. That is the failure mode this whole procedure exists to
# prevent, so it is reported before any size ranking.
sysctl vm.swapusage 2>/dev/null || echo "(swap info unavailable)"
free_pct=$(memory_pressure 2>/dev/null | sed -n 's/.*free percentage: *\([0-9]*\).*/\1/p' | tail -1)
[ -n "${free_pct:-}" ] && echo "system-wide memory free: ${free_pct}%"

hr "TOP CONSUMERS UNDER $ROOT"
du -shx "$ROOT"/* "$ROOT"/.[a-zA-Z]* 2>/dev/null | sort -rh | head -25

hr "REGENERABLE BUILD ARTIFACTS (per-project, safe to plan)"
printf '%-16s %10s  %s\n' PATTERN SIZE DIRS
for pat in node_modules target build dist .next out __pycache__ .pytest_cache; do
  # -prune stops descent, so nested matches are not double-counted within a
  # pattern. Patterns can still overlap each other (a dist/ inside a
  # node_modules/), so treat the column as indicative, not additive.
  tot=$(find "$ROOT" -maxdepth 7 -type d -name "$pat" -prune 2>/dev/null -exec du -sk {} + 2>/dev/null \
        | awk '{s+=$1} END{printf "%.1fG", s/1048576}')
  cnt=$(find "$ROOT" -maxdepth 7 -type d -name "$pat" -prune 2>/dev/null | wc -l | tr -d ' ')
  printf '%-16s %10s  %s\n' "$pat" "${tot:-0G}" "$cnt"
done

hr "SHARED CACHES (global — never auto-planned, see runbook)"
# These are single caches shared by every project on the machine. They cannot be
# partially deleted per-project, so a live session anywhere can be depending on
# them. Reported for a human decision; the planner never touches them.
for d in "$HOME/.m2/repository" "$HOME/.npm" "$HOME/.gradle/caches" "$HOME/.cache" \
         "$HOME/.rustup" "$HOME/.cargo" "$HOME/Library/Caches" "$HOME/.nvm" "$HOME/.asdf"; do
  [ -d "$d" ] && du -shx "$d" 2>/dev/null
done | sort -rh

hr "VM / CONTAINER DISK IMAGES (sparse — check actual, not apparent, size)"
# `ls -lh` reports the virtual size of a sparse image and will wildly overstate
# it. `du` reports blocks actually allocated. Reclaiming these means deleting or
# recreating the VM; pruning inside it does not shrink the host file.
for f in "$HOME/.colima/_lima/_disks"/*/datadisk "$HOME/.docker"/*/*.raw \
         "$HOME/Library/Containers/com.docker.docker/Data/vms"/*/*.raw; do
  [ -f "$f" ] && printf '%8s  %s\n' "$(du -h "$f" 2>/dev/null | cut -f1)" "$f"
done 2>/dev/null

hr "NEXT"
cat <<'EOF'
This survey changed nothing. To build a deletion plan:

  reclaim-plan.sh --root <DIR> > plan.tsv     # read-only; honours live sessions
  # review plan.tsv by eye
  reclaim-apply.sh plan.tsv --confirm         # the only script that deletes

Shared caches and VM images above are deliberately excluded from the planner.
See references/runbook.md for why, and for how to reclaim them by hand.
EOF
exit 0
