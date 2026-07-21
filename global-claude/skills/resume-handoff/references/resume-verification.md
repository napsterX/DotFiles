# Resume Verification Policy

## Core rule

A handoff is recovery evidence, not execution authority.

Verify enough current state to explain whether the handoff is still coherent,
then stop and wait for the user. Never continue the task from this skill.

## Read-only boundary

Allowed:

- reading the current handoff and metadata;
- reading applicable project instructions and named files;
- read-only repository inspection such as branch, HEAD, status, log, and diff;
- the session-continuity helper's read-only `locate` and `collect` commands.

Not allowed:

- implementation edits;
- tests, builds, linters, migrations, or repository verification;
- starting or stopping project processes;
- Git or GitHub mutations;
- executing the handoff's next action.

## Verification depth

Use the smallest read-only verification sufficient to detect material drift.
Read actual changed files and relevant contracts. Do not run the repository
suite merely to restore context.

## Drift severity

### Expected drift

Expected drift is explicitly predicted by the handoff and does not invalidate
its context. Examples:

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

Material drift changes the report. It does not authorize this skill to fix or
continue anything.

## Validation confidence

### High

Current repository, requirements, changed files, and handoff context are
verified. Relevant recorded validation still applies, and no material unknown
remains.

### Moderate

The objective and repository state are verified, but a named environmental,
runtime, or prior-test limitation remains.

### Low

A material requirement, code state, boundary, or validation claim cannot be
verified.

Confidence describes context quality only. No confidence level permits
continuation from `/resume-handoff`.

## Conflict handling

Current tracked contracts win over the handoff. Current code wins over a claim
that code was changed. A passing result from another commit does not apply to
current unvalidated changes.

Report conflicts explicitly, preserve the handoff's documented next action as
informational context when useful, and end with `AWAITING USER INSTRUCTIONS`.
