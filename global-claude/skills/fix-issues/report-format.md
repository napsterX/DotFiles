# Final Report Format

## Invocation

- Command:
- Run ID:
- Run mode: NEW / RESUMED
- Journal path:
- Requested maximum:
- Effective maximum:
- Maximum attempts per issue: 3
- Issue timeout: 60 minutes by default
- Dynamic model routing: ENABLED
- Repository:
- Task worktree:
- Branch:
- Starting HEAD:
- Ending HEAD:
- Lock key:
- Lock disposition:
- Resume validation:

## Queue Summary

- Eligible issues found:
- Bounded issues selected:
- P3 selected:
- P2 selected:
- Selection order:

## Outcomes

For every selected issue:

- Issue:
- Title:
- Priority:
- Status:
- Elapsed time:
- Deadline:
- Attempts used:
- Attempt models:
- Final model rationale:
- Runtime model evidence:
- Root cause:
- Acceptance proof:
- Fix summary:
- Verification:
- Infrastructure retries:
- Commit SHA:
- Issue comment status:
- Blocker, timeout, or failure reason:

## Counts

- Requested maximum:
- Selected:
- Fixed:
- Already resolved:
- Invalid:
- Duplicate:
- Blocked:
- Failed:
- Timed out:
- Total worker attempts:
- Total infrastructure retries:

## Commits

List chronologically:

```text
<sha> <issue> <subject>
```

## Verification

- Issue-level commands:
- Retry-specific evidence:
- Cumulative commands:
- Passed checks:
- Failed checks:
- Skipped checks:
- Pre-existing failures:
- Introduced failures:

## Audit and PR Finalization

- Manifest:
- Delegation attempted: YES / NO
- `/audit-and-pr` result:
- Audit verdict:
- PR:
- CI:
- Merge disposition:
- Cleanup:
- Finalization blocker:

## Recovery and Notification

- Last durable transition:
- Resume required: YES / NO
- FirstMate notification event:
- FirstMate delivery: DELIVERED / NOT_AVAILABLE / FAILED_NONBLOCKING
- Lock released: YES / NO

## Remaining Queue

- Remaining eligible P3:
- Remaining eligible P2:
- Next eligible issues:
- End reason: LIMIT / QUEUE_EXHAUSTED / STOP_CONDITION / RESUME_REQUIRED

## Manual Actions

List only actions that actually require human intervention.
