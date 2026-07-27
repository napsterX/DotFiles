---
name: resume-handoff
description: Locate and verify the exact latest operational handoff for the current repository family, reconstruct context, report selection or freshness failures, then stop and wait for explicit user instructions.
argument-hint: ""
user-invocable: true
model: opus
effort: high
---

# Resume Handoff

Load verified context only. Never execute the handoff's next action, modify files, run
validation, or make Git/GitHub changes.

Read [references/resume-verification.md](references/resume-verification.md).

## Hard stop contract

Read-only inspection is allowed. Implementation, tests, builds, migrations,
repository verification, process changes, Git mutations, GitHub mutations, and
automatic continuation are prohibited.

## Procedure

### 1. Resolve the repository family and candidate task worktree

Do not assume `$PWD` identifies the worktree recorded by the handoff. Use the
current directory only to identify the repository family. The published metadata
must identify the actual task worktree.

Run:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" locate \
  --cwd "$PWD" \
  --kind handoff
```

The command must validate current/archive hashes, sidecar identity, and the latest
pointer before returning a handoff. If it fails, report metadata or selection
failure; do not search arbitrary old handoffs and pretend recovery succeeded.

### 2. Read identity before narrative

Capture and report:

- handoff ID and generated time;
- source session ID;
- selection method;
- repository family;
- recorded active task worktree;
- recorded branch and HEAD;
- current invocation directory and current worktree;
- content hash;
- helper freshness classification.

Read the returned handoff and metadata. Then collect fresh state against the
**recorded active task worktree**, not blindly against `$PWD`:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" collect \
  --cwd "<recorded-active-worktree>" \
  --session-id "${CLAUDE_SESSION_ID}"
```

If the recorded worktree no longer exists, classify the handoff as
`WORKTREE_UNAVAILABLE` and stop after reporting context.

### 3. Distinguish publication/selection failure from later drift

Compare handoff identity and current state.

Classifications:

- **CURRENT** — exact handoff selected; recorded task worktree, branch, HEAD, and
  material status still agree.
- **EXPECTED_DRIFT** — explicitly predicted change does not invalidate context.
- **MATERIAL_DRIFT** — the handoff was valid but current state later changed.
- **SELECTION_MISMATCH** — located artifact is not the latest published ID or
  points to the wrong task worktree.
- **INVALID_AT_PUBLICATION** — recorded claims were already inconsistent with the
  publication snapshot or omitted work that existed before publication.
- **METADATA_INVALID** — pointer, sidecar, archive, or digest mismatch.
- **UNVERIFIABLE** — required evidence is unavailable.

Do not infer that another session changed the repository merely because HEAD
differs. Use timestamps, publication metadata, and commit times. When the cause
cannot be proven, say so.

### 4. Reconstruct context without masking failure

Read applicable project instructions and named authoritative files. An
implementation log or issue comment may be used as supplemental recovery
evidence, but it does not convert a failed handoff into a successful recovery.
State explicitly:

```text
Handoff recovery: FAILED_<classification>
Supplemental recovery source: <source or none>
```

### 5. Stop

Return the report and stop at `AWAITING USER INSTRUCTIONS`.

## Required loaded report

```text
HANDOFF LOADED

Handoff Identity:
- ID: <id>
- Generated: <timestamp>
- Source session: <id>
- Selection method: <method>
- Repository family: <identity>
- Recorded active worktree: <path>
- Recorded branch: <branch>
- Recorded HEAD: <sha>
- Content SHA-256: <hash>

Handoff:
<absolute path>

Objective:
<one sentence>

Definition of Done:
<concise statement>

Current Verified State:
- Invocation directory: <path>
- Active task worktree: <path or unavailable>
- Branch: <branch>
- HEAD: <sha>
- Working tree: <state>

Freshness:
CURRENT / EXPECTED_DRIFT / MATERIAL_DRIFT / SELECTION_MISMATCH /
INVALID_AT_PUBLICATION / METADATA_INVALID / UNVERIFIABLE
- <details>

Handoff Recovery:
SUCCESS / FAILED_<classification>

Supplemental Recovery Evidence:
<none or sources, clearly secondary>

Completed Work:
- <item>

Remaining Work:
- <item>

Validation State:
- Confidence: HIGH / MODERATE / LOW
- Evidence: <summary>

Constraints and Risks:
- <item>

Documented Next Action:
<informational only>

Status:
AWAITING USER INSTRUCTIONS
```

## No-handoff report

```text
HANDOFF NOT FOUND

Current Directory:
<path>

Status:
AWAITING USER INSTRUCTIONS
```
