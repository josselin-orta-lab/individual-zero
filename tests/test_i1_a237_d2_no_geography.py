"""A2.37-R1: D2 cannot manufacture visited terrain when geography is absent."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from build_i1_fork import generate


class I1A237D2NoGeographyTests(unittest.TestCase):
    def test_physically_lived_water_then_unknown_movement_abstains(self):
        with TemporaryDirectory() as tmp:
            generated=Path(tmp)/"generated"
            generate(generated)
            code=r"""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_d2_runtime import I1WaterPrudentRuntime,REVIEW
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1lab.journal import HashChainedJournal
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from i1.experimental.stage6_visible_delta_shadow import ShadowVisibleDeltaModel,FIELDS

s11=build_stage11_reference_runtime(autonomous_mortal=True)
s10=build_stage10_reference_runtime(autonomous_mortal=True)
stage11=s11._stage11_config
s9=stage11.stage9;s8=s9.stage8;s7=s8.stage7;s6=s7.stage6;s4=s6.stage4
needs=replace(s4.value_needs,version="a237-d2-none-needs-v1",
 setpoints={**s4.value_needs.setpoints,"water":95.0,"food":80.0})
plan=replace(s6.planning,version="a237-d2-none-plan-v1",
 setpoints={**s6.planning.setpoints,"water":95.0,"food":80.0})
s9=replace(s9,stage8=replace(s8,stage7=replace(s7,
 stage6=replace(s6,stage4=replace(s4,value_needs=needs),planning=plan))))
stage11=replace(stage11,stage9=s9,geographic=None)
sleep=replace(s10._stage10_config.sleep,version="a237-d2-none-sleep-v1",
 fatigue_gain=0.0,night_weight=0.0,consolidation_weight=0.0)
stage10=replace(s10._stage10_config,stage9=s9,sleep=sleep)
initial=s11.world.config.initial_position
world_config=replace(s11.world.config,version="a237-d2-none-world-v1",
 initial_body=replace(s11.world.config.initial_body,
 food=14.0,water=12.0,energy=65.0,integrity=100.0))
layout=replace(s11.world._layout,
 resources=((initial.moved("east"),"berry_b",12),),
 water_sources=frozenset({initial}),danger_zones=frozenset(),
 lethal_zones=frozenset(),obstacles=frozenset(),creatures=frozenset())
delta=tuple((act,tuple((k,1 if (act=="COLLECT_B" and k=="inventory_berry_b") else 0)
 for k in FIELDS)) for act in ("MOVE_E","COLLECT_B"))
model=ShadowVisibleDeltaModel("stage6-visible-deltas-shadow-v1","a"*64,
 delta,(("MOVE_E",8),("COLLECT_B",8)))
policy=Stage12DetectionPolicy(version="a237-d2-none-detectors-v1",
 window=12,stagnation_steps=3,stagnation_tolerance=.05,
 loop_repetitions=2,loop_max_period=2,entropy_min_samples=3,
 entropy_warning_fraction=.25,bias_min_outcomes_each=2,
 attribution_bias_threshold=.75)
with TemporaryDirectory() as home:
 path=str(Path(home)/"life.wal")
 life=I1WaterPrudentRuntime(
  world_config=world_config,layout=layout,
  safety_config=s11.stage3.substrate.safety._config,
  safety_facts=s11._canonical_safety._innate,
  protected_integrity_threshold=s11.stage3.control._config.protected_integrity_threshold,
  stage11_config=stage11,stage10_config=stage10,
  equipment=s11.equipment,autonomous_mortal=True,
  wal_path=path,birth_life_id="i1:a237:none-geography",
  diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
  detector_policy=policy,i1_model_enabled=True,i1_model=model,
  i1_lived_recall_enabled=True,i1_recall_cost_uc=1,
  i1_water_probe_enabled=True,i1_water_learning_enabled=True,
  i1_water_consider_uc=2,i1_water_acquire_uc=2,
  i1_d2_prudence=True,i1_d2_review_uc=1)
 assert life.exploration.geographic is None
 for i in range(5):
  outcome=life.run_step()
  assert outcome.execution_status=="applied",(i,outcome.execution_status)
 assert life.journal.verify()
 audit=HashChainedJournal.audit_durable_wal(path)
 assert audit["head_hash"]==life.journal.head_hash
 events=[e.causal_event for e in life.journal.entries]
 reviews=[e["data"] for e in events if e["kind"]=="i1_d2_movement_commitment_review"]
 assert reviews,"expected authentic D2 review, not invented geography"
 assert all(r["prior_physical_visit"] is False and
  r["current_safety_known"] is False and
  r["decision"]=="defer_unknown_or_unfunded" for r in reviews)
 charges=[e["data"] for e in events if e["kind"]=="compute_charge"
  and e.get("data",{}).get("operation")==REVIEW]
 assert charges and all(c["accepted"] is True for c in charges)
 assert all(e["data"]["command"]["primitive"]!="se_deplacer"
  for e in events if e["kind"]=="command_admitted" and "command" in e.get("data",{}))
 print("I1_A237_NO_GEOGRAPHY_ABSTAINS_OK")
"""
            env=os.environ.copy()
            env["PYTHONPATH"]=str(generated)+os.pathsep+str(
                Path(__file__).resolve().parents[1]/"src")
            run=subprocess.run([sys.executable,"-c",code],
                env=env,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr+"\n"+run.stdout)
            self.assertIn("I1_A237_NO_GEOGRAPHY_ABSTAINS_OK",run.stdout)


if __name__=="__main__":
    unittest.main()
