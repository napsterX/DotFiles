#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_control.py"
spec = importlib.util.spec_from_file_location("run_control", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class RunControlTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fix issues runtime ")
        self.root = Path(self.temp.name)
        self.repo = self.root / "repository with spaces"
        self.common = self.root / "common.git"
        self.task = self.root / "task worktree"
        for path in (self.repo, self.common, self.task):
            path.mkdir()
        self.now = datetime(2026, 7, 30, 4, 0, tzinfo=timezone.utc)

    def tearDown(self):
        self.temp.cleanup()

    def create_journal(self):
        return module.RunJournal.create(
            self.root / "runs",
            repository_root=self.repo,
            git_common_dir=self.common,
            task_root=self.task,
            repository_identifier="owner/repo",
            branch="issue/bounded-run",
            starting_head="a" * 40,
            requested_maximum=10,
            issue_timeout_minutes=60,
            run_id="run-123",
            created_at=self.now,
        )

    def test_01_default_budget_is_active_before_sixty_minutes(self):
        result = module.budget_decision(
            module.format_utc(self.now), now=self.now + timedelta(minutes=59, seconds=59)
        )
        self.assertEqual("ACTIVE", result.status)
        self.assertEqual(1, result.remaining_seconds)

    def test_02_budget_expires_at_sixty_minutes(self):
        result = module.budget_decision(
            module.format_utc(self.now), now=self.now + timedelta(minutes=60)
        )
        self.assertEqual("EXPIRED", result.status)
        self.assertEqual(0, result.remaining_seconds)

    def test_03_timeout_bounds_are_enforced(self):
        with self.assertRaises(module.RunControlError):
            module.validate_timeout_minutes(4)
        with self.assertRaises(module.RunControlError):
            module.validate_timeout_minutes(241)

    def test_04_journal_is_atomic_and_append_only(self):
        journal = self.create_journal()
        journal.checkpoint(
            "QUEUE_SELECTED",
            {"issues": [12, 13]},
            now=self.now + timedelta(seconds=1),
            state_updates={"selected_issues": [12, 13]},
        )
        state = journal.state()
        self.assertEqual(2, state["sequence"])
        self.assertEqual([12, 13], state["selected_issues"])
        events = [json.loads(line) for line in journal.events_path.read_text().splitlines()]
        self.assertEqual(["RUN_CREATED", "QUEUE_SELECTED"], [e["event"] for e in events])
        self.assertEqual(events[0]["event_sha256"], events[1]["previous_event_sha256"])

    def test_05_terminal_journal_rejects_new_work(self):
        journal = self.create_journal()
        journal.checkpoint("RUN_COMPLETED", now=self.now + timedelta(seconds=1))
        with self.assertRaises(module.RunControlError):
            journal.checkpoint("ISSUE_STARTED", {"issue": 1})

    def test_06_resume_ready_when_identity_head_and_tree_match(self):
        journal = self.create_journal()
        result = journal.validate_resume(
            repository_root=self.repo,
            git_common_dir=self.common,
            task_root=self.task,
            branch="issue/bounded-run",
            current_head="a" * 40,
            worktree_clean=True,
        )
        self.assertEqual("RESUME_READY", result)

    def test_07_resume_blocks_head_mismatch(self):
        journal = self.create_journal()
        result = journal.validate_resume(
            repository_root=self.repo,
            git_common_dir=self.common,
            task_root=self.task,
            branch="issue/bounded-run",
            current_head="b" * 40,
            worktree_clean=True,
        )
        self.assertEqual("RESUME_BLOCKED_CURRENT_HEAD_MISMATCH", result)

    def test_08_interrupted_attempt_with_dirty_tree_is_recoverable_not_silently_resumed(self):
        journal = self.create_journal()
        journal.checkpoint("ISSUE_STARTED", {"issue": 7})
        journal.checkpoint("ATTEMPT_STARTED", {"issue": 7, "attempt": 1})
        result = journal.validate_resume(
            repository_root=self.repo,
            git_common_dir=self.common,
            task_root=self.task,
            branch="issue/bounded-run",
            current_head="a" * 40,
            worktree_clean=False,
        )
        self.assertEqual("RESUME_RECOVER_INTERRUPTED_ISSUE", result)

    def test_09_lock_blocks_second_run(self):
        lock = module.RunLock(self.root / "locks" / "repo.lock")
        self.assertEqual(
            "ACQUIRED",
            lock.acquire(run_id="run-1", session_id="session-1", lease_seconds=4500, now=self.now),
        )
        self.assertEqual(
            "BLOCKED_ACTIVE_LOCK",
            lock.acquire(run_id="run-2", session_id="session-2", lease_seconds=4500, now=self.now),
        )

    def test_10_same_run_can_reacquire_and_renew(self):
        lock = module.RunLock(self.root / "locks" / "repo.lock")
        lock.acquire(run_id="run-1", session_id="session-1", lease_seconds=100, now=self.now)
        result = lock.acquire(
            run_id="run-1",
            session_id="session-1",
            lease_seconds=200,
            now=self.now + timedelta(seconds=10),
        )
        self.assertEqual("REACQUIRED_SAME_RUN", result)
        owner = module.load_json(lock.owner_path)
        self.assertEqual(
            module.format_utc(self.now + timedelta(seconds=210)), owner["lease_expires_at"]
        )

    def test_11_stale_lock_requires_explicit_reclaim(self):
        lock = module.RunLock(self.root / "locks" / "repo.lock")
        lock.acquire(run_id="run-1", session_id="session-1", lease_seconds=10, now=self.now)
        later = self.now + timedelta(seconds=11)
        self.assertEqual(
            "BLOCKED_STALE_LOCK",
            lock.acquire(run_id="run-2", session_id="session-2", lease_seconds=100, now=later),
        )
        self.assertEqual(
            "ACQUIRED",
            lock.acquire(
                run_id="run-2",
                session_id="session-2",
                lease_seconds=100,
                now=later,
                reclaim_stale=True,
            ),
        )

    def test_12_only_owner_can_release_lock(self):
        lock = module.RunLock(self.root / "locks" / "repo.lock")
        lock.acquire(run_id="run-1", session_id="session-1", lease_seconds=100, now=self.now)
        with self.assertRaises(module.RunControlError):
            lock.release(run_id="run-2")
        self.assertEqual("RELEASED", lock.release(run_id="run-1"))

    def test_13_lock_key_includes_worktree_and_branch(self):
        first = module.lock_key(self.repo, self.common, self.task, "issue/a")
        second = module.lock_key(self.repo, self.common, self.task, "issue/b")
        third = module.lock_key(self.repo, self.common, self.root / "other", "issue/a")
        self.assertNotEqual(first, second)
        self.assertNotEqual(first, third)

    def test_14_default_lease_covers_issue_budget_plus_grace(self):
        self.assertEqual(4500, module.default_lock_lease_seconds(60))

    def test_15_cleanup_events_do_not_erase_terminal_status(self):
        journal = self.create_journal()
        journal.checkpoint("RUN_COMPLETED", now=self.now + timedelta(seconds=1))
        journal.checkpoint("NOTIFICATION_ATTEMPTED", {"status": "DELIVERED"})
        state = journal.state()
        self.assertEqual("RUN_COMPLETED", state["status"])
        self.assertEqual("NOTIFICATION_ATTEMPTED", state["last_event"])
        with self.assertRaises(module.RunControlError):
            journal.checkpoint("ISSUE_STARTED", {"issue": 2})

    def test_16_crash_after_acceptance_before_commit_requires_reconciliation(self):
        journal = self.create_journal()
        journal.checkpoint("CANDIDATE_ACCEPTED", {"issue": 7})
        result = journal.validate_resume(
            repository_root=self.repo,
            git_common_dir=self.common,
            task_root=self.task,
            branch="issue/bounded-run",
            current_head="a" * 40,
            worktree_clean=True,
        )
        self.assertEqual("RESUME_RECONCILE_ACCEPTED_CANDIDATE", result)

    def test_17_crash_after_commit_before_journal_update_requires_commit_reconciliation(self):
        journal = self.create_journal()
        journal.checkpoint("CANDIDATE_ACCEPTED", {"issue": 7})
        result = journal.validate_resume(
            repository_root=self.repo,
            git_common_dir=self.common,
            task_root=self.task,
            branch="issue/bounded-run",
            current_head="b" * 40,
            worktree_clean=True,
        )
        self.assertEqual("RESUME_RECONCILE_PENDING_COMMIT", result)


if __name__ == "__main__":
    unittest.main()
