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

Evidence Ledger:
- <category>
  - Command/procedure:
  - Result:
  - Code state:
  - Covers:
  - Source:
  - Status: VERIFIED REUSABLE / VERIFIED BUT STALE / CLAIM ONLY / FAILED / NOT APPLICABLE / REQUIRED BUT UNAVAILABLE
  - Reason:

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

CI Enforcement:
- Required: YES / NO
- Currently enforced: YES / NO / UNKNOWN / NOT CONFIGURED — ACCEPTED REPOSITORY STATE
- Required command:
- Existing workflow/job:
- Gap: <omit when the repository has no CI as an accepted state>
- Automatic wiring eligibility: ELIGIBLE / NOT ELIGIBLE / NOT APPLICABLE
- Reason:
- Branch-protection review required: YES / NO

Stop Conditions Triggered:
- <condition, or NONE>

Confidence:
HIGH / MODERATE / LOW

Confidence Reason:
<why this level is justified>
```

Do not hide failed, stale, unavailable, or claim-only evidence.

Do not convert a required-but-unavailable critical check into a deliberate omission.
