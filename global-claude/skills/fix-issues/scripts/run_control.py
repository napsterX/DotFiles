#!/usr/bin/env python3
"""Durable run journal, per-issue budget, and execution lock for /fix-issues."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = 2
DEFAULT_ISSUE_TIMEOUT_MINUTES = 60
MIN_ISSUE_TIMEOUT_MINUTES = 5
MAX_ISSUE_TIMEOUT_MINUTES = 240
LOCK_GRACE_SECONDS = 15 * 60
TERMINAL_RUN_STATUSES = {"RUN_COMPLETED", "RUN_STOPPED", "FINALIZATION_BLOCKED"}
ALLOWED_EVENTS = {
    "RUN_CREATED",
    "LOCK_ACQUIRED",
    "QUEUE_SELECTED",
    "ISSUE_STARTED",
    "ATTEMPT_STARTED",
    "ATTEMPT_FINISHED",
    "CANDIDATE_ACCEPTED",
    "CANDIDATE_REJECTED",
    "ISSUE_COMMITTED",
    "ISSUE_ALREADY_RESOLVED",
    "ISSUE_INVALID",
    "ISSUE_DUPLICATE",
    "ISSUE_BLOCKED",
    "ISSUE_FAILED",
    "ISSUE_TIMED_OUT",
    "QUEUE_REFRESHED",
    "CUMULATIVE_VERIFICATION_STARTED",
    "CUMULATIVE_VERIFICATION_FINISHED",
    "FINALIZATION_STARTED",
    "FINALIZATION_FINISHED",
    "RUN_COMPLETED",
    "RUN_STOPPED",
    "FINALIZATION_BLOCKED",
    "NOTIFICATION_ATTEMPTED",
    "LOCK_RELEASED",
}


class RunControlError(ValueError):
    """Raised when durable run state is invalid or unsafe."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_utc(value: str) -> datetime:
    candidate = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(candidate)
    if parsed.tzinfo is None:
        raise RunControlError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_path(path: str | Path) -> str:
    return str(Path(path).expanduser().resolve())


def _safe_slug(value: str, maximum: int = 48) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._")
    return (slug or "unnamed")[:maximum]


def repository_key(repository_root: str | Path, git_common_dir: str | Path) -> str:
    root = _canonical_path(repository_root)
    common = _canonical_path(git_common_dir)
    digest = hashlib.sha256(f"{root}\0{common}".encode("utf-8")).hexdigest()[:12]
    return f"{_safe_slug(Path(root).name)}-{digest}"


def lock_key(
    repository_root: str | Path,
    git_common_dir: str | Path,
    task_root: str | Path,
    branch: str,
) -> str:
    values = (
        _canonical_path(repository_root),
        _canonical_path(git_common_dir),
        _canonical_path(task_root),
        branch,
    )
    digest = hashlib.sha256("\0".join(values).encode("utf-8")).hexdigest()[:16]
    return f"{_safe_slug(Path(values[0]).name)}-{_safe_slug(branch, 28)}-{digest}"


def validate_timeout_minutes(value: int) -> int:
    if value < MIN_ISSUE_TIMEOUT_MINUTES or value > MAX_ISSUE_TIMEOUT_MINUTES:
        raise RunControlError(
            "issue timeout must be between "
            f"{MIN_ISSUE_TIMEOUT_MINUTES} and {MAX_ISSUE_TIMEOUT_MINUTES} minutes"
        )
    return value


def issue_deadline(started_at: str | datetime, timeout_minutes: int) -> datetime:
    validate_timeout_minutes(timeout_minutes)
    start = parse_utc(started_at) if isinstance(started_at, str) else started_at
    if start.tzinfo is None:
        raise RunControlError("issue start time must include a timezone")
    return start.astimezone(timezone.utc) + timedelta(minutes=timeout_minutes)


@dataclass(frozen=True)
class BudgetDecision:
    status: str
    elapsed_seconds: int
    remaining_seconds: int
    deadline: str


def budget_decision(
    started_at: str | datetime,
    timeout_minutes: int = DEFAULT_ISSUE_TIMEOUT_MINUTES,
    now: str | datetime | None = None,
) -> BudgetDecision:
    start = parse_utc(started_at) if isinstance(started_at, str) else started_at
    if start.tzinfo is None:
        raise RunControlError("issue start time must include a timezone")
    current = utc_now() if now is None else (parse_utc(now) if isinstance(now, str) else now)
    if current.tzinfo is None:
        raise RunControlError("current time must include a timezone")
    deadline = issue_deadline(start, timeout_minutes)
    elapsed = max(0, int((current - start).total_seconds()))
    remaining = max(0, int((deadline - current).total_seconds()))
    return BudgetDecision(
        status="EXPIRED" if current >= deadline else "ACTIVE",
        elapsed_seconds=elapsed,
        remaining_seconds=remaining,
        deadline=format_utc(deadline),
    )


