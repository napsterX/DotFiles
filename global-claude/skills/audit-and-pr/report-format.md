# Final Report Format

Return:

```text
AUDIT AND PR RESULT

Audit Model:
<model and effort>

Objective:
<one sentence>

Invocation Source:
- Type: DIRECT_USER / FIX_ISSUES_DELEGATED
- Manifest: <absolute path> / NOT_APPLICABLE
- Manifest status: VALID / REJECTED / NOT_APPLICABLE
- Source skill: fix-issues / NOT_APPLICABLE
- Batch starting HEAD: <sha> / NOT_APPLICABLE
- Delegated final HEAD: <sha> / NOT_APPLICABLE
- Fixed issues: <numbers> / NOT_APPLICABLE

Operating Mode:
- Mode: NORMAL / BASELINE_RESTORATION
- Source: DEFAULT / EXPLICIT / INFERRED
- Target already-red lane: <name or NOT_APPLICABLE>
- Target failure: <identity or NOT_APPLICABLE>
- Classification announced before remote mutation: YES / NO / NOT_APPLICABLE

Worktree Execution:
- Invocation root:
- Task root:
- Git common directory:
- Target branch:
- Initial target HEAD:
- Worktree class: CURRENT / CLAUDE_MANAGED / EXTERNAL_REGISTERED
- Execution mode: IN_PLACE / ENTERWORKTREE / PINNED_TASK_ROOT
- EnterWorktree attempted: YES / NO
- Cross-worktree safety: PASS / BLOCKED

Audited Scope:
- Repository:
- Branch:
- Canonical base:
- Merge-base:
- Diff/range:
- Initial HEAD:
- Final audited HEAD:
- Verification-governance-sensitive: YES / NO

Deterministic Preflight:
- Adapter: ./scripts/verify / not present / invalid
- Validation mode: Repository Verification V1 / legacy audit workflow
- Doctor command: ./scripts/verify doctor / NOT_APPLICABLE
- Doctor result: exit <code> / NOT_APPLICABLE / NOT RUN
- Doctor duration:
- Fast command: ./scripts/verify fast --base <resolved-base> / NOT_APPLICABLE
- Fast result: exit <code> / NOT_APPLICABLE / SKIPPED
- Fast skip reason: <reason> / NONE
- Fast duration:
- Fast planned/executed: <n>/<n> / not reported
- Preflight status: PASS / NOT_APPLICABLE / BLOCKED_REQUIRED_CHECK / BLOCKED_INVOCATION / BLOCKED_ADAPTER / BLOCKED_CONFIGURATION / BLOCKED_ENVIRONMENT / BLOCKED_TIMEOUT / BLOCKED_INTERRUPTED / BLOCKED_PROTOCOL / BLOCKED_BASE_RESOLUTION
- Contradictions: <details> / NONE
- Output evidence: <concise diagnostic summary; preserve complete captured output in the working record>

Baseline Restoration:
- Candidate: YES / NO
- Canonical base directly reproduced: YES / NO / NOT_APPLICABLE
- Canonical base commit:
- Authoritative lane/profile:
- Base command:
- Base result:
- Branch command:
- Branch result:
- Comparison environment/profile:
- Comparison reruns: <count and reason> / NONE
- Target failure repaired: YES / NO / NOT_APPLICABLE
- Failure ledger complete: YES / NO / NOT_APPLICABLE
- Ledger:
  | Failure identity | Base result | Branch result | Owner | Disposition |
  |------------------|-------------|---------------|-------|-------------|
  | ... | ... | ... | ... | FIXED_BY_BRANCH / UNCHANGED_TRACKED_BASELINE / PRE_EXISTING_NEWLY_UNMASKED / NEW_REGRESSION / UNATTRIBUTED |
- New regressions: NONE / <rows>
- Unattributed failures: NONE / <rows>
- Protected-domain residuals: NONE / <rows>
- Residual canonical issues: <links> / NOT_APPLICABLE
- Eligibility: ELIGIBLE / BLOCKED / NOT_APPLICABLE
- Blockers: <details> / NONE

Parallel Audit Execution:
- Requested mode: AUTO / SEQUENTIAL / PARALLEL
- Actual mode: SEQUENTIAL / PARALLEL
- Host concurrency available: YES / NO
- Lane count:
- Immutable packet HEAD/base/scope:
- Lanes:
  - <lane>: COMPLETE / FAILED / TIMED OUT / STALE
- Synthesis conflicts resolved:
- Read-only integrity preserved: YES / NO
- Reason for lane plan:

Evidence Contract:
- Planned checks:
  - <check, purpose, required/advisory>
- Planned versus executed:
  - <check>: PASS / FAIL / UNAVAILABLE / NOT RUN / NOT APPLICABLE
- Exact audited code state:
- Change-relevant high-risk checks directly executed: YES / NO / NOT APPLICABLE
- Reconciliation status: COMPLETE / INCOMPLETE / BLOCKED

Final Independent Audit:
- Verdict: ACCEPTED / ACCEPTED_WITH_LOW_RISK_RESIDUALS / BLOCKED_P0_P1 / BLOCKED_VERIFICATION / AUDIT_BLOCKED
- Risk:
- P0 remaining:
- P1 remaining:
- Why deterministic verification was or was not sufficient evidence:

Finding Disposition Table:
| Finding | Severity | Disposition | In current scope? | Rationale | Issue or repair evidence |
|---------|----------|-------------|-------------------|-----------|--------------------------|
| ... | P0/P1/P2/P3 | FIX_NOW / DEFER_TO_ISSUE / ADD_TO_EXISTING_ISSUE / BATCH_INTO_CLEANUP_ISSUE / ACCEPT_AS_LOW_VALUE / DISMISS / BLOCK_ACCEPTANCE | YES/NO | ... | ... |

Disposition Integrity:
- Every material finding has severity and disposition: YES / NO
- Acceptance-critical finding deferred or dismissed: NONE / <blocker>
- Severity downgrade used to avoid remediation: NONE / <blocker>
- Issue gate failures unresolved: NONE / <blocker>
- New-issue budget: <used>/3
- Budget exception: <explanation> / NOT_APPLICABLE

Remediated Now:
- Rounds used:
- Single writer: YES / NO
- Findings:
  - <finding, severity, why immediate repair was appropriate, change, targeted validation, optional fast rerun, independent complete-diff re-audit>
- Post-remediation review: PASS / BLOCKED_REVIEW_INCOMPLETE / BLOCKED_REGRESSION / NOT_APPLICABLE
- Reverted attempts:
- Post-remediation fast runs: <HEAD, command, result, reason> / NONE

Deferred With Issues:
- <finding, severity, impact, evidence, why deferred, proposed remediation, acceptance criteria, components/files, priority, dependencies, issue URL, repository-specific agent route when already supported>

Added To Existing Issues:
- <finding, severity, issue URL, evidence added>

Batched Findings:
- <batch issue URL, shared root cause/outcome, included finding IDs, why batching is economically justified>

Accepted Low-Value Findings:
- <finding, severity, rationale for no repair and no permanent backlog>

Dismissed Findings:
- <finding, severity, duplicate/speculative/irrelevant/outdated/subjective/non-actionable/unsupported rationale>

Final Repository Verification:
- Adapter: ./scripts/verify / not present / invalid
- Profile: ship / NOT_APPLICABLE
- Validation mode: Repository Verification V1 / legacy audit workflow
- Base: <resolved-base>
- Final committed HEAD: <sha>
- Command: ./scripts/verify ship --base <resolved-base> / legacy command
- Result: exit <code> / legacy result / NOT RUN
- Duration:
- Planned/executed: <n>/<n> / not reported
- Pass/failure/unavailable/advisory: <counts or not reported>
- Working tree clean after final gate: YES / NO
- HEAD unchanged through final gate: YES / NO
- Commit added after final gate: YES / NO
- Aggregate gate status: NORMAL_GREEN / FAILED_PRE_EXISTING_BASELINE / NOT_APPLICABLE / BLOCKED
- Status: PASS / FAILED_PRE_EXISTING_BASELINE / NOT_APPLICABLE / BLOCKED_REQUIRED_CHECK / BLOCKED_INVOCATION / BLOCKED_ADAPTER / BLOCKED_CONFIGURATION / BLOCKED_ENVIRONMENT / BLOCKED_TIMEOUT / BLOCKED_INTERRUPTED / BLOCKED_PROTOCOL / BLOCKED_BASE_RESOLUTION
- Contradictions: <details> / NONE
- Output evidence: <concise diagnostic summary; preserve complete captured output in the working record>

Testing Confidence:
- Level: HIGH / MODERATE / LOW
- Reason:
- Material testing limitations: <details or NONE>

CI Enforcement Confidence:
- Level: HIGH / MODERATE / LOW / NOT_APPLICABLE
- CI architecture state:
- Required checks enforced:
- Documented repository-wide limitation: <details or NONE>
- Change-specific enforcement gap: <details or NONE>
- Reason:

Merge Eligibility:
- Classification: AUTO_MERGE_ELIGIBLE / MANUAL_MERGE_REQUIRED / BLOCKED / PENDING_PR_AND_CI
- Baseline-restoration auto-merge prohibited: YES / NO / NOT_APPLICABLE
- Repository-policy reason:
- Live gate reason:

Testing:
- Reused:
- Rerun:
- Newly executed:
- Deliberately omitted:
- Unable to validate:

Issue-Required Finding Tracking:
- Status: COMPLETE / NOT_APPLICABLE / TRACKING BLOCKED
- Findings requiring issues:
- Findings mapped to equivalent open issues:
- Reused open issues:
- Newly created issues:
- New-issue budget used: <n>/3
- Budget exception explained: YES / NO / NOT_APPLICABLE
- Batched mappings:
- Findings:
  - <finding ID, severity, disposition, issue URL, reused/new/batched>
- Untracked issue-required findings: NONE / <finding and reason>
- GitHub unavailable or issue mutation failure: NONE / <reason>

Final Acceptance Decision:
- ACCEPTED
- ACCEPTED_WITH_EXPLICITLY_DOCUMENTED_LOW_RISK_RESIDUALS
- BLOCKED_BY_UNRESOLVED_P0_P1
- BLOCKED_BY_REQUIRED_VERIFICATION
- AUDIT_BLOCKED
- Rationale:

Historical Backlog Hygiene:
- Performed by this run: NO
- Recommended separate bounded operation: YES / NO
- Suggested classifications: KEEP / MERGE / CLOSE_DUPLICATE / CLOSE_OBSOLETE / CLOSE_NON_ACTIONABLE / CLOSE_LOW_VALUE / CONSOLIDATE
- Rationale:

PR Change Summary:
- Source HEAD:
- Managed block action: CREATED / REPLACED / UNCHANGED / BLOCKED
- Included categories: Added / Changed / Fixed / Removed / NONE
- User-facing impact: PRESENT / NO_EXTERNAL_CHANGE
- Breaking changes: PRESENT / NONE
- Issue-required links included: <count>
- Finding-disposition summary included: YES / NO
- Existing PR content preserved outside managed block: YES / NO / NOT_APPLICABLE
- Permanent changelog convention: NONE / CHANGELOG_FILE / CHANGESETS / TOWNCRIER / CUSTOM_FRAGMENT
- Permanent artifact action: PR_BODY_ONLY / VALIDATE_EXISTING / CREATE_REQUIRED_ARTIFACT / BLOCKED
- Permanent artifact validation: PASS / FAIL / NOT_APPLICABLE
- Baseline-restoration section: PRESENT / NOT_APPLICABLE / BLOCKED
- Failure ledger rows included: <count> / NOT_APPLICABLE
- Truthful nonzero aggregate result included: YES / NO / NOT_APPLICABLE
- Manual-merge statement included: YES / NO / NOT_APPLICABLE
- Summary status: READY / BLOCKED_STALE_HEAD / BLOCKED_MARKERS / BLOCKED_SENSITIVE_CONTENT / BLOCKED_CHANGELOG

Git:
- Branch:
- Commits:
- Push:

PR:
- URL:
- Status:

CI:
- GREEN / RED / UNRESOLVED / NOT CONFIGURED — ACCEPTED REPOSITORY STATE
- Details:

Merge:
- Result:
- Merge commit:
- Method:
- Manual merge required by baseline restoration: YES / NO
- Non-default integration target: YES / NO
- Post-merge issue reconciliation: COMPLETE / BLOCKED / NOT_APPLICABLE
- Reconciled issue record: <PR, reviewed head, merge SHA, audit disposition, exception> / NOT_APPLICABLE

Cleanup:
- PR target branch updated:
- GitHub default branch changed or untouched:
- Local feature branch:
- Remote feature branch:
- Final working tree:

Outcome:
- MERGED AND CLEANED UP
- MERGED — CLEANUP INCOMPLETE
- PR OPEN — MANUAL REVIEW REQUIRED
- PR OPEN — BASELINE RESTORATION, MANUAL MERGE REQUIRED
- PR OPEN — CI FAILED
- PR OPEN — CI UNRESOLVED
- TRACKING BLOCKED — BRANCH PUSHED, PR NOT MUTATED
- PREFLIGHT BLOCKED
- FINAL VERIFICATION FAILED — LOCAL COMMIT RETAINED
- SHIPMENT BLOCKED
- AUDIT BLOCKED

Blocking Reason:
<include when not merged and cleaned up>

Smallest Safe Follow-up Prompt:
<include when additional work is required>
```

