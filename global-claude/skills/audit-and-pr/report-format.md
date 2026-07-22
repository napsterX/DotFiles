# Final Report Format

Return:

```text
AUDIT AND PR RESULT

Audit Model:
<model and effort>

Objective:
<one sentence>

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
- Verdict:
- Risk:
- P0 remaining:
- P1 remaining:
- P2 deferred — code unchanged:
- P3 deferred — code unchanged:
- Objective-required finding incorrectly classified as P2/P3: YES / NO
- Why deterministic verification was or was not sufficient evidence:

Finding Disposition:
- P0/P1 remediation candidates:
- P0/P1 blockers not safely remediable:
- Confirmed P2/P3 excluded from remediation:
- Audit-process notes excluded from ticketing:
- Severity downgrades used to avoid remediation: NONE / <blocker>

Remediation:
- Eligible priorities: P0 / P1 only
- Rounds used:
- Single writer: YES / NO
- Retained P0/P1 fixes:
  - <finding, original priority, change, targeted validation, optional fast rerun, re-audit>
- Deferred P2/P3 code modifications: NONE / <blocker>
- Reverted attempts:
- Post-remediation fast runs: <HEAD, command, result, reason> / NONE

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
- Status: PASS / NOT_APPLICABLE / BLOCKED_REQUIRED_CHECK / BLOCKED_INVOCATION / BLOCKED_ADAPTER / BLOCKED_CONFIGURATION / BLOCKED_ENVIRONMENT / BLOCKED_TIMEOUT / BLOCKED_INTERRUPTED / BLOCKED_PROTOCOL / BLOCKED_BASE_RESOLUTION
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
- Repository-policy reason:
- Live gate reason:

Testing:
- Reused:
- Rerun:
- Newly executed:
- Deliberately omitted:
- Unable to validate:

Deferred Finding Tracking:
- Status: COMPLETE / NOT_APPLICABLE / TRACKING BLOCKED
- Confirmed P2/P3 findings:
- Findings mapped to equivalent open issues:
- Reused open issues:
- Newly created issues:
- Grouped P3 mappings:
- Findings:
  - <finding ID, priority, code unchanged, issue URL, reused/new>
- Untracked findings: NONE / <finding and reason>
- GitHub unavailable or issue creation failure: NONE / <reason>

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

Cleanup:
- Default branch updated:
- Local feature branch:
- Remote feature branch:
- Final working tree:

Outcome:
- MERGED AND CLEANED UP
- MERGED — CLEANUP INCOMPLETE
- PR OPEN — MANUAL REVIEW REQUIRED
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

Keep deterministic preflight, parallel audit execution, evidence
reconciliation, finding disposition, deferred-finding tracking, final Repository
Verification, independent audit, testing confidence, CI enforcement confidence,
CI result, PR state, merge eligibility, and merge result separate. Never collapse the result into “tests passed” or
imply any adapter exit `0` is audit approval.

A documented repository-wide CI coverage limitation must not lower testing
confidence when the exact audited commit passed the applicable final ship gate,
the working tree stayed clean, no commit followed, all change-relevant high-risk
checks were directly executed, and planned versus executed evidence reconciles.
Report the limitation under CI Enforcement Confidence and its effect under Merge
Eligibility.


If deferred-finding tracking blocks, state explicitly:

- the final exact-HEAD repository gate passed before remote tracking began;
- whether the branch was pushed;
- no PR was created or updated after tracking failed;
- no merge was attempted;
- every confirmed P2/P3 still lacking an equivalent open issue;
- GitHub search or creation failure evidence without exposing credentials;
- that P2/P3 code remained unchanged.

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
