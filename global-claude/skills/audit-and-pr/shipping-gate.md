# Shipping Gates

This workflow has three gates and three independent confidence/eligibility
decisions. Do not collapse them.

Confidence and eligibility decisions:

- **Testing confidence** reflects direct evidence for the exact audited code
  state.
- **CI enforcement confidence** reflects durable CI coverage.
- **Merge eligibility** applies repository-specific merge policy plus live
  audit, verification, CI, review, and protection state.

Workflow gates:

- **Deterministic preflight** decides whether the implementation is ready for a
  deep independent audit.
- **Audit eligibility** decides whether the independently audited implementation
  may be committed for shipment.
- **Final exact-HEAD verification** validates the committed SHA immediately
  before push and PR operations.

Repository verification never replaces the independent audit.

## Gate 0: deterministic preflight

Run after repository safety, branch/HEAD, canonical base, merge-base, and audit
scope are established, but before the deep independent audit.

Follow `repository-verification-policy.md`.

### Adapter present and valid

Run safely:

```text
./scripts/verify doctor
```

Run the base-aware fast profile when required by risk, change type, repository
policy, or lack of reusable exact-HEAD evidence:

```text
./scripts/verify fast --base <resolved-base>
```

A documentation-only or trivially low-risk change may skip `fast` with an
explicit evidence-based reason. Do not run the full `ship` profile at this gate.

In normal mode, continue only after all required preflight invocations return
effective exit `0` with no contradictory output and no adapter-caused HEAD or
working-tree change. In a `BASELINE_RESTORATION` candidate, `doctor` must still
pass. A `fast` exit `1` may be retained only as comparison evidence while the
canonical-base and branch failure ledger is built under
`baseline-restoration-policy.md`; exit `2` through `5` or any protocol,
environment, HEAD, or tree defect still blocks.

### Adapter absent

When `./scripts/verify` genuinely does not exist, record `NOT_APPLICABLE`,
preserve legacy validation discovery and workflow, and continue. Do not create
an adapter or fail solely because it is absent.

### Adapter invalid or failed

Block before the deep audit when the path exists but is invalid or a required
preflight invocation returns nonzero, times out, is interrupted, contradicts
success, changes HEAD, or changes the working tree, except for the narrowly
retained `fast` exit `1` comparison evidence described above. That evidence does
not clear preflight until the untouched canonical base is reproduced and the
preliminary ledger contains no new, unattributed, untracked, or protected-domain
residual.

Never fall back to legacy validation after a present adapter fails.

## Gate 1: audit eligibility

Evaluate the final authoritative independent audit after all retained
remediation, targeted validation, evidence reconciliation, and re-audit rounds.

### Block when

- verdict is FAIL;
- result is AUDIT BLOCKED;
- any P0 remains;
- any P1 remains;
- a finding required by the current objective or acceptance criteria is being
  deferred as P2/P3;
- any confirmed P2/P3 lacks a complete issue-ready tracking record;
- testing confidence is Low;
- a testing stop condition remains;
- required deterministic preflight is unresolved or failed, unless the only
  retained exit `1` is the exact authoritative lane under an otherwise eligible
  `BASELINE_RESTORATION` comparison;
- CI enforcement confidence is Low because required enforcement is missing,
  newly weakened, or violates repository policy;
- objective is unsatisfied;
- an unexplained validation failure remains; known restoration residuals count
  as explained only when the complete ledger classifies them as
  `UNCHANGED_TRACKED_BASELINE` or `PRE_EXISTING_NEWLY_UNMASKED` and every owner
  is an open canonical issue;
- a required parallel audit lane failed, became stale, or remained uncovered.

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
- every remaining P2/P3 is genuinely non-blocking, independently closeable, was
  not modified by remediation, and has a complete issue-ready tracking record;
- testing confidence is High or Moderate;
- no required stop condition remains;
- required `doctor` and applicable `fast` preflight passed, or adapter absence
  was confirmed and legacy validation remains acceptable;
- all lane results were bound to the current audit state and synthesized;
- CI enforcement confidence is High or Not Applicable, or a documented accepted
  repository-wide limitation is Moderate and does not violate audit eligibility
  policy.

Clearing this gate permits branch preparation and a scoped commit. It does not
permit push, PR creation/update, issue creation, or merge. Confirmed P2/P3
findings remain `PASS WITH GAPS`; their actual open-issue links are mandatory
after final exact-HEAD verification and push, before PR mutation or merge.

### CI coverage limitation rule

At this gate, testing confidence is provisional until the final exact-HEAD ship
or legacy gate completes. A documented repository-wide CI coverage limitation
must not reduce testing confidence merely because some required checks are
local-only.

After final verification passes, or an exact-HEAD result receives a complete
`FAILED_PRE_EXISTING_BASELINE` classification, testing confidence may remain
`HIGH` when:

- direct evidence covers the exact committed code state;
- the authoritative final ship or legacy gate passed;
- the working tree remained clean;
- no commit followed;
- planned versus executed checks reconcile.

CI enforcement confidence and merge eligibility remain separate. Manual merge
is the default for an accepted Moderate CI-enforcement limitation unless
repository policy explicitly permits automatic merge with that exact condition.

## Gate 2: final exact-HEAD verification

Run only after the final independently audited scope has been committed and the
working tree is clean.

Record:

```text
git rev-parse HEAD
git status --porcelain
```

Status output must be empty. Preserve the canonical base resolved before the
audit. If repository or PR state invalidates it, resolve again and restart the
affected audit scope rather than guessing.

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

This is the mandatory full repository ship gate. It normally runs once for each
final committed candidate, not once before audit and not once after every
remediation edit.

### Adapter absent

Preserve the legacy repository validation and shipping workflow. Adapter absence
is not itself a finding or blocker unless repository policy separately requires
it.

### Normal green result

Exit `0` with no contradiction and unchanged clean repository state clears the
normal final gate.

### Controlled baseline-restoration result

If and only if the final adapter exits `1`, evaluate
`baseline-restoration-policy.md`. Do not reinterpret the adapter result. A fully
eligible comparison is classified `FAILED_PRE_EXISTING_BASELINE`. It permits
push and PR creation, requires manual merge, and never permits auto-merge.

### Block when

- a present adapter is non-executable, a directory, invalid, or unusable;
- canonical base cannot be resolved or validated;
- adapter exits `1` without complete `BASELINE_RESTORATION` eligibility;
- adapter exits `2`, `3`, `4`, `5`, or any unsupported nonzero code;
- adapter is interrupted or times out;
- adapter output contradicts exit `0`;
- HEAD changes while the gate runs;
- the command changes staged, unstaged, or untracked state;
- the exact result cannot be established;
- legacy validation fails without an equivalent complete restoration
  classification for the repository-native mandatory lane.

When blocked:

- retain the local commit;
- do not push;
- do not file tracking issues from the failed shipment attempt. The sole
  exception is an exact canonical issue for an independently proven newly
  unmasked baseline residual after audit; creating it does not clear the gate,
  and the restoration decision must be rerun before push;
- do not create or update a PR;
- do not merge;
- report the committed SHA, base, exact command, exit state, captured output,
  and dirty paths if any.

Any corrective edit is new implementation work. It requires:

1. a bounded fix;
2. targeted validation;
3. an independent re-audit against the new state;
4. a new commit;
5. a clean tree;
6. another final exact-HEAD ship run.

A normal green result permits push and PR creation/update. A complete
`FAILED_PRE_EXISTING_BASELINE` classification also permits push and PR
creation/update, but requires the full ledger in the PR and manual merge. Neither
result by itself permits merge.
