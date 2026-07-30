#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "delegated_invocation.py"
spec = importlib.util.spec_from_file_location("delegated_invocation", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

A = "a" * 40
B = "b" * 40
C = "c" * 40


class DelegatedInvocationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="delegated invocation ")
        self.repo = Path(self.temp.name) / "repo with spaces"
        self.repo.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def manifest(self, **overrides):
        value = {
            "schema_version": 1,
            "source_skill": "fix-issues",
            "request": "audit-and-pr-finalization",
            "repository_root": str(self.repo),
            "repository": "owner/repo",
            "branch": "issue/batch-p3-p2",
            "starting_head": A,
            "ending_head": B,
            "fixed_issues": [{"number": 12, "commit_sha": C}],
            "outcomes": [{"number": 12, "status": "fixed"}],
            "cumulative_verification": {"status": "PASS", "commands": ["verify"]},
            "created_at": "2026-07-30T00:00:00Z",
        }
        value.update(overrides)
        return value

    def test_01_valid_manifest(self):
        result = module.validate_manifest(
            self.manifest(),
            current_repository=str(self.repo),
            current_branch="issue/batch-p3-p2",
            current_head=B,
        )
        self.assertEqual("VALID", result["status"])
        self.assertEqual(1, result["fixed_count"])

    def test_02_wrong_source_skill_rejected(self):
        with self.assertRaises(module.DelegationError):
            module.validate_manifest(self.manifest(source_skill="other"))

    def test_03_no_fixed_issues_rejected(self):
        with self.assertRaises(module.DelegationError):
            module.validate_manifest(self.manifest(fixed_issues=[]))

    def test_04_head_mismatch_rejected(self):
        with self.assertRaises(module.DelegationError):
            module.validate_manifest(self.manifest(), current_head=A)

    def test_05_repository_mismatch_rejected(self):
        other = Path(self.temp.name) / "other"
        other.mkdir()
        with self.assertRaises(module.DelegationError):
            module.validate_manifest(self.manifest(), current_repository=str(other))

    def test_06_duplicate_issue_rejected(self):
        fixed = [
            {"number": 12, "commit_sha": C},
            {"number": 12, "commit_sha": "d" * 40},
        ]
        with self.assertRaises(module.DelegationError):
            module.validate_manifest(self.manifest(fixed_issues=fixed))

    def test_07_fixed_issue_must_appear_in_outcomes(self):
        with self.assertRaises(module.DelegationError):
            module.validate_manifest(self.manifest(outcomes=[{"number": 13, "status": "fixed"}]))

    def test_08_schema_two_run_journal_is_accepted(self):
        journal = Path(self.temp.name) / "runs" / "run-state.json"
        journal.parent.mkdir()
        journal.write_text("{}", encoding="utf-8")
        common = Path(self.temp.name) / "common.git"
        common.mkdir()
        manifest = self.manifest(
            schema_version=2,
            run_id="run-123",
            run_journal=str(journal),
            task_worktree=str(self.repo),
            git_common_dir=str(common),
            issue_timeout_minutes=60,
        )
        result = module.validate_manifest(
            manifest,
            current_repository=str(self.repo),
            current_branch="issue/batch-p3-p2",
            current_head=B,
        )
        self.assertEqual(2, result["schema_version"])
        self.assertEqual("run-123", result["run_id"])

    def test_09_schema_two_requires_run_identity(self):
        with self.assertRaises(module.DelegationError):
            module.validate_manifest(self.manifest(schema_version=2))


if __name__ == "__main__":
    unittest.main()
