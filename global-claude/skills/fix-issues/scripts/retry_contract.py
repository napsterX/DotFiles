#!/usr/bin/env python3
"""Deterministic retry and finalization decisions for /fix-issues."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

MAX_ATTEMPTS = 3
FINAL_ATTEMPT_STATUSES = {
    "candidate_ready",
    "already_resolved",
    "invalid",
    "duplicate",
    "blocked",
    "retryable_failed",
    "terminal_failed",
}


class RetryError(ValueError):
    """Raised when retry evidence is incomplete or contradictory."""


@dataclass(frozen=True)
class RetryState:
    attempt: int
    attempt_status: str
    repository_safe: bool
    head_unchanged: bool
    worktree_attributable: bool
    material_new_plan: bool = False
    acceptance_passed: bool = False
    at_least_one_fix: bool = False
    cumulative_safe: bool = False


def decide_attempt(state: RetryState) -> str:
    if state.attempt < 1 or state.attempt > MAX_ATTEMPTS:
        raise RetryError(f"attempt must be between 1 and {MAX_ATTEMPTS}")
    if state.attempt_status not in FINAL_ATTEMPT_STATUSES:
        raise RetryError(f"unsupported attempt_status: {state.attempt_status}")
    if not (state.repository_safe and state.head_unchanged and state.worktree_attributable):
        return "STOP_BATCH_UNSAFE_STATE"

    if state.attempt_status == "candidate_ready":
        return "COMMIT" if state.acceptance_passed else (
            "RETRY" if state.attempt < MAX_ATTEMPTS and state.material_new_plan else "FAIL_ISSUE"
        )
    if state.attempt_status == "retryable_failed":
        if state.attempt >= MAX_ATTEMPTS:
            return "FAIL_ISSUE_ATTEMPTS_EXHAUSTED"
        if not state.material_new_plan:
            return "FAIL_ISSUE_NO_PROGRESS"
        return "RETRY"
    if state.attempt_status in {
        "already_resolved", "invalid", "duplicate", "blocked", "terminal_failed"
    }:
        return "FINALIZE_ISSUE"
    raise RetryError("unreachable attempt status")


def decide_finalization(at_least_one_fix: bool, cumulative_safe: bool) -> str:
    if not at_least_one_fix:
        return "NOT_APPLICABLE_NO_FIXES"
    if not cumulative_safe:
        return "FINALIZATION_BLOCKED"
    return "INVOKE_AUDIT_AND_PR"


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("attempt", "finalization"), required=True)
    args = parser.parse_args()
    try:
        raw = json.load(__import__("sys").stdin)
        if args.mode == "attempt":
            state = RetryState(
                attempt=int(raw["attempt"]),
                attempt_status=str(raw["attempt_status"]),
                repository_safe=bool(raw["repository_safe"]),
                head_unchanged=bool(raw["head_unchanged"]),
                worktree_attributable=bool(raw["worktree_attributable"]),
                material_new_plan=bool(raw.get("material_new_plan", False)),
                acceptance_passed=bool(raw.get("acceptance_passed", False)),
            )
            print(decide_attempt(state))
        else:
            print(
                decide_finalization(
                    bool(raw.get("at_least_one_fix", False)),
                    bool(raw.get("cumulative_safe", False)),
                )
            )
        return 0
    except (RetryError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(_main())
