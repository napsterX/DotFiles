#!/usr/bin/env python3
"""Pure decision logic for audit evidence, CI enforcement, and merge eligibility.

The skill documentation remains authoritative. This helper exists so the three
independent decisions can be exercised with executable tests instead of being
only prose.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import argparse
import json
from typing import Literal

TestingConfidence = Literal["HIGH", "MODERATE", "LOW"]
CIEnforcementConfidence = Literal["HIGH", "MODERATE", "LOW", "NOT_APPLICABLE"]
MergeEligibility = Literal[
    "AUTO_MERGE_ELIGIBLE", "MANUAL_MERGE_REQUIRED", "BLOCKED"
]


@dataclass(frozen=True)
class DecisionInputs:
    # Testing evidence and exact-code-state binding.
    evidence_plan_reconciled: bool = True
    change_relevant_high_risk_checks_executed: bool = True
    required_test_failure: bool = False
    material_test_gap: bool = False
    noncritical_test_limitation: bool = False
    repository_gate_applicable: bool = True
    repository_gate_passed: bool = True
    repository_gate_bound_to_audited_head: bool = True
    working_tree_clean_after_gate: bool = True
    commit_added_after_gate: bool = False

    # CI architecture and enforcement.
    ci_configured: bool = True
    ci_explicitly_required: bool = False
    required_checks_enforced_in_ci: bool = True
    accepted_repository_wide_ci_limitation: bool = False
    ci_limitation_documented: bool = False

    # Final shipment and merge gates.
    audit_eligible: bool = True
    final_verification_passed: bool = True
    ci_result: Literal["GREEN", "RED", "UNRESOLVED", "NOT_CONFIGURED"] = "GREEN"
    required_reviews_satisfied: bool = True
    protection_allows_merge: bool = True
    no_unaudited_commits: bool = True
    repository_policy_requires_manual_merge_for_ci_gap: bool = False
    repository_policy_explicitly_allows_auto_merge_with_ci_gap: bool = False


@dataclass(frozen=True)
class DecisionResult:
    testing_confidence: TestingConfidence
    ci_enforcement_confidence: CIEnforcementConfidence
    merge_eligibility: MergeEligibility
    testing_reasons: list[str] = field(default_factory=list)
    ci_enforcement_reasons: list[str] = field(default_factory=list)
    merge_reasons: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def assess_decisions(inputs: DecisionInputs) -> DecisionResult:
    testing_reasons: list[str] = []

    if inputs.required_test_failure:
        testing_reasons.append("a required test or validation failed")
    if inputs.material_test_gap:
        testing_reasons.append("a material change-relevant test obligation is uncovered")
    if not inputs.evidence_plan_reconciled:
        testing_reasons.append("planned and executed evidence was not reconciled")
    if not inputs.change_relevant_high_risk_checks_executed:
        testing_reasons.append("change-relevant high-risk checks were not directly executed")
    if inputs.repository_gate_applicable:
        if not inputs.repository_gate_passed:
            testing_reasons.append("the repository ship gate did not pass")
        if not inputs.repository_gate_bound_to_audited_head:
            testing_reasons.append("the ship result is not bound to the audited HEAD")
        if not inputs.working_tree_clean_after_gate:
            testing_reasons.append("the working tree was not clean after the ship gate")
        if inputs.commit_added_after_gate:
            testing_reasons.append("a commit was added after the ship result")

    if testing_reasons:
        testing_confidence: TestingConfidence = "LOW"
    elif inputs.noncritical_test_limitation:
        testing_confidence = "MODERATE"
        testing_reasons.append("a named non-critical testing limitation remains")
    else:
        testing_confidence = "HIGH"
        testing_reasons.append("all change-relevant evidence obligations passed for the audited code state")

    ci_reasons: list[str] = []
    ci_required_or_configured = inputs.ci_configured or inputs.ci_explicitly_required
    if not ci_required_or_configured:
        ci_confidence: CIEnforcementConfidence = "NOT_APPLICABLE"
        ci_reasons.append("CI is not configured and is an accepted repository state")
    elif inputs.required_checks_enforced_in_ci:
        ci_confidence = "HIGH"
        ci_reasons.append("all required permanent checks are enforced in CI")
    elif (
        inputs.accepted_repository_wide_ci_limitation
        and inputs.ci_limitation_documented
    ):
        ci_confidence = "MODERATE"
        ci_reasons.append("a documented repository-wide CI coverage limitation leaves required checks local-only")
    else:
        ci_confidence = "LOW"
        ci_reasons.append("required CI enforcement is missing, unknown, or not an accepted documented limitation")

    merge_reasons: list[str] = []
    hard_blockers = []
    if not inputs.audit_eligible:
        hard_blockers.append("independent audit is not eligible for shipment")
    if not inputs.final_verification_passed:
        hard_blockers.append("final exact-HEAD verification did not pass")
    if inputs.ci_result in {"RED", "UNRESOLVED"}:
        hard_blockers.append(f"CI is {inputs.ci_result}")
    if inputs.ci_result == "NOT_CONFIGURED" and ci_required_or_configured:
        hard_blockers.append("CI is required or configured but no valid result is available")
    if not inputs.required_reviews_satisfied:
        hard_blockers.append("required review is missing")
    if not inputs.protection_allows_merge:
        hard_blockers.append("repository protection does not permit merge")
    if not inputs.no_unaudited_commits:
        hard_blockers.append("an unaudited commit is present")
    if testing_confidence == "LOW":
        hard_blockers.append("testing confidence is LOW")
    if ci_confidence == "LOW":
        hard_blockers.append("CI enforcement confidence is LOW")

    if hard_blockers:
        merge_eligibility: MergeEligibility = "BLOCKED"
        merge_reasons.extend(hard_blockers)
    elif testing_confidence == "MODERATE":
        merge_eligibility = "MANUAL_MERGE_REQUIRED"
        merge_reasons.append("testing confidence is MODERATE")
    elif ci_confidence == "MODERATE":
        if inputs.repository_policy_explicitly_allows_auto_merge_with_ci_gap:
            merge_eligibility = "AUTO_MERGE_ELIGIBLE"
            merge_reasons.append("repository policy explicitly permits automatic merge with the accepted CI coverage limitation")
        else:
            merge_eligibility = "MANUAL_MERGE_REQUIRED"
            if inputs.repository_policy_requires_manual_merge_for_ci_gap:
                merge_reasons.append("repository policy requires manual merge for the accepted CI coverage limitation")
            else:
                merge_reasons.append("no repository policy explicitly permits automatic merge with the accepted CI coverage limitation")
    else:
        merge_eligibility = "AUTO_MERGE_ELIGIBLE"
        merge_reasons.append("testing, CI, audit, verification, review, and protection gates permit automatic merge")

    return DecisionResult(
        testing_confidence=testing_confidence,
        ci_enforcement_confidence=ci_confidence,
        merge_eligibility=merge_eligibility,
        testing_reasons=testing_reasons,
        ci_enforcement_reasons=ci_reasons,
        merge_reasons=merge_reasons,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        required=True,
        help="JSON object containing DecisionInputs fields",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    raw = json.loads(args.json)
    result = assess_decisions(DecisionInputs(**raw))
    print(result.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
