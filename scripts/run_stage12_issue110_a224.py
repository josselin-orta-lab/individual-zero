"""A2.24 preregistered 20 authentic Stage12 M11 lives; lab-only sensor attacks."""
import argparse
from copy import deepcopy
from dataclasses import asdict, replace
import json
from pathlib import Path
import sys
from unittest.mock import patch

from i0.modules.perception import SymbolicPerception
from lab.world import WorldBody, Position
from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.sqlite_life_store import SQLiteLifeLedger
from lab.determinism import canonical_causal_bytes, sha256_hex

SEEDS={151:(8,8),152:(12,8),153:(16,8),154:(20,8)}
CASES=("honest_base","honest_twin","output_spoof","input_spoof","joint_spoof")

def digest(x):
    return sha256_hex(canonical_causal_bytes(x))

def relocate_local(local):
    return replace(local,position=local.position.moved("east"),
        adjacent=tuple(replace(cell,position=cell.position.moved("east"))
                       for cell in local.adjacent),
        visible_entities=tuple(replace(ent,position=ent.position.moved("east"))
                               for ent in local.visible_entities))

def relocate_capture(capture):
    return replace(capture,x=capture.x+1,
        adjacent=tuple(replace(cell,x=cell.x+1) for cell in capture.adjacent),
        visible_entities=tuple(replace(ent,x=ent.x+1) for ent in capture.visible_entities))

def fresh(seed,case,life_id):
    folder=str(Path(__file__).resolve().parent)
    if folder not in sys.path:sys.path.insert(0,folder)
    from run_stage12_issue110_a223b import fresh as born
    # Each variant fixes its physical location before birth. The imported
    # fixture has a different finite seed domain, so inject and withdraw
    # only this new deterministic case (never alter a living WorldBody).
    from run_stage12_issue110_a223b import SEEDS as POSITIONS
    original=POSITIONS.get(seed)
    x,y=SEEDS[seed]
    POSITIONS[seed]=(x+int(case=="honest_twin"),y)
    try:return born(seed,life_id)
    finally:
        if original is None:del POSITIONS[seed]
        else:POSITIONS[seed]=original

