#!/usr/bin/env bash
# Emit the set of paths that must NOT be reclaimed because a live Claude Code
# session is working in them. One absolute path per line, on stdout.
#
# Why this exists: build artifacts look identically disposable whether or not a
# session is mid-flight in them. Deleting node_modules or target/ underneath
# running work produces failures that look like bugs in the work, not like
# disk cleanup. This is the guard.
#
# Detection is deliberately conservative and evidence-based, from two sources
# that each catch what the other misses:
#   1. Running `claude` processes -> their working directory, via lsof. Catches a
#      session that is alive but IDLE, whose transcript has gone cold.
#   2. Any session transcript modified within --window minutes -> its cwd, plus
#      every repo it has WRITTEN to (file_path entries), reduced to the
#      enclosing git repo. Catches work outside the session's own cwd.
#
# Source 2 reads written-file evidence rather than every path mentioned, because
# a session that merely *surveyed* the fleet would otherwise protect the entire
# fleet and reclaim nothing.
#
# LIMIT: a session that has only planned work it has not yet written, in repos
# outside its cwd, is invisible to both sources. Pass such a work list
# via --extra. This is the common case for a fan-out rollout.

# NOT `set -e`: this script's output gates deletion, and an abort partway through
# would emit a SHORT list that reads as "less to protect" rather than as failure.
# Sources handle their own errors; completeness is asserted at the end instead.
set -uo pipefail

WINDOW=120
ROOT=""
EXTRA=""
CONFIG_DIRS=()

usage() {
  cat <<'USAGE'
usage: protect-list.sh [--window MINUTES] [--root DIR] [--extra FILE] [--config-dir DIR]

  --window N      treat transcripts modified in the last N minutes as live (default 120)
  --root DIR      only emit protected paths under DIR
  --extra FILE    additional protected paths (one per line); use for a session's
                  known work list that it has not written to yet
  --config-dir D  Claude config dir to scan (repeatable; default ~/.claude and ~/.claude-*)
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --window) WINDOW="$2"; shift 2 ;;
    --root) ROOT="${2%/}"; shift 2 ;;
    --extra) EXTRA="$2"; shift 2 ;;
    --config-dir) CONFIG_DIRS+=("$2"); shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ ${#CONFIG_DIRS[@]} -eq 0 ]; then
  for d in "$HOME"/.claude "$HOME"/.claude-*; do
    [ -d "$d/projects" ] && CONFIG_DIRS+=("$d")
  done
fi

# repo_root PATH — nearest ancestor containing .git. Emits NOTHING when the path
# is not inside a repo.
#
# Falling back to the path itself is wrong and was observed to be actively
# harmful: a session writing to a scratch file directly under the scan root
# emitted the scan root, which protects every repo beneath it and silently
# reclaims nothing. A path outside any repo is not project work, so it needs no
# build-artifact protection.
repo_root() {
  local p="$1"
  while [ "$p" != "/" ] && [ -n "$p" ] && [ "$p" != "." ]; do
    [ -d "$p/.git" ] && { printf '%s\n' "$p"; return 0; }
    p="$(dirname "$p")"
  done
  return 1
}

emit_from_transcript() {
  local t="$1"
  # cwd of the session
  grep -o '"cwd":"[^"]*"' "$t" 2>/dev/null | sed 's/"cwd":"//; s/"$//'
  # repos the session has written to
  grep -o '"file_path":"[^"]*"' "$t" 2>/dev/null | sed 's/"file_path":"//; s/"$//' \
    | while IFS= read -r f; do [ -n "$f" ] && repo_root "$(dirname "$f")"; done
  return 0
}

# Working directory of every running claude process. Catches live-but-idle
# sessions, whose transcripts are too cold for the --window test.
# NOTE: `ps` is used rather than `pgrep -x claude`, which was observed to miss
# live CLI processes that `ps` reports. Under-detection here means deleting a
# running session's files, so prefer the source that finds more.
emit_from_processes() {
  command -v lsof >/dev/null 2>&1 || return 0
  local pid
  for pid in $(ps -eo pid,comm | awk '$2=="claude" || $2 ~ /\/claude$/ {print $1}'); do
    # A pid can vanish between listing and inspection; that must not abort the
    # run, because a truncated protection list means deleting live work.
    lsof -a -d cwd -p "$pid" -Fn 2>/dev/null | sed -n 's/^n//p' || true
  done
  return 0
}

LIVE_PROCS=$(ps -eo pid,comm | awk '$2=="claude" || $2 ~ /\/claude$/ {print $1}' | wc -l | tr -d ' ')
FOUND=0
TMP_OUT="$(mktemp)"
trap 'rm -f "$TMP_OUT"' EXIT

{
  emit_from_processes
  for cfg in "${CONFIG_DIRS[@]:-}"; do
    [ -d "$cfg/projects" ] || continue
    while IFS= read -r t; do
      emit_from_transcript "$t"
    done < <(find "$cfg/projects" -name '*.jsonl' -mmin "-$WINDOW" 2>/dev/null)
  done
  if [ -n "$EXTRA" ] && [ -f "$EXTRA" ]; then
    grep -v '^[[:space:]]*$' "$EXTRA" || true
  fi
} | sed 's|/*$||' | sort -u > "$TMP_OUT"

TOO_COARSE=""
# TOTAL counts everything detected anywhere, before --root filtering. FOUND
# counts what survives the filter. The health check must use TOTAL: finding
# nothing *under a given subtree* is normal and expected when scanning a tree no
# session happens to be working in, whereas finding nothing at all while
# sessions are running means detection itself is broken.
TOTAL=$(grep -c . "$TMP_OUT" 2>/dev/null || echo 0)

while IFS= read -r p; do
  [ -n "$p" ] || continue
  if [ -n "$ROOT" ]; then
    # A session whose cwd is the scan root (or an ancestor of it) would protect
    # every candidate beneath it. Emitting that is indistinguishable from
    # "reclaim nothing", so surface it as a decision for the operator instead of
    # silently choosing either extreme.
    case "$ROOT" in
      "$p"|"$p"/*) TOO_COARSE="$TOO_COARSE $p"; continue ;;
    esac
    case "$p" in "$ROOT"|"$ROOT"/*) printf '%s\n' "$p"; FOUND=$((FOUND+1)) ;; esac
  else
    printf '%s\n' "$p"; FOUND=$((FOUND+1))
  fi
done < "$TMP_OUT"

if [ -n "$TOO_COARSE" ]; then
  echo "protect-list: NOTE — session(s) rooted at or above the scan root:$TOO_COARSE" >&2
  echo "protect-list: excluded as too coarse to be useful. If such a session is doing" >&2
  echo "protect-list: fleet-wide work, pass its specific targets via --extra." >&2
fi

# A live session with nothing protected is far more likely to be a broken
# detector than a genuinely idle machine. Say so on stderr rather than letting a
# caller read the silence as "safe to delete everything".
if [ "$LIVE_PROCS" -gt 0 ] && [ "$TOTAL" -eq 0 ]; then
  echo "protect-list: WARNING — $LIVE_PROCS live claude process(es) but nothing detected anywhere." >&2
  echo "protect-list: treat this as detection failure, not as an empty protection set." >&2
  exit 3
fi

exit 0
