---
name: resume-handoff
description: Locate and verify the current operational handoff, reconstruct the active task and current repository state, report material drift, then stop and wait for explicit user instructions. Never starts or continues implementation.
argument-hint: ""
disable-model-invocation: true
user-invocable: true
model: opus
effort: high
---

# Resume Handoff

Restore verified context from the current handoff, present the reconstructed
state, and stop.

This skill is a context-loading operation only. It must never execute the
handoff's next action, resume implementation, run validation, modify files, or
make Git/GitHub changes.

Read [references/resume-verification.md](references/resume-verification.md)
before loading the handoff.

This skill accepts no mode or continuation argument. If `$ARGUMENTS` is not
empty, ignore it only when it is a harmless label; otherwise state that
`/resume-handoff` always loads context and waits for instructions.

## Hard stop contract

After reading and reporting, return control to the user.

Never:

- edit implementation, test, configuration, documentation, or handoff files;
- execute the documented next action;
- run tests, builds, linters, migrations, servers, or repository verification;
- create, switch, merge, delete, commit, or push branches;
- create or update issues or pull requests;
- continue automatically because the handoff appears valid;
- treat the handoff as permission to act.

Read-only commands needed to establish current state are allowed.

## Procedure

### 1. Locate the handoff

Run:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" locate \
  --cwd "$PWD" \
  --kind handoff
```

If no current handoff exists, stop. Do not scan unrelated repositories or guess
which previous session the user meant.

### 2. Read current authority before trusting the handoff

Read:

- applicable project instructions;
- the handoff and its metadata sidecar;
- authoritative task and architecture files named in the handoff;
- changed files named in the handoff;
- current repository state returned by a fresh read-only `collect` command.

Run:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" collect \
  --cwd "$PWD" \
  --session-id "${CLAUDE_SESSION_ID}"
```

Do not run any command whose purpose is to validate or advance the task.

### 3. Verify material claims

Compare at minimum:

- canonical project root and project key;
- branch and HEAD;
- staged, unstaged, and untracked files;
- named changed files and their current contents;
- task objective and requirements;
- decisions and invariants;
- recorded validation evidence and whether later edits invalidate it;
- blockers and runtime state;
- whether the documented next action is still pending.

Classify each material difference as:

- **NO DRIFT** — current state agrees;
- **EXPECTED DRIFT** — explicitly predicted state changed as expected;
- **MATERIAL DRIFT** — current state can invalidate the handoff;
- **UNVERIFIABLE** — evidence is unavailable.

### 4. Reconstruct working context

Produce a concise summary containing:

- active objective;
- definition of done;
- current verified state;
- applicable constraints and invariants;
- completed work;
- remaining work;
- recorded validation and its current applicability;
- material drift or unverifiable claims;
- blockers and risks;
- documented next action;
- files most likely relevant to the user's next instruction.

Do not restate the full handoff. Do not import superseded conversation context.

### 5. Stop and wait

Do not correct drift, perform the next action, or continue the task.

Return exactly one of the report structures below and stop.

## Required loaded report

```text
HANDOFF LOADED

Handoff:
<absolute path>

Objective:
<one sentence>

Definition of Done:
<concise statement>

Current Verified State:
- Project:
- Branch:
- HEAD:
- Working tree:

Completed Work:
- <verified or session-evidence item>

Remaining Work:
- <item>

Validation State:
- Confidence: HIGH / MODERATE / LOW
- Evidence: <concise summary>

Drift:
NONE / EXPECTED ONLY / MATERIAL / UNVERIFIABLE
- <details when applicable>

Constraints and Risks:
- <item>

Documented Next Action:
<one bounded action from the handoff; informational only>

Status:
AWAITING USER INSTRUCTIONS
```

## Required no-handoff report

```text
HANDOFF NOT FOUND

Current Directory:
<path>

Status:
AWAITING USER INSTRUCTIONS
```

Never append an offer to begin the documented next action. The user decides
what happens next.
