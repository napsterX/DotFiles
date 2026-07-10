# Audit Report Format

Return:

```text
IMPLEMENTATION AUDIT RESULT

Mode:
STANDALONE / PARENT

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
- Evidence reused:
  - <command/procedure and result>
- Evidence rerun:
  - <command/procedure, result, and reason>
- New validation executed:
  - <command/procedure, result, and gap closed>
- Deliberately omitted:
  - <test/category and reason>
- Unable to validate:
  - <required validation and reason>
- CI enforcement:
  - Required:
  - Currently enforced: <or `NOT CONFIGURED — ACCEPTED REPOSITORY STATE` when the repository has no CI by design>
  - Gap: <omit when accepted-no-CI>
  - Automatic wiring eligibility:
  - Branch-protection review required:
- Confidence: HIGH / MODERATE / LOW
- Confidence reason:

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
- Do not include unrelated recommendations.
- The follow-up prompt addresses only identified blockers or gaps.
