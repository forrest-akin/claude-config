---
name: commit-sequencing
description: Decides whether a change needs a stack of commits and cuts the boundaries so each commit deploys alone, with expand before contract. Use when planning a change that may span several commits, when splitting one, or when checking that a planned sequence can ship commit by commit. Not for writing a commit message or folding a fix into an earlier commit.
---

# Commit sequencing

## Stack or not

Always stack a breaking change to an API, schema or event contract (expand, then contract), and a
refactor that comes with a behavior change. Otherwise stack when at least two hold, else one commit:

- layered change where each layer deploys on its own;
- a partial delivery that is useful by itself;
- roughly 200+ lines over 3+ files with clear seams;
- risky shared state (shared tables, hot endpoints).

A stack estimated under about 100 lines collapses to one commit, unless that would put an expand
and its contract, or a refactor and a behavior change, in one commit.

## Cutting

- Test every cut: could trunk ship right here with nothing after it? If not, re-cut.
- Each commit can be reverted alone without breaking the ones after it.
- Map tasks to commits, one each by default. Merge tasks that can't deploy without each other.
  Split a task that has an additive and a destructive half. Order every additive change before the
  destructive change that depends on it.
- A dependency cycle between tasks is reported with both tasks and the artifact each waits on. No
  partial sequence is produced.
- Red flags: a placeholder message (WIP, temp, part N); code unreachable after its commit; a very
  large commit.

## What forces expand/contract

- **Breaking**: removing or renaming an endpoint or a response field; making an optional input
  required; changing a field's type; dropping or renaming a column or table; editing an
  already-applied migration; removing a component still wired elsewhere; a backward-incompatible
  message-schema change.
- **Warn**: a non-null column without a default on a large table; new required config without a
  default; a new consumer with no explicit start-offset policy; new enum values consumers may not
  tolerate.
- **Safe**: optional response fields, new endpoints, nullable columns with their migration, new
  components not yet wired.
- When the app validates its schema at startup, the schema model and its migration land in the
  same commit.
