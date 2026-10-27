"""Generated natural I1 lived-site route, no fabricated entity or motor choice."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class LivedSiteNaturalL2(unittest.TestCase):
    def test_generated_natural_pipeline_and_cold_m11(self):
        with TemporaryDirectory(prefix="i1-384-") as directory:
            build = Path(directory) / "generated"
            generate(build)
            program = r"""
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.stage11_runtime import Stage11Runtime
from i1.modules.stage11_evaluator import Stage11OptionEvaluator
from i1.modules.geographic_exploration import GeographicExploration
from i1.modules.geographic_planning import propose_lived_site_return
from i1.modules.spatial_memory import find_lived_site_returns
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset, _birth_parameters

source=inspect.getsource(Stage11Runtime._phase_hooks)
assert "find_lived_site_returns(" in source
assert "propose_lived_site_return(" in source
assert "freeze_lived_sites(" in source
assert 'operation="geographic_route_search"' in source
assert 'operation="competition_register"' in source
assert "i1_lived_site_option_registration" in source
assert "lived_site" in inspect.getsource(Stage11OptionEvaluator.evaluate)
assert "site_effect_for(" in inspect.getsource(Stage11OptionEvaluator._experienced_site_context)
assert "lived_offered" in inspect.getsource(GeographicExploration.export_causal_state)

preset,_ = load_preset("oasis")
params,_ = _birth_parameters(preset)
params = dict(params,diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1)
life_id="i1:384:natural-return"
def fresh():
    return I1Runtime(birth_life_id=life_id,wal_path=None,
        autonomous_mortal=True,m11_sqlite_custody=True,**params)
def state(rt):
    return {owner.owner_id:owner.export_causal_state() for owner in rt.causal_owners}
with TemporaryDirectory() as folder:
    db=str(Path(folder)/"life.sqlite")
    with birth_i1_m11(db_path=db,life_id=life_id,**params) as born:
        for i in range(6):
            receipt=born.run_step()
            assert receipt.status=="active",receipt
        prior=state(born._runtime)
        prior_geo=born._runtime.exploration.geographic.export_causal_state()
    audit=SQLiteLifeLedger.audit_read_only(path=db,expected_individual_id=life_id)
    assert audit.may_recover and audit.generation==6 and not audit.pending_intent
    with recover_i1_m11(db_path=db,life_id=life_id,runtime_factory=fresh) as cold:
        assert state(cold._runtime)==prior
        assert cold._runtime.exploration.geographic.export_causal_state()==prior_geo
        receipt=cold.run_step()
        assert receipt.status=="active" and receipt.generation==7
        for e in cold._runtime.journal.entries_since(0):
            event=e.causal_event
            if event.get("kind")=="i1_lived_site_option_registration":
                assert event["data"]["option_ref"].startswith("option:lived-site:")
    final=SQLiteLifeLedger.audit_read_only(path=db,expected_individual_id=life_id)
    assert final.may_recover and final.generation==7 and not final.pending_intent
print("I1_384_LIVED_SITE_NATURAL_CUSTODY_OK")
"""
            env = dict(os.environ, PYTHONPATH=os.pathsep.join(
                (str(build), str(ROOT / "src"), str(ROOT / "tools"))),
                PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run(
                [sys.executable, "-B", "-c", program],
                cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            self.assertIn("I1_384_LIVED_SITE_NATURAL_CUSTODY_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
