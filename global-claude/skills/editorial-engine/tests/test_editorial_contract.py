#!/usr/bin/env python3
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent

class EditorialContractTests(unittest.TestCase):
    def test_primary_skill_name(self):
        self.assertIn("name: editorial-engine", (ROOT / "SKILL.md").read_text())

    def test_compatibility_shim_is_thin(self):
        shim = SKILLS / "article" / "SKILL.md"
        text = shim.read_text()
        self.assertIn("Immediately invoke `editorial-engine`", text)
        self.assertLess(len(text.splitlines()), 30)
        self.assertNotIn("Stage 1:", text)

    def test_eval_preserves_hard_gates_and_threshold(self):
        text = (ROOT / "references" / "eval.md").read_text()
        self.assertIn("No fabricated facts", text)
        self.assertIn("No fabricated personal experiences", text)
        self.assertIn("`READY`: 85-89", text)
        self.assertIn("at least `READY`", text)

    def test_visual_taxonomy(self):
        text = (ROOT / "references" / "visual-policy.md").read_text()
        for label in ("Explanatory", "Evidentiary", "Photographic", "Editorial / conceptual illustration", "Infographic"):
            self.assertIn(label, text)

    def test_visual_generation_delegates(self):
        text = (ROOT / "SKILL.md").read_text()
        self.assertIn("delegate", text.lower())
        self.assertIn("`local-image-generation`", text)
        self.assertIn("must not contain or execute raw MFLUX/MLX syntax", text)

    def test_no_low_level_backend_commands_in_editorial_files(self):
        forbidden = [r"mflux-generate", r"python\s+-m\s+mflux", r"mlx_lm", r"--quantize", r"--steps\s+\d+"]
        for path in [ROOT / "SKILL.md", *list((ROOT / "references").glob("*.md"))]:
            text = path.read_text().lower()
            for pattern in forbidden:
                self.assertIsNone(re.search(pattern, text), f"{pattern} found in {path}")

    def test_visual_retry_bound_and_review(self):
        text = (ROOT / "references" / "visual-policy.md").read_text()
        self.assertIn("Maximum three local quality-directed attempts", text)
        self.assertIn("Inspect the actual image", text)

    def test_visual_style_cliches(self):
        text = (ROOT / "references" / "visual-style.md").read_text()
        for phrase in ("glowing AI brains", "hooded hackers", "floating padlocks", "fake dashboards"):
            self.assertIn(phrase, text)

    def test_truth_rules_preserved(self):
        text = (ROOT / "references" / "research-and-truth.md").read_text()
        for phrase in ("Never invent facts", "Never attribute a personal belief", "Never turn inference into fact", "Never fabricate a\n"):
            self.assertIn(phrase, text)

    def test_required_refs_exist(self):
        refs = ROOT / "references"
        for name in ("editorial-workflow.md", "research-and-truth.md", "human-writing.md", "visual-policy.md", "visual-style.md", "image-brief-template.md", "eval.md"):
            self.assertTrue((refs / name).is_file(), name)

if __name__ == "__main__":
    unittest.main()
