# Audit Report Format

Return:

```text
IMPLEMENTATION AUDIT RESULT

Mode:
STANDALONE / PARENT / PARENT-LANE

Verdict:
PASS / PASS WITH GAPS / FAIL

Original Objective:
<one paragraph>

Audited Scope:
- Repository:
- Branch:
- Commit:
- Diff/range:
- Working tree:

Implemented Changes:
- <behavioral change>

Requirement Coverage:
- <requirement>: PASS / GAP / FAIL
  - Evidence:
  - Notes:

Implementation Findings:
P0:
- <finding>

P1:
- <finding>

P2:
- <finding>

P3:
- <finding>

Audit Process Notes:
- <note>

Testing Assessment:
- Risk level: LOW / MEDIUM / HIGH
- Requested behavior: COVERED / GAP / NOT APPLICABLE
- Happy path: COVERED / GAP / NOT APPLICABLE
- Primary failure path: COVERED / GAP / NOT APPLICABLE
- Regression surface: COVERED / GAP / NOT APPLICABLE
- Security/boundary behavior: COVERED / GAP / NOT APPLICABLE
- Repository quality gates: COVERED / GAP / NOT APPLICABLE
- Evidence plan:
  - <required check and purpose>
- Evidence reused:
  - <command/procedure and result>
- Evidence rerun:
  - <command/procedure, result, and reason>
- New validation executed:
  - <command/procedure, result, and gap closed>
- Planned versus executed reconciliation:
  - <planned check>: PASS / FAIL / UNAVAILABLE / NOT RUN / NOT APPLICABLE
- Deliberately omitted:
  - <test/category and reason>
- Unable to validate:
  - <required validation and reason>

Testing Confidence:
- Level: HIGH / MODERATE / LOW
- Reason:
- Exact audited code state:
- Material testing limitations: <details or NONE>

CI Enforcement Confidence:
- Level: HIGH / MODERATE / LOW / NOT_APPLICABLE
- CI state: GREEN / RED / UNRESOLVED / NOT CONFIGURED — ACCEPTED REPOSITORY STATE / NOT YET OBSERVED
- Required enforcement:
- Currently enforced:
- Documented repository-wide limitation: <details or NONE>
- New change-specific enforcement gap: <details or NONE>
- Automatic wiring eligibility:
- Branch-protection review required:
- Reason:

Merge Eligibility:
- Classification: AUTO_MERGE_ELIGIBLE / MANUAL_MERGE_REQUIRED / BLOCKED / PENDING_PR_AND_CI
- Repository-policy reason:
- This classification does not alter the independent audit verdict or testing confidence.

Risk Assessment:
LOW / MEDIUM / HIGH
<reason>

Recommended Action:
MERGE / FIX FIRST / SPLIT FOLLOW-UP / REVERT / MANUAL REVIEW

Smallest Safe Follow-up Prompt:
<include only when fixes or additional work are required>
```

Rules:

- Omit empty P0, P1, P2, or P3 subsections.
- Write `NONE` for no audit-process notes.
- Do not hide failed or unavailable validation.
- Do not downgrade a testing stop condition.
- Never use a CI architecture limitation as the reason for lowering testing
  confidence when exact-HEAD ship evidence and all change-relevant high-risk
  checks satisfy the evidence contract.
- Report CI enforcement confidence and merge eligibility separately.
- Do not include unrelated recommendations.
- The follow-up prompt addresses only identified blockers or gaps.
