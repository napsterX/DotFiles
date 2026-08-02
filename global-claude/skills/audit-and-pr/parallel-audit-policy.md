# Parallel Audit Policy

Parallelism is an optimization, not a relaxation of audit authority. Use
read-only concurrent lanes against one immutable audit state and keep mutation
and shipment sequential.

## Sequential barriers

Keep these operations sequential:

- repository/worktree safety and canonical-base resolution;
- deterministic preflight decisions;
- authoritative synthesis and finding disposition;
- remediation writes;
- issue search/update/create mutations;
- commit creation;
- final exact-HEAD ship gate;
- push, PR mutation, CI disposition, merge, and cleanup.

Never allow two workers to edit the same worktree concurrently.

## Automatic lane selection

Use `scripts/audit_parallelism.py` when available. Default mode is `AUTO`.

- Documentation-only or no more than five low-risk files in one domain: one
  integrated lane.
- Medium change, commonly 6–20 files or two domains: two lanes.
- High-risk, more than 20 files, or at least three domains: three lanes.
- Verification-governance-sensitive change: add a dedicated verification lane,
  up to four total.
- If concurrent workers are unavailable, use one integrated sequential audit.

Explicit sequential or parallel requests do not change the four-lane maximum or
single-writer rule.

## Parallel preparation

After adapter validity and `doctor` pass, required `fast` preflight may overlap
with read-only packet preparation when the host supports it.

Preparation may collect objective, issues, PR context, instructions, changed-file
map, domains, risk, prior evidence, verification-sensitive paths, and the audit
packet. It must not edit, remediate, mutate GitHub, or issue a final verdict.

## Immutable audit packet

Every lane receives the same:

- repository and pinned `TASK_ROOT`;
- exact `HEAD`;
- canonical base and merge-base;
- complete diff/range;
- objective and linked ticket;
- repository instructions;
- unrelated-work boundary;
- deterministic preflight evidence or legacy mode;
- evidence plan and prior ledger;
- risk and affected domains;
- verification-governance-sensitive flag;
- known constraints.

Reject stale lane results from another HEAD, base, or scope.

## Standard read-only lanes

### Correctness and behavior

Review objective coverage, logic, interfaces, state transitions, error handling,
concurrency, idempotency, and compatibility.

### Security and data boundaries

Review authentication, authorization, tenancy, ownership, privacy, secrets,
persistence, migrations, destructive operations, and privileged boundaries.

### Architecture, evidence, and operations

Review architecture consistency, test sufficiency, CI enforcement, operational
behavior, observability, recovery, rollout, rollback, contracts, docs, and
governance.

### Verification governance

Activate for verification-sensitive diffs. Review adapter/profile changes,
required-check membership, skip/applicability behavior, blocking/advisory
classification, allowlists, baselines, thresholds, timeouts, exit codes,
reconciliation, and false-green paths.

Two-lane mode combines correctness with security and combines architecture with
evidence/operations. One-lane mode covers all dimensions.

## Lane contract

Each lane is read-only and must not edit, commit, push, mutate PRs, create issues,
merge, clean branches, run duplicate broad test suites, remediate, or issue the
authoritative verdict.

Each lane returns:

- exact HEAD/base/scope;
- dimensions completed;
- findings with severity, direct evidence, and disposition-relevant facts;
- current-scope relationship;
- remediation boundedness and verification signals;
- issue-gate evidence when deferral may be appropriate;
- missing evidence, uncertainty, and conflicts;
- no-change confirmation.

Lanes propose facts and risks, not final dispositions. Test execution remains
centralized through `minimal-sufficient-testing`.

## Authoritative synthesis

One lead must:

1. reject stale or incomplete lane results;
2. deduplicate findings and repeated manifestations;
3. resolve conflicting conclusions;
4. directly verify proposed P0/P1 findings;
5. add omitted cross-lane risks;
6. reconcile the evidence plan;
7. preserve severity independently of convenience;
8. assign every material finding one validated disposition:
   `FIX_NOW`, `DEFER_TO_ISSUE`, `ADD_TO_EXISTING_ISSUE`,
   `BATCH_INTO_CLEANUP_ISSUE`, `ACCEPT_AS_LOW_VALUE`, `DISMISS`, or
   `BLOCK_ACCEPTANCE`;
9. explain why each P2 is fixed now or deferred;
10. prevent automatic P3 ticket generation;
11. apply the issue-creation gate and identify duplicate/batch candidates;
12. produce one authoritative finding ledger, verdict, testing confidence, CI
    enforcement confidence, and provisional merge eligibility.

Parallel lanes never create competing final verdicts or GitHub issues.

## Remediation and re-audit

Use exactly one remediation writer and provide only validated `FIX_NOW` findings.
This may include mandatory P0/P1, bounded directly related P2, and trivial
adjacent behavior-preserving P3.

After tracked files change:

1. run targeted validation;
2. rerun `fast --base <resolved-base>` only when evidence was invalidated,
   repository policy requires it, or verification machinery changed;
3. run focused conformance evidence for verification changes;
4. review the complete final diff;
5. recheck sensitive boundaries when relevant;
6. create a new immutable audit packet;
7. rerun applicable lanes and synthesis;
8. block on regression, uncontrolled scope expansion, or incomplete evidence;
9. reassess all severities and dispositions.

High-risk remediation requires a fresh review context or independent lane. The
writer cannot certify its own repair alone.

Do not run full `ship` after every round. Reserve it for the final committed
candidate.

## Final-gate overlap

While final `ship --base <resolved-base>` runs, read-only drafting may prepare a
PR body, disposition table, and report skeleton from audited evidence. Treat all
drafts as provisional until final HEAD and issue-required tracking are fixed.

Do not push, mutate a PR, create issues, merge, or clean branches until shipment
is `NORMAL_GREEN`, successful legacy validation, or complete
`FAILED_PRE_EXISTING_BASELINE`. Issue mutations remain centralized afterward.

## Failure handling

- Failed or invalid preflight blocks the deep audit.
- Lane failure is recorded and rerun sequentially or blocks uncovered dimensions.
- Timeout/interruption is an audit-process blocker for that lane.
- Any tracked mutation during read-only work invalidates the packet.

## Worktree binding

Every lane uses the same canonical `TASK_ROOT` and immutable HEAD. External
registered worktrees are inspected by absolute path; no lane may call
`EnterWorktree` or create another worktree.
