#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "workflow_plan.py"
spec = importlib.util.spec_from_file_location("workflow_plan", HELPER)
assert spec and spec.loader
wf = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = wf
spec.loader.exec_module(wf)


class WorkflowPlanTests(unittest.TestCase):
    def plan(self, **kwargs):
        return wf.build_workflow_plan(wf.WorkflowInputs(**kwargs))

    def test_valid_adapter_uses_doctor_and_fast_not_initial_ship(self):
        result = self.plan(adapter_state="VALID", run_fast_preflight=True)
        self.assertEqual(("verify_doctor", "verify_fast_with_base"), result.pre_audit_steps)
        self.assertFalse(result.initial_ship_required)
        self.assertNotIn("verify_ship_with_base", result.pre_audit_steps)

    def test_fast_preflight_can_be_deliberately_skipped(self):
        result = self.plan(adapter_state="VALID", run_fast_preflight=False)
        self.assertEqual(("verify_doctor",), result.pre_audit_steps)

    def test_invalid_adapter_blocks_before_audit(self):
        result = self.plan(adapter_state="INVALID")
        self.assertTrue(result.blocked_before_audit)
        self.assertEqual(("block_invalid_adapter",), result.pre_audit_steps)

    def test_absent_adapter_preserves_legacy_flow(self):
        result = self.plan(adapter_state="ABSENT", final_scope_committed=True)
        self.assertEqual(("legacy_validation_discovery",), result.pre_audit_steps)
        self.assertEqual(("legacy_final_validation",), result.final_steps)
        self.assertFalse(result.final_ship_required)

    def test_normal_remediation_does_not_run_ship(self):
        result = self.plan(
            adapter_state="VALID",
            remediation_changed_tracked_files=True,
        )
        self.assertEqual(("targeted_validation", "independent_reaudit"), result.remediation_steps)
        self.assertFalse(result.remediation_ship_required)
        self.assertNotIn("verify_ship_with_base", result.remediation_steps)

    def test_remediation_can_rerun_fast_when_preflight_is_invalidated(self):
        result = self.plan(
            adapter_state="VALID",
            remediation_changed_tracked_files=True,
            remediation_invalidates_preflight=True,
        )
        self.assertIn("verify_fast_with_base", result.remediation_steps)
        self.assertNotIn("verify_ship_with_base", result.remediation_steps)

    def test_governance_sensitive_remediation_adds_conformance_and_fast(self):
        result = self.plan(
            adapter_state="VALID",
            remediation_changed_tracked_files=True,
            governance_sensitive=True,
        )
        self.assertIn("verify_fast_with_base", result.remediation_steps)
        self.assertIn("focused_verification_conformance", result.remediation_steps)

    def test_final_committed_head_requires_one_ship_gate(self):
        result = self.plan(adapter_state="VALID", final_scope_committed=True)
        self.assertEqual(("verify_ship_with_base",), result.final_steps)
        self.assertTrue(result.final_ship_required)

    def test_uncommitted_scope_does_not_run_final_ship(self):
        result = self.plan(adapter_state="VALID", final_scope_committed=False)
        self.assertEqual((), result.final_steps)
        self.assertFalse(result.final_ship_required)


if __name__ == "__main__":
    unittest.main(verbosity=1)
