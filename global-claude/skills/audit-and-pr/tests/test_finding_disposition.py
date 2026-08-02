#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "finding_disposition.py"
spec = importlib.util.spec_from_file_location("finding_disposition", HELPER)
assert spec and spec.loader
fd = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = fd
spec.loader.exec_module(fd)


class FindingDispositionTests(unittest.TestCase):
    def decide(self, **kwargs):
        defaults = {
            "rationale": "evidence-backed disposition",
        }
        defaults.update(kwargs)
        return fd.decide_finding(fd.FindingInputs(**defaults))

    def tracking(self, **kwargs):
        return fd.assess_issue_tracking(fd.IssueTrackingInputs(**kwargs))

    def post(self, **kwargs):
        return fd.assess_post_remediation(fd.PostRemediationInputs(**kwargs))

    def bounded_fix_fields(self):
        return {
            "remediation_authorized": True,
            "remediation_feasible": True,
            "directly_related": True,
            "self_contained": True,
            "clear_acceptance_criteria": True,
            "deterministic_verification": True,
            "low_regression_risk": True,
        }

    def issue_gate_fields(self):
        return {
            "issue_actionable": True,
            "issue_material_enough": True,
            "issue_appropriately_scoped": True,
            "issue_verifiable": True,
            "issue_likely_to_be_worked": True,
            "better_deferred_than_fixed_now": True,
        }

    def test_p0_authorized_fix_now_remains_acceptance_blocking_until_verified(self):
        result = self.decide(
            severity="P0",
            proposed_disposition="FIX_NOW",
            remediation_authorized=True,
            remediation_feasible=True,
        )
        self.assertEqual("ACCEPTED", result.decision_status)
        self.assertEqual("FIX_NOW", result.disposition)
        self.assertTrue(result.may_modify_code)
        self.assertTrue(result.acceptance_blocked_now)

    def test_unresolved_p0_or_p1_must_block_acceptance(self):
        for severity in ("P0", "P1"):
            with self.subTest(severity=severity):
                result = self.decide(
                    severity=severity,
                    proposed_disposition="BLOCK_ACCEPTANCE",
                )
                self.assertEqual("BLOCK_ACCEPTANCE", result.disposition)
                self.assertTrue(result.acceptance_blocked_now)
                self.assertFalse(result.issue_required)

    def test_p1_cannot_be_deferred_to_issue(self):
        result = self.decide(
            severity="P1",
            proposed_disposition="DEFER_TO_ISSUE",
            **self.issue_gate_fields(),
        )
        self.assertEqual("REJECTED", result.decision_status)
        self.assertEqual("BLOCK_ACCEPTANCE", result.disposition)

    def test_scenario_1_directly_related_bounded_p2_is_fixed_now(self):
        result = self.decide(
            severity="P2",
            proposed_disposition="FIX_NOW",
            introduced_or_exposed_by_change=True,
            missing_important_verification=True,
            **self.bounded_fix_fields(),
        )
        self.assertEqual("ACCEPTED", result.decision_status)
        self.assertEqual("FIX_NOW", result.disposition)
        self.assertFalse(result.issue_required)

    def test_p2_fix_now_rejected_when_it_requires_architecture(self):
        result = self.decide(
            severity="P2",
            proposed_disposition="FIX_NOW",
            introduced_or_exposed_by_change=True,
            requires_architecture=True,
            **self.bounded_fix_fields(),
        )
        self.assertEqual("REJECTED", result.decision_status)
        self.assertIn("architecture", " ".join(result.issue_gate_failures))

    def test_scenario_2_unrelated_architectural_p2_can_be_deferred(self):
        result = self.decide(
            severity="P2",
            proposed_disposition="DEFER_TO_ISSUE",
            requires_architecture=True,
            directly_related=False,
            **self.issue_gate_fields(),
        )
        self.assertEqual("DEFER_TO_ISSUE", result.disposition)
        self.assertEqual("CREATE_NEW", result.issue_action)

    def test_scenario_5_existing_open_issue_is_reused(self):
        result = self.decide(
            severity="P2",
            proposed_disposition="DEFER_TO_ISSUE",
            existing_issue_state="OPEN_EQUIVALENT",
            **self.issue_gate_fields(),
        )
        self.assertEqual("ADD_TO_EXISTING_ISSUE", result.disposition)
        self.assertEqual("REUSE_OPEN", result.issue_action)

    def test_closed_issue_is_context_not_active_tracking(self):
        result = self.decide(
            severity="P2",
            proposed_disposition="DEFER_TO_ISSUE",
            existing_issue_state="CLOSED_EQUIVALENT",
            **self.issue_gate_fields(),
        )
        self.assertEqual("CREATE_NEW", result.issue_action)

    def test_scenario_3_cosmetic_p3_can_be_accepted_as_low_value(self):
        result = self.decide(
            severity="P3",
            proposed_disposition="ACCEPT_AS_LOW_VALUE",
            issue_material_enough=False,
            issue_likely_to_be_worked=False,
            economically_useful=False,
        )
        self.assertEqual("ACCEPT_AS_LOW_VALUE", result.disposition)
        self.assertFalse(result.issue_required)

    def test_trivial_adjacent_behavior_preserving_p3_can_be_fixed_now(self):
        result = self.decide(
            severity="P3",
            proposed_disposition="FIX_NOW",
            trivial_adjacent=True,
            behavior_preserving=True,
            **self.bounded_fix_fields(),
        )
        self.assertEqual("FIX_NOW", result.disposition)
        self.assertTrue(result.may_modify_code)

    def test_scenario_4_repeated_findings_are_batched(self):
        result = self.decide(
            severity="P3",
            proposed_disposition="BATCH_INTO_CLEANUP_ISSUE",
            batchable=True,
            related_finding_count=8,
            **self.issue_gate_fields(),
        )
        self.assertEqual("BATCH_INTO_CLEANUP_ISSUE", result.disposition)
        self.assertEqual("CREATE_OR_REUSE_BATCH", result.issue_action)

    def test_repeated_findings_cannot_create_occurrence_level_issue(self):
        result = self.decide(
            severity="P3",
            proposed_disposition="DEFER_TO_ISSUE",
            batchable=True,
            related_finding_count=8,
            **self.issue_gate_fields(),
        )
        self.assertEqual("REJECTED", result.decision_status)

    def test_scenario_7_speculative_finding_is_dismissed(self):
        result = self.decide(
            severity="P3",
            proposed_disposition="DISMISS",
            speculative=True,
            unsupported_by_evidence=True,
        )
        self.assertEqual("DISMISS", result.disposition)
        self.assertFalse(result.issue_required)

    def test_duplicate_finding_is_dismissed_not_ticketed(self):
        result = self.decide(
            severity="P2",
            proposed_disposition="DISMISS",
            duplicate=True,
        )
        self.assertEqual("DISMISS", result.disposition)

    def test_issue_creation_gate_blocks_non_actionable_backlog(self):
        gate = self.issue_gate_fields()
        gate["issue_actionable"] = False
        result = self.decide(
            severity="P2",
            proposed_disposition="DEFER_TO_ISSUE",
            **gate,
        )
        self.assertEqual("REJECTED", result.decision_status)
        self.assertIn("actionable", " ".join(result.issue_gate_failures))

    def test_objective_required_p2_cannot_be_deferred(self):
        result = self.decide(
            severity="P2",
            proposed_disposition="DEFER_TO_ISSUE",
            objective_required=True,
            **self.issue_gate_fields(),
        )
        self.assertEqual("BLOCK_ACCEPTANCE", result.disposition)
        self.assertTrue(result.acceptance_blocked_now)

    def test_missing_rationale_rejects_disposition(self):
        result = self.decide(
            severity="P3",
            proposed_disposition="ACCEPT_AS_LOW_VALUE",
            rationale="   ",
            economically_useful=False,
        )
        self.assertEqual("REJECTED", result.decision_status)

    def test_only_issue_required_dispositions_need_open_links(self):
        result = self.tracking(
            findings_requiring_issue=2,
            findings_with_open_issue_links=2,
            newly_created_issues=1,
        )
        self.assertEqual("COMPLETE", result.status)
        self.assertTrue(result.merge_allowed)

    def test_missing_required_issue_blocks(self):
        result = self.tracking(
            findings_requiring_issue=2,
            findings_with_open_issue_links=1,
            newly_created_issues=1,
        )
        self.assertEqual("BLOCKED_MISSING_ISSUES", result.status)

    def test_default_new_issue_budget_is_three(self):
        result = self.tracking(
            findings_requiring_issue=4,
            findings_with_open_issue_links=4,
            newly_created_issues=4,
        )
        self.assertEqual("BLOCKED_ISSUE_BUDGET", result.status)

    def test_issue_budget_can_be_exceeded_with_explicit_explanation(self):
        result = self.tracking(
            findings_requiring_issue=4,
            findings_with_open_issue_links=4,
            newly_created_issues=4,
            budget_exception_explained=True,
        )
        self.assertEqual("COMPLETE", result.status)

    def test_no_issue_required_findings_is_complete(self):
        result = self.tracking(
            findings_requiring_issue=0,
            findings_with_open_issue_links=0,
            newly_created_issues=0,
        )
        self.assertTrue(result.complete)

    def test_scenario_6_post_remediation_regression_blocks_acceptance(self):
        result = self.post(
            complete_final_diff_reviewed=True,
            original_finding_resolved=True,
            required_verification_passed=True,
            security_and_data_boundaries_rechecked=True,
            objective_still_satisfied=True,
            new_regression_detected=True,
        )
        self.assertEqual("BLOCKED_REGRESSION", result.status)
        self.assertFalse(result.accepted)

    def test_complete_post_remediation_review_passes(self):
        result = self.post(
            complete_final_diff_reviewed=True,
            original_finding_resolved=True,
            required_verification_passed=True,
            security_and_data_boundaries_rechecked=True,
            objective_still_satisfied=True,
        )
        self.assertEqual("PASS", result.status)
        self.assertTrue(result.accepted)


if __name__ == "__main__":
    unittest.main(verbosity=1)
