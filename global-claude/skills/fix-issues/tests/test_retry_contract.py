#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "retry_contract.py"
spec = importlib.util.spec_from_file_location("retry_contract", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class RetryContractTests(unittest.TestCase):
    def state(self, **overrides):
        values = dict(
            attempt=1,
            attempt_status="candidate_ready",
            repository_safe=True,
            head_unchanged=True,
            worktree_attributable=True,
            material_new_plan=False,
            acceptance_passed=True,
        )
        values.update(overrides)
        return module.RetryState(**values)

    def test_01_verified_candidate_commits(self):
        self.assertEqual("COMMIT", module.decide_attempt(self.state()))

    def test_02_rejected_candidate_retries_with_new_plan(self):
        self.assertEqual(
            "RETRY",
            module.decide_attempt(
                self.state(acceptance_passed=False, material_new_plan=True)
            ),
        )

    def test_03_rejected_candidate_without_new_plan_fails(self):
        self.assertEqual(
            "FAIL_ISSUE",
            module.decide_attempt(self.state(acceptance_passed=False)),
        )

    def test_04_retryable_failure_retries(self):
        self.assertEqual(
            "RETRY",
            module.decide_attempt(
                self.state(
                    attempt_status="retryable_failed",
                    acceptance_passed=False,
                    material_new_plan=True,
                )
            ),
        )

    def test_05_retryable_failure_without_progress_fails(self):
        self.assertEqual(
            "FAIL_ISSUE_NO_PROGRESS",
            module.decide_attempt(
                self.state(
                    attempt_status="retryable_failed",
                    acceptance_passed=False,
                    material_new_plan=False,
                )
            ),
        )

    def test_06_attempt_three_exhausts(self):
        self.assertEqual(
            "FAIL_ISSUE_ATTEMPTS_EXHAUSTED",
            module.decide_attempt(
                self.state(
                    attempt=3,
                    attempt_status="retryable_failed",
                    acceptance_passed=False,
                    material_new_plan=True,
                )
            ),
        )

    def test_07_unsafe_repository_stops_batch(self):
        self.assertEqual(
            "STOP_BATCH_UNSAFE_STATE",
            module.decide_attempt(self.state(repository_safe=False)),
        )

    def test_08_blocked_finalizes_issue(self):
        self.assertEqual(
            "FINALIZE_ISSUE",
            module.decide_attempt(
                self.state(attempt_status="blocked", acceptance_passed=False)
            ),
        )

    def test_09_no_fixes_skips_audit_and_pr(self):
        self.assertEqual(
            "NOT_APPLICABLE_NO_FIXES",
            module.decide_finalization(False, True),
        )

    def test_10_unsafe_cumulative_state_blocks_finalization(self):
        self.assertEqual(
            "FINALIZATION_BLOCKED",
            module.decide_finalization(True, False),
        )

    def test_11_safe_fixed_batch_invokes_audit_and_pr(self):
        self.assertEqual(
            "INVOKE_AUDIT_AND_PR",
            module.decide_finalization(True, True),
        )


if __name__ == "__main__":
    unittest.main()
