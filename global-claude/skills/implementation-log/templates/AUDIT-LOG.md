---
schema_version: 2
log_id: <generated-log-id>
created_at: <UTC timestamp>
task_type: audit
status: <completed|partial|blocked>
task_id: <task ID, issue number, label, or none>
session_id: <Claude session ID or unknown>
prompt_id: <Claude prompt ID or manual>
repository: <absolute repository root>
branch: <branch or DETACHED>
head_before: <full SHA or unknown>
head_after: <full SHA or unknown>
validation_status: <passed|failed|partial|not_run>
issue_state: <open|closed|unchanged|not_applicable|unknown>
audit_verdict: <approved|approved_with_accepted_limitations|changes_required|blocked|inconclusive>
---

# Implementation Log: <concise audit title>

## Objective

<State the exact audit objective, closure question, and observable decision condition.>

## Scope

### Included

- <Agreed audit scope and review areas.>

### Excluded

- <Explicit exclusions, or “None.”>

## Repository and Task State

- **Repository state:** <clean/dirty and concise explanation>
- **Branch:** <branch>
- **HEAD:** <full or abbreviated SHA>
- **Task/issue:** <identifier and title, or none>
- **Issue state:** <open/closed/unchanged/not applicable/unknown>
- **Issue action:** <closed, reopened, commented, unchanged, or not applicable>

## Work Performed

- **VERIFIED** — <Concrete audit, correction, verification, and documentation work completed.>

## Files Changed or Inspected

| Path | State | Purpose |
|---|---|---|
| `<path>` | <added/modified/deleted/inspected/unchanged> | <Why it mattered to the audit> |

## Decisions and Invariants

- **VERIFIED / SESSION EVIDENCE / INFERRED / UNKNOWN** — <Decision, invariant, or contract the audit preserved or established.>

## Audit Verdict

- **Verdict:** <APPROVED|APPROVED WITH ACCEPTED LIMITATIONS|CHANGES REQUIRED|BLOCKED|INCONCLUSIVE>
- **Decision basis:** <One concise evidence-backed explanation.>

## Audit Scope and Coverage

- **Agreed scope:** <The exact closure or review scope.>
- **Evidence inspected:** <Files, diffs, commands, issue material, and runtime evidence.>
- **Coverage completed:** <What was fully reviewed.>
- **Coverage not completed:** <Anything omitted, unavailable, or not independently verified.>

## Defects Found

| ID | Severity | Defect | Evidence | Closure impact | Status |
|---|---|---|---|---|---|
| D-01 | <critical/high/medium/low> | <Specific defect> | <Evidence> | <Blocks/does not block closure> | <corrected/open/accepted> |

Use this exact statement only when genuinely applicable:

- None found within audited scope.

## Corrections Applied

| Defect ID | Correction | Files | Validation | Result |
|---|---|---|---|---|
| D-01 | <Correction made> | `<paths>` | <Exact validation> | <PASS/FAIL/PARTIAL> |

For a read-only audit with no corrections, use:

- None; audit was read-only.

## Review Area Disposition

| Review area | Expected behavior or criterion | Evidence | Result | Residual limitation |
|---|---|---|---|---|
| <Named review area> | <What had to be true> | <Files/tests/output> | <VERIFIED/CORRECTED/FAILED/NOT VERIFIED> | <None or explicit limitation> |

Every review area explicitly requested in the prompt or issue must have one row.

## Validation Evidence

| Command or Procedure | Result | Evidence | Proves | Does Not Prove |
|---|---|---|---|---|
| `<exact command or procedure>` | <PASS/FAIL/SKIPPED/NOT RUN> | <VERIFIED or SESSION EVIDENCE> | <Supported conclusion> | <Remaining limitation> |

## Final Validation Summary

- **Overall validation:** <PASS|FAIL|PARTIAL|NOT RUN>
- **Test files:** <integer|unknown|not applicable>
- **Tests passed:** <integer|unknown|not applicable>
- **Tests failed:** <integer|unknown|not applicable>
- **Tests skipped:** <integer|unknown|not applicable>
- **Other gates:** <typecheck, lint, build, migration checks, static analysis, or not applicable>
- **Checks not run:** <Explicit list or “None.”>
- **Confidence supported:** <What the completed validation justifies.>
- **Does not prove:** <What remains outside the evidence.>

## Accepted Limitations

- <Each accepted limitation, owner, rationale, and why it does not block the verdict.>

Use this exact statement only when applicable:

- None accepted.

## Remaining Findings

- <Open defect, unresolved uncertainty, follow-up, or “None remaining within audited scope.”>

## Final Recommendation

- **Recommendation:** <Finalize/Do not finalize/Finalize conditionally/Continue remediation>
- **Ready to finalize:** <yes/no/conditional>
- **Issue disposition:** <Issue remained open/Issue was closed/Issue state unchanged/Unknown/not applicable>
- **Rationale:** <Concise evidence-based rationale.>

## Next Action

<One concrete next action, or “None required for this audited scope.”>

## Shareable Summary

- **Audit verdict:** <verdict>
- **Defects found and corrected:** <concise count and disposition>
- **Review-area coverage:** <all requested areas and their outcomes>
- **Validation:** <commands/gates and exact final test count>
- **Accepted limitations:** <none or concise list>
- **Remaining findings:** <none or concise list>
- **Issue state:** <open/closed/unchanged/unknown/not applicable>
- **Next action:** <one concrete action>

<Add a concise narrative that lets a reviewer decide whether the task is ready to finalize without needing the Claude transcript.>
