# Finding and Verdict Policy

## Separate implementation findings from audit-process notes

### Implementation findings

Repository or change defects, including:

- incorrect behavior
- missing requirement
- security weakness
- missing required test
- missing CI enforcement
- missing contract update
- regression
- risky assumption
- maintainability problem

These receive P0-P3 priority.

### Audit-process notes

Audit execution limitations, including:

- command produced unexpected tracked output
- prior evidence was poorly recorded
- tool or environment unavailable
- redundant command already ran
- logs inaccessible
- repository metadata ambiguous

Do not turn these into implementation findings unless they reveal a real repository defect.

## Priorities

### P0 — Critical blocker

Examples:

- exploitable security failure
- cross-tenant exposure
- destructive data-loss risk
- unrecoverable migration failure
- severe outage risk
- materially incorrect payment behavior
- implementation fundamentally fails the objective

Blocks shipment.

### P1 — Must fix before shipment

Examples:

- core requested behavior incorrect or missing
- important authorization boundary broken or unvalidated
- critical regression
- material data-integrity issue
- primary workflow lacks direct validation
- Low testing confidence
- critical required CI enforcement is absent, when CI is required (not
  merely that the repository has no CI as an accepted state)
- migration or rollback materially unsafe
- repository-required quality gate can be bypassed

Blocks shipment.

### P2 — Should fix soon

Examples:

- meaningful non-blocking regression risk
- non-critical failure-path gap
- maintainability issue likely to create defects
- important documentation or operational gap
- meaningful non-critical test exists but is not enforced in the
  repository's existing CI (not applicable when the repository has no CI as
  an accepted state)
- actionable behavior gap safe to ship temporarily

Does not automatically block shipment.

### P3 — Minor follow-up

Examples:

- polish
- minor docs improvement
- low-probability resilience
- small cleanup
- optional maintainability improvement

Must be actionable. Do not invent findings to appear thorough.

## Verdicts

### PASS

Use only when:

- objective satisfied
- no P0-P3 implementation finding remains
- testing confidence High
- required CI enforcement present, when CI is required (a repository with no
  CI as an accepted state satisfies this by definition)
- no material audit limitation

### PASS WITH GAPS

Use when:

- core objective satisfied
- no P0 or P1 remains
- testing confidence High or Moderate
- one or more P2/P3 findings or named non-critical limitations remain

Moderate confidence always means PASS WITH GAPS, not PASS.

### FAIL

Use when:

- P0 or P1 remains
- objective not satisfied
- testing confidence Low
- testing stop condition triggered
- CI enforcement is required and critical enforcement is absent
- unexplained validation failure remains

### AUDIT BLOCKED

Use when review cannot begin reliably because objective, scope, repository state, or required input is unavailable.

## Recommended action

Choose one:

- MERGE
- FIX FIRST
- SPLIT FOLLOW-UP
- REVERT
- MANUAL REVIEW
