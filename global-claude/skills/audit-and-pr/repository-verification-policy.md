# Repository Verification Policy

Repository Verification V1 is a repository-local deterministic verification
contract. Repository verification never replaces the independent audit.

The workflow uses lightweight deterministic profiles before the audit and the
full authoritative `ship` profile only for the final committed audited HEAD.

## Canonical base resolution

Resolve the base before any base-aware adapter invocation using the established
Git and PR context, in this order:

1. an explicitly supplied valid audit base;
2. the existing PR target branch;
3. the remote default branch.

Prefer the remote-tracking form when available, such as `origin/develop`.
Validate the candidate as a commit and calculate the merge base. Do not hardcode
`origin/main`, `origin/master`, or any repository-specific branch.

If no canonical base can be resolved, stop before adapter invocation. Report the
candidates examined and the failure. Never guess.

Use argument separation. The base is one argument even when it contains
punctuation. Do not use `eval` or concatenate repository-controlled values into
a shell command.

## Adapter state

Inspect `./scripts/verify` without modifying it.

### Valid adapter

A valid adapter:

- exists;
- is a regular file;
- is executable.

Supported invocations in this skill are:

```text
./scripts/verify doctor
./scripts/verify fast --base <resolved-base>
./scripts/verify ship --base <resolved-base>
```

Use `scripts/repository_verification.py` for safe invocation and evidence
capture when executable helpers are available. Pass repository path, profile,
resolved base, timeout, and changed paths as separate arguments.

### Adapter absent

When `./scripts/verify` genuinely does not exist:

- record Repository Verification V1 as not installed;
- preserve the legacy validation workflow;
- continue legacy repository-native validation discovery and independent audit;
- use the existing legacy final validation before push and PR operations;
- do not create an adapter;
- do not treat absence as a finding unless repository policy separately
  requires adoption.

### Invalid adapter state

When the path exists but is a directory, non-executable, broken, an invalid
launcher, or otherwise unusable:

- block as a repository configuration defect;
- preserve diagnostic output;
- do not `chmod`, repair, replace, or bypass it automatically;
- do not fall back to legacy validation.

Fallback is permitted only for genuine absence.

## Invocation evidence

Capture for every adapter invocation:

- repository path;
- profile;
- invocation HEAD;
- resolved base when applicable;
- exact argument-safe command;
- adapter exit code;
- effective workflow result;
- duration;
- stdout;
- stderr;
- planned count when reported;
- executed count when reported;
- pass count when reported;
- failure count when reported;
- unavailable count when reported;
- advisory count when reported.

Preserve output for diagnosis, but never print the full environment or expose
secret values. Do not inject fake credentials, install tools or browser
binaries, start Docker, weaken repository configuration, or reinterpret a
missing dependency as success.

## Exit codes

Handle adapter exit codes exactly for `doctor`, `fast`, and `ship`:

- `0`: the invoked profile passed;
- `1`: one or more required checks failed; block the current stage;
- `2`: invalid invocation or unsupported argument; block as integration or
  protocol defect;
- `3`: adapter, configuration, or protocol error; block;
- `4`: required dependency, environment, service, browser, secret, or tool is
  unavailable; block as environment;
- `5`: interrupted or timed out; block.

Never fall back to legacy validation after exit `1` through `5`. Never treat a
nonzero result as advisory. Unsupported exit codes are protocol defects.

## Contradictory success output

Human-readable output is valid; JSON is not required. Exit `0` is not acceptable
when the adapter's own output explicitly reports:

- planned count differs from executed count;
- required check omitted;
- blocking check unavailable;
- incomplete execution;
- duplicate terminal results;
- missing terminal results;
- reconciliation failure;
- internal adapter failure.

Treat this as an adapter/protocol defect. Also block if any invoked profile
changes `HEAD` or the working-tree state.

## Pre-audit deterministic stage

After repository safety, branch/HEAD, canonical base, merge-base, and intended
audit scope are established:

1. detect adapter state;
2. when valid, run:

   ```text
   ./scripts/verify doctor
   ```

3. run:

   ```text
   ./scripts/verify fast --base <resolved-base>
   ```

   when code or configuration changed, risk is Medium or High, repository policy
   requires it, or no reusable exact-HEAD fast evidence exists;
