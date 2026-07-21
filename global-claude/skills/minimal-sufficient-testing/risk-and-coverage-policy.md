# Risk, Coverage, and CI Policy

## Analyze the change

Determine:

1. Behavior added, changed, removed, or fixed.
2. Externally observable contract.
3. Existing behavior that could regress.
4. Touched files, modules, interfaces, schemas, workflows, and dependencies.
5. User-visible impact.
6. Persistence and data-transition impact.
7. Authentication, authorization, roles, ownership, tenancy, privacy, or sensitive-data impact.
8. External services, APIs, queues, jobs, workers, webhooks, emails, payments, files, or generated-content impact.
9. Critical product-journey impact.
10. Bug-regression risk.
11. Production consequence if wrong.
12. Existing nearby test protection.
13. Existing CI enforcement.

## Risk classification

### Low

Typical:

- isolated logic
- narrow presentation behavior
- documentation-only change
- no persistence or external boundary
- low blast radius
- easy rollback
- visible non-destructive failure

### Medium

Typical:

- shared component or service behavior
- API behavior
- user-facing workflow
- limited persistence
- moderate regression surface
- bounded async behavior
- stable external boundary
- recoverable user disruption

### High

Typical:

- authentication or authorization
- tenancy or ownership
- security or privacy controls
- payments or entitlements
- destructive operations
- migrations
- data-loss or corruption risk
- critical workflow
- public API compatibility
- external side effects
- retry, replay, or idempotency correctness
- privileged access
- broad shared infrastructure
- difficult rollback
- silent or irreversible failure

Risk and confidence are independent.

## Minimum evidence obligations

Combined reused, rerun, and new evidence must cover each applicable obligation.

### Requested behavior

Directly validate what was asked.

A build or lint result does not prove the feature works.

### Happy path

Validate the primary intended use from the caller, consumer, or user perspective.

### Primary failure path

Validate the most probable or consequential failure for the actual change.

Examples:

- invalid input
- missing data
- unauthorized access
- dependency failure
- rejected transition
- persistence failure
- duplicate operation
- replay
- malformed file
- retry exhaustion

### Regression protection

Validate existing behavior most likely to be broken by the changed surface.

### Security and boundary behavior

Directly validate applicable boundaries:

- authentication
- authorization
- ownership
- tenancy
- RLS
- privileged access
- sensitive data
- payments
- destructive operations
- migrations
- webhook verification
- idempotency
- file validation
- queue retry or replay
- public API compatibility

Static checks are not substitutes.

### Repository quality gates

Discover actual repository commands for:

- formatting
- lint
- type checking
- targeted automated tests
- static analysis
- build or compile

Do not invent commands when repository-defined commands exist.

## Test selection order

Prioritize:

1. Original requirements not directly validated.
2. Critical journeys.
3. Security, authorization, tenancy, privacy, and data integrity.
4. Realistic regressions.
5. Common failure conditions.
6. Edge cases with meaningful likelihood or impact.

Deprioritize:

- Verified reusable evidence
- duplicate tests at the same contract layer
- broad unrelated suites when targeted checks suffice
- implementation-detail tests when behavior is the contract
- cosmetic snapshots
- improbable low-impact combinations
- speculative scenarios
- tests added only to increase coverage

## Test-layer selection

Prefer:

- static checks for structural invariants
- unit tests for isolated deterministic logic
- component tests for contained UI behavior
- integration tests for persistence and service boundaries
- contract tests for interface compatibility
- authorization tests for access control
- migration tests for data and schema transitions
- worker/queue tests for retry, replay, and idempotency
- mocked provider-boundary tests for external services
- end-to-end tests for critical workflows
- regression tests for bug fixes
- specific manual verification for low-value visual behavior

Choose the narrowest layer that directly protects the highest-risk behavior.

## Permanent-test rule

Add or update an automated test when:

- the behavior can realistically regress
- failure matters enough to block shipping
- existing tests are inadequate
- prior execution evidence is insufficient
- expected behavior is clear
- the test can be deterministic without disproportionate complexity

