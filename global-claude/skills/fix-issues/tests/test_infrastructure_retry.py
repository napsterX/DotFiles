#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "infrastructure_retry.py"
spec = importlib.util.spec_from_file_location("infrastructure_retry", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class InfrastructureRetryTests(unittest.TestCase):
    def evidence(self, **overrides):
        values = dict(operation="github_read", attempt=1, message="connection reset")
        values.update(overrides)
        return module.FailureEvidence(**values)

    def test_01_transient_http_retries_with_bounded_backoff(self):
        result = module.decide_retry(self.evidence(http_status=503, message=""))
        self.assertEqual("RETRY_AFTER_BACKOFF", result.action)
        self.assertEqual(15, result.delay_seconds)

    def test_02_second_retry_waits_sixty_seconds(self):
        result = module.decide_retry(self.evidence(attempt=2, http_status=429, message=""))
        self.assertEqual(60, result.delay_seconds)

    def test_03_third_failure_exhausts_retries(self):
        result = module.decide_retry(self.evidence(attempt=3, http_status=502, message=""))
        self.assertEqual("RETRIES_EXHAUSTED", result.action)

    def test_04_authentication_failure_never_retries(self):
        result = module.decide_retry(self.evidence(http_status=401, message="bad credentials"))
        self.assertEqual("STOP_OPERATION", result.action)

    def test_05_unknown_failure_never_retries(self):
        result = module.decide_retry(self.evidence(message="deterministic validation failed"))
        self.assertEqual("STOP_OPERATION", result.action)

    def test_06_mutation_requires_read_after_write_reconciliation(self):
        result = module.decide_retry(
            self.evidence(operation="github_comment", http_status=503, message="")
        )
        self.assertEqual("RECONCILE_BEFORE_RETRY", result.action)

    def test_07_reconciled_absent_mutation_can_retry(self):
        result = module.decide_retry(
            self.evidence(
                operation="github_comment",
                http_status=503,
                message="",
                mutation_reconciled_absent=True,
            )
        )
        self.assertEqual("RETRY_AFTER_BACKOFF", result.action)

    def test_08_budget_can_prevent_retry(self):
        result = module.decide_retry(
            self.evidence(http_status=503, message="", remaining_budget_seconds=10)
        )
        self.assertEqual("BUDGET_EXHAUSTED", result.action)

    def test_09_network_exit_code_is_retryable(self):
        result = module.decide_retry(self.evidence(exit_code=28, message=""))
        self.assertEqual("RETRY_AFTER_BACKOFF", result.action)

    def test_10_tests_are_not_supported_retry_operations(self):
        result = module.decide_retry(
            self.evidence(operation="test_command", message="timeout")
        )
        self.assertEqual("STOP_OPERATION", result.action)
        self.assertEqual("UNSUPPORTED_OPERATION", result.classification)

    def test_11_idempotency_marker_is_stable_and_sanitized(self):
        marker = module.idempotency_marker("run with spaces", 42, "github_comment")
        self.assertEqual(
            "<!-- fix-issues:run-with-spaces:issue-42:github_comment -->", marker
        )

    def test_12_marker_rejects_read_operation(self):
        with self.assertRaises(module.InfrastructureRetryError):
            module.idempotency_marker("run", 1, "github_read")


if __name__ == "__main__":
    unittest.main()
