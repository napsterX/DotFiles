#!/usr/bin/env python3
"""Deterministic contracts for audit-and-pr PR summaries and changelog handling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

START_MARKER = "<!-- audit-and-pr:change-summary:start -->"
END_MARKER = "<!-- audit-and-pr:change-summary:end -->"
CATEGORY_ORDER = ("Added", "Changed", "Fixed", "Removed")
VALID_CONVENTIONS = {
    "NONE",
    "CHANGELOG_FILE",
    "CHANGESETS",
    "TOWNCRIER",
    "CUSTOM_FRAGMENT",
}

VALID_FINDING_DISPOSITIONS = {
    "FIX_NOW",
    "DEFER_TO_ISSUE",
    "ADD_TO_EXISTING_ISSUE",
    "BATCH_INTO_CLEANUP_ISSUE",
    "ACCEPT_AS_LOW_VALUE",
    "DISMISS",
    "BLOCK_ACCEPTANCE",
}
ISSUE_REQUIRED_DISPOSITIONS = {
    "DEFER_TO_ISSUE",
    "ADD_TO_EXISTING_ISSUE",
    "BATCH_INTO_CLEANUP_ISSUE",
}
DISPOSITION_HEADINGS = (
    ("FIX_NOW", "Remediated now"),
    ("DEFER_TO_ISSUE", "Deferred with issues"),
    ("ADD_TO_EXISTING_ISSUE", "Added to existing issues"),
    ("BATCH_INTO_CLEANUP_ISSUE", "Batched findings"),
    ("ACCEPT_AS_LOW_VALUE", "Accepted low value"),
    ("DISMISS", "Dismissed"),
    ("BLOCK_ACCEPTANCE", "Acceptance blockers"),
)

VALID_BASELINE_DISPOSITIONS = {
    "FIXED_BY_BRANCH",
    "UNCHANGED_TRACKED_BASELINE",
    "PRE_EXISTING_NEWLY_UNMASKED",
}


@dataclass(frozen=True)
class ChangeEntry:
    category: str
    text: str


@dataclass(frozen=True)
class DeferredFinding:
    """Backward-compatible issue-required finding input."""

    priority: str
    title: str
    issue_url: str


@dataclass(frozen=True)
class FindingDispositionEntry:
    severity: str
    disposition: str
    title: str
    issue_url: str = ""


@dataclass(frozen=True)
class BaselineLedgerRow:
    failure_identity: str
    base_result: str
    branch_result: str
    owner_issue_url: str
    disposition: str


@dataclass(frozen=True)
class BaselineRestorationSummary:
    target_failure_fixed: str
    canonical_base: str
    base_commit: str
    base_command: str
    base_result: str
    branch_commit: str
    branch_command: str
    branch_result: str
    aggregate_ship_command: str
    aggregate_ship_exit_code: int
    ledger: tuple[BaselineLedgerRow, ...]


@dataclass(frozen=True)
class SummaryInputs:
    final_head: str
    changes: tuple[ChangeEntry, ...]
    user_facing_impacts: tuple[str, ...] = ()
    breaking_changes: tuple[str, ...] = ()
    deferred_findings: tuple[DeferredFinding, ...] = ()
    finding_dispositions: tuple[FindingDispositionEntry, ...] = ()
    baseline_restoration: Optional[BaselineRestorationSummary] = None


@dataclass(frozen=True)
class ChangelogInputs:
    convention: str = "NONE"
    repository_requires_entry: bool = False
    change_requires_entry: bool = False
    artifact_present: bool = False
    creation_authorized: bool = False
    deterministic_format: bool = False


@dataclass(frozen=True)
class ChangelogDecision:
    status: str
    may_modify_repository: bool
    blocks_shipment: bool
    reason: str


def _clean_items(values: Iterable[str], field: str) -> tuple[str, ...]:
    result: list[str] = []
    for value in values:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError(f"{field} contains an empty item")
        result.append(cleaned)
    return tuple(result)


def _table_cell(value: str, field: str) -> str:
    cleaned = " ".join(value.split())
    if not cleaned:
        raise ValueError(f"{field} is required")
    return cleaned.replace("|", "\\|")


def _render_baseline_restoration(summary: BaselineRestorationSummary) -> list[str]:
    if summary.aggregate_ship_exit_code == 0:
        raise ValueError("baseline-restoration summary requires a truthful nonzero aggregate ship result")
    if summary.aggregate_ship_exit_code != 1:
        raise ValueError("only aggregate ship exit 1 can be classified as FAILED_PRE_EXISTING_BASELINE")
    if not summary.ledger:
        raise ValueError("baseline-restoration summary requires a complete failure ledger")

    target = _table_cell(summary.target_failure_fixed, "target_failure_fixed")
    canonical_base = _table_cell(summary.canonical_base, "canonical_base")
    base_commit = _table_cell(summary.base_commit, "base_commit")
    base_command = _table_cell(summary.base_command, "base_command")
    base_result = _table_cell(summary.base_result, "base_result")
    branch_commit = _table_cell(summary.branch_commit, "branch_commit")
    branch_command = _table_cell(summary.branch_command, "branch_command")
    branch_result = _table_cell(summary.branch_result, "branch_result")
    aggregate_command = _table_cell(summary.aggregate_ship_command, "aggregate_ship_command")

    rows: list[BaselineLedgerRow] = []
    fixed_count = 0
    for row in summary.ledger:
        disposition = row.disposition.strip().upper()
        if disposition not in VALID_BASELINE_DISPOSITIONS:
            raise ValueError(f"unsupported baseline-restoration disposition: {row.disposition}")
        identity = _table_cell(row.failure_identity, "failure_identity")
        base = _table_cell(row.base_result, "base_result")
        branch = _table_cell(row.branch_result, "branch_result")
        owner = row.owner_issue_url.strip()
        if not owner.startswith(("https://", "http://")):
            raise ValueError("every baseline ledger row requires a canonical issue URL")
        if disposition == "FIXED_BY_BRANCH":
            fixed_count += 1
        rows.append(BaselineLedgerRow(identity, base, branch, owner, disposition))
    if fixed_count == 0:
        raise ValueError("baseline-restoration ledger must contain at least one FIXED_BY_BRANCH row")

    lines = [
        "## Baseline restoration",
        "",
        "- Classification: `FAILED_PRE_EXISTING_BASELINE`",
        f"- Target failure fixed: {target}",
        f"- Canonical base: `{canonical_base}` at `{base_commit}`",
        f"- Canonical-base reproduction: `{base_command}` -> {base_result}",
        f"- Final branch: `{branch_commit}`",
        f"- Final branch comparison: `{branch_command}` -> {branch_result}",
        f"- Aggregate ship gate: `{aggregate_command}` -> exit {summary.aggregate_ship_exit_code}",
        "- New or unattributed failures: NONE",
        "- Merge: manual maintainer or user merge required; automatic merge is forbidden.",
        "- Scope: this exception applies only to the recorded ledger and is not precedent for unrelated PRs.",
        "- Normal green-gate policy resumes when the baseline lane is restored.",
        "",
        "### Base-versus-branch failure ledger",
        "",
        "| Failure identity | Base result | Branch result | Owner | Disposition |",
        "|------------------|-------------|---------------|-------|-------------|",
    ]
    for row in rows:
        lines.append(
            f"| {row.failure_identity} | {row.base_result} | {row.branch_result} | "
            f"[issue]({row.owner_issue_url}) | `{row.disposition}` |"
        )
    lines.append("")
    return lines


def render_managed_summary(inputs: SummaryInputs) -> str:
    final_head = inputs.final_head.strip()
    if not final_head:
        raise ValueError("final_head is required")

    grouped: dict[str, list[str]] = {category: [] for category in CATEGORY_ORDER}
    for entry in inputs.changes:
        category = entry.category.strip().title()
        if category not in grouped:
            raise ValueError(f"unsupported change category: {entry.category}")
        text = " ".join(entry.text.split())
        if not text:
            raise ValueError("change entry text is required")
        grouped[category].append(text)

    if not any(grouped.values()):
        raise ValueError("at least one final-diff change entry is required")

    impacts = _clean_items(inputs.user_facing_impacts, "user_facing_impacts")
    breaking = _clean_items(inputs.breaking_changes, "breaking_changes")

    dispositions: list[FindingDispositionEntry] = []
    for finding in inputs.deferred_findings:
        priority = finding.priority.strip().upper()
        if priority not in {"P2", "P3"}:
            raise ValueError("only P2/P3 findings belong in legacy deferred findings")
        title = " ".join(finding.title.split())
        issue_url = finding.issue_url.strip()
        if not title or not issue_url.startswith(("https://", "http://")):
            raise ValueError("deferred findings require a title and open issue URL")
        dispositions.append(
            FindingDispositionEntry(priority, "DEFER_TO_ISSUE", title, issue_url)
        )

    for finding in inputs.finding_dispositions:
        severity = finding.severity.strip().upper()
        disposition = finding.disposition.strip().upper()
        title = " ".join(finding.title.split())
        issue_url = finding.issue_url.strip()
        if severity not in {"P0", "P1", "P2", "P3"}:
            raise ValueError(f"unsupported severity: {finding.severity}")
        if disposition not in VALID_FINDING_DISPOSITIONS:
            raise ValueError(f"unsupported finding disposition: {finding.disposition}")
        if not title:
            raise ValueError("finding disposition title is required")
        if disposition in ISSUE_REQUIRED_DISPOSITIONS:
            if not issue_url.startswith(("https://", "http://")):
                raise ValueError("issue-required dispositions require an open issue URL")
        elif issue_url:
            raise ValueError("non-issue dispositions must not carry an issue URL")
        dispositions.append(FindingDispositionEntry(severity, disposition, title, issue_url))

    if any(character.isspace() for character in final_head):
        raise ValueError("final_head must be one argument-safe revision identifier")

    lines = [
        START_MARKER,
        f"<!-- audit-and-pr:source-head:{final_head} -->",
        "## Change summary",
        "",
    ]
    for category in CATEGORY_ORDER:
        if not grouped[category]:
            continue
        lines.extend([f"### {category}"])
        lines.extend(f"- {item}" for item in grouped[category])
        lines.append("")

    lines.extend(["## User-facing impact"])
    if impacts:
        lines.extend(f"- {item}" for item in impacts)
    else:
        lines.append("- No externally visible behavior change.")
    lines.append("")

    if breaking:
        lines.append("## Breaking changes")
        lines.extend(f"- {item}" for item in breaking)
        lines.append("")

    if dispositions:
        lines.append("## Finding disposition")
        for disposition, heading in DISPOSITION_HEADINGS:
            group = [entry for entry in dispositions if entry.disposition == disposition]
            if not group:
                continue
            lines.append(f"### {heading}")
            for entry in group:
                label = f"{entry.severity}: {entry.title}"
                if entry.issue_url:
                    lines.append(f"- [{label}]({entry.issue_url})")
                else:
                    lines.append(f"- {label}")
            lines.append("")

    if inputs.baseline_restoration is not None:
        lines.extend(_render_baseline_restoration(inputs.baseline_restoration))

    lines.append(END_MARKER)
    return "\n".join(lines)


def upsert_managed_summary(existing_body: str, managed_summary: str) -> str:
    if not managed_summary.startswith(START_MARKER) or not managed_summary.endswith(END_MARKER):
        raise ValueError("managed summary must contain the canonical outer markers")

    start_count = existing_body.count(START_MARKER)
    end_count = existing_body.count(END_MARKER)
    if start_count != end_count or start_count > 1:
        raise ValueError("unmatched or duplicate managed summary markers")

    if start_count == 0:
        body = existing_body.rstrip()
        return f"{body}\n\n{managed_summary}\n" if body else f"{managed_summary}\n"

    start = existing_body.index(START_MARKER)
    end = existing_body.index(END_MARKER, start) + len(END_MARKER)
    return existing_body[:start] + managed_summary + existing_body[end:]


def decide_permanent_changelog(inputs: ChangelogInputs) -> ChangelogDecision:
    convention = inputs.convention.strip().upper()
    if convention not in VALID_CONVENTIONS:
        raise ValueError(f"unsupported changelog convention: {inputs.convention}")

    required = inputs.repository_requires_entry and inputs.change_requires_entry
    if not required:
        return ChangelogDecision(
            status="PR_BODY_ONLY",
            may_modify_repository=False,
            blocks_shipment=False,
            reason="No established repository requirement applies to this change.",
        )

    if convention == "NONE":
        return ChangelogDecision(
            status="BLOCKED_UNDEFINED_CONVENTION",
            may_modify_repository=False,
            blocks_shipment=True,
            reason="A permanent entry is required but no usable convention is defined.",
        )

    if inputs.artifact_present:
        return ChangelogDecision(
            status="VALIDATE_EXISTING",
            may_modify_repository=False,
            blocks_shipment=False,
            reason="Validate the existing required artifact against the final audited diff.",
        )

    if inputs.creation_authorized and inputs.deterministic_format:
        return ChangelogDecision(
            status="CREATE_REQUIRED_ARTIFACT",
            may_modify_repository=True,
            blocks_shipment=False,
            reason="Repository policy authorizes deterministic artifact creation.",
        )

    return ChangelogDecision(
        status="BLOCKED_MISSING_REQUIRED_ARTIFACT",
        may_modify_repository=False,
        blocks_shipment=True,
        reason="Do not invent changelog format, release level, or package impact.",
    )
