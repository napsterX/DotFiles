#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "shipping_decision.py"
spec = importlib.util.spec_from_file_location("shipping_decision", HELPER)
assert spec and spec.loader
sd = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = sd
spec.loader.exec_module(sd)


class ShippingDecisionTests(unittest.TestCase):
    def assess(self, **kwargs):
        return sd.assess_decisions(sd.DecisionInputs(**kwargs))

    def test_documented_ci_architecture_gap_does_not_lower_testing_confidence(self):
        result = self.assess(
            required_checks_enforced_in_ci=False,
            accepted_repository_wide_ci_limitation=True,
            ci_limitation_documented=True,
            repository_policy_requires_manual_merge_for_ci_gap=True,
        )
        self.assertEqual("HIGH", result.testing_confidence)
        self.assertEqual("MODERATE", result.ci_enforcement_confidence)
        self.assertEqual("MANUAL_MERGE_REQUIRED", result.merge_eligibility)

    def test_unaccepted_ci_gap_is_separate_from_testing_confidence(self):
        result = self.assess(required_checks_enforced_in_ci=False)
        self.assertEqual("HIGH", result.testing_confidence)
        self.assertEqual("LOW", result.ci_enforcement_confidence)
        self.assertEqual("BLOCKED", result.merge_eligibility)

    def test_no_ci_accepted_state_can_auto_merge(self):
        result = self.assess(
            ci_configured=False,
            ci_explicitly_required=False,
            required_checks_enforced_in_ci=False,
            ci_result="NOT_CONFIGURED",
        )
        self.assertEqual("HIGH", result.testing_confidence)
        self.assertEqual("NOT_APPLICABLE", result.ci_enforcement_confidence)
        self.assertEqual("AUTO_MERGE_ELIGIBLE", result.merge_eligibility)

    def test_ship_result_must_match_exact_audited_head(self):
        result = self.assess(repository_gate_bound_to_audited_head=False)
        self.assertEqual("LOW", result.testing_confidence)
        self.assertEqual("BLOCKED", result.merge_eligibility)

    def test_commit_after_ship_invalidates_testing_evidence(self):
        result = self.assess(commit_added_after_gate=True)
        self.assertEqual("LOW", result.testing_confidence)
        self.assertEqual("BLOCKED", result.merge_eligibility)

    def test_missing_change_relevant_high_risk_check_lowers_testing_confidence(self):
        result = self.assess(change_relevant_high_risk_checks_executed=False)
        self.assertEqual("LOW", result.testing_confidence)
        self.assertEqual("BLOCKED", result.merge_eligibility)

    def test_plan_execution_reconciliation_is_required(self):
        result = self.assess(evidence_plan_reconciled=False)
        self.assertEqual("LOW", result.testing_confidence)
        self.assertIn("reconciled", " ".join(result.testing_reasons))

    def test_ci_failure_blocks_merge_without_rewriting_testing_confidence(self):
        result = self.assess(ci_result="RED")
        self.assertEqual("HIGH", result.testing_confidence)
        self.assertEqual("BLOCKED", result.merge_eligibility)

    def test_noncritical_testing_limitation_requires_manual_merge(self):
        result = self.assess(noncritical_test_limitation=True)
        self.assertEqual("MODERATE", result.testing_confidence)
        self.assertEqual("MANUAL_MERGE_REQUIRED", result.merge_eligibility)

    def test_explicit_repository_policy_can_allow_auto_merge_with_accepted_gap(self):
        result = self.assess(
            required_checks_enforced_in_ci=False,
            accepted_repository_wide_ci_limitation=True,
            ci_limitation_documented=True,
            repository_policy_explicitly_allows_auto_merge_with_ci_gap=True,
        )
        self.assertEqual("HIGH", result.testing_confidence)
        self.assertEqual("MODERATE", result.ci_enforcement_confidence)
        self.assertEqual("AUTO_MERGE_ELIGIBLE", result.merge_eligibility)

    def test_final_verification_and_audit_remain_independent_blockers(self):
        result = self.assess(audit_eligible=False, final_verification_passed=False)
        self.assertEqual("HIGH", result.testing_confidence)
        self.assertEqual("BLOCKED", result.merge_eligibility)
        joined = " ".join(result.merge_reasons)
        self.assertIn("independent audit", joined)
        self.assertIn("final exact-HEAD", joined)

    def test_missing_deferred_finding_tracking_blocks_merge(self):
        result = self.assess(deferred_findings_tracking_complete=False)
        self.assertEqual("HIGH", result.testing_confidence)
        self.assertEqual("BLOCKED", result.merge_eligibility)
        self.assertIn("P2/P3", " ".join(result.merge_reasons))

    def test_legacy_mode_does_not_require_repository_adapter(self):
        result = self.assess(repository_gate_applicable=False)
        self.assertEqual("HIGH", result.testing_confidence)
        self.assertEqual("AUTO_MERGE_ELIGIBLE", result.merge_eligibility)


if __name__ == "__main__":
    unittest.main(verbosity=1)