Do not invent product requirements through tests.

## Manual validation

Manual verification must specify:

- setup
- action
- expected result
- failure signal

Manual-only validation is insufficient for repeatable critical behavior involving authorization, tenancy, privacy, data integrity, payments, migrations, destructive operations, idempotency, or critical backend workflows.

## Evidence-plan reconciliation

Before executing missing validation, record the minimum evidence plan for the
actual change. The plan must identify:

- each behavior or boundary to prove;
- the command or procedure that will prove it;
- the code state to which the result must bind;
- whether the check is required, advisory, or not applicable;
- the failure signal.

After execution, classify every planned item as:

- `PASS`;
- `FAIL`;
- `UNAVAILABLE`;
- `NOT RUN`;
- `NOT APPLICABLE`.

Do not claim completion while a required item is `UNAVAILABLE` or `NOT RUN`.
Repository Verification planned-versus-executed reconciliation may satisfy this
for checks declared by the adapter, but the independent testing assessment must
still add any change-relevant obligations the repository omitted.

## Three independent outputs

Never collapse these decisions:

1. **Testing confidence** — whether the exact audited implementation is directly
   and sufficiently proven.
2. **CI enforcement confidence** — whether required permanent protections are
   durably enforced by CI.
3. **Provisional merge impact** — whether the evidence and CI posture suggest
   automatic merge, manual merge, or blocking, subject to the orchestrator's
   repository-specific policy and live PR state.

CI enforcement cannot substitute for direct testing. Conversely, a CI
architecture limitation cannot erase valid direct evidence.

## Exact-code-state evidence contract

A documented repository-wide CI coverage limitation must not reduce testing
confidence when all applicable conditions are true:

- `./scripts/verify ship --base <resolved-base>` passed for the exact audited
  commit when Repository Verification V1 is present;
- the working tree remained clean after the gate;
- no commit was added afterward;
- every change-relevant high-risk check was directly executed and passed;
- planned and executed evidence reconcile;
- no required check failed, remained unavailable, or was omitted;
- no local-versus-CI contradiction or other material uncertainty remains.

For a legacy repository without `./scripts/verify`, apply the same principle to
the repository's existing final validation evidence. Adapter absence is not a
confidence penalty.

When the contract is satisfied, testing confidence may be `HIGH` even if CI
cannot run a Docker-backed integration suite, browser suite, service-dependent
suite, or another documented repository-wide check. Report the enforcement gap
separately.

A failed CI check or unexplained local-versus-CI disagreement may lower testing
confidence because it creates conflicting evidence. The cause is the unresolved
conflict, not the mere fact that CI coverage is incomplete.

## CI enforcement assessment

First classify the repository's CI state.

### No CI configured

The repository has no CI workflows or checks configured at all, and none of
the following apply: the user explicitly requested CI, repository governance
explicitly requires CI, or the current task specifically includes
establishing CI.

Treat this as an intentional, accepted repository state:

- Record CI state as `NOT CONFIGURED — ACCEPTED REPOSITORY STATE`.
- Record CI enforcement confidence as `NOT_APPLICABLE`.
- Do not report an enforcement gap.
- Do not recommend or create CI.
- This alone must not lower testing confidence, create a P0-P3 finding, require
  manual review, or block automatic merge.

### CI exists or is explicitly required

For every required permanent test or quality gate, determine:

- whether CI enforcement is required;
- whether CI currently runs it;
- which workflow or job owns it;
- whether the gap is change-specific or a documented repository-wide
  architecture limitation;
- whether repository policy accepts the limitation and what merge effect it
  specifies;
- whether missing enforcement is mechanical to add;
- whether branch protection requires manual review.

CI enforcement is normally required when the check protects:

- security or authorization;
- tenancy;
- payments;
- migrations;
- data integrity;
- destructive operations;
- critical workflows;
- public contracts;
- regressions that must never return;
- repository-mandated quality gates.

### CI enforcement confidence

#### HIGH

All required permanent checks are enforced in CI, or repository policy
explicitly defines an equivalent durable enforcement mechanism.

