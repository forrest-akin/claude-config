---
name: disk-space-reclamation
description: Reclaim disk space on a macOS dev machine without breaking work that is currently running — survey what is consuming the volume, build an auditable deletion plan that spares repos live Claude Code sessions are using, then apply it. Use when the disk is full or nearly full, when a machine crashed or froze under storage exhaustion, when builds fail with "no space left on device", or when asked what is eating the disk. Do not use to shrink a git repository's own history (that is git gc / filter-repo), or to delete one specific known file.
---

# Disk space reclamation

## The rule that matters most

`bin/protect-list.sh` finds what is running. Everything else is downstream of it.

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
`~/.cache`. See runbook §5.

**Language runtimes and toolchains** — `.nvm`, `.asdf`, `.rustup`, `.ghcup`.
Repos pin old versions via `.nvmrc` / `.tool-versions`; removing a major line
breaks them. Prune redundant *patch* versions within a major, keep the newest of
each major, and check what is actually pinned first.

**VM and container disk images** — reclaiming these means deleting or recreating
the VM, which destroys images and named volumes. Confirm explicitly; pruning
inside the VM does not shrink the host file.

## Reading the numbers honestly

- **`swap total = 0` on a near-full volume is the crash cause**, not a curiosity:
  there is no room to back swap, so memory pressure hard-crashes instead of
  paging. Report it when present — it means fixing disk fixes both symptoms.

## Reference

- [`references/runbook.md`](references/runbook.md) — read before the first survey:
  the ordered procedure, the survey→decide→apply loop, and macOS traps (BSD
  `xargs` has no `-d`, `pgrep` can miss live processes, `stat -f %m`).
- `lib/select.sh` — pure classification logic; `tests/test-select.sh` covers it.
  Both the live-session guard and the source-directory guard exist because a real
  scan nearly deleted something it should not have. Keep the tests green.
