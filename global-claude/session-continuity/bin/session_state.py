#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

MAX_BYTES = 32768
REQUIRED_SECTIONS = (
    "## Handoff Metadata",
    "## Active Objective",
    "## Definition of Done",
    "## Next Exact Action",
)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(
        r"(?i)\b(?:api[_-]?key|token|secret|password)\s*[:=]\s*[^<\s][^\s]{7,}"
    ),
)


def run_git(cwd: Path, *args: str) -> tuple[int, str, str]:
    process = subprocess.run(
        ["git", "-C", str(cwd), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    return process.returncode, process.stdout.strip(), process.stderr.strip()


def real(path: Path) -> Path:
    return Path(os.path.realpath(path))


def repo_identity(cwd: Path) -> dict:
    cwd = real(cwd)
    rc, top, _ = run_git(cwd, "rev-parse", "--show-toplevel")
    if rc != 0:
        key = hashlib.sha256(str(cwd).encode()).hexdigest()[:12]
        return {
            "is_git": False,
            "invocation_directory": str(cwd),
            "worktree_root": str(cwd),
            "repository_family": str(cwd),
            "project_name": cwd.name,
            "project_key": f"{cwd.name}-{key}",
            "branch": None,
            "head": None,
            "status": [],
            "common_dir": None,
        }

    worktree = real(Path(top))
    _, common, _ = run_git(worktree, "rev-parse", "--git-common-dir")
    common_path = Path(common)
    if not common_path.is_absolute():
        common_path = worktree / common_path
    common_real = real(common_path)

    family_source = str(common_real)
    key = hashlib.sha256(family_source.encode()).hexdigest()[:12]
    name = common_real.parent.name if common_real.name == ".git" else common_real.name

    _, branch, _ = run_git(worktree, "branch", "--show-current")
    rc_head, head, _ = run_git(worktree, "rev-parse", "HEAD")
    rc_status, status, _ = run_git(worktree, "status", "--porcelain=v1", "-uall")

    return {
        "is_git": True,
        "invocation_directory": str(cwd),
        "worktree_root": str(worktree),
        "repository_family": family_source,
        "common_dir": str(common_real),
        "project_name": name,
        "project_key": f"{name}-{key}",
        "branch": branch or "DETACHED",
        "head": head if rc_head == 0 else None,
        "status": status.splitlines() if rc_status == 0 and status else [],
    }


def handoffs_base() -> Path:
    return Path(
        os.environ.get(
            "CLAUDE_SESSION_HANDOFFS",
            Path.home() / ".claude/session-handoffs",
        )
    )


def storage_root(state: dict) -> Path:
    return handoffs_base() / state["project_key"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as file_handle:
            file_handle.write(data)
            file_handle.flush()
            os.fsync(file_handle.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def legacy_candidates(state: dict) -> list[Path]:
    """Find older project-key directories that plausibly belong to this repository.

    Schema-v2 candidates are matched by repository-family or canonical worktree.
    Schema-v1 candidates are accepted only when their Markdown contains the exact
    canonical worktree or repository-family path. This avoids matching repositories
    solely because they share a display name.
    """

    base = handoffs_base()
    current = storage_root(state)
    if not base.is_dir():
        return []

    candidates: list[Path] = []
    for root in sorted(base.glob(f"{state['project_name']}-*")):
        if not root.is_dir() or real(root) == real(current):
            continue

        current_md = root / "CURRENT.md"
        if not current_md.is_file():
            continue

        current_json = root / "CURRENT.json"
        if current_json.is_file():
            try:
                metadata = json.loads(current_json.read_text())
            except Exception:
                continue

            family = metadata.get("repository_family")
            active_worktree = metadata.get("active_worktree")
            family_matches = bool(family and real(Path(family)) == real(Path(state["repository_family"])))
            worktree_matches = bool(
                active_worktree
                and Path(active_worktree).exists()
                and os.path.samefile(active_worktree, state["worktree_root"])
            )
            if family_matches or worktree_matches:
                candidates.append(root)
            continue

        try:
            text = current_md.read_text(errors="replace")
        except OSError:
            continue

        exact_paths = {
            state["worktree_root"],
            state["repository_family"],
            state["invocation_directory"],
        }
        if any(path and path in text for path in exact_paths):
            candidates.append(root)

    return candidates


def cmd_collect(args: argparse.Namespace) -> int:
    state = repo_identity(Path(args.cwd))
    state["session_id"] = args.session_id
    state["collected_at"] = datetime.now(timezone.utc).isoformat()
    state["storage_directory"] = str(storage_root(state))
    state["legacy_storage_candidates"] = [str(path) for path in legacy_candidates(state)]
    print(json.dumps(state, indent=2))
    return 0


def cmd_draft(args: argparse.Namespace) -> int:
    """Return a unique draft path without creating a placeholder file.

    Claude Code's Write tool treats an existing unread file as an overwrite and can
    reject the first write. Returning a non-existent path lets Write create it once.
    """

    state = repo_identity(Path(args.cwd))
    drafts = storage_root(state) / "drafts"
    drafts.mkdir(parents=True, exist_ok=True)

    for _ in range(128):
        candidate = drafts / f"{args.kind}-{secrets.token_hex(8)}.md"
        if not candidate.exists():
            print(candidate)
            return 0

    print("could not allocate a unique draft path", file=sys.stderr)
    return 2


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return ["file does not exist"]

    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        errors.append(f"file exceeds {MAX_BYTES} bytes")

    text = data.decode("utf-8", errors="replace")
    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"missing section: {section}")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            errors.append("possible secret or private key detected")
    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    errors = validate(Path(args.file))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("VALID")
    return 0


def cmd_publish(args: argparse.Namespace) -> int:
    source = Path(args.source)
    errors = validate(source)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    before = repo_identity(Path(args.cwd))
    root = storage_root(before)
    archive = root / "archive"
    archive.mkdir(parents=True, exist_ok=True)

    handoff_id = (
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-"
        f"{secrets.token_hex(6)}"
    )
    content = source.read_bytes()
    content_hash = hashlib.sha256(content).hexdigest()
    now = datetime.now(timezone.utc).isoformat()

    archive_md = archive / f"{handoff_id}.md"
    archive_json = archive / f"{handoff_id}.json"
    current_md = root / "CURRENT.md"
    current_json = root / "CURRENT.json"
    latest_json = root / "LATEST.json"

    legacy = legacy_candidates(before)
    metadata = {
        "schema_version": 2,
        "handoff_id": handoff_id,
        "generated_at": now,
        "source_session_id": args.session_id,
        "label": args.label or None,
        "project_key": before["project_key"],
        "repository_family": before["repository_family"],
        "invocation_directory": before["invocation_directory"],
        "active_worktree": before["worktree_root"],
        "branch": before["branch"],
        "head": before["head"],
        "status": before["status"],
        "content_sha256": content_hash,
        "archive_path": str(archive_md),
        "current_path": str(current_md),
        "legacy_predecessor_roots": [str(path) for path in legacy],
    }

    atomic_write(archive_md, content)
    atomic_write(archive_json, json.dumps(metadata, indent=2).encode())
    atomic_write(current_md, content)
    atomic_write(current_json, json.dumps(metadata, indent=2).encode())
    atomic_write(latest_json, json.dumps(metadata, indent=2).encode())

    after = repo_identity(Path(args.cwd))
    problems: list[str] = []
    if (
        before["worktree_root"] != after["worktree_root"]
        or before["head"] != after["head"]
        or before["status"] != after["status"]
    ):
        problems.append("repository state changed during publication")
    if sha256_file(current_md) != content_hash or sha256_file(archive_md) != content_hash:
        problems.append("published content hash mismatch")

    located = json.loads(current_json.read_text())
    if located.get("handoff_id") != handoff_id:
        problems.append("current pointer does not reference published handoff")

    if problems:
        print("; ".join(problems), file=sys.stderr)
        return 2

    receipt = {**metadata, "status": "PUBLISHED_AND_VERIFIED"}
    print(json.dumps(receipt, indent=2))
    return 0


def locate_v2(root: Path, state: dict) -> tuple[int, dict | None, str | None]:
    latest = root / "LATEST.json"
    current = root / "CURRENT.md"
    metadata_path = root / "CURRENT.json"
    if not current.is_file() or not metadata_path.is_file() or not latest.is_file():
        return 1, None, None

    try:
        metadata = json.loads(metadata_path.read_text())
        latest_metadata = json.loads(latest.read_text())
    except Exception as error:
        return 2, None, f"invalid handoff metadata: {error}"

    problems: list[str] = []
    if metadata.get("handoff_id") != latest_metadata.get("handoff_id"):
        problems.append("CURRENT and LATEST handoff IDs differ")
    if sha256_file(current) != metadata.get("content_sha256"):
        problems.append("CURRENT content hash mismatch")

    archive_path = Path(metadata.get("archive_path", ""))
    if not archive_path.is_file() or sha256_file(archive_path) != metadata.get("content_sha256"):
        problems.append("archive missing or hash mismatch")

    recorded_family = metadata.get("repository_family")
    if not recorded_family or real(Path(recorded_family)) != real(Path(state["repository_family"])):
        problems.append("repository-family mismatch")

    if problems:
        return 2, None, "; ".join(problems)

    output = {
        **metadata,
        "located_path": str(current),
        "selection_method": "repository-family latest verified handoff",
        "current_invocation_directory": state["invocation_directory"],
        "current_worktree": state["worktree_root"],
        "current_head": state["head"],
        "freshness": (
            "CURRENT"
            if metadata.get("active_worktree") == state["worktree_root"]
            and metadata.get("head") == state["head"]
            else "DRIFT_REQUIRES_REVIEW"
        ),
    }
    return 0, output, None


def locate_legacy(root: Path, state: dict) -> dict:
    current = root / "CURRENT.md"
    return {
        "schema_version": 1,
        "handoff_id": None,
        "project_key": root.name,
        "located_path": str(current),
        "selection_method": "legacy project-key compatibility scan",
        "current_invocation_directory": state["invocation_directory"],
        "current_worktree": state["worktree_root"],
        "current_head": state["head"],
        "freshness": "LEGACY_UNVERIFIED",
        "migration_required": True,
    }


def cmd_locate(args: argparse.Namespace) -> int:
    state = repo_identity(Path(args.cwd))
    current_root = storage_root(state)

    result, output, error = locate_v2(current_root, state)
    if result == 0 and output is not None:
        print(json.dumps(output, indent=2))
        return 0
    if result == 2:
        print(error, file=sys.stderr)
        return 2

    # A schema-v1 handoff may already live under the current key. Prefer that
    # exact repository directory before scanning older key variants.
    if (current_root / "CURRENT.md").is_file():
        print(json.dumps(locate_legacy(current_root, state), indent=2))
        return 0

    candidates = legacy_candidates(state)
    if not candidates:
        return 1
    if len(candidates) > 1:
        print(
            "multiple legacy handoff directories match this repository: "
            + ", ".join(str(path) for path in candidates),
            file=sys.stderr,
        )
        return 2

    legacy_root = candidates[0]
    legacy_result, legacy_output, legacy_error = locate_v2(legacy_root, state)
    if legacy_result == 0 and legacy_output is not None:
        legacy_output["selection_method"] = "legacy project-key v2 compatibility scan"
        legacy_output["legacy_project_key"] = legacy_root.name
        legacy_output["migration_required"] = True
        print(json.dumps(legacy_output, indent=2))
        return 0
    if legacy_result == 2:
        print(legacy_error, file=sys.stderr)
        return 2

    print(json.dumps(locate_legacy(legacy_root, state), indent=2))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    for name in ("collect", "draft-path", "locate"):
        command = subparsers.add_parser(name)
        command.add_argument("--cwd", required=True)
        command.add_argument("--kind", default="handoff")
        command.add_argument("--session-id", default="")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--kind", default="handoff")
    validate_parser.add_argument("--file", required=True)

    publish_parser = subparsers.add_parser("publish")
    publish_parser.add_argument("--kind", default="handoff")
    publish_parser.add_argument("--source", required=True)
    publish_parser.add_argument("--cwd", required=True)
    publish_parser.add_argument("--session-id", default="")
    publish_parser.add_argument("--label", default="")

    args = parser.parse_args()
    functions = {
        "collect": cmd_collect,
        "draft-path": cmd_draft,
        "validate": cmd_validate,
        "publish": cmd_publish,
        "locate": cmd_locate,
    }
    raise SystemExit(functions[args.cmd](args))


if __name__ == "__main__":
    main()
