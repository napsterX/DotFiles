#!/usr/bin/env python3
"""Validate /fix-issues finalization manifests for /audit-and-pr."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class DelegationError(ValueError):
    """Raised when delegated finalization is stale, malformed, or unauthorized."""


def _require_sha(value: object, field: str) -> str:
    text = str(value).strip().lower()
    if not SHA_RE.fullmatch(text):
        raise DelegationError(f"{field} must be a full 40-character Git SHA")
    return text


def validate_manifest(
    raw: dict,
    *,
    current_repository: str | None = None,
    current_branch: str | None = None,
    current_head: str | None = None,
) -> dict[str, object]:
    schema_version = int(raw.get("schema_version", 0))
    if schema_version not in {1, 2}:
        raise DelegationError("schema_version must be 1 or 2")
    if raw.get("source_skill") != "fix-issues":
        raise DelegationError("source_skill must be fix-issues")
    if raw.get("request") != "audit-and-pr-finalization":
        raise DelegationError("request must be audit-and-pr-finalization")

    repository = Path(str(raw.get("repository_root", ""))).expanduser()
    if schema_version == 2:
        run_id = str(raw.get("run_id", "")).strip()
        journal_path = Path(str(raw.get("run_journal", ""))).expanduser()
        task_worktree = Path(str(raw.get("task_worktree", ""))).expanduser()
        git_common_dir = Path(str(raw.get("git_common_dir", ""))).expanduser()
        if not run_id or any(ch in run_id for ch in "\n\r\0"):
            raise DelegationError("schema 2 run_id is missing or invalid")
        if not journal_path.is_absolute():
            raise DelegationError("schema 2 run_journal must be absolute")
        if not task_worktree.is_absolute() or not git_common_dir.is_absolute():
            raise DelegationError("schema 2 task_worktree and git_common_dir must be absolute")
    if not repository.is_absolute():
        raise DelegationError("repository_root must be absolute")
    branch = str(raw.get("branch", "")).strip()
    if not branch or any(ch in branch for ch in "\n\r\0"):
        raise DelegationError("branch is missing or invalid")

    starting_head = _require_sha(raw.get("starting_head"), "starting_head")
    ending_head = _require_sha(raw.get("ending_head"), "ending_head")
    fixed = raw.get("fixed_issues")
    outcomes = raw.get("outcomes")
    verification = raw.get("cumulative_verification")
    if not isinstance(fixed, list) or not fixed:
        raise DelegationError("fixed_issues must contain at least one issue")
    if not isinstance(outcomes, list) or not outcomes:
        raise DelegationError("outcomes must be a non-empty list")
    if not isinstance(verification, dict):
        raise DelegationError("cumulative_verification must be an object")

    issue_numbers: set[int] = set()
    commit_shas: set[str] = set()
    normalized_fixed: list[dict[str, object]] = []
    for item in fixed:
        if not isinstance(item, dict):
            raise DelegationError("fixed_issues entries must be objects")
        number = int(item.get("number", 0))
        if number <= 0 or number in issue_numbers:
            raise DelegationError("fixed issue numbers must be positive and unique")
        commit = _require_sha(item.get("commit_sha"), "fixed_issues.commit_sha")
        if commit in commit_shas:
            raise DelegationError("fixed issue commit SHAs must be unique")
        issue_numbers.add(number)
        commit_shas.add(commit)
        normalized_fixed.append({"number": number, "commit_sha": commit})

    outcome_numbers: set[int] = set()
    for item in outcomes:
        if not isinstance(item, dict):
            raise DelegationError("outcomes entries must be objects")
        number = int(item.get("number", 0))
        status = str(item.get("status", "")).strip()
        if number <= 0 or number in outcome_numbers or not status:
            raise DelegationError("outcome issue numbers must be unique and status required")
        outcome_numbers.add(number)
    if not issue_numbers.issubset(outcome_numbers):
        raise DelegationError("every fixed issue must appear in outcomes")

    if current_repository is not None:
        current_path = Path(current_repository).expanduser()
        try:
            same = os.path.samefile(repository, current_path)
        except FileNotFoundError as exc:
            raise DelegationError("repository path does not exist") from exc
        if not same:
            raise DelegationError("manifest repository does not match TASK_ROOT")
    if current_branch is not None and branch != current_branch:
        raise DelegationError("manifest branch does not match live branch")
    if current_head is not None and ending_head != _require_sha(current_head, "current_head"):
        raise DelegationError("manifest ending_head does not match live HEAD")

    result = {
        "status": "VALID",
        "schema_version": schema_version,
        "source_skill": "fix-issues",
        "repository_root": str(repository.resolve()),
        "branch": branch,
        "starting_head": starting_head,
        "ending_head": ending_head,
        "fixed_issues": normalized_fixed,
        "fixed_count": len(normalized_fixed),
    }
    if schema_version == 2:
        result.update({
            "run_id": run_id,
            "run_journal": str(journal_path.resolve()),
            "task_worktree": str(task_worktree.resolve()),
            "git_common_dir": str(git_common_dir.resolve()),
        })
    return result


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--current-repository")
    parser.add_argument("--current-branch")
    parser.add_argument("--current-head")
    args = parser.parse_args()
    try:
        raw = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = validate_manifest(
            raw,
            current_repository=args.current_repository,
            current_branch=args.current_branch,
            current_head=args.current_head,
        )
        print(json.dumps(result, indent=2))
        return 0
    except (DelegationError, OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(_main())
