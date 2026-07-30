# Delegated Invocation Policy

## Purpose

Allow `/fix-issues` to invoke `/audit-and-pr` once after a bounded batch without
making audit-and-pr generally self-starting.

## Authorized entry paths

1. Direct user invocation: `/audit-and-pr` or
   `/audit-and-pr baseline-restoration`.
2. Model-initiated finalization from `/fix-issues` with a validated manifest.

Any other model-initiated invocation is rejected before repository commands,
GitHub mutation, or audit work.

## Required manifest

The caller must provide an absolute path to a JSON manifest with:

- `schema_version: 1` for legacy callers or `schema_version: 2` for durable
  `/fix-issues` runs;
- `source_skill: fix-issues`;
- `request: audit-and-pr-finalization`;
- absolute repository root;
- repository identifier;
- branch;
- full batch starting and ending SHAs;
- at least one fixed issue;
- one exact retained commit SHA per fixed issue;
- all selected issue outcomes;
- cumulative verification evidence;
- creation timestamp;
- for schema 2: run ID, absolute run-journal path, task worktree, Git common
  directory, configured issue timeout, and timed-out outcomes.

Validate using `scripts/delegated_invocation.py` or equivalent deterministic
logic.

## Live-state binding

Before any side effect, confirm:

- manifest repository root equals resolved `TASK_ROOT` by filesystem identity;
- manifest branch equals the checked-out task branch;
- manifest ending HEAD equals live full HEAD;
- worktree is clean;
- every fixed issue commit is reachable from ending HEAD and after batch starting
  HEAD;
- no duplicate issue or commit appears;
- no selected issue is omitted from outcomes.

A stale, malformed, missing, cross-repository, or HEAD-mismatched manifest
returns `DELEGATED_INVOCATION_REJECTED`.

## Scope reconstruction

Treat the manifest as bounded orchestration evidence, not proof that the code is
correct. Reconstruct the objective from the listed issues, live commits,
repository instructions, and current GitHub state. Perform the ordinary
independent audit and all existing gates.

The manifest does not authorize:

- skipping deterministic preflight;
- trusting issue-level verification without review;
- weakening P0/P1 remediation rules;
- omitting P2/P3 finding tracking;
- bypassing final ship, CI, branch protection, merge policy, or cleanup;
- automatically entering baseline-restoration mode.

## Reporting

Report:

```text
Invocation Source:
- Type: DIRECT_USER / FIX_ISSUES_DELEGATED
- Manifest:
- Manifest status: VALID / REJECTED
- Source skill:
- Batch starting HEAD:
- Delegated final HEAD:
- Fixed issues:
```
