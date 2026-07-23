#!/usr/bin/env python3
"""Validate model-selected /fix-bugs routing decisions without choosing a model."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass

ALLOWED_MODELS = {"sonnet", "opus", "fable"}
ALLOWED_RISK = {"low", "medium", "high", "critical"}
ALLOWED_COMPLEXITY = {"localized", "multi-file", "cross-module", "cross-system"}


class RoutingError(ValueError):
    """Raised when a routing record is incomplete or unsafe."""


@dataclass(frozen=True)
class RoutingDecision:
    issue: int
    selected_model: str
    risk: str
    complexity: str
    rationale: str
    alternatives_considered: tuple[str, ...]
    implementation_expected: bool = True

    @classmethod
    def from_mapping(cls, raw: dict) -> "RoutingDecision":
        alternatives = raw.get("alternatives_considered", [])
        if not isinstance(alternatives, list):
            raise RoutingError("alternatives_considered must be a list")
        return cls(
            issue=int(raw["issue"]),
            selected_model=str(raw["selected_model"]).strip().lower(),
            risk=str(raw["risk"]).strip().lower(),
            complexity=str(raw["complexity"]).strip().lower(),
            rationale=str(raw["rationale"]).strip(),
            alternatives_considered=tuple(str(item).strip().lower() for item in alternatives),
            implementation_expected=bool(raw.get("implementation_expected", True)),
        )


def validate_decision(decision: RoutingDecision) -> None:
    if decision.issue <= 0:
        raise RoutingError("issue must be a positive integer")
    if decision.selected_model not in ALLOWED_MODELS:
        raise RoutingError(
            "selected_model must be one of: sonnet, opus, fable; inherit and haiku are prohibited"
        )
    if decision.risk not in ALLOWED_RISK:
        raise RoutingError("risk must be low, medium, high, or critical")
    if decision.complexity not in ALLOWED_COMPLEXITY:
        raise RoutingError(
            "complexity must be localized, multi-file, cross-module, or cross-system"
        )
    if len(decision.rationale) < 20:
        raise RoutingError("rationale must explain why the selected model is proportionate")
    invalid_alternatives = set(decision.alternatives_considered) - ALLOWED_MODELS
    if invalid_alternatives:
        raise RoutingError(
            f"unsupported alternatives: {', '.join(sorted(invalid_alternatives))}"
        )
    if decision.selected_model in decision.alternatives_considered:
        raise RoutingError("selected model must not be listed as a rejected alternative")


def override_status(selected_model: str, override: str | None) -> str:
    value = (override or "").strip().lower()
    if not value or value == "inherit":
        return "NORMAL_RESOLUTION"
    if value == selected_model:
        return "MATCHING_ENVIRONMENT_OVERRIDE"
    return "BLOCKED_BY_ENVIRONMENT_OVERRIDE"


def dispatch_record(decision: RoutingDecision) -> dict[str, object]:
    validate_decision(decision)
    status = override_status(
        decision.selected_model, os.environ.get("CLAUDE_CODE_SUBAGENT_MODEL")
    )
    if status == "BLOCKED_BY_ENVIRONMENT_OVERRIDE":
        raise RoutingError(
            "CLAUDE_CODE_SUBAGENT_MODEL conflicts with the selected per-issue model"
        )
    return {
        "subagent_type": "bug-fix-worker",
        "model": decision.selected_model,
        "issue": decision.issue,
        "routing_status": status,
    }


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="JSON file; stdin when omitted")
    args = parser.parse_args()
    try:
        if args.input:
            with open(args.input, "r", encoding="utf-8") as handle:
                raw = json.load(handle)
        else:
            raw = json.load(__import__("sys").stdin)
        decision = RoutingDecision.from_mapping(raw)
        print(json.dumps(dispatch_record(decision), indent=2))
        return 0
    except (RoutingError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(_main())
