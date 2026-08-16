#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill"
SKILL_MD = SKILL / "SKILL.md"
REFS = SKILL / "references"
INSTALL = ROOT / "install.sh"


class SkillPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL_MD.read_text(encoding="utf-8")

    def test_01_frontmatter_and_version(self):
        self.assertIn("name: local-image-generation", self.text)
        self.assertIn("version: 2.1.0", self.text)
        self.assertIn("user-invocable: true", self.text)

    def test_02_required_references_exist(self):
        for name in ("model-routing.md", "prompting.md", "quality-guidance.md", "licensing.md", "cli-contract.md"):
            self.assertTrue((REFS / name).is_file(), name)

    def test_03_v2_command_surface_documented(self):
        contract = (REFS / "cli-contract.md").read_text(encoding="utf-8")
        for command in ("doctor", "policy", "generate", "edit", "review", "upscale", "promote", "config", "version"):
            self.assertIn(f"`{command}`", contract)

    def test_04_precision_role_present(self):
        self.assertIn("precision", self.text)
        routing = (REFS / "model-routing.md").read_text(encoding="utf-8")
        self.assertIn("`precision`", routing)

    def test_05_skill_calls_ai_image_not_mflux(self):
        self.assertIn("Use `ai-image` only", self.text)
        self.assertNotIn("mflux-generate-", self.text)
        self.assertNotIn("mflux-upscale-", self.text)

    def test_06_visual_inspection_and_review_required(self):
        self.assertIn("Inspect the image, not only JSON", self.text)
        self.assertIn("ai-image review", self.text)
        self.assertIn("Do not mark a candidate accepted before actually inspecting it", self.text)

    def test_07_bounded_quality_loop(self):
        self.assertIn("Maximum three normal visual-quality attempts", self.text)
        self.assertIn("--quality-attempt", self.text)
        quality = (REFS / "quality-guidance.md").read_text(encoding="utf-8")
        self.assertIn("Default maximum: 3 visual-quality attempts total", quality)

    def test_08_explicit_fallback_only(self):
        self.assertIn("Fallback is explicit", self.text)
        self.assertIn("--use-fallback", self.text)
        self.assertIn("never silently reroute", self.text)

    def test_09_upscale_after_acceptance(self):
        self.assertIn("Upscale after acceptance", self.text)
        quality = (REFS / "quality-guidance.md").read_text(encoding="utf-8")
        self.assertIn("accept the base candidate first", quality)

    def test_10_no_text_default_is_encoded(self):
        prompting = (REFS / "prompting.md").read_text(encoding="utf-8")
        self.assertIn("Default no-text policy", prompting)
        self.assertIn("No headline", prompting)

    def test_11_edit_workflow_preservation(self):
        self.assertIn("what must change", self.text)
        self.assertIn("what must remain unchanged", self.text)
        self.assertIn("--reference", self.text)

    def test_12_package_does_not_ship_runtime_binary_or_config(self):
        forbidden = []
        for p in ROOT.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(ROOT).as_posix()
            if rel == "ai-image" or rel.endswith("/ai-image"):
                forbidden.append(rel)
            if p.name in {"defaults.json", "defaults.dist.json", "models.json", "models.dist.json"}:
                forbidden.append(rel)
        self.assertEqual([], forbidden)

    def test_13_installer_copies_skill_and_dotfiles_without_touching_runtime(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            installed = home / ".claude" / "skills" / "local-image-generation"
            runtime_bin = home / ".local" / "bin" / "ai-image"
            runtime_cfg = home / ".config" / "ai-image" / "models.json"
            runtime_bin.parent.mkdir(parents=True)
            runtime_cfg.parent.mkdir(parents=True)
            runtime_bin.write_text("DO-NOT-TOUCH-BINARY\n", encoding="utf-8")
            runtime_cfg.write_text("DO-NOT-TOUCH-CONFIG\n", encoding="utf-8")
            runtime_bin.chmod(0o755)
            env = dict(os.environ)
            env["HOME"] = str(home)
            env["SKIP_AI_IMAGE_PREFLIGHT"] = "1"
            r = subprocess.run([str(INSTALL)], env=env, capture_output=True, text=True, timeout=20)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertTrue((installed / "SKILL.md").is_file())
            self.assertTrue((installed / "references" / "cli-contract.md").is_file())
            dot = home / "git" / "DotFiles" / "global-claude" / "skills" / "local-image-generation"
            self.assertTrue((dot / "SKILL.md").is_file())
            self.assertEqual("DO-NOT-TOUCH-BINARY\n", runtime_bin.read_text(encoding="utf-8"))
            self.assertEqual("DO-NOT-TOUCH-CONFIG\n", runtime_cfg.read_text(encoding="utf-8"))

    def test_14_installer_backs_up_existing_skill(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            old = home / ".claude" / "skills" / "local-image-generation"
            old.mkdir(parents=True)
            (old / "SKILL.md").write_text("old-skill\n", encoding="utf-8")
            env = dict(os.environ)
            env["HOME"] = str(home)
            env["SKIP_AI_IMAGE_PREFLIGHT"] = "1"
            r = subprocess.run([str(INSTALL)], env=env, capture_output=True, text=True, timeout=20)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            backups = list((home / ".claude" / "skill-backups").glob("*/local-image-generation/SKILL.md"))
            self.assertTrue(backups)
            self.assertEqual("old-skill\n", backups[0].read_text(encoding="utf-8"))


def flat(path: Path) -> str:
    """Collapse whitespace so contract assertions survive markdown re-wrapping."""
    return " ".join(path.read_text(encoding="utf-8").split())


class PromotionWorkflowTests(unittest.TestCase):
    """The delivery defect: candidates must never occupy the caller's final path."""

    @classmethod
    def setUpClass(cls):
        cls.text = flat(SKILL_MD)
        cls.quality = flat(REFS / "quality-guidance.md")
        cls.contract = flat(REFS / "cli-contract.md")

    def test_15_final_delivery_path_is_never_a_generation_target(self):
        self.assertIn(
            "Never generate, edit, or upscale directly into the caller's final delivery path",
            self.text,
        )
        self.assertIn("The final path is written only by `ai-image promote`", self.text)

    def test_16_attempt_one_uses_a_derived_candidate_path_not_the_final_name(self):
        # The requested name foo.png must map to foo.candidate.png for attempt 1,
        # which is precisely what the old workflow got wrong.
        self.assertIn("foo.candidate.png", self.text)
        self.assertIn("foo.candidate.attempt-02.png", self.text)
        self.assertIn("foo.candidate.attempt-03.png", self.text)
        self.assertIn("Insert `.candidate` before the requested suffix", self.text)
        self.assertIn("--output <candidate-base>", self.text)

    def test_17_accepted_candidate_is_promoted_not_regenerated(self):
        self.assertIn("ai-image promote", self.text)
        self.assertIn(
            "Never re-run a model to obtain the requested filename",
            self.text,
        )
        self.assertIn("Promotion copies the accepted bytes", self.text)
        self.assertIn("copies the accepted bytes rather than re-running a model", self.quality)
        self.assertIn("review.decision = accepted", self.contract)

    def test_18_rejected_attempts_and_sidecars_are_retained(self):
        self.assertIn("Keep rejected attempts.", self.text)
        self.assertIn(
            "Rejected candidates and their review sidecars must remain on disk",
            self.text,
        )
        self.assertIn("Never use `--overwrite` to replace an earlier attempt", self.text)
        self.assertIn("Candidate retention", self.quality)
        self.assertIn("destroys the audit trail", self.quality)

    def test_19_promotion_stage_is_part_of_the_workflow(self):
        self.assertIn("## Stage 8 - Promote the accepted candidate", self.text)
        self.assertIn("--input <accepted-candidate>", self.text)
        self.assertIn("--output <caller-requested-path>", self.text)
        self.assertIn("accepted candidate path it was promoted from", self.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
