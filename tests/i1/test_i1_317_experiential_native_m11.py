"""M11 whole-current-state cold parity for opt-in native Stage8 relevancy.

Use a fresh generation, never an older rollback. The canonical birth is
unchanged, while changing the research flag on cold recovery must fail.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class ExperientialM11Cold317(unittest.TestCase):
    def test_fresh_birth_cold_recovery_and_contract_rejection(self):
        with TemporaryDirectory() as folder:
            generated=Path(folder)/"generated"
            generate(generated)
            script="""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.m11_transactional_mortal import M11TransactionalMortal
from i1lab.sqlite_life_store import RecoveryBlocked
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from i1.modules.experienced_place_relevance import I1ExperiencedPlaceStage8
base=build_stage11_reference_runtime(autonomous_mortal=True)
sleep=build_stage10_reference_runtime(autonomous_mortal=True)
stage10=replace(sleep._stage10_config,stage9=base._stage11_config.stage9)
detector=Stage12DetectionPolicy(
    version="i1-experience-m11-317",window=12,stagnation_steps=3,
    stagnation_tolerance=.05,loop_repetitions=2,loop_max_period=2,
    entropy_min_samples=3,entropy_warning_fraction=.25,
    bias_min_outcomes_each=2,attribution_bias_threshold=.75)
life_id="i1:experience:m11:317"
params=dict(
    world_config=base.world.config,layout=base.world._layout,
    safety_config=base.stage3.substrate.safety._config,
    safety_facts=base._canonical_safety._innate,
    protected_integrity_threshold=
        base.stage3.control._config.protected_integrity_threshold,
    stage11_config=base._stage11_config,stage10_config=stage10,
    equipment=base.equipment,detector_policy=detector,
    diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1)
def fresh(enabled):
    return I1Runtime(
        birth_life_id=life_id,autonomous_mortal=True,
        m11_sqlite_custody=True,wal_path=None,
        i1_experienced_place_enabled=enabled,**params)
with TemporaryDirectory() as temp:
    p1=str(Path(temp)/"continuous.sqlite")
    p2=str(Path(temp)/"cold.sqlite")
    with M11TransactionalMortal.birth(
        db_path=p1,runtime=fresh(True),individual_id=life_id) as continuous:
        assert isinstance(continuous._runtime.stage8_option_evaluator,
                          I1ExperiencedPlaceStage8)
        one=continuous.run_step()
        two=continuous.run_step()
        assert one.status==two.status=="active"
    with M11TransactionalMortal.birth(
        db_path=p2,runtime=fresh(True),individual_id=life_id) as cold:
        first=cold.run_step()
        assert first.journal_head==one.journal_head
    try:
        with M11TransactionalMortal.cold_recover(
            db_path=p2,individual_id=life_id,
            runtime_factory=lambda:fresh(False)):
            pass
    except RecoveryBlocked:
        pass
    else:
        raise AssertionError("changed research birth contract accepted")
    with M11TransactionalMortal.cold_recover(
        db_path=p2,individual_id=life_id,
        runtime_factory=lambda:fresh(True)) as resumed:
        assert isinstance(resumed._runtime.stage8_option_evaluator,
                          I1ExperiencedPlaceStage8)
        later=resumed.run_step()
        assert later.world_step==2
        assert later.journal_head==two.journal_head
print("I1_EXPERIENTIAL_NATIVE_M11_CURRENT_COLD_PARITY_OK")
"""
            proc=subprocess.run(
                [sys.executable,"-c",script],
                env={"PYTHONPATH":str(generated)+":"+str(ROOT/"src")},
                capture_output=True,text=True,check=False)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertIn("I1_EXPERIENTIAL_NATIVE_M11_CURRENT_COLD_PARITY_OK",proc.stdout)
if __name__=="__main__":
    unittest.main()