Keep operating mode, deterministic preflight, baseline-restoration comparison
and ledger, parallel audit execution, evidence reconciliation, finding
disposition, issue-required tracking, final Repository Verification,
independent audit, testing confidence, CI enforcement confidence, CI result, PR
state, merge eligibility, issue reconciliation, and merge result separate. Never collapse the result into “tests passed” or
imply any adapter exit `0` is audit approval.

A documented repository-wide CI coverage limitation must not lower testing
confidence when the exact audited commit passed the applicable final ship gate,
the working tree stayed clean, no commit followed, all change-relevant high-risk
checks were directly executed, and planned versus executed evidence reconciles.
Report the limitation under CI Enforcement Confidence and its effect under Merge
Eligibility.


If issue-required tracking blocks, state explicitly:

- the final exact-HEAD repository gate passed before remote tracking began;
- whether the branch was pushed;
- no PR was created or updated after tracking failed;
- no merge was attempted;
- every issue-required finding still lacking an equivalent open issue;
- GitHub search or creation failure evidence without exposing credentials;
- that non-`FIX_NOW` findings remained unchanged.

## Adapter-present example

```text
Deterministic Preflight:
- Adapter: ./scripts/verify
- Validation mode: Repository Verification V1
- Doctor command: ./scripts/verify doctor
- Doctor result: exit 0
- Fast command: ./scripts/verify fast --base origin/main
- Fast result: exit 0
- Preflight status: PASS

Baseline Restoration:
- Candidate: YES / NO
- Canonical base directly reproduced: YES / NO / NOT_APPLICABLE
- Canonical base commit:
- Authoritative lane/profile:
- Base command:
- Base result:
- Branch command:
- Branch result:
- Comparison environment/profile:
- Comparison reruns: <count and reason> / NONE
- Target failure repaired: YES / NO / NOT_APPLICABLE
- Failure ledger complete: YES / NO / NOT_APPLICABLE
- Ledger:
  | Failure identity | Base result | Branch result | Owner | Disposition |
  |------------------|-------------|---------------|-------|-------------|
  | ... | ... | ... | ... | FIXED_BY_BRANCH / UNCHANGED_TRACKED_BASELINE / PRE_EXISTING_NEWLY_UNMASKED / NEW_REGRESSION / UNATTRIBUTED |
- New regressions: NONE / <rows>
- Unattributed failures: NONE / <rows>
- Protected-domain residuals: NONE / <rows>
- Residual canonical issues: <links> / NOT_APPLICABLE
- Eligibility: ELIGIBLE / BLOCKED / NOT_APPLICABLE
- Blockers: <details> / NONE

Parallel Audit Execution:
- Requested mode: AUTO
- Actual mode: PARALLEL
- Lane count: 3
- Immutable packet HEAD/base/scope: <sha> / origin/main / <range>
- Lanes: correctness-behavior PASS; security-data-boundaries PASS; architecture-evidence-operations PASS
- Read-only integrity preserved: YES

Final Repository Verification:
- Adapter: ./scripts/verify
- Profile: ship
- Base: origin/main
- Final committed HEAD: <sha>
- Command: ./scripts/verify ship --base origin/main
- Result: exit 0
- Planned/executed: 19/19
- Working tree clean after final gate: YES
- HEAD unchanged through final gate: YES
- Status: PASS
```

