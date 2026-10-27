"""Cross-owner L2 regression: one canonical I1 life and authenticated M11 recovery.

Tests software custody and wiring, not multi-hop behavior or survival benefit.
"""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class CognitiveCoexistenceTests(unittest.TestCase):
    def test_canonical_competition_exploration_sleep_joint_recovery(self):
        with TemporaryDirectory(prefix="i1-cross-357-") as d:
            generated = Path(d) / "generated"
            generate(generated)
            code = """
from pathlib import Path
from tempfile import TemporaryDirectory
import inspect
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.stage11_runtime import Stage11Runtime
from i1lab.stage10_runtime import Stage10Runtime
from run_i1_world_preset import load_preset, _birth_parameters
from i1lab.sqlite_life_store import SQLiteLifeLedger

preset, _ = load_preset("oasis")
args, _ = _birth_parameters(preset)
args = dict(args, diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1)
identity = "i1:357:cross-l2"
def new_runtime():
    return I1Runtime(birth_life_id=identity, wal_path=None,
                     autonomous_mortal=True, m11_sqlite_custody=True, **args)

assert "record_applied_memory_intention" in inspect.getsource(Stage11Runtime._dispatch_decision)
# A full Perception precedes the reflex/Competition fork. An already
# committed spatial arrival must not depend on a later cognitive cycle.
assert "observe_memory_intention" in inspect.getsource(Stage11Runtime._on_open_step_capture)
assert "observe_memory_intention" not in inspect.getsource(Stage11Runtime._phase_hooks)
assert "intent.confirmed_step == capture.t_monde" not in inspect.getsource(Stage11Runtime._phase_hooks)
assert "intent.confirmed_step != capture.t_monde" in inspect.getsource(Stage11Runtime._before_competition_accumulation)
assert "note_applied_local_action" in inspect.getsource(Stage11Runtime._dispatch_decision)
assert "observe_lived_site_followup" in inspect.getsource(Stage11Runtime._on_open_step_capture)
assert "record_applied_sleep_decision" in inspect.getsource(Stage10Runtime._sleep_step)
assert "_propose_independent_local" in inspect.getsource(I1Runtime._phase_hooks)
with TemporaryDirectory(prefix="i1-357-ledger-") as directory:
    db = str(Path(directory) / "life.sqlite")
    with birth_i1_m11(db_path=db, life_id=identity, **args) as live:
        rt = live._runtime
        assert rt.exploration.geographic.config.experienced_site_effects is True
        assert rt.competition.applied_memory_intention is None
        assert rt.sleep_session.mode == "awake"
        first = live.run_step()
        assert first.status == "active"
        rt = live._runtime  # M11 has replaced the private runtime instance
        frozen = {
            "competition": rt.competition.export_causal_state(),
            "geography": rt.exploration.geographic.export_causal_state(),
            "sleep": rt.sleep_session.export_causal_state(),
        }
        assert "lived_site_effects" in frozen["geography"]
        assert "pending_site_action" in frozen["geography"]
    audit = SQLiteLifeLedger.audit_read_only(path=db, expected_individual_id=identity)
    assert audit.may_recover and audit.generation == 1
    with recover_i1_m11(db_path=db, life_id=identity, runtime_factory=new_runtime) as recovered:
        rt = recovered._runtime
        assert rt.competition.export_causal_state() == frozen["competition"]
        assert rt.exploration.geographic.export_causal_state() == frozen["geography"]
        assert rt.sleep_session.export_causal_state() == frozen["sleep"]
        second = recovered.run_step()
        assert second.status == "active" and second.generation == first.generation + 1
        assert recovered._runtime.exploration.geographic.config.experienced_site_effects is True
print("I1_CROSS_L2_357_M11_OK")
"""
            env = dict(os.environ, PYTHONPATH=os.pathsep.join(
                (str(generated), str(ROOT / "src"), str(ROOT / "tools"))),
                PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run([sys.executable, "-B", "-c", code],
                cwd=ROOT, capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("I1_CROSS_L2_357_M11_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
