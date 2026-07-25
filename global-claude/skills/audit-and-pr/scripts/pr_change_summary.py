#!/usr/bin/env python3
"""Deterministic contracts for audit-and-pr PR summaries and changelog handling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

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


@dataclass(frozen=True)
class ChangeEntry:
    category: str
    text: str


@dataclass(frozen=True)
class DeferredFinding:
    priority: str
    title: str
    issue_url: str


@dataclass(frozen=True)
class SummaryInputs:
    final_head: str
    changes: tuple[ChangeEntry, ...]
    user_facing_impacts: tuple[str, ...] = ()
    breaking_changes: tuple[str, ...] = ()
    deferred_findings: tuple[DeferredFinding, ...] = ()


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

    deferred: list[DeferredFinding] = []
    for finding in inputs.deferred_findings:
        priority = finding.priority.strip().upper()
        if priority not in {"P2", "P3"}:
            raise ValueError("only P2/P3 findings belong in Deferred findings")
        title = " ".join(finding.title.split())
        issue_url = finding.issue_url.strip()
        if not title or not issue_url.startswith(("https://", "http://")):
            raise ValueError("deferred findings require a title and open issue URL")
        deferred.append(DeferredFinding(priority, title, issue_url))

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

    if deferred:
        lines.append("## Deferred findings")
        for finding in deferred:
            lines.append(
                f"- [{finding.priority}: {finding.title}]({finding.issue_url})"
            )
        lines.append("")

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
