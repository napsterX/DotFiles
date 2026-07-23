#!/usr/bin/env python3
"""Deterministic contracts for /fix-bugs argument and queue handling."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Sequence

DEFAULT_MAXIMUM = 1
MAXIMUM_CAP = 10
PROCESSED_STATUSES = {
    "fixed",
    "already_resolved",
    "invalid",
    "duplicate",
    "blocked",
    "failed",
}

BUG_LABELS = {"bug", "type:bug", "type/bug", "kind:bug"}
P2_LABELS = {"p2", "priority:p2", "priority/p2"}
P3_LABELS = {"p3", "priority:p3", "priority/p3"}
DUPLICATE_LABELS = {"duplicate", "status:duplicate", "status/duplicate"}
INVALID_LABELS = {"invalid", "status:invalid", "status/invalid"}


class ContractError(ValueError):
    """Raised when an invocation or issue violates the deterministic contract."""


def parse_maximum(arguments: Sequence[str]) -> int:
    if len(arguments) == 0:
        return DEFAULT_MAXIMUM
    if len(arguments) != 1:
        raise ContractError("expected at most one maximum_issue_count argument")

    raw = arguments[0]
    if not raw.isascii() or not raw.isdigit():
        raise ContractError("maximum_issue_count must be a positive integer")

    value = int(raw)
    if value == 0:
        raise ContractError("maximum_issue_count must be greater than zero")
    if value > MAXIMUM_CAP:
        raise ContractError(
            f"maximum_issue_count exceeds the supported cap of {MAXIMUM_CAP}"
        )
    return value


def normalize_label(label: str) -> str:
    return "".join(label.strip().lower().split())


def normalized_labels(labels: Iterable[str]) -> set[str]:
    return {normalize_label(label) for label in labels}


def classify_priority(labels: Iterable[str]) -> str | None:
    values = normalized_labels(labels)
    has_p2 = bool(values & P2_LABELS)
    has_p3 = bool(values & P3_LABELS)
    if has_p2 and has_p3:
        raise ContractError("issue has conflicting P2 and P3 labels")
    if has_p2:
        return "P2"
    if has_p3:
        return "P3"
    return None


@dataclass(frozen=True)
class Issue:
    number: int
    title: str
    state: str
    labels: tuple[str, ...]
    created_at: str

    @classmethod
    def from_mapping(cls, raw: dict) -> "Issue":
        labels = raw.get("labels", [])
        parsed_labels: list[str] = []
        for label in labels:
            if isinstance(label, str):
                parsed_labels.append(label)
            elif isinstance(label, dict) and isinstance(label.get("name"), str):
                parsed_labels.append(label["name"])
            else:
                raise ContractError("unsupported label representation")
        return cls(
            number=int(raw["number"]),
            title=str(raw.get("title", "")),
            state=str(raw.get("state", "")),
            labels=tuple(parsed_labels),
            created_at=str(raw.get("createdAt", raw.get("created_at", ""))),
        )


def is_eligible(issue: Issue) -> bool:
    if issue.state.strip().lower() != "open":
        return False
    values = normalized_labels(issue.labels)
    if not values & BUG_LABELS:
        return False
    if values & (DUPLICATE_LABELS | INVALID_LABELS):
        return False
    return classify_priority(issue.labels) in {"P2", "P3"}


def _parse_created_at(value: str) -> datetime:
    candidate = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ContractError(f"invalid issue created_at value: {value!r}") from exc


def select_queue(issues: Iterable[Issue], maximum: int) -> list[Issue]:
    if maximum < 1 or maximum > MAXIMUM_CAP:
        raise ContractError(f"maximum must be between 1 and {MAXIMUM_CAP}")
    eligible = [issue for issue in issues if is_eligible(issue)]
    eligible.sort(
        key=lambda issue: (
            0 if classify_priority(issue.labels) == "P2" else 1,
            _parse_created_at(issue.created_at),
            issue.number,
        )
    )
    return eligible[:maximum]


def consumes_slot(status: str) -> bool:
    return status in PROCESSED_STATUSES


def _main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    args_parser = subparsers.add_parser("validate-args")
    args_parser.add_argument("arguments", nargs="*")

    queue_parser = subparsers.add_parser("select-queue")
    queue_parser.add_argument("--maximum", type=int, required=True)

    parsed = parser.parse_args()
    try:
        if parsed.command == "validate-args":
            print(parse_maximum(parsed.arguments))
            return 0

        payload = json.load(__import__("sys").stdin)
        if not isinstance(payload, list):
            raise ContractError("queue input must be a JSON array")
        issues = [Issue.from_mapping(item) for item in payload]
        selected = select_queue(issues, parsed.maximum)
        print(
            json.dumps(
                [
                    {
                        "number": issue.number,
                        "title": issue.title,
                        "priority": classify_priority(issue.labels),
                        "created_at": issue.created_at,
                    }
                    for issue in selected
                ],
                indent=2,
            )
        )
        return 0
    except (ContractError, KeyError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(_main())
