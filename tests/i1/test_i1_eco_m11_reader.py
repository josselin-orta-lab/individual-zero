"""Current mortal I1 M11 -> ECO-v1 observer contract (no new behaviour)."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class EcoV1M11ReadOnlyTests(unittest.TestCase):
    def test_real_mortal_physical_receipts_score_without_state_mutation(self):
        with TemporaryDirectory(prefix="i1-eco-v1-m11-") as tmp:
            generated = Path(tmp) / "generated"
            generate(generated)
            program = r"""
from pathlib import Path
from tempfile import TemporaryDirectory

from i1lab.i1_birth import birth_i1_m11
from run_i1_world_preset import _birth_parameters, load_preset
from i1_eco_m11_reader import audited_life_metrics

preset, digest = load_preset("oasis")
raw, _ = _birth_parameters(preset)
params = dict(raw, diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1)
identity = "i1:eco:v1:m11:reader:real"
with TemporaryDirectory() as home:
    path = str(Path(home) / "life.sqlite")
    with birth_i1_m11(db_path=path, life_id=identity, **params) as actor:
        rt = actor._runtime
        setpoints = dict(rt.value_needs.config.setpoints)
        scales = dict(rt.value_needs.config.normalization_scales)
        for _ in range(3):
            receipt = actor.run_step()
            if receipt.status == "dead":
                break
        head = rt.journal.head_hash
        last = dict(rt.world.body.as_dict())
        count = len(rt.journal.entries)
    observed = audited_life_metrics(
        path=path, individual_id=identity, horizon=3,
        setpoints=setpoints, scales=scales)
    assert observed["journal_head"] == head
    assert observed["journal_count"] == count
    assert observed["generation"] == 3
    assert observed["metrics"]["observed_steps"] == 3
    assert observed["metrics"]["adaptive_benefit"] == "NOT_ESTABLISHED"
    assert observed["custody"] == "audited_SQLite_M11_read_only"
    assert observed["metrics"]["deficit_area_total"] >= 0
    assert last["food"] <= 100
"""
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONPATH=os.pathsep.join((
                           str(generated), str(ROOT / "src"), str(ROOT / "tools"))))
            result = subprocess.run([sys.executable, "-B", "-c", program],
                                    cwd=ROOT, env=env, capture_output=True,
                                    text=True, timeout=240)
            self.assertEqual(result.returncode, 0,
                             result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
