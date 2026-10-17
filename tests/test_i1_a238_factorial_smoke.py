"""A2.38 exploratory developer smoke, NOT confirmatory 160-birth science."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_i1_fork import generate


class I1A238FactorialSmoke(unittest.TestCase):
    def test_four_living_ablation_arms_and_hidden_lethal(self):
        with TemporaryDirectory() as tmp:
            generated = Path(tmp) / "generated"
            generate(generated)
            code = r"""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_a238_runtime import I1A238ExperimentalRuntime, H1_REVIEW, H2_REVIEW
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1lab.journal import HashChainedJournal
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from i1.experimental.stage6_visible_delta_shadow import ShadowVisibleDeltaModel,FIELDS
from i1lab.world import BerryEffect

s11 = build_stage11_reference_runtime(autonomous_mortal=True)
s10 = build_stage10_reference_runtime(autonomous_mortal=True)
s9=s11._stage11_config.stage9;s8=s9.stage8;s7=s8.stage7;s6=s7.stage6;s4=s6.stage4
needs=replace(s4.value_needs,version="a238-smoke-needs",
 setpoints={**s4.value_needs.setpoints,"water":92.0,"food":77.0})
plan=replace(s6.planning,version="a238-smoke-plan",
 setpoints={**s6.planning.setpoints,"water":92.0,"food":77.0})
s9=replace(s9,stage8=replace(s8,stage7=replace(s7,
 stage6=replace(s6,stage4=replace(s4,value_needs=needs),planning=plan))))
s11conf=replace(s11._stage11_config,stage9=s9,geographic=None)
sleep=replace(s10._stage10_config.sleep,version="a238-smoke-sleep",
 fatigue_gain=0.0,night_weight=0.0,consolidation_weight=0.0)
s10conf=replace(s10._stage10_config,stage9=s9,sleep=sleep)
delta=tuple((act,tuple((k,1 if (act=="MOVE_E" and k=="x") or
 (act=="COLLECT_B" and k=="inventory_berry_b") else 0)
 for k in FIELDS)) for act in ("MOVE_E","COLLECT_B"))
model=ShadowVisibleDeltaModel("stage6-visible-deltas-shadow-v1","a"*64,
 delta,(("MOVE_E",8),("COLLECT_B",8)))
policy=Stage12DetectionPolicy(version="a238-smoke-detection-v1",
 window=12,stagnation_steps=3,stagnation_tolerance=.05,
 loop_repetitions=2,loop_max_period=2,entropy_min_samples=3,
 entropy_warning_fraction=.25,bias_min_outcomes_each=2,
 attribution_bias_threshold=.75)
with TemporaryDirectory() as home:
 for scenario in ("blocked", "safe", "lethal"):
  for arm, alt, move in (("BASE",False,False),("ALTERNATE_NEED",True,False),
                         ("BOUNDED_MOVE",False,True),("BOTH",True,True)):
   root=Path(home)/scenario/arm
   root.mkdir(parents=True)
   initial=s11.world.config.initial_position
   east=initial.moved("east")
   physical=replace(s11.world.config,version="a238-smoke-real-costs",
    initial_body=replace(s11.world.config.initial_body,energy=64,
     food=13,water=18,integrity=100),
    food_decay_per_step=.2,water_decay_per_step=.4,
    action_energy_costs={"se_deplacer":2.0,"collecter":1.0,
     "manger":.5,"boire":.5,"attendre":.35,"dormir":.25,
     "poser_une_pierre":1.5,"fabriquer_outil":1.5},
    berry_effects={"berry_a":BerryEffect(0,-100),
     "berry_b":BerryEffect(6,0)})
   blocked=scenario=="blocked"
   layout=replace(s11.world._layout,
    resources=(((initial if blocked else east),"berry_b",11),),
    water_sources=frozenset({east if blocked else initial}),
    lethal_zones=frozenset({east} if scenario=="lethal" else {}),
    danger_zones=frozenset(),creatures=frozenset(),obstacles=frozenset())
   wal=str(root/"life.wal")
   life=I1A238ExperimentalRuntime(
    world_config=physical,layout=layout,
    safety_config=s11.stage3.substrate.safety._config,
    safety_facts=s11._canonical_safety._innate,
    protected_integrity_threshold=s11.stage3.control._config.protected_integrity_threshold,
    stage11_config=s11conf,stage10_config=s10conf,
    equipment=s11.equipment,autonomous_mortal=True,
    wal_path=wal,birth_life_id="i1:a238:smoke:"+scenario+":"+arm,
    diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
    detector_policy=policy,i1_model_enabled=True,i1_model=model,
    i1_lived_recall_enabled=True,i1_recall_cost_uc=1,
    i1_water_probe_enabled=True,i1_water_learning_enabled=True,
    i1_water_consider_uc=2,i1_water_acquire_uc=2,
    i1_d2_prudence=True,i1_d2_review_uc=1,
    i1_a238_alternate_need=alt,i1_a238_bounded_move=move,
    i1_a238_need_review_uc=1,i1_a238_move_review_uc=3,
    i1_a238_max_move_reviews=2)
   for _ in range(12):
    out=life.run_step()
    if out.execution_status!="applied":
     break
   assert life.journal.verify(),(scenario,arm,"journal")
   audit=HashChainedJournal.audit_durable_wal(wal)
   assert audit["head_hash"]==life.journal.head_hash,(scenario,arm,"wal")
   events=[e.causal_event for e in life.journal.entries]
   charges=[e.get("data",{}) for e in events if e["kind"]=="compute_charge"]
   h1=[c for c in charges if c.get("operation")==H1_REVIEW]
   h2=[c for c in charges if c.get("operation")==H2_REVIEW]
   assert not (h1 and not alt),(scenario,arm,"H1 off billed")
   assert not (h2 and not move),(scenario,arm,"H2 off billed")
   assert all(c.get("requested_uc")==1 for c in h1),(scenario,arm,"H1 price")
   assert all(c.get("requested_uc")==3 for c in h2),(scenario,arm,"H2 price")
   risk=[e["data"] for e in events if
      e["kind"]=="i1_a238_unknown_commitment_review"]
   assert len([x for x in risk if x["decision"]=="commit_unknown"])<=2
   assert all(x["hidden_world_queried"] is False and
      x["safety_known"] is False for x in risk)
   print("SMOKE",scenario,arm,
    "steps",life.scheduler.t_monde,
    "deaths",life.stage3.substrate.mortal_status.value,
    "H1",len(h1),"H2",len(h2),
    "collections",sum(e.get("kind")=="command_admitted" and
     e.get("data",{}).get("command",{}).get("primitive")=="collecter"
     for e in events))
print("I1_A238_FACTORIAL_SMOKE_OK")
"""
            env = os.environ.copy()
            env["PYTHONPATH"] = str(generated)+os.pathsep+str(
                Path(__file__).resolve().parents[1]/"src")
            proc = subprocess.run([sys.executable,"-c",code],env=env,
                                  text=True,capture_output=True)
            self.assertEqual(proc.returncode,0,proc.stdout+"\n"+proc.stderr)
            self.assertIn("I1_A238_FACTORIAL_SMOKE_OK",proc.stdout)


if __name__ == "__main__":
    unittest.main()
