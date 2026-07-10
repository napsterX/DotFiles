---
name: implementation-log
description: Write a verified, decision-grade repository-local implementation log when a material engineering task, audit, review, debugging investigation, validation pass, documentation change, or operational task has completed, partially completed, or reached a blocker. Invoke automatically before the final response for qualifying work; do not use for pure Q&A, planning-only discussion, status checks, or no-op turns.
when_to_use: Use after material repository work or a substantive read-only audit that produces findings worth preserving. For audits and closure reviews, the log must contain the final verdict, defects and corrections, review-area disposition, accepted limitations, exact validation totals, repository and issue state, and final recommendation.
argument-hint: "[optional-task-id-or-label]"
user-invocable: true
model: inherit
effort: high
---

# Implementation Log

Create one concise, evidence-backed, decision-grade implementation log for the
material task that just completed, partially completed, or reached a blocker.
Store it inside the current Git repository. The log is the canonical final task
record that the user can share with another reviewer without also pasting the
Claude transcript.

Read these supporting files before writing the log:

- [references/logging-policy.md](references/logging-policy.md)
- the task-specific template selected below

The optional task ID or label is:

```text
$ARGUMENTS
```

The current Claude session ID is:

```text
${CLAUDE_SESSION_ID}
```

## Qualification gate

Write a log when the current task materially did one or more of the following:

- changed source, configuration, infrastructure, schema, tests, documentation,
  architecture, automation, or operational state;
- completed a code, design, architecture, security, reliability, or closure audit;
- investigated a defect or incident and established useful evidence;
- ran meaningful validation, hardening, migration, cleanup, or recovery work;
- ended partially or blocked after producing material work or findings.

Do not write a log for:

- pure questions or explanations;
- brainstorming or planning with no durable result;
- a status lookup that changed nothing and produced no material finding;
- a canceled task before useful work occurred;
- handoff, resume, or compaction bookkeeping by itself;
- a turn whose only change is an implementation log.

If the task does not qualify, stop silently and do not create a file.

## Procedure

### 1. Resolve repository and prompt state

Run:

```bash
python3 "$HOME/.claude/session-continuity/bin/implementation_log.py" context \
  --cwd "$PWD" \
  --session-id "${CLAUDE_SESSION_ID}"
```

The helper returns the repository root, configured log directory, session and
prompt identifiers, branch and HEAD, prompt-start baseline, current Git state,
change summary, and exact draft path.

Stop if the current directory is not inside a Git repository. Do not create an
implementation log outside a repository.

### 2. Establish the task record

Recover the single material task being completed from the current prompt,
conversation, repository, active issue or ticket, and authoritative project
material.

Use one task type:

- `implementation`
- `audit`
- `debugging`
- `validation`
- `documentation`
- `operations`
- `maintenance`
- `research`

Use one status:

- `completed`
- `partial`
- `blocked`

Use one validation status:

- `passed`
- `failed`
- `partial`
- `not_run`

Use one issue state:

- `open`
- `closed`
- `unchanged`
- `not_applicable`
- `unknown`

For audits, use exactly one verdict:

- `approved`
- `approved_with_accepted_limitations`
- `changes_required`
- `blocked`
- `inconclusive`

For non-audits, use:

```text
audit_verdict: not_applicable
```

Do not claim `completed` when required work remains incomplete. Do not claim
`passed` when required validation failed, was skipped, or remains unknown. Audit
completion means the agreed scope was reviewed; it does not mean the system has
no defects.

### 3. Select the exact template

Use one of these templates without inventing a new schema:

- `audit` → [templates/AUDIT-LOG.md](templates/AUDIT-LOG.md)
- `implementation` → [templates/IMPLEMENTATION-LOG.md](templates/IMPLEMENTATION-LOG.md)
- `debugging` → [templates/DEBUGGING-LOG.md](templates/DEBUGGING-LOG.md)
- `validation` → [templates/VALIDATION-LOG.md](templates/VALIDATION-LOG.md)
- `documentation`, `operations`, `maintenance`, or `research` →
  [templates/GENERAL-LOG.md](templates/GENERAL-LOG.md)

Do not delete required sections. Do not substitute a generic implementation log
for an audit or closure review.

### 4. Inspect authoritative evidence

Inspect only what is necessary to support the final record:

- applicable project instructions and active task or issue material;
- current Git status and relevant diffs;
- files changed or inspected during the task;
- validation output from this task;
- audit, review, or debugging evidence produced during this task;
- actual issue or ticket state when a task identifier exists.

