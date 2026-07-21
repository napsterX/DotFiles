#!/usr/bin/env python3
"""Safe Repository Verification V1 adapter runner for /audit-and-pr.

The runner does not resolve policy on its own. The skill resolves the canonical
base first and passes that exact value with ``--base``. This helper validates the
resolved base, detects adapter state, invokes the adapter without a shell,
captures evidence, detects contradictory success output, and terminates the
adapter process group on timeout or interruption.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import signal
import stat
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

COUNT_NAMES = ("planned", "executed", "pass", "failure", "unavailable", "advisory")
COUNT_PATTERNS = {
    name: re.compile(rf"(?im)^\s*{name}(?:\s+count)?\s*[:=]\s*(\d+)\b")
    for name in COUNT_NAMES
}
PLANNED_EXECUTED_PATTERN = re.compile(
    r"(?im)^\s*planned\s*/\s*executed\s*[:=]\s*(\d+)\s*/\s*(\d+)\b"
)

# These patterns describe explicit failure statements. They intentionally avoid
# broad keyword-only matching so ordinary explanatory output does not become a
# false blocker.
CONTRADICTION_PATTERNS = (
    ("required check omitted", re.compile(r"(?i)\brequired check(?:s)?\b.*\bomitted\b|\bomitted\b.*\brequired check(?:s)?\b")),
    ("blocking check unavailable", re.compile(r"(?i)\bblocking check(?:s)?\b.*\bunavailable\b|\bunavailable\b.*\bblocking check(?:s)?\b")),
    ("incomplete execution", re.compile(r"(?i)\bincomplete execution\b|\bexecution incomplete\b")),
    ("duplicate terminal results", re.compile(r"(?i)\bduplicate terminal result(?:s)?\b")),
    ("missing terminal results", re.compile(r"(?i)\bmissing terminal result(?:s)?\b")),
    ("reconciliation failure", re.compile(r"(?i)\breconciliation (?:failed|failure|error)\b")),
    ("internal adapter failure", re.compile(r"(?i)\binternal adapter (?:failed|failure|error)\b|\badapter internal (?:failed|failure|error)\b")),
)

GOVERNANCE_EXACT_PATHS = {
    "scripts/verify",
}
GOVERNANCE_PATH_FRAGMENTS = (
    "verification",
    "verify-registry",
    "verify_registry",
    "allowlist",
    "allow-list",
    "baseline",
    "github-minimal",
    "github_minimal",
    "ship-governance",
    "ship_governance",
    "planned-executed",
    "planned_executed",
)


@dataclass
class Counts:
    planned: Optional[int] = None
    executed: Optional[int] = None
    pass_count: Optional[int] = None
    failure: Optional[int] = None
    unavailable: Optional[int] = None
    advisory: Optional[int] = None


@dataclass
class VerificationResult:
    repository: str
    adapter: str
    profile: str
    base: str
    invocation_head: Optional[str]
    final_head: Optional[str]
    command: list[str]
    command_display: str
    mode: str
    status: str
    adapter_exit_code: Optional[int]
    effective_exit_code: int
    duration_seconds: float
    stdout: str
    stderr: str
    counts: Counts = field(default_factory=Counts)
    contradictions: list[str] = field(default_factory=list)
    adapter_present: bool = False
    adapter_valid: bool = False
    timed_out: bool = False
    interrupted: bool = False
    tree_changed: bool = False
    head_changed: bool = False
    governance_sensitive: bool = False
    changed_paths: list[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_json(self) -> str:
        payload = asdict(self)
        # Keep the report terms requested by the skill while avoiding a Python
        # keyword collision in the dataclass field name.
        payload["counts"]["pass"] = payload["counts"].pop("pass_count")
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _run_git(repo: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def _git_head(repo: Path) -> Optional[str]:
    result = _run_git(repo, ["rev-parse", "HEAD"])
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _git_status(repo: Path) -> Optional[bytes]:
    result = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def validate_base(repo: Path, base: str) -> tuple[bool, str]:
    if not base:
        return False, "canonical base is empty"
    result = _run_git(repo, ["rev-parse", "--verify", "--end-of-options", f"{base}^{{commit}}"])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "base is not a valid commit"
        return False, detail
    return True, result.stdout.strip()


def parse_counts(output: str) -> Counts:
    values: dict[str, Optional[int]] = {name: None for name in COUNT_NAMES}
    combined = PLANNED_EXECUTED_PATTERN.search(output)
    if combined:
        values["planned"] = int(combined.group(1))
        values["executed"] = int(combined.group(2))
    for name, pattern in COUNT_PATTERNS.items():
        match = pattern.search(output)
        if match:
            values[name] = int(match.group(1))
    return Counts(
        planned=values["planned"],
        executed=values["executed"],
        pass_count=values["pass"],
        failure=values["failure"],
        unavailable=values["unavailable"],
        advisory=values["advisory"],
    )


def detect_contradictions(output: str, counts: Counts) -> list[str]:
    contradictions: list[str] = []
    if (
        counts.planned is not None
        and counts.executed is not None
        and counts.planned != counts.executed
    ):
        contradictions.append(
            f"planned count {counts.planned} differs from executed count {counts.executed}"
        )
    if counts.failure is not None and counts.failure > 0:
        contradictions.append(f"failure count is {counts.failure} despite exit 0")
    for label, pattern in CONTRADICTION_PATTERNS:
        if pattern.search(output):
            contradictions.append(label)
    return contradictions


def is_governance_sensitive(paths: Iterable[str]) -> bool:
    for raw_path in paths:
        normalized = raw_path.replace("\\", "/").strip().lstrip("./")
        lowered = normalized.lower()
        if lowered in GOVERNANCE_EXACT_PATHS:
            return True
        if lowered.startswith("scripts/verify.") or lowered.startswith("scripts/verify/"):
            return True
        if any(fragment in lowered for fragment in GOVERNANCE_PATH_FRAGMENTS):
            return True
        if lowered.startswith(".github/workflows/") and (
            "verify" in lowered or "ship" in lowered
        ):
            return True
    return False


def repository_verification_allows_audit(result: VerificationResult) -> bool:
    return result.status in {"PASS", "NOT_APPLICABLE"} and result.effective_exit_code == 0


def repository_verification_allows_shipment(
    final_result: VerificationResult,
    *,
    audit_eligible: bool,
) -> bool:
    return audit_eligible and final_result.status in {"PASS", "NOT_APPLICABLE"} and final_result.effective_exit_code == 0


def _terminate_process_group(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except PermissionError:
        process.terminate()
    try:
        process.wait(timeout=2)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    except PermissionError:
        process.kill()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass


def _status_for_exit(exit_code: int) -> str:
    return {
        0: "PASS",
        1: "BLOCKED_REQUIRED_CHECK",
        2: "BLOCKED_INVOCATION",
        3: "BLOCKED_ADAPTER",
        4: "BLOCKED_ENVIRONMENT",
        5: "BLOCKED_INTERRUPTED",
    }.get(exit_code, "BLOCKED_PROTOCOL")


def run_repository_verification(
    repo: Path,
    base: str,
    *,
    timeout_seconds: float = 1800,
    changed_paths: Optional[Sequence[str]] = None,
    extra_env: Optional[Mapping[str, str]] = None,
) -> VerificationResult:
    repo = repo.resolve()
    changed = list(changed_paths or [])
    adapter = repo / "scripts" / "verify"
    command = [str(adapter), "ship", "--base", base]
    display_command = " ".join(shlex.quote(part) for part in ["./scripts/verify", "ship", "--base", base])
    head_before = _git_head(repo)
    status_before = _git_status(repo)
    started = time.monotonic()

    common = dict(
        repository=str(repo),
        adapter="./scripts/verify",
        profile="ship",
        base=base,
        invocation_head=head_before,
        final_head=head_before,
        command=["./scripts/verify", "ship", "--base", base],
        command_display=display_command,
        duration_seconds=0.0,
        stdout="",
        stderr="",
        governance_sensitive=is_governance_sensitive(changed),
        changed_paths=changed,
    )

    if not os.path.lexists(adapter):
        return VerificationResult(
            **common,
            mode="legacy",
            status="NOT_APPLICABLE",
            adapter_exit_code=None,
            effective_exit_code=0,
            adapter_present=False,
            adapter_valid=False,
        )

    if not adapter.is_file():
        return VerificationResult(
            **common,
            mode="adapter",
            status="BLOCKED_CONFIGURATION",
            adapter_exit_code=None,
            effective_exit_code=3,
            adapter_present=True,
            adapter_valid=False,
            error="./scripts/verify exists but is not a regular file",
        )

    mode = adapter.stat().st_mode
    if not (mode & stat.S_IXUSR or mode & stat.S_IXGRP or mode & stat.S_IXOTH):
        return VerificationResult(
            **common,
            mode="adapter",
            status="BLOCKED_CONFIGURATION",
            adapter_exit_code=None,
            effective_exit_code=3,
            adapter_present=True,
            adapter_valid=False,
            error="./scripts/verify exists but is not executable",
        )

    base_valid, base_detail = validate_base(repo, base)
    if not base_valid:
        return VerificationResult(
            **common,
            mode="adapter",
            status="BLOCKED_BASE_RESOLUTION",
            adapter_exit_code=None,
            effective_exit_code=3,
            adapter_present=True,
            adapter_valid=True,
            error=f"resolved base is invalid: {base_detail}",
        )

    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    try:
        process = subprocess.Popen(
            command,
            cwd=str(repo),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            shell=False,
            env=env,
            start_new_session=True,
        )
    except OSError as exc:
        failure = dict(common)
        failure["duration_seconds"] = round(time.monotonic() - started, 6)
        return VerificationResult(
            **failure,
            mode="adapter",
            status="BLOCKED_ADAPTER",
            adapter_exit_code=None,
            effective_exit_code=3,
            adapter_present=True,
            adapter_valid=False,
            error=f"adapter could not be executed: {exc}",
        )

    timed_out = False
    interrupted = False
    stdout = ""
    stderr = ""
    exit_code: Optional[int]
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        exit_code = process.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
        _terminate_process_group(process)
        stdout, stderr = process.communicate()
        stdout = stdout or ""
        stderr = stderr or ""
        exit_code = 5
    except KeyboardInterrupt:
        interrupted = True
        _terminate_process_group(process)
        tail_out, tail_err = process.communicate()
        stdout += tail_out or ""
        stderr += tail_err or ""
        exit_code = 5

    duration = round(time.monotonic() - started, 6)
    head_after = _git_head(repo)
    status_after = _git_status(repo)
    head_changed = head_before != head_after
    tree_changed = status_before != status_after
    combined_output = f"{stdout}\n{stderr}"
    counts = parse_counts(combined_output)
    contradictions = detect_contradictions(combined_output, counts)

    if timed_out:
        status_name = "BLOCKED_TIMEOUT"
        effective_exit = 5
    elif interrupted:
        status_name = "BLOCKED_INTERRUPTED"
        effective_exit = 5
    elif exit_code is None:
        status_name = "BLOCKED_PROTOCOL"
        effective_exit = 3
    elif exit_code < 0:
        status_name = "BLOCKED_INTERRUPTED"
        effective_exit = 5
    elif exit_code == 0 and (contradictions or head_changed or tree_changed):
        if head_changed:
            contradictions.append("adapter changed HEAD while running")
        if tree_changed:
            contradictions.append("adapter changed the repository working tree while running")
        status_name = "BLOCKED_PROTOCOL"
        effective_exit = 3
    else:
        status_name = _status_for_exit(exit_code)
        effective_exit = exit_code if exit_code in {0, 1, 2, 3, 4, 5} else 3

    error: Optional[str] = None
    if timed_out:
        error = f"adapter exceeded timeout of {timeout_seconds:g} seconds"
    elif interrupted:
        error = "adapter invocation was interrupted"
    elif exit_code is not None and exit_code not in {0, 1, 2, 3, 4, 5}:
        error = f"adapter returned unsupported exit code {exit_code}"

    return VerificationResult(
        repository=str(repo),
        adapter="./scripts/verify",
        profile="ship",
        base=base,
        invocation_head=head_before,
        final_head=head_after,
        command=["./scripts/verify", "ship", "--base", base],
        command_display=display_command,
        mode="adapter",
        status=status_name,
        adapter_exit_code=exit_code,
        effective_exit_code=effective_exit,
        duration_seconds=duration,
        stdout=stdout,
        stderr=stderr,
        counts=counts,
        contradictions=contradictions,
        adapter_present=True,
        adapter_valid=True,
        timed_out=timed_out,
        interrupted=interrupted,
        tree_changed=tree_changed,
        head_changed=head_changed,
        governance_sensitive=is_governance_sensitive(changed),
        changed_paths=changed,
        error=error,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--base", required=True)
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=1800,
        help="adapter timeout; use the skill/repository command timeout when defined",
    )
    parser.add_argument(
        "--changed-path",
        action="append",
        default=[],
        help="audited path used to activate verification-governance-sensitive review",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = run_repository_verification(
        args.repo,
        args.base,
        timeout_seconds=args.timeout_seconds,
        changed_paths=args.changed_path,
    )
    print(result.to_json())
    return result.effective_exit_code


if __name__ == "__main__":
    raise SystemExit(main())
