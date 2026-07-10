# Remediation Policy

## Eligibility

Auto-fix only findings that are:

- unambiguous
- mechanical
- low risk
- within original scope
- safe without design judgment
- verifiable through re-audit

When uncertain, do not fix.

## Potentially safe fixes

- canonical formatting
- deterministic lint auto-fix
- unused imports
- dead code with no intended behavior
- accidental debug output
- stray temporary files
- unambiguous `.gitignore` entries
- factually incorrect comments/docs proven by code
- missing or incorrect test for already-correct behavior with an unambiguous assertion
- trivial bug with exactly one reasonable correction
- obvious typo where repository evidence proves intended value
- mechanical CI wiring explicitly marked ELIGIBLE by `minimal-sufficient-testing`

Small does not automatically mean safe.

## Never auto-fix

- authentication
- authorization
- tenancy
- ownership
- RLS
- privileged access
- security controls
- privacy
- secrets
- payments or entitlements
- destructive operations
- migrations
- retention policy
- public contracts
- architecture boundaries
- protected zones
- missing requirements
- multiple reasonable solutions
- product judgment
- ADR decisions
- materially uncertain findings
- branch-protection settings
- secrets, permissions, runners, cloud credentials, or deployment CI

## Round process

At most three rounds.

Before each round:

1. Record current findings.
2. Snapshot the current diff and files.
3. Identify eligible fixes.
4. Preserve unrelated changes.
5. State what will be changed and why it qualifies.

For test or CI gaps:

- invoke `minimal-sufficient-testing` in Implementation mode
- add only required tests
- wire CI only when marked ELIGIBLE
- respect stop conditions
- do not add broader coverage marked unnecessary

Apply fixes without committing.

Then rerun the complete audit on the same pinned audit model and effort.

A complete re-audit reconsiders all ten dimensions and reassesses the ledger. It does not automatically rerun every test.

## Regression handling

If a round introduces a new implementation finding:

- revert only that round's changes
- preserve pre-round and unrelated changes
- do not use destructive Git reset
- stop remediation
- report the failed attempt
- continue to the shipment gate using the restored pre-round state

If no eligible finding remains, stop.

If three rounds do not converge, stop for human review.

## Retained fix record

For each retained fix, record:

- finding
- change
- why safe
- validation
- round

Do not report reverted attempts as retained fixes.
