"""Canonical I1 independent-local candidate integration, no population campaign.

A few authentic, mortal M11 steps demonstrate that locally perceived options
enter the real Planning and Competition pipeline alongside goal-linked ones.
The separate pure negative checks cannot be called ecological efficacy tests.
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


class LocalOpportunityNaturalIntegration(unittest.TestCase):
    def generated(self, code):
        with TemporaryDirectory(prefix="i1-327-") as folder:
            built = Path(folder) / "i1-built"
            generate(built)
            env = dict(os.environ, PYTHONPATH=os.pathsep.join((
                str(built), str(ROOT / "src"), str(ROOT / "tools"),
            )), PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run(
                [sys.executable, "-B", "-c", code], cwd=ROOT, env=env,
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return result.stdout

    def test_canonical_birth_phase_path_and_uc_costs(self):
        self.assertIn("I1_327_CANONICAL_BIRTH_OK", self.generated(r'''
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset, _birth_parameters
from i1.experimental.local_opportunity_selection import local_interaction_choices

source,_=load_preset("oasis")
parameters,at_birth=_birth_parameters(source)
params=dict(parameters,diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1)
life_id="i1:local:327:canonical"
def fresh():
    return I1Runtime(birth_life_id=life_id,wal_path=None,
                     autonomous_mortal=True,m11_sqlite_custody=True,**params)

with TemporaryDirectory(prefix="i1-327-lived-") as tmp:
    db=str(Path(tmp)/"life.sqlite")
    with birth_i1_m11(db_path=db,life_id=life_id,**params) as life:
        rt=life._runtime
        assert type(rt) is I1Runtime
        cfg=rt._config.compute_budget
        assert cfg.operation_costs["i1_unknown_action_consider"]>0
        assert cfg.operation_costs["competition_register"]>0
        assert cfg.operation_costs["competition_evaluate"]>0
        assert "goal-independent-local" in cfg.version
        start=len(rt.journal.entries_since(0))
        receipt=life.run_step()
        assert receipt.status=="active"
        entries=[item.causal_event for item in life._runtime.journal.entries_since(start)]
        local=[item for item in entries if item.get("kind")=="i1_local_opportunity_perceived"]
        assert local,"natural birth did not run independent local producer"
        proposals=[item for item in entries if item.get("kind")=="i1_local_opportunity_proposed"]
        assert proposals, "visible oasis produced no competing local proposal"
        registrations=[item for item in entries
                       if item.get("kind")=="i1_local_opportunity_registration"]
        assert registrations,"local proposal bypassed normal Competition register"
        assert all(item.get("data",{}).get("goal_ref") is None
                   for item in proposals), proposals
        assert all(item.get("data",{}).get("motor_command_forced") is False
                   and item.get("data",{}).get("predicted_result") is None
                   for item in proposals), proposals
        # The actual applied command remains solely Action Control's.
        assert receipt.outcome in ("applied","dead","safety_block")
        assert life._runtime.stage3.substrate.bench is None
    audit=SQLiteLifeLedger.audit_read_only(path=db,expected_individual_id=life_id)
    assert audit.may_recover and audit.generation==1 and not audit.pending_intent
    with recover_i1_m11(db_path=db,life_id=life_id,runtime_factory=fresh) as resumed:
        assert type(resumed._runtime) is I1Runtime
        followup=resumed.run_step()
        assert followup.generation==2 and followup.status=="active"
print("I1_327_CANONICAL_BIRTH_OK")
'''))

    def test_local_filter_and_scoring_identity(self):
        self.assertIn("I1_327_NEGATIVE_CONTRACT_OK", self.generated(r'''
from i1.experimental.local_opportunity_selection import local_interaction_choices
from i1.interfaces import PrimitiveCommand
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.i1_active_runtime import I1PartialEvidenceAdapter
from i1.modules.competition import OptionEvidenceInput
from i1.contracts import EvaluationOption
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from dataclasses import replace

available=(PrimitiveCommand("collecter",{"target":"wood"}),
           PrimitiveCommand("se_deplacer",{"direction":"east"}),
           PrimitiveCommand("boire"),
           PrimitiveCommand("attendre"))
assert len(local_interaction_choices(available,enabled=True))==2
assert local_interaction_choices(available,enabled=False)==()
try: local_interaction_choices(available,enabled="true")
except ValueError: pass
else: raise AssertionError("nonbool enabled accepted")
try: local_interaction_choices(available*33,enabled=True)
except ValueError: pass
else: raise AssertionError("unbounded candidates accepted")
assert I1Runtime._phase_hooks is not None
# One advisory Q owner and one evaluation adapter; no new Q/TD writer.
import inspect
text=inspect.getsource(I1Runtime._phase_hooks)
assert "normal_plan(ctx)" in text and "normal_register(ctx)" in text
assert "competition_register" in text
assert "i1_local_opportunity_registration" in text
assert "stage3.control.dispatch" not in text
text2=inspect.getsource(I1Runtime._propose_independent_local)
assert "q_active.learned_value" in text2
assert "state_from_capture" in text2
assert "local_interaction_choices" in text2
print("I1_327_NEGATIVE_CONTRACT_OK")
'''))


if __name__ == "__main__":
    unittest.main()
