# Baseline Restoration Policy

`BASELINE_RESTORATION` is a narrow shipment classification for incrementally
repairing an already-red mandatory repository lane. It is not a general waiver
for failed checks and it never turns a red gate green.

Normal mode remains the default: any unexplained or branch-caused required gate
failure blocks push, PR mutation, and merge.

## Invocation and conservative inference

The user may request the mode explicitly:

```text
/audit-and-pr baseline-restoration
```

The skill may also classify a run as a baseline-restoration candidate when the
canonical issue, current implementation handoff, or authoritative repository
evidence clearly states that the branch repairs one or more identified failures
from an already-red mandatory lane.

A red check by itself is never enough to infer the mode. Before any remote
mutation, report whether the mode source is `EXPLICIT` or `INFERRED`, the target
failure, the canonical base, and the authoritative lane or command.

Any other invocation argument is invalid.

## Candidate versus eligible

Selecting or inferring the mode creates only a candidate. Eligibility exists
only after every requirement in this policy is proven against the exact
canonical base and final audited branch HEAD.

## Required evidence

Prove all of the following:

1. Resolve the canonical audit base using the normal base-resolution policy.
2. Reproduce the relevant mandatory lane on an untouched checkout or disposable
   detached worktree at that exact base commit.
3. Use the repository's own authoritative verification adapter or documented
   mandatory lane, with the same profile, material environment, and dependency
   conditions used for the branch comparison.
4. Record every base failure with an exact identity:
   - check or test name;
   - first causal error;
   - material environment or profile;
   - canonical open tracking issue.
5. Prove the branch fixes at least one identified base failure.
6. Prove the repaired target passes on the implementation branch.
7. Prove the remaining branch failure set is an unchanged subset of the base
   failure set, except for independently proven pre-existing failures newly
   unmasked when an earlier setup blocker was removed.
8. Give every newly unmasked pre-existing failure its own canonical open issue
   before push or PR creation.
9. Prove the branch introduces no new or unattributed failure.
10. Run every change-specific validation and every mandatory gate not blocked by
    the known baseline failure set.
11. Complete the independent audit with no remaining in-scope P0 or P1 and at
    least Moderate testing confidence.
12. Prove neither the implementation nor the audit remediation weakened,
    disabled, skipped, quarantined, retried, reclassified, or extended the
    timeout of the failing gate merely to obtain a favorable comparison.
13. Prove the issue, handoff, or repository record identifies this change as
    incremental restoration of the already-red lane.
14. Bind the final comparison to the exact final audited committed HEAD and a
    clean working tree.

## Base-versus-branch failure ledger

Build this complete ledger:

| Failure identity | Base result | Branch result | Owner | Disposition |
|------------------|-------------|---------------|-------|-------------|

A failure identity includes the check or test name, first causal error, and
material environment or profile. Do not merge distinct first causal errors into
one row.

Allowed dispositions:

- `FIXED_BY_BRANCH`: failed on the canonical base and passes on the branch.
- `UNCHANGED_TRACKED_BASELINE`: the exact failure remains on both base and branch
  and has a canonical open issue.
- `PRE_EXISTING_NEWLY_UNMASKED`: not visible in the aggregate base run because an
  earlier blocker prevented execution, but independently proven to exist at the
  base commit and linked to a canonical open issue.
- `NEW_REGRESSION`: appears only on the branch and is plausibly caused by the
  current diff.
- `UNATTRIBUTED`: cannot be proven to be an unchanged or newly unmasked
  pre-existing failure.

Any `NEW_REGRESSION` or `UNATTRIBUTED` row blocks shipment.

## Protected domains

Never use this mode to bypass a residual failure involving:

- security;
- authorization;
- tenancy isolation;
- migration safety;
- data integrity;
- payment correctness;
- destructive operations;
- privacy.

A protected-domain gate that remains red blocks shipment even when the same
failure exists on the canonical base. Fixing a protected-domain failure is not a
waiver for another protected-domain residual.

## Verification execution limits

- Run the canonical-base reproduction once.
- Run the branch comparison once.
- Do not rerun intermittent failures until a favorable sample appears.
- Rerun the affected comparison only after a retained remediation changes files
  relevant to the lane or its verification machinery.
- If the canonical base, environment, command, or verification machinery changes,
  invalidate the comparison and reproduce it again.
- Do not install tools, inject fake credentials, or alter repository configuration
  to manufacture comparable results.

## Final ship-gate handling

Run the normal final command against the exact final committed HEAD:

```text
./scripts/verify ship --base <resolved-base>
```

- Exit `0`: proceed under normal green-gate policy. The exception is not needed.
- Exit `1`: evaluate this policy. A nonzero result may proceed only when the
  complete final ledger proves eligibility.
- Exit `2`, `3`, `4`, `5`, timeout, interruption, contradictory output, HEAD
  mutation, or working-tree mutation: block. These are not baseline failures.

When eligible, classify the aggregate gate truthfully as:

```text
FAILED_PRE_EXISTING_BASELINE
```

This permits push and PR creation only. It does not permit automatic merge.

## Merge policy

Every baseline-restoration PR requires a maintainer or user to merge manually.
Never enable auto-merge, invoke an automatic merge command, or treat branch
protection as satisfied by the exception.

State that the exception is scoped to the recorded ledger and creates no
precedent for unrelated PRs. Normal green-gate policy resumes when the baseline
lane is restored.

## PR requirements

In addition to normal PR content, include:

1. The target failure fixed by the branch.
2. Exact canonical-base reproduction command, commit, environment/profile, and
   result.
3. Exact final branch command, commit, environment/profile, and result.
4. The complete base-versus-branch failure ledger.
5. Links to every residual failure owner.
6. A statement that no new or unattributed failure appeared.
7. All change-specific and non-blocked mandatory validation.
8. The aggregate ship command and truthful nonzero result.
9. The `FAILED_PRE_EXISTING_BASELINE` classification.
10. The manual-merge requirement.
11. The statement that normal green-gate policy resumes after baseline repair.

## Non-default integration branches

When the PR target is an integration branch that is not GitHub's default branch:

- do not rely on `Closes`, `Fixes`, or equivalent keywords to close the issue;
- after the maintainer or user confirms merge, manually reconcile the target
  issue according to repository policy;
- record the PR number, reviewed head, merge SHA, audit disposition, and
  baseline-restoration classification;
- only then perform normal safe branch and worktree cleanup.

Never assume a specific repository uses `staging`, `develop`, or another branch.
