# Final Report Format

Return:

```text
AUDIT AND PR RESULT

Audit Model:
<model>

Objective:
<one sentence>

Audited Scope:
- Repository:
- Branch:
- Diff/range:

Final Audit:
- Verdict:
- Risk:
- Testing confidence:
- P0 remaining:
- P1 remaining:
- P2 remaining:
- P3 remaining:

Auto-fixes:
- <retained fix and validation>
- NONE

Testing:
- Reused:
- Rerun:
- Newly executed:
- Deliberately omitted:
- Unable to validate:
- CI enforcement:
- Confidence reason:

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

Outcome:
- MERGED AND CLEANED UP
- PR OPEN — MANUAL REVIEW REQUIRED
- PR OPEN — CI FAILED
- PR OPEN — CI UNRESOLVED
- SHIPMENT BLOCKED
- AUDIT BLOCKED

Blocking Reason:
<include when not merged>

Smallest Safe Follow-up Prompt:
<include when additional work is required>
```

If shipment was blocked, state explicitly:

- nothing was committed by this workflow
- nothing was pushed
- no tracking issues were filed
- no PR was opened or updated
- which retained local fixes remain

If a PR is open but unmerged, state exactly why automatic merge was not permitted.
