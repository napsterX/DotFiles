#!/usr/bin/env python3
"""Executable decision contract for controlled baseline-restoration shipment."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from typing import Literal

ModeSource = Literal["NONE", "EXPLICIT", "INFERRED"]
ResultState = Literal["PASS", "FAIL", "NOT_OBSERVED"]
TestingConfidence = Literal["HIGH", "MODERATE", "LOW"]
Disposition = Literal[
    "FIXED_BY_BRANCH",
    "UNCHANGED_TRACKED_BASELINE",
    "PRE_EXISTING_NEWLY_UNMASKED",
    "NEW_REGRESSION",
    "UNATTRIBUTED",
]

PROTECTED_DOMAINS = {
    "security",
    "authorization",
    "tenancy",
    "tenancy-isolation",
    "migration",
    "migration-safety",
    "data-integrity",
    "payment",
    "destructive-operation",
    "privacy",
}


@dataclass(frozen=True)
class FailureObservation:
    check_name: str
    first_causal_error: str
    environment_profile: str
    base_result: ResultState
    branch_result: ResultState
    canonical_issue: str = ""
    canonical_issue_open: bool = False
    pre_existing_newly_unmasked_proven: bool = False
    plausibly_caused_by_current_diff: bool = False
    domain: str = "general"


@dataclass(frozen=True)
class LedgerEntry:
    failure_identity: str
    base_result: ResultState
    branch_result: ResultState
    owner: str
    disposition: Disposition
    domain: str


@dataclass(frozen=True)
class RestorationInputs:
    mode_source: ModeSource = "NONE"
    restoration_intent_proven: bool = False
    canonical_base_reproduced: bool = False
    same_authoritative_command: bool = False
    same_material_environment: bool = False
    base_commit_unchanged: bool = True
    final_ship_exit_code: int = 1
    final_head_bound: bool = True
    working_tree_clean: bool = True
    change_specific_validation_passed: bool = True
    nonblocked_mandatory_gates_passed: bool = True
    no_remaining_p0: bool = True
    no_remaining_p1: bool = True
    testing_confidence: TestingConfidence = "HIGH"
    gate_weakened: bool = False
    favorable_retry_sampling_used: bool = False
    ledger_complete: bool = True
    observations: tuple[FailureObservation, ...] = ()


@dataclass(frozen=True)
class RestorationDecision:
    classification: Literal[
        "NORMAL_GREEN", "FAILED_PRE_EXISTING_BASELINE", "BLOCKED"
    ]
    eligible: bool
    allow_push_and_pr: bool
    manual_merge_required: bool
    auto_merge_allowed: bool
    ledger: list[LedgerEntry] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def _required_text(value: str, field_name: str) -> str:
    cleaned = " ".join(value.split())
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def classify_observation(observation: FailureObservation) -> LedgerEntry:
    name = _required_text(observation.check_name, "check_name")
    error = _required_text(observation.first_causal_error, "first_causal_error")
    environment = _required_text(
        observation.environment_profile, "environment_profile"
    )
    owner = observation.canonical_issue.strip()
    identity = f"{name} | {error} | {environment}"
    domain = observation.domain.strip().lower() or "general"

    if observation.base_result == "FAIL" and observation.branch_result == "PASS":
        disposition: Disposition = "FIXED_BY_BRANCH"
    elif observation.base_result == "FAIL" and observation.branch_result == "FAIL":
        disposition = (
            "UNCHANGED_TRACKED_BASELINE"
            if observation.canonical_issue_open and owner
            else "UNATTRIBUTED"
        )
    elif observation.branch_result == "FAIL":
        if (
            observation.pre_existing_newly_unmasked_proven
            and observation.canonical_issue_open
            and owner
        ):
            disposition = "PRE_EXISTING_NEWLY_UNMASKED"
        elif observation.plausibly_caused_by_current_diff:
            disposition = "NEW_REGRESSION"
        else:
            disposition = "UNATTRIBUTED"
    else:
        # A passing entry that was not a base failure does not establish
        # restoration and cannot be used to pad the ledger.
        disposition = "UNATTRIBUTED"

    return LedgerEntry(
        failure_identity=identity,
        base_result=observation.base_result,
        branch_result=observation.branch_result,
        owner=owner,
        disposition=disposition,
        domain=domain,
    )


def assess_baseline_restoration(inputs: RestorationInputs) -> RestorationDecision:
    ledger = [classify_observation(item) for item in inputs.observations]

    if inputs.final_ship_exit_code == 0:
        return RestorationDecision(
            classification="NORMAL_GREEN",
            eligible=False,
            allow_push_and_pr=True,
            manual_merge_required=False,
            auto_merge_allowed=True,
            ledger=ledger,
            reasons=["The final aggregate ship gate passed; no exception is needed."],
        )

    blockers: list[str] = []
    reasons: list[str] = []

    if inputs.final_ship_exit_code != 1:
        blockers.append(
            "only exit 1 may represent a comparable required-check baseline failure"
        )
    if inputs.mode_source == "NONE":
        blockers.append("baseline-restoration mode was neither explicitly requested nor safely inferred")
    if not inputs.restoration_intent_proven:
        blockers.append("the task is not proven to be incremental restoration of an already-red lane")
    if not inputs.canonical_base_reproduced:
        blockers.append("the untouched canonical base was not directly reproduced")
    if not inputs.same_authoritative_command:
        blockers.append("base and branch were not compared with the same authoritative command or lane")
    if not inputs.same_material_environment:
        blockers.append("base and branch were not compared under the same material environment or profile")
    if not inputs.base_commit_unchanged:
        blockers.append("the canonical base changed after reproduction")
    if not inputs.final_head_bound:
        blockers.append("the final comparison is not bound to the exact audited committed HEAD")
    if not inputs.working_tree_clean:
        blockers.append("the working tree was not clean after final verification")
    if not inputs.change_specific_validation_passed:
        blockers.append("change-specific validation did not pass")
    if not inputs.nonblocked_mandatory_gates_passed:
        blockers.append("a mandatory gate outside the proven baseline set did not pass")
    if not inputs.no_remaining_p0:
        blockers.append("an in-scope P0 remains")
    if not inputs.no_remaining_p1:
        blockers.append("an in-scope P1 remains")
    if inputs.testing_confidence == "LOW":
        blockers.append("testing confidence is LOW")
    if inputs.gate_weakened:
        blockers.append("verification was weakened, skipped, quarantined, reclassified, or extended")
    if inputs.favorable_retry_sampling_used:
        blockers.append("repeated reruns were used to manufacture a favorable comparison")
    if not inputs.ledger_complete:
        blockers.append("the base-versus-branch failure ledger is incomplete")
    if not ledger:
        blockers.append("the failure ledger is empty")

    fixed = [row for row in ledger if row.disposition == "FIXED_BY_BRANCH"]
    if not fixed:
        blockers.append("the branch does not fix any identified canonical-base failure")

    for observation, row in zip(inputs.observations, ledger):
        if not observation.canonical_issue_open or not row.owner:
            blockers.append(f"failure lacks a canonical open issue: {row.failure_identity}")
        if row.disposition == "NEW_REGRESSION":
            blockers.append(f"new regression: {row.failure_identity}")
        elif row.disposition == "UNATTRIBUTED":
            blockers.append(f"unattributed failure: {row.failure_identity}")
        elif row.branch_result == "FAIL" and row.domain in PROTECTED_DOMAINS:
            blockers.append(
                f"protected-domain residual cannot use baseline restoration: {row.failure_identity}"
            )
        elif row.disposition in {
            "UNCHANGED_TRACKED_BASELINE",
            "PRE_EXISTING_NEWLY_UNMASKED",
        } and not row.owner:
            blockers.append(f"residual failure lacks a canonical issue: {row.failure_identity}")

    if blockers:
        return RestorationDecision(
            classification="BLOCKED",
            eligible=False,
            allow_push_and_pr=False,
            manual_merge_required=False,
            auto_merge_allowed=False,
            ledger=ledger,
            blockers=blockers,
            reasons=reasons,
        )

    reasons.extend(
        [
            "the branch fixes at least one reproduced canonical-base failure",
            "all residual failures are unchanged tracked baseline failures or proven pre-existing newly unmasked failures",
            "no new or unattributed failure remains",
            "the aggregate ship gate remains truthfully red due only to the recorded pre-existing baseline",
        ]
    )
    return RestorationDecision(
        classification="FAILED_PRE_EXISTING_BASELINE",
        eligible=True,
        allow_push_and_pr=True,
        manual_merge_required=True,
        auto_merge_allowed=False,
        ledger=ledger,
        blockers=[],
        reasons=reasons,
    )



@dataclass(frozen=True)
class PostMergeReconciliationInputs:
    pr_target_branch: str
    github_default_branch: str
    merge_confirmed: bool = False
    issue_reconciled: bool = False


@dataclass(frozen=True)
class PostMergeReconciliationDecision:
    reconciliation_required: bool
    cleanup_allowed: bool
    cleanup_target_branch: str
    reason: str


def assess_post_merge_reconciliation(
    inputs: PostMergeReconciliationInputs,
) -> PostMergeReconciliationDecision:
    target = _required_text(inputs.pr_target_branch, "pr_target_branch")
    default = _required_text(inputs.github_default_branch, "github_default_branch")
    if not inputs.merge_confirmed:
        return PostMergeReconciliationDecision(
            reconciliation_required=False,
            cleanup_allowed=False,
            cleanup_target_branch=target,
            reason="merge is not confirmed",
        )
    if target == default:
        return PostMergeReconciliationDecision(
            reconciliation_required=False,
            cleanup_allowed=True,
            cleanup_target_branch=target,
            reason="PR targeted the GitHub default branch",
        )
    if not inputs.issue_reconciled:
        return PostMergeReconciliationDecision(
            reconciliation_required=True,
            cleanup_allowed=False,
            cleanup_target_branch=target,
            reason="non-default integration target requires manual issue reconciliation before cleanup",
        )
    return PostMergeReconciliationDecision(
        reconciliation_required=True,
        cleanup_allowed=True,
        cleanup_target_branch=target,
        reason="manual issue reconciliation is recorded for the non-default integration target",
    )

def _observation_from_json(raw: dict) -> FailureObservation:
    return FailureObservation(**raw)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", required=True, help="JSON object matching RestorationInputs")
    args = parser.parse_args()
    raw = json.loads(args.json)
    observations = tuple(
        _observation_from_json(item) for item in raw.pop("observations", [])
    )
    result = assess_baseline_restoration(
        RestorationInputs(observations=observations, **raw)
    )
    print(result.to_json())
    return 0 if result.classification != "BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
