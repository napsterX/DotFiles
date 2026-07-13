# Testing and Validation

- Every runtime behavior change needs automated coverage proportional to its risk and failure mode. Documentation-only, comment-only, and type-only changes do not require artificial tests.
- Every bug fix needs a regression test that would fail on the old behavior and pass after the fix. Exercise the same runtime layer or user path where the defect occurred; helper-only or source-pattern tests are insufficient when the defect lived higher in the stack.
- Test success, expected failure, and important edge cases. For authorization changes, test both allowed and denied access. For multi-tenant systems, include cross-tenant denial. For stateful workflows, test invalid transitions and recovery where relevant.
- For asynchronous work, test idempotency, retry classification, duplicate execution, timeout or lease recovery, and terminal failure handling when those behaviors exist.
- Use integration tests for database constraints, transactions, migrations, triggers, and access policies when unit tests cannot prove the behavior.
- Add or update browser/E2E coverage when a new or materially changed critical user workflow cannot be validated adequately below the browser layer. Do not require E2E merely for every copy or cosmetic change.
- Tests must be deterministic, isolated, and based on synthetic data. Unit tests must not make real network calls.
- Discover and use the repository's real validation commands; do not invent script names. Run the narrowest relevant tests during implementation and the repository-required gates before completion.
- When practical, record a pre-change baseline before broad or risky work. Distinguish failures introduced by the change from verified pre-existing failures; never label a failure pre-existing without evidence.
- Do not delete, disable, weaken, or rewrite valid tests merely to make the suite pass. Do not weaken compiler, linter, or security settings to hide defects.
