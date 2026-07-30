#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "worktree_context.py"
spec = importlib.util.spec_from_file_location("worktree_context", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(cwd), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise AssertionError(result.stderr)
    return result.stdout.strip()


class WorktreeContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="audit worktree context ")
        self.base = Path(self.tmp.name)
        self.repo = self.base / "project root"
        self.repo.mkdir()
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.name", "Test User")
        git(self.repo, "config", "user.email", "test@example.com")
        (self.repo / "README.md").write_text("base\n")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-m", "initial")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def add_branch_worktree(self, path: Path, branch: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        git(self.repo, "worktree", "add", "-b", branch, str(path), "main")

    def test_current_checkout_uses_in_place(self) -> None:
        r = module.resolve(self.repo, None, None)
        self.assertEqual("CURRENT", r.worktree_class)
        self.assertEqual("IN_PLACE", r.execution_mode)
        self.assertFalse(r.enter_worktree_should_be_attempted)

    def test_external_sibling_is_pinned_and_never_entered(self) -> None:
        target = self.base / "project-issue-446"
        self.add_branch_worktree(target, "issue-446")
        r = module.resolve(self.repo, target, None)
        self.assertEqual("EXTERNAL_REGISTERED", r.worktree_class)
        self.assertEqual("PINNED_TASK_ROOT", r.execution_mode)
        self.assertFalse(r.enter_worktree_allowed)
        self.assertFalse(r.enter_worktree_should_be_attempted)
        self.assertTrue(os.path.samefile(target, r.task_root))

    def test_claude_managed_worktree_is_recognized_but_switch_is_not_required(self) -> None:
        target = self.repo / ".claude" / "worktrees" / "issue-7"
        self.add_branch_worktree(target, "issue-7")
        r = module.resolve(self.repo, target, None)
        self.assertEqual("CLAUDE_MANAGED", r.worktree_class)
        self.assertTrue(r.enter_worktree_allowed)
        self.assertFalse(r.enter_worktree_should_be_attempted)

    def test_branch_resolution_selects_external_worktree(self) -> None:
        target = self.base / "feature location"
        self.add_branch_worktree(target, "feature/test")
        r = module.resolve(self.repo, None, "feature/test")
        self.assertEqual("feature/test", r.target_branch)
        self.assertTrue(os.path.samefile(target, r.task_root))

    def test_unregistered_target_is_blocked(self) -> None:
        other = self.base / "not registered"
        other.mkdir()
        with self.assertRaises(module.WorktreeError):
            module.resolve(self.repo, other, None)

    def test_other_repository_is_blocked(self) -> None:
        other = self.base / "other repo"
        other.mkdir()
        git(other, "init", "-b", "main")
        with self.assertRaises(module.WorktreeError):
            module.resolve(self.repo, other, None)

    def test_path_with_spaces_is_safe(self) -> None:
        target = self.base / "external worktree with spaces"
        self.add_branch_worktree(target, "spaces")
        cmd = ["python3", str(MODULE_PATH), "--invocation-root", str(self.repo), "--target-path", str(target)]
        result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("OK", payload["status"])
        self.assertTrue(os.path.samefile(target, payload["task_root"]))

    def test_missing_branch_is_blocked(self) -> None:
        with self.assertRaises(module.WorktreeError):
            module.resolve(self.repo, None, "does-not-exist")


if __name__ == "__main__":
    unittest.main()
