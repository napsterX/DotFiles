---
schema_version: 2
log_id: <generated-log-id>
created_at: <UTC timestamp>
task_type: debugging
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

# Implementation Log: <concise debugging title>

## Objective

<State the symptom to explain or correct and the success condition.>

## Scope

### Included

- <Systems and paths investigated.>

### Excluded

- <Explicit exclusions, or none.>

## Repository and Task State

- **Repository state:** <clean/dirty and concise explanation>
- **Branch:** <branch>
- **HEAD:** <SHA>
- **Task/issue:** <identifier or none>
- **Issue state:** <open/closed/unchanged/not applicable/unknown>

## Work Performed

- **VERIFIED** — <Investigation and correction work.>

## Files Changed or Inspected

| Path | State | Purpose |
|---|---|---|
| `<path>` | <modified/inspected/etc.> | <Why it mattered> |

## Decisions and Invariants

- **VERIFIED / SESSION EVIDENCE / INFERRED / UNKNOWN** — <Relevant contract or constraint.>

## Validation Evidence

| Command or Procedure | Result | Evidence | Proves | Does Not Prove |
|---|---|---|---|---|
| `<exact command>` | <PASS/FAIL/SKIPPED/NOT RUN> | <evidence class> | <conclusion> | <limitation> |

## Final Validation Summary

- **Overall validation:** <PASS|FAIL|PARTIAL|NOT RUN>
- **Other gates:** <tests and other checks>
- **Checks not run:** <list or none>
- **Confidence supported:** <what is justified>
- **Does not prove:** <remaining uncertainty>

## Symptom

<Observed behavior and reproduction evidence.>

## Root Cause

<Verified root cause, or clearly marked hypothesis if not proven.>

## Correction

<Correction applied, or why no correction was made.>

## Regression Validation

<Exact regression evidence and outcome.>

## Remaining Risk

<Residual risk or none.>

## Result

<Actual debugging outcome.>

## Next Action

<One concrete action or none required.>

## Shareable Summary

<Self-contained 150–350 word summary including symptom, root cause confidence, correction, regression evidence, remaining risk, issue state, and next action.>
