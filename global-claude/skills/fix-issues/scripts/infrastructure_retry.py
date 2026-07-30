#!/usr/bin/env python3
"""Bounded transient-infrastructure retry decisions for /fix-issues."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass

MAX_OPERATION_ATTEMPTS = 3
BACKOFF_SECONDS = (0, 15, 60)
RETRYABLE_HTTP = {408, 425, 429, 500, 502, 503, 504}
NONRETRYABLE_HTTP = {400, 401, 403, 404, 409, 410, 422}
RETRYABLE_EXIT_CODES = {5, 6, 7, 18, 28, 35, 52, 55, 56}
RETRYABLE_PATTERNS = (
    r"connection (?:reset|refused|closed)",
    r"temporary failure",
    r"temporarily unavailable",
    r"timed? out",
    r"timeout",
    r"tls handshake timeout",
    r"network is unreachable",
    r"could not resolve host",
    r"remote end hung up",
    r"bad gateway",
    r"service unavailable",
    r"gateway timeout",
    r"secondary rate limit",
)
NONRETRYABLE_PATTERNS = (
    r"authentication failed",
    r"bad credentials",
    r"permission denied",
    r"forbidden",
    r"not authorized",
    r"repository not found",
    r"validation failed",
    r"unprocessable entity",
    r"missing required secret",
    r"model.*mismatch",
)
READ_OPERATIONS = {
    "github_read",
    "github_queue_refresh",
    "git_fetch",
    "ci_poll",
    "remote_status",
}
MUTATION_OPERATIONS = {
    "github_comment",
    "github_issue_create",
    "git_push",
}


class InfrastructureRetryError(ValueError):
    """Raised for invalid or contradictory retry evidence."""


@dataclass(frozen=True)
class FailureEvidence:
    operation: str
    attempt: int
    http_status: int | None = None
    exit_code: int | None = None
    error_type: str | None = None
    message: str = ""
    remaining_budget_seconds: int | None = None
    mutation_reconciled_absent: bool = False


@dataclass(frozen=True)
class RetryDecision:
    action: str
    classification: str
    delay_seconds: int
    reason: str
    requires_reconciliation: bool


def _matches(patterns: tuple[str, ...], message: str) -> bool:
    lowered = message.lower()
    return any(re.search(pattern, lowered) for pattern in patterns)


def classify_failure(evidence: FailureEvidence) -> str:
    if evidence.operation not in READ_OPERATIONS | MUTATION_OPERATIONS:
        return "UNSUPPORTED_OPERATION"
    if evidence.http_status in NONRETRYABLE_HTTP:
        return "NONRETRYABLE_PROTOCOL_OR_AUTH"
    if evidence.http_status in RETRYABLE_HTTP:
        return "TRANSIENT_HTTP"
    if _matches(NONRETRYABLE_PATTERNS, evidence.message):
        return "NONRETRYABLE_AUTH_OR_POLICY"
    if evidence.exit_code in RETRYABLE_EXIT_CODES:
        return "TRANSIENT_TRANSPORT"
    if _matches(RETRYABLE_PATTERNS, evidence.message):
        return "TRANSIENT_TRANSPORT"
    if evidence.error_type and evidence.error_type.lower() in {
        "connectionerror",
        "timeouterror",
        "temporarilyunavailable",
        "ratelimited",
    }:
        return "TRANSIENT_TRANSPORT"
    return "NONRETRYABLE_OR_UNKNOWN"


def decide_retry(evidence: FailureEvidence) -> RetryDecision:
    if evidence.attempt < 1 or evidence.attempt > MAX_OPERATION_ATTEMPTS:
        raise InfrastructureRetryError(
            f"attempt must be between 1 and {MAX_OPERATION_ATTEMPTS}"
        )
    classification = classify_failure(evidence)
    mutation = evidence.operation in MUTATION_OPERATIONS

    if classification.startswith("NONRETRYABLE") or classification == "UNSUPPORTED_OPERATION":
        return RetryDecision(
            action="STOP_OPERATION",
            classification=classification,
            delay_seconds=0,
            reason="failure is not a bounded transient-infrastructure condition",
            requires_reconciliation=False,
        )
    if evidence.attempt >= MAX_OPERATION_ATTEMPTS:
        return RetryDecision(
            action="RETRIES_EXHAUSTED",
            classification=classification,
            delay_seconds=0,
            reason="maximum infrastructure attempts exhausted",
            requires_reconciliation=mutation,
        )
    if mutation and not evidence.mutation_reconciled_absent:
        return RetryDecision(
            action="RECONCILE_BEFORE_RETRY",
            classification=classification,
            delay_seconds=0,
            reason="mutation outcome must be read back before a retry can be issued",
            requires_reconciliation=True,
        )

    next_delay = BACKOFF_SECONDS[evidence.attempt]
    if (
        evidence.remaining_budget_seconds is not None
        and evidence.remaining_budget_seconds <= next_delay
    ):
        return RetryDecision(
            action="BUDGET_EXHAUSTED",
            classification=classification,
            delay_seconds=0,
            reason="per-issue budget cannot accommodate the next retry delay",
            requires_reconciliation=mutation,
        )
    return RetryDecision(
        action="RETRY_AFTER_BACKOFF",
        classification=classification,
        delay_seconds=next_delay,
        reason="bounded transient-infrastructure failure",
        requires_reconciliation=mutation,
    )


def idempotency_marker(run_id: str, issue_number: int, operation: str) -> str:
    if operation not in MUTATION_OPERATIONS:
        raise InfrastructureRetryError("idempotency markers are only for mutations")
    safe_run = re.sub(r"[^A-Za-z0-9._-]", "-", run_id)
    safe_operation = re.sub(r"[^A-Za-z0-9._-]", "-", operation)
    return f"<!-- fix-issues:{safe_run}:issue-{issue_number}:{safe_operation} -->"


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", required=True)
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--http-status", type=int)
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--error-type")
    parser.add_argument("--message", default="")
    parser.add_argument("--remaining-budget-seconds", type=int)
    parser.add_argument("--mutation-reconciled-absent", action="store_true")
    args = parser.parse_args()
    try:
        decision = decide_retry(
            FailureEvidence(
                operation=args.operation,
                attempt=args.attempt,
                http_status=args.http_status,
                exit_code=args.exit_code,
                error_type=args.error_type,
                message=args.message,
                remaining_budget_seconds=args.remaining_budget_seconds,
                mutation_reconciled_absent=args.mutation_reconciled_absent,
            )
        )
        print(json.dumps(decision.__dict__, indent=2, sort_keys=True))
        return 0
    except (InfrastructureRetryError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(_main())
