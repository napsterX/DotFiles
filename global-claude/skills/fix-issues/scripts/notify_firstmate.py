#!/usr/bin/env python3
"""Non-blocking FirstMate notification adapter for /fix-issues."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

DEFAULT_TIMEOUT_SECONDS = 10
ALLOWED_EVENTS = {"RUN_COMPLETED", "RUN_STOPPED", "MANUAL_ACTION_REQUIRED"}


class NotificationError(ValueError):
    """Raised when notification input is invalid."""


@dataclass(frozen=True)
class NotificationResult:
    status: str
    event: str
    executable: str | None
    protocol: str | None
    exit_code: int | None
    detail: str


def find_firstmate_notify(env: dict[str, str] | None = None) -> str | None:
    values = os.environ if env is None else env
    override = values.get("FIRSTMATE_NOTIFY_BIN")
    if override:
        candidate = Path(override).expanduser()
        return str(candidate.resolve()) if candidate.is_file() and os.access(candidate, os.X_OK) else None
    found = shutil.which("firstmate-notify", path=values.get("PATH"))
    if found:
        return str(Path(found).resolve())
    # A supplied environment is an explicit discovery sandbox. Do not leak the
    # caller process's real home directory into tests or controlled invocations.
    # Normal CLI use passes env=None and still checks the user's actual ~/.local/bin.
    home_value = str(Path.home()) if env is None else values.get("HOME")
    if home_value:
        candidate = Path(home_value).expanduser() / ".local" / "bin" / "firstmate-notify"
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate.resolve())
    return None


def _probe_help(executable: str, timeout_seconds: int) -> str:
    try:
        completed = subprocess.run(
            [executable, "--help"],
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
            env={**os.environ, "NO_COLOR": "1"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return f"{completed.stdout}\n{completed.stderr}".lower()


def build_command(executable: str, title: str, message: str, help_text: str) -> tuple[str, list[str]]:
    has_send = " send " in f" {help_text.replace(chr(10), ' ')} " or "usage: firstmate-notify send" in help_text
    if "--title" in help_text and "--message" in help_text:
        prefix = [executable, "send"] if has_send else [executable]
        return "TITLE_MESSAGE", [*prefix, "--title", title, "--message", message]
    if "--title" in help_text and "--body" in help_text:
        prefix = [executable, "send"] if has_send else [executable]
        return "TITLE_BODY", [*prefix, "--title", title, "--body", message]
    if "--message" in help_text:
        prefix = [executable, "send"] if has_send else [executable]
        return "MESSAGE_ONLY", [*prefix, "--message", f"{title}: {message}"]
    return "POSITIONAL", [executable, f"{title}\n{message}"]


def send_notification(
    event: str,
    title: str,
    message: str,
    *,
    env: dict[str, str] | None = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> NotificationResult:
    if event not in ALLOWED_EVENTS:
        raise NotificationError(f"unsupported notification event: {event}")
    if not title.strip() or not message.strip():
        raise NotificationError("title and message are required")
    executable = find_firstmate_notify(env)
    if not executable:
        return NotificationResult(
            status="NOT_AVAILABLE",
            event=event,
            executable=None,
            protocol=None,
            exit_code=None,
            detail="firstmate-notify was not found; no fallback notifier was used",
        )
    help_text = _probe_help(executable, timeout_seconds)
    protocol, command = build_command(executable, title, message, help_text)
    execution_env = dict(os.environ)
    if env is not None:
        execution_env.update(env)
    try:
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
            env=execution_env,
        )
    except subprocess.TimeoutExpired:
        return NotificationResult(
            status="FAILED_NONBLOCKING",
            event=event,
            executable=executable,
            protocol=protocol,
            exit_code=None,
            detail="firstmate-notify timed out",
        )
    except OSError as exc:
        return NotificationResult(
            status="FAILED_NONBLOCKING",
            event=event,
            executable=executable,
            protocol=protocol,
            exit_code=None,
            detail=f"firstmate-notify could not be executed: {type(exc).__name__}",
        )
    detail = (completed.stderr or completed.stdout).strip()
    if len(detail) > 500:
        detail = detail[:500] + "..."
    return NotificationResult(
        status="DELIVERED" if completed.returncode == 0 else "FAILED_NONBLOCKING",
        event=event,
        executable=executable,
        protocol=protocol,
        exit_code=completed.returncode,
        detail=detail or ("notification accepted" if completed.returncode == 0 else "notification command failed"),
    )


def _main(arguments: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", choices=sorted(ALLOWED_EVENTS), required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--message", required=True)
    args = parser.parse_args(arguments)
    try:
        result = send_notification(args.event, args.title, args.message)
        print(json.dumps(result.__dict__, indent=2, sort_keys=True))
        return 0
    except NotificationError as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(_main())
