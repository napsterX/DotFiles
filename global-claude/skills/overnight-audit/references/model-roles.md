# Model roles

The controller uses capability roles rather than hard-coded vendors/models.

## PRIMARY_INVESTIGATOR

Responsibilities:
- repository/subsystem comprehension
- hypothesis generation
- evidence interpretation
- cross-file and architectural reasoning
- candidate-finding formulation

Must be willing to reject its own hypothesis.

## CHALLENGER

Receives the hypothesis, evidence packet, proposed finding, and relevant repository facts but not hidden reasoning. Its objective is to falsify the candidate finding by identifying:
- overlooked guards/invariants
- impossible execution paths
- incorrect assumptions
- tests/contracts that disprove the claim
- overstated impact/severity
- duplicate/known issue status

Return CONFIRM, REJECT, or INCONCLUSIVE with concrete reasons.

## OPTIONAL_ESCALATION_MODEL

Not enabled in v0.1. Reserved for high-impact disagreements that cannot be resolved deterministically.
