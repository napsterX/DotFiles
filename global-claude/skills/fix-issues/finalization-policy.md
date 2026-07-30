# Finalization Policy

## When to invoke audit-and-pr

Invoke `/audit-and-pr` exactly once after queue processing only when:

- at least one issue was fixed and committed;
- all retained issue commits are present and ordered;
- the worktree is clean;
- HEAD is stable;
- cumulative verification evidence is available;
- no repository-wide stop condition remains;
- the run journal is current and the execution lock is still owned by this run.

If no issue was fixed, do not invoke it. If repository state is unsafe, journal
`FINALIZATION_BLOCKED` without pretending an audit occurred.

## Incremental run record

The finalization manifest is not the first durable record. The run journal from
`runtime-state-policy.md` must already contain every issue and attempt transition.
Journal `FINALIZATION_STARTED` before writing the finalization manifest and
`FINALIZATION_FINISHED` after `/audit-and-pr` returns.

## Finalization manifest

Write JSON under the active run directory:

```text
~/.claude/fix-issues-runs/<repository-key>/<run-id>/audit-and-pr-finalization.json
```

It must include:

- `schema_version: 2`;
- `source_skill: fix-issues`;
- `request: audit-and-pr-finalization`;
- run ID and run-journal path;
- repository root and identifier;
- task worktree and Git common directory;
- branch;
- batch starting HEAD;
- final ending HEAD;
- requested and selected counts;
- configured issue timeout;
- all issue outcomes, including `timed_out`;
- fixed issue numbers and exact commit SHAs;
- attempt counts and final model per issue;
- infrastructure retry evidence;
- cumulative verification commands and results;
- remaining queue counts;
- creation timestamp.

Validate the manifest before delegation using
`~/.claude/skills/audit-and-pr/scripts/delegated_invocation.py` with the live
repository root, branch, and full HEAD. Then pass the manifest path to
`/audit-and-pr`. The finalizer must repeat that validation before any side
effect.

## Delegation boundary

`/fix-issues` owns:

- queue selection;
- issue investigation attempts;
- per-issue model routing;
- issue-level proof, time budget, and retry;
- durable journal and resume controls;
- execution lock;
- one retained commit per fixed issue;
- cumulative pre-finalization verification;
- the finalization manifest;
- terminal FirstMate notification.

`/audit-and-pr` exclusively owns:

- independent audit and risk-adaptive audit lanes;
- bounded P0/P1 remediation and re-audit;
- P2/P3 audit-finding issue tracking;
- final exact-HEAD ship gate;
- push and PR generation/update;
- CI and merge disposition;
- post-merge reconciliation and cleanup.

Do not duplicate PR titles, PR bodies, focused-review prompts, audit reports, or
manual GitHub commands in `/fix-issues`.

## Terminal ordering

After `/audit-and-pr` returns:

1. journal its exact outcome;
2. classify the run `RUN_COMPLETED`, `RUN_STOPPED`, or
   `MANUAL_ACTION_REQUIRED`;
3. attempt the FirstMate notification;
4. journal notification delivery;
5. release the execution lock;
6. report any notification or lock-release failure without changing the audit
   verdict.

## Finalizer outcomes

Record one of:

- `AUDIT_AND_PR_COMPLETED`
- `AUDIT_AND_PR_BLOCKED`
- `AUDIT_AND_PR_FAILED`
- `NOT_APPLICABLE_NO_FIXES`
- `FINALIZATION_BLOCKED`

Do not invoke `/audit-and-pr` repeatedly to manufacture a favorable result. Its
own bounded remediation policy controls any repair loop.
