# Verification and Retry Policy

## Objective

Prove that an issue is fixed before retaining a commit. Use a bounded
implement -> verify -> review -> repair -> reverify loop. Never equate code
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

Maximum attempts per selected issue: `3` total.

Each attempt must record:

- attempt number;
- starting HEAD;
- selected model and rationale;
- root-cause hypothesis;
- changed plan from any prior attempt;
- exact verification commands;
- first causal failure;
- changed paths;
- whether repository state remains safe.

A fresh worker invocation should be used for each retry so the next attempt
reviews the evidence rather than merely continuing an anchored narrative.

## Candidate acceptance

A candidate is accepted only when:

- HEAD remains at the issue checkpoint because no commit has been created yet;
- the acceptance proof passes;
- change-specific tests pass;
- applicable type, lint, build, integration, migration, or repository-native
  checks pass;
- the complete diff is issue-scoped;
- no new regression or unexplained failure appears;
- repository state is attributable and safe.

For high/critical risk, security/data boundaries, or static-only proof, require a
fresh read-only verification pass independent of the implementation worker.

## Retry decision

Retry only when:

- the attempt number is below `3`;
- the first causal failure is known;
- the repository remains safe;
- the issue remains actionable;
- the next attempt changes evidence, hypothesis, implementation plan, model, or
  verification strategy materially.

Do not retry:

- unchanged commands merely hoping for a different result;
- unavailable credentials or external services;
- missing product or architecture decisions;
- destructive migrations requiring authorization;
- security/compliance approval blockers;
- platform model-routing mismatch;
- uncertain worktree ownership;
- unexpected HEAD movement;
- failures that cannot be attributed to the issue candidate.

## Cleanup after terminal failure

Because `/fix-issues` requires a clean worktree at issue start and no commit is
created before acceptance, current-issue changes are attributable.

On terminal failure:

1. compare current HEAD to `ISSUE_START_HEAD`;
2. inventory tracked and newly created untracked paths;
3. restore only tracked paths changed by the current issue to
   `ISSUE_START_HEAD`;
4. remove only newly created untracked paths proven to belong to the current
   issue;
5. verify HEAD unchanged and tree clean.

Do not use broad `git clean`, discard pre-existing data, or continue when path
provenance is uncertain.

## Commit after acceptance

After acceptance, create one logical commit for the issue. Use repository commit
conventions; otherwise:

```text
fix(<scope>): <concise description> (#<issue-number>)
```

Then verify the commit, run any required post-commit check, and require a clean
worktree before advancing the queue.
