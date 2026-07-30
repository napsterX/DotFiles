#!/usr/bin/env python3
"""Resolve and classify an audit target Git worktree without switching sessions."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


class WorktreeError(RuntimeError):
    pass


def run_git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(cwd), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise WorktreeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def canonical(path: str | Path) -> Path:
    return Path(os.path.realpath(os.fspath(path)))


@dataclass(frozen=True)
class Entry:
    path: Path
    head: str
    branch_ref: str | None
    detached: bool

    @property
    def branch(self) -> str | None:
        prefix = "refs/heads/"
        if self.branch_ref and self.branch_ref.startswith(prefix):
            return self.branch_ref[len(prefix):]
        return self.branch_ref


def parse_worktrees(text: str) -> list[Entry]:
    entries: list[Entry] = []
    block: dict[str, str | bool] = {}
    for line in [*text.splitlines(), ""]:
        if not line:
            if block:
                if "worktree" not in block or "HEAD" not in block:
                    raise WorktreeError("malformed git worktree list output")
                entries.append(
                    Entry(
                        path=canonical(str(block["worktree"])),
                        head=str(block["HEAD"]),
                        branch_ref=str(block["branch"]) if "branch" in block else None,
                        detached=bool(block.get("detached", False)),
                    )
                )
                block = {}
            continue
        key, _, value = line.partition(" ")
        block[key] = value if value else True
    return entries


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


@dataclass(frozen=True)
class Resolution:
    invocation_root: str
    task_root: str
    git_common_directory: str
    target_branch: str | None
    target_head: str
    worktree_class: str
    execution_mode: str
    enter_worktree_allowed: bool
    enter_worktree_should_be_attempted: bool
    registered: bool


def resolve(invocation: Path, target_path: Path | None, target_branch: str | None) -> Resolution:
    invocation_root = canonical(run_git(invocation, "rev-parse", "--show-toplevel"))
    common_raw = run_git(invocation_root, "rev-parse", "--git-common-dir")
    common = canonical(common_raw if os.path.isabs(common_raw) else invocation_root / common_raw)
    entries = parse_worktrees(run_git(invocation_root, "worktree", "list", "--porcelain"))
    if not entries:
        raise WorktreeError("repository has no registered worktrees")

    if target_path is not None:
        wanted = canonical(target_path)
        matches = [e for e in entries if e.path == wanted]
        if not matches:
            raise WorktreeError(f"target path is not a registered worktree: {wanted}")
    elif target_branch:
        matches = [e for e in entries if e.branch == target_branch or e.branch_ref == target_branch]
        if not matches:
            raise WorktreeError(f"target branch is not checked out in a registered worktree: {target_branch}")
    else:
        matches = [e for e in entries if e.path == invocation_root]

    if len(matches) != 1:
        raise WorktreeError(f"target worktree is ambiguous: {len(matches)} matches")
    target = matches[0]

    target_common_raw = run_git(target.path, "rev-parse", "--git-common-dir")
    target_common = canonical(target_common_raw if os.path.isabs(target_common_raw) else target.path / target_common_raw)
    if target_common != common:
        raise WorktreeError("target worktree belongs to a different Git common directory")

    primary = entries[0].path
    managed_parent = canonical(primary / ".claude" / "worktrees")
    if target.path == invocation_root:
        worktree_class = "CURRENT"
        execution_mode = "IN_PLACE"
        allowed = False
    elif is_relative_to(target.path, managed_parent):
        worktree_class = "CLAUDE_MANAGED"
        execution_mode = "PINNED_TASK_ROOT"
        allowed = True
    else:
        worktree_class = "EXTERNAL_REGISTERED"
        execution_mode = "PINNED_TASK_ROOT"
        allowed = False

    return Resolution(
        invocation_root=str(invocation_root),
        task_root=str(target.path),
        git_common_directory=str(common),
        target_branch=target.branch,
        target_head=target.head,
        worktree_class=worktree_class,
        execution_mode=execution_mode,
        enter_worktree_allowed=allowed,
        enter_worktree_should_be_attempted=False,
        registered=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--invocation-root", type=Path, required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--target-path", type=Path)
    group.add_argument("--target-branch")
    args = parser.parse_args()
    try:
        result = resolve(args.invocation_root, args.target_path, args.target_branch)
    except WorktreeError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps({"status": "OK", **asdict(result)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
