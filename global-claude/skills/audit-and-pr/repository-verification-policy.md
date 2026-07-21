# Repository Verification Policy

Repository Verification V1 is a repository-local deterministic verification
contract. Repository verification never replaces the independent audit.

Repository verification answers whether the repository's declared checks ran
and passed. The independent audit still decides whether those checks are
sufficient and whether the implementation is logically, architecturally,
securely, and operationally ready to merge.

## Canonical base resolution

Resolve the base before adapter invocation using the skill's established Git
and PR context, in this order:

1. an explicitly supplied valid audit base;
2. the existing PR target branch;
3. the remote default branch.

Prefer the remote-tracking form when available, such as `origin/develop`.
Validate the candidate as a commit and calculate the merge base. Do not
hardcode `origin/main`, `origin/master`, or any repository-specific branch.

If no canonical base can be resolved, stop before adapter invocation. Report
the candidates examined and the failure. Never guess.

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

Invoke exactly:

```text
./scripts/verify ship --base <resolved-base>
```

The helper at `scripts/repository_verification.py` performs safe invocation and
evidence capture when executable helpers are available. Pass the repository,
resolved base, the existing command timeout, and audited changed paths as
separate arguments.

### Adapter absent

When `./scripts/verify` genuinely does not exist:

- record Repository Verification V1 as not installed;
- preserve the legacy validation workflow;
- continue legacy repository-native validation and independent audit;
- do not create an adapter;
- do not treat absence as a finding unless repository policy separately
  requires adoption.

### Invalid adapter state

When the path exists but is a directory, non-executable, broken, an invalid
launcher, or otherwise unusable:

- block shipment as a repository configuration defect;
- preserve diagnostic output;
- do not `chmod`, repair, replace, or bypass it automatically;
- do not fall back to legacy validation.

Fallback is permitted only for genuine absence.

## Invocation evidence

Capture for every adapter invocation:

- repository path;
- invocation HEAD;
- resolved base;
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

Handle adapter exit codes exactly:

- `0`: repository ship gate passed; independent audit may continue;
- `1`: one or more required checks failed; block;
- `2`: invalid invocation or unsupported argument; block as integration or
  protocol defect;
- `3`: adapter, configuration, or protocol error; block;
- `4`: required dependency, environment, service, browser, secret, or tool is
  unavailable; block as environment;
- `5`: interrupted or timed out; block.

Never fall back to legacy validation after exit `1` through `5`. Never treat a
nonzero result as advisory. Unsupported exit codes are protocol defects and
block.

## Contradictory success output

Human-readable adapter output is valid; JSON is not required. However, exit
`0` is not acceptable when the adapter's own output explicitly reports:

- planned count differs from executed count;
- required check omitted;
- blocking check unavailable;
- incomplete execution;
- duplicate terminal results;
- missing terminal results;
- reconciliation failure;
- internal adapter failure.

Treat this as an adapter/protocol defect. Also block if the adapter changes
`HEAD` or changes the working-tree state while running.

## Required invocation points

### Initial deterministic gate

After repository safety, branch/HEAD, canonical base, merge base, and intended
audit scope are established:

1. detect the adapter;
2. run `ship --base <resolved-base>` when valid;
3. stop immediately on any blocker;
4. continue independent audit only after exit `0`, or after confirmed adapter
   absence and the legacy validation path.

A successful initial run does not authorize shipment.

### Remediation revalidation

After any retained remediation round changes tracked files:

1. run targeted validation selected by `minimal-sufficient-testing`;
2. rerun `ship --base <resolved-base>`;
3. capture the current HEAD and complete result;
4. stop remediation and shipment on any blocker;
5. perform the complete independent re-audit required by the remediation
   policy.

Do not rely on an earlier successful run after tracked content changes.

### Final exact-HEAD gate

After audit eligibility clears and the final audited scope is committed:

1. require a clean working tree;
2. record the exact committed HEAD;
3. rerun `ship --base <resolved-base>`;
4. require exit `0` with no contradictory output, HEAD change, or tree change;
5. bind the result to that SHA.

Only this final result can satisfy the repository-verification condition for
push, PR operations, and merge. If the PR head later differs, restart audit and
verification for the new commit.

For adapter-absent repositories, the final verification condition is the
preserved legacy validation result plus the independent audit and existing
shipping gates.

## Independent audit authority

Ship exit `0` does not equal audit approval. Valid blocking outcomes include:

- deterministic ship passes but the independent audit fails;
- declared tests omit material behavior;
- authorization or tenancy logic is incorrect;
- architecture, data, migration, privacy, or governance risk remains;
- verification machinery was weakened;
- CI, review, branch protection, or merge policy blocks.

Keep repository verification, independent audit, CI, PR state, and merge state
separate in reasoning and reporting.

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
2. inspect the adapter changes directly;
3. confirm no required check was removed or improperly weakened;
4. inspect expected-versus-executed reconciliation;
5. inspect allowlists and baselines for excessive breadth;
6. inspect unavailable and skipped behavior;
7. classify false-green paths as P0 or P1;
8. require focused conformance evidence;
9. do not trust the modified adapter solely because it exits `0`.

Never remediate by making checks advisory, broadening blanket allowlists or
baselines, disabling tests, adding skips, or lowering thresholds merely to get
green output. Verification machinery may change only when the finding is in
that machinery and the change receives independent review.

## Timeout and interruption

Reuse the skill or repository command-timeout framework. Do not impose an
arbitrarily short timeout on `ship`.

On timeout or interruption:

- terminate the adapter and its child process group safely;
- prevent orphaned child processes;
- preserve stdout and stderr;
- report timeout or interruption distinctly;
- block with effective exit `5`;
- never continue as though verification passed.
