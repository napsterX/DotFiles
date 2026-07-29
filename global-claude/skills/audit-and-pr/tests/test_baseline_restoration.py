#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "baseline_restoration.py"
spec = importlib.util.spec_from_file_location("baseline_restoration", HELPER)
assert spec and spec.loader
br = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = br
spec.loader.exec_module(br)


class BaselineRestorationTests(unittest.TestCase):
    def observation(self, **overrides):
        values = dict(
            check_name="dashboard test A",
            first_causal_error="expected rendered card",
            environment_profile="ship / node 22",
            base_result="FAIL",
            branch_result="PASS",
            canonical_issue="https://example.test/issues/435",
            canonical_issue_open=True,
            domain="general",
        )
        values.update(overrides)
        return br.FailureObservation(**values)

    def assess(self, observations, **overrides):
        values = dict(
            mode_source="EXPLICIT",
            restoration_intent_proven=True,
            canonical_base_reproduced=True,
            same_authoritative_command=True,
            same_material_environment=True,
            final_ship_exit_code=1,
            observations=tuple(observations),
        )
        values.update(overrides)
        return br.assess_baseline_restoration(br.RestorationInputs(**values))

    def test_normal_green_ship_needs_no_exception(self):
        result = self.assess([self.observation()], final_ship_exit_code=0)
        self.assertEqual("NORMAL_GREEN", result.classification)
        self.assertTrue(result.allow_push_and_pr)
        self.assertFalse(result.manual_merge_required)

    def test_red_base_branch_fixes_one_with_tracked_residuals_is_allowed(self):
        result = self.assess(
            [
                self.observation(),
                self.observation(
                    check_name="dashboard test B",
                    first_causal_error="missing loading state",
                    base_result="FAIL",
                    branch_result="FAIL",
                    canonical_issue="https://example.test/issues/436",
                ),
            ]
        )
        self.assertEqual("FAILED_PRE_EXISTING_BASELINE", result.classification)
        self.assertTrue(result.eligible)
        self.assertTrue(result.allow_push_and_pr)
        self.assertTrue(result.manual_merge_required)
        self.assertFalse(result.auto_merge_allowed)

    def test_current_branch_regression_is_blocked(self):
        result = self.assess(
            [
                self.observation(),
                self.observation(
                    check_name="branch-only failure",
                    first_causal_error="new assertion failed",
                    base_result="PASS",
                    branch_result="FAIL",
                    canonical_issue="",
                    canonical_issue_open=False,
                    plausibly_caused_by_current_diff=True,
                ),
            ]
        )
        self.assertEqual("BLOCKED", result.classification)
        self.assertIn("new regression", " ".join(result.blockers))

    def test_unattributed_branch_only_failure_is_blocked(self):
        result = self.assess(
            [
                self.observation(),
                self.observation(
                    check_name="unknown branch failure",
                    first_causal_error="timeout",
                    base_result="NOT_OBSERVED",
                    branch_result="FAIL",
                    canonical_issue="",
                    canonical_issue_open=False,
                ),
            ]
        )
        self.assertEqual("BLOCKED", result.classification)
        self.assertIn("unattributed", " ".join(result.blockers))

    def test_red_security_gate_cannot_use_exception(self):
        result = self.assess(
            [
                self.observation(),
                self.observation(
                    check_name="authorization isolation",
                    first_causal_error="cross-tenant access allowed",
                    base_result="FAIL",
                    branch_result="FAIL",
                    canonical_issue="https://example.test/issues/99",
                    domain="authorization",
                ),
            ]
        )
        self.assertEqual("BLOCKED", result.classification)
        self.assertIn("protected-domain residual", " ".join(result.blockers))

    def test_newly_unmasked_preexisting_failure_with_issue_is_allowed(self):
        result = self.assess(
            [
                self.observation(),
                self.observation(
                    check_name="dashboard test C",
                    first_causal_error="fixture import fails",
                    base_result="NOT_OBSERVED",
                    branch_result="FAIL",
                    canonical_issue="https://example.test/issues/438",
                    canonical_issue_open=True,
                    pre_existing_newly_unmasked_proven=True,
                ),
            ]
        )
        self.assertEqual("FAILED_PRE_EXISTING_BASELINE", result.classification)
        dispositions = {row.disposition for row in result.ledger}
        self.assertIn("PRE_EXISTING_NEWLY_UNMASKED", dispositions)

    def test_newly_unmasked_failure_without_issue_is_blocked(self):
        result = self.assess(
            [
                self.observation(),
                self.observation(
                    check_name="dashboard test C",
                    first_causal_error="fixture import fails",
                    base_result="NOT_OBSERVED",
                    branch_result="FAIL",
                    canonical_issue="",
                    canonical_issue_open=False,
                    pre_existing_newly_unmasked_proven=True,
                ),
            ]
        )
        self.assertEqual("BLOCKED", result.classification)

    def test_exit_codes_other_than_one_are_not_baseline_failures(self):
        for exit_code in (2, 3, 4, 5):
            with self.subTest(exit_code=exit_code):
                result = self.assess([self.observation()], final_ship_exit_code=exit_code)
                self.assertEqual("BLOCKED", result.classification)

    def test_mode_is_not_inferred_from_red_gate_alone(self):
        result = self.assess(
            [self.observation()],
            mode_source="NONE",
            restoration_intent_proven=False,
        )
        self.assertEqual("BLOCKED", result.classification)
        self.assertIn("neither explicitly requested", " ".join(result.blockers))

    def test_low_testing_confidence_blocks(self):
        result = self.assess([self.observation()], testing_confidence="LOW")
        self.assertEqual("BLOCKED", result.classification)

    def test_gate_weakening_blocks(self):
        result = self.assess([self.observation()], gate_weakened=True)
        self.assertEqual("BLOCKED", result.classification)

    def test_favorable_retry_sampling_blocks(self):
        result = self.assess([self.observation()], favorable_retry_sampling_used=True)
        self.assertEqual("BLOCKED", result.classification)

    def test_non_default_integration_target_requires_manual_issue_reconciliation(self):
        before = br.assess_post_merge_reconciliation(
            br.PostMergeReconciliationInputs(
                pr_target_branch="staging",
                github_default_branch="main",
                merge_confirmed=True,
                issue_reconciled=False,
            )
        )
        self.assertTrue(before.reconciliation_required)
        self.assertFalse(before.cleanup_allowed)

        after = br.assess_post_merge_reconciliation(
            br.PostMergeReconciliationInputs(
                pr_target_branch="staging",
                github_default_branch="main",
                merge_confirmed=True,
                issue_reconciled=True,
            )
        )
        self.assertTrue(after.cleanup_allowed)
        self.assertEqual("staging", after.cleanup_target_branch)

    def test_default_branch_target_does_not_require_manual_issue_reconciliation(self):
        result = br.assess_post_merge_reconciliation(
            br.PostMergeReconciliationInputs(
                pr_target_branch="main",
                github_default_branch="main",
                merge_confirmed=True,
            )
        )
        self.assertFalse(result.reconciliation_required)
        self.assertTrue(result.cleanup_allowed)
        self.assertEqual("main", result.cleanup_target_branch)

    def test_fixed_base_failure_still_requires_canonical_open_issue(self):
        result = self.assess(
            [
                self.observation(
                    canonical_issue="",
                    canonical_issue_open=False,
                )
            ]
        )
        self.assertEqual("BLOCKED", result.classification)
        self.assertIn("canonical open issue", " ".join(result.blockers))

    def test_conclusive_inferred_mode_can_be_eligible(self):
        result = self.assess(
            [self.observation()],
            mode_source="INFERRED",
            restoration_intent_proven=True,
        )
        self.assertEqual("FAILED_PRE_EXISTING_BASELINE", result.classification)
        self.assertTrue(result.eligible)


if __name__ == "__main__":
    unittest.main(verbosity=1)
