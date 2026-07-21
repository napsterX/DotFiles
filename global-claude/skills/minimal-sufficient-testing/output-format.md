# Required Output

Return this structure:

```text
MINIMAL SUFFICIENT TESTING RESULT

Mode:
PLAN / VALIDATE / IMPLEMENTATION

Risk Level:
LOW / MEDIUM / HIGH

Risk Reason:
<plain engineering explanation>

Code State:
- Repository:
- Branch:
- Commit:
- Working tree:
- Audited diff/range:

Evidence Plan:
- <check>
  - Purpose:
  - Required: YES / NO
  - Command/procedure:
  - Expected result:
  - Code-state binding:

Evidence Ledger:
- <category>
  - Command/procedure:
  - Result:
  - Code state:
  - Covers:
  - Source:
  - Status: VERIFIED REUSABLE / VERIFIED BUT STALE / CLAIM ONLY / FAILED / NOT APPLICABLE / REQUIRED BUT UNAVAILABLE
  - Reason:

Planned Versus Executed:
- <planned check>: PASS / FAIL / UNAVAILABLE / NOT RUN / NOT APPLICABLE
  - Evidence:
  - Notes:

Coverage Assessment:
- Requested behavior: COVERED / GAP / NOT APPLICABLE
- Happy path: COVERED / GAP / NOT APPLICABLE
- Primary failure path: COVERED / GAP / NOT APPLICABLE
- Regression surface: COVERED / GAP / NOT APPLICABLE
- Security/boundary behavior: COVERED / GAP / NOT APPLICABLE
- Repository quality gates: COVERED / GAP / NOT APPLICABLE

Tests Required:
- <test or validation>
  - Test type:
  - What it protects:
  - Why it is necessary:
  - Suggested location:
  - Positive case:
  - Negative/failure case:
  - Action: REUSE / RERUN / ADD / EXECUTE

Tests Not Required:
- <category or test>: <reason>

Commands Executed:
- <command>: PASS / FAIL / NOT EXECUTED

Commands Still Required:
- <command or procedure>

Manual Verification:
- <procedure, or NOT REQUIRED>

Testing Confidence:
- Level: HIGH / MODERATE / LOW
- Reason:
- Exact audited code state:
- Material testing limitations: <details or NONE>

CI Enforcement Confidence:
- Level: HIGH / MODERATE / LOW / NOT_APPLICABLE
- CI state: GREEN / RED / UNRESOLVED / NOT CONFIGURED — ACCEPTED REPOSITORY STATE / NOT YET OBSERVED
- Required: YES / NO
- Currently enforced: YES / NO / UNKNOWN / NOT CONFIGURED — ACCEPTED REPOSITORY STATE
- Required command:
- Existing workflow/job:
- Documented repository-wide limitation: <details or NONE>
- Change-specific gap: <details or NONE>
- Automatic wiring eligibility: ELIGIBLE / NOT ELIGIBLE / NOT APPLICABLE
- Branch-protection review required: YES / NO
- Reason:

Provisional Merge Impact:
AUTO_MERGE_ELIGIBLE / MANUAL_MERGE_REQUIRED / BLOCKED / PENDING_PR_AND_CI

Merge Impact Reason:
<repository-policy-aware reason; do not rewrite testing confidence>

Stop Conditions Triggered:
- <condition, or NONE>
```

Do not hide failed, stale, unavailable, claim-only, or not-run evidence.

Do not convert a required-but-unavailable critical check into a deliberate
omission.

Never lower testing confidence solely because CI does not enforce a check that
was directly executed successfully for the exact audited commit under a
documented accepted repository-wide CI architecture limitation. Report that
limitation under CI Enforcement Confidence and Provisional Merge Impact.
