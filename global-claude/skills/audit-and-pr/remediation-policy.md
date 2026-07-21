# Remediation Policy

## Eligibility

Auto-fix only findings that are:

- unambiguous;
- mechanical;
- low risk;
- within original scope;
- safe without design judgment;
- verifiable through repository revalidation and independent re-audit.

When uncertain, do not fix.

## Potentially safe fixes

- canonical formatting;
- deterministic lint auto-fix;
- unused imports;
- dead code with no intended behavior;
- accidental debug output;
- stray temporary files;
- unambiguous `.gitignore` entries;
- factually incorrect comments/docs proven by code;
- missing or incorrect test for already-correct behavior with an unambiguous
  assertion;
- trivial bug with exactly one reasonable correction;
- obvious typo where repository evidence proves intended value;
- mechanical CI wiring explicitly marked ELIGIBLE by
  `minimal-sufficient-testing`.

Small does not automatically mean safe.

## Never auto-fix

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

Verification machinery may be changed only when the actual finding is in that
machinery. Such a change is verification-governance-sensitive and requires
focused conformance evidence plus independent review.

## Round process

At most three rounds.

Before each round:

1. record current findings;
2. snapshot the current diff, tracked paths, HEAD, and latest Repository
   Verification result or legacy mode;
3. identify eligible fixes;
4. preserve unrelated changes;
5. state what will be changed and why it qualifies.

For test or CI gaps:

- invoke `minimal-sufficient-testing` in Implementation mode;
- add only required tests;
- wire CI only when marked ELIGIBLE;
- respect stop conditions;
- do not add broader coverage marked unnecessary.

Apply fixes without committing.

Before each remediation round, record the minimum evidence plan for the exact
findings being corrected. The plan must identify targeted checks, expected
results, and code-state binding.

If the retained round changes tracked files:

1. run targeted validation selected by `minimal-sufficient-testing`;
2. reconcile every planned check as PASS, FAIL, UNAVAILABLE, NOT RUN, or NOT APPLICABLE;
3. rerun `./scripts/verify ship --base <resolved-base>` when the adapter is
   present;
4. when the adapter is absent, rerun the legacy validation invalidated by the
   changes;
5. capture the current HEAD, exact command, output, counts, and result;
6. stop on any verification or evidence-reconciliation blocker; never fall back after adapter failure;
7. rerun the complete independent audit on the same pinned audit model and
   effort.

A complete re-audit reconsiders all ten dimensions and reassesses the ledger.
It does not automatically rerun every test.

Do not rely on a successful Repository Verification result from before tracked
files changed.

## Regression handling

If a round introduces a new implementation finding:

- revert only that round's changes;
- preserve pre-round and unrelated changes;
- do not use destructive Git reset;
- rerun the applicable verification if the restoration changed tracked files;
- stop remediation;
- report the failed attempt;
- continue to the audit eligibility gate only from the restored, revalidated
  pre-round state.

If no eligible finding remains, stop.

If three rounds do not converge, stop for human review.

## Retained fix record

For each retained fix, record:

- finding;
- change;
- why safe;
- targeted validation;
- Repository Verification or legacy revalidation result;
- independent re-audit result;
- round.

Do not report reverted attempts as retained fixes.

## Confidence separation during remediation

Do not lower testing confidence merely because a documented accepted
repository-wide CI limitation remains after a remediation round. Testing
confidence follows the direct evidence for the exact remediated code state. CI
enforcement confidence and merge eligibility are reported separately.
