"""A0 must reject absent worlds without manufacturing a scientific verdict."""
import tempfile
import os
import subprocess
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
from build_i1_fork import generate
from aggregate_i1_eco_a0 import aggregate
from run_i1_eco_a0 import PRESETS


class A0AggregationContractTests(unittest.TestCase):
    def test_corrupt_m11_is_recorded_without_losing_other_worlds(self):
        with tempfile.TemporaryDirectory() as home:
            root = Path(home)
            generated = root / "generated"
            generate(generated)
            directory = root / "i1-eco-a0-oasis-test"
            directory.mkdir()
            (directory / "report.json").write_text(
                '{"schema":"i1-eco-v1-a0-measurement-only",'
                '"presets":["oasis"],"horizons":{"oasis":24},'
                '"verdict":"MEASUREMENT_FRAGMENT_READY","lives":[{'
                '"preset":"oasis","horizon":24,"identity":"i1:eco:v1:a0:oasis",'
                '"interpretation":"MEASUREMENT_ONLY_NOT_ADAPTIVE_GO"}]}',
                encoding="utf-8")
            (directory / "oasis.sqlite").write_bytes(b"not a SQLite database")
            result = aggregate(root, generated)
        self.assertEqual(result["verdict"], "MEASUREMENT_BLOCKED")
        self.assertEqual(len(result["problems"]), len(PRESETS))
        self.assertEqual(result["problems"][0]["preset"], "oasis")
        self.assertEqual(result["problems"][0]["problem"], "TECHNICAL_AUDIT_FAILURE")

    def test_missing_all_six_keeps_evidence_gap_visible(self):
        with tempfile.TemporaryDirectory() as home:
            root = Path(home)
            generated = root / "generated"
            generate(generated)
            with patch("aggregate_i1_eco_a0.subprocess.check_output",
                       return_value="a" * 40 + "\n"):
                result = aggregate(root, generated)
        self.assertEqual(result["verdict"], "MEASUREMENT_BLOCKED")
        self.assertEqual(result["audited_lives"], [])
        self.assertEqual(len(result["problems"]), len(PRESETS))
        self.assertEqual(result["adaptive_learning_go"], "NOT_ESTABLISHED")
        self.assertFalse(result["independent_cohort"])
        self.assertFalse(result["td_masked_comparator"])


    def test_effective_physics_matches_canonical_mortal_m11_birth(self):
        """Raw preset physics is not I1's versioned natural birth config."""
        with tempfile.TemporaryDirectory() as home:
            root = Path(home)
            generated = root / "generated"
            generate(generated)
            program = r"""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from run_i1_world_preset import load_preset, _birth_parameters
from aggregate_i1_eco_a0 import _effective_birth_physics_digest
from i1lab.i1_birth import birth_i1_m11

preset, _ = load_preset("oasis")
params, _ = _birth_parameters(preset)
expected = _effective_birth_physics_digest(params)
assert expected != params["world_config"].digest()
with TemporaryDirectory() as tmp:
    with birth_i1_m11(
        db_path=str(Path(tmp) / "life.sqlite"),
        life_id="i1:eco:a0:birth-digest-contract",
        **params,
    ) as actor:
        actual = actor._runtime.world.config.digest()
        assert actual == expected, (actual, expected)
        actor.run_step()
        assert actor._runtime.world.config.digest() == expected
"""
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONPATH=os.pathsep.join((
                           str(generated), str(ROOT / "src"),
                           str(ROOT / "tools"))))
            result = subprocess.run(
                [sys.executable, "-B", "-c", program],
                cwd=ROOT, env=env, capture_output=True,
                text=True, timeout=180)
            self.assertEqual(result.returncode, 0,
                             result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
