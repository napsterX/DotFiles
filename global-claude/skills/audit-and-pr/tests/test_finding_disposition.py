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
        return fd.decide_finding(fd.FindingInputs(**kwargs))

    def tracking(self, **kwargs):
        return fd.assess_deferred_tracking(fd.DeferredTrackingInputs(**kwargs))

    def test_p0_eligible_fix_enters_remediation(self):
        result = self.decide(severity="P0", remediation_eligible=True)
        self.assertEqual("REMEDIATE_CURRENT_SCOPE", result.disposition)
        self.assertTrue(result.may_modify_code)

    def test_p1_eligible_fix_enters_remediation(self):
        result = self.decide(severity="P1", remediation_eligible=True)
        self.assertEqual("REMEDIATE_CURRENT_SCOPE", result.disposition)

    def test_unfixable_p0_or_p1_blocks_instead_of_deferring(self):
        for severity in ("P0", "P1"):
            with self.subTest(severity=severity):
                result = self.decide(severity=severity, remediation_eligible=False)
                self.assertEqual("BLOCK_SHIPMENT", result.disposition)
                self.assertTrue(result.merge_blocked_now)
                self.assertFalse(result.issue_required)

    def test_p2_is_never_fixed_even_when_mechanical(self):
        result = self.decide(severity="P2", remediation_eligible=True)
        self.assertEqual("DEFER_TO_GITHUB", result.disposition)
        self.assertFalse(result.may_modify_code)
        self.assertTrue(result.issue_required)

    def test_p3_is_never_fixed_even_when_mechanical(self):
        result = self.decide(severity="P3", remediation_eligible=True)
        self.assertEqual("DEFER_TO_GITHUB", result.disposition)
        self.assertFalse(result.may_modify_code)

    def test_equivalent_open_issue_is_reused(self):
        result = self.decide(severity="P2", existing_issue_state="OPEN_EQUIVALENT")
        self.assertEqual("REUSE_OPEN", result.issue_action)

    def test_closed_equivalent_does_not_count_as_active_tracking(self):
        result = self.decide(severity="P3", existing_issue_state="CLOSED_EQUIVALENT")
        self.assertEqual("CREATE_NEW", result.issue_action)

    def test_objective_required_gap_cannot_be_deferred_as_p2_or_p3(self):
        for severity in ("P2", "P3"):
            with self.subTest(severity=severity):
                result = self.decide(severity=severity, objective_required=True)
                self.assertEqual("BLOCK_CLASSIFICATION_REVIEW", result.disposition)
                self.assertTrue(result.merge_blocked_now)

    def test_audit_process_note_is_not_fixed_or_ticketed(self):
        result = self.decide(severity="P2", kind="AUDIT_PROCESS_NOTE")
        self.assertEqual("REPORT_ONLY", result.disposition)
        self.assertFalse(result.issue_required)

    def test_unconfirmed_speculation_is_not_ticketed(self):
        result = self.decide(severity="P3", confirmed=False)
        self.assertEqual("REPORT_ONLY", result.disposition)

    def test_all_deferred_findings_must_have_open_issue_links(self):
        result = self.tracking(
            confirmed_deferred_findings=3,
            findings_with_open_issue_links=2,
        )
        self.assertEqual("BLOCKED_MISSING_ISSUES", result.status)
        self.assertFalse(result.merge_allowed)

    def test_github_failure_blocks_merge(self):
        result = self.tracking(
            confirmed_deferred_findings=2,
            findings_with_open_issue_links=0,
            issue_creation_failed=True,
        )
        self.assertEqual("BLOCKED_GITHUB", result.status)
        self.assertFalse(result.merge_allowed)

    def test_complete_tracking_allows_merge_gate_to_continue(self):
        result = self.tracking(
            confirmed_deferred_findings=2,
            findings_with_open_issue_links=2,
        )
        self.assertEqual("COMPLETE", result.status)
        self.assertTrue(result.merge_allowed)

    def test_no_deferred_findings_is_complete(self):
        result = self.tracking(
            confirmed_deferred_findings=0,
            findings_with_open_issue_links=0,
        )
        self.assertTrue(result.complete)

    def test_invalid_tracking_counts_are_rejected(self):
        with self.assertRaises(ValueError):
            self.tracking(
                confirmed_deferred_findings=1,
                findings_with_open_issue_links=2,
            )


if __name__ == "__main__":
    unittest.main(verbosity=1)
