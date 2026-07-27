# Resume Verification Policy

## Core rule

A handoff is recovery evidence, not execution authority. First prove that the
artifact selected is the exact latest verified publication for the repository
family. Then compare its recorded task worktree with current state.

## Identity-first verification

Before reading the narrative, verify:

- latest pointer, current sidecar, and archive share one handoff ID;
- current and archive content match the recorded SHA-256;
- repository-family identity matches;
- recorded active worktree is explicit;
- publication timestamp and source session are available.

Never silently fall back to an older `CURRENT.md` or archive entry.

## Drift versus publication failure

A HEAD mismatch alone does not prove later drift.

- `MATERIAL_DRIFT` requires evidence that the handoff was valid when published
  and the repository changed afterward.
- `INVALID_AT_PUBLICATION` applies when omitted commits or contradictory state
  already existed before publication.
- `SELECTION_MISMATCH` applies when discovery returned a different handoff than
  the latest verified publication or the wrong worktree identity.
- If timing cannot distinguish these cases, use `UNVERIFIABLE`; do not invent an
  explanation involving another session.

## Supplemental evidence

Implementation logs, issue comments, and Git history may help reconstruct the
current state. They remain supplemental. Report continuity failure honestly and
do not promote them into a successful handoff result.

## Read-only boundary

Allowed: handoff/metadata reads, project-instruction reads, Git status/log/diff,
and helper `locate`/`collect` calls.

Forbidden: implementation, tests, builds, linters, migrations, repository
verification, process mutation, Git/GitHub mutation, or executing the next action.

## Confidence

HIGH means identity, current state, and relevant recorded evidence all reconcile.
MODERATE means context is coherent with named limitations. LOW means identity,
state, or a material claim cannot be verified.

Every report ends with `AWAITING USER INSTRUCTIONS`.