## Adapter-absent example

```text
Deterministic Preflight:
- Adapter: not present
- Validation mode: legacy audit workflow
- Doctor result: NOT_APPLICABLE
- Fast result: NOT_APPLICABLE
- Preflight status: NOT_APPLICABLE

Final Repository Verification:
- Adapter: not present
- Profile: NOT_APPLICABLE
- Validation mode: legacy audit workflow
- Final result: legacy validation passed
- Status: NOT_APPLICABLE
```

## Environment-blocker example

```text
Deterministic Preflight:
- Adapter: ./scripts/verify
- Doctor result: exit 4
- Preflight status: BLOCKED_ENVIRONMENT
- Missing requirements: <names only>
```

If preflight blocks, state explicitly:

- the deep independent audit did not begin;
- nothing was modified, committed, pushed, tracked, or merged by this workflow;
- the base, exact command, exit mapping, duration, and diagnostic output;
- legacy fallback was not used for a present adapter.

If audit eligibility was blocked, state explicitly:

- nothing was committed by this workflow;
- nothing was pushed;
- no tracking issues were filed;
- no PR was opened or updated;
- which retained local fixes remain.

If final exact-HEAD verification failed, state explicitly:

- the local commit and exact SHA were retained;
- nothing was pushed after the failed gate;
- no tracking issues were filed after the failed gate;
- no PR was opened or updated after the failed gate;
- the exact base, command, exit mapping, contradiction, timeout/interruption, or
  tree-change evidence.

