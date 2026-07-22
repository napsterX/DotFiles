#!/usr/bin/env python3
"""Executable severity and tracking policy for /audit-and-pr findings.

The skill documentation remains authoritative. This helper prevents remediation
logic from treating mechanically easy P2/P3 findings as in-scope fixes and
ensures every confirmed deferred finding has durable GitHub tracking before
merge.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from typing import Literal

Severity = Literal["P0", "P1", "P2", "P3"]
FindingKind = Literal["IMPLEMENTATION", "AUDIT_PROCESS_NOTE"]
ExistingIssueState = Literal["NONE", "OPEN_EQUIVALENT", "CLOSED_EQUIVALENT"]
Disposition = Literal[
    "REMEDIATE_CURRENT_SCOPE",
    "BLOCK_SHIPMENT",
    "DEFER_TO_GITHUB",
    "REPORT_ONLY",
    "BLOCK_CLASSIFICATION_REVIEW",
]
IssueAction = Literal["NONE", "REUSE_OPEN", "CREATE_NEW"]


@dataclass(frozen=True)
class FindingInputs:
    severity: Severity
    kind: FindingKind = "IMPLEMENTATION"
    confirmed: bool = True
    objective_required: bool = False
    remediation_eligible: bool = False
    existing_issue_state: ExistingIssueState = "NONE"


@dataclass(frozen=True)
class FindingDecision:
    disposition: Disposition
    may_modify_code: bool
    issue_required: bool
    issue_action: IssueAction
    merge_blocked_now: bool
    reason: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


@dataclass(frozen=True)
class DeferredTrackingInputs:
    confirmed_deferred_findings: int
    findings_with_open_issue_links: int
    issue_creation_failed: bool = False
    github_available: bool = True


@dataclass(frozen=True)
class DeferredTrackingDecision:
    complete: bool
    merge_allowed: bool
    status: Literal["COMPLETE", "BLOCKED_GITHUB", "BLOCKED_MISSING_ISSUES"]
    reason: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def decide_finding(inputs: FindingInputs) -> FindingDecision:
    if inputs.kind == "AUDIT_PROCESS_NOTE" or not inputs.confirmed:
        return FindingDecision(
            disposition="REPORT_ONLY",
            may_modify_code=False,
            issue_required=False,
            issue_action="NONE",
            merge_blocked_now=False,
            reason="Only confirmed implementation findings receive remediation or GitHub tracking.",
        )

    if inputs.severity in {"P0", "P1"}:
        if inputs.remediation_eligible:
            return FindingDecision(
                disposition="REMEDIATE_CURRENT_SCOPE",
                may_modify_code=True,
                issue_required=False,
                issue_action="NONE",
                merge_blocked_now=False,
                reason="P0/P1 may be remediated only when the existing bounded-remediation policy marks the fix eligible.",
            )
        return FindingDecision(
            disposition="BLOCK_SHIPMENT",
            may_modify_code=False,
            issue_required=False,
            issue_action="NONE",
            merge_blocked_now=True,
            reason="Unresolved P0/P1 findings block shipment and may not be deferred to backlog tracking.",
        )

    # P2/P3 are always deferred, regardless of mechanical ease.
    if inputs.objective_required:
        return FindingDecision(
            disposition="BLOCK_CLASSIFICATION_REVIEW",
            may_modify_code=False,
            issue_required=False,
            issue_action="NONE",
            merge_blocked_now=True,
            reason="A finding required to satisfy the current objective cannot be deferred as P2/P3; reclassify it or mark the objective unsatisfied.",
        )

    if inputs.existing_issue_state == "OPEN_EQUIVALENT":
        issue_action: IssueAction = "REUSE_OPEN"
    else:
        issue_action = "CREATE_NEW"

    return FindingDecision(
        disposition="DEFER_TO_GITHUB",
        may_modify_code=False,
        issue_required=True,
        issue_action=issue_action,
        merge_blocked_now=False,
        reason="Confirmed P2/P3 findings are not fixed by /audit-and-pr and require an equivalent open GitHub issue before merge.",
    )


def assess_deferred_tracking(inputs: DeferredTrackingInputs) -> DeferredTrackingDecision:
    if inputs.confirmed_deferred_findings < 0 or inputs.findings_with_open_issue_links < 0:
        raise ValueError("finding counts must be non-negative")
    if inputs.findings_with_open_issue_links > inputs.confirmed_deferred_findings:
        raise ValueError("linked finding count cannot exceed deferred finding count")

    if inputs.confirmed_deferred_findings == 0:
        return DeferredTrackingDecision(
            complete=True,
            merge_allowed=True,
            status="COMPLETE",
            reason="No confirmed P2/P3 findings require tracking.",
        )

    if not inputs.github_available or inputs.issue_creation_failed:
        return DeferredTrackingDecision(
            complete=False,
            merge_allowed=False,
            status="BLOCKED_GITHUB",
            reason="GitHub tracking could not be completed; merge remains blocked.",
        )

    if inputs.findings_with_open_issue_links != inputs.confirmed_deferred_findings:
        return DeferredTrackingDecision(
            complete=False,
            merge_allowed=False,
            status="BLOCKED_MISSING_ISSUES",
            reason="Every confirmed P2/P3 finding must map to an equivalent open GitHub issue before merge.",
        )

    return DeferredTrackingDecision(
        complete=True,
        merge_allowed=True,
        status="COMPLETE",
        reason="Every confirmed deferred finding maps to an equivalent open GitHub issue.",
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    finding = subparsers.add_parser("finding")
    finding.add_argument("--json", required=True)

    tracking = subparsers.add_parser("tracking")
    tracking.add_argument("--json", required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    raw = json.loads(args.json)
    if args.command == "finding":
        print(decide_finding(FindingInputs(**raw)).to_json())
    else:
        print(assess_deferred_tracking(DeferredTrackingInputs(**raw)).to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
