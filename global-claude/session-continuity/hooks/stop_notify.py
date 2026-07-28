#!/usr/bin/env python3
"""Fire a macOS notification (with sound) naming the repo on Stop."""
from __future__ import annotations

import json
import os
import subprocess
import sys


FIRSTMATE_NOTIFIER = os.path.expanduser(
    "~/Applications/First Mate Reporting.app/Contents/MacOS/terminal-notifier"
)


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}

    cwd = (event.get("cwd") if isinstance(event, dict) else None) or os.getcwd()
    name = os.path.basename(cwd.rstrip("/")) or "Claude Code"

    # The firstmate session itself takes a turn every time it relays a watched
    # pane's status, which would otherwise fire a second, redundant banner
    # right alongside the pane's own. Skip firstmate entirely rather than
    # notify on every relay.
    if name == "firstmate":
        return 0

    notifier_bin = FIRSTMATE_NOTIFIER if os.path.exists(FIRSTMATE_NOTIFIER) else "terminal-notifier"

    notified = False
    try:
        result = subprocess.run(
            [
                notifier_bin,
                "-title", name,
                "-subtitle", "⚓️ First mate reporting",
                "-message", "Turn complete — awaiting your command.",
                "-sound", "Glass",
                "-group", f"claude-{name}",
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        notified = result.returncode == 0
    except Exception:
        notified = False

    if not notified:
        try:
            subprocess.run(
                [
                    "osascript", "-e",
                    'display notification "Turn complete - awaiting your command." '
                    'with title "%s" subtitle "First mate reporting" sound name "Glass"'
                    % name.replace('"', "'"),
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
