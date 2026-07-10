---
schema_version: 2
log_id: <generated-log-id>
created_at: <UTC timestamp>
task_type: implementation
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

<The precise task objective and observable completion condition.>

## Scope

### Included

- <Work actually included.>

### Excluded

- <Work explicitly outside this task, or none.>

## Repository and Task State

- **Repository state:** <clean/dirty and concise explanation>
- **Branch:** <branch>
- **HEAD:** <full or abbreviated SHA>
- **Task/issue:** <identifier and title, or none>
- **Issue state:** <open/closed/unchanged/not applicable/unknown>

## Work Performed

- **VERIFIED** — <Concrete implementation work.>

## Files Changed or Inspected

| Path | State | Purpose |
|---|---|---|
| `<path>` | <added/modified/deleted/inspected/unchanged> | <Why it mattered> |

## Decisions and Invariants

- **VERIFIED / SESSION EVIDENCE / INFERRED / UNKNOWN** — <Decision, contract, or invariant.>

## Validation Evidence

| Command or Procedure | Result | Evidence | Proves | Does Not Prove |
|---|---|---|---|---|
| `<exact command or procedure>` | <PASS/FAIL/SKIPPED/NOT RUN> | <VERIFIED or SESSION EVIDENCE> | <Supported conclusion> | <Remaining limitation> |

## Final Validation Summary

- **Overall validation:** <PASS|FAIL|PARTIAL|NOT RUN>
- **Other gates:** <test/typecheck/lint/build/migration/static checks or not applicable>
- **Checks not run:** <Explicit list or “None.”>
- **Confidence supported:** <What the validation justifies.>
- **Does not prove:** <What remains outside the evidence.>

## Implementation Result

<One concise statement of the actual implementation outcome and completion status.>

## Known Limitations

- <Known limitation or “None identified within the completed scope.”>

## Risks and Unresolved Items

- <Material risk, blocker, uncertainty, or “None identified within the completed scope.”>

## Next Action

<One concrete next action, or “None required for this task.”>

## Shareable Summary

<Self-contained 150–350 word summary suitable for sharing with another reviewer or ChatGPT. Include objective, implementation result, files or contracts affected, validation status, unresolved items, issue state, and next action.>
