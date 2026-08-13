#!/usr/bin/env python3
import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT.parents[1]
CLI = PKG / "bin" / "ai-image"
CONFIG_SRC = PKG / "config" / "ai-image"

PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c6360000000020001e221bc330000000049454e44ae426082"
)

class AiImageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ai-image-tests-"))
        self.cfg = self.tmp / "config"
        self.cfg.mkdir()
        shutil.copy(CONFIG_SRC / "defaults.json", self.cfg / "defaults.json")
        shutil.copy(CONFIG_SRC / "models.json", self.cfg / "models.json")
        self.env = dict(os.environ)
        self.env["AI_IMAGE_CONFIG_DIR"] = str(self.cfg)
        self.brief = self.tmp / "brief.md"
        self.brief.write_text("# Brief\nA restrained conceptual illustration with no text.\n")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_cli(self, *args):
        return subprocess.run([str(CLI), *args], env=self.env, text=True, capture_output=True, check=False, timeout=20)

    def configure_fake(self):
        fake = self.tmp / "fake-backend.py"
        fake.write_text(
            "#!/usr/bin/env python3\n"
            "import shutil,sys\n"
            "from pathlib import Path\n"
            f"PNG=bytes.fromhex('{PNG_1X1.hex()}')\n"
            "args=sys.argv[1:]\n"
            "if '--copy' in args:\n"
            " i=args.index('--copy'); shutil.copyfile(args[i+1], args[i+2]); sys.exit(0)\n"
            "i=args.index('--output'); Path(args[i+1]).write_bytes(PNG)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        local = {
            "backends": {"mflux": {
                "enabled": True,
                "executable": str(fake),
                "generate_args": ["--model", "{model}", "--prompt", "{prompt}", "--width", "{width}", "--height", "{height}", "--seed", "{seed}", "--output", "{output}"],
                "upscale_args": ["--copy", "{input}", "{output}"],
                "timeout_seconds": 10,
                "environment": {}
            }},
            "roles": {
                "editorial": {"model": "fake-editorial", "license_approved": True},
                "upscale": {"model": "fake-upscale", "license_approved": True}
            }
        }
        (self.cfg / "local.json").write_text(json.dumps(local))

    def test_version(self):
        r = self.run_cli("version")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("ai-image-1", r.stdout)

    def test_help(self):
        r = self.run_cli("--help")
        self.assertEqual(0, r.returncode)
        self.assertIn("generate", r.stdout)
        self.assertIn("upscale", r.stdout)

    def test_unconfigured_doctor_is_clear(self):
        r = self.run_cli("doctor", "--json")
        self.assertEqual(4, r.returncode)
        data = json.loads(r.stdout)
        self.assertEqual("not_ready", data["status"])
        self.assertTrue(data["blockers"])

    def test_config_does_not_dump_environment(self):
        self.env["SUPER_SECRET_FOR_TEST"] = "never-print-this"
        r = self.run_cli("config", "--json")
        self.assertEqual(0, r.returncode)
        self.assertNotIn("never-print-this", r.stdout)

    def test_license_block_before_generation(self):
        out = self.tmp / "out.png"
        r = self.run_cli("generate", "--brief", str(self.brief), "--purpose", "editorial", "--aspect", "16:9", "--quality", "high", "--output", str(out), "--json")
        self.assertEqual(4, r.returncode)
        self.assertEqual("LICENSE_NOT_APPROVED", json.loads(r.stdout)["code"])
        self.assertFalse(out.exists())

    def test_safe_dry_run_plan(self):
        self.configure_fake()
        out = self.tmp / "out.png"
        r = self.run_cli("generate", "--brief", str(self.brief), "--purpose", "editorial", "--aspect", "16:9", "--quality", "high", "--output", str(out), "--dry-run", "--json")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual("planned", data["status"])
        self.assertEqual([1536, 864], [data["width"], data["height"]])
        self.assertEqual("fake-editorial", data["model"])
        self.assertFalse(out.exists())

    def test_dry_run_redacts_brief_content(self):
        self.configure_fake()
        secret_phrase = "private editorial concept do not log"
        self.brief.write_text(secret_phrase + "\n")
        out = self.tmp / "out.png"
        r = self.run_cli("generate", "--brief", str(self.brief), "--purpose", "editorial", "--aspect", "1:1", "--quality", "draft", "--output", str(out), "--dry-run", "--json")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertNotIn(secret_phrase, r.stdout)
        data = json.loads(r.stdout)
        self.assertIn("<redacted-brief-content>", data["command"])

    def test_generate_success_and_metadata(self):
        self.configure_fake()
        out = self.tmp / "hero.png"
        r = self.run_cli("generate", "--brief", str(self.brief), "--purpose", "editorial", "--aspect", "1:1", "--quality", "draft", "--output", str(out), "--seed", "123", "--json")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual("success", data["status"])
        self.assertEqual(123, data["seed"])
        self.assertTrue(out.is_file())
        self.assertTrue(Path(data["metadata"]).is_file())

    def test_upscale_success(self):
        self.configure_fake()
        src = self.tmp / "source.png"
        src.write_bytes(PNG_1X1)
        out = self.tmp / "upscaled.png"
        r = self.run_cli("upscale", "--input", str(src), "--output", str(out), "--json")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual(src.read_bytes(), out.read_bytes())
        self.assertTrue(json.loads(r.stdout)["upscaled"])

    def test_prompt_is_argument_not_shell(self):
        self.configure_fake()
        dangerous = self.tmp / "touch-me"
        self.brief.write_text(f"$(touch {dangerous}) ; `touch {dangerous}` ; no shell\n")
        out = self.tmp / "out.png"
        r = self.run_cli("generate", "--brief", str(self.brief), "--purpose", "editorial", "--aspect", "1:1", "--quality", "draft", "--output", str(out), "--json")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertFalse(dangerous.exists())

    def test_unknown_aspect_fails(self):
        self.configure_fake()
        out = self.tmp / "out.png"
        r = self.run_cli("generate", "--brief", str(self.brief), "--purpose", "editorial", "--aspect", "7:5", "--quality", "high", "--output", str(out), "--json")
        self.assertEqual(3, r.returncode)
        self.assertEqual("UNSUPPORTED_ASPECT", json.loads(r.stdout)["code"])

    def test_missing_brief_fails(self):
        self.configure_fake()
        out = self.tmp / "out.png"
        r = self.run_cli("generate", "--brief", str(self.tmp / "missing.md"), "--purpose", "editorial", "--aspect", "1:1", "--quality", "draft", "--output", str(out), "--json")
        self.assertEqual(3, r.returncode)
        self.assertEqual("BRIEF_NOT_FOUND", json.loads(r.stdout)["code"])

if __name__ == "__main__":
    unittest.main()
