---
name: minimal-sufficient-testing
description: Determine the smallest risk-weighted body of test evidence needed for a code change. Reuse trustworthy validation already completed, invalidate stale evidence, identify remaining coverage gaps, assess CI enforcement, and recommend or execute only the tests needed to reach justified confidence.
user-invocable: true
---

# Minimal Sufficient Testing

Determine the smallest credible body of evidence that gives strong confidence a code change is correct, safe, and maintainable.

Do not test everything. Do not skip important testing to save time. Do not rerun trustworthy evidence merely for ceremony.

## Authority

This skill is the authority for:

- prior test-evidence validation
- evidence reuse and invalidation
- change-risk classification
- coverage-gap identification
- test-layer selection
- deciding what must run or rerun
- deciding whether permanent tests are required
- deciding whether CI enforcement is required
- stopping conditions
- testing confidence

Other skills may supply objectives, diffs, findings, or an initial evidence ledger. They must not replace this decision framework.

## Required supporting files

Read these before producing a final decision:

- `evidence-policy.md`
- `risk-and-coverage-policy.md`
- `output-format.md`

## Operating modes

### Plan mode

Use when asked what tests should be added or run.

- Inspect the change when repository access is available.
- Produce a testing decision.
- Do not modify code.
- Do not execute commands unless execution was explicitly requested.

### Validate mode

Use when invoked by a read-only audit.

- Inspect the repository and change.
- Validate prior evidence.
- Execute required existing checks when necessary.
- Do not add or edit tests.
- Do not intentionally modify tracked files.
- Return missing tests or CI enforcement as coverage gaps.

If a validation command unexpectedly modifies a tracked file, stop and report it. Do not silently overwrite or broadly restore user work.

### Implementation mode

Use when an implementation or remediation workflow explicitly authorizes test changes.

- Validate prior evidence.
- Identify remaining gaps.
- Add or update only tests required by this decision.
- Mechanically wire an existing passing command into existing CI only when the CI policy in `risk-and-coverage-policy.md` marks it eligible.
- Execute targeted validation.
- Avoid unrelated production-code changes.

## Required inputs

Establish:

1. Original objective.
2. Current diff, commit range, PR, or changed-file set.
3. Current code state.
4. Repository scripts and testing conventions.
5. Existing related tests.
6. Prior evidence supplied by the current session or caller.
7. Known audit findings, when applicable.
8. Environmental limitations.
9. Existing CI workflows and which commands they enforce.

If the changed behavior or objective cannot be identified, stop instead of generating a generic test plan.

## Process

1. Identify the exact code state.
2. Build and validate the evidence ledger.
3. Analyze changed behavior and boundaries.
4. Assign Low, Medium, or High risk.
5. Determine applicable evidence obligations.
6. Identify uncovered requirements and risks.
7. Select the narrowest effective test layer.
8. Determine whether the protection must be permanent and enforced in CI.
9. Execute or prescribe only the missing work.
10. Apply stop conditions.
11. Assign High, Moderate, or Low confidence.
12. Produce the required output.

## Core stopping rule

Testing is sufficient when all applicable conditions are true:

- the requested behavior is directly validated
- the primary happy path is covered
- the dominant failure path is covered
- likely regression surfaces are checked
- applicable security and data-integrity boundaries are directly validated
- meaningful repository quality gates have current passing evidence
- required CI enforcement exists, is explicitly identified as a gap when CI is required, or the repository has no CI as an accepted state
- prior evidence was reviewed for continued validity
- no unexplained failure or material uncertainty remains

Stop there. Do not continue generating low-value tests for increasingly remote edge cases.
