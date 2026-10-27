"""#564: longer-lived natural M11 shadow cohort; no cognitive index installed.

Extend the validated #573 paired-life protocol without changing its causal
observer, Memory scoring or UC. No minimum speedup/episode count gate: death
and missing old recall remain authentic negative evidence.
"""
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]


class LongerNaturalShadow564(unittest.TestCase):
    def test_extended_unforced_m11_shadow_preserves_causal_reports(self):
        source = runpy.run_path(
            str(ROOT / "tests/i1/test_i1_natural_shadow_recall_564.py")
        )["PROGRAM"]
        old = '''results = [
    natural_pair("empty-land", 12),
    natural_pair("oasis", 12),
]'''
        new = '''results = [
    natural_pair("empty-land", 48),
    natural_pair("oasis", 32),
]'''
        self.assertEqual(source.count(old), 1, "source shadow protocol drift")
        program = source.replace(old, new).replace(
            "I1_NATURAL_SHADOW_RECALL_564=",
            "I1_LONG_NATURAL_SHADOW_RECALL_564=",
        )
        with TemporaryDirectory() as temp:
            generated = Path(temp) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                cwd=ROOT, capture_output=True, text=True, timeout=180,
            )
            self.assertEqual(build.returncode, 0,
                             build.stdout + build.stderr)
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join(
                (str(generated), str(ROOT / "src"), str(ROOT / "tools")))
            env["PYTHONHASHSEED"] = "0"
            run = subprocess.run(
                [sys.executable, "-c", program], cwd=ROOT, env=env,
                capture_output=True, text=True, timeout=300,
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            lines = [x for x in run.stdout.splitlines() if x.startswith(
                "I1_LONG_NATURAL_SHADOW_RECALL_564=")]
            self.assertEqual(len(lines), 1, run.stdout)
            record = json.loads(lines[0].split("=", 1)[1])
            self.assertEqual(record["evidence"], "natural-M11-paired-shadow-L1")
            self.assertTrue(record["shadow_never_controls_recall"])
            self.assertTrue(record["index_not_serialized"])
            self.assertEqual([x["preset"] for x in record["rows"]],
                             ["empty-land", "oasis"])
            self.assertLessEqual(record["rows"][0]["physical_steps"], 48)
            self.assertLessEqual(record["rows"][1]["physical_steps"], 32)
            for row in record["rows"]:
                self.assertGreater(row["physical_steps"], 0)
                self.assertGreater(row["recall_shadow_checks"], 0)
                self.assertTrue(row["cold_and_reports_identical"])
                self.assertGreaterEqual(row["episode_volume"],
                                        row["candidate_volume"])
            print(lines[0])


if __name__ == "__main__":
    unittest.main()
