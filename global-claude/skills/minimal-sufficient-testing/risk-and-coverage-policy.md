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

## CI enforcement assessment

First classify the repository's CI state.

### No CI configured

The repository has no CI workflows or checks configured at all, and none of
the following apply: the user explicitly requested CI, repository governance
explicitly requires CI, or the current task specifically includes
establishing CI.

Treat this as an intentional, accepted repository state, not a gap:

- Record it as `NOT CONFIGURED — ACCEPTED REPOSITORY STATE`.
- Do not report an enforcement gap.
- Do not recommend or create CI.
- This alone must not lower confidence, create a P0-P3 finding, or require
  manual review.

### CI exists, or is explicitly required

For every required permanent test or quality gate, determine:

- whether CI enforcement is required
- whether CI currently runs it
- which workflow/job owns it
- whether missing enforcement is mechanical to add
- whether branch protection requires manual review

CI enforcement is normally required when the test protects:

- security or authorization
- tenancy
- payments
- migrations
- data integrity
- destructive operations
- critical workflows
- public contracts
- regressions that must never return
- repository-mandated quality gates

Report missing critical enforcement according to the existing finding
priority policy. Mechanically add a missing check only when Automatic CI
wiring eligibility below permits it.

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

- add or rotate secrets
- change workflow permissions
- introduce `pull_request_target`
- add unclear third-party actions
- configure self-hosted runners
- add cloud credentials
- redesign CI
- change deployment/release workflows
- change branch-protection settings
- make a status check required in repository settings
- choose among multiple reasonable CI architectures

Branch-protection gaps must be reported for manual repository-setting review.

## Stop conditions

Stop with Low confidence when:

- objective or behavior cannot be identified
- persistence changed without integration-level or equivalent validation
- authorization changed without negative-access validation
- tenancy changed without cross-tenant denial validation
- a bug fix lacks regression evidence and no credible omission justification exists
- related tests fail
- required lint, typecheck, static, or build checks fail
- required infrastructure is unavailable
- test behavior is nondeterministic
- unexplained failure remains
- critical requirement lacks direct validation
- CI enforcement is required (CI exists, or is explicitly required) and
  critical enforcement is absent and cannot be mechanically added

## Confidence

### High

- critical behavior directly validated
- dominant failures covered
- relevant regressions covered
- applicable boundaries validated
- required CI enforcement present, when CI is required (a repository with no
  CI as an accepted state satisfies this by definition and may still be High)
- evidence current and trustworthy
- no material limitation

### Moderate

- core behavior validated
- no critical required test missing
- a named non-critical environment, tooling, evidence, or CI limitation
  remains - this means CI exists or is required and has a real, named
  limitation, never merely that the repository has no CI as an accepted
  state

Moderate confidence must state the limitation precisely.

### Low

- important behavior unvalidated
- stop condition triggered
- critical evidence stale, unavailable, failed, or missing
- CI enforcement is required and critical enforcement is absent
- material unexplained uncertainty remains
