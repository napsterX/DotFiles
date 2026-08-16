#!/usr/bin/env python3
import base64
import json
import os
import sys
import time
from pathlib import Path

PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Zlm8AAAAASUVORK5CYII="
)

args = sys.argv[1:]
log = os.environ.get("FAKE_ARGV_LOG")
if log:
    Path(log).parent.mkdir(parents=True, exist_ok=True)
    with Path(log).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(args) + "\n")

sleep = float(os.environ.get("FAKE_SLEEP_SECONDS", "0"))
if sleep:
    time.sleep(sleep)

state = os.environ.get("FAKE_FAIL_ONCE_STATE")
if state:
    p = Path(state)
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("failed-once\n", encoding="utf-8")
        print("intentional first failure", file=sys.stderr)
        raise SystemExit(9)

try:
    idx = args.index("--output")
    output = Path(args[idx + 1])
except (ValueError, IndexError):
    print("missing --output", file=sys.stderr)
    raise SystemExit(7)

output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(PNG_1X1)
print(f"wrote {output}")
