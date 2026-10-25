# Runbook: reclaiming disk space on a macOS dev machine

Ordered procedure, with the reasoning behind each step. Derived from an incident
where a 460 GB volume reached 100% and the machine crashed; ~133 GB was
reclaimed with two Claude Code sessions running throughout.

---

## 0. Diagnose before you delete

```bash
df -h /System/Volumes/Data
sysctl vm.swapusage
memory_pressure | tail -5
```

**`swap total = 0.00M` on a near-full volume is the finding.** macOS allocates
swap on demand into free disk. With no free disk there is no swap, so memory
pressure cannot page out and the machine hard-crashes instead of slowing down.
If someone reports "it crashed, and memory was full too", this is usually why,
and disk is the single root cause behind both symptoms.

Do not chase the memory symptom separately. Free the disk and re-check.

---

## 1. Survey top-down, never bottom-up

```bash
${CLAUDE_SKILL_DIR}/bin/disk-survey.sh ~          # or: du -shx ~/* ~/.[a-zA-Z]* | sort -rh | head -30
```

Rank, then drill into the top entries only. Enumerating every large file first
buries the few decisions that actually matter. Expect the winners to be a small
number of very large things, not a long tail.

Check outside `$HOME` too — `/Applications`, `/Library`, `/opt` — but expect
less there.

---

## 2. Establish what is running BEFORE planning

```bash
${CLAUDE_SKILL_DIR}/bin/protect-list.sh --root ~/repos
```

This is the step that separates safe cleanup from an outage.

Two detection sources, because each misses what the other catches:

| Source | Catches | Misses |
|---|---|---|
| Running `claude` processes → cwd via `lsof` | live-but-**idle** sessions whose transcript has gone cold | work outside the session's cwd |
| Transcripts modified within `--window` → cwd + written `file_path`s | work in repos away from cwd | repos a session plans to touch but has not written to yet |

**The gap is real**: a fan-out rollout that has scanned 65 repos but written to
none of them is invisible to both. Ask what each live session is doing and pass
its target list via `--extra`. A session's own work directory often already
holds that list.

Two guards worth knowing:

- **Ancestor sessions are excluded, loudly.** A session whose cwd is the scan
  root would protect every candidate beneath it — indistinguishable from "reclaim
  nothing". It is reported on stderr for a human decision rather than silently
  protecting everything or silently protecting nothing.
- **Zero detections while sessions run means the detector broke**, not that the
  machine is idle. `protect-list.sh` exits 3 and the planner refuses to emit.

---

## 3. Plan, review, then apply

```bash
${CLAUDE_SKILL_DIR}/bin/reclaim-plan.sh --root ~/repos > plan.tsv   # read-only
${CLAUDE_SKILL_DIR}/bin/reclaim-apply.sh plan.tsv                   # dry run, no --confirm
${CLAUDE_SKILL_DIR}/bin/reclaim-apply.sh plan.tsv --confirm         # deletes
```

The plan keeps `keep` rows on purpose so a reviewer can audit *why* something was
spared, rather than trusting that the protection logic ran.

`reclaim-apply.sh` fails closed: it refuses any category the planner does not
emit, refuses `/` and `$HOME`, and skips paths that vanished since planning. A
hand-edited plan cannot turn it into a general-purpose deleter.

---

## 4. Tiering: rank by size ÷ cost-to-restore

Present opportunities this way and let the human choose.

**Tier 1 — large, safe, regenerable.** Stale VM disk images for a stopped VM,
old IDE version caches and logs, per-project build output, app-managed caches
that re-download. Usually the bulk of the win.

**Tier 2 — regenerable but expensive to refetch.** Dependency caches behind a
slow network or VPN, language toolchains for work not currently active. Real
space, real cost to undo.

**Tier 3 — small or judgement-dependent.** Downloads, installers, heap dumps,
unused applications. Ask; do not assume.

---

## 5. Categories with specific traps

**Sparse VM / container images.** `ls -lh` reports virtual size (may show 100 G),
`du` reports allocated blocks (the real number). Pruning *inside* the VM does not
shrink the host file — only deleting or recreating the VM does. That destroys
images **and named volumes**, so confirm explicitly before doing it.

**Shared global caches.** `~/.m2/repository`, `~/.npm`, `~/.gradle/caches` are
single caches serving every project. There is no safe partial delete, and a live
build anywhere depends on them. Never auto-plan them. Cleaning `~/.npm` while a
concurrent `npm install` runs can corrupt that install.

**Language runtimes.** Check what is actually pinned before pruning:

```bash
find ~/repos -maxdepth 5 -name .nvmrc -exec cat {} \; | sort | uniq -c | sort -rn
find ~/repos -maxdepth 5 -name .tool-versions -exec cat {} \; | sort | uniq -c
```

`lts/hydrogen` is Node 18, `lts/iron` is Node 20. Dropping a major that repos
pin breaks them. Prune redundant patch versions within each major instead, and
keep the version currently active.

**Never reach inside an installed dependency tree.** Scanning for `build` or
`dist` descends into `node_modules` and finds thousands of matches — a real scan
produced 2673 of them, including `node_modules/jest-runtime/build`, which is that
package's shipped compiled output. Every dependency carries its own
`package.json`, so a project-marker check *approves* them, and deleting them
corrupts the install into inexplicable runtime errors. Prune `node_modules`
during traversal for every other pattern. It is also the single biggest speedup:
pruning cut a fleet scan from over ten minutes to under four.

**Artifacts hard-linked into a shared store.** Once repos move to pnpm, `du`
reports a node_modules at full size while deleting it frees almost nothing —
measured: `du` said 186 MB, actual reclaimed was 2 MB. Detect these (a
`pnpm-lock.yaml` beside the `node_modules`) and keep them. Planning them buys a
reinstall for no space.

**Directories named like build output but containing source.** `target`,
`build`, `dist`, and `out` are all real package names too — a live scan found
Java source at `src/java/org/agnitas/target`. The planner requires the parent to
carry the ecosystem's project marker (`pom.xml`, `package.json`, …) before
treating a directory as disposable. Never match on name alone.

---

## 6. macOS-specific traps

- **BSD `xargs` has no `-d`.** `xargs -d'\n'` fails silently in ways that look
  like "zero bytes found". Use `tr '\n' '\0' | xargs -0`.
- **`stat` is `stat -f %m`**, not GNU `stat -c %Y`.
- **`pgrep -x claude` was observed to miss live CLI processes** that
  `ps -eo pid,comm` reports. For a protection list, under-detection means
  deleting live work — prefer the source that finds more.
- **`du` counts hard links once per traversal.** With a content-addressed store
  (pnpm), summed `node_modules` sizes overstate real usage badly. Trust `df`.
- **`sudo -n` fails without passwordless sudo**, and `cmd | sort | head || fallback`
  never runs the fallback, because the pipeline's status comes from `head`.

---

## 7. Verify honestly

Report the free-space delta from `df`, measured before and after — not the sum of
planned sizes. They diverge whenever hard links, sparse files, or concurrent
writes are involved. When they diverge sharply, say so and explain why rather
than quoting the flattering number.

---

## 8. If the same artifacts keep coming back

Recurring cleanup of the same directories is a structural problem. For Node
fleets, a content-addressable store (pnpm) stores each package version once and
hard-links it into every project, so the Nth repo needing a given version costs
nothing extra.

Measure before promising a number. Sharing depends entirely on how much version
drift exists across the fleet — a store dedupes by *exact* version, so
`react@18.2.0` and `react@18.3.1` are two entries. Install two representative
repos, compare store growth against the second repo's `node_modules` size, and
extrapolate from that rather than from a general claim.