def verify_one(folder,seed,case):
    life_id=f"a224:m11:{seed}:{case}"
    db=str((folder/"life.sqlite").resolve())
    expected=SEEDS[seed][0]+(case=="honest_twin")
    physical_x=expected
    original_local=WorldBody.capture_local
    original_percept=SymbolicPerception.capture
    witness={"raw":None,"source":None,"input":None,"output":None,"telemetry":None}
    def capture_local(self,*args,**kwargs):
        value=original_local(self,*args,**kwargs)
        # Stage3 obtains the physical local input once at step 1.
        if value.t_monde==1 and witness["raw"] is None:
            witness["raw"]=value.as_dict()
        if case in ("input_spoof","joint_spoof"):
            faked=relocate_local(value)
            if value.t_monde==1:
                witness["source"]=(faked if case=="joint_spoof" else value).as_dict()
            return faked
        if value.t_monde==1:
            witness["source"]=value.as_dict()
        return value
    def capture(self,*args,**kwargs):
        result=original_percept(self,*args,**kwargs)
        if kwargs.get("local_state",{}).get("t_monde")==1 and witness["input"] is None:
            witness["input"]=deepcopy(kwargs["local_state"])
            witness["telemetry"]=deepcopy(kwargs["telemetry"])
        if case=="output_spoof":
            result=relocate_capture(result)
        if result.t_monde==1 and witness["output"] is None:
            witness["output"]=asdict(result)
        return result
    with patch.object(WorldBody,"capture_local",capture_local),patch.object(SymbolicPerception,"capture",capture):
        # Temporary class-patching in this one laboratory process never leaks
        # into other processes or alters persistent runtime source code.
        with M11TransactionalMortal.birth(db_path=db,
             runtime=fresh(seed,case,life_id),individual_id=life_id) as life:
            step=life.run_step()
            assert step.generation==1
    assert all(witness[k] is not None for k in ("raw","source","input","output","telemetry"))
    audit=SQLiteLifeLedger.audit_read_only(path=db,expected_individual_id=life_id)
    assert audit.generation==1 and audit.may_recover and not audit.pending_intent
    with SQLiteLifeLedger.open_existing(path=db,expected_individual_id=life_id) as ledger:
        rows=[json.loads(raw) for raw in ledger.export_canonical_journal().splitlines()]
    assert rows and len(rows)==audit.journal_count and rows[-1]["event_hash"]==audit.journal_head
    captures=[(i,r) for i,r in enumerate(rows) if r["causal_event"]["kind"]=="perceptual_capture"]
    closed=[(i,r) for i,r in enumerate(rows) if r["causal_event"]["kind"]=="step_closed"]
    assert len(captures)==len(closed)==1
    i,r=captures[0];j,closure=closed[0]
    event=r["causal_event"];data=event["data"]
    assert i<j and event["attempt_ref"]==closure["causal_event"]["attempt_ref"]
    assert data["agency_capture_schema"]=="stage12-first-person-cue-v1"
    assert len(data["agency_visible_adjacent"])==4
    assert data["position"]=={"x":witness["output"]["x"],"y":witness["output"]["y"]}, (seed,case,data["position"],witness["output"]["x"],witness["output"]["y"],witness["input"])
    assert data["capture_t_monde"]==witness["output"]["t_monde"]==1
    assert data["agency_visible_inventory"]==witness["output"]["inventory"]
    assert all(a["x"]==b["x"] and a["y"]==b["y"] for a,b in zip(
        data["agency_visible_adjacent"],witness["output"]["adjacent"]))
    projection=asdict(original_percept(SymbolicPerception(),
        local_state=witness["input"],telemetry=witness["telemetry"]))
    input_matches_source=witness["input"]==witness["source"]
    output_matches_input=witness["output"]==projection
    truthful=(
        witness["output"]["x"]==physical_x and
        witness["raw"]["position"]["x"]==physical_x and
        witness["output"]["y"]==SEEDS[seed][1]
    )
    assert (output_matches_input,input_matches_source,truthful)=={
        "honest_base":(True,True,True),
        "honest_twin":(True,True,True),
        "output_spoof":(False,True,False),
        "input_spoof":(True,False,False),
        "joint_spoof":(True,True,False),
    }[case]
    return {"seed":seed,"case":case,"physical_x":physical_x,
            "first_person_capture":witness["output"],
            "capture_sha256":digest(witness["output"]),
            "input_matches_source":input_matches_source,
            "output_matches_input":output_matches_input,
            "physically_truthful":truthful,
            "journal_head":audit.journal_head,"journal_count":audit.journal_count,
            "receipt_ref":event["attempt_ref"],"receipt_data":data,
            "raw_source_sha256":digest(witness["raw"]),
            "announced_source_sha256":digest(witness["source"])}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    a.output_dir.mkdir(parents=True,exist_ok=False)
    results=[]
    for seed in SEEDS:
        per_seed={}
        for case in CASES:
            folder=a.output_dir/f"{seed}-{case}"
            folder.mkdir()
            result=verify_one(folder,seed,case)
            per_seed[case]=result
            results.append(result)
            (folder/"audit.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        twin=per_seed["honest_twin"]
        for name in CASES[2:]:
            fake=per_seed[name]
            assert fake["first_person_capture"]==twin["first_person_capture"],(seed,name)
            assert fake["receipt_data"]==twin["receipt_data"],(seed,name)
    total=lambda label:sum(bool(x[label]) for x in results)
    assert len(results)==20
    summary={"schema":"a224-sensory-boundary-v1","physical_lives":20,
        "committed_generations":20,"spatial_variants":list(SEEDS),
        "output_consistent_with_input":total("output_matches_input"),
        "input_consistent_with_announced_source":total("input_matches_source"),
        "physically_truthful":total("physically_truthful"),
        "physically_false_but_dual_checks_pass":sum(
            not r["physically_truthful"] and r["input_matches_source"]
            and r["output_matches_input"] for r in results),
        "indistinguishable_adversarial_pairs":12,
        "autonomous_600_step_lives":0,"ga06_pairs":0,
        "runtime_changed":False,"stage12":"PARTIAL","operator_reception":False}
    assert (summary["output_consistent_with_input"],
            summary["input_consistent_with_announced_source"],
            summary["physically_truthful"],
            summary["physically_false_but_dual_checks_pass"])==(16,16,8,4)
    (a.output_dir/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("A224_SUMMARY "+json.dumps(summary,sort_keys=True),flush=True)
if __name__=="__main__":main()
