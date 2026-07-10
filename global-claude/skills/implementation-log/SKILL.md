---
name: implementation-log
description: Write a verified repository-local implementation log when a material engineering task, audit, review, debugging investigation, validation pass, documentation change, or operational task has completed, partially completed, or reached a blocker. Invoke automatically before the final response for qualifying work; do not use for pure Q&A, planning-only discussion, status checks, or no-op turns.
when_to_use: Use after material repository work or a substantive read-only audit that produces findings worth preserving. The log is the concise evidence-backed record the user can share with another reviewer or ChatGPT.
argument-hint: "[optional-task-id-or-label]"
user-invocable: true
model: inherit
effort: medium
---

# Implementation Log

Create one concise, evidence-backed implementation log for the material task that
just completed, partially completed, or reached a blocker. Store it inside the
current Git repository. The log is a durable engineering record and a shareable
summary, not a transcript dump and not a substitute for the repository.

Read these supporting files before writing the log:

- [references/logging-policy.md](references/logging-policy.md)
- [templates/IMPLEMENTATION-LOG.md](templates/IMPLEMENTATION-LOG.md)

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
- completed a code or design audit with substantive findings;
- investigated a defect or incident and established useful evidence;
- ran a meaningful validation, hardening, migration, cleanup, or recovery task;
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

The helper returns:

- repository root;
- configured implementation-log directory;
- session and prompt identifiers;
- branch and current HEAD;
- baseline state captured when the user prompt began, when available;
- current Git state excluding the implementation-log directory;
- deterministic change summary;
- the draft path to use.

Stop if the current directory is not inside a Git repository. Do not create an
implementation log outside a repository.

### 2. Establish the task record

Recover the single task being completed from the current prompt, conversation,
and authoritative repository material. Identify:

- objective and observable result;
- task type;
- completion status;
- scope actually performed;
- changed or inspected files;
- decisions and invariants;
- exact validation commands and results;
- audit findings, if any;
- risks, blockers, and unresolved items;
- the smallest useful next action, if one remains.

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

Do not claim `completed` when required validation failed, was skipped, or remains
unknown. A completed audit may have unresolved findings; completion means the
audit scope finished, not that every finding was remediated.

### 3. Inspect authoritative evidence

Inspect only what is needed to support the log:

- applicable project instructions and active task or issue material;
- current Git status and relevant diffs;
- files changed or inspected during the task;
- validation output from this task;
- audit or debugging evidence produced during this task.

Do not begin new implementation work solely to improve the log. Do not run broad
or expensive validation solely for logging. If evidence was not freshly rerun,
label it accurately.

Classify material claims as:

- **VERIFIED** — confirmed from current repository, filesystem, or command
  output;
- **SESSION EVIDENCE** — observed earlier in the current task but not rerun while
  writing the log;
- **INFERRED** — reasoned conclusion requiring later verification;
- **UNKNOWN** — unresolved.

Repository state and authoritative tracked contracts override conversational
claims.

### 4. Write the draft

Use the exact template. Keep the result concise and useful to an engineer who did
not see the session:

- target: 80 to 220 lines;
- hard limit: 32 KiB and 300 lines;
- no full large diffs;
- no full raw logs;
- no transcript dumps;
- no environment dumps;
- no secret values;
- no speculative narrative presented as fact.

The `Shareable Summary` must be self-contained and suitable for pasting into a
new ChatGPT conversation. It must state what was done, validation status,
material unresolved items, and the next action without requiring the rest of the
log.

Write the draft to the exact draft path returned by the `context` command.

### 5. Validate and publish

Validate the draft:

```bash
python3 "$HOME/.claude/session-continuity/bin/implementation_log.py" validate \
  --file "<draft-path>"
```

Resolve every validation error. Read any credential warning before deciding it
is a safe placeholder.

Publish only after validation succeeds:

```bash
python3 "$HOME/.claude/session-continuity/bin/implementation_log.py" publish \
  --source "<draft-path>" \
  --cwd "$PWD" \
  --session-id "${CLAUDE_SESSION_ID}" \
  --label "$ARGUMENTS"
```

The helper:

- resolves the active prompt identity;
- validates the log again;
- creates the repository-local implementation-log directory if necessary;
- creates the directory README on first use;
- writes the log atomically;
- de-duplicates repeated publication within the same prompt;
- records a completion marker outside the repository for the Stop guard.

### 6. Re-read the published log

Check the final file for:

- objective/result mismatch;
- unsupported completion claims;
- incorrect branch, HEAD, or file-state claims;
- missing material failures or audit findings;
- vague validation statements without commands or evidence class;
- secrets or sensitive data;
- a Shareable Summary that omits the actual result.

Correct and republish within the same prompt if necessary.

## Stop conditions

Stop and report instead of publishing when:

- no Git repository can be resolved;
- the task does not meet the qualification gate;
- the task objective cannot be identified without guessing;
- repository state materially contradicts the claimed result and cannot be
  reconciled;
- the draft contains a suspected credential or private key;
- required sections cannot be completed honestly;
- the helper or atomic publish fails.

## Required final output

After a successful publish, include this compact block in the task's normal final
response:

```text
IMPLEMENTATION LOG

Path: <repository-relative path>
Type: <task type>
Status: <completed|partial|blocked>
Result: <one sentence>
Validation: <one sentence>
Unresolved: <none or one sentence>
```

Do not create a second summary file. Do not modify previous implementation logs
from earlier prompts.
