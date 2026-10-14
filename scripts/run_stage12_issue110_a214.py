"""A2.14 offline-only translation and physical-outcome conflict experiment.

No runtime I0 modifications, no access to oracle, no inferred food etiology.
Only physically executed external WorldBody.apply consequences form examples.
"""
from __future__ import annotations
import argparse
from collections import Counter
from dataclasses import replace
import json
from pathlib import Path
import random
import subprocess

from i0.equipment import FrozenTableEquipment
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.simulator import state_from_capture
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import Position
from run_stage12_issue110_a213 import make_world

SEEDS=tuple(range(61,69))
FAMILIES=("translated_move_free","translated_move_blocked",
          "translated_collect","translated_eat","hidden_toxic",
          "hidden_hazard","visible_obstacle","body_saturation",
          "inventory_mismatch","night_creature")
TRANSLATED=frozenset(FAMILIES[:4])
HIDDEN=frozenset(("hidden_toxic","hidden_hazard"))
VISIBLE=frozenset(FAMILIES[6:])
_PHYSICAL_RECEIPTS=[]
_WORLD_ROLES={}

def hash_object(obj):
    return sha256_hex(canonical_causal_bytes(obj))

def view(world,t):
    return state_from_capture(
        capture=SymbolicPerception().capture(
            local_state=world.capture_local(t_monde=t).as_dict(),
            telemetry=world.telemetry()),
        is_night=world.is_night(t))

def relative_state(state):
    data=state.as_dict()
    origin=(data.pop("x"),data.pop("y"))
    for neighbor in data["adjacent"]:
        neighbor["x"]-=origin[0]
        neighbor["y"]-=origin[1]
    return data

def relational_key(state,command):
    return hash_object({"state":relative_state(state),
                        "command":command.as_dict()})

def physical_example(world,t,command):
    before=view(world,t)
    pos=(before.x,before.y)
    result=world.apply(command,t_monde=t)
    _PHYSICAL_RECEIPTS.append({
        "role":_WORLD_ROLES.get(id(world),"unregistered"),
        "t_monde":t,
        "command":command.as_dict(),
        "transition_sha256":hash_object(result.as_dict()),
    })
    after=view(world,t+1)
    outcome={
        "position_delta":{"x":after.x-pos[0],"y":after.y-pos[1]},
        "body_after":after.as_dict()["body"],
        "inventory_after":after.as_dict()["inventory"],
        "local_after":relative_state(after),
        "terminal":result.lethal,
        "effects":dict(result.effects),
    }
    return {
        "full_key":FrozenTableEquipment.input_digest(before,command),
        "relational_key":relational_key(before,command),
        "outcome_hash":hash_object(outcome),
        "outcome":outcome,
        "transition_sha256":hash_object(result.as_dict()),
        "state_before":before.as_dict(),
        "command":command.as_dict(),
    }

def consume_step(world,*,prep_t=1,food_t=2):
    command=PrimitiveCommand("collecter",{"target":"berry_a"})
    physical_example(world,prep_t,command)
    return physical_example(world,food_t,
        PrimitiveCommand("manger",{"target":"berry_a"}))

def world_for(base,p,food,water,family,role):
    options={}
    if family in ("translated_move_blocked",):
        options["obstacle"]=True
    if family=="visible_obstacle" and role=="heldout":
        options["obstacle"]=True
    if family=="inventory_mismatch" and role=="heldout":
        options["berry"]=False
    if family=="night_creature":
        options["creature"]=True
    if family=="body_saturation" and role=="heldout":
        food=97.0
    if family=="hidden_toxic" and role in ("heldout","conflict"):
        options["toxic"]=True
    return make_world(base,p,food,water,**options)

def world_step(world,family,role):
    if family in ("translated_collect",):
        return physical_example(world,1,
            PrimitiveCommand("collecter",{"target":"berry_a"}))
    if family in ("translated_eat","hidden_toxic","hidden_hazard",
                  "body_saturation","inventory_mismatch"):
        if family=="hidden_hazard":
            physical_example(world,1,
                PrimitiveCommand("collecter",{"target":"berry_a"}))
            if role in ("heldout","conflict"):
                world.apply_scenario_event("set_danger_zone",{
                    "position":world.position.as_dict(),"active":True})
            return physical_example(world,2,
                PrimitiveCommand("manger",{"target":"berry_a"}))
        return consume_step(world)
    if family=="night_creature":
        t=world.config.night_start_step+1 if role=="heldout" else 1
        return physical_example(world,t,PrimitiveCommand("attendre"))
    return physical_example(world,1,
        PrimitiveCommand("se_deplacer",{"direction":"east"}))

def positions_for(seed,family):
    rng=random.Random(seed*9973+FAMILIES.index(family)*100003)
    p=Position(rng.randint(6,17),rng.randint(6,17))
    delta=Position(rng.randint(3,8),rng.randint(3,8))
    return p,Position(p.x+delta.x,p.y+delta.y),float(rng.randint(39,55)),float(rng.randint(60,80))

class ConflictAbstainingLookup:
    """Offline strict key-to-observed-effects multiset; no synthetic effects."""
    def __init__(self):
        self.records={}
    def observe(self,row):
        self.records.setdefault(row["relational_key"],set()).add(row["outcome_hash"])
    def predict(self,row):
        choices=self.records.get(row["relational_key"],set())
        if len(choices)!=1:
            return None
        return next(iter(choices))