def _fsync_directory(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        _fsync_directory(path.parent)
    finally:
        temporary_path.unlink(missing_ok=True)


def load_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RunControlError(f"unable to read valid JSON from {path}") from exc
    if not isinstance(raw, dict):
        raise RunControlError(f"expected JSON object in {path}")
    return raw


class RunJournal:
    """Atomic current state plus fsync'd append-only transition evidence."""

    def __init__(self, run_dir: str | Path):
        self.run_dir = Path(run_dir).expanduser().resolve()
        self.state_path = self.run_dir / "run-state.json"
        self.events_path = self.run_dir / "events.jsonl"

    @classmethod
    def create(
        cls,
        runs_root: str | Path,
        *,
        repository_root: str | Path,
        git_common_dir: str | Path,
        task_root: str | Path,
        repository_identifier: str,
        branch: str,
        starting_head: str,
        requested_maximum: int,
        issue_timeout_minutes: int = DEFAULT_ISSUE_TIMEOUT_MINUTES,
        run_id: str | None = None,
        created_at: datetime | None = None,
    ) -> "RunJournal":
        timeout = validate_timeout_minutes(issue_timeout_minutes)
        key = repository_key(repository_root, git_common_dir)
        identifier = run_id or f"{utc_now().strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(4)}"
        journal = cls(Path(runs_root).expanduser() / key / identifier)
        if journal.run_dir.exists():
            raise RunControlError(f"run already exists: {journal.run_dir}")
        journal.run_dir.mkdir(parents=True, exist_ok=False)
        timestamp = created_at or utc_now()
        state: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "run_id": identifier,
            "repository_key": key,
            "repository_root": _canonical_path(repository_root),
            "git_common_dir": _canonical_path(git_common_dir),
            "task_root": _canonical_path(task_root),
            "repository_identifier": repository_identifier,
            "branch": branch,
            "starting_head": starting_head,
            "current_head": starting_head,
            "requested_maximum": requested_maximum,
            "issue_timeout_minutes": timeout,
            "status": "RUN_CREATED",
            "sequence": 0,
            "current_issue": None,
            "selected_issues": [],
            "outcomes": [],
            "fixed_commits": [],
            "created_at": format_utc(timestamp),
            "updated_at": format_utc(timestamp),
            "last_event_sha256": None,
        }
        atomic_write_json(journal.state_path, state)
        journal.checkpoint("RUN_CREATED", {"starting_head": starting_head}, now=timestamp)
        return journal

    def state(self) -> dict[str, Any]:
        return load_json(self.state_path)

    def checkpoint(
        self,
        event: str,
        payload: Mapping[str, Any] | None = None,
        *,
        now: datetime | None = None,
        state_updates: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if event not in ALLOWED_EVENTS:
            raise RunControlError(f"unsupported run event: {event}")
        state = self.state()
        if state.get("status") in TERMINAL_RUN_STATUSES and event not in {
            "NOTIFICATION_ATTEMPTED",
            "LOCK_RELEASED",
        }:
            raise RunControlError("terminal run cannot accept non-cleanup transitions")
        timestamp = now or utc_now()
        sequence = int(state.get("sequence", 0)) + 1
        event_record: dict[str, Any] = {
            "sequence": sequence,
            "event": event,
            "timestamp": format_utc(timestamp),
            "payload": dict(payload or {}),
            "previous_event_sha256": state.get("last_event_sha256"),
        }
        canonical = json.dumps(event_record, sort_keys=True, separators=(",", ":"))
        event_record["event_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event_record, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        state["sequence"] = sequence
        previous_status = state.get("status")
        if previous_status not in TERMINAL_RUN_STATUSES:
            state["status"] = event
        state["last_event"] = event
        state["updated_at"] = event_record["timestamp"]
        state["last_event_sha256"] = event_record["event_sha256"]
        for key, value in dict(state_updates or {}).items():
            state[key] = value
        atomic_write_json(self.state_path, state)
        return state

    def validate_resume(
        self,
        *,
        repository_root: str | Path,
        git_common_dir: str | Path,
        task_root: str | Path,
        branch: str,
        current_head: str,
        worktree_clean: bool,
    ) -> str:
        state = self.state()
        if state.get("status") in TERMINAL_RUN_STATUSES:
            return "RESUME_NOT_APPLICABLE_TERMINAL"
        comparisons = {
            "repository_root": _canonical_path(repository_root),
            "git_common_dir": _canonical_path(git_common_dir),
            "task_root": _canonical_path(task_root),
            "branch": branch,
            "current_head": current_head,
        }
        for field, actual in comparisons.items():
            if state.get(field) != actual:
                if field == "current_head" and state.get("status") == "CANDIDATE_ACCEPTED":
                    return "RESUME_RECONCILE_PENDING_COMMIT"
                return f"RESUME_BLOCKED_{field.upper()}_MISMATCH"
        if state.get("status") == "CANDIDATE_ACCEPTED":
            return "RESUME_RECONCILE_ACCEPTED_CANDIDATE"
        if worktree_clean:
            return "RESUME_READY"
        if state.get("status") in {"ATTEMPT_STARTED", "ATTEMPT_FINISHED", "CANDIDATE_REJECTED"}:
            return "RESUME_RECOVER_INTERRUPTED_ISSUE"
        return "RESUME_BLOCKED_DIRTY_WORKTREE"


class RunLock:
    """Atomic lease lock keyed by repository family, worktree, and branch."""

    def __init__(self, lock_dir: str | Path):
        self.lock_dir = Path(lock_dir).expanduser().resolve()
        self.owner_path = self.lock_dir / "owner.json"

    def inspect(self, now: datetime | None = None) -> tuple[str, dict[str, Any] | None]:
        if not self.lock_dir.exists():
            return "ABSENT", None
        owner = load_json(self.owner_path)
        current = now or utc_now()
        expires_at = parse_utc(str(owner["lease_expires_at"]))
        return ("STALE" if current >= expires_at else "ACTIVE"), owner

    def acquire(
        self,
        *,
        run_id: str,
        session_id: str,
        lease_seconds: int,
        now: datetime | None = None,
        reclaim_stale: bool = False,
    ) -> str:
        if lease_seconds <= 0:
            raise RunControlError("lease_seconds must be positive")
        current = now or utc_now()
        try:
            self.lock_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            status, owner = self.inspect(current)
            if owner and owner.get("run_id") == run_id:
                self.heartbeat(run_id=run_id, lease_seconds=lease_seconds, now=current)
                return "REACQUIRED_SAME_RUN"
            if status == "STALE" and reclaim_stale:
                archived = self.lock_dir.with_name(
                    f"{self.lock_dir.name}.stale-{current.strftime('%Y%m%dT%H%M%SZ')}"
                )
                os.replace(self.lock_dir, archived)
                self.lock_dir.mkdir(parents=True, exist_ok=False)
            else:
                return "BLOCKED_ACTIVE_LOCK" if status == "ACTIVE" else "BLOCKED_STALE_LOCK"
        owner = {
            "run_id": run_id,
            "session_id": session_id,
            "acquired_at": format_utc(current),
            "heartbeat_at": format_utc(current),
            "lease_expires_at": format_utc(current + timedelta(seconds=lease_seconds)),
        }
        atomic_write_json(self.owner_path, owner)
        return "ACQUIRED"

    def heartbeat(
        self,
        *,
        run_id: str,
        lease_seconds: int,
        now: datetime | None = None,
    ) -> None:
        owner = load_json(self.owner_path)
        if owner.get("run_id") != run_id:
            raise RunControlError("lock owner does not match run")
        current = now or utc_now()
        owner["heartbeat_at"] = format_utc(current)
        owner["lease_expires_at"] = format_utc(current + timedelta(seconds=lease_seconds))
        atomic_write_json(self.owner_path, owner)

    def release(self, *, run_id: str) -> str:
        if not self.lock_dir.exists():
            return "ALREADY_RELEASED"
        owner = load_json(self.owner_path)
        if owner.get("run_id") != run_id:
            raise RunControlError("cannot release a lock owned by another run")
        shutil.rmtree(self.lock_dir)
        _fsync_directory(self.lock_dir.parent)
        return "RELEASED"


def default_lock_lease_seconds(issue_timeout_minutes: int) -> int:
    validate_timeout_minutes(issue_timeout_minutes)
    return issue_timeout_minutes * 60 + LOCK_GRACE_SECONDS


def _main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    budget = sub.add_parser("budget")
    budget.add_argument("--started-at", required=True)
    budget.add_argument("--timeout-minutes", type=int, default=DEFAULT_ISSUE_TIMEOUT_MINUTES)
    budget.add_argument("--now")

    resume = sub.add_parser("resume-check")
    resume.add_argument("--run-dir", required=True)
    resume.add_argument("--repository-root", required=True)
    resume.add_argument("--git-common-dir", required=True)
    resume.add_argument("--task-root", required=True)
    resume.add_argument("--branch", required=True)
    resume.add_argument("--current-head", required=True)
    resume.add_argument("--worktree-clean", action="store_true")

    args = parser.parse_args()
    try:
        if args.command == "budget":
            decision = budget_decision(args.started_at, args.timeout_minutes, args.now)
            print(json.dumps(decision.__dict__, indent=2, sort_keys=True))
        else:
            result = RunJournal(args.run_dir).validate_resume(
                repository_root=args.repository_root,
                git_common_dir=args.git_common_dir,
                task_root=args.task_root,
                branch=args.branch,
                current_head=args.current_head,
                worktree_clean=args.worktree_clean,
            )
            print(result)
        return 0
    except (RunControlError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(_main())
