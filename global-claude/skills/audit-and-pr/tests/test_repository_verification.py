#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import signal
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
HELPER = SKILL_ROOT / "scripts" / "repository_verification.py"
sys.path.insert(0, str(HELPER.parent))

import repository_verification as rv  # noqa: E402


def run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"command failed: {command}\nstdout={result.stdout}\nstderr={result.stderr}"
        )
    return result


class RepositoryVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.suite_temp = tempfile.TemporaryDirectory(prefix="audit-and-pr-suite-")
        cls.template = Path(cls.suite_temp.name) / "template"
        cls.template.mkdir()
        run(["git", "init"], cwd=cls.template)
        run(["git", "config", "user.name", "Skill Test"], cwd=cls.template)
        run(["git", "config", "user.email", "skill-test@example.invalid"], cwd=cls.template)
        run(["git", "checkout", "-b", "main"], cwd=cls.template)
        (cls.template / "tracked.txt").write_text("initial\n")
        run(["git", "add", "tracked.txt"], cwd=cls.template)
        run(["git", "commit", "-m", "initial"], cwd=cls.template)
        sha = run(["git", "rev-parse", "HEAD"], cwd=cls.template).stdout.strip()
        run(["git", "update-ref", "refs/remotes/origin/main", sha], cwd=cls.template)
        run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main"],
            cwd=cls.template,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.suite_temp.cleanup()

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(
            prefix="case-", dir=self.suite_temp.name
        )
        self.root = Path(self.temp.name)
        self.repo = self.root / "repository with spaces"
        number = int(self._testMethodName.split("_", 2)[1])
        if number in {10, 11, 13, 20, 23, 30, 31}:
            shutil.copytree(self.template, self.repo, symlinks=True)
        else:
            self.repo.mkdir()
            (self.repo / "tracked.txt").write_text("initial\n")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def set_remote_ref(self, branch: str, target: str = "HEAD") -> str:
        sha = run(["git", "rev-parse", target], cwd=self.repo).stdout.strip()
        run(["git", "update-ref", f"refs/remotes/origin/{branch}", sha], cwd=self.repo)
        if branch == "main":
            run(
                ["git", "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main"],
                cwd=self.repo,
            )
        return sha

    def make_adapter(self, body: str, *, executable: bool = True) -> Path:
        adapter = self.repo / "scripts" / "verify"
        adapter.parent.mkdir(parents=True, exist_ok=True)
        adapter.write_text("#!/usr/bin/env python3\n" + body)
        adapter.chmod(0o755 if executable else 0o644)
        return adapter

    def verify(self, base: str = "origin/main", **kwargs) -> rv.VerificationResult:
        return rv.run_repository_verification(self.repo, base, **kwargs)

    def verify_fast(
        self,
        base: str = "origin/main",
        *,
        base_valid: bool = True,
        **kwargs,
    ) -> rv.VerificationResult:
        heads = iter(["a" * 40, "a" * 40])
        statuses = iter([b"", b""])
        base_result = (True, "b" * 40) if base_valid else (False, "invalid base")
        with (
            mock.patch.object(rv, "_git_head", side_effect=lambda _repo: next(heads)),
            mock.patch.object(rv, "_git_status", side_effect=lambda _repo: next(statuses)),
            mock.patch.object(rv, "validate_base", return_value=base_result),
        ):
            return rv.run_repository_verification(self.repo, base, **kwargs)

    # 1. Adapter absent: legacy validation remains available.
    def test_01_adapter_absent_uses_legacy_mode(self) -> None:
        result = self.verify_fast()
        self.assertEqual("NOT_APPLICABLE", result.status)
        self.assertEqual("legacy", result.mode)
        self.assertTrue(rv.repository_verification_allows_audit(result))

    # 2. Valid adapter exit 0 receives the explicit base and permits audit.
    def test_02_adapter_exit_zero_passes_explicit_base(self) -> None:
        self.make_adapter("import sys\nprint('ARGS=' + repr(sys.argv[1:]))\nprint('Planned/executed: 3/3')\nsys.exit(0)\n")
        result = self.verify_fast()
        self.assertEqual("PASS", result.status)
        self.assertIn("['ship', '--base', 'origin/main']", result.stdout)
        self.assertEqual(3, result.counts.planned)
        self.assertEqual(3, result.counts.executed)
        self.assertTrue(rv.repository_verification_allows_audit(result))

    # 3-7. Exact Repository Verification exit-code mapping and no fallback.
    def test_03_exit_one_blocks_without_fallback(self) -> None:
        self.make_adapter("import sys\nprint('required check failed')\nsys.exit(1)\n")
        result = self.verify_fast()
        self.assertEqual("BLOCKED_REQUIRED_CHECK", result.status)
        self.assertEqual(1, result.effective_exit_code)
        self.assertEqual("adapter", result.mode)

    def test_04_exit_two_blocks_without_fallback(self) -> None:
        self.make_adapter("import sys\nprint('unsupported argument', file=sys.stderr)\nsys.exit(2)\n")
        result = self.verify_fast()
        self.assertEqual("BLOCKED_INVOCATION", result.status)
        self.assertEqual(2, result.effective_exit_code)

    def test_05_exit_three_blocks_without_fallback(self) -> None:
        self.make_adapter("import sys\nprint('adapter error', file=sys.stderr)\nsys.exit(3)\n")
        result = self.verify_fast()
        self.assertEqual("BLOCKED_ADAPTER", result.status)
        self.assertEqual(3, result.effective_exit_code)

    def test_06_exit_four_is_environment_blocker(self) -> None:
        self.make_adapter("import sys\nprint('browser unavailable', file=sys.stderr)\nsys.exit(4)\n")
        result = self.verify_fast()
        self.assertEqual("BLOCKED_ENVIRONMENT", result.status)
        self.assertEqual(4, result.effective_exit_code)

    def test_07_exit_five_is_interruption_blocker(self) -> None:
        self.make_adapter("import sys\nprint('interrupted', file=sys.stderr)\nsys.exit(5)\n")
        result = self.verify_fast()
        self.assertEqual("BLOCKED_INTERRUPTED", result.status)
        self.assertEqual(5, result.effective_exit_code)

    # 8. Non-executable adapter is a configuration defect; no chmod/fallback.
    def test_08_non_executable_adapter_blocks(self) -> None:
        adapter = self.make_adapter("raise SystemExit(0)\n", executable=False)
        before = adapter.stat().st_mode
        result = self.verify_fast()
        self.assertEqual("BLOCKED_CONFIGURATION", result.status)
        self.assertEqual(before, adapter.stat().st_mode)
        self.assertEqual("adapter", result.mode)

    # 9. Directory at adapter path blocks.
    def test_09_adapter_directory_blocks(self) -> None:
        (self.repo / "scripts" / "verify").mkdir(parents=True)
        result = self.verify_fast()
        self.assertEqual("BLOCKED_CONFIGURATION", result.status)

    # 10. origin/main is passed exactly.
    def test_10_origin_main_is_passed_exactly(self) -> None:
        self.make_adapter("import sys\nprint('|'.join(sys.argv[1:]))\n")
        result = self.verify_fast("origin/main")
        self.assertEqual("ship|--base|origin/main", result.stdout.strip())
        self.assertEqual("origin/main", result.base)

    # 11. A non-main base with punctuation is passed as one exact argument.
    def test_11_non_main_base_is_passed_exactly(self) -> None:
        self.set_remote_ref("release/v1.2-test")
        self.make_adapter("import sys\nprint(repr(sys.argv[1:]))\n")
        result = self.verify_fast("origin/release/v1.2-test")
        self.assertEqual("PASS", result.status)
        self.assertIn("'origin/release/v1.2-test'", result.stdout)

    # 12. Invalid base blocks before invoking the adapter.
    def test_12_base_resolution_failure_prevents_invocation(self) -> None:
        marker = self.root / "should-not-exist"
        self.make_adapter(f"from pathlib import Path\nPath({str(marker)!r}).write_text('ran')\n")
        result = self.verify_fast("origin/does-not-exist", base_valid=False)
        self.assertEqual("BLOCKED_BASE_RESOLUTION", result.status)
        self.assertFalse(marker.exists())

    # 13. A changed final HEAD is captured by the required rerun.
    def test_13_remediation_commit_changes_head_and_rerun_captures_it(self) -> None:
        self.make_adapter("print('Planned/executed: 1/1')\n")
        initial = self.verify()
        (self.repo / "tracked.txt").write_text("remediated\n")
        run(["git", "add", "tracked.txt"], cwd=self.repo)
        run(["git", "commit", "-m", "remediation"], cwd=self.repo)
        final = self.verify()
        self.assertNotEqual(initial.invocation_head, final.invocation_head)
        self.assertEqual("PASS", final.status)

    # 14. Deterministic pass cannot override a failed independent audit.
    def test_14_ship_pass_but_audit_fails_still_blocks_shipment(self) -> None:
        self.make_adapter("print('Planned/executed: 1/1')\n")
        result = self.verify_fast()
        self.assertFalse(
            rv.repository_verification_allows_shipment(result, audit_eligible=False)
        )

    # 15. A failed post-remediation run blocks despite an earlier pass.
    def test_15_post_remediation_failure_blocks_shipment(self) -> None:
        state = self.root / "adapter-state"
        self.make_adapter(
            f"from pathlib import Path\nimport sys\np=Path({str(state)!r})\n"
            "code = 0 if not p.exists() else 1\np.write_text('used')\nsys.exit(code)\n"
        )
        initial = self.verify_fast()
        final = self.verify_fast()
        self.assertEqual("PASS", initial.status)
        self.assertEqual("BLOCKED_REQUIRED_CHECK", final.status)
        self.assertFalse(
            rv.repository_verification_allows_shipment(final, audit_eligible=True)
        )

    # 16. Verification machinery changes activate heightened review.
    def test_16_governance_sensitive_paths_activate(self) -> None:
        self.make_adapter("print('Planned/executed: 1/1')\n")
        result = self.verify_fast(changed_paths=["scripts/verify", "src/app.py"])
        self.assertTrue(result.governance_sensitive)
        self.assertTrue(rv.is_governance_sensitive([".github/workflows/github-minimal.yml"]))
        self.assertFalse(rv.is_governance_sensitive(["src/app.py"]))

    # 17. Exit 0 with planned != executed is a protocol blocker.
    def test_17_zero_exit_with_count_mismatch_blocks(self) -> None:
        self.make_adapter("print('Planned/executed: 19/18')\n")
        result = self.verify_fast()
        self.assertEqual("BLOCKED_PROTOCOL", result.status)
        self.assertEqual(0, result.adapter_exit_code)
        self.assertEqual(3, result.effective_exit_code)
        self.assertTrue(any("differs" in item for item in result.contradictions))

    # 18. Exit 0 explicitly reporting a blocking unavailable check blocks.
    def test_18_zero_exit_with_blocking_unavailable_blocks(self) -> None:
        self.make_adapter("print('Blocking check unavailable: browser')\n")
        result = self.verify_fast()
        self.assertEqual("BLOCKED_PROTOCOL", result.status)
        self.assertIn("blocking check unavailable", result.contradictions)

    # 19. Repository paths containing spaces execute safely.
    def test_19_repository_path_with_spaces_is_safe(self) -> None:
        self.make_adapter("import os\nprint(os.getcwd())\n")
        result = self.verify_fast()
        self.assertEqual("PASS", result.status)

        # macOS may expose the same temporary directory through both /var and
        # /private/var. Compare filesystem identity rather than lexical spelling
        # so the test verifies safe invocation without rejecting that alias.
        reported_path = Path(result.stdout.strip())
        self.assertTrue(reported_path.is_absolute())
        self.assertTrue(os.path.samefile(self.repo, reported_path))

    # 20. Base punctuation remains one argument, not shell syntax.
    def test_20_base_punctuation_has_no_argument_splitting(self) -> None:
        branch = "feature/a.b-c_1"
        self.set_remote_ref(branch)
        self.make_adapter("import sys\nprint(len(sys.argv))\nprint(sys.argv[3])\n")
        result = self.verify_fast(f"origin/{branch}")
        self.assertEqual("4", result.stdout.splitlines()[0])
        self.assertEqual(f"origin/{branch}", result.stdout.splitlines()[1])

    # 21. Large stdout and stderr are captured without pipe deadlock.
    def test_21_large_stdout_and_stderr_are_captured(self) -> None:
        self.make_adapter(
            "import sys\n"
            "sys.stdout.write('O' * 300000)\n"
            "sys.stderr.write('E' * 300000)\n"
        )
        result = self.verify_fast(timeout_seconds=10)
        self.assertEqual("PASS", result.status)
        self.assertEqual(300000, len(result.stdout))
        self.assertEqual(300000, len(result.stderr))

    # 22. Timeout terminates the adapter process group and blocks.
    def test_22_timeout_kills_child_process_group(self) -> None:
        pidfile = self.root / "child.pid"
        self.make_adapter(
            "import subprocess, time\n"
            f"p=subprocess.Popen(['sleep','60'])\nopen({str(pidfile)!r}, 'w').write(str(p.pid))\n"
            "time.sleep(60)\n"
        )
        result = self.verify_fast(timeout_seconds=2.0)
        self.assertEqual("BLOCKED_TIMEOUT", result.status)
        self.assertEqual(5, result.effective_exit_code)
        self.assertTrue(pidfile.exists())
        child_pid = int(pidfile.read_text())
        deadline = time.time() + 3
        alive = True
        while time.time() < deadline:
            probe = subprocess.run(
                ["ps", "-p", str(child_pid), "-o", "stat="],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False,
            )
            alive = probe.returncode == 0 and bool(probe.stdout.strip())
            if not alive:
                break
            time.sleep(0.1)
        self.assertFalse(alive, f"child process {child_pid} survived timeout")

    # 23. User interruption blocks and returns effective exit 5.
    def test_23_interrupt_blocks(self) -> None:
        self.make_adapter("print('adapter started')\n")

        class InterruptedProcess:
            pid = 999999
            returncode = None

            def __init__(self) -> None:
                self.calls = 0

            def communicate(self, timeout=None):
                self.calls += 1
                if self.calls == 1:
                    raise KeyboardInterrupt
                self.returncode = -signal.SIGINT
                return ("partial stdout", "interrupted stderr")

        fake = InterruptedProcess()
        heads = iter(["a" * 40, "a" * 40])
        statuses = iter([b"", b""])
        with (
            mock.patch.object(rv.subprocess, "Popen", return_value=fake),
            mock.patch.object(rv, "_terminate_process_group"),
            mock.patch.object(rv, "_git_head", side_effect=lambda _repo: next(heads)),
            mock.patch.object(rv, "_git_status", side_effect=lambda _repo: next(statuses)),
            mock.patch.object(rv, "validate_base", return_value=(True, "b" * 40)),
        ):
            result = rv.run_repository_verification(
                self.repo, "origin/main", timeout_seconds=30
            )

        self.assertEqual("BLOCKED_INTERRUPTED", result.status)
        self.assertEqual(5, result.effective_exit_code)
        self.assertTrue(result.interrupted)
        self.assertIn("partial stdout", result.stdout)
        self.assertIn("interrupted stderr", result.stderr)

    # 24. Existing merge and cleanup policy remains intact.
    def test_24_merge_and_cleanup_contract_is_preserved(self) -> None:
        policy = (SKILL_ROOT / "ci-and-merge-policy.md").read_text()
        for required in (
            "Mandatory post-merge cleanup",
            "git branch -d <branch>",
            "`-D`",
            "use admin bypass",
            "permissions permit it",
        ):
            self.assertIn(required, policy)

    # 25. Legacy repositories remain shippable under their existing gates.
    def test_25_legacy_repository_decision_remains_intact(self) -> None:
        result = self.verify_fast()
        self.assertTrue(rv.repository_verification_allows_audit(result))
        self.assertTrue(
            rv.repository_verification_allows_shipment(result, audit_eligible=True)
        )

    # Additional invalid-launcher and output-capture coverage.
    def test_26_invalid_launcher_blocks_as_adapter_defect(self) -> None:
        adapter = self.repo / "scripts" / "verify"
        adapter.parent.mkdir(parents=True)
        adapter.write_text("not a valid executable format\n")
        adapter.chmod(0o755)
        result = self.verify_fast()
        self.assertEqual("BLOCKED_ADAPTER", result.status)
        self.assertEqual(3, result.effective_exit_code)

    def test_27_reported_counts_and_stderr_are_preserved(self) -> None:
        self.make_adapter(
            "import sys\n"
            "print('planned: 5')\nprint('executed: 5')\nprint('pass: 4')\n"
            "print('failure: 0')\nprint('unavailable: 0')\nprint('advisory: 1')\n"
            "print('diagnostic stderr', file=sys.stderr)\n"
        )
        result = self.verify_fast()
        self.assertEqual("PASS", result.status)
        self.assertEqual(5, result.counts.planned)
        self.assertEqual(5, result.counts.executed)
        self.assertEqual(4, result.counts.pass_count)
        self.assertEqual(0, result.counts.failure)
        self.assertEqual(0, result.counts.unavailable)
        self.assertEqual(1, result.counts.advisory)
        self.assertIn("diagnostic stderr", result.stderr)


    def test_28_zero_exit_with_failure_count_blocks(self) -> None:
        self.make_adapter("print('planned: 2')\nprint('executed: 2')\nprint('failure: 1')\n")
        result = self.verify_fast()
        self.assertEqual("BLOCKED_PROTOCOL", result.status)
        self.assertTrue(any("failure count" in item for item in result.contradictions))

    def test_29_unsupported_nonzero_exit_is_protocol_blocker(self) -> None:
        self.make_adapter("raise SystemExit(9)\n")
        result = self.verify_fast()
        self.assertEqual("BLOCKED_PROTOCOL", result.status)
        self.assertEqual(9, result.adapter_exit_code)
        self.assertEqual(3, result.effective_exit_code)

    def test_30_adapter_tree_change_blocks_even_on_zero(self) -> None:
        self.make_adapter("from pathlib import Path\nPath('tracked.txt').write_text('changed\\n')\n")
        result = self.verify()
        self.assertEqual("BLOCKED_PROTOCOL", result.status)
        self.assertTrue(result.tree_changed)




if __name__ == "__main__":
    requested = os.environ.get("AUDIT_PR_TEST_RANGE", "all")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RepositoryVerificationTests)
    if requested != "all":
        start_text, end_text = requested.split("-", 1)
        start_number, end_number = int(start_text), int(end_text)
        filtered = unittest.TestSuite()
        for test in suite:
            method = test._testMethodName
            number = int(method.split("_", 2)[1])
            if start_number <= number <= end_number:
                filtered.addTest(test)
        suite = filtered
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
