# Remediation Policy

## Severity boundary

Severity determines disposition before mechanical-fix eligibility is considered.

- Only confirmed P0/P1 implementation findings may enter remediation.
- Confirmed P2/P3 findings are never modified by `/audit-and-pr`, even when a
  change looks mechanical, low risk, or easy to validate.
- An unresolved P0/P1 remains a shipment blocker and may not be converted into a
  backlog issue merely because remediation is difficult.
- Never lower a finding to P2/P3 to avoid current-scope remediation.
- If a finding is necessary to satisfy the current objective or acceptance
  criteria, it cannot be deferred as P2/P3. Reclassify it as blocking or mark the
  objective unsatisfied.
- Audit-process notes and unconfirmed speculation are reported as limitations or
  notes; they are neither remediated nor converted into implementation tickets.

Use `scripts/finding_disposition.py` or equivalent logic to make this decision
before any file modification.

## P0/P1 remediation eligibility

For P0/P1 findings only, remediate when the correction is:

- unambiguous;
- mechanical;
- low risk;
- within original scope;
- safe without design judgment;
- verifiable through targeted validation and independent re-audit.

When uncertain, do not fix. The unresolved P0/P1 blocks shipment.

## Potentially safe P0/P1 fixes

- canonical formatting required to clear a blocking repository gate;
- deterministic lint auto-fix;
- unused imports causing a blocking build or lint failure;
- dead code with no intended behavior when directly tied to the blocker;
- accidental debug output;
- stray temporary files;
- unambiguous `.gitignore` entries;
- factually incorrect comments/docs proven by code when the error is blocking;
- missing or incorrect test for already-correct behavior with an unambiguous
  assertion;
- trivial blocking bug with exactly one reasonable correction;
- obvious typo where repository evidence proves intended value;
- mechanical CI wiring explicitly marked ELIGIBLE by
  `minimal-sufficient-testing`.

Small does not automatically mean safe. P2/P3 findings remain deferred even when
one of these descriptions appears to fit.

## Never auto-fix

- any P2 or P3 finding;
- authentication;
- authorization;
- tenancy;
- ownership;
- RLS;
- privileged access;
- security controls;
- privacy;
- secrets;
- payments or entitlements;
- destructive operations;
- migrations;
- retention policy;
- public contracts;
- architecture boundaries;
- protected zones;
- missing requirements;
- multiple reasonable solutions;
- product judgment;
- ADR decisions;
- materially uncertain findings;
- branch-protection settings;
- secrets, permissions, runners, cloud credentials, or deployment CI.

Never remediate merely to obtain green verification by:

- making a blocking check advisory;
- broadening an allowlist without narrowly proven need;
- adding a blanket baseline;
- disabling or skipping tests;
- weakening applicability rules;
- lowering a threshold or timeout without evidence;
- suppressing planned-versus-executed reconciliation;
- changing exit-code behavior to hide a blocker.

Verification machinery may be changed only when the actual P0/P1 finding is in
that machinery. Such a change is verification-governance-sensitive and requires
focused conformance evidence plus independent review.

## Deferred P2/P3 ledger

After authoritative audit synthesis, create one normalized ledger entry for each
confirmed P2/P3 implementation finding. Each entry must contain enough
information to create or match a durable GitHub issue:

- stable finding identifier;
- priority;
- concise title;
- observed gap and evidence;
- user, system, security, operational, or maintainability risk;
- affected paths or components;
- exact audited branch and commit;
- acceptance criteria;
- minimum validation plan;
- audit origin;
- candidate equivalent-issue search terms.

Do not edit code for these findings. Do not let parallel audit lanes create
issues independently. The synthesis lead owns deduplication and the tracking
ledger.

A P2/P3 may remain in the final audit only when it is genuinely non-blocking and
independently closeable. The audit verdict is `PASS WITH GAPS`, not `PASS`.

## Single-writer rule

