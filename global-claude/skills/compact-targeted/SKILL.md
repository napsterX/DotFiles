---
name: compact-targeted
description: Prepare a concise, verified preservation anchor before Claude Code compacts the current conversation, so the same active task can continue with less context loss. Use only when the user explicitly invokes /compact-targeted.
argument-hint: "[optional-preservation-focus]"
disable-model-invocation: true
user-invocable: true
model: opus
effort: high
---

# Targeted Compact

Prepare a preservation anchor for the single active task, publish it outside the
repository, and print the exact built-in `/compact` command the user should run.

This skill does not and cannot execute `/compact`. Do not claim compaction has
occurred.

Read:

- [references/compaction-policy.md](references/compaction-policy.md)
- [templates/COMPACT-ANCHOR.md](templates/COMPACT-ANCHOR.md)

Optional preservation focus:

```text
$ARGUMENTS
```

Session ID:

```text
${CLAUDE_SESSION_ID}
```

## Procedure

### 1. Identify the coherent active task

Preserve only the task currently being executed. Determine:

- active objective and definition of done;
- applicable requirements and constraints;
- current verified repository state;
- files that matter next;
- decisions and invariants;
- valid test or validation evidence;
- unresolved failure or uncertainty;
- rejected approaches likely to recur;
- exact next action.

Use the optional focus to prioritize detail, not to override authoritative
requirements or omit material blockers.

### 2. Collect deterministic state

Run:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" collect \
  --cwd "$PWD" \
  --session-id "${CLAUDE_SESSION_ID}"
```

Inspect the relevant diff and task files when needed. Do not run implementation
work or expensive validation.

### 3. Write the anchor

Use the exact template. Target at most 180 lines and enforce a hard limit of
8 KiB. Prefer precise file paths, commands, and decisions over narrative.

Classify material statements as `VERIFIED`, `SESSION EVIDENCE`, `INFERRED`, or
`UNKNOWN` using the same evidence discipline as `/handoff`.

Obtain a temporary path:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" draft-path \
  --cwd "$PWD" \
  --kind compact
```

Write the anchor there.

### 4. Validate and publish

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" validate \
  --kind compact \
  --file "<draft-path>"
```

Then:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" publish \
  --kind compact \
  --source "<draft-path>" \
  --cwd "$PWD" \
  --session-id "${CLAUDE_SESSION_ID}" \
  --label "$ARGUMENTS"
```

The installed `SessionStart(compact)` hook will re-inject a fresh anchor after
manual or automatic compaction when the session and project match.

### 5. Report

Return exactly:

```text
COMPACTION ANCHOR READY

Anchor:
<absolute COMPACT-CURRENT.md path>

Objective:
<one sentence>

Preservation Focus:
<focus or GENERAL ACTIVE-TASK CONTINUITY>

Next Exact Action:
<one action>

Run Now:
/compact Preserve the active objective, definition of done, applicable constraints, verified repository state, changed files, decisions and invariants, validation evidence, unresolved failures, rejected approaches, and exact next action from the latest COMPACTION ANCHOR. Discard superseded discussion, duplicate explanations, completed exploration, and verbose logs. Do not invent missing state.
```

Do not perform additional work after printing the command.

## Stop conditions

Stop without publishing if:

- there is no coherent single active task;
- current repository state materially contradicts the task and cannot be
  reconciled;
- a material blocker cannot be represented honestly;
- a suspected secret is present;
- the anchor exceeds the hard limit after removing nonessential detail;
- validation or atomic publish fails.
