# Evidence, confidence, and severity

## Evidence levels

- E0 — speculation only. Never actionable.
- E1 — direct code/config evidence indicating a plausible defect.
- E2 — corroborated evidence across multiple code paths, contracts, static analysis, or repository history.
- E3 — executable reproduction, failing test, trace, or deterministic proof.

Default actionable threshold is E2/E3. E1 may surface only when potential impact is severe and must be labeled `URGENT INVESTIGATION REQUIRED`.

## Confidence

Confidence estimates whether the claim is true. Keep it separate from impact.

- High: >= 0.85
- Medium: 0.60–0.84
- Low: < 0.60

## Severity

- P0 — active catastrophic compromise/data loss/outage requiring immediate action.
- P1 — serious security/correctness/data-integrity/reliability defect with credible high impact.
- P2 — meaningful product/architecture/reliability/performance defect worth scheduling promptly.
- P3 — worthwhile improvement with concrete benefit and bounded impact.
- P4 — observation/taste/polish. Do not surface as an actionable overnight finding.

Architecture preference alone is not a finding. Demonstrate current cost, risk, defect history, product limitation, or operational burden.
