#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import stat
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "notify_firstmate.py"
spec = importlib.util.spec_from_file_location("notify_firstmate", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class FirstMateNotificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="firstmate notify ")
        self.root = Path(self.temp.name)
        self.log = self.root / "argv.json"

    def tearDown(self):
        self.temp.cleanup()

    def fake(self, help_text: str, exit_code: int = 0) -> Path:
        path = self.root / "firstmate-notify"
        path.write_text(
            textwrap.dedent(
                f"""\
                #!{sys.executable}
                import json, os, sys
                if '--help' in sys.argv:
                    print({help_text!r})
                    raise SystemExit(0)
                with open(os.environ['NOTIFY_ARGV_LOG'], 'w', encoding='utf-8') as handle:
                    json.dump(sys.argv[1:], handle)
                raise SystemExit({exit_code})
                """
            ),
            encoding="utf-8",
        )
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def env(self, executable: Path):
        return {
            "FIRSTMATE_NOTIFY_BIN": str(executable),
            "NOTIFY_ARGV_LOG": str(self.log),
            "PATH": os.environ.get("PATH", ""),
        }

    def test_01_missing_cli_is_nonblocking_and_uses_no_fallback(self):
        result = module.send_notification(
            "RUN_COMPLETED",
            "Done",
            "Three issues fixed",
            env={"PATH": "", "HOME": str(self.root)},
        )
        self.assertEqual("NOT_AVAILABLE", result.status)
        self.assertIn("no fallback", result.detail)


    def test_02_home_fallback_uses_supplied_environment_only(self):
        executable = self.root / ".local" / "bin" / "firstmate-notify"
        executable.parent.mkdir(parents=True)
        source = self.fake("usage: firstmate-notify TEXT")
        source.replace(executable)
        result = module.send_notification(
            "RUN_COMPLETED",
            "Done",
            "Three fixed",
            env={
                "PATH": "",
                "HOME": str(self.root),
                "NOTIFY_ARGV_LOG": str(self.log),
            },
        )
        self.assertEqual("DELIVERED", result.status)
        self.assertTrue(os.path.samefile(executable, result.executable))

    def test_03_title_message_protocol(self):
        executable = self.fake("usage: firstmate-notify --title X --message Y")
        result = module.send_notification(
            "RUN_COMPLETED", "Done", "Three fixed", env=self.env(executable)
        )
        self.assertEqual("DELIVERED", result.status)
        self.assertEqual(["--title", "Done", "--message", "Three fixed"], json.loads(self.log.read_text()))

    def test_04_title_body_protocol(self):
        executable = self.fake("usage: firstmate-notify send --title X --body Y")
        result = module.send_notification(
            "RUN_STOPPED", "Stopped", "GitHub unavailable", env=self.env(executable)
        )
        self.assertEqual("TITLE_BODY", result.protocol)
        self.assertEqual(
            ["send", "--title", "Stopped", "--body", "GitHub unavailable"],
            json.loads(self.log.read_text()),
        )

    def test_05_positional_fallback_is_still_firstmate_only(self):
        executable = self.fake("usage: firstmate-notify TEXT")
        result = module.send_notification(
            "MANUAL_ACTION_REQUIRED", "Review", "PR ready", env=self.env(executable)
        )
        self.assertEqual("POSITIONAL", result.protocol)
        self.assertEqual(["Review\nPR ready"], json.loads(self.log.read_text()))

    def test_06_cli_failure_is_nonblocking(self):
        executable = self.fake("usage: firstmate-notify TEXT", exit_code=7)
        result = module.send_notification(
            "RUN_STOPPED", "Stopped", "Blocked", env=self.env(executable)
        )
        self.assertEqual("FAILED_NONBLOCKING", result.status)
        self.assertEqual(7, result.exit_code)

    def test_07_invalid_event_is_rejected(self):
        executable = self.fake("usage: firstmate-notify TEXT")
        with self.assertRaises(module.NotificationError):
            module.send_notification("ISSUE_FIXED", "Title", "Message", env=self.env(executable))


if __name__ == "__main__":
    unittest.main()
