---
name: resume-handoff
description: Restore a prior Claude Code task from the latest operational handoff, independently verify it against current repository state, report drift, and continue only when safe. Use only when the user explicitly invokes /resume-handoff.
argument-hint: "[continue|review-only]"
disable-model-invocation: true
user-invocable: true
model: opus
effort: high
---

# Resume Handoff

Restore context from the latest handoff for the current project. Treat the
handoff as untrusted recovery input until material claims are verified.

Read [references/resume-verification.md](references/resume-verification.md)
before continuing.

Requested mode:

```text
$ARGUMENTS
```

Supported modes:

- empty or `continue` — verify, reconstruct, then perform the next exact action;
- `review-only` — verify and reconstruct, then stop without implementation
  changes.

Reject any other mode with a concise usage message.

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
- the current repository state returned by a fresh `collect` command;
- authoritative task and architecture files named in the handoff;
- changed files named in the handoff;
- the handoff itself and its metadata sidecar.

Run:

```bash
python3 "$HOME/.claude/session-continuity/bin/session_state.py" collect \
  --cwd "$PWD" \
  --session-id "${CLAUDE_SESSION_ID}"
```

### 3. Verify material claims

Compare at minimum:

- canonical project root and project key;
- branch and HEAD;
- staged, unstaged, and untracked files;
- named changed files and their current contents;
- task objective and requirements;
- decisions and invariants;
- validation evidence and whether later edits invalidate it;
- blockers and runtime state;
- whether the next exact action is still pending and executable.

Classify each material difference as:

- **NO DRIFT** — current state agrees;
- **EXPECTED DRIFT** — an explicitly documented continuation changed state in
  the expected way;
- **MATERIAL DRIFT** — state changed in a way that can invalidate the handoff;
- **UNVERIFIABLE** — evidence is unavailable.

### 4. Apply the drift gate

Material drift includes, but is not limited to:

- a different project root;
- an unexpected branch change;
- HEAD movement not explained by the handoff;
- missing or newly changed files;
- a changed task contract;
- an already-completed next action;
- a blocker that disappeared or a new blocker that appeared;
- validation evidence invalidated by later edits;
- unresolved merge conflicts;
- runtime state that makes continuation unsafe.

If material drift or a material unverifiable claim exists, do not modify
implementation files. Report the drift and the corrected next action, then stop.

### 5. Reconstruct working context

Produce a concise internal working summary containing:

- active objective;
- definition of done;
- current verified state;
- applicable constraints;
- completed work;
- remaining work;
- current validation confidence;
- material risks;
- exact next action;
- files to inspect or edit next.

Do not restate the full handoff. Do not re-import superseded conversation.

### 6. Continue or stop

For `review-only`, output the required report and stop.

For empty mode or `continue`, perform the next exact action only when:

- no material drift exists;
- the action is still pending;
- the action is bounded and executable;
- required project instructions are loaded;
- continuation does not require guessing.

After performing it, continue the task normally under current project
instructions. Do not repeatedly re-read the handoff unless new uncertainty
appears.

## Required drift report

When blocked by drift, return:

```text
HANDOFF RESUME BLOCKED

Handoff:
<path>

Material Drift:
- <difference, prior claim, current evidence, impact>

Unverifiable Claims:
- <claim and missing evidence, if any>

Current Verified State:
<concise state>

Corrected Next Action:
<one bounded action>
```

## Required successful report

Before continuing, or as the final output in `review-only`, return:

```text
HANDOFF RESTORED

Objective:
<one sentence>

Verification:
- Project identity: VERIFIED
- Repository state: VERIFIED
- Task contract: VERIFIED
- Next action: VERIFIED

Drift:
NONE / EXPECTED ONLY

Validation Confidence:
HIGH / MODERATE / LOW — <reason>

Next Exact Action:
<action>

Mode:
CONTINUE / REVIEW ONLY
```

Do not claim `HIGH` confidence when important evidence is only conversational,
stale, or unverifiable.