If a PR is open but unmerged, state exactly why automatic merge was not
permitted.

If merge succeeded but cleanup was incomplete, do not call the workflow clean.
Name every branch or working-tree condition left behind.

## Baseline-restoration example

```text
Operating Mode:
- Mode: BASELINE_RESTORATION
- Source: EXPLICIT
- Target already-red lane: dashboard ship lane
- Target failure: dashboard test A

Baseline Restoration:
- Candidate: YES
- Canonical base directly reproduced: YES
- Canonical base commit: <base-sha>
- Base command: ./scripts/verify ship --base origin/staging
- Base result: exit 1 — A, B, C
- Branch command: ./scripts/verify ship --base origin/staging
- Branch result: exit 1 — B, C
- Target failure repaired: YES
- Failure ledger complete: YES
- Ledger:
  | Failure identity | Base result | Branch result | Owner | Disposition |
  | dashboard test A | FAIL | PASS | #435 | FIXED_BY_BRANCH |
  | dashboard test B | FAIL | FAIL | #436 | UNCHANGED_TRACKED_BASELINE |
  | dashboard test C | FAIL | FAIL | #438 | UNCHANGED_TRACKED_BASELINE |
- New regressions: NONE
- Unattributed failures: NONE
- Eligibility: ELIGIBLE

Final Repository Verification:
- Result: exit 1
- Aggregate gate status: FAILED_PRE_EXISTING_BASELINE
- Status: FAILED_PRE_EXISTING_BASELINE

Merge Eligibility:
- Classification: MANUAL_MERGE_REQUIRED
- Baseline-restoration auto-merge prohibited: YES

Outcome:
- PR OPEN — BASELINE RESTORATION, MANUAL MERGE REQUIRED
```
