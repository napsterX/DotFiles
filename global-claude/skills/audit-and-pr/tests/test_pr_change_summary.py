#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "pr_change_summary.py"
spec = importlib.util.spec_from_file_location("pr_change_summary", HELPER)
assert spec and spec.loader
pcs = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = pcs
spec.loader.exec_module(pcs)


class PrChangeSummaryTests(unittest.TestCase):
    def render(self, **kwargs):
        return pcs.render_managed_summary(pcs.SummaryInputs(**kwargs))

    def decide(self, **kwargs):
        return pcs.decide_permanent_changelog(pcs.ChangelogInputs(**kwargs))

    def test_requires_final_head(self):
        with self.assertRaises(ValueError):
            self.render(
                final_head="",
                changes=(pcs.ChangeEntry("Changed", "Updated behavior"),),
            )

    def test_omits_empty_change_categories(self):
        result = self.render(
            final_head="abc123",
            changes=(pcs.ChangeEntry("Fixed", "Prevented duplicate retries"),),
        )
        self.assertIn("<!-- audit-and-pr:source-head:abc123 -->", result)
        self.assertIn("### Fixed", result)
        self.assertNotIn("### Added", result)
        self.assertNotIn("### Removed", result)

    def test_default_user_impact_is_explicit(self):
        result = self.render(
            final_head="abc123",
            changes=(pcs.ChangeEntry("Changed", "Refactored internal routing"),),
        )
        self.assertIn("No externally visible behavior change.", result)

    def test_breaking_heading_appears_only_when_needed(self):
        without = self.render(
            final_head="abc123",
            changes=(pcs.ChangeEntry("Changed", "Updated routing"),),
        )
        with_breaking = self.render(
            final_head="abc123",
            changes=(pcs.ChangeEntry("Changed", "Renamed configuration"),),
            breaking_changes=("Replace OLD_URL with NEW_URL before deployment",),
        )
        self.assertNotIn("## Breaking changes", without)
        self.assertIn("## Breaking changes", with_breaking)

    def test_deferred_findings_require_p2_or_p3_and_issue_url(self):
        with self.assertRaises(ValueError):
            self.render(
                final_head="abc123",
                changes=(pcs.ChangeEntry("Fixed", "Resolved blocker"),),
                deferred_findings=(pcs.DeferredFinding("P1", "Still blocked", "https://x/1"),),
            )
        with self.assertRaises(ValueError):
            self.render(
                final_head="abc123",
                changes=(pcs.ChangeEntry("Fixed", "Resolved blocker"),),
                deferred_findings=(pcs.DeferredFinding("P2", "Deferred bug", "#42"),),
            )

    def test_deferred_findings_are_separate_from_fixed(self):
        result = self.render(
            final_head="abc123",
            changes=(pcs.ChangeEntry("Fixed", "Resolved authorization blocker"),),
            deferred_findings=(
                pcs.DeferredFinding("P2", "Retry telemetry gap", "https://example.test/issues/42"),
            ),
        )
        self.assertIn("## Deferred findings", result)
        self.assertIn("P2: Retry telemetry gap", result)
        fixed_section = result.split("### Fixed", 1)[1].split("## User-facing impact", 1)[0]
        self.assertNotIn("Retry telemetry gap", fixed_section)

    def test_existing_pr_content_is_preserved_outside_managed_block(self):
        section = self.render(
            final_head="abc123",
            changes=(pcs.ChangeEntry("Added", "Added export support"),),
        )
        body = "# Repository template\n\nOwner: team-a"
        updated = pcs.upsert_managed_summary(body, section)
        self.assertTrue(updated.startswith(body))
        self.assertIn(pcs.START_MARKER, updated)

    def test_existing_managed_block_is_replaced_not_duplicated(self):
        first = self.render(
            final_head="abc123",
            changes=(pcs.ChangeEntry("Added", "Old summary"),),
        )
        second = self.render(
            final_head="def456",
            changes=(pcs.ChangeEntry("Changed", "New summary"),),
        )
        updated = pcs.upsert_managed_summary(f"Header\n\n{first}\n\nFooter", second)
        self.assertEqual(1, updated.count(pcs.START_MARKER))
        self.assertNotIn("Old summary", updated)
        self.assertIn("New summary", updated)
        self.assertIn("Header", updated)
        self.assertIn("Footer", updated)

    def test_duplicate_or_unmatched_markers_block(self):
        section = self.render(
            final_head="abc123",
            changes=(pcs.ChangeEntry("Changed", "Summary"),),
        )
        with self.assertRaises(ValueError):
            pcs.upsert_managed_summary(pcs.START_MARKER, section)
        with self.assertRaises(ValueError):
            pcs.upsert_managed_summary(section + "\n" + section, section)

    def test_no_repository_requirement_means_pr_body_only(self):
        result = self.decide(convention="CHANGELOG_FILE")
        self.assertEqual("PR_BODY_ONLY", result.status)
        self.assertFalse(result.may_modify_repository)

    def test_changelog_file_presence_alone_does_not_authorize_edit(self):
        result = self.decide(
            convention="CHANGELOG_FILE",
            repository_requires_entry=False,
            change_requires_entry=True,
            creation_authorized=True,
            deterministic_format=True,
        )
        self.assertEqual("PR_BODY_ONLY", result.status)

    def test_existing_required_fragment_is_validated(self):
        result = self.decide(
            convention="CHANGESETS",
            repository_requires_entry=True,
            change_requires_entry=True,
            artifact_present=True,
        )
        self.assertEqual("VALIDATE_EXISTING", result.status)
        self.assertFalse(result.blocks_shipment)

    def test_deterministic_authorized_fragment_may_be_created(self):
        result = self.decide(
            convention="TOWNCRIER",
            repository_requires_entry=True,
            change_requires_entry=True,
            creation_authorized=True,
            deterministic_format=True,
        )
        self.assertEqual("CREATE_REQUIRED_ARTIFACT", result.status)
        self.assertTrue(result.may_modify_repository)

    def test_missing_or_undefined_required_artifact_blocks(self):
        missing = self.decide(
            convention="CUSTOM_FRAGMENT",
            repository_requires_entry=True,
            change_requires_entry=True,
        )
        undefined = self.decide(
            convention="NONE",
            repository_requires_entry=True,
            change_requires_entry=True,
        )
        self.assertTrue(missing.blocks_shipment)
        self.assertTrue(undefined.blocks_shipment)


if __name__ == "__main__":
    unittest.main(verbosity=1)
