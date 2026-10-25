#!/usr/bin/env bash
# Tests for the pure classification logic in lib/select.sh.
#
# classify() decides whether a reclamation candidate is deleted or kept. It is
# the function standing between a plan file and `rm -rf`, so it takes the clock
# and the mtime as arguments rather than reading them — that keeps it pure and
# lets these tests pin every boundary exactly.

set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/select.sh
. "$HERE/../lib/select.sh"

PASS=0; FAIL=0
DAY=86400
NOW=1000000000

check() { # check <name> <expected> <actual>
  if [ "$2" = "$3" ]; then PASS=$((PASS+1))
  else FAIL=$((FAIL+1)); printf 'FAIL: %s\n  expected: %s\n  actual:   %s\n' "$1" "$2" "$3"; fi
}

PROTECT="$(mktemp)"; trap 'rm -f "$PROTECT"' EXIT
cat > "$PROTECT" <<'EOF'
/repos/active-app
/repos/group/other-app
EOF

old=$((NOW - 30*DAY))
fresh=$((NOW - 1*DAY))

# --- protection by exact project match ---------------------------------------
check "exact protected project is kept" \
  "keep|active-session" \
  "$(classify /repos/active-app/node_modules "$old" "$NOW" 7 "$PROTECT")"

# --- protection extends to nested paths under a protected project ------------
# A protected project's subpackages must inherit protection; a rollout touching
# /repos/active-app can install into /repos/active-app/frontend/node_modules.
check "nested path under protected project is kept" \
  "keep|active-session" \
  "$(classify /repos/active-app/frontend/node_modules "$old" "$NOW" 7 "$PROTECT")"

# --- a prefix that is not a path boundary must NOT match ---------------------
# /repos/active-app-legacy is a DIFFERENT project. Naive prefix matching would
# protect it and silently under-reclaim.
check "sibling with protected name as prefix is deleted" \
  "delete|stale" \
  "$(classify /repos/active-app-legacy/node_modules "$old" "$NOW" 7 "$PROTECT")"

# --- recency guard -----------------------------------------------------------
check "recently modified unprotected path is kept" \
  "keep|recent" \
  "$(classify /repos/idle/node_modules "$fresh" "$NOW" 7 "$PROTECT")"

check "stale unprotected path is deleted" \
  "delete|stale" \
  "$(classify /repos/idle/node_modules "$old" "$NOW" 7 "$PROTECT")"

# --- boundary: exactly at the age threshold counts as recent -----------------
at_edge=$((NOW - 7*DAY))
check "exactly at age threshold is kept" \
  "keep|recent" \
  "$(classify /repos/idle/node_modules "$at_edge" "$NOW" 7 "$PROTECT")"

check "one second past threshold is deleted" \
  "delete|stale" \
  "$(classify /repos/idle/node_modules "$((at_edge - 1))" "$NOW" 7 "$PROTECT")"

# --- protection wins over recency, and over age ------------------------------
check "protected path is kept even when stale" \
  "keep|active-session" \
  "$(classify /repos/group/other-app/node_modules "$old" "$NOW" 7 "$PROTECT")"

# --- empty protect file must not protect everything --------------------------
EMPTY="$(mktemp)"
check "empty protect list still deletes stale paths" \
  "delete|stale" \
  "$(classify /repos/idle/node_modules "$old" "$NOW" 7 "$EMPTY")"
rm -f "$EMPTY"

# --- age 0 disables the recency guard ----------------------------------------
check "age threshold of 0 deletes even fresh paths" \
  "delete|stale" \
  "$(classify /repos/idle/node_modules "$fresh" "$NOW" 0 "$PROTECT")"

# --- artifact markers -------------------------------------------------------
# Name matching alone is not enough. A real scan found
# `openemm-patches/src/java/org/agnitas/target` — Java SOURCE in a directory
# called `target`. Deleting it would destroy committed code. A candidate only
# counts as a build artifact when its PARENT carries the ecosystem's project
# marker, so a stray `target/` deep in a source tree is spared.

check "target requires a JVM project marker" \
  "pom.xml build.gradle build.gradle.kts build.sbt" \
  "$(artifact_markers target)"

check "node_modules requires package.json" \
  "package.json" \
  "$(artifact_markers node_modules)"

check "__pycache__ needs no marker (always disposable)" \
  "" \
  "$(artifact_markers __pycache__)"

check "unknown category needs no marker" \
  "" \
  "$(artifact_markers something-else)"

# `build`/`dist`/`out` are the most overloaded names, so they accept markers from
# several ecosystems rather than guessing one.
case "$(artifact_markers build)" in
  *package.json*pom.xml*|*pom.xml*package.json*) B=ok ;;
  *) B="missing multi-ecosystem markers: $(artifact_markers build)" ;;
esac
check "build accepts markers from multiple ecosystems" "ok" "$B"

# --- store-linked artifacts -------------------------------------------------
# Measured on a real repo: `du` reported 186 MB for a pnpm-managed node_modules,
# but deleting it freed 2 MB — the content is hard-linked into a shared store, so
# removing one link frees nothing until the last link goes. Planning these wastes
# a reinstall and reclaims nothing, so they must be identified and kept.

check "node_modules is store-linked when a pnpm lockfile is present" \
  "pnpm-lock.yaml" \
  "$(store_linked_marker node_modules)"

check "target has no store-linked form" \
  "" \
  "$(store_linked_marker target)"

check "unknown category has no store-linked form" \
  "" \
  "$(store_linked_marker whatever)"

# --- never reach inside an installed dependency tree -------------------------
# A real scan planned 2673 deletions inside node_modules — paths like
# `node_modules/jest-runtime/build`, which is that package's SHIPPED compiled
# code. Each dependency carries its own package.json, so the artifact-marker
# check happily approves them. Deleting them silently corrupts every affected
# repo. Anything under a node_modules/ belongs to the installed tree and is only
# ever removed by deleting that whole tree.

in_dep() { if in_dependency_tree "$1"; then echo yes; else echo no; fi; }

check "build dir inside node_modules is dependency content" \
  "yes" "$(in_dep /r/app/node_modules/jest-runtime/build)"

check "nested node_modules is still dependency content" \
  "yes" "$(in_dep /r/app/node_modules/a/node_modules/b/dist)"

check "the node_modules dir itself is not INSIDE a dependency tree" \
  "no" "$(in_dep /r/app/node_modules)"

check "project's own build dir is not dependency content" \
  "no" "$(in_dep /r/app/build)"

check "a path merely containing the word is not a match" \
  "no" "$(in_dep /r/my-node_modules-notes/build)"

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
