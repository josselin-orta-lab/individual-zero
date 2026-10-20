"""#329: autonomous reentry preserves freedom to sleep, without a wake lock."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class AwakeSleepReentryTests(unittest.TestCase):
    def test_generated_owner_gate_and_natural_m11(self):
        with TemporaryDirectory(prefix="i1-329-") as tmp:
            built=Path(tmp)/"generated"
            generate(built)
            program=r'''
from pathlib import Path
from tempfile import TemporaryDirectory
import inspect
from i1.interfaces import PrimitiveCommand
from i1.modules.action_control import AdmissionResult,PreparedCommand
from i1.modules.sleep_session import SleepSession
from i1.modules.sleep_pressure import SleepPressureConfig,SleepPressureRules,WakeSignals
from i1lab.stage10_runtime import Stage10Runtime
from i1lab.i1_birth import birth_i1_m11,recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from run_i1_world_preset import load_preset,_birth_parameters

source=inspect.getsource(Stage10Runtime._sleep_step)
assert "record_applied_sleep_decision" in source
assert "_verify_ordinary_sleep_provenance" in source
assert source.index("finish_sleep_step(")<source.index("record_applied_sleep_decision(")
assert "stage10_sleep_woke" in source
cfg=SleepPressureConfig(version="wake:329",fatigue_gain=.1,sleep_fatigue_recovery=.1,
 waking_recovery_profile_relief=0,fatigue_weight=.5,consolidation_weight=.3,
 night_weight=.2,unconsolidated_episode_reference=8,
 memory_saturation_reference=2,natural_wake_threshold=.1,
 alert_wake_threshold=.7,max_consecutive_sleep_steps=6)
rules=SleepPressureRules(cfg)
sleep=SleepSession(wake_policy_version=cfg.version)
cmd=PrimitiveCommand("dormir")
prepared=PreparedCommand(command=cmd,source="decision",option_ref="option:329")
admission=AdmissionResult(ok=True,reason=None,scope=None,rule_id=None,
 rule_type=None,policy_version="test",command=cmd)
assert sleep.open_world_step(1)=="awake"
sleep.record_applied_sleep_decision(world_step=1,admission=admission,
 prepared=prepared,execution_status="applied")
assert sleep.open_world_step(2)=="sleeping"
wake=sleep.evaluate_sleep_step(signals=WakeSignals(admitted_reflex=False,
 reduced_perception_alert=1.0,authorized_dated_intention_due=False,
 consecutive_sleep_steps=1,consolidation_active=False),
 frozen_sleep_pressure=.8,wake_rule=rules)
assert wake.reason=="alert" and wake.resume_cognition
sleep.finish_sleep_step(decision=wake,admission=admission,prepared=prepared,
 command_sent=True,world_advanced=True,consolidation_interrupted=False)
sleep.record_applied_sleep_decision(world_step=2,admission=admission,
 prepared=prepared,execution_status="applied")
assert sleep.export_causal_state()["admitted_sleep_step"]==2
cold=SleepSession(wake_policy_version=cfg.version)
cold.restore_causal_state(sleep.export_causal_state())
assert cold.open_world_step(3)=="sleeping"
false=SleepSession(wake_policy_version=cfg.version)
false.open_world_step(1)
for status in ("refused","not_applied"):
 try:
  false.record_applied_sleep_decision(world_step=1,admission=admission,
   prepared=prepared,execution_status=status)
  raise AssertionError("nonapplied reentry sleep accepted")
 except ValueError: pass
assert false.export_causal_state()["admitted_sleep_step"] is None
# No suppression of a sleep candidate or alteration of wake thresholds.
assert "invalidate_candidate" not in source and "sleep_option_registered" not in source
preset,_=load_preset("oasis")
params,_=_birth_parameters(preset)
params=dict(params,diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1)
life_id="i1:329:reentry-natural"
def fresh():
 return I1Runtime(birth_life_id=life_id,wal_path=None,
   autonomous_mortal=True,m11_sqlite_custody=True,**params)
with TemporaryDirectory() as temp:
 db=str(Path(temp)/"life.sqlite")
 with birth_i1_m11(db_path=db,life_id=life_id,**params) as life:
  first=life.run_step()
  assert first.status=="active"
 with recover_i1_m11(db_path=db,life_id=life_id,runtime_factory=fresh) as life:
  second=life.run_step()
  assert second.status=="active" and second.generation==first.generation+1
print("I1_329_WAKE_REENTRY_OWNER_M11_OK")
'''
            env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(built),str(ROOT/"src"),str(ROOT/"tools"))),
                     PYTHONDONTWRITEBYTECODE="1")
            proc=subprocess.run([sys.executable,"-B","-c",program],cwd=ROOT,
                                capture_output=True,text=True,env=env)
            self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
            self.assertIn("I1_329_WAKE_REENTRY_OWNER_M11_OK",proc.stdout)

if __name__=="__main__":
    unittest.main()
