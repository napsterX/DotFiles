# CI, Merge, and Cleanup Policy

## Poll CI

After the PR exists, inspect checks using the repository's GitHub tooling.

Poll approximately every 30 seconds.

Stop after 20 minutes.

## States

### Green

Every configured required check reaches a successful terminal state.

### Red

Any required check fails, errors, cancels, times out, or otherwise ends
unsuccessfully.

Do not merge.

### Unresolved

Checks remain queued/running after the cap, status cannot be determined, an
expected required check is absent, or branch protection reports an unmet
condition.

Do not merge.

### No CI (repository has no CI system configured)

The repository has no CI workflows or checks configured at all - not merely
zero checks reported on this PR. Unless the user explicitly requested CI,
repository governance explicitly requires CI, or the current task specifically
includes establishing CI, this is an accepted repository state, not a gap.

Zero checks in this state count as green. Apply the automatic-merge rules
exactly as if required CI were green.

This is distinct from Unresolved above, which covers a repository that does
have CI configured but where an expected check is absent, still pending, or its
status cannot be determined for this PR.

## CI configuration additions

A missing CI check may be added during remediation only when
`minimal-sufficient-testing` marks the wiring ELIGIBLE.

After adding it:

1. Re-audit the workflow change.
2. Commit the audited change.
3. Re-run `./scripts/verify ship --base <resolved-base>` for the new exact SHA when the adapter is present, or the preserved legacy final validation when absent.
4. Push it with the implementation.
5. Confirm the new check appears on the PR.
6. Confirm it passes.

Do not treat a local pass as sufficient when the purpose was durable CI
enforcement.

Never automatically change:

- branch protection;
- required-status settings;
- workflow permissions;
- secrets;
- credentials;
- runners;
- deployment/release behavior;
- repository governance.

## Independent merge inputs

Keep these fields separate through the entire PR phase:

- `testing_confidence`: HIGH / MODERATE / LOW;
- `ci_enforcement_confidence`: HIGH / MODERATE / LOW / NOT_APPLICABLE;
- `merge_eligibility`: AUTO_MERGE_ELIGIBLE / MANUAL_MERGE_REQUIRED / BLOCKED;
- `deferred_findings_tracking`: COMPLETE / NOT_APPLICABLE / TRACKING BLOCKED.

A documented repository-wide CI coverage limitation does not lower testing
confidence when the exact audited commit passed the authoritative ship gate and
all change-relevant high-risk checks were directly executed. It may set CI
enforcement confidence to Moderate and may require manual merge under repository
policy.

If CI and local evidence conflict, investigate the conflict. Testing confidence
may change because the evidence is contradictory, not because CI coverage is
incomplete.

## Automatic merge gate

Automatic merge requires all:

- audit eligibility gate cleared;
- final Repository Verification or legacy gate passed for the exact PR HEAD;
- testing confidence High;
- required CI green, or the repository has no CI as an accepted state;
- CI enforcement confidence High or Not Applicable, unless repository policy explicitly permits automatic merge with a documented accepted Moderate enforcement limitation;
- merge eligibility classified AUTO_MERGE_ELIGIBLE;
- no required review missing;
- protection allows merge without bypass;
- no unaudited commits appeared;
- no P0/P1 remains;
- deferred-finding tracking is COMPLETE or NOT_APPLICABLE, with every confirmed
  P2/P3 mapped to an equivalent open GitHub issue.

Immediately before merge, confirm the PR head SHA still equals the SHA that
passed `./scripts/verify ship --base <resolved-base>` when the adapter is present, or the final legacy validation when absent. If it differs, stop and restart from audit of the
new commit.

## High-risk changes

When CI exists for a High-risk change, at least one relevant, independent CI
check must run and pass before automatic merge.

When the repository has no CI as an accepted state, the No-CI rule below
applies to High-risk changes exactly as it does to any other risk level: the
absence of CI does not by itself require manual review or block automatic merge.

## Moderate testing confidence

Moderate testing confidence allows PR preparation but never automatic merge.
Stop for manual review and name the actual testing limitation.

A documented repository-wide CI coverage limitation is not, by itself, a reason
for Moderate testing confidence. Report it under CI enforcement confidence.

## Moderate CI enforcement confidence

When CI exists but a documented accepted repository-wide architecture limitation
leaves required high-risk checks local-only:

- keep testing confidence based on direct exact-HEAD evidence;
- record CI enforcement confidence as Moderate;
- apply repository-specific merge policy;
- require manual merge by default unless repository policy explicitly allows
  automatic merge with that exact limitation.

Do not globalize a repository-specific auto-merge exception.

## No-CI rule

A repository with no CI configured is an accepted state, not a limitation,
unless the user explicitly requested CI, repository governance explicitly
requires CI, or the current task specifically includes establishing CI. It does
not by itself lower confidence, create a finding, create a tracking issue,
require manual review, or block automatic merge.

When no CI exists:

- any risk level, at High confidence, may auto-merge exactly as it would with
  green required CI;
- Moderate testing confidence still requires manual review; CI absence is unrelated.

## Failed or unresolved CI

Do not modify code and retry during the CI phase.

A CI fix is a new implementation change requiring another audit cycle, a new
commit, and another final Repository Verification or legacy gate run.

Report check name, state, concise failure detail, and PR URL.

## Protection

Never:

- use admin bypass;
- force merge;
- dismiss checks;
- bypass review;
- alter protection;
- substitute your own approval.

If merge fails because repository controls block it, report and stop.

If deferred-finding tracking is incomplete, merge is blocked independently of
CI, review, and protection state. Do not treat a green PR as permission to merge
while a confirmed P2/P3 lacks an open issue link.

## Merge method

Follow repository convention.

If none is evident, default to squash.

Request remote source-branch deletion as part of merge only when repository
practice and permissions permit it. Failure to delete the remote branch does
not invalidate a confirmed merge, but it must be reported.

## Mandatory post-merge cleanup

Run only after GitHub confirms the PR is merged and provides the resulting
merge commit or equivalent merged state.

1. Record the merged PR URL, source branch, default branch, and merge commit.
2. Ensure unrelated local work is not present. If unrelated local work would be
   endangered by switching branches, do not stash, reset, clean, or overwrite
   it. Report cleanup as blocked and leave the work untouched.
3. Switch to the default branch.
4. Fetch `origin` and fast-forward the local default branch only. Never create a
   merge commit merely to update it and never reset it destructively.
5. Verify the merged PR's changes are present on the updated default branch.
6. Verify the local feature branch is fully merged into the updated default
   branch.
7. Delete the local feature branch with `git branch -d <branch>` only. Never use
   `-D`.
8. Confirm the remote feature branch was deleted by the merge operation. If it
   remains and repository practice permits deletion, delete only that exact
   merged remote branch with `git push origin --delete <branch>`.
9. Confirm the final branch, HEAD, working-tree status, and remaining local and
   remote feature-branch state.

Cleanup must never:

- delete the default branch;
- delete a branch not proven merged;
- delete an unrelated branch;
- discard local changes;
- use `git reset --hard`, `git clean`, forced checkout, or forced branch
  deletion;
- treat cleanup failure as permission to rewrite history.

If merge succeeds but cleanup is partially blocked, report
`MERGED — CLEANUP INCOMPLETE`, name the exact residue, and preserve it safely.
