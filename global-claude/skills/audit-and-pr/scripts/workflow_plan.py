#!/usr/bin/env python3
"""Executable reference for /audit-and-pr verification sequencing.

This helper describes required stage order. It does not execute repository
commands. It preserves the normal final-green flow and the narrow,
evidence-bound BASELINE_RESTORATION comparison flow.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Literal

AdapterState = Literal["ABSENT", "VALID", "INVALID"]
OperatingMode = Literal["NORMAL", "BASELINE_RESTORATION"]


@dataclass(frozen=True)
class WorkflowInputs:
    adapter_state: AdapterState = "VALID"
    operating_mode: OperatingMode = "NORMAL"
    run_fast_preflight: bool = True
    remediation_changed_tracked_files: bool = False
    remediation_invalidates_preflight: bool = False
    remediation_affects_baseline_comparison: bool = False
    governance_sensitive: bool = False
    final_scope_committed: bool = False


@dataclass(frozen=True)
class WorkflowPlan:
    pre_audit_steps: tuple[str, ...]
    remediation_steps: tuple[str, ...]
    final_steps: tuple[str, ...]
    blocked_before_audit: bool
    initial_ship_required: bool
    remediation_ship_required: bool
    final_ship_required: bool
    baseline_comparison_required: bool

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def build_workflow_plan(inputs: WorkflowInputs) -> WorkflowPlan:
    if inputs.adapter_state == "INVALID":
        return WorkflowPlan(
            pre_audit_steps=("block_invalid_adapter",),
            remediation_steps=(),
            final_steps=(),
            blocked_before_audit=True,
            initial_ship_required=False,
            remediation_ship_required=False,
            final_ship_required=False,
            baseline_comparison_required=False,
        )

    if inputs.adapter_state == "ABSENT":
        pre_audit = ["legacy_validation_discovery"]
        if inputs.operating_mode == "BASELINE_RESTORATION":
            pre_audit.extend(
                [
                    "resolve_authoritative_red_lane",
                    "reproduce_canonical_base_once",
                    "compare_branch_once",
                    "build_baseline_failure_ledger",
                    "validate_baseline_restoration_candidate",
                ]
            )
        remediation: list[str] = []
        if inputs.remediation_changed_tracked_files:
            remediation.append("targeted_validation")
            if (
                inputs.operating_mode == "BASELINE_RESTORATION"
                and inputs.remediation_affects_baseline_comparison
            ):
                remediation.extend(
                    [
                        "rerun_affected_baseline_comparison",
                        "refresh_baseline_failure_ledger",
                    ]
                )
            remediation.append("independent_reaudit")
        final: list[str] = []
        if inputs.final_scope_committed:
            final.append("legacy_final_validation")
            if inputs.operating_mode == "BASELINE_RESTORATION":
                final.extend(
                    [
                        "classify_nonzero_legacy_gate_against_baseline_ledger",
                        "require_manual_merge_if_exception_used",
                    ]
                )
        return WorkflowPlan(
            pre_audit_steps=tuple(pre_audit),
            remediation_steps=tuple(remediation),
            final_steps=tuple(final),
            blocked_before_audit=False,
            initial_ship_required=False,
            remediation_ship_required=False,
            final_ship_required=False,
            baseline_comparison_required=(
                inputs.operating_mode == "BASELINE_RESTORATION"
            ),
        )

    pre_audit_list = ["verify_doctor"]
    if inputs.run_fast_preflight:
        pre_audit_list.append("verify_fast_with_base")
    if inputs.operating_mode == "BASELINE_RESTORATION":
        pre_audit_list.extend(
            [
                "resolve_authoritative_red_lane",
                "reproduce_canonical_base_once",
                "compare_branch_once",
                "build_baseline_failure_ledger",
                "validate_baseline_restoration_candidate",
            ]
        )

    remediation_list: list[str] = []
    if inputs.remediation_changed_tracked_files:
        remediation_list.append("targeted_validation")
        if inputs.remediation_invalidates_preflight or inputs.governance_sensitive:
            remediation_list.append("verify_fast_with_base")
        if inputs.governance_sensitive:
            remediation_list.append("focused_verification_conformance")
        if (
            inputs.operating_mode == "BASELINE_RESTORATION"
            and inputs.remediation_affects_baseline_comparison
        ):
            remediation_list.extend(
                [
                    "rerun_affected_baseline_comparison",
                    "refresh_baseline_failure_ledger",
                ]
            )
        remediation_list.append("independent_reaudit")

    final: list[str] = []
    if inputs.final_scope_committed:
        final.append("verify_ship_with_base")
        if inputs.operating_mode == "BASELINE_RESTORATION":
            final.extend(
                [
                    "classify_nonzero_ship_against_baseline_ledger",
                    "require_manual_merge_if_exception_used",
                ]
            )

    return WorkflowPlan(
        pre_audit_steps=tuple(pre_audit_list),
        remediation_steps=tuple(remediation_list),
        final_steps=tuple(final),
        blocked_before_audit=False,
        initial_ship_required=False,
        remediation_ship_required=False,
        final_ship_required=inputs.final_scope_committed,
        baseline_comparison_required=(
            inputs.operating_mode == "BASELINE_RESTORATION"
        ),
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter-state", choices=("ABSENT", "VALID", "INVALID"), default="VALID")
    parser.add_argument("--mode", choices=("NORMAL", "BASELINE_RESTORATION"), default="NORMAL")
    parser.add_argument("--skip-fast", action="store_true")
    parser.add_argument("--remediation-changed", action="store_true")
    parser.add_argument("--remediation-invalidates-preflight", action="store_true")
    parser.add_argument("--remediation-affects-baseline-comparison", action="store_true")
    parser.add_argument("--governance-sensitive", action="store_true")
    parser.add_argument("--final-committed", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    plan = build_workflow_plan(
        WorkflowInputs(
            adapter_state=args.adapter_state,
            operating_mode=args.mode,
            run_fast_preflight=not args.skip_fast,
            remediation_changed_tracked_files=args.remediation_changed,
            remediation_invalidates_preflight=args.remediation_invalidates_preflight,
            remediation_affects_baseline_comparison=args.remediation_affects_baseline_comparison,
            governance_sensitive=args.governance_sensitive,
            final_scope_committed=args.final_committed,
        )
    )
    print(plan.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
