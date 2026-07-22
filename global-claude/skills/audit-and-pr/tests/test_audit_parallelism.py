#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "audit_parallelism.py"
spec = importlib.util.spec_from_file_location("audit_parallelism", HELPER)
assert spec and spec.loader
ap = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ap
spec.loader.exec_module(ap)


class AuditParallelismTests(unittest.TestCase):
    def plan(self, **kwargs):
        return ap.plan_parallelism(ap.ParallelismInputs(**kwargs))

    def test_docs_only_stays_sequential(self):
        result = self.plan(changed_paths=("README.md", "docs/flow.md"), risk="LOW")
        self.assertEqual("SEQUENTIAL", result.execution_mode)
        self.assertEqual(1, result.max_workers)
        self.assertTrue(result.docs_only)

    def test_small_low_risk_change_stays_sequential(self):
        result = self.plan(
            changed_paths=("src/a.py", "tests/test_a.py"),
            risk="LOW",
            affected_domains=1,
        )
        self.assertEqual(1, result.max_workers)

    def test_medium_change_gets_two_lanes(self):
        result = self.plan(
            changed_paths=tuple(f"src/f{i}.py" for i in range(8)),
            risk="MEDIUM",
            affected_domains=2,
        )
        self.assertEqual("PARALLEL", result.execution_mode)
        self.assertEqual(2, result.max_workers)

    def test_high_risk_change_gets_three_lanes(self):
        result = self.plan(
            changed_paths=("src/auth.py", "src/tenant.py"),
            risk="HIGH",
            affected_domains=2,
        )
        self.assertEqual(3, result.max_workers)

    def test_large_change_gets_three_lanes(self):
        result = self.plan(
            changed_paths=tuple(f"src/f{i}.py" for i in range(21)),
            risk="MEDIUM",
            affected_domains=2,
        )
        self.assertEqual(3, result.max_workers)

    def test_governance_sensitive_adds_dedicated_lane(self):
        result = self.plan(
            changed_paths=("scripts/verify", "src/app.py"),
            risk="HIGH",
            affected_domains=3,
            governance_sensitive=True,
        )
        self.assertEqual(4, result.max_workers)
        self.assertEqual("verification-governance", result.lanes[-1].lane_id)

    def test_governance_lane_does_not_exceed_four_workers(self):
        result = self.plan(
            changed_paths=tuple(f"src/f{i}.py" for i in range(30)),
            risk="HIGH",
            affected_domains=5,
            governance_sensitive=True,
            explicit_mode="PARALLEL",
        )
        self.assertLessEqual(result.max_workers, 4)

    def test_host_without_parallel_support_falls_back_cleanly(self):
        result = self.plan(
            changed_paths=tuple(f"src/f{i}.py" for i in range(30)),
            risk="HIGH",
            affected_domains=4,
            host_supports_parallel=False,
        )
        self.assertEqual("SEQUENTIAL", result.execution_mode)
        self.assertEqual(1, result.max_workers)

    def test_explicit_sequential_wins(self):
        result = self.plan(
            changed_paths=tuple(f"src/f{i}.py" for i in range(30)),
            risk="HIGH",
            explicit_mode="SEQUENTIAL",
        )
        self.assertEqual(1, result.max_workers)

    def test_explicit_parallel_uses_three_standard_lanes(self):
        result = self.plan(
            changed_paths=("src/a.py",),
            risk="LOW",
            explicit_mode="PARALLEL",
        )
        self.assertEqual(3, result.max_workers)

    def test_all_lanes_are_read_only(self):
        result = self.plan(
            changed_paths=tuple(f"src/f{i}.py" for i in range(10)),
            risk="MEDIUM",
            affected_domains=2,
        )
        self.assertTrue(all(lane.read_only for lane in result.lanes))


if __name__ == "__main__":
    unittest.main(verbosity=1)
