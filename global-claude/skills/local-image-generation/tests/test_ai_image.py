#!/usr/bin/env python3
"""Static contract tests for the externally managed ai-image boundary."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT.parents[1]


class AiImageBoundaryTests(unittest.TestCase):
    def test_skill_uses_stable_external_cli_contract(self):
        text = (ROOT / "SKILL.md").read_text()
        self.assertIn("`ai-image`", text)
        self.assertIn("externally managed prerequisites", text)
        normalized = " ".join(text.split())
        self.assertIn("must not install, update, replace, back up, delete, or copy them", normalized)
        self.assertIn("Do not bypass `ai-image`", text)

    def test_package_does_not_bundle_ai_image_binary(self):
        self.assertFalse((PKG / "bin" / "ai-image").exists())

    def test_package_does_not_bundle_ai_image_configuration(self):
        self.assertFalse((PKG / "config" / "ai-image").exists())

    def test_cli_reference_remains_stable(self):
        text = (ROOT / "references" / "cli-contract.md").read_text()
        for command in (
            "ai-image doctor",
            "ai-image generate",
            "ai-image upscale",
            "ai-image config",
            "ai-image version",
        ):
            self.assertIn(command, text)

    def test_routing_keeps_models_out_of_skill_api(self):
        text = (ROOT / "references" / "model-routing.md").read_text()
        self.assertIn("Callers select semantic roles", text)
        self.assertIn("externally managed `ai-image`", text)
        self.assertIn("must not install, replace, or back", text)

    def test_license_unknown_is_not_approved(self):
        text = (ROOT / "references" / "licensing.md").read_text()
        self.assertIn("Unknown means not approved", text)
        self.assertIn("does not own or", text)


if __name__ == "__main__":
    unittest.main()
