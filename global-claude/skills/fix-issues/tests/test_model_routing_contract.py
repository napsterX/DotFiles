#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "model_routing_contract.py"
spec = importlib.util.spec_from_file_location("model_routing_contract", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class ModelRoutingContractTests(unittest.TestCase):
    def decision(self, model="sonnet", **overrides):
        values = dict(
            issue=42,
            attempt=1,
            selected_model=model,
            risk="medium",
            complexity="localized",
            rationale="Scoped implementation with clear behavior and established tests.",
            alternatives_considered=("opus",),
            implementation_expected=True,
            previous_model=None,
        )
        values.update(overrides)
        return module.RoutingDecision(**values)

    def test_01_sonnet_is_allowed(self):
        module.validate_decision(self.decision("sonnet"))

    def test_02_opus_is_allowed(self):
        module.validate_decision(self.decision("opus", alternatives_considered=("sonnet",)))

    def test_03_fable_is_allowed(self):
        module.validate_decision(self.decision("fable", alternatives_considered=("opus",)))

    def test_04_inherit_is_rejected(self):
        with self.assertRaises(module.RoutingError):
            module.validate_decision(self.decision("inherit"))

    def test_05_haiku_is_rejected_for_implementation(self):
        with self.assertRaises(module.RoutingError):
            module.validate_decision(self.decision("haiku"))

    def test_06_short_rationale_is_rejected(self):
        with self.assertRaises(module.RoutingError):
            module.validate_decision(self.decision(rationale="Because."))

    def test_07_selected_model_cannot_be_rejected_alternative(self):
        with self.assertRaises(module.RoutingError):
            module.validate_decision(self.decision(alternatives_considered=("sonnet",)))

    def test_08_dispatch_contains_explicit_model_and_attempt(self):
        with patch.dict(os.environ, {}, clear=True):
            result = module.dispatch_record(self.decision("opus", alternatives_considered=("sonnet",)))
        self.assertEqual("issue-fix-worker", result["subagent_type"])
        self.assertEqual("opus", result["model"])
        self.assertEqual(1, result["attempt"])

    def test_09_matching_environment_override_is_allowed(self):
        with patch.dict(os.environ, {"CLAUDE_CODE_SUBAGENT_MODEL": "opus"}, clear=True):
            result = module.dispatch_record(self.decision("opus", alternatives_considered=("sonnet",)))
        self.assertEqual("MATCHING_ENVIRONMENT_OVERRIDE", result["routing_status"])

    def test_10_conflicting_environment_override_blocks(self):
        with patch.dict(os.environ, {"CLAUDE_CODE_SUBAGENT_MODEL": "haiku"}, clear=True):
            with self.assertRaises(module.RoutingError):
                module.dispatch_record(self.decision("opus", alternatives_considered=("sonnet",)))

    def test_11_inherit_environment_uses_normal_resolution(self):
        with patch.dict(os.environ, {"CLAUDE_CODE_SUBAGENT_MODEL": "inherit"}, clear=True):
            result = module.dispatch_record(self.decision())
        self.assertEqual("NORMAL_RESOLUTION", result["routing_status"])

    def test_12_invalid_risk_is_rejected(self):
        with self.assertRaises(module.RoutingError):
            module.validate_decision(self.decision(risk="unknown"))

    def test_13_retry_may_escalate(self):
        module.validate_decision(
            self.decision(
                "opus",
                attempt=2,
                previous_model="sonnet",
                alternatives_considered=("fable",),
            )
        )

    def test_14_retry_cannot_silently_downgrade(self):
        with self.assertRaises(module.RoutingError):
            module.validate_decision(
                self.decision(
                    "sonnet",
                    attempt=2,
                    previous_model="opus",
                    alternatives_considered=("fable",),
                )
            )

    def test_15_first_attempt_cannot_have_previous_model(self):
        with self.assertRaises(module.RoutingError):
            module.validate_decision(self.decision(previous_model="sonnet"))


if __name__ == "__main__":
    unittest.main()
