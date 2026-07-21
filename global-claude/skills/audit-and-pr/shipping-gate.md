# Shipping Gates

This workflow has three shipping gates and three independent confidence/eligibility decisions. Do not collapse them.

Confidence and eligibility decisions:

- **Testing confidence** reflects direct evidence for the exact audited code state.
- **CI enforcement confidence** reflects durable CI coverage.
- **Merge eligibility** applies repository-specific merge policy plus live audit, verification, CI, review, and protection state.

Shipping gates:

- **Initial repository verification** decides whether the independent audit may
  begin under adapter or legacy mode.
- **Audit eligibility** decides whether the independently audited implementation
  may be committed for shipment.
- **Final exact-HEAD verification** validates the committed SHA immediately
  before push and PR operations.

Repository verification never replaces the independent audit.

## Gate 0: initial repository verification

Run after repository safety, branch/HEAD, canonical base, merge-base, and audit
scope are established, but before the independent audit.

Follow `repository-verification-policy.md`.

### Adapter present and valid

Run with argument separation:

```text
./scripts/verify ship --base <resolved-base>
```

Continue only after effective exit `0` with no contradictory output and no
adapter-caused HEAD or working-tree change.

### Adapter absent

When `./scripts/verify` genuinely does not exist, record
`NOT_APPLICABLE`, preserve the legacy validation workflow, and continue. Do not
create an adapter or fail solely because it is absent.

### Adapter invalid or failed

Block before independent audit when the path exists but is invalid or when the
adapter returns any nonzero result, times out, is interrupted, contradicts
success, changes HEAD, or changes the working tree.

Never fall back to legacy validation after a present adapter fails.

## Gate 1: audit eligibility

Evaluate the final independent audit after retained remediation and all required
post-remediation repository-verification reruns.

### Block when

- verdict is FAIL;
- result is AUDIT BLOCKED;
- any P0 remains;
- any P1 remains;
- testing confidence is Low;
- a testing stop condition remains;
- the latest required Repository Verification result is blocked;
- CI enforcement confidence is Low because required enforcement is missing, newly weakened, or violates repository policy;
- objective is unsatisfied;
- an unexplained validation failure remains.

When blocked:

- leave retained safe fixes uncommitted;
- do not create a shipping branch;
- do not commit;
- do not push;
- do not file issues;
- do not open or update a PR;
- report blockers and retained local changes;
- include the smallest safe follow-up prompt.

### Clear when

- verdict is PASS or PASS WITH GAPS;
- no P0/P1 remains;
- testing confidence is High or Moderate;
- no required stop condition remains;
- the latest adapter run passed, or adapter absence was confirmed and legacy
  validation remains acceptable;
- CI enforcement confidence is High or Not Applicable, or a documented accepted repository-wide limitation is classified Moderate and does not violate the audit eligibility policy.

Clearing this gate permits branch preparation and a scoped commit. It does not
permit push, PR creation/update, or merge.

### CI coverage limitation rule

A documented repository-wide CI coverage limitation must not lower testing
confidence when the exact audited code state satisfies all required direct
evidence, the authoritative ship gate passed, the working tree remained clean,
no commit followed, and planned versus executed checks reconcile.

In that case:

- testing confidence may remain `HIGH`;
- CI enforcement confidence is reported separately, normally `MODERATE`;
- audit eligibility may clear;
- merge eligibility is determined later from repository policy, and defaults to
  manual review when CI exists but required high-risk checks are local-only
  unless repository policy explicitly permits automatic merge.

Do not create a per-change implementation finding for an accepted repository-
wide limitation unless the audited change weakens verification or violates an
explicit repository rule.

## Gate 2: final exact-HEAD verification

Run only after the final independently audited scope has been committed and the
working tree is clean.

Record:

```text
git rev-parse HEAD
git status --porcelain
```

The status output must be empty. Preserve the canonical base resolved before
the audit; if repository or PR state invalidates it, resolve again and restart
the affected audit scope rather than guessing.

### Valid adapter

Run exactly, with the base as one argument:

```text
./scripts/verify ship --base <resolved-base>
```

Require all:

- adapter exit `0`;
- no contradictory success output;
- verified SHA equals the recorded pre-run SHA;
- working tree remains clean and unchanged;
- no unaudited commit appeared.

### Adapter absent

Preserve the legacy repository validation and shipping workflow. Adapter
absence is not itself a finding or blocker unless repository policy separately
requires it.

### Block when

- a present adapter is non-executable, a directory, invalid, or unusable;
- canonical base cannot be resolved or validated;
- adapter exits `1`, `2`, `3`, `4`, `5`, or any unsupported nonzero code;
- adapter is interrupted or times out;
- adapter output contradicts exit `0`;
- HEAD changes while the gate runs;
- the command changes staged, unstaged, or untracked state;
- the exact result cannot be established;
- legacy validation fails for an adapter-absent repository.

When blocked:

- retain the local commit;
- do not push;
- do not file tracking issues from the failed shipment attempt;
- do not create or update a PR;
- do not merge;
- report the committed SHA, base, exact command, exit state, captured output,
  and dirty paths if any.

Any corrective edit is new implementation work. It requires:

1. a bounded fix;
2. targeted validation;
3. Repository Verification rerun when present;
4. a complete independent re-audit;
5. a new commit;
6. a clean tree;
7. another final exact-HEAD verification run.

Clearing this gate permits push and PR creation/update. It does not by itself
permit merge.
