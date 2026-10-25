---
name: doc-drift
description: Finds the docs and config a change made wrong, or sweeps a whole repo for doc-vs-code and doc-vs-doc drift, and decides which side wins each conflict. Use before committing a change that renames, removes or recounts something, when asked whether docs match the code, or for a repo-wide drift audit. Not for reviewing a single document's quality.
---

# Doc drift

## Scope

- **Change-based**: list the facts the diff touches (names, paths, endpoints, environment
  variables, flags, versions, counts), then search the repo's docs and config for other statements
  of them. Drift outside the diff is context, not a finding.
- **Full**: inventory the docs and the fact-carrying config, then cross-check them.

## Which side wins

- **Countable facts**: the filesystem.
- **Facts the code defines** (endpoints, environment variables, signatures, flags, dependency
  versions): the code.
- **Declared facts** (version numbers, feature descriptions): the most recently edited doc.

Each fix names the winning side and the rule that decided it. When the winner is ambiguous,
propose the fix instead of applying it.

## Judging

- Compare values, not wording. Two phrasings of one fact agree; differences of opinion or
  adjective are not drift.
- Rank by whether a reader would act wrongly. Highest: a documented endpoint or variable that no
  longer exists, or a version mismatch across manifests. Middle: a count slightly off, a list
  missing a new item. Lowest: a stale comment.
- Never skip a file silently; report anything that couldn't be read.
