---
schema_version: 2
log_id: <generated-log-id>
created_at: <UTC timestamp>
task_type: <documentation|operations|maintenance|research>
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

# Implementation Log: <concise task title>

## Objective

<Precise objective and observable completion condition.>

## Scope

### Included

- <Included work.>

### Excluded

- <Excluded work or none.>

## Repository and Task State

- **Repository state:** <clean/dirty and concise explanation>
- **Branch:** <branch>
- **HEAD:** <SHA>
- **Task/issue:** <identifier or none>
- **Issue state:** <open/closed/unchanged/not applicable/unknown>

## Work Performed

- **VERIFIED** — <Concrete work completed.>

## Files Changed or Inspected

| Path | State | Purpose |
|---|---|---|
| `<path>` | <state> | <purpose> |

## Decisions and Invariants

- **VERIFIED / SESSION EVIDENCE / INFERRED / UNKNOWN** — <Decision or invariant.>

## Validation Evidence

| Command or Procedure | Result | Evidence | Proves | Does Not Prove |
|---|---|---|---|---|
| `<exact command or procedure>` | <PASS/FAIL/SKIPPED/NOT RUN> | <evidence class> | <conclusion> | <limitation> |

## Final Validation Summary

- **Overall validation:** <PASS|FAIL|PARTIAL|NOT RUN>
- **Other gates:** <checks or not applicable>
- **Checks not run:** <list or none>
- **Confidence supported:** <what is justified>
- **Does not prove:** <remaining uncertainty>

## Findings

<Material result or finding.>

## Result

<Actual outcome and status.>

## Risks and Unresolved Items

<Material risk, blocker, or none.>

## Next Action

<One concrete next action or none required.>

## Shareable Summary

<Self-contained 150–350 word summary including objective, result, evidence, unresolved items, issue state, and next action.>
