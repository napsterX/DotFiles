# Verification and Retry Policy

## Objective

Prove that an issue is fixed before retaining a commit. Use a bounded
implement -> verify -> review -> repair -> reverify loop. Never equate a source
change with issue resolution.

## Acceptance proof before edits

For every issue, define the observable condition that distinguishes broken from
fixed. Prefer:

1. failing automated test before the change and passing after;
2. deterministic reproduction before and after;
3. stable command/output or data-state assertion;
4. static causal proof only when runtime evidence is impractical.

When no reliable expected behavior can be established, classify the issue
`blocked` instead of guessing.

## Attempt contract

Maximum implementation attempts per selected issue: `3` total.

Each attempt must record:

- attempt number;
- starting HEAD;
- issue start time and absolute UTC deadline;
- remaining budget before dispatch and after return;
- selected model and rationale;
- root-cause hypothesis;
- changed plan from any prior attempt;
- exact verification commands;
- first causal failure;
- changed paths;
- whether repository state remains safe.

Use a fresh worker invocation for each retry so the next attempt reviews the
prior evidence rather than continuing an anchored narrative.

Before every dispatch or expensive command, verify that time remains. Configure
command timeout at or below the remaining issue budget. The worker must return
`time_budget_exceeded` when the deadline is reached.

## Candidate acceptance

A candidate is accepted only when:

- HEAD remains at the issue checkpoint because no commit has been created yet;
- the issue deadline has not expired;
- the acceptance proof passes;
- change-specific tests pass;
- applicable type, lint, build, integration, migration, or repository-native
  checks pass;
- the complete diff is issue-scoped;
- no new regression or unexplained failure appears;
- repository state is attributable and safe.

For high/critical risk, security/data boundaries, or static-only proof, require a
fresh read-only verification pass independent of the implementation worker.

## Implementation retry decision

Retry source implementation only when:

- the attempt number is below `3`;
- the issue deadline has not expired;
- the first causal failure is known;
- the repository remains safe;
- the issue remains actionable;
- the next attempt changes evidence, hypothesis, implementation plan, model, or
  verification strategy materially.

Do not use implementation attempts for temporary GitHub or network errors. Those
are governed separately by `infrastructure-retry-policy.md`.

Do not retry source work for:

- unchanged commands merely hoping for a different result;
- unavailable credentials or external services after infrastructure retry is
  exhausted;
- missing product or architecture decisions;
- destructive migrations requiring authorization;
- security/compliance approval blockers;
- platform model-routing mismatch;
- uncertain worktree ownership;
- unexpected HEAD movement;
- failures that cannot be attributed to the issue candidate;
- an expired issue budget.

## Timeout disposition

At the issue deadline:

1. stop starting new work;
2. terminate only owned command/process groups when supported;
3. reject any uncommitted candidate;
4. clean only current-issue changes using the issue-start checkpoint;
5. require unchanged HEAD and a clean worktree;
6. journal `ISSUE_TIMED_OUT`;
7. count the issue as `timed_out` and consume one slot;
8. continue to the next issue when cleanup and repository safety are proven.

If termination or cleanup cannot be proven safe, stop the whole batch.

## Cleanup after terminal failure or timeout

Because `/fix-issues` requires a clean worktree at issue start and no commit is
created before acceptance, current-issue changes are attributable.

On terminal failure or timeout:

1. compare current HEAD to `ISSUE_START_HEAD`;
2. inventory tracked and newly created untracked paths;
3. restore only tracked paths changed by the current issue to
   `ISSUE_START_HEAD`;
4. remove only newly created untracked paths proven to belong to the current
   issue;
5. verify HEAD unchanged and tree clean;
6. checkpoint the terminal issue outcome before moving on.

Do not use broad `git clean`, discard pre-existing data, or continue when path
provenance is uncertain.

## Commit after acceptance

Check the issue deadline immediately before commit. After acceptance, create one
logical commit for the issue. Use repository commit conventions; otherwise:

```text
fix(<scope>): <concise description> (#<issue-number>)
```

Then run only bounded commit-integrity checks, verify the commit, journal
`ISSUE_COMMITTED`, and require a clean worktree before advancing the queue. Do
not start a new repair round after the deadline.
