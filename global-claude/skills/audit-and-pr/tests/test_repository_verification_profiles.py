#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "repository_verification.py"
spec = importlib.util.spec_from_file_location("repository_verification", HELPER)
assert spec and spec.loader
rv = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = rv
spec.loader.exec_module(rv)


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class RepositoryVerificationProfileTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="audit-pr-profiles-"))
        self.repo = self.root / "repo with spaces"
        self.repo.mkdir()
        run(["git", "init", "-q"], self.repo)
        run(["git", "config", "user.email", "test@example.com"], self.repo)
        run(["git", "config", "user.name", "Test User"], self.repo)
        (self.repo / "README.md").write_text("base\n")
        run(["git", "add", "README.md"], self.repo)
        run(["git", "commit", "-qm", "base"], self.repo)
        run(["git", "branch", "-M", "main"], self.repo)
        run(["git", "remote", "add", "origin", str(self.repo)], self.repo)
        run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"], self.repo)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def make_adapter(self, body: str):
        path = self.repo / "scripts" / "verify"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/usr/bin/env python3\n" + body)
        path.chmod(0o755)

    def test_doctor_invocation_has_no_base_argument(self):
        self.make_adapter("import sys\nprint('|'.join(sys.argv[1:]))\n")
        result = rv.run_repository_verification(
            self.repo,
            "origin/main",
            profile="doctor",
        )
        self.assertEqual("PASS", result.status)
        self.assertEqual(["./scripts/verify", "doctor"], result.command)
        self.assertEqual("doctor", result.stdout.strip())

    def test_fast_invocation_passes_exact_base(self):
        self.make_adapter("import sys\nprint('|'.join(sys.argv[1:]))\n")
        result = rv.run_repository_verification(
            self.repo,
            "origin/main",
            profile="fast",
        )
        self.assertEqual("PASS", result.status)
        self.assertEqual(["./scripts/verify", "fast", "--base", "origin/main"], result.command)
        self.assertEqual("fast|--base|origin/main", result.stdout.strip())

    def test_ship_remains_final_profile(self):
        self.make_adapter("import sys\nprint('|'.join(sys.argv[1:]))\n")
        result = rv.run_repository_verification(
            self.repo,
            "origin/main",
            profile="ship",
        )
        self.assertEqual("PASS", result.status)
        self.assertEqual("ship|--base|origin/main", result.stdout.strip())

    def test_fast_failure_blocks_without_fallback(self):
        self.make_adapter("raise SystemExit(1)\n")
        result = rv.run_repository_verification(
            self.repo,
            "origin/main",
            profile="fast",
        )
        self.assertEqual("BLOCKED_REQUIRED_CHECK", result.status)
        self.assertEqual("adapter", result.mode)

    def test_unsupported_profile_is_invocation_blocker(self):
        self.make_adapter("print('should not run')\n")
        result = rv.run_repository_verification(
            self.repo,
            "origin/main",
            profile="full",
        )
        self.assertEqual("BLOCKED_INVOCATION", result.status)
        self.assertEqual(2, result.effective_exit_code)


if __name__ == "__main__":
    unittest.main(verbosity=1)
