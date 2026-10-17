"""Build-time I1 source isolation and deterministic generated-world checks."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate, rewrite


class I1GeneratedIsolationTests(unittest.TestCase):
    def test_namespaces_and_reproducible_manifest(self):
        src = ROOT / "src"
        with TemporaryDirectory() as a, TemporaryDirectory() as b:
            first, second = generate(Path(a)), generate(Path(b))
            self.assertEqual(first, second)
            self.assertGreater(len(first["files"]), 170)
            self.assertIn("i1/modules/stage6_planning.py", first["files"])
            self.assertIn("i1lab/stage12_runtime.py", first["files"])
            self.assertIn("i1lab/world.py", first["files"])
            self.assertEqual(
                first["files"]["i1lab/world.py"]["source_path"],
                "i1/runtime/world.py",
            )
            self.assertNotIn("i1/runtime/world.py", first["files"])
            # Journals and Stage10 publication are I1-owned, not text-patched Lab.
            for module in ("journal.py", "journal_views.py", "consolidation_lived_evidence.py", "consolidation_postcut_journal.py", "sqlite_life_store.py", "sqlite_runtime_custody.py", "consolidation_publication.py", "stage10_runtime.py", "stage4_runtime.py"):
                rel = "i1lab/" + module
                source = src / "i1" / "runtime" / module
                self.assertEqual(
                    first["files"][rel]["source_path"],
                    "i1/runtime/" + module,
                )
                self.assertEqual((Path(a) / rel).read_text(),
                                 rewrite(source.read_text()))
                self.assertNotIn("i1/runtime/" + module, first["files"])
            for rel, data in first["files"].items():
                content = (Path(a) / rel).read_bytes()
                self.assertEqual(sha256(content).hexdigest(), data["built_sha256"])
                self.assertTrue((src / data["source_path"]).exists())
            # Physics belongs to I1 directly, not to generated string patches.
            source_world = (src / "i1" / "runtime" / "world.py").read_text()
            self.assertEqual(
                (Path(a) / "i1lab" / "world.py").read_text(),
                rewrite(source_world),
            )

    def test_ordinary_i0_and_lab_sources_unchanged(self):
        with TemporaryDirectory() as folder:
            generate(Path(folder))
            self.assertIn("from i0.interfaces import PrimitiveCommand",
                          (ROOT / "src/lab/world.py").read_text())
            self.assertIn("from i1.interfaces import PrimitiveCommand",
                          (Path(folder) / "i1lab/world.py").read_text())
            self.assertIn("from i1.modules", (
                Path(folder) / "i1lab/stage12_runtime.py"
            ).read_text() or (
                Path(folder) / "i1lab/stage11_runtime.py"
            ).read_text())

    def test_no_output_into_source_tree(self):
        with self.assertRaises(ValueError):
            generate(ROOT / "src" / "i1-generated")

    def test_imports_of_generated_packages(self):
        with TemporaryDirectory() as folder:
            generate(Path(folder))
            script = ("import i1.modules.stage6_planning; "
                      "import i1lab.stage12_runtime; "
                      "import i1lab.world; "
                      "from i1.experimental.stage6_visible_delta_shadow "
                      "import ShadowVisibleDeltaModel; "
                      "print('I1_IMPORTS_OK')")
            run = subprocess.run(
                [sys.executable, "-c", script],
                env={"PYTHONPATH": str(Path(folder))},
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("I1_IMPORTS_OK", run.stdout)


if __name__ == "__main__":
    unittest.main()
