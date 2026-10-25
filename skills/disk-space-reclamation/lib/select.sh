#!/usr/bin/env bash
# Pure classification logic for reclamation candidates.
#
# Nothing here touches the filesystem or the clock. Callers read mtimes and the
# current time at the edge and pass them in, so this logic is fully testable and
# the decision to `rm -rf` never depends on ambient state.

# is_protected PATH PROTECT_FILE
#   Succeeds when PATH is a protected project or lives underneath one.
#   Matching is path-boundary aware: /repos/app protects /repos/app/frontend but
#   NOT /repos/app-legacy, which is a different project.
is_protected() {
  local path="$1" protect_file="$2" line
  [ -f "$protect_file" ] || return 1
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    case "$path" in
      "$line") return 0 ;;
      "$line"/*) return 0 ;;
    esac
  done < "$protect_file"
  return 1
}

# artifact_markers CATEGORY
#   Prints the filenames that must exist in a candidate's PARENT directory for it
#   to be a genuine build artifact. Empty output means no check is needed.
#
#   Directory names are ambiguous: a real scan found Java source at
#   `.../src/java/org/agnitas/target`. Requiring the parent to carry the
#   ecosystem's project marker distinguishes `myapp/target` (Maven output,
#   disposable) from `org/agnitas/target` (a package, committed source).
artifact_markers() {
  case "$1" in
    node_modules|.next)
      printf 'package.json\n' ;;
    target)
      printf 'pom.xml build.gradle build.gradle.kts build.sbt\n' ;;
    build|dist|out)
      # The most overloaded names; accept any recognised project root.
      printf 'package.json pom.xml build.gradle build.gradle.kts Makefile CMakeLists.txt setup.py pyproject.toml\n' ;;
    *)
      printf '\n' ;;
  esac
}

# store_linked_marker CATEGORY
#   Prints the filename whose presence in the candidate's PARENT means the
#   artifact is hard-linked into a shared content-addressable store. Empty output
#   means the category has no such form.
#
#   Measured on a real repo: `du` reported 186 MB for a pnpm-managed
#   node_modules, but deleting it freed 2 MB. Removing one hard link frees
#   nothing while the store still holds the file, so these are pure cost — a
#   reinstall bought for no space. Keep them.
store_linked_marker() {
  case "$1" in
    node_modules) printf 'pnpm-lock.yaml\n' ;;
    *)            printf '\n' ;;
  esac
}

# in_dependency_tree PATH
#   Succeeds when PATH lies INSIDE an installed dependency tree.
#
#   A real scan planned 2673 deletions of paths like
#   `node_modules/jest-runtime/build` — that package's shipped compiled output.
#   Every dependency carries its own package.json, so the artifact-marker check
#   approves them, and removing them corrupts the install in ways that surface
#   later as inexplicable runtime errors. Dependency content is only ever removed
#   by deleting the whole node_modules, never piecemeal.
in_dependency_tree() {
  case "$1" in
    */node_modules/*) return 0 ;;
    *)                return 1 ;;
  esac
}

# classify PATH MTIME_EPOCH NOW_EPOCH MIN_AGE_DAYS PROTECT_FILE
#   Prints "keep|<reason>" or "delete|<reason>".
#
#   Precedence, strongest first:
#     active-session — the path belongs to work a live session is doing
#     recent         — modified within MIN_AGE_DAYS (0 disables this guard)
#     stale          — safe to reclaim
classify() {
  local path="$1" mtime="$2" now="$3" min_age_days="$4" protect_file="$5"

  if is_protected "$path" "$protect_file"; then
    printf 'keep|active-session\n'; return 0
  fi

  if [ "$min_age_days" -gt 0 ]; then
    local age=$(( now - mtime )) threshold=$(( min_age_days * 86400 ))
    if [ "$age" -le "$threshold" ]; then
      printf 'keep|recent\n'; return 0
    fi
  fi

  printf 'delete|stale\n'
}
