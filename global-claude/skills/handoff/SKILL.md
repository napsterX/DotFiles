---
name: handoff
description: Create a verified operational handoff for the current Claude Code task before clearing, changing sessions, or transferring work. Use only when the user explicitly invokes /handoff.
argument-hint: "[optional-label-or-focus]"
disable-model-invocation: true
user-invocable: true
model: opus
effort: high
---

# Handoff

Create a durable, verified operational handoff for the active task. The handoff
is recovery state, not an informal summary and not a substitute for the
repository.

Do not use a forked subagent for the core handoff. The current conversation is
required to recover objectives, constraints, decisions, rejected approaches,
and validation evidence.

Read these supporting files before writing the handoff:

- [references/handoff-policy.md](references/handoff-policy.md)
- [templates/HANDOFF.md](templates/HANDOFF.md)

The optional user focus is:

```text
$ARGUMENTS
```

The current Claude session ID is:

```text
${CLAUDE_SESSION_ID}
```

## Procedure

### 1. Establish the active task

Determine from the conversation and authoritative project material:

- the single active objective;
- the definition of done;
- the current phase;
- applicable user requirements and constraints;
- decisions and invariants that still govern the work;
- explicitly rejected or superseded approaches;
- unresolved failures, blockers, and uncertainty;
- the smallest executable next action.

Do not merge unrelated tasks into one handoff. If the session contains several
threads, preserve only the thread the user is currently continuing and list
other unfinished threads as deferred context.

### 2. Collect deterministic state

Run:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" collect \
  --cwd "$PWD" \
  --session-id "${CLAUDE_SESSION_ID}"
```

Use the returned project root, project key, storage directory, branch, HEAD,
status, changed-file list, and timestamp as verified evidence.

Also inspect only the project material needed to verify the active task:

- applicable `CLAUDE.md`, `CLAUDE.local.md`, and scoped rules;
- the active issue, task, plan, architecture contract, or implementation note;
- files changed or discussed during the session;
- relevant diffs;
- the latest validation output already present in the conversation or files.

Do not run broad or expensive test suites solely to create a handoff. Low-cost
read-only verification is allowed. Record any validation not rerun as reused
session evidence rather than fresh evidence.

### 3. Write a draft

Use the exact template and evidence labels from the supporting files. Keep the
handoff concise enough to be reconstructed quickly:

- target: at most 300 lines;
- hard limit: 32 KiB;
- no full large diffs;
- no full raw logs;
- no environment dumps;
- no secret values.

For every material claim, distinguish:

- **VERIFIED** — confirmed from current repository, filesystem, or command
  output;
- **SESSION EVIDENCE** — recorded in this conversation but not rerun now;
- **INFERRED** — a reasoned conclusion that still needs verification;
- **UNKNOWN** — unresolved.

Repository state and authoritative tracked contracts override conversation
claims.

Write the draft to a temporary file outside the repository. Obtain the path
with:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" draft-path \
  --cwd "$PWD" \
  --kind handoff
```

### 4. Validate and publish atomically

Validate the draft:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" validate \
  --kind handoff \
  --file "<draft-path>"
```

Resolve every validation error. Do not suppress a credential warning without
reading the flagged line and confirming it contains only a safe placeholder.

Publish only after validation succeeds:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" publish \
  --kind handoff \
  --source "<draft-path>" \
  --cwd "$PWD" \
  --session-id "${CLAUDE_SESSION_ID}" \
  --label "$ARGUMENTS"
```

The helper atomically replaces `CURRENT.md`, writes sidecar metadata, and
archives the same validated content.

### 5. Re-read the published handoff

Read the final `CURRENT.md` path returned by `publish`. Check for:

- contradictions between objective and next action;
- incorrect branch, HEAD, or working-tree claims;
- completion claims unsupported by evidence;
- stale rejected approaches presented as active decisions;
- missing material blockers;
- leaked secret values;
- a vague or non-executable next action.

If the final file is wrong, correct a new draft and publish again. Never report
success merely because a file exists.

## Stop conditions

Stop and report instead of publishing when:

- the active objective cannot be identified without guessing;
- the current directory cannot be resolved safely;
- authoritative project state materially contradicts the conversation and the
  correct state cannot be established;
- required handoff sections cannot be completed honestly;
- the draft contains a suspected credential or private key;
- the helper or atomic publish fails;
- the next action cannot be stated as a concrete operation.

## Required final output

Return exactly this structure:

```text
HANDOFF CREATED

Objective:
<one sentence>

Handoff:
<absolute CURRENT.md path>

Archive:
<absolute archive path>

Repository State:
- Root: <path>
- Branch: <branch or NOT A GIT REPOSITORY>
- HEAD: <abbreviated SHA or NOT APPLICABLE>
- Working tree: CLEAN / DIRTY / NOT APPLICABLE

Next Exact Action:
<one concrete action>

Material Uncertainty:
<none, or concise statement>

Next Commands:
/clear <short-sanitized-label>
/resume-handoff
```

Do not attempt to execute `/clear` yourself. Do not perform the next action in
the same turn after publishing the handoff. `/resume-handoff` only reloads and
verifies this handoff, reports the reconstructed state, and waits for explicit
user instructions; it never starts the task automatically.
