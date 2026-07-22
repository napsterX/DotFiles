#!/usr/bin/env python3
"""Executable reference for /audit-and-pr verification sequencing.

This helper describes the required stage order. It does not execute repository
commands. Its purpose is to prevent regression to an expensive initial full
ship gate or mandatory ship reruns after every remediation edit.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Literal

AdapterState = Literal["ABSENT", "VALID", "INVALID"]


@dataclass(frozen=True)
class WorkflowInputs:
    adapter_state: AdapterState = "VALID"
    run_fast_preflight: bool = True
    remediation_changed_tracked_files: bool = False
    remediation_invalidates_preflight: bool = False
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
        )

    if inputs.adapter_state == "ABSENT":
        pre_audit = ("legacy_validation_discovery",)
        final = ("legacy_final_validation",) if inputs.final_scope_committed else ()
        remediation = (
            ("targeted_validation", "independent_reaudit")
            if inputs.remediation_changed_tracked_files
            else ()
        )
        return WorkflowPlan(
            pre_audit_steps=pre_audit,
            remediation_steps=remediation,
            final_steps=final,
            blocked_before_audit=False,
            initial_ship_required=False,
            remediation_ship_required=False,
            final_ship_required=False,
        )

    pre_audit_list = ["verify_doctor"]
    if inputs.run_fast_preflight:
        pre_audit_list.append("verify_fast_with_base")

    remediation_list: list[str] = []
    if inputs.remediation_changed_tracked_files:
        remediation_list.append("targeted_validation")
        if inputs.remediation_invalidates_preflight or inputs.governance_sensitive:
            remediation_list.append("verify_fast_with_base")
        if inputs.governance_sensitive:
            remediation_list.append("focused_verification_conformance")
        remediation_list.append("independent_reaudit")

    final = ("verify_ship_with_base",) if inputs.final_scope_committed else ()
    return WorkflowPlan(
        pre_audit_steps=tuple(pre_audit_list),
        remediation_steps=tuple(remediation_list),
        final_steps=final,
        blocked_before_audit=False,
        initial_ship_required=False,
        remediation_ship_required=False,
        final_ship_required=inputs.final_scope_committed,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter-state", choices=("ABSENT", "VALID", "INVALID"), default="VALID")
    parser.add_argument("--skip-fast", action="store_true")
    parser.add_argument("--remediation-changed", action="store_true")
    parser.add_argument("--remediation-invalidates-preflight", action="store_true")
    parser.add_argument("--governance-sensitive", action="store_true")
    parser.add_argument("--final-committed", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    plan = build_workflow_plan(
        WorkflowInputs(
            adapter_state=args.adapter_state,
            run_fast_preflight=not args.skip_fast,
            remediation_changed_tracked_files=args.remediation_changed,
            remediation_invalidates_preflight=args.remediation_invalidates_preflight,
            governance_sensitive=args.governance_sensitive,
            final_scope_committed=args.final_committed,
        )
    )
    print(plan.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
