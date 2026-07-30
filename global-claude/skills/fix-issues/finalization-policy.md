# Finalization Policy

## When to invoke audit-and-pr

Invoke `/audit-and-pr` exactly once after queue processing only when:

- at least one issue was fixed and committed;
- all retained issue commits are present and ordered;
- the worktree is clean;
- HEAD is stable;
- cumulative verification evidence is available;
- no repository-wide stop condition remains.

If no issue was fixed, do not invoke it. If repository state is unsafe, report
`FINALIZATION_BLOCKED` without pretending an audit occurred.

## Finalization manifest

Write a durable JSON manifest outside the product repository under:

```text
~/.claude/fix-issues-runs/<repository-key>/<run-id>/audit-and-pr-finalization.json
```

It must include:

- `schema_version: 1`;
- `source_skill: fix-issues`;
- `request: audit-and-pr-finalization`;
- repository root and identifier;
- branch;
- batch starting HEAD;
- final ending HEAD;
- requested and selected counts;
- all issue outcomes;
- fixed issue numbers and exact commit SHAs;
- attempt counts and final model per issue;
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
- issue-level proof and retry;
- one retained commit per fixed issue;
- cumulative pre-finalization verification;
- the finalization manifest.

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

## Finalizer outcomes

Record one of:

- `AUDIT_AND_PR_COMPLETED`
- `AUDIT_AND_PR_BLOCKED`
- `AUDIT_AND_PR_FAILED`
- `NOT_APPLICABLE_NO_FIXES`
- `FINALIZATION_BLOCKED`

Do not invoke `/audit-and-pr` repeatedly to manufacture a favorable result.
Its own bounded remediation policy controls any repair loop.
