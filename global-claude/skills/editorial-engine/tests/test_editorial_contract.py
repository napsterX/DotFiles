#!/usr/bin/env python3
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent
REFS = ROOT / "references"


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
        text = (REFS / "eval.md").read_text()
        self.assertIn("No fabricated facts", text)
        self.assertIn("No fabricated personal experiences", text)
        self.assertIn("`READY`: 85-89", text)
        self.assertIn("at least `READY`", text)

    def test_repository_contract_is_versioned_and_deterministic(self):
        text = (REFS / "publication-contract.md").read_text()
        self.assertIn("<repository-root>/.editorial/contract.md", text)
        self.assertIn("editorial_contract_version: 1", text)
        self.assertIn("Do not search for or inherit a contract from a parent", text)
        self.assertIn("do **not** silently", text)
        self.assertIn("specializes", text)
        self.assertIn("cannot weaken universal", text)

    def test_repository_contract_standard_files(self):
        text = (REFS / "publication-contract.md").read_text()
        for name in (
            "brand.md",
            "audience.md",
            "archetypes.md",
            "visual-system.md",
            "components.md",
            "evidence-policy.md",
            "language.md",
            "quality-gates.md",
        ):
            self.assertIn(name, text)

    def test_skill_resolves_repo_contract_before_publication_work(self):
        text = (ROOT / "SKILL.md").read_text()
        self.assertIn("Repository publication contract", text)
        self.assertIn(".editorial/contract.md", text)
        self.assertIn("exact repository root", text)
        self.assertIn("repository-specific publication readiness is blocked", text)

    def test_composition_separates_mode_from_archetype(self):
        text = (REFS / "publication-composition.md").read_text()
        self.assertIn("Editorial mode is not publication archetype", text)
        self.assertIn("Visual cadence without visual quotas", text)
        self.assertIn("TOC and navigation restraint", text)
        self.assertIn("Component-aware composition", text)
        self.assertIn("Responsive composition", text)
        self.assertIn("never require an image every n words", text.lower())

    def test_publication_eval_is_independent_and_evidence_based(self):
        text = (REFS / "publication-eval.md").read_text()
        self.assertIn("independent", text)
        self.assertIn("actual rendered result", text)
        self.assertIn("`PUBLICATION_READY`", text)
        self.assertIn("`PUBLICATION_UNVERIFIED`", text)
        self.assertIn("Source markup or CSS alone is not sufficient", text)
        self.assertIn("score 85-100", text)

    def test_skill_requires_two_independent_readiness_gates(self):
        text = (ROOT / "SKILL.md").read_text()
        self.assertIn("Two independent readiness gates", text)
        self.assertIn("`READY`", text)
        self.assertIn("`PUBLICATION_READY`", text)
        self.assertIn("`PUBLICATION_UNVERIFIED`", text)

    def test_workflow_includes_render_review_and_reverification(self):
        text = (REFS / "editorial-workflow.md").read_text()
        self.assertIn("Publication archetype and composition plan", text)
        self.assertIn("Rendered publication review", text)
        self.assertIn("full page", text)
        self.assertIn("required breakpoint", text)
        self.assertIn("re-render", text.lower())

    def test_visual_taxonomy(self):
        text = (REFS / "visual-policy.md").read_text()
        for label in (
            "Explanatory",
            "Evidentiary",
            "Photographic",
            "Editorial / conceptual illustration",
            "Infographic",
        ):
            self.assertIn(label, text)

    def test_visual_policy_includes_page_level_cadence_without_quota(self):
        text = (REFS / "visual-policy.md").read_text()
        self.assertIn("cognitive transitions", text)
        self.assertIn("information density", text)
        self.assertIn("page-level cadence", text)
        self.assertIn("never\nrequire an image every N words", text)
        self.assertIn("Repository visual-system precedence", text)

    def test_visual_generation_delegates(self):
        text = (ROOT / "SKILL.md").read_text()
        self.assertIn("delegate", text.lower())
        self.assertIn("`local-image-generation`", text)
        self.assertIn("must not contain or execute raw MFLUX/MLX syntax", text)

    def test_no_low_level_backend_commands_in_editorial_files(self):
        forbidden = [
            r"mflux-generate",
            r"python\s+-m\s+mflux",
            r"mlx_lm",
            r"--quantize",
            r"--steps\s+\d+",
        ]
        for path in [ROOT / "SKILL.md", *list(REFS.glob("*.md"))]:
            text = path.read_text().lower()
            for pattern in forbidden:
                self.assertIsNone(re.search(pattern, text), f"{pattern} found in {path}")

    def test_visual_retry_bound_and_review(self):
        text = (REFS / "visual-policy.md").read_text()
        self.assertIn("Maximum three local quality-directed attempts", text)
        self.assertIn("Inspect the actual image", text)

    def test_visual_style_cliches_and_repo_precedence(self):
        text = (REFS / "visual-style.md").read_text()
        for phrase in ("glowing AI brains", "hooded hackers", "floating padlocks", "fake dashboards"):
            self.assertIn(phrase, text)
        self.assertIn(".editorial/visual-system.md", text)
        self.assertIn("takes precedence", text)

    def test_truth_rules_preserved(self):
        text = (REFS / "research-and-truth.md").read_text()
        for phrase in (
            "Never invent facts",
            "Never attribute a personal belief",
            "Never turn inference into fact",
            "Never fabricate a\n",
        ):
            self.assertIn(phrase, text)

    def test_generic_engine_contains_no_product_specific_policy(self):
        forbidden_products = ("Fidem", "ManyDoors", "Vichara")
        for path in [ROOT / "SKILL.md", *list(REFS.glob("*.md"))]:
            text = path.read_text()
            for product in forbidden_products:
                self.assertNotIn(product, text, f"product-specific policy leaked into {path}")

    def test_required_refs_exist(self):
        for name in (
            "editorial-workflow.md",
            "research-and-truth.md",
            "human-writing.md",
            "visual-policy.md",
            "visual-style.md",
            "image-brief-template.md",
            "eval.md",
            "publication-contract.md",
            "publication-composition.md",
            "publication-eval.md",
        ):
            self.assertTrue((REFS / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
