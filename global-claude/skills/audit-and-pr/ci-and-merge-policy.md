# CI and Merge Policy

## Poll CI

After the PR exists, inspect checks using the repository's GitHub tooling.

Poll approximately every 30 seconds.

Stop after 20 minutes.

## States

### Green

Every configured required check reaches a successful terminal state.

### Red

Any required check fails, errors, cancels, times out, or otherwise ends unsuccessfully.

Do not merge.

### Unresolved

Checks remain queued/running after the cap, status cannot be determined, an expected required check is absent, or branch protection reports an unmet condition.

Do not merge.

### No CI (repository has no CI system configured)

The repository has no CI workflows or checks configured at all - not merely
zero checks reported on this PR. Unless the user explicitly requested CI,
repository governance explicitly requires CI, or the current task
specifically includes establishing CI, this is an accepted repository state,
not a gap.

Zero checks in this state count as green. Apply the automatic-merge rules
exactly as if required CI were green.

This is distinct from Unresolved above, which covers a repository that does
have CI configured but where an expected check is absent, still pending, or
its status cannot be determined for this PR.

## CI configuration additions

A missing CI check may be added during remediation only when `minimal-sufficient-testing` marks the wiring ELIGIBLE.

After adding it:

1. Re-audit the workflow change.
2. Push it with the implementation.
3. Confirm the new check appears on the PR.
4. Confirm it passes.

Do not treat a local pass as sufficient when the purpose was durable CI enforcement.

Never automatically change:

- branch protection
- required-status settings
- workflow permissions
- secrets
- credentials
- runners
- deployment/release behavior
- repository governance

## Automatic merge gate

Automatic merge requires all:

- shipment gate cleared
- testing confidence High
- required CI green, or the repository has no CI as an accepted state
- required CI enforcement present, when CI is required
- no required review missing
- protection allows merge without bypass
- no unaudited commits appeared
- no P0/P1 remains

## High-risk changes

When CI exists for a High-risk change, at least one relevant, independent CI
check must run and pass before automatic merge - this does not change.

When the repository has no CI as an accepted state, the No-CI rule below
applies to High-risk changes exactly as it does to any other risk level: the
absence of CI does not by itself require manual review or block automatic
merge.

## Moderate confidence

Moderate confidence allows PR preparation but never automatic merge.

Stop for manual review and name the limitation. This is unrelated to CI: it
applies whether or not CI exists, and the absence of CI must never be the
named limitation.

## No-CI rule

A repository with no CI configured is an accepted state, not a limitation,
unless the user explicitly requested CI, repository governance explicitly
requires CI, or the current task specifically includes establishing CI. It
does not by itself lower confidence, create a finding, create a tracking
issue, require manual review, or block automatic merge.

When no CI exists:

- Any risk level, at High confidence, may auto-merge exactly as it would
  with green required CI.
- Moderate confidence still requires manual review - the same rule that
  applies when CI exists, unrelated to CI's absence.

## Failed or unresolved CI

Do not modify code and retry during the CI phase.

A CI fix is a new implementation change requiring another audit cycle.

Report check name, state, concise failure detail, and PR URL.

## Protection

Never:

- use admin bypass
- force merge
- dismiss checks
- bypass review
- alter protection
- substitute your own approval

If merge fails because repository controls block it, report and stop.

## Merge method

Follow repository convention.

If none is evident, default to squash.

Delete remote branch when consistent with repository practice.

## Local cleanup

After successful merge:

1. Switch to default branch.
2. Pull or fast-forward.
3. Verify feature branch merged.
4. Safely delete local feature branch.
5. Preserve unrelated work.

Never force-delete an unmerged branch.
