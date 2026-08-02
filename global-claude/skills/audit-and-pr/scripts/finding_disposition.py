#!/usr/bin/env python3
"""Risk-based finding disposition and issue-creation contract for /audit-and-pr.

Severity describes impact. Disposition describes what the current audit should do.
The skill documentation remains authoritative; this helper validates that a
proposed disposition is supported by evidence and that permanent GitHub tracking
is created only when the explicit issue-creation gate passes.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import json
from typing import Literal

Severity = Literal["P0", "P1", "P2", "P3"]
FindingKind = Literal["IMPLEMENTATION", "AUDIT_PROCESS_NOTE"]
ExistingIssueState = Literal["NONE", "OPEN_EQUIVALENT", "CLOSED_EQUIVALENT"]
Disposition = Literal[
    "FIX_NOW",
    "DEFER_TO_ISSUE",
    "ADD_TO_EXISTING_ISSUE",
    "BATCH_INTO_CLEANUP_ISSUE",
    "ACCEPT_AS_LOW_VALUE",
    "DISMISS",
    "BLOCK_ACCEPTANCE",
]
IssueAction = Literal[
    "NONE",
    "REUSE_OPEN",
    "CREATE_NEW",
    "CREATE_OR_REUSE_BATCH",
]
DecisionStatus = Literal["ACCEPTED", "REJECTED"]


@dataclass(frozen=True)
class FindingInputs:
    severity: Severity
    proposed_disposition: Disposition
    rationale: str
    kind: FindingKind = "IMPLEMENTATION"
    confirmed: bool = True

    # Acceptance impact.
    objective_required: bool = False
    blocks_safe_acceptance: bool = False

    # Current-scope remediation evidence.
    remediation_authorized: bool = False
    remediation_feasible: bool = False
    directly_related: bool = False
    introduced_or_exposed_by_change: bool = False
    self_contained: bool = False
    clear_acceptance_criteria: bool = False
    deterministic_verification: bool = False
    low_regression_risk: bool = False
    context_reconstruction_cost_high: bool = False
    realistic_material_problem: bool = False
    may_escalate_to_p1: bool = False
    missing_important_verification: bool = False
    trivial_adjacent: bool = False
    behavior_preserving: bool = False

    # Scope-expansion and deferral signals.
    requires_architecture: bool = False
    requires_migration_or_data_model: bool = False
    expands_product_scope: bool = False
    broad_cross_component: bool = False
    repair_risk_exceeds_defect: bool = False
    obscures_intended_pr: bool = False
    optimization_without_evidence: bool = False
    depends_future_decision_or_dependency: bool = False

    # Issue-creation gate.
    issue_actionable: bool = False
    issue_material_enough: bool = False
    issue_appropriately_scoped: bool = False
    issue_verifiable: bool = False
    issue_likely_to_be_worked: bool = False
    better_deferred_than_fixed_now: bool = False
    existing_issue_state: ExistingIssueState = "NONE"
    batchable: bool = False
    related_finding_count: int = 1

    # Low-value or dismissal evidence.
    economically_useful: bool = True
    speculative: bool = False
    subjective: bool = False
    duplicate: bool = False
    outdated: bool = False
    irrelevant: bool = False
    unsupported_by_evidence: bool = False
    non_actionable: bool = False


@dataclass(frozen=True)
class FindingDecision:
    decision_status: DecisionStatus
    severity: Severity
    disposition: Disposition
    may_modify_code: bool
    issue_required: bool
    issue_action: IssueAction
    acceptance_blocked_now: bool
    issue_gate_failures: list[str] = field(default_factory=list)
    reason: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


@dataclass(frozen=True)
class IssueTrackingInputs:
    findings_requiring_issue: int
    findings_with_open_issue_links: int
    newly_created_issues: int
    default_new_issue_budget: int = 3
    budget_exception_explained: bool = False
    github_available: bool = True
    issue_creation_failed: bool = False


@dataclass(frozen=True)
class IssueTrackingDecision:
    complete: bool
    merge_allowed: bool
    status: Literal[
        "COMPLETE",
        "BLOCKED_GITHUB",
        "BLOCKED_MISSING_ISSUES",
        "BLOCKED_ISSUE_BUDGET",
    ]
    reason: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


@dataclass(frozen=True)
class PostRemediationInputs:
    complete_final_diff_reviewed: bool
    original_finding_resolved: bool
    required_verification_passed: bool
    security_and_data_boundaries_rechecked: bool
    objective_still_satisfied: bool
    new_regression_detected: bool = False
    uncontrolled_scope_expansion_detected: bool = False


@dataclass(frozen=True)
class PostRemediationDecision:
    accepted: bool
    status: Literal["PASS", "BLOCKED_REVIEW_INCOMPLETE", "BLOCKED_REGRESSION"]
    reason: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def _reject(inputs: FindingInputs, reason: str, failures: list[str] | None = None) -> FindingDecision:
    return FindingDecision(
        decision_status="REJECTED",
        severity=inputs.severity,
        disposition="BLOCK_ACCEPTANCE",
        may_modify_code=False,
        issue_required=False,
        issue_action="NONE",
        acceptance_blocked_now=True,
        issue_gate_failures=failures or [],
        reason=reason,
    )


def _issue_gate_failures(inputs: FindingInputs) -> list[str]:
    checks = {
        "finding is actionable": inputs.issue_actionable,
        "impact is material enough for permanent backlog": inputs.issue_material_enough,
        "scope is one coherent outcome or root cause": inputs.issue_appropriately_scoped,
        "acceptance criteria are verifiable": inputs.issue_verifiable,
        "work is realistically likely to be scheduled": inputs.issue_likely_to_be_worked,
        "deferral is safer or more efficient than bounded remediation": inputs.better_deferred_than_fixed_now,
    }
    return [label for label, passed in checks.items() if not passed]


def _fix_now_evidence(inputs: FindingInputs) -> list[str]:
    required = {
        "remediation is authorized": inputs.remediation_authorized,
        "remediation is feasible": inputs.remediation_feasible,
        "finding is directly related to the audited change": inputs.directly_related,
        "repair is semantically self-contained": inputs.self_contained,
        "acceptance criteria are clear": inputs.clear_acceptance_criteria,
        "verification is deterministic": inputs.deterministic_verification,
        "regression risk is low or bounded": inputs.low_regression_risk,
    }
    failures = [label for label, passed in required.items() if not passed]

    if inputs.severity == "P2":
        value_signals = (
            inputs.introduced_or_exposed_by_change,
            inputs.context_reconstruction_cost_high,
            inputs.realistic_material_problem,
            inputs.may_escalate_to_p1,
            inputs.missing_important_verification,
        )
        if not any(value_signals):
            failures.append("P2 lacks evidence that immediate repair has material contextual value")

    if inputs.severity == "P3":
        if not inputs.trivial_adjacent:
            failures.append("P3 repair is not genuinely trivial and directly adjacent")
        if not inputs.behavior_preserving:
            failures.append("P3 repair is not proven behavior-preserving")

    scope_blockers = {
        "requires architecture redesign": inputs.requires_architecture,
        "requires migration or material data-model work": inputs.requires_migration_or_data_model,
        "expands product scope": inputs.expands_product_scope,
        "requires broad cross-component work": inputs.broad_cross_component,
        "repair risk exceeds the defect": inputs.repair_risk_exceeds_defect,
        "would obscure or materially expand the intended PR": inputs.obscures_intended_pr,
        "is an unsupported optimization": inputs.optimization_without_evidence,
        "depends on a future decision or dependency": inputs.depends_future_decision_or_dependency,
    }
    failures.extend(label for label, present in scope_blockers.items() if present)
    return failures


def decide_finding(inputs: FindingInputs) -> FindingDecision:
    if not inputs.rationale.strip():
        return _reject(inputs, "Every finding requires an explicit disposition rationale.")

    if inputs.related_finding_count < 1:
        return _reject(inputs, "related_finding_count must be at least one.")

    dismissal_evidence = any(
        (
            not inputs.confirmed,
            inputs.kind == "AUDIT_PROCESS_NOTE",
            inputs.speculative,
            inputs.subjective,
            inputs.duplicate,
            inputs.outdated,
            inputs.irrelevant,
            inputs.unsupported_by_evidence,
            inputs.non_actionable,
        )
    )

    # P0/P1 cannot be deferred or accepted as residual risk.
    if inputs.severity in {"P0", "P1"}:
        if inputs.proposed_disposition == "FIX_NOW":
            if inputs.remediation_authorized and inputs.remediation_feasible:
                return FindingDecision(
                    decision_status="ACCEPTED",
                    severity=inputs.severity,
                    disposition="FIX_NOW",
                    may_modify_code=True,
                    issue_required=False,
                    issue_action="NONE",
                    acceptance_blocked_now=True,
                    reason="P0/P1 requires immediate authorized remediation and remains acceptance-blocking until reverified.",
                )
            return _reject(
                inputs,
                "P0/P1 may use FIX_NOW only when remediation is both authorized and feasible; otherwise BLOCK_ACCEPTANCE is required.",
            )
        if inputs.proposed_disposition == "BLOCK_ACCEPTANCE":
            return FindingDecision(
                decision_status="ACCEPTED",
                severity=inputs.severity,
                disposition="BLOCK_ACCEPTANCE",
                may_modify_code=False,
                issue_required=False,
                issue_action="NONE",
                acceptance_blocked_now=True,
                reason="Unresolved P0/P1 blocks acceptance and cannot be satisfied by future tracking alone.",
            )
        return _reject(inputs, "P0/P1 permits only FIX_NOW or BLOCK_ACCEPTANCE.")

    # Unconfirmed/process-only/speculative findings must not become backlog.
    if dismissal_evidence:
        if inputs.proposed_disposition != "DISMISS":
            return _reject(
                inputs,
                "Unconfirmed, process-only, duplicate, speculative, outdated, irrelevant, subjective, or unsupported observations must be dismissed rather than fixed or ticketed.",
            )
        return FindingDecision(
            decision_status="ACCEPTED",
            severity=inputs.severity,
            disposition="DISMISS",
            may_modify_code=False,
            issue_required=False,
            issue_action="NONE",
            acceptance_blocked_now=False,
            reason="The observation does not justify remediation or permanent backlog.",
        )

    if inputs.objective_required or inputs.blocks_safe_acceptance:
        if inputs.proposed_disposition == "FIX_NOW":
            failures = _fix_now_evidence(inputs)
            if not failures:
                return FindingDecision(
                    decision_status="ACCEPTED",
                    severity=inputs.severity,
                    disposition="FIX_NOW",
                    may_modify_code=True,
                    issue_required=False,
                    issue_action="NONE",
                    acceptance_blocked_now=True,
                    reason="The finding is required for safe acceptance and has a bounded, verifiable repair.",
                )
            return _reject(inputs, "The acceptance-critical repair does not satisfy FIX_NOW evidence.", failures)
        if inputs.proposed_disposition == "BLOCK_ACCEPTANCE":
            return FindingDecision(
                decision_status="ACCEPTED",
                severity=inputs.severity,
                disposition="BLOCK_ACCEPTANCE",
                may_modify_code=False,
                issue_required=False,
                issue_action="NONE",
                acceptance_blocked_now=True,
                reason="The finding prevents safe acceptance and cannot be deferred.",
            )
        return _reject(inputs, "A finding required for safe acceptance must be FIX_NOW or BLOCK_ACCEPTANCE.")

    if inputs.proposed_disposition == "FIX_NOW":
        failures = _fix_now_evidence(inputs)
        if failures:
            return _reject(inputs, "FIX_NOW evidence is incomplete or scope expansion is excessive.", failures)
        return FindingDecision(
            decision_status="ACCEPTED",
            severity=inputs.severity,
            disposition="FIX_NOW",
            may_modify_code=True,
            issue_required=False,
            issue_action="NONE",
            acceptance_blocked_now=False,
            reason="A bounded, directly related repair is safer and more efficient while current context is available.",
        )

    if inputs.proposed_disposition in {
        "DEFER_TO_ISSUE",
        "ADD_TO_EXISTING_ISSUE",
        "BATCH_INTO_CLEANUP_ISSUE",
    }:
        gate_failures = _issue_gate_failures(inputs)
        if gate_failures:
            return _reject(inputs, "The issue-creation gate did not pass.", gate_failures)

        if inputs.existing_issue_state == "OPEN_EQUIVALENT":
            return FindingDecision(
                decision_status="ACCEPTED",
                severity=inputs.severity,
                disposition="ADD_TO_EXISTING_ISSUE",
                may_modify_code=False,
                issue_required=True,
                issue_action="REUSE_OPEN",
                acceptance_blocked_now=False,
                reason="An equivalent open issue already owns the remediation outcome; add evidence rather than create a duplicate.",
            )

        if inputs.proposed_disposition == "ADD_TO_EXISTING_ISSUE":
            return _reject(inputs, "ADD_TO_EXISTING_ISSUE requires an equivalent open issue.")

        if inputs.proposed_disposition == "BATCH_INTO_CLEANUP_ISSUE":
            if not inputs.batchable or inputs.related_finding_count < 2:
                return _reject(inputs, "Batch disposition requires at least two related findings with one coherent root cause or cleanup outcome.")
            return FindingDecision(
                decision_status="ACCEPTED",
                severity=inputs.severity,
                disposition="BATCH_INTO_CLEANUP_ISSUE",
                may_modify_code=False,
                issue_required=True,
                issue_action="CREATE_OR_REUSE_BATCH",
                acceptance_blocked_now=False,
                reason="Related low-severity findings are economically better tracked as one coherent cleanup or root-cause issue.",
            )

        if inputs.batchable and inputs.related_finding_count > 1:
            return _reject(inputs, "Repeated manifestations should be batched rather than creating an occurrence-level issue.")

        return FindingDecision(
            decision_status="ACCEPTED",
            severity=inputs.severity,
            disposition="DEFER_TO_ISSUE",
            may_modify_code=False,
            issue_required=True,
            issue_action="CREATE_NEW",
            acceptance_blocked_now=False,
            reason="The finding passes the issue gate and is safer or more efficient as a dedicated future unit of work.",
        )

    if inputs.proposed_disposition == "ACCEPT_AS_LOW_VALUE":
        if not inputs.confirmed:
            return _reject(inputs, "Unconfirmed observations must be dismissed, not accepted as valid residual findings.")
        if inputs.blocks_safe_acceptance or inputs.objective_required:
            return _reject(inputs, "Acceptance-critical findings cannot be accepted as low value.")
        if inputs.issue_material_enough and inputs.issue_likely_to_be_worked and inputs.economically_useful:
            return _reject(inputs, "A materially valuable, schedulable finding should be fixed, added to an existing issue, batched, or deferred through the issue gate.")
        return FindingDecision(
            decision_status="ACCEPTED",
            severity=inputs.severity,
            disposition="ACCEPT_AS_LOW_VALUE",
            may_modify_code=False,
            issue_required=False,
            issue_action="NONE",
            acceptance_blocked_now=False,
            reason="The finding is valid but its expected remediation or tracking value does not justify current scope or permanent backlog cost.",
        )

    if inputs.proposed_disposition == "DISMISS":
        return _reject(inputs, "A confirmed supported finding may be dismissed only with duplicate, speculative, subjective, outdated, irrelevant, unsupported, or non-actionable evidence.")

    if inputs.proposed_disposition == "BLOCK_ACCEPTANCE":
        return _reject(inputs, "P2/P3 may block acceptance only when objective_required or blocks_safe_acceptance is explicitly established.")

    return _reject(inputs, "Unsupported disposition.")


def assess_issue_tracking(inputs: IssueTrackingInputs) -> IssueTrackingDecision:
    counts = (
        inputs.findings_requiring_issue,
        inputs.findings_with_open_issue_links,
        inputs.newly_created_issues,
        inputs.default_new_issue_budget,
    )
    if any(value < 0 for value in counts):
        raise ValueError("issue tracking counts and budget must be non-negative")
    if inputs.findings_with_open_issue_links > inputs.findings_requiring_issue:
        raise ValueError("linked finding count cannot exceed issue-required finding count")
    if inputs.newly_created_issues > inputs.findings_with_open_issue_links:
        raise ValueError("new issue count cannot exceed linked issue count")

    if inputs.findings_requiring_issue == 0:
        return IssueTrackingDecision(
            complete=True,
            merge_allowed=True,
            status="COMPLETE",
            reason="No finding disposition requires permanent GitHub tracking.",
        )

    if not inputs.github_available or inputs.issue_creation_failed:
        return IssueTrackingDecision(
            complete=False,
            merge_allowed=False,
            status="BLOCKED_GITHUB",
            reason="Required issue search, update, or creation could not be completed.",
        )

    if inputs.findings_with_open_issue_links != inputs.findings_requiring_issue:
        return IssueTrackingDecision(
            complete=False,
            merge_allowed=False,
            status="BLOCKED_MISSING_ISSUES",
            reason="Every finding with an issue-required disposition must map to an equivalent open GitHub issue.",
        )

    if (
        inputs.newly_created_issues > inputs.default_new_issue_budget
        and not inputs.budget_exception_explained
    ):
        return IssueTrackingDecision(
            complete=False,
            merge_allowed=False,
            status="BLOCKED_ISSUE_BUDGET",
            reason="The default new-issue budget was exceeded without explaining why findings could not be fixed, reused, or consolidated.",
        )

    return IssueTrackingDecision(
        complete=True,
        merge_allowed=True,
        status="COMPLETE",
        reason="All issue-required findings are linked, deduplicated, scoped, and within the issue budget or a documented exception.",
    )


def assess_post_remediation(inputs: PostRemediationInputs) -> PostRemediationDecision:
    if inputs.new_regression_detected or inputs.uncontrolled_scope_expansion_detected:
        return PostRemediationDecision(
            accepted=False,
            status="BLOCKED_REGRESSION",
            reason="Post-remediation review found a new regression or uncontrolled scope expansion.",
        )

    required = {
        "complete final diff was reviewed": inputs.complete_final_diff_reviewed,
        "original finding was resolved": inputs.original_finding_resolved,
        "required verification passed": inputs.required_verification_passed,
        "security and data boundaries were rechecked": inputs.security_and_data_boundaries_rechecked,
        "objective remains satisfied": inputs.objective_still_satisfied,
    }
    missing = [label for label, passed in required.items() if not passed]
    if missing:
        return PostRemediationDecision(
            accepted=False,
            status="BLOCKED_REVIEW_INCOMPLETE",
            reason="Post-remediation acceptance review is incomplete: " + "; ".join(missing),
        )

    return PostRemediationDecision(
        accepted=True,
        status="PASS",
        reason="The complete final diff passed independent post-remediation acceptance review.",
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    finding = subparsers.add_parser("finding")
    finding.add_argument("--json", required=True)

    tracking = subparsers.add_parser("tracking")
    tracking.add_argument("--json", required=True)

    post = subparsers.add_parser("post-remediation")
    post.add_argument("--json", required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    raw = json.loads(args.json)
    if args.command == "finding":
        print(decide_finding(FindingInputs(**raw)).to_json())
    elif args.command == "tracking":
        print(assess_issue_tracking(IssueTrackingInputs(**raw)).to_json())
    else:
        print(assess_post_remediation(PostRemediationInputs(**raw)).to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
