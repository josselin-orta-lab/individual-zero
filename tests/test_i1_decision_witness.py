"""Independent I1 life: force no planner leak, collect real decision receipts.

This is a synthetic SOFTWARE control with a declared fake corpus digest. It is
not a scientific A2.30 prospective independent-life replication.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_i1_fork import generate


class I1DecisionWitnessTests(unittest.TestCase):
    def test_partial_model_in_actual_mortal_cognitive_cycle(self):
        with TemporaryDirectory() as d:
            output = Path(d) / "fork"
            generate(output)
            source = r"""
import json
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_active_runtime import ExperimentalI1Stage12Runtime
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1lab.world import Position
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from i1.experimental.stage6_visible_delta_shadow import (
    ShadowVisibleDeltaModel, FIELDS
)
s11 = build_stage11_reference_runtime(autonomous_mortal=True)
s10 = build_stage10_reference_runtime(autonomous_mortal=True)
world = replace(s11.world.config,
    version="i1-decision-software-fixture-v1",
    initial_body=replace(s11.world.config.initial_body,
                         food=10.0, water=90.0, energy=60.0))
layout = replace(s11.world._layout,
    resources=((world.initial_position, "berry_b", 3),),
    water_sources=frozenset())
sleep = replace(s10._stage10_config.sleep,
    fatigue_gain=0.0, night_weight=0.0, consolidation_weight=0.0)
config = replace(s10._stage10_config, stage9=s11._stage11_config.stage9, sleep=sleep)
p = Stage12DetectionPolicy(
    version="i1-decision-witness-v1", window=12, stagnation_steps=3,
    stagnation_tolerance=.05, loop_repetitions=2, loop_max_period=2,
    entropy_min_samples=3, entropy_warning_fraction=.25,
    bias_min_outcomes_each=2, attribution_bias_threshold=.75
)
def coefficients(action):
    values = {"x":1 if action=="MOVE_E" else 0,
              "y":0, "energy":0.0, "food":0.0, "water":0.0,
              "inventory_berry_b":1 if action=="COLLECT_B" else 0}
    return tuple((key,values[key]) for key in FIELDS)
model = ShadowVisibleDeltaModel(
    "stage6-visible-deltas-shadow-v1", "a"*64,
    tuple((name,coefficients(name)) for name in ("MOVE_E","COLLECT_B")),
    (("MOVE_E",8),("COLLECT_B",8)))
def birth(enabled, directory):
    return ExperimentalI1Stage12Runtime(
        world_config=world, layout=layout,
        safety_config=s11.stage3.substrate.safety._config,
        safety_facts=s11._canonical_safety._innate,
        protected_integrity_threshold=s11.stage3.control._config.protected_integrity_threshold,
        stage11_config=s11._stage11_config,stage10_config=config,
        equipment=s11.equipment, autonomous_mortal=True,
        wal_path=str(directory/("on.wal" if enabled else "off.wal")),
        birth_life_id="i1:decision:" + ("on" if enabled else "off"),
        diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
        detector_policy=p,i1_model_enabled=enabled,
        i1_model=model if enabled else None)
with TemporaryDirectory() as d:
    on=birth(True,Path(d))
    off=birth(False,Path(d))
    results={}
    for label,life in (("on",on),("off",off)):
        physical=[]
        for step in range(3):
            x=life.run_step()
            physical.append(x.execution_status)
            if x.execution_status == "dead":
                break
        assert life.journal.verify()
        entries=[json.loads(line)["causal_event"] for line in
                 life.journal.canonical_bytes().splitlines()]
        kinds=[entry["kind"] for entry in entries]
        i1events=[e for e in entries if e["kind"].startswith("i1_partial_")]
        results[label]={"physical":physical,"i1_kinds":[x["kind"] for x in i1events],
                        "active_goal":(life.goal_manager.active_goal.goal_type
                        if life.goal_manager.active_goal else None),
                        "planning": [e["data"] for e in entries
                            if e["kind"]=="stage6_planning_result"][-6:],
                        "registered":[e["data"] for e in entries
                            if e["kind"]=="option_registration"][-6:]}
        if label=="on":
            assert "i1_partial_preaction_forecast" in kinds, str(results)
            assert "i1_partial_instrumental_option_proposed" in kinds, str(results)
            for event in i1events:
                if event["kind"]=="i1_partial_preaction_forecast":
                    p=event["data"]["result"]
                    assert p["safe"] is None and p["terminal"] is None
                    assert p["causal_responsibility"] is None
                    assert event["data"]["physical_safety_certified"] is False
        else:
            assert not i1events, str(results)
    print("I1_DECISION_WITNESS_SOFTWARE:",json.dumps(results,sort_keys=True))
"""
            result=subprocess.run([sys.executable,"-c",source],
                env={"PYTHONPATH":str(output)+":"+str(
                    Path(__file__).resolve().parents[1]/"src")},
                text=True,capture_output=True,check=False)
            self.assertEqual(result.returncode,0,result.stderr + "\n" + result.stdout)
            self.assertIn("I1_DECISION_WITNESS_SOFTWARE:",result.stdout)


if __name__=="__main__":
    unittest.main()
