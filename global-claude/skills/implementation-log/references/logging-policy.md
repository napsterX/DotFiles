# Decision-Grade Implementation Logging Policy

## Purpose

Implementation logs provide a chronological, repository-local record of material
engineering work. They are intended to be shareable with a reviewer who did not
see the Claude Code session.

The log must answer the decision question created by the task. For an audit or
closure review, it must let a reviewer determine whether the task is ready to
finalize without requesting a separate final report.

Implementation logs are not transcripts, release notes, commit messages,
tickets, or architecture decisions. Those artifacts remain authoritative for
their own purposes.

## One material task, one log

Create one log for one task boundary. A task may span many commands and edits.
Do not create a log after every conversational turn.

A later prompt that materially changes the result creates a new log. Rewriting a
previous task's log to make history look cleaner is prohibited. Re-publication
within the same prompt is permitted only to correct the active record before the
task ends.

## Authority order

When claims conflict, use this order:

1. Current repository and filesystem state
2. Authoritative tracked requirements, architecture, and issue records
3. Exact validation output
4. Current task transcript evidence
5. Model inference

Expose unresolved conflicts. Never silently choose the most convenient account.

## Evidence classes

Every material claim must be supportable as:

- **VERIFIED**
- **SESSION EVIDENCE**
- **INFERRED**
- **UNKNOWN**

Avoid `fully validated`, `complete`, `safe`, `production-ready`, or equivalent
language unless the recorded evidence justifies it.

## Task-specific schemas

The task type controls the required schema. Generic prose is not acceptable when
a task-specific decision contract exists.

### Audit and closure review

An audit record must include:

- explicit verdict;
- agreed scope and exclusions;
- evidence inspected;
- all requested review areas;
- defects found and severity;
- corrections applied;
- exact behavior or semantics established;
- validation commands and totals;
- accepted limitations;
- remaining findings;
- issue state and action;
- final recommendation;
- decision-grade Shareable Summary.

Allowed verdicts:

- `APPROVED`
- `APPROVED WITH ACCEPTED LIMITATIONS`
- `CHANGES REQUIRED`
- `BLOCKED`
- `INCONCLUSIVE`

`APPROVED` and `APPROVED WITH ACCEPTED LIMITATIONS` require passed validation.
If tests were run, test-file, passed, failed, and skipped counts must be numeric.
An approval verdict cannot coexist with failing tests or an unknown failed-test
count.

`APPROVED WITH ACCEPTED LIMITATIONS` requires at least one named limitation and a
reason it does not block finalization.

`CHANGES REQUIRED` and `BLOCKED` require at least one substantive defect or
blocker.

Every review area named by the user, issue, plan, or audit prompt requires one
row in `Review Area Disposition`. Do not collapse requested topics into a vague
`all areas passed` statement.

### Implementation

Record the actual implementation result, changed contracts, decisions,
validation, known limitations, unresolved risk, issue state, and next action.

### Debugging

Record the symptom, reproduction evidence, root-cause confidence, correction,
regression validation, remaining risk, and issue state.

### Validation

Record the acceptance question, exact coverage, commands, pass/fail result,
checks not run, known gaps, confidence boundary, and issue state.

### Documentation, operations, maintenance, and research

Record the objective, durable result, evidence, affected files or operational
state, validation or verification, risks, issue state, and next action.

## Validation recording

For each meaningful validation, record:

- exact command or procedure;
- PASS, FAIL, SKIPPED, or NOT RUN;
- evidence class;
- what it proves;
- what it does not prove.

The Final Validation Summary must state:

- overall result;
- test files, passed, failed, and skipped for audits when tests ran;
- other gates such as lint, typecheck, build, migration, or static checks;
- checks not run;
- confidence supported;
- remaining evidence boundary.

Do not convert `command ran` into `behavior is correct`.

## Repository and issue state

The record must state current branch, HEAD, repository state, task or issue
identifier, and issue state. Audits additionally require the issue action taken
and final issue disposition.

Do not infer that an issue was closed because validation passed. Record issue
state only when verified. Use `unknown` when it was not checked.

## Truncation and publication integrity

A published log must:

- contain every required section in order;
- contain substantive content in every section;
- contain no unresolved template placeholder;
- end with a complete Shareable Summary;
- contain no terminal process narration such as `Publishing:`;
- pass validation before publication;
- pass byte-for-byte readback after atomic publication;
- pass validation again after readback.

A completion marker is valid only after post-write verification succeeds.

## Shareable Summary standard

The summary is not decorative. It is the portable final report.

For audits it must explicitly label:

- Audit verdict
- Defects found and corrected
- Review-area coverage
- Validation
- Accepted limitations
- Remaining findings
- Issue state
- Next action

The summary must not contradict the main body or frontmatter.

## Sensitive information

Never record:

- secret values or credentials;
- private keys or tokens;
- session cookies;
- raw environment dumps;
- unnecessary personal data;
- proprietary raw logs when a minimal excerpt is sufficient.

Record secret names, not values. Use `<redacted>` only where a placeholder is
necessary and clearly intentional.

## Repository location and immutability

Default location:

```text
<repo>/implementation-logs/
```

Optional repository configuration:

```text
<repo>/.claude/implementation-logging.json
```

Example:

```json
{
  "enabled": true,
  "directory": "docs/implementation-logs",
  "strict_change_guard": true,
  "create_readme": true
}
```

The directory must remain inside the repository. Absolute paths, `.git` paths,
and parent traversal are rejected.

Logs use UTC-sortable names:

```text
YYYY-MM-DDTHHMMSSffffffZ--task-slug.md
```

Do not edit logs from previous prompts merely to improve wording. Add a new
corrective log when later work changes the record materially.
