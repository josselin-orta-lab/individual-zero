"""A2.35 development witness: true I1 mortal steps, on/off and failed first act."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_i1_fork import generate


class I1A235PhysicalWitness(unittest.TestCase):
    def test_separate_mortal_lives_and_charged_recall(self):
        with TemporaryDirectory() as td:
            out = Path(td) / "generated"
            generate(out)
            program = r"""
import json
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_active_runtime import ExperimentalI1Stage12Runtime
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1lab.injected_scenario import ScenarioEvent
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from i1.experimental.stage6_visible_delta_shadow import ShadowVisibleDeltaModel,FIELDS
s11=build_stage11_reference_runtime(autonomous_mortal=True)
s10=build_stage10_reference_runtime(autonomous_mortal=True)
cfg=replace(s11.world.config,version="a235-mortal-witness-v1",
  initial_body=replace(s11.world.config.initial_body,
    food=10.0,water=90.0,energy=66.0,integrity=100.0))
layout=replace(s11.world._layout,
  resources=((cfg.initial_position,"berry_b",14),),
  water_sources=frozenset(),obstacles=frozenset(),
  danger_zones=frozenset(),lethal_zones=frozenset(),creatures=frozenset())
sleep=replace(s10._stage10_config.sleep,
  fatigue_gain=0.0,night_weight=0.0,consolidation_weight=0.0)
s10cfg=replace(s10._stage10_config,stage9=s11._stage11_config.stage9,sleep=sleep)
detector=Stage12DetectionPolicy(
  version="a235-mortal-witness-v1",window=12,stagnation_steps=3,
  stagnation_tolerance=.05,loop_repetitions=2,loop_max_period=2,
  entropy_min_samples=3,entropy_warning_fraction=.25,
  bias_min_outcomes_each=2,attribution_bias_threshold=.75)
coefficients=lambda a:tuple((k, (1 if (a=="COLLECT_B" and k=="inventory_berry_b") else 0)) for k in FIELDS)
model=ShadowVisibleDeltaModel("stage6-visible-deltas-shadow-v1","a"*64,
 tuple((action,coefficients(action)) for action in ("MOVE_E","COLLECT_B")),
 (("MOVE_E",8),("COLLECT_B",8)))
results={}
with TemporaryDirectory() as root:
 for name,enabled,forced in (("on",True,False),("off",False,False),("failed",True,True)):
  opts=({"scenario_id":"a235-forced-"+name,
    "scenario_version":"a235-forced-v1",
    "scenario_events":(ScenarioEvent(t_monde=1,sequence=0,
      operation="set_action_failure_schedule",
      payload={"primitive":"collecter","schedule":[True]},
      phase="before_step"),)} if forced else {})
  life=ExperimentalI1Stage12Runtime(
    world_config=cfg,layout=layout,
    safety_config=s11.stage3.substrate.safety._config,
    safety_facts=s11._canonical_safety._innate,
    protected_integrity_threshold=s11.stage3.control._config.protected_integrity_threshold,
    stage11_config=s11._stage11_config,stage10_config=s10cfg,
    equipment=s11.equipment,autonomous_mortal=True,
    wal_path=str(Path(root)/(name+".wal")),birth_life_id="i1:a235:"+name,
    diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
    detector_policy=detector,i1_model_enabled=True,i1_model=model,
    i1_lived_recall_enabled=enabled,i1_recall_cost_uc=1)
  steps=[]
  for i in range(10):
   outcome=life.run_step()
   steps.append({"t":i+1,"status":outcome.execution_status,
                 "action":outcome.command_primitive})
   if outcome.execution_status!="applied":break
  assert life.journal.verify()
  events=[dict(e.causal_event) for e in life.journal.entries]
  review=[{"t":e.get("t_monde"),"sources":e["data"].get("source_event_refs")}
          for e in events if e.get("kind")=="i1_lived_recall_review"]
  evidence=[{"t":e.get("t_monde"),"evidence":e["data"]["evidence"]}
            for e in events if e.get("kind")=="stage8_option_evaluation"
            and str(e["data"].get("learning_signature","")).startswith("i1_partial:")]
  recall=[{"t":e.get("t_monde"),"ep":e["data"]["episode_ref"]}
            for e in events if e.get("kind")=="memory_recall_proposed"]
  closes=[{"t":e.get("t_monde"),"ep":e["data"]["id"],
          "refs":len(e["data"]["event_refs"])}
          for e in events if e.get("kind")=="episode_closed"]
  results[name]={"steps":steps,"review":review,
    "evidence":evidence,"recalls":recall,"closed":closes,
    "positive_lived_boost":any(v["evidence"]==0.45 for v in evidence),
    "journal_sha":life.journal.head_hash,
    "charged":sum(e.get("kind")=="compute_charge"
     and e["data"].get("operation")=="i1_lived_recall_review"
     and e["data"].get("accepted") for e in events)}
 assert results["off"]["review"]==[] and results["off"]["charged"]==0
 assert results["on"]["charged"]>=1 and results["failed"]["charged"]>=1
 assert all(v["evidence"]==0.35 for v in results["off"]["evidence"])
 print("A235_WITNESS:"+json.dumps(results,sort_keys=True))
"""
            env=os.environ.copy()
            env["PYTHONPATH"]=str(out)+os.pathsep+str(Path(__file__).resolve().parents[1]/"src")
            result=subprocess.run([sys.executable,"-c",program],
                                  env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr+"\n"+result.stdout)
            self.assertIn("A235_WITNESS:",result.stdout)
            print(result.stdout.strip())


if __name__=="__main__":
    unittest.main()
