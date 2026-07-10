---
schema_version: 1
log_id: <generated-log-id>
created_at: <UTC timestamp>
task_type: <implementation|audit|debugging|validation|documentation|operations|maintenance|research>
status: <completed|partial|blocked>
task_id: <task ID, label, or none>
session_id: <Claude session ID or unknown>
prompt_id: <Claude prompt ID or manual>
repository: <absolute repository root>
branch: <branch or DETACHED>
head_before: <full SHA or unknown>
head_after: <full SHA or unknown>
---

# Implementation Log: <concise task title>

## Objective

<The precise task objective and observable completion condition.>

## Scope

### Included

- <Work actually included.>

### Excluded

- <Work explicitly outside this task, or none.>

## Work Performed

- **VERIFIED** — <Concrete implementation, audit, investigation, validation, or documentation work.>

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

## Findings

- <Audit, debugging, or validation finding; use “None” only when genuinely applicable.>

## Risks and Unresolved Items

- <Material risk, blocker, uncertainty, or “None identified within the completed scope.”>

## Result

<One concise statement of the actual outcome and status.>

## Next Action

<One concrete next action, or “None required for this task.”>

## Shareable Summary

<Self-contained 150–300 word summary suitable for sharing with another reviewer or ChatGPT. Include objective, result, validation, unresolved items, and next action.>
