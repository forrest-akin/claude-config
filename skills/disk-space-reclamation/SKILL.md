---
name: disk-space-reclamation
description: Reclaim disk space on a macOS dev machine without breaking work that is currently running — survey what is consuming the volume, build an auditable deletion plan that spares repos live Claude Code sessions are using, then apply it. Use when the disk is full or nearly full, when a machine crashed or froze under storage exhaustion, when builds fail with "no space left on device", or when asked what is eating the disk. Do not use to shrink a git repository's own history (that is git gc / filter-repo), or to delete one specific known file.
---

# Disk space reclamation

## The rule that matters most

**Never delete without first asking what is running.** Build artifacts look
identically disposable whether or not a session is mid-flight in them. Deleting
`node_modules` or `target/` under active work produces failures that look like
bugs in the work, not like cleanup — the most expensive possible outcome,
because the time is lost to debugging the wrong thing.

`bin/protect-list.sh` answers that question from live processes and recent
session transcripts. Everything else is downstream of it.

## Procedure

```
${CLAUDE_SKILL_DIR}/bin/disk-survey.sh [ROOT]                  # 1. read-only. changes nothing.
${CLAUDE_SKILL_DIR}/bin/reclaim-plan.sh --root DIR > plan.tsv  # 2. read-only. honours live sessions.
#    review plan.tsv                        # 3. HUMAN reads it and approves.
${CLAUDE_SKILL_DIR}/bin/reclaim-apply.sh plan.tsv --confirm    # 4. the only script that deletes.
```

Step 3 is not optional and is not yours to skip. `reclaim-apply.sh` is dry-run
without `--confirm`; run it that way first and show the output. Present findings
ranked by size against cost-to-restore and let the user choose what to act on.

## What the planner deliberately will not touch

**Shared global caches** — `~/.m2/repository`, `~/.npm`, `~/.gradle/caches`,
`~/.cache`. One cache serves every project, so it cannot be partitioned and any
live session may depend on it. `~/.m2` in particular has no safe partial delete:
a single Maven build anywhere needs it. These are surfaced by the survey for a
human decision and never planned.

**Language runtimes and toolchains** — `.nvm`, `.asdf`, `.rustup`, `.ghcup`.
Repos pin old versions via `.nvmrc` / `.tool-versions`; removing a major line
breaks them. Prune redundant *patch* versions within a major, keep the newest of
each major, and check what is actually pinned first.

**VM and container disk images** — reclaiming these means deleting or recreating
the VM, which destroys images and named volumes. Confirm explicitly; pruning
inside the VM does not shrink the host file.

## Reading the numbers honestly

- **`du` counts a hard-linked file once per traversal.** Where a content-addressed
  store is in use (pnpm), summing per-repo `node_modules` overstates real usage.
  Trust the free-space delta from `df`, not the planned total.
- **Sparse images**: `ls -lh` shows virtual size, `du` shows allocated blocks.
  Quote `du`.
- **`swap total = 0` on a near-full volume is the crash cause**, not a curiosity:
  there is no room to back swap, so memory pressure hard-crashes instead of
  paging. Report it when present — it means fixing disk fixes both symptoms.

## When reclamation keeps recurring

Repeated cleanup of the same artifacts is a structural problem, not a hygiene
one. For Node fleets, a content-addressable store (pnpm) stores each package
version once and hard-links it into every project. Measure the real sharing
ratio on your own repos before promising a number — it varies enormously with
how much version drift exists across the fleet.

## Reference

- [`references/runbook.md`](references/runbook.md) — the full ordered procedure,
  the survey→decide→apply loop, and the macOS-specific traps (BSD `xargs` has no
  `-d`, `pgrep` can miss live processes, `stat -f %m`).
- `lib/select.sh` — pure classification logic; `tests/test-select.sh` covers it.
  Both the live-session guard and the source-directory guard exist because a real
  scan nearly deleted something it should not have. Keep the tests green.