Use exactly one remediation writer against one worktree. Parallel audit lanes
may review the result, but no second worker may edit files, generate overlapping
outputs, commit, or mutate Git state concurrently.

## Round process

At most three rounds.

Before each round:

1. record current findings and preserve their original severity;
2. snapshot the current diff, tracked paths, HEAD, deterministic preflight
   evidence, and legacy/adapter mode;
3. exclude every P2/P3 from the remediation candidate set;
4. identify eligible P0/P1 fixes;
5. preserve unrelated changes;
6. state what will be changed and why it qualifies;
7. define the minimum evidence plan for the exact P0/P1 findings being corrected.

For blocking test or CI gaps:

- invoke `minimal-sufficient-testing` in Implementation mode;
- add only required tests;
- wire CI only when marked ELIGIBLE;
- respect stop conditions;
- do not add broader coverage marked unnecessary.

Apply eligible P0/P1 fixes without committing.

If the retained round changes tracked files:

1. run targeted validation selected by `minimal-sufficient-testing`;
2. reconcile every planned check as `PASS`, `FAIL`, `UNAVAILABLE`, `NOT RUN`, or
   `NOT APPLICABLE`;
3. rerun `./scripts/verify fast --base <resolved-base>` only when the change
   invalidates prior fast evidence, repository policy requires it, or
   verification machinery changed;
4. when the adapter is absent, rerun only the legacy validation invalidated by
   the changes;
5. for verification-governance changes, run focused conformance tests and
   activate the dedicated governance audit lane;
6. capture current HEAD, commands, outputs, and results;
7. stop on any required validation or evidence-reconciliation blocker;
8. build a fresh immutable audit packet for the new state;
9. rerun the applicable read-only audit lanes and authoritative synthesis using
   the same pinned audit model and effort;
10. confirm that P2/P3 findings remained unmodified and refresh their issue-ready
    ledger entries if evidence or affected paths changed.

Do not run `./scripts/verify ship` after each remediation round. The full ship
profile is mandatory only after the final audited scope is committed. Targeted
validation and risk-triggered `fast` provide the in-loop feedback.

A complete re-audit reconsiders all ten dimensions and reassesses the ledger.
Parallel lanes may perform those dimensions concurrently, but the synthesis is
single and authoritative. The re-audit does not automatically rerun every test.

## Validation concurrency

Independent validation commands may run concurrently only when repository
policy or `minimal-sufficient-testing` proves they do not contend for shared
ports, databases, Docker state, generated files, build directories, snapshots,
coverage output, browser state, or other mutable resources. Otherwise run them
sequentially.

## Regression handling

If a round introduces a new implementation finding:

- revert only that round's changes;
- preserve pre-round and unrelated changes;
- do not use destructive Git reset;
- rerun targeted validation needed to prove restoration;
- rerun `fast` only if the restoration invalidated its evidence or repository
  policy requires it;
- stop remediation;
- report the failed attempt;
- continue to audit eligibility only from the restored, revalidated, re-audited
  pre-round state.

If no eligible P0/P1 finding remains, stop remediation. P2/P3 findings are not a
reason to start or continue a remediation round.

If three rounds do not converge on P0/P1 findings, stop for human review.

## Retained fix record

For each retained P0/P1 fix, record:

- finding and original priority;
- change;
- why safe;
- targeted validation;
- any risk-triggered `fast` or legacy revalidation result;
- independent re-audit result;
- round.

For each P2/P3, record `DEFERRED — CODE UNCHANGED` plus its tracking-ledger
identifier. Do not report reverted attempts as retained fixes.

## Confidence separation during remediation

Do not lower testing confidence merely because a documented accepted
repository-wide CI limitation remains after a remediation round. Testing
confidence follows direct evidence for the exact remediated state. Final High
confidence remains contingent on the final exact-HEAD ship or legacy gate. CI
enforcement confidence and merge eligibility are reported separately.
