#!/usr/bin/env python3
"""Pure lane-planning logic for /audit-and-pr parallel read-only audits.

The skill documentation remains authoritative. This helper makes the automatic
parallelism decision executable and testable. It never starts agents or mutates a
repository.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import PurePosixPath
from typing import Literal, Sequence

Risk = Literal["LOW", "MEDIUM", "HIGH"]
ExecutionMode = Literal["SEQUENTIAL", "PARALLEL"]

DOC_EXTENSIONS = {
    ".md", ".mdx", ".txt", ".rst", ".adoc", ".png", ".jpg", ".jpeg", ".gif", ".svg",
}
DOC_PATH_PREFIXES = ("docs/", "documentation/")
DOC_FILENAMES = {
    "readme", "readme.md", "changelog", "changelog.md", "license", "license.md",
    "contributing.md", "code_of_conduct.md",
}


@dataclass(frozen=True)
class ParallelismInputs:
    changed_paths: tuple[str, ...] = ()
    risk: Risk = "MEDIUM"
    affected_domains: int = 1
    governance_sensitive: bool = False
    host_supports_parallel: bool = True
    explicit_mode: Literal["AUTO", "SEQUENTIAL", "PARALLEL"] = "AUTO"


@dataclass(frozen=True)
class AuditLane:
    lane_id: str
    focus: str
    read_only: bool = True


@dataclass(frozen=True)
class ParallelismPlan:
    execution_mode: ExecutionMode
    max_workers: int
    lanes: tuple[AuditLane, ...] = field(default_factory=tuple)
    changed_file_count: int = 0
    docs_only: bool = False
    reason: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def _normalized(path: str) -> str:
    return path.replace("\\", "/").strip().lstrip("./").lower()


def is_docs_only(paths: Sequence[str]) -> bool:
    if not paths:
        return False
    for raw in paths:
        path = _normalized(raw)
        pure = PurePosixPath(path)
        if path.startswith(DOC_PATH_PREFIXES):
            continue
        if pure.name in DOC_FILENAMES:
            continue
        if pure.suffix in DOC_EXTENSIONS:
            continue
        return False
    return True


def _standard_lanes(count: int) -> list[AuditLane]:
    if count <= 1:
        return [
            AuditLane(
                "integrated",
                "all audit dimensions with one authoritative read-only reviewer",
            )
        ]
    if count == 2:
        return [
            AuditLane(
                "correctness-security",
                "objective coverage, logic, interfaces, failure behavior, auth, tenancy, privacy, and data safety",
            ),
            AuditLane(
                "architecture-evidence",
                "architecture, migrations, operations, rollback, tests, CI enforcement, and governance sufficiency",
            ),
        ]
    return [
        AuditLane(
            "correctness-behavior",
            "objective coverage, logical correctness, interfaces, state transitions, failure behavior, concurrency, and compatibility",
        ),
        AuditLane(
            "security-data-boundaries",
            "authentication, authorization, tenancy, privacy, secrets, persistence, migrations, and destructive boundaries",
        ),
        AuditLane(
            "architecture-evidence-operations",
            "architecture, evidence sufficiency, tests, CI enforcement, observability, recovery, rollout, rollback, docs, and governance",
        ),
    ]


def plan_parallelism(inputs: ParallelismInputs) -> ParallelismPlan:
    paths = tuple(path for path in inputs.changed_paths if path.strip())
    file_count = len(paths)
    docs_only = is_docs_only(paths)

    if inputs.explicit_mode == "SEQUENTIAL" or not inputs.host_supports_parallel:
        reason = (
            "parallel execution was explicitly disabled"
            if inputs.explicit_mode == "SEQUENTIAL"
            else "the host does not support concurrent read-only audit workers"
        )
        return ParallelismPlan(
            execution_mode="SEQUENTIAL",
            max_workers=1,
            lanes=tuple(_standard_lanes(1)),
            changed_file_count=file_count,
            docs_only=docs_only,
            reason=reason,
        )

    if inputs.explicit_mode == "PARALLEL":
        base_lane_count = 3
    elif docs_only or (
        file_count <= 5
        and inputs.risk == "LOW"
        and inputs.affected_domains <= 1
        and not inputs.governance_sensitive
    ):
        base_lane_count = 1
    elif (
        file_count > 20
        or inputs.risk == "HIGH"
        or inputs.affected_domains >= 3
    ):
        base_lane_count = 3
    else:
        base_lane_count = 2

    lanes = _standard_lanes(base_lane_count)
    if inputs.governance_sensitive:
        lanes.append(
            AuditLane(
                "verification-governance",
                "adapter/profile changes, required-check membership, skip/applicability logic, baselines, thresholds, timeouts, exit codes, and false-green paths",
            )
        )

    # Four is the hard ceiling. If explicit parallel mode plus governance would
    # exceed it, retain all three standard lanes and one governance lane.
    lanes = lanes[:4]
    mode: ExecutionMode = "PARALLEL" if len(lanes) > 1 else "SEQUENTIAL"
    reason = (
        "small or documentation-only change; concurrency overhead would exceed useful work"
        if len(lanes) == 1
        else f"auto-selected {len(lanes)} read-only audit lanes for the change size, risk, domains, and governance sensitivity"
    )
    return ParallelismPlan(
        execution_mode=mode,
        max_workers=len(lanes),
        lanes=tuple(lanes),
        changed_file_count=file_count,
        docs_only=docs_only,
        reason=reason,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--risk", choices=("LOW", "MEDIUM", "HIGH"), default="MEDIUM")
    parser.add_argument("--affected-domains", type=int, default=1)
    parser.add_argument("--governance-sensitive", action="store_true")
    parser.add_argument("--no-parallel-host", action="store_true")
    parser.add_argument("--mode", choices=("AUTO", "SEQUENTIAL", "PARALLEL"), default="AUTO")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    plan = plan_parallelism(
        ParallelismInputs(
            changed_paths=tuple(args.path),
            risk=args.risk,
            affected_domains=max(1, args.affected_domains),
            governance_sensitive=args.governance_sensitive,
            host_supports_parallel=not args.no_parallel_host,
            explicit_mode=args.mode,
        )
    )
    print(plan.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
