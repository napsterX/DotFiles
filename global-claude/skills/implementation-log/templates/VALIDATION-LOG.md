---
schema_version: 2
log_id: <generated-log-id>
created_at: <UTC timestamp>
task_type: validation
status: <completed|partial|blocked>
task_id: <task ID, label, or none>
session_id: <Claude session ID or unknown>
prompt_id: <Claude prompt ID or manual>
repository: <absolute repository root>
branch: <branch or DETACHED>
head_before: <full SHA or unknown>
head_after: <full SHA or unknown>
validation_status: <passed|failed|partial|not_run>
issue_state: <open|closed|unchanged|not_applicable|unknown>
audit_verdict: not_applicable
---

# Implementation Log: <concise validation title>

## Objective

<State the validation question and pass condition.>

## Scope

### Included

- <Checks included.>

### Excluded

- <Checks excluded or unavailable.>

## Repository and Task State

- **Repository state:** <clean/dirty and concise explanation>
- **Branch:** <branch>
- **HEAD:** <SHA>
- **Task/issue:** <identifier or none>
- **Issue state:** <open/closed/unchanged/not applicable/unknown>

## Work Performed

- **VERIFIED** — <Validation work completed.>

## Files Changed or Inspected

| Path | State | Purpose |
|---|---|---|
| `<path>` | <modified/inspected/unchanged> | <Why it mattered> |

## Decisions and Invariants

- **VERIFIED / SESSION EVIDENCE / INFERRED / UNKNOWN** — <Relevant acceptance contract.>

## Validation Evidence

| Command or Procedure | Result | Evidence | Proves | Does Not Prove |
|---|---|---|---|---|
| `<exact command>` | <PASS/FAIL/SKIPPED/NOT RUN> | <evidence class> | <conclusion> | <limitation> |

## Final Validation Summary

- **Overall validation:** <PASS|FAIL|PARTIAL|NOT RUN>
- **Other gates:** <test/typecheck/lint/build/etc.>
- **Checks not run:** <list or none>
- **Confidence supported:** <what is justified>
- **Does not prove:** <remaining uncertainty>

## Validation Objective

<Precise acceptance question.>

## Coverage

<What was exercised, including environments and paths.>

## Findings

<Material findings, including failures and skipped coverage.>

## Validation Verdict

<PASS, FAIL, PARTIAL, or NOT RUN with rationale.>

## Known Gaps

<Unvalidated areas or none.>

## Result

<Actual result and status.>

## Next Action

<One concrete next action or none required.>

## Shareable Summary

<Self-contained 150–350 word summary including validation objective, exact checks, pass/fail result, coverage gaps, issue state, and next action.>
