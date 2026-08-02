# Risk-Based Remediation and Finding Disposition Policy

## Core principle

Severity and disposition are separate decisions.

- **Severity** describes impact: `P0`, `P1`, `P2`, or `P3`.
- **Disposition** describes what the current audit should do:
  - `FIX_NOW`
  - `DEFER_TO_ISSUE`
  - `ADD_TO_EXISTING_ISSUE`
  - `BATCH_INTO_CLEANUP_ISSUE`
  - `ACCEPT_AS_LOW_VALUE`
  - `DISMISS`
  - `BLOCK_ACCEPTANCE`

Every material finding must receive both. Never derive disposition mechanically
from severity alone. Record an evidence-based rationale before modifying code or
creating backlog.

Use `scripts/finding_disposition.py` or equivalent logic to validate each
proposed disposition.

## P0

P0 is an active or imminent catastrophic condition, including destructive or
irreversible data corruption, active compromise, material secret exposure,
large-scale cross-tenant exposure, complete production outage, or an imminent
destructive production state.

Required disposition:

- `FIX_NOW` when remediation is explicitly authorized and feasible; or
- `BLOCK_ACCEPTANCE` otherwise.

A P0 remains acceptance-blocking until the repair is independently reverified.
A future issue is not an acceptable substitute.

## P1

P1 is a material correctness, security, privacy, tenancy, data-integrity,
availability, or external-contract failure that makes the current implementation
unsafe to release.

Required disposition:

- `FIX_NOW` when repair is authorized, feasible, and consistent with an accepted
  design or requirement; or
- `BLOCK_ACCEPTANCE` otherwise.

Do not accept the implementation with an unresolved P1. Do not lower a P1 merely
to avoid current-scope remediation. A ticket alone does not clear acceptance.

High-risk P0/P1 remediation in security, authorization, tenancy, privacy,
migrations, data semantics, payments, destructive operations, or architecture
requires an independent post-remediation review lane. When the design itself is
ambiguous or unauthorized, block rather than guess.

## P2

P2 is risk-based. It is not automatically fixed and not automatically deferred.

### Prefer `FIX_NOW`

Use `FIX_NOW` when all or most of these conditions are supported:

- directly related to the changed execution path or behavior;
- introduced or exposed by the current change;
- self-contained and semantically bounded;
- no new architecture, migration, product capability, or broad refactor;
- clear acceptance criteria;
- deterministic verification;
- low or bounded regression risk;
- deferral would require reconstructing essentially the same context;
- prevents a realistic operational, security, privacy, reliability,
  maintainability, or user-facing problem;
- could plausibly become P1 in production;
- represents missing verification for important behavior introduced by the
  current change.

### Prefer an issue disposition

Use `DEFER_TO_ISSUE` or `ADD_TO_EXISTING_ISSUE` when one or more apply:

- unrelated or only tangentially related to the audited change;
- architectural redesign is required;
- migration or material data-model work is required;
- product scope expands;
- broad cross-component work is required;
- repair risk exceeds the present defect;
- the repair would obscure or materially enlarge the intended PR;
- it is an optimization without evidence of a current operational problem;
- it depends on a future decision, dependency, provider, or product requirement;
- it should be implemented and reviewed as a dedicated unit.

The report must state why each P2 was fixed now or deferred.

## P3

P3 does not automatically create an issue.

Use:

- `FIX_NOW` only when genuinely trivial, directly adjacent, behavior-preserving,
  and easy to verify;
- `BATCH_INTO_CLEANUP_ISSUE` when related findings collectively justify one
  future root-cause or cleanup outcome;
- `ADD_TO_EXISTING_ISSUE` when an equivalent issue already exists;
- `DEFER_TO_ISSUE` only when an individual concrete P3 passes every issue gate;
- `ACCEPT_AS_LOW_VALUE` when valid but not worth current work or permanent
  tracking cost;
- `DISMISS` when speculative, subjective, duplicate, outdated, irrelevant,
  unsupported, or non-actionable.

An individual P3 issue is allowed only when the desired outcome is concrete,
acceptance criteria are clear, value is credible, scheduling is realistic, and
consolidation is inferior.

## Findings required for acceptance

A finding required to satisfy the current ticket, acceptance criteria, or safe
release may use only:

- `FIX_NOW`; or
- `BLOCK_ACCEPTANCE`.

Do not hide an acceptance-critical gap under P2/P3 deferral, low-value acceptance,
or dismissal.

## Issue-creation gate

Before any new deferred issue is created, prove all seven:

1. **Actionable**: a clear defect or improvement and plausible remediation.
2. **Material enough**: impact justifies permanent backlog.
3. **Non-duplicative**: open and relevant closed issues were searched.
4. **Appropriately scoped**: one coherent outcome or shared root cause.
5. **Verifiable**: meaningful acceptance criteria can be written.
6. **Likely to be worked**: not merely an observation nobody expects to schedule.
7. **Better deferred than fixed now**: explain why deferral is safer or more
   efficient than bounded remediation.

If any condition fails, do not create a new issue. Choose another supported
disposition and explain it.

## Duplicate and consolidation rules

Before creating backlog:

