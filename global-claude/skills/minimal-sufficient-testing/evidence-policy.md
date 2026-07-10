# Evidence Policy

## Identify the code state

Record:

- repository
- branch
- current commit SHA
- clean or dirty working tree
- audited diff or commit range
- relevant untracked files
- concise changed-file list

For a clean tree, the commit SHA is normally sufficient.

For a dirty tree, also record:

- `git status --short`
- relevant changed files
- whether each evidence item ran before or after the current working-tree changes

“Materially equivalent” must be demonstrated, not assumed.

## Evidence sources

Inspect:

- exact terminal commands and outputs
- CI results
- test reports
- build logs
- browser or manual-validation records
- defect reproduction and post-fix confirmation
- implementation transcripts
- prior audit output
- commit messages
- PR descriptions

Commit messages, PR descriptions, and narrative summaries are discovery sources. They are not proof by themselves.

## Ledger fields

For each entry record:

- category
- command or procedure
- result
- code state
- environment or configuration
- behavior or risk covered
- source
- status
- reason

## Evidence statuses

### Verified reusable

The execution and result are identifiable, current, complete, and appropriate.

Count it without rerunning.

### Verified but stale

The execution is real, but a later relevant change invalidated it.

Do not count it until rerun or replaced.

### Claim only

A narrative says it ran, but exact execution or result is unavailable.

Do not count it.

### Failed

A verifiable execution failed.

Treat it as unresolved until explained and corrected.

### Not applicable

The category genuinely does not apply.

### Required but unavailable

The validation materially matters but cannot be performed because of missing infrastructure, access, environment, data, or tooling.

This normally reduces confidence and may trigger a stop condition.

## Reuse requirements

Classify evidence as Verified reusable only when all are true:

1. Exact command, test, or procedure is identifiable.
2. Result is clearly recorded.
3. Execution completed.
4. It ran against the current or demonstrably equivalent code state.
5. No later relevant change invalidated it.
6. Relevant dependencies, configuration, environment, schema, and database state match.
7. It directly or appropriately supports the requirement or risk.
8. It was not skipped, interrupted, inferred, or accepted only from a summary.

Do not rerun Verified reusable evidence merely because it appears in a checklist.

## Invalidation rules

Mark evidence stale when:

- relevant production code changed afterward
- relevant test code changed afterward
- it ran before the final fix
- command or result is unverifiable
- branch, commit, worktree, environment, or configuration differs materially
- dependencies changed materially
- schema or migration state changed
- generated code or assets changed
- runtime configuration changed
- the run was partial, flaky, interrupted, skipped, or ambiguous
- it validates only an implementation detail instead of the observable contract
- a new finding exposes an uncovered risk
- repository policy requires a fresh final aggregate gate
- rerunning a cheap critical check is cheaper than the uncertainty

Invalidate narrowly.

A documentation change does not invalidate unrelated integration evidence. A localized code fix does not automatically invalidate every test suite.
