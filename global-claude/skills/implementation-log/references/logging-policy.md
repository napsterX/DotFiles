# Implementation Logging Policy

## Purpose

Implementation logs provide a chronological, repository-local record of material
engineering work. They are designed for:

- handoff to another engineer or model;
- review of what changed and why;
- validation traceability;
- reconstruction of audit findings and debugging conclusions;
- a durable history beyond ephemeral chat transcripts.

They are not release notes, commit messages, tickets, architecture decisions, or
complete session transcripts. Those artifacts remain separate and authoritative
for their own purposes.

## One material task, one log

Create one log for one completed task boundary. A task boundary may span many tool
calls or several implementation phases inside one prompt. Do not create a log
after every edit or command.

A follow-up prompt that materially changes the result creates a new log. Do not
rewrite an older log to make history look cleaner. Re-publication within the same
prompt is allowed only to correct the current draft before the task ends.

## Authority order

Use this authority order when claims conflict:

1. Current repository and filesystem state
2. Authoritative tracked requirements, architecture, and task records
3. Exact validation output
4. Current task transcript evidence
5. Model inference

The log must expose unresolved conflict rather than silently selecting the most
convenient account.

## Task qualification

Log material work, including:

- implementation and refactoring;
- schema, infrastructure, security, configuration, and automation changes;
- tests and validation that establish a new confidence result;
- code, architecture, security, reliability, or operational audits;
- debugging and incident investigation with durable findings;
- documentation work that changes project contracts or execution guidance;
- blocked or partial work that another session must understand.

Do not log:

- ordinary questions and answers;
- tentative brainstorming;
- duplicate explanations;
- no-op checks with no material finding;
- work unrelated to the repository;
- session-continuity bookkeeping alone.

## Evidence language

Every non-trivial claim should be supportable as one of:

- **VERIFIED**
- **SESSION EVIDENCE**
- **INFERRED**
- **UNKNOWN**

Avoid words such as “fully validated,” “complete,” “safe,” or “production-ready”
unless the evidence and validation scope justify them.

## Validation recording

For each meaningful validation, record:

- exact command or procedure;
- result;
- evidence class;
- what it proves;
- what it does not prove.

Do not convert “command was run” into “behavior is correct.” Failed, skipped, and
unavailable checks remain visible.

## Audit recording

For audits, distinguish:

- scope reviewed;
- evidence inspected;
- findings;
- severity or priority when justified;
- false positives or rejected concerns;
- remediation status;
- residual unknowns.

Audit completion means the agreed scope was reviewed. It does not mean the system
has no defects.

## Repository location

The default location is:

```text
<repo>/implementation-logs/
```

A repository may override this with:

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

The directory must remain inside the repository. Absolute paths and parent
traversal are rejected.

## Naming and immutability

Logs use UTC-sortable names:

```text
YYYY-MM-DDTHHMMSSffffffZ--task-slug.md
```

Do not rename or edit logs from previous prompts merely to improve wording. Add a
new corrective log when later work changes the record materially.

## Sensitive information

Never record:

- secret values or credentials;
- private keys or tokens;
- session cookies;
- raw environment dumps;
- unnecessary personal data;
- proprietary raw logs when a minimal excerpt is sufficient.

Record secret names, not values. Use explicit placeholders such as `<redacted>`.

## Shareable Summary standard

The summary must let a reviewer answer:

1. What task was attempted?
2. What was actually changed or learned?
3. What validation ran and what confidence does it support?
4. What remains unresolved?
5. What should happen next?

It should normally fit within 150 to 300 words.
