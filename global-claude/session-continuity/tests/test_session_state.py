#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "bin/session_state.py"


class SessionStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="handoff contract "))
        self.repo = self.temp / "repo with spaces"
        self.repo.mkdir()
        self.handoffs = self.temp / "handoffs"
        self.env = {
            **os.environ,
            "CLAUDE_SESSION_HANDOFFS": str(self.handoffs),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        subprocess.run(
            ["git", "init", "-b", "develop", str(self.repo)],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "-C", str(self.repo), "config", "user.email", "t@example.com"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.repo), "config", "user.name", "T"],
            check=True,
        )
        (self.repo / "a.txt").write_text("a\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "a.txt"], check=True)
        subprocess.run(
            ["git", "-C", str(self.repo), "commit", "-m", "init"],
            check=True,
            capture_output=True,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp, ignore_errors=True)

    def cmd(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            env=self.env,
            check=check,
        )

    @staticmethod
    def handoff_text(project_path: str | None = None) -> str:
        project_line = f"\n- Project: `{project_path}`" if project_path else ""
        return (
            "# Claude Code Operational Handoff\n\n"
            "## Handoff Metadata\n"
            "- Schema version: 2"
            f"{project_line}\n\n"
            "## Active Objective\nX\n\n"
            "## Definition of Done\nY\n\n"
            "## Next Exact Action\nZ\n"
        )

    def draft(self) -> Path:
        result = self.cmd("draft-path", "--cwd", str(self.repo))
        path = Path(result.stdout.strip())
        self.assertFalse(path.exists(), "draft-path must not create a placeholder file")
        path.write_text(self.handoff_text(str(self.repo.resolve())))
        return path

    def test_draft_path_is_nonexistent_until_writer_creates_it(self) -> None:
        path = Path(self.cmd("draft-path", "--cwd", str(self.repo)).stdout.strip())
        self.assertFalse(path.exists())
        path.write_text("created once")
        self.assertTrue(path.is_file())

    def test_immediate_publish_then_locate(self) -> None:
        published = json.loads(
            self.cmd(
                "publish",
                "--source",
                str(self.draft()),
                "--cwd",
                str(self.repo),
                "--session-id",
                "s1",
            ).stdout
        )
        located = json.loads(self.cmd("locate", "--cwd", str(self.repo)).stdout)
        self.assertEqual(published["handoff_id"], located["handoff_id"])
        self.assertEqual("CURRENT", located["freshness"])

    def test_new_publish_replaces_old_current(self) -> None:
        first = json.loads(
            self.cmd(
                "publish", "--source", str(self.draft()), "--cwd", str(self.repo)
            ).stdout
        )
        (self.repo / "a.txt").write_text("b\n")
        subprocess.run(
            ["git", "-C", str(self.repo), "commit", "-am", "next"],
            check=True,
            capture_output=True,
        )
        second = json.loads(
            self.cmd(
                "publish", "--source", str(self.draft()), "--cwd", str(self.repo)
            ).stdout
        )
        located = json.loads(self.cmd("locate", "--cwd", str(self.repo)).stdout)
        self.assertNotEqual(first["handoff_id"], second["handoff_id"])
        self.assertEqual(second["handoff_id"], located["handoff_id"])

    def test_hash_mismatch_blocks(self) -> None:
        published = json.loads(
            self.cmd(
                "publish", "--source", str(self.draft()), "--cwd", str(self.repo)
            ).stdout
        )
        Path(published["current_path"]).write_text("tampered")
        result = self.cmd("locate", "--cwd", str(self.repo), check=False)
        self.assertEqual(2, result.returncode)

    def test_realpath_alias_safe(self) -> None:
        canonical = Path(os.path.realpath(self.repo))
        collected = json.loads(
            self.cmd("collect", "--cwd", str(canonical)).stdout
        )
        self.assertTrue(os.path.samefile(collected["worktree_root"], self.repo))

    def test_linked_worktree_family_locates_latest(self) -> None:
        worktree = self.temp / "linked"
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "worktree",
                "add",
                "-b",
                "task",
                str(worktree),
            ],
            check=True,
            capture_output=True,
        )
        published = json.loads(
            self.cmd(
                "publish", "--source", str(self.draft()), "--cwd", str(worktree)
            ).stdout
        )
        located = json.loads(self.cmd("locate", "--cwd", str(self.repo)).stdout)
        self.assertEqual(published["handoff_id"], located["handoff_id"])
        self.assertEqual(str(Path(os.path.realpath(worktree))), located["active_worktree"])


    def test_schema_v1_under_current_key_is_discovered(self) -> None:
        collected = json.loads(self.cmd("collect", "--cwd", str(self.repo)).stdout)
        current_root = Path(collected["storage_directory"])
        current_root.mkdir(parents=True)
        current = current_root / "CURRENT.md"
        current.write_text(self.handoff_text(collected["worktree_root"]))

        located = json.loads(self.cmd("locate", "--cwd", str(self.repo)).stdout)
        self.assertEqual(str(current), located["located_path"])
        self.assertEqual("LEGACY_UNVERIFIED", located["freshness"])

    def test_legacy_schema_v1_project_key_is_discovered(self) -> None:
        collected = json.loads(self.cmd("collect", "--cwd", str(self.repo)).stdout)
        legacy_root = self.handoffs / f"{collected['project_name']}-legacy123456"
        legacy_root.mkdir(parents=True)
        legacy_current = legacy_root / "CURRENT.md"
        legacy_current.write_text(self.handoff_text(collected["worktree_root"]))

        located = json.loads(self.cmd("locate", "--cwd", str(self.repo)).stdout)
        self.assertEqual(str(legacy_current), located["located_path"])
        self.assertEqual("LEGACY_UNVERIFIED", located["freshness"])
        self.assertTrue(located["migration_required"])

    def test_legacy_schema_v2_project_key_is_discovered(self) -> None:
        published = json.loads(
            self.cmd(
                "publish", "--source", str(self.draft()), "--cwd", str(self.repo)
            ).stdout
        )
        current_root = Path(published["current_path"]).parent
        legacy_root = self.handoffs / f"{published['project_key']}-legacy"
        current_root.rename(legacy_root)

        for name in ("CURRENT.json", "LATEST.json"):
            path = legacy_root / name
            metadata = json.loads(path.read_text())
            metadata["project_key"] = legacy_root.name
            metadata["current_path"] = str(legacy_root / "CURRENT.md")
            metadata["archive_path"] = str(legacy_root / "archive" / Path(metadata["archive_path"]).name)
            path.write_text(json.dumps(metadata, indent=2))

        located = json.loads(self.cmd("locate", "--cwd", str(self.repo)).stdout)
        self.assertEqual(published["handoff_id"], located["handoff_id"])
        self.assertEqual(legacy_root.name, located["legacy_project_key"])
        self.assertTrue(located["migration_required"])

    def test_multiple_legacy_candidates_block_selection(self) -> None:
        collected = json.loads(self.cmd("collect", "--cwd", str(self.repo)).stdout)
        for suffix in ("old-one", "old-two"):
            root = self.handoffs / f"{collected['project_name']}-{suffix}"
            root.mkdir(parents=True)
            (root / "CURRENT.md").write_text(
                self.handoff_text(collected["worktree_root"])
            )

        result = self.cmd("locate", "--cwd", str(self.repo), check=False)
        self.assertEqual(2, result.returncode)
        self.assertIn("multiple legacy handoff directories", result.stderr)

    def test_same_project_name_elsewhere_is_not_matched(self) -> None:
        other_parent = self.temp / "other"
        other_repo = other_parent / self.repo.name
        other_repo.mkdir(parents=True)
        subprocess.run(
            ["git", "init", "-b", "main", str(other_repo)],
            check=True,
            capture_output=True,
        )
        collected = json.loads(self.cmd("collect", "--cwd", str(self.repo)).stdout)
        root = self.handoffs / f"{collected['project_name']}-unrelated"
        root.mkdir(parents=True)
        (root / "CURRENT.md").write_text(self.handoff_text(str(other_repo.resolve())))

        result = self.cmd("locate", "--cwd", str(self.repo), check=False)
        self.assertEqual(1, result.returncode)


if __name__ == "__main__":
    unittest.main()
