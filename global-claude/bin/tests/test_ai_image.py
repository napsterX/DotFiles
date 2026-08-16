#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AI_IMAGE = ROOT / "ai-image"
FAKE = ROOT / "tests" / "fakes" / "fake_backend.py"


class _AiImageHarness:
    """Shared fake-backend fixture. Not collected as a suite on its own."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.root = Path(self.td.name)
        self.cfg = self.root / "config"
        self.bin = self.root / "bin"
        self.out = self.root / "out"
        self.cfg.mkdir()
        self.bin.mkdir()
        self.out.mkdir()
        for name in ("fake-krea", "fake-flux", "fake-flux-edit", "fake-qwen", "fake-upscale"):
            (self.bin / name).symlink_to(FAKE)
        self.write_config()
        self.env = dict(os.environ)
        self.env["AI_IMAGE_CONFIG_DIR"] = str(self.cfg)
        self.env["PATH"] = f"{self.bin}:{self.env.get('PATH','')}"

    def tearDown(self):
        self.td.cleanup()

    def write_config(self, *, fail_once_state: str | None = None, timeout: int = 10, sleep_seconds: float | None = None):
        env = {"FAKE_ARGV_LOG": str(self.root / "argv.log")}
        if fail_once_state:
            env["FAKE_FAIL_ONCE_STATE"] = fail_once_state
        if sleep_seconds is not None:
            env["FAKE_SLEEP_SECONDS"] = str(sleep_seconds)
        defaults = {
            "schema_version": 2,
            "default_quality": "high",
            "default_timeout_seconds": timeout,
            "technical_retry_attempts": 1,
            "metadata_sidecar": True,
            "aspects": {"16:9": {"draft": [64, 36], "standard": [96, 54], "high": [128, 72]}},
            "policies": {
                "no-text": {
                    "prompt_prefix": "IMAGE ONLY. NO TEXT.",
                    "acceptance_criteria": ["No unintended text."],
                    "retry_guidance": ["Retry with a new seed."]
                },
                "edit": {"prompt_prefix": "EDIT ONLY REQUESTED REGION.", "acceptance_criteria": ["Preserve unrelated regions."]},
                "up": {"acceptance_criteria": ["Preserve identity."]}
            },
            "backends": {
                "krea": {"enabled": True, "executable": "fake-krea", "generate_args": ["--prompt", "{prompt}", "--width", "{width}", "--height", "{height}", "--steps", "{steps}", "--seed", "{seed}", "--output", "{output}"], "edit_args": [], "upscale_args": [], "timeout_seconds": timeout, "environment": env},
                "flux": {"enabled": True, "executable": "fake-flux", "generate_args": ["--model", "{model}", "--prompt", "{prompt}", "--steps", "{steps}", "--seed", "{seed}", "--output", "{output}"], "edit_args": [], "upscale_args": [], "timeout_seconds": timeout, "environment": env},
                "edit": {"enabled": True, "executable": "fake-flux-edit", "generate_args": [], "edit_args": ["--model", "{model}", "--image-paths", "{image_paths}", "--prompt", "{prompt}", "--steps", "{steps}", "--seed", "{seed}", "--output", "{output}"], "upscale_args": [], "timeout_seconds": timeout, "environment": env},
                "qwen": {"enabled": True, "executable": "fake-qwen", "generate_args": ["--model", "{model}", "--prompt", "{prompt}", "--negative-prompt", "{negative_prompt}", "--output", "{output}"], "edit_args": [], "upscale_args": [], "timeout_seconds": timeout, "environment": env},
                "up": {"enabled": True, "executable": "fake-upscale", "generate_args": [], "edit_args": [], "upscale_args": ["--model", "{model}", "--image-path", "{input}", "--resolution", "{resolution}", "--softness", "{softness}", "--output", "{output}"], "timeout_seconds": timeout, "environment": env}
            },
            "cloud": {"enabled": False}
        }
        models = {
            "schema_version": 2,
            "roles": {
                "editorial": {"provider": "local", "backend": "krea", "model": "krea", "license_approved": True, "policy": "no-text", "fallback_role": "photorealistic", "parameters": {"steps": 8}},
                "photorealistic": {"provider": "local", "backend": "flux", "model": "flux", "license_approved": True, "policy": "no-text", "fallback_role": "editorial", "parameters": {"steps": 4}},
                "conceptual": {"provider": "local", "backend": "krea", "model": "krea", "license_approved": True, "policy": "no-text", "fallback_role": "precision", "parameters": {"steps": 8}},
                "precision": {"provider": "local", "backend": "qwen", "model": "qwen", "license_approved": True, "policy": "no-text", "fallback_role": "editorial", "parameters": {"steps": 30, "negative_prompt": "text"}},
                "fast-draft": {"provider": "local", "backend": "flux", "model": "flux", "license_approved": True, "policy": "no-text", "fallback_role": "editorial", "parameters": {"steps": 4}},
                "typography": {"provider": "local", "backend": "qwen", "model": "qwen", "license_approved": True, "policy": "no-text", "fallback_role": "", "parameters": {"steps": 30, "negative_prompt": "bad"}},
                "editing": {"provider": "local", "backend": "edit", "model": "flux", "license_approved": True, "policy": "edit", "fallback_role": "", "parameters": {"steps": 4}},
                "upscale": {"provider": "local", "backend": "up", "model": "seed", "license_approved": True, "policy": "up", "fallback_role": "", "parameters": {"resolution": "2x", "softness": 0.5}}
            }
        }
        (self.cfg / "defaults.json").write_text(json.dumps(defaults), encoding="utf-8")
        (self.cfg / "models.json").write_text(json.dumps(models), encoding="utf-8")

    def run_ai(self, *args, env=None):
        e = dict(self.env)
        if env:
            e.update(env)
        return subprocess.run([str(AI_IMAGE), *args], capture_output=True, text=True, env=e, timeout=20)

    def make_brief(self, text="A professional portrait"):
        p = self.root / "brief.md"
        p.write_text(text, encoding="utf-8")
        return p

class AiImageTests(_AiImageHarness, unittest.TestCase):
    def test_01_version(self):
        r = self.run_ai("version")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("ai-image-v2", r.stdout)

    def test_02_doctor_ready_including_editing(self):
        r = self.run_ai("doctor", "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertEqual(data["status"], "ready")
        self.assertIn("editing", data["ready_roles"])
        self.assertIn("upscale", data["ready_roles"])

    def test_03_generate_injects_policy_and_metadata(self):
        brief = self.make_brief("A leader in architecture")
        output = self.out / "hero.png"
        r = self.run_ai("generate", "--brief", str(brief), "--purpose", "editorial", "--aspect", "16:9", "--quality", "high", "--seed", "42", "--output", str(output), "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertTrue(output.is_file())
        meta = json.loads(Path(str(output) + ".ai-image.json").read_text())
        self.assertEqual(meta["effective_role"], "editorial")
        self.assertEqual(meta["seed"], 42)
        self.assertEqual(meta["actual_width"], 1)
        log = (self.root / "argv.log").read_text()
        self.assertIn("IMAGE ONLY. NO TEXT.", log)
        self.assertNotIn("A leader in architecture\"", json.dumps(meta.get("command")))

    def test_04_quality_attempt_gets_deterministic_suffix(self):
        brief = self.make_brief()
        requested = self.out / "hero.png"
        r = self.run_ai("generate", "--brief", str(brief), "--purpose", "editorial", "--aspect", "16:9", "--output", str(requested), "--quality-attempt", "2", "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        actual = self.out / "hero.attempt-02.png"
        self.assertTrue(actual.is_file())
        data = json.loads(r.stdout)
        self.assertEqual(data["quality_attempt"], 2)
        self.assertEqual(data["output"], str(actual.resolve()))

    def test_05_explicit_fallback_route(self):
        brief = self.make_brief()
        output = self.out / "fallback.png"
        r = self.run_ai("generate", "--brief", str(brief), "--purpose", "editorial", "--use-fallback", "--aspect", "16:9", "--output", str(output), "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertTrue(data["fallback_used"])
        self.assertEqual(data["fallback_from"], "editorial")
        self.assertEqual(data["effective_role"], "photorealistic")

    def test_06_technical_retry_succeeds(self):
        state = str(self.root / "fail-once.state")
        self.write_config(fail_once_state=state)
        brief = self.make_brief()
        output = self.out / "retry.png"
        r = self.run_ai("generate", "--brief", str(brief), "--purpose", "editorial", "--aspect", "16:9", "--output", str(output), "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertEqual(data["technical_attempt"], 2)
        self.assertTrue(Path(state).exists())

    def test_07_edit_expands_input_and_multiple_references(self):
        brief = self.make_brief("Put the glasses on the person")
        source = self.root / "source.png"
        ref1 = self.root / "glasses.png"
        ref2 = self.root / "jacket.png"
        source.write_bytes(b"source")
        ref1.write_bytes(b"ref1")
        ref2.write_bytes(b"ref2")
        output = self.out / "edit.png"
        r = self.run_ai("edit", "--input", str(source), "--reference", str(ref1), "--reference", str(ref2), "--brief", str(brief), "--seed", "7", "--output", str(output), "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertEqual(len(data["references"]), 2)
        logline = json.loads((self.root / "argv.log").read_text().splitlines()[-1])
        idx = logline.index("--image-paths")
        self.assertEqual(logline[idx + 1:idx + 4], [str(source.resolve()), str(ref1.resolve()), str(ref2.resolve())])

    def test_08_upscale_and_override_parameters(self):
        source = self.root / "source.png"
        source.write_bytes(b"source")
        output = self.out / "up.png"
        r = self.run_ai("upscale", "--input", str(source), "--resolution", "3x", "--softness", "0.25", "--output", str(output), "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertEqual(data["resolution"], "3x")
        self.assertEqual(data["softness"], 0.25)
        self.assertTrue(output.is_file())

    def test_09_review_records_external_decision(self):
        brief = self.make_brief()
        output = self.out / "review.png"
        r = self.run_ai("generate", "--brief", str(brief), "--purpose", "editorial", "--aspect", "16:9", "--output", str(output))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        r = self.run_ai("review", "--input", str(output), "--decision", "rejected", "--reason", "unwanted typography", "--reviewer", "claude-code", "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        meta = json.loads(Path(str(output) + ".ai-image.json").read_text())
        self.assertEqual(meta["review"]["decision"], "rejected")
        self.assertIn("unwanted typography", meta["review"]["reasons"])

    def test_10_refuses_accidental_overwrite(self):
        brief = self.make_brief()
        output = self.out / "exists.png"
        output.write_bytes(b"existing")
        r = self.run_ai("generate", "--brief", str(brief), "--purpose", "editorial", "--aspect", "16:9", "--output", str(output), "--json")
        self.assertEqual(r.returncode, 3)
        data = json.loads(r.stdout)
        self.assertEqual(data["code"], "OUTPUT_EXISTS")
        self.assertEqual(output.read_bytes(), b"existing")

    def test_11_dry_run_redacts_brief_content(self):
        secret = "VERY-SENSITIVE-BRIEF-CONTENT"
        brief = self.make_brief(secret)
        output = self.out / "dry.png"
        r = self.run_ai("generate", "--brief", str(brief), "--purpose", "editorial", "--aspect", "16:9", "--output", str(output), "--dry-run", "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn(secret, r.stdout)
        self.assertFalse(output.exists())

    def test_12_policy_exposes_acceptance_contract(self):
        r = self.run_ai("policy", "--purpose", "conceptual", "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertEqual(data["policy"], "no-text")
        self.assertTrue(data["acceptance_criteria"])

    def test_13_timeout_returns_process_exit_and_no_output(self):
        self.write_config(timeout=1, sleep_seconds=2.0)
        brief = self.make_brief()
        output = self.out / "timeout.png"
        r = self.run_ai("generate", "--brief", str(brief), "--purpose", "editorial", "--aspect", "16:9", "--output", str(output), "--json")
        self.assertEqual(r.returncode, 5, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertEqual(data["code"], "GENERATION_TIMEOUT")
        self.assertFalse(output.exists())

    def test_14_unsupported_schema_is_config_error(self):
        defaults = json.loads((self.cfg / "defaults.json").read_text())
        defaults["schema_version"] = 999
        (self.cfg / "defaults.json").write_text(json.dumps(defaults), encoding="utf-8")
        models = json.loads((self.cfg / "models.json").read_text())
        models.pop("schema_version", None)
        (self.cfg / "models.json").write_text(json.dumps(models), encoding="utf-8")
        r = self.run_ai("doctor", "--json")
        self.assertEqual(r.returncode, 3)
        data = json.loads(r.stdout)
        self.assertEqual(data["code"], "CONFIG_SCHEMA_UNSUPPORTED")

    def test_15_installer_replaces_binary_backs_it_up_and_leaves_config_alone(self):
        # This package owns the executable and its tests only. It carries no
        # configuration change, so it must not read, rewrite, or back up
        # ~/.config/ai-image, which the operator manages separately.
        home = self.root / "install-home"
        old_bin = home / ".local" / "bin" / "ai-image"
        cfg_dir = home / ".config" / "ai-image"
        old_bin.parent.mkdir(parents=True)
        cfg_dir.mkdir(parents=True)
        old_bin.write_text("old-binary\n", encoding="utf-8")
        old_bin.chmod(0o755)
        defaults_text = "{\"operator_edited\": true}\n"
        models_text = "{\"operator_edited_models\": true}\n"
        local_text = "{\"machine_specific\": true}\n"
        (cfg_dir / "defaults.json").write_text(defaults_text, encoding="utf-8")
        (cfg_dir / "models.json").write_text(models_text, encoding="utf-8")
        (cfg_dir / "local.json").write_text(local_text, encoding="utf-8")
        env = dict(os.environ)
        env["HOME"] = str(home)
        r = subprocess.run([str(ROOT / "install.sh")], capture_output=True, text=True, env=env, timeout=20)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("ai-image-v2", subprocess.run([str(old_bin), "version"], capture_output=True, text=True, env=env).stdout)

        # Operator-managed configuration is byte-for-byte untouched.
        self.assertEqual(defaults_text, (cfg_dir / "defaults.json").read_text(encoding="utf-8"))
        self.assertEqual(models_text, (cfg_dir / "models.json").read_text(encoding="utf-8"))
        self.assertEqual(local_text, (cfg_dir / "local.json").read_text(encoding="utf-8"))
        self.assertEqual(
            sorted(p.name for p in cfg_dir.iterdir()),
            ["defaults.json", "local.json", "models.json"],
        )
        # No config was copied into the backup snapshot either.
        self.assertEqual([], list((home / ".ai-image-backups").glob("*/config/*")))

        # DotFiles receives the executable and the runtime test suite.
        dot_bin = home / "git" / "DotFiles" / "global-claude" / "bin"
        self.assertTrue((dot_bin / "ai-image").is_file())
        self.assertTrue((dot_bin / "tests" / "test_ai_image.py").is_file())
        self.assertTrue((dot_bin / "tests" / "fakes" / "fake_backend.py").is_file())
        self.assertFalse((home / "git" / "DotFiles" / "global-claude" / "config").exists())

        backups = list((home / ".ai-image-backups").glob("*/local/bin/ai-image"))
        self.assertTrue(backups)
        self.assertEqual(backups[0].read_text(), "old-binary\n")


class PromoteTests(_AiImageHarness, unittest.TestCase):
    """Promotion publishes an accepted candidate without re-running any model."""

    def make_candidate(self, name="hero.candidate.png", *, attempt=1, decision="accepted"):
        brief = self.make_brief()
        requested = self.out / name
        args = ["generate", "--brief", str(brief), "--purpose", "editorial", "--aspect", "16:9", "--output", str(requested)]
        if attempt > 1:
            args += ["--quality-attempt", str(attempt)]
        r = self.run_ai(*args, "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        candidate = Path(json.loads(r.stdout)["output"])
        if decision is not None:
            r = self.run_ai("review", "--input", str(candidate), "--decision", decision, "--reason", "inspected", "--json")
            self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        return candidate

    def test_16_promote_accepted_candidate_succeeds(self):
        candidate = self.make_candidate()
        final = self.out / "hero.png"
        r = self.run_ai("promote", "--input", str(candidate), "--output", str(final), "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["operation"], "promote")
        self.assertFalse(data["regenerated"])
        self.assertTrue(final.is_file())

    def test_17_promoted_bytes_and_hash_equal_candidate(self):
        candidate = self.make_candidate()
        final = self.out / "hero.png"
        r = self.run_ai("promote", "--input", str(candidate), "--output", str(final), "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertEqual(candidate.read_bytes(), final.read_bytes())
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        self.assertEqual(data["sha256"], digest)
        self.assertEqual(data["promoted_from_sha256"], digest)

    def test_18_source_candidate_remains(self):
        candidate = self.make_candidate()
        before = candidate.read_bytes()
        final = self.out / "hero.png"
        self.assertEqual(0, self.run_ai("promote", "--input", str(candidate), "--output", str(final)).returncode)
        self.assertTrue(candidate.is_file())
        self.assertEqual(before, candidate.read_bytes())

    def test_19_source_sidecar_remains(self):
        candidate = self.make_candidate()
        sidecar = Path(str(candidate) + ".ai-image.json")
        before = sidecar.read_text(encoding="utf-8")
        final = self.out / "hero.png"
        self.assertEqual(0, self.run_ai("promote", "--input", str(candidate), "--output", str(final)).returncode)
        self.assertTrue(sidecar.is_file())
        self.assertEqual(before, sidecar.read_text(encoding="utf-8"))

    def test_20_final_sidecar_preserves_quality_attempt_and_review(self):
        candidate = self.make_candidate("hero.candidate.png", attempt=2)
        self.assertTrue(candidate.name.endswith(".attempt-02.png"))
        final = self.out / "hero.png"
        r = self.run_ai("promote", "--input", str(candidate), "--output", str(final), "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        meta = json.loads(Path(str(final) + ".ai-image.json").read_text(encoding="utf-8"))
        # Original quality attempt survives promotion rather than resetting to 1.
        self.assertEqual(meta["quality_attempt"], 2)
        self.assertEqual(meta["review"]["decision"], "accepted")
        self.assertIn("inspected", meta["review"]["reasons"])
        # Generation provenance is preserved verbatim.
        self.assertEqual(meta["operation"], "generate")
        self.assertEqual(meta["effective_role"], "editorial")
        # Only promotion lineage is added.
        self.assertEqual(meta["promoted_from"], str(candidate))
        self.assertEqual(meta["promoted_from_sha256"], hashlib.sha256(candidate.read_bytes()).hexdigest())
        self.assertIn("promoted_at_utc", meta)

    def test_21_rejected_or_unreviewed_candidate_cannot_be_promoted(self):
        rejected = self.make_candidate("rejected.candidate.png", decision="rejected")
        final = self.out / "from-rejected.png"
        r = self.run_ai("promote", "--input", str(rejected), "--output", str(final), "--json")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(json.loads(r.stdout)["code"], "CANDIDATE_NOT_ACCEPTED")
        self.assertFalse(final.exists())

        unreviewed = self.make_candidate("unreviewed.candidate.png", decision=None)
        final2 = self.out / "from-unreviewed.png"
        r = self.run_ai("promote", "--input", str(unreviewed), "--output", str(final2), "--json")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(json.loads(r.stdout)["code"], "CANDIDATE_NOT_ACCEPTED")
        self.assertFalse(final2.exists())

    def test_22_existing_final_destination_is_not_overwritten(self):
        candidate = self.make_candidate()
        final = self.out / "hero.png"
        final.write_bytes(b"already-delivered")
        r = self.run_ai("promote", "--input", str(candidate), "--output", str(final), "--json")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(json.loads(r.stdout)["code"], "OUTPUT_EXISTS")
        self.assertEqual(b"already-delivered", final.read_bytes())

    def test_23_promotion_requires_a_sidecar_and_refuses_self_destination(self):
        orphan = self.out / "orphan.png"
        orphan.write_bytes(b"no-sidecar")
        r = self.run_ai("promote", "--input", str(orphan), "--output", str(self.out / "x.png"), "--json")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(json.loads(r.stdout)["code"], "METADATA_MISSING")

        candidate = self.make_candidate()
        r = self.run_ai("promote", "--input", str(candidate), "--output", str(candidate), "--json")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(json.loads(r.stdout)["code"], "PROMOTION_SOURCE_IS_DESTINATION")

    def test_24_dry_run_reports_without_writing(self):
        candidate = self.make_candidate()
        final = self.out / "hero.png"
        r = self.run_ai("promote", "--input", str(candidate), "--output", str(final), "--dry-run", "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(json.loads(r.stdout)["operation"], "promote")
        self.assertFalse(final.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