- search by behavior, component, root cause, evidence terms, and acceptance
  outcome;
- add evidence to an equivalent open issue;
- use relevant closed issues as history, not active ownership;
- do not create multiple issues for repeated manifestations of one root cause;
- do not create one issue per file, line, typo, test gap, or cosmetic occurrence;
- use one coherent cleanup or root-cause issue when grouping has real economic
  value.

## Default issue budget

Below P1, normally create no more than **three new issues per audited change**.
Reused open issues do not consume this new-issue budget.

The budget does not authorize hiding material findings. Exceed it only when the
report explicitly explains for each excess issue:

- why it cannot be fixed now;
- why it cannot be grouped;
- why no existing issue is suitable;
- why it has independent engineering or product value.

## Scope control

Audit findings do not authorize unrestricted cleanup. Do not automatically
repair:

- unrelated legacy defects;
- general code-quality concerns outside the changed path;
- broad formatting or naming cleanup;
- optional architecture improvements;
- unrelated dependency upgrades;
- optional refactors or product enhancements;
- speculative performance optimization;
- repository-wide test cleanup.

Optimize for the smallest final change that is safe, correct, supportable, and
verifiable.

## Single-writer rule

Use exactly one remediation writer against the pinned `TASK_ROOT`. Parallel audit
lanes may review but must not edit, commit, generate overlapping outputs, or
mutate Git state concurrently.

## Remediation eligibility

A `FIX_NOW` candidate must be:

- authorized and feasible;
- directly related;
- semantically bounded;
- supported by clear acceptance criteria;
- deterministically verifiable;
- low or bounded regression risk;
- free of uncontrolled scope expansion.

P3 additionally requires trivial adjacency and behavior preservation. P2
requires evidence that immediate repair has meaningful contextual value.

Do not remediate merely to obtain green verification by weakening checks,
allowlists, baselines, applicability, thresholds, timeouts, or exit-code
behavior.

Verification machinery may change only when the actual finding is in that
machinery. Such a change is verification-governance-sensitive and requires
focused conformance evidence and the dedicated review lane.

## Bounded round process

At most three remediation rounds.

Before each round:

1. preserve original severity and proposed disposition;
2. snapshot HEAD, diff, tracked paths, deterministic evidence, and worktree
   state;
3. include only validated `FIX_NOW` findings;
4. preserve unrelated work;
5. state the exact repair and why it is bounded;
6. define the minimum evidence plan.

Apply eligible fixes without committing.

If the retained round changes tracked files:

1. run targeted validation selected by `minimal-sufficient-testing`;
2. reconcile every planned check as `PASS`, `FAIL`, `UNAVAILABLE`, `NOT RUN`, or
   `NOT APPLICABLE`;
3. rerun `./scripts/verify fast --base <resolved-base>` only when evidence was
   invalidated, repository policy requires it, or verification machinery changed;
4. in legacy mode, rerun only invalidated native validation;
5. for verification-governance changes, run focused conformance tests;
6. capture current HEAD, commands, output, and results;
7. build a fresh immutable audit packet;
8. rerun applicable read-only lanes and authoritative synthesis;
9. reassess every finding's severity and disposition;
10. update issue-ready records only for findings that still require tracking.

Do not run `./scripts/verify ship` after each remediation round. The full ship
profile is mandatory only for the final committed candidate.

## Post-remediation acceptance review

A repair is not accepted merely because the original finding disappeared.
Review the complete final diff and prove:

- the original finding is resolved;
- no new defect or regression was introduced;
- security, authorization, tenancy, privacy, and data-integrity boundaries were
  rechecked when relevant;
- required tests and verification pass;
- intended ticket and approved architecture remain satisfied;
- remediation did not introduce uncontrolled scope expansion.

Use `scripts/finding_disposition.py post-remediation` or equivalent logic.
High-risk repairs require a fresh review context or independent lane. The writer
must not be the sole acceptance authority.

## Regression handling

If a remediation round introduces a regression or uncontrolled scope expansion:

- revert only that round's attributable changes;
- preserve pre-round and unrelated work;
- never use destructive reset or clean;
- rerun targeted validation needed to prove restoration;
- stop or begin a materially different bounded round only when safe;
- report the failed attempt.

If three rounds do not converge, stop for human review.

## Retained records

For every `FIX_NOW` finding, record:

- finding and original severity;
- why immediate repair was appropriate;
- exact change;
- targeted validation;
- optional `fast` or legacy rerun;
- post-remediation independent review;
- round.

For every other finding, record disposition, rationale, and issue or evidence
reference when applicable. Do not report reverted attempts as retained fixes.

## Baseline-restoration interaction

`BASELINE_RESTORATION` does not relax this policy. It may retain bounded
`FIX_NOW` findings under the same rules, but cannot use the exception to absorb
new regressions or protected-domain failures.

When remediation changes the already-red lane or verification machinery:

1. run targeted validation;
2. rerun only the affected base-versus-branch comparison;
3. refresh the exact failure ledger;
4. re-audit the immutable state;
5. reject any `NEW_REGRESSION`, `UNATTRIBUTED`, untracked residual, or protected
   domain residual.

Do not repeatedly rerun to obtain a favorable sample or weaken the lane.