def run_pair(base,family,seed):
    _PHYSICAL_RECEIPTS.clear()
    _WORLD_ROLES.clear()
    source_p,target_p,food,water=positions_for(seed,family)
    source=world_for(base,source_p,food,water,family,"source")
    heldout=world_for(base,target_p,food,water,family,"heldout")
    _WORLD_ROLES.update({id(source):"source",id(heldout):"heldout"})
    src=world_step(source,family,"source")
    target=world_step(heldout,family,"heldout")
    extra=None
    if family in HIDDEN:
        # A separate physical prenatally witnessed contradiction, not the
        # heldout test world and never a hidden oracle label in cognition.
        conflict_p=Position(source_p.x+1,source_p.y+1)
        third=world_for(base,conflict_p,food,water,family,"conflict")
        _WORLD_ROLES[id(third)]="contradictory_prebirth"
        extra=world_step(third,family,"conflict")
    naive=ConflictAbstainingLookup()
    naive.observe(src)
    conservative=ConflictAbstainingLookup()
    conservative.observe(src)
    if extra is not None:
        conservative.observe(extra)
    naive_prediction=naive.predict(target)
    safe_prediction=conservative.predict(target)
    same_relational=src["relational_key"]==target["relational_key"]
    same_full=src["full_key"]==target["full_key"]
    outcome_equal=src["outcome_hash"]==target["outcome_hash"]
    if family in TRANSLATED:
        assert same_relational and not same_full and outcome_equal
        assert naive_prediction==target["outcome_hash"]
        assert safe_prediction==target["outcome_hash"]
    elif family in HIDDEN:
        assert same_relational and not outcome_equal
        assert extra["relational_key"]==target["relational_key"]
        assert extra["outcome_hash"]==target["outcome_hash"]
        assert naive_prediction is not None and naive_prediction!=target["outcome_hash"]
        assert safe_prediction is None
    else:
        assert not same_relational and naive_prediction is None and safe_prediction is None
    return {
        "family":family,"seed":seed,
        "source_coordinate":source_p.as_dict(),
        "heldout_coordinate":target_p.as_dict(),
        "full_key_covered":same_full,"relational_key_covered":same_relational,
        "source_outcome_sha256":src["outcome_hash"],
        "heldout_outcome_sha256":target["outcome_hash"],
        "source_transition_sha256":src["transition_sha256"],
        "heldout_transition_sha256":target["transition_sha256"],
        "conflict_transition_sha256":extra["transition_sha256"] if extra else None,
        "hidden_conflict_observed_prenatally":bool(extra),
        "naive_predicted":naive_prediction is not None,
        "naive_correct":naive_prediction==target["outcome_hash"] if naive_prediction else None,
        "conflict_model_predicted":safe_prediction is not None,
        "conflict_model_correct":safe_prediction==target["outcome_hash"] if safe_prediction else None,
        "physically_observed_consequence":target["outcome"],
        "physical_transitions_applied":len(_PHYSICAL_RECEIPTS),
        "physical_transition_receipts":list(_PHYSICAL_RECEIPTS),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=False)
    base=build_stage11_reference_runtime().world.config
    rows=[]
    for family in FAMILIES:
        for seed in SEEDS:
            result=run_pair(base,family,seed)
            rows.append(result)
            (args.output_dir/f"{family}-{seed}.json").write_text(
                json.dumps(result,indent=2,sort_keys=True)+"\n")
    by_family={}
    for family in FAMILIES:
        subset=[row for row in rows if row["family"]==family]
        by_family[family]={
            "count":len(subset),
            "exact_baseline_covered":sum(x["full_key_covered"] for x in subset),
            "naive_covered":sum(x["naive_predicted"] for x in subset),
            "naive_correct":sum(x["naive_correct"] is True for x in subset),
            "naive_wrong":sum(x["naive_correct"] is False for x in subset),
            "conservative_covered":sum(x["conflict_model_predicted"] for x in subset),
            "conservative_wrong":sum(x["conflict_model_correct"] is False for x in subset)}
    summary={
        "schema":"a214-offline-relative-conflict-abstention-v1",
        "code_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        "seeds":list(SEEDS),"families":list(FAMILIES),
        "heldout_pairs":len(rows),"source_and_test_worlds":len(rows)*2,
        "additional_contradictory_training_worlds":len(HIDDEN)*len(SEEDS),
        "total_physical_worlds":len(rows)*2+len(HIDDEN)*len(SEEDS),
        "total_physical_transitions":sum(x["physical_transitions_applied"] for x in rows),
        "unregistered_world_receipts":sum(r["role"]=="unregistered" for x in rows
                                          for r in x["physical_transition_receipts"]),
        "family_results":by_family,
        "stage12_science_verdict":"PARTIAL","operator_accepted":False,
        "normative_modified":False,"cognitive_code_modified":False}
    (args.output_dir/"a214-summary.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("A214_SUMMARY "+json.dumps(summary,sort_keys=True),flush=True)
    return 0 if (len(rows)==80 and summary["total_physical_transitions"]==272
                 and summary["unregistered_world_receipts"]==0
                 and sum(by_family[x]["conservative_covered"] for x in TRANSLATED)==32
                 and sum(by_family[x]["naive_wrong"] for x in HIDDEN)==16
                 and sum(by_family[x]["conservative_covered"] for x in HIDDEN)==0
                 and sum(by_family[x]["conservative_covered"] for x in VISIBLE)==0
                 ) else 2

if __name__=="__main__":
    raise SystemExit(main())
