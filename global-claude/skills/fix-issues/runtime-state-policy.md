# Runtime State, Resume, Budget, and Lock Policy

## Durable run journal

Create the run journal before queue discovery under:

```text
~/.claude/fix-issues-runs/<repository-key>/<run-id>/
├── run-state.json
├── events.jsonl
└── audit-and-pr-finalization.json   # only during finalization
```

Use `scripts/run_control.py`. `run-state.json` is the current atomic checkpoint.
`events.jsonl` is the fsync'd append-only transition record. Never treat prose in
chat as the durable source of truth.

Record at least these transitions:

```text
RUN_CREATED
LOCK_ACQUIRED
QUEUE_SELECTED
ISSUE_STARTED
ATTEMPT_STARTED
ATTEMPT_FINISHED
CANDIDATE_ACCEPTED or CANDIDATE_REJECTED
ISSUE_COMMITTED / ISSUE_ALREADY_RESOLVED / ISSUE_INVALID /
ISSUE_DUPLICATE / ISSUE_BLOCKED / ISSUE_FAILED / ISSUE_TIMED_OUT
QUEUE_REFRESHED
CUMULATIVE_VERIFICATION_STARTED
CUMULATIVE_VERIFICATION_FINISHED
FINALIZATION_STARTED
FINALIZATION_FINISHED
RUN_COMPLETED or RUN_STOPPED
NOTIFICATION_ATTEMPTED
LOCK_RELEASED
```

Checkpoint immediately after every transition. Include exact repository, task
worktree, branch, expected HEAD, current issue, attempt, selected model, first
causal failure, issue deadline, verification evidence, retained commit, outcome,
and queue counts when applicable.

A crash after issue six must leave enough state to identify the last completed
transition without reconstructing the run from conversation history.

## Resume invocation

Supported forms:

```text
/fix-issues resume
/fix-issues resume <run-id>
```

When no run ID is supplied, select only the newest nonterminal run matching the
exact repository family, task worktree, and branch. Multiple plausible runs are
ambiguous and block resume.

Before continuing, verify:

- repository root and Git common directory;
- task worktree realpath;
- branch;
- expected HEAD and retained commit chain;
- worktree cleanliness or an attributable interrupted issue;
- journal schema and event-chain consistency;
- lock ownership or stale-lock recovery eligibility.

Do not resume when the repository, worktree, branch, or HEAD moved unexpectedly.

If the last transition was `ATTEMPT_STARTED` and HEAD is unchanged, the issue
started from a clean tree, and current uncommitted paths are therefore
attributable to that issue, classify the state as an interrupted issue. Inspect
the candidate. Either prove and accept it through the normal acceptance contract,
or clean only those attributable paths and use the next bounded attempt. Never
blindly continue an unknown partial implementation.

If a crash occurred after `CANDIDATE_ACCEPTED` but before `ISSUE_COMMITTED` was
journaled, reconcile Git history first. Accept a discovered commit only when it
is exactly one child of the recorded HEAD, issue-scoped, and satisfies the saved
acceptance evidence. Otherwise stop for manual reconciliation.

## Repository/worktree/branch lock

This repository/worktree/branch lock prevents overlapping unattended runs.

Acquire an atomic lease lock before queue discovery. The key must include:

- repository family;
- task worktree;
- branch.

Store the lock under:

```text
~/.claude/fix-issues-runs/locks/<lock-key>/owner.json
```

The owner record includes run ID, session ID, acquisition time, heartbeat, and
lease expiry. A second run against the same key must stop.

Renew the lease at every journal transition and immediately before a worker
attempt. The lease must cover the issue deadline plus a 15-minute cleanup grace
period. Do not call a lock stale merely because a long worker is active inside
its declared issue budget.

A stale lock is never silently stolen by a new run. It may be reclaimed only by
an explicit resume of the matching run after repository and journal validation,
or after the stale owner is archived and the operator has established that no
live run remains.

Release the lock after terminal journaling and notification. Lock-release failure
must be reported.

## Per-issue wall-clock budget

Default issue budget: **60 minutes**.

Optional override:

```text
/fix-issues 10 --issue-timeout-minutes 45
```

Allowed range: 5 through 240 minutes.

The clock starts at `ISSUE_STARTED` and covers issue-context reading, acceptance
proof, model routing, all worker attempts, targeted verification, independent
candidate review, cleanup, and the commit decision.

Before every worker dispatch, retry, verification command, candidate acceptance,
and commit, calculate remaining time with `scripts/run_control.py`. Pass the
absolute UTC deadline and remaining seconds to the worker. Never start a command
whose configured timeout exceeds the remaining issue budget.

At or after the deadline:

1. do not start another attempt or validation command;
2. request the worker to stop and terminate owned command/process groups safely
   when the execution surface supports cancellation;
3. do not commit an uncommitted candidate;
4. inventory and remove only current-issue changes under the existing provenance
   rules;
5. verify HEAD unchanged and worktree clean;
6. journal `ISSUE_TIMED_OUT`;
7. consume one selected-issue slot;
8. continue to the next issue when repository state is safe.

If cleanup or process termination cannot be proven safe, stop the entire batch.

Check the deadline immediately before commit. A commit created before the
deadline may complete only short commit-integrity checks afterward; do not begin
new repair work after the deadline.

The Agent tool may not expose a hard preemption mechanism on every Claude Code
version. The deadline is still mandatory, and the worker must self-check it
before each expensive action. Report any platform inability to terminate an
already-running agent call honestly.
