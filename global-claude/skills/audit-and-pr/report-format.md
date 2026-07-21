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
- Verification-governance-sensitive: YES / NO

Repository Verification:
- Adapter: ./scripts/verify / not present / invalid
- Profile: ship / NOT_APPLICABLE
- Validation mode: Repository Verification V1 / legacy audit workflow
- Base: <resolved-base>
- Initial HEAD: <sha>
- Initial command: <exact command>
- Initial result: exit <code> / NOT_APPLICABLE
- Initial duration:
- Initial planned/executed: <n>/<n> / not reported
- Initial pass/failure/unavailable/advisory: <counts or not reported>
- Post-remediation runs: <HEAD, command, result, duration, counts for each> / NONE
- Final HEAD: <sha>
- Final command: <exact command>
- Final result: exit <code> / legacy result / NOT RUN
- Status: PASS / NOT_APPLICABLE / BLOCKED_REQUIRED_CHECK / BLOCKED_INVOCATION / BLOCKED_ADAPTER / BLOCKED_CONFIGURATION / BLOCKED_ENVIRONMENT / BLOCKED_TIMEOUT / BLOCKED_INTERRUPTED / BLOCKED_PROTOCOL / BLOCKED_BASE_RESOLUTION
- Contradictions: <details> / NONE
- Output evidence: <concise diagnostic summary; preserve complete captured output in the working record>

Evidence Contract:
- Planned checks:
  - <check, purpose, required/advisory>
- Planned versus executed:
  - <check>: PASS / FAIL / UNAVAILABLE / NOT RUN / NOT APPLICABLE
- Exact audited code state:
- Working tree clean after final gate: YES / NO
- Commit added after final gate: YES / NO
- Change-relevant high-risk checks directly executed: YES / NO / NOT APPLICABLE
- Reconciliation status: COMPLETE / INCOMPLETE / BLOCKED

Final Independent Audit:
- Verdict:
- Risk:
- P0 remaining:
- P1 remaining:
- P2 remaining:
- P3 remaining:
- Why Repository Verification was or was not sufficient evidence:

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

Auto-fixes:
- <retained fix and targeted validation, evidence reconciliation, verification rerun, re-audit>
- NONE

Testing:
- Reused:
- Rerun:
- Newly executed:
- Deliberately omitted:
- Unable to validate:

Tracking:
- <finding and issue>
- <finding retained in PR only>
- Unavailable: <reason>

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
- REPOSITORY VERIFICATION BLOCKED
- FINAL VERIFICATION FAILED — LOCAL COMMIT RETAINED
- SHIPMENT BLOCKED
- AUDIT BLOCKED

Blocking Reason:
<include when not merged and cleaned up>

Smallest Safe Follow-up Prompt:
<include when additional work is required>
```

Keep Repository Verification, evidence reconciliation, independent audit,
testing confidence, CI enforcement confidence, CI result, PR state, merge
eligibility, and merge result separate. Never collapse the result into “tests
passed” or imply exit `0` is audit approval.

A documented repository-wide CI coverage limitation must not lower testing
confidence when the exact audited commit passed the applicable ship gate, the
working tree stayed clean, no commit followed, all change-relevant high-risk
checks were directly executed, and planned versus executed evidence reconciles.
Report the limitation under CI Enforcement Confidence and its effect under Merge
Eligibility.

## Adapter-present example

```text
Repository Verification:
- Adapter: ./scripts/verify
- Profile: ship
- Validation mode: Repository Verification V1
- Base: origin/main
- Initial HEAD: <sha>
- Initial command: ./scripts/verify ship --base origin/main
- Initial result: exit 0
- Initial planned/executed: 19/19
- Post-remediation runs: <sha> — exit 0
- Final HEAD: <sha>
- Final result: exit 0
- Status: PASS

Testing Confidence:
- Level: HIGH
- Reason: all change-relevant high-risk checks passed for the exact audited commit

CI Enforcement Confidence:
- Level: MODERATE
- Documented repository-wide limitation: Docker-backed integration suite is local-only

Merge Eligibility:
- Classification: MANUAL_MERGE_REQUIRED
- Repository-policy reason: manual merge required for the accepted CI coverage limitation
```

## Adapter-absent example

```text
Repository Verification:
- Adapter: not present
- Profile: NOT_APPLICABLE
- Validation mode: legacy audit workflow
- Base: origin/develop
- Initial result: NOT_APPLICABLE
- Final result: legacy validation passed
- Status: NOT_APPLICABLE
```

## Environment-blocker example

```text
Repository Verification:
- Adapter: ./scripts/verify
- Profile: ship
- Base: origin/main
- Initial result: exit 4
- Status: BLOCKED_ENVIRONMENT
- Missing requirements: <names only>
```

If initial Repository Verification blocks, state explicitly:

- independent audit did not begin;
- nothing was modified, committed, pushed, tracked, or merged by this workflow;
- the base, exact command, exit mapping, duration, and diagnostic output;
- legacy fallback was not used.

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
- the exact base, command, exit mapping, contradiction, timeout/interruption, or tree-change evidence.

If a PR is open but unmerged, state exactly why automatic merge was not
permitted.

If merge succeeded but cleanup was incomplete, do not call the full workflow
clean. Name every branch or working-tree condition left behind.
