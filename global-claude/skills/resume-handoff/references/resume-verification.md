# Resume Verification Policy

## Core rule

Never continue because the handoff sounds coherent. Continue because current
state confirms that the handoff remains coherent.

## Verification depth

Use the smallest verification sufficient to detect material drift. Read the
actual changed files and relevant contracts. Do not run the full repository
suite merely to restore context unless the handoff's next action is itself a
validation action.

## Drift severity

### Expected drift

Expected drift is explicitly predicted by the handoff and does not invalidate
the next action. Examples:

- a temporary process is no longer running and the handoff said it may stop;
- an untracked generated artifact was intentionally removed;
- the handoff was archived after creation without changing the project.

### Material drift

Material drift can change what work is correct or safe. Examples:

- code or contracts changed outside the documented session;
- branch or HEAD differs unexpectedly;
- changed-file set differs;
- the active ticket was revised;
- the documented next action was already completed;
- test evidence no longer applies to the current tree;
- the handoff points at files that no longer exist;
- a new conflict, lock, failing process, or migration state exists.

## Validation confidence

### High

Current repository, requirements, changed files, and next action are verified.
Relevant validation evidence applies to the current code state, and no material
unknown remains.

### Moderate

The objective and repository state are verified, but a named environmental,
runtime, or prior-test limitation remains. Work can continue if the next action
addresses or does not depend on that limitation.

### Low

A material requirement, code state, boundary, or validation claim cannot be
verified. Low confidence blocks continuation.

## Conflict handling

Current tracked contracts win over the handoff. Current code wins over a claim
that code was changed. A passing result from another commit does not win over
current unvalidated changes. Report the conflict explicitly and derive a new
next action from current evidence.
