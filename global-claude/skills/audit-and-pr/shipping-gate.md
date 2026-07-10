# Shipment Gate

Evaluate the final audit after retained remediation.

## Block shipment when

- verdict is FAIL
- result is AUDIT BLOCKED
- any P0 remains
- any P1 remains
- testing confidence is Low
- a testing stop condition remains
- CI enforcement is required and critical enforcement is absent (a
  repository with no CI as an accepted state does not trigger this)
- objective is unsatisfied
- unexplained validation failure remains

When blocked:

- leave retained safe fixes uncommitted
- do not create a shipping branch
- do not commit
- do not push
- do not file issues
- do not open or update a PR
- report blockers and retained local changes
- include the smallest safe follow-up prompt

## Clear shipment when

- verdict is PASS or PASS WITH GAPS
- no P0/P1 remains
- confidence is High or Moderate
- no required stop condition remains
- critical CI enforcement is present where CI is required, the repository
  has no CI as an accepted state, or the gap is explicitly non-critical and
  reflected in PASS WITH GAPS

Clearing shipment permits PR preparation.

It does not automatically permit merge.
