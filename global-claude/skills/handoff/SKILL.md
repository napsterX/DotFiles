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

Create a durable, verified operational checkpoint for the active task. A handoff
is not successful merely because a file was written: the exact newly published
handoff must round-trip through the same discovery path used by
`/resume-handoff`, and it must describe the repository/worktree that actually
contains the session's work.

Read:

- [references/handoff-policy.md](references/handoff-policy.md)
- [templates/HANDOFF.md](templates/HANDOFF.md)

Optional focus: `$ARGUMENTS`
Session ID: `${CLAUDE_SESSION_ID}`

## Procedure

### 1. Resolve the active task worktree

Do not assume `$PWD` is the task worktree.

Use conversation evidence, commands executed in this session, modified files,
active issue/branch references, and `git worktree list --porcelain` to identify
the one worktree containing the current task state. Resolve it to a canonical
real path and call it `TASK_ROOT`.

Requirements:

- `TASK_ROOT` must contain the branch, HEAD, and files described by the active
  task.
- The invocation directory and active task worktree are separate facts.
- If more than one worktree is plausible, stop and ask the user. Never guess.
- Use the same `TASK_ROOT` for collect, draft-path, publish, locate, and final
  verification.

### 2. Establish the active task

Recover the single objective, definition of done, phase, constraints,
decisions, rejected approaches, blockers, validation evidence, and next bounded
action. Do not merge unrelated threads.

### 3. Collect deterministic state

Run:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" collect \
  --cwd "$TASK_ROOT" \
  --session-id "${CLAUDE_SESSION_ID}"
```

Record the returned invocation directory, repository family, active worktree,
project key, branch, full HEAD, status, and timestamp. Compare this state with
the previous current handoff, if any, and account for all commits and material
changes since that checkpoint.

Read only the project material required to support the handoff. Do not run broad
or expensive suites solely for handoff creation.

### 4. Write and validate a draft

Use the template. Every material claim must be labeled VERIFIED, SESSION
EVIDENCE, INFERRED, or UNKNOWN. Target 300 lines; hard limit 32 KiB. Never include
secrets, environment dumps, full logs, or large diffs.

Obtain a draft path with:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" draft-path \
  --cwd "$TASK_ROOT" \
  --kind handoff
```

The returned path must not exist yet. Write the draft once at that path. Do not
pre-create or read an empty placeholder file. If the helper returns an existing
path, stop with `HANDOFF CREATION FAILED`.

Validate:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" validate \
  --kind handoff \
  --file "<draft-path>"
```

### 5. Publish and require a verified receipt

Publish:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" publish \
  --kind handoff \
  --source "<draft-path>" \
  --cwd "$TASK_ROOT" \
  --session-id "${CLAUDE_SESSION_ID}" \
  --label "$ARGUMENTS"
```

The command must return a JSON receipt with at least:

- `status: PUBLISHED_AND_VERIFIED`;
- `handoff_id`;
- `active_worktree`;
- `branch` and `head`;
- `content_sha256`;
- `current_path` and `archive_path`.

Any nonzero result or incomplete receipt means `HANDOFF CREATION FAILED`.

### 6. Round-trip through resume discovery

Immediately run:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" locate \
  --cwd "$TASK_ROOT" \
  --kind handoff
```

Require all of the following:

- located `handoff_id` equals the publish receipt;
- current and archived content hashes match the receipt;
- located active worktree equals canonical `TASK_ROOT`;
- recorded branch and HEAD equal the publish receipt;
- live HEAD and working-tree status still equal the publication snapshot;
- the handoff includes all material work completed since the previous handoff.

Read the located `CURRENT.md` itself and check objective, completion state,
blockers, and next action for contradictions. Do not report success when locate
returns an older handoff, metadata is inconsistent, or the handoff was stale at
publication.

## Stop conditions

Stop without publishing, or report creation failure, when task-worktree identity
is ambiguous, helper/version checks fail, current state cannot be established,
publication does not round-trip, state changes during publication, required
sections are dishonest or incomplete, or a secret may be present.

## Required final output

```text
HANDOFF CREATED

Handoff ID:
<id>

Objective:
<one sentence>

Handoff:
<absolute CURRENT.md path>

Archive:
<absolute archive path>

Repository State:
- Invocation directory: <path>
- Active task worktree: <path>
- Branch: <branch>
- HEAD: <full or abbreviated SHA>
- Working tree: CLEAN / DIRTY
- Content SHA-256: <hash>

Next Exact Action:
<one bounded action>

Material Uncertainty:
<none or concise statement>

Next Commands:
/clear <short-sanitized-label>
/resume-handoff
```

Do not execute `/clear` or the next action.