Do not begin new implementation solely to improve the log. Do not run broad or
expensive validation solely for logging. If evidence was not freshly rerun,
label it accurately.

Classify material claims as:

- **VERIFIED** — confirmed from current repository, filesystem, issue state, or
  command output;
- **SESSION EVIDENCE** — observed earlier in the current task but not rerun while
  writing the log;
- **INFERRED** — reasoned conclusion requiring later verification;
- **UNKNOWN** — unresolved.

Repository state and authoritative tracked contracts override conversational
claims.

### 5. Apply the audit completion contract

For `task_type: audit`, the log is invalid unless it contains all of the
following:

1. Explicit audit verdict.
2. Exact agreed scope and evidence inspected.
3. Every requested review area with a disposition row.
4. Every material defect found, its severity, evidence, closure impact, and
   status.
5. Every correction applied and its validation.
6. Explicit fail-open/fail-closed, retry, deduplication, migration, offline,
   security, or other behavioral semantics when those were part of the scope.
7. Exact validation commands and outcomes.
8. Final test counts when tests were run: files, passed, failed, and skipped.
9. Checks not run and what the validation does not prove.
10. Accepted limitations and why they do not block the verdict.
11. Remaining findings.
12. Repository state, task or issue state, and action taken.
13. Final recommendation and whether the task is ready to finalize.
14. A Shareable Summary containing the same verdict, limitations, issue state,
    validation result, and next action.

An audit log must be sufficient for an independent reviewer to decide whether
the issue is ready to finalize. A separate Claude final response must not be
required to recover the verdict or correction summary.

### 6. Write the draft

Write the draft to the exact path returned by the `context` command.

Content rules:

- target: 100 to 300 lines;
- hard limit: 48 KiB and 420 lines;
- no full large diffs;
- no full raw logs;
- no transcript dumps;
- no environment dumps;
- no secret values;
- no speculative narrative presented as fact;
- no empty required section;
- no process narration such as `Publishing:` or `Validating:`;
- no unresolved placeholders.

The Shareable Summary must be self-contained. For an audit, preserve the exact
labels required by the audit template.

### 7. Validate and publish

Validate the draft:

```bash
python3 "$HOME/.claude/session-continuity/bin/implementation_log.py" validate \
  --file "<draft-path>"
```

Resolve every validation error. Do not downgrade a factual gap into polished
wording. If required evidence is unavailable, record it as unknown and choose a
compatible status or verdict.

Publish only after validation succeeds:

```bash
python3 "$HOME/.claude/session-continuity/bin/implementation_log.py" publish \
  --source "<draft-path>" \
  --cwd "$PWD" \
  --session-id "${CLAUDE_SESSION_ID}" \
  --label "$ARGUMENTS"
```

The helper validates again, publishes atomically, reads the final file back
byte-for-byte, validates the readback, de-duplicates publication within the same
prompt, and writes the Stop-guard completion marker only after successful
readback verification.

### 8. Re-read the published log

Re-read the exact published path and verify:

- the file ends with a complete Shareable Summary;
- the verdict is present and consistent everywhere;
- defects and corrections are complete;
- all requested review areas are represented;
- validation totals are exact when tests ran;
- accepted limitations and remaining findings are explicit;
- repository and issue state are accurate;
- the recommendation follows from the evidence;
- no line ends with unfinished process narration;
- no secret or sensitive value was recorded.

Correct and republish within the same prompt when necessary.

## Stop conditions

Stop and report instead of publishing when:

- no Git repository can be resolved;
- the task does not meet the qualification gate;
- the task objective cannot be identified without guessing;
- repository or issue state materially contradicts the claimed result;
- an audit verdict cannot be justified from available evidence;
- a required review area was not actually reviewed;
- final test counts cannot be recovered even though tests were reported as run;
- the draft contains a suspected credential or private key;
- a required section cannot be completed honestly;
- validation, atomic publish, readback, or post-write validation fails.

## Required final output

After successful publication, derive the task's final response from the published
log. Include:

```text
IMPLEMENTATION LOG

Path: <repository-relative path>
Type: <task type>
Status: <completed|partial|blocked>
Verdict: <audit verdict or not applicable>
Result: <one sentence>
Validation: <one sentence including exact test count when applicable>
Issue state: <open|closed|unchanged|not applicable|unknown>
Accepted limitations: <none or one sentence>
Unresolved: <none or one sentence>
```

Do not leave the final verdict only in chat. Do not create a second summary file.
Do not modify logs from earlier prompts.