#### MODERATE

A documented, accepted repository-wide CI architecture limitation leaves one or
more required checks local-only, while the exact-code-state evidence contract
is satisfied.

This does not lower testing confidence. Report the exact limitation and its
repository-policy merge impact. By default, require manual merge unless
repository policy explicitly permits automatic merge with that limitation.

#### LOW

Required enforcement is missing, unknown, newly weakened, or not covered by an
accepted documented limitation. This may be a change finding and normally
blocks automatic merge until repository policy resolves it.

#### NOT_APPLICABLE

CI is not configured and that state is explicitly accepted as described above.

## Automatic CI wiring eligibility

In Implementation mode, an existing passing command may be wired into an existing CI workflow only when all are true:

1. The command already exists.
2. It passes locally or in equivalent validation.
3. The repository already has a clear analogous CI pattern.
4. The target job/workflow is unambiguous.
5. No new secrets or credentials are required.
6. No permission changes are required.
7. No new runner, service container, database, or cloud infrastructure is required.
8. No deployment or release behavior changes.
9. No material CI architecture choice is required.
10. Runtime and cost impact are small and obvious.
11. The workflow change can be re-audited.
12. The new check can be observed on the PR.

Mark such a change `ELIGIBLE`.

Otherwise mark it `NOT ELIGIBLE` and report it.

Never automatically:

- add or rotate secrets;
- change workflow permissions;
- introduce `pull_request_target`;
- add unclear third-party actions;
- configure self-hosted runners;
- add cloud credentials;
- redesign CI;
- change deployment or release workflows;
- change branch-protection settings;
- make a status check required in repository settings;
- choose among multiple reasonable CI architectures.

Branch-protection gaps must be reported for manual repository-setting review.

## Testing stop conditions

Stop with `LOW` testing confidence when:

- objective or behavior cannot be identified;
- persistence changed without integration-level or equivalent validation;
- authorization changed without negative-access validation;
- tenancy changed without cross-tenant denial validation;
- a bug fix lacks regression evidence and no credible omission justification exists;
- related tests fail;
- required lint, typecheck, static, or build checks fail;
- required infrastructure is unavailable for a change-relevant required check;
- test behavior is nondeterministic;
- planned and executed evidence do not reconcile;
- a required check is unavailable or not run;
- unexplained failure or conflicting local-versus-CI evidence remains;
- a critical requirement lacks direct validation;
- the exact audited code state cannot be established.

Do not lower testing confidence solely because a documented accepted CI
coverage limitation exists.

## Testing confidence

### HIGH

- critical behavior directly validated;
- dominant failures covered;
- relevant regressions covered;
- applicable boundaries validated;
- all change-relevant high-risk checks directly executed;
- evidence plan reconciled;
- evidence current, trustworthy, and bound to the exact audited code state;
- no material testing limitation or evidence conflict remains.

### MODERATE

- core behavior validated;
- no critical required test missing;
- a named non-critical environment, tooling, or evidence limitation remains.

A CI enforcement limitation by itself is not a testing-confidence limitation.
Moderate testing confidence must state the actual testing uncertainty precisely.

### LOW

- important behavior unvalidated;
- a testing stop condition triggered;
- critical evidence stale, unavailable, failed, missing, or bound to a different
  code state;
- material unexplained uncertainty remains.

## Provisional merge impact

Return one of:

- `AUTO_MERGE_ELIGIBLE` — testing confidence is High and no CI enforcement or
  policy limitation requires manual handling;
- `MANUAL_MERGE_REQUIRED` — testing confidence is Moderate, or a documented
  accepted CI limitation requires manual merge under repository policy;
- `BLOCKED` — testing confidence is Low, CI enforcement confidence is Low, or a
  required gate fails;
- `PENDING_PR_AND_CI` — the audit evidence is complete but live PR/CI state is
  not yet available.

This is advisory to the parent. `audit-and-pr` owns the final merge decision and
must still apply live CI, review, protection, exact-SHA, and repository-specific
merge policy.