4. permit a documented `fast` skip only for documentation-only or trivially
   low-risk changes where the evidence plan does not require it;
5. stop before the deep independent audit on any required preflight blocker;
6. when the adapter is absent, preserve legacy validation discovery and
   continue.

Do not invoke `ship` in the normal pre-audit stage. `doctor` and `fast` are
fail-fast readiness checks, not audit approval.

A `fast` failure means the implementation is not audit-ready. Preserve output
and stop rather than spending deep-audit time on a deterministically broken
state. No legacy fallback is allowed for a present adapter.

## Remediation revalidation

After a retained remediation round changes tracked files:

1. run targeted validation selected by `minimal-sufficient-testing`;
2. reconcile the remediation evidence plan;
3. rerun `fast --base <resolved-base>` only when the remediation invalidates
   earlier preflight evidence, repository policy requires it, or verification
   machinery changed;
4. require focused conformance evidence when verification machinery changed;
5. perform the independent re-audit against a fresh immutable packet.

Do not run `ship` after every remediation round. The deterministic evidence
inside the loop should be the minimum sufficient evidence for the exact fixes.
The complete ship suite is reserved for the final committed candidate.

## Final exact-HEAD gate

After audit eligibility clears and the final audited scope is committed:

1. require a clean working tree;
2. record the exact committed HEAD;
3. run exactly:

   ```text
   ./scripts/verify ship --base <resolved-base>
   ```

4. require exit `0` with no contradictory output, HEAD change, or tree change;
5. bind the result to that SHA.

Only this final result can satisfy the repository-verification condition for
push, PR operations, and merge. If the PR head later differs, restart audit and
verification for the new commit.

For adapter-absent repositories, the final verification condition remains the
preserved legacy validation result plus the independent audit and existing
shipping gates.

If final `ship` fails, retain the local commit and stop before push, tracking
issues, PR mutation, or merge. Any correction is new implementation work and
requires targeted validation, independent re-audit, a new commit, and another
final ship run.

## Independent audit authority

A passing `doctor`, `fast`, or `ship` profile does not equal audit approval.
Valid blocking outcomes include:

- deterministic profiles pass but the independent audit fails;
- declared tests omit material behavior;
- authorization or tenancy logic is incorrect;
- architecture, data, migration, privacy, or governance risk remains;
- verification machinery was weakened;
- CI, review, branch protection, or merge policy blocks.

Keep preflight, final repository verification, independent audit, CI, PR state,
and merge state separate in reasoning and reporting.

## Verification-governance-sensitive changes

Activate heightened scrutiny when the audited diff modifies verification
machinery, including:

- `scripts/verify` or `scripts/verify.*`;
- adapter helpers or tests;
- verification registries or profile membership;
- scanner configuration;
- allowlists or accepted baselines;
- skip logic or applicability rules;
- blocking/advisory classification;
- thresholds or timeouts;
- exit-code handling;
- planned-versus-executed reconciliation;
- ship governance;
- `github-minimal` workflows.

Then:

1. flag the audit as verification-governance-sensitive;
2. add the dedicated governance audit lane when parallel mode is active;
3. inspect adapter changes directly;
4. confirm no required check was removed or improperly weakened;
5. inspect expected-versus-executed reconciliation;
6. inspect allowlists and baselines for excessive breadth;
7. inspect unavailable and skipped behavior;
8. classify false-green paths as P0 or P1;
9. require focused conformance evidence;
10. do not trust the modified adapter solely because it exits `0`.

Never remediate merely to get green output by making checks advisory,
broadening blanket allowlists or baselines, disabling tests, adding skips, or
lowering thresholds. Verification machinery may change only when the finding is
in that machinery and the change receives independent review.

## Timeout and interruption

Reuse the skill or repository command-timeout framework. Do not impose an
arbitrarily short timeout on `doctor`, `fast`, or `ship`.

On timeout or interruption:

- terminate the adapter and child process group safely;
- prevent orphaned child processes;
- preserve stdout and stderr;
- report timeout or interruption distinctly;
- block with effective exit `5`;
- never continue as though the profile passed.
