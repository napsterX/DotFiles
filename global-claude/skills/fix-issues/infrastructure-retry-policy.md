# Transient Infrastructure Retry Policy

## Scope

Infrastructure retries are separate from implementation attempts. A temporary
GitHub or network failure does not consume one of the three code-repair attempts,
but it remains bounded by the per-issue wall-clock budget.

Use `scripts/infrastructure_retry.py` for deterministic classification.

## Retryable conditions

The following may be retried when evidence shows they are transient:

- GitHub/API HTTP 408, 425, 429, 500, 502, 503, or 504;
- connection reset/refused/closed;
- temporary DNS or network failure;
- TLS handshake timeout;
- temporary Git fetch transport failure;
- temporary CI-status polling unavailability;
- an explicit server rate-limit response with a bounded retry window.

Maximum operation attempts: `3`.

Backoff before subsequent attempts:

```text
after attempt 1: 15 seconds
after attempt 2: 60 seconds
```

Do not retry when the remaining issue budget cannot accommodate the backoff and
operation.

## Never retry as infrastructure

Do not use this policy for:

- failing tests or builds;
- deterministic verification failures;
- authentication or authorization failure;
- permission denial or repository not found;
- malformed or rejected requests;
- missing required credentials or secrets;
- branch-protection rejection;
- model-routing failure;
- product or architecture decisions;
- security, migration, data-integrity, or destructive-operation blockers.

Do not repeatedly rerun a flaky test until it passes. Test retry policy remains
owned by repository instructions and verification evidence, not this layer.

## Read versus mutation operations

Read-only operations such as issue fetch, queue refresh, Git fetch, and CI status
polling can be retried directly after bounded backoff.

Mutation operations require read-after-write reconciliation before retry:

- GitHub issue comments;
- GitHub issue creation for a newly discovered gap;
- an explicitly authorized push.

Use a stable hidden idempotency marker derived from run ID, issue number, and
operation. Before retrying, read the remote state. If the mutation already
succeeded, record success and do not issue it again. If its state is ambiguous,
stop rather than risk a duplicate.

## Exhaustion and batch impact

When retries are exhausted:

- an issue-local external dependency marks that issue `blocked` and consumes a
  slot when the next issue can still be processed safely;
- loss of GitHub issue discovery, queue refresh, repository access, or other
  batch-wide infrastructure journals `RUN_STOPPED` and stops the run;
- budget exhaustion during backoff journals `ISSUE_TIMED_OUT` and follows the
  timeout cleanup path.

Record every infrastructure attempt, classification, delay, reconciliation, and
final disposition in the run journal.
