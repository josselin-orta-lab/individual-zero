"""A2.23b: born-enabled subjective agency, real M11 crashes and cold continuation."""
import argparse
from copy import deepcopy
from dataclasses import replace
import json
import os
from pathlib import Path
import subprocess
import sys

from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.sqlite_life_store import SQLiteLifeLedger, RecoveryBlocked
from lab.world import Position

SEEDS = {141:(8,8),142:(12,8),143:(16,8),144:(20,8)}
POINTS = ("after_intent","before_private_execution","after_private_execution",
          "before_sql_commit","after_sql_commit","after_publication")

def fresh(seed, individual):
    path=str(Path(__file__).resolve().parents[1]/"tests")
    if path not in sys.path:sys.path.insert(0,path)
    from test_stage12_mortal_runtime import stage12_runtime
    from lab.world import WorldLayout
    from lab.stage12_runtime import Stage12Runtime
    from lab.stage11_reference_fixture import build_stage11_reference_runtime
    from lab.stage10_reference_fixture import build_stage10_reference_runtime
    from i0.modules.stage12_detectors import Stage12DetectionPolicy
    s11=build_stage11_reference_runtime(autonomous_mortal=True)
    s10=build_stage10_reference_runtime(autonomous_mortal=True)
    sleep=replace(s10._stage10_config.sleep,fatigue_gain=0.0,night_weight=0.0,
                  consolidation_weight=0.0)
    combined=replace(s10._stage10_config,stage9=s11._stage11_config.stage9,sleep=sleep)
    pos=Position(*SEEDS[seed])
    world_cfg=replace(s11.world.config,initial_position=pos)
    layout=WorldLayout(water_sources=frozenset({pos.moved("east").moved("east")}))
    # Immutable reference Equipment is fixed before each independent birth.
    equipment=s11.equipment
    return Stage12Runtime(world_config=world_cfg,layout=layout,
        safety_config=s11.stage3.substrate.safety._config,
        safety_facts=s11._canonical_safety._innate,
        protected_integrity_threshold=s11.stage3.control._config.protected_integrity_threshold,
        stage11_config=s11._stage11_config,stage10_config=combined,
        equipment=equipment,wal_path=None,m11_sqlite_custody=True,
        autonomous_mortal=True,birth_life_id=individual,
        subjective_goal_agency=True,goal_agency_cost_uc=1,
        diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
        detector_policy=Stage12DetectionPolicy(
            version="stage12-mortal-live-dev-v1",window=12,
            stagnation_steps=3,stagnation_tolerance=0.05,
            loop_repetitions=2,loop_max_period=2,
            entropy_min_samples=3,entropy_warning_fraction=0.25,
            bias_min_outcomes_each=2,attribution_bias_threshold=0.75))

def identity(seed):
    return f"m11:stage12:a223b:{seed}"

def worker(db,point,seed):
    with M11TransactionalMortal.birth(db_path=db,runtime=fresh(seed,identity(seed)),
                                      individual_id=identity(seed)) as life:
        def kill(at):
            if at==point:os._exit(76)
        life.run_step(test_fault=kill)
        raise AssertionError("hook not reached")

def read(db,seed):
    audit=SQLiteLifeLedger.audit_read_only(path=db,expected_individual_id=identity(seed))
    with SQLiteLifeLedger.open_existing(path=db,expected_individual_id=identity(seed)) as ledger:
        rows=[json.loads(line) for line in ledger.export_canonical_journal().splitlines()]
    return audit,rows

def receipts(rows):
    return [row for row in rows if row["causal_event"].get("kind")=="perceptual_capture"]

def verify(rows,audit,seed,expected):
    captures=receipts(rows)
    assert len(captures)==expected
    assert len(rows)==audit.journal_count
    if rows:assert rows[-1]["event_hash"]==audit.journal_head
    closures=[row for row in rows if row["causal_event"].get("kind")=="step_closed"]
    assert len(closures)==expected
    for step,(rec,closed) in enumerate(zip(captures,closures),1):
        event=rec["causal_event"];data=event["data"]
        assert event["emitter"]=="stage3-runtime"
        assert event["t_monde"]==data["capture_t_monde"]==step
        assert event["attempt_ref"]==closed["causal_event"]["attempt_ref"]
        assert data["agency_capture_schema"]=="stage12-first-person-cue-v1"
        assert len(data["agency_visible_adjacent"])==4
        if step==1:
            assert data["position"]=={"x":SEEDS[seed][0],"y":SEEDS[seed][1]}
        assert "oracle_canary" not in str(data)
        assert rec["index"] < closed["index"]
    return captures

def audit_run(db,point,seed):
    audit,rows=read(db,seed)
    pending=point in POINTS[:4]
    assert audit.generation==(0 if pending else 1)
    assert audit.pending_intent==pending
    assert audit.may_recover!=pending
    verify(rows,audit,seed,0 if pending else 1)
    if pending:
        try:
            with M11TransactionalMortal.cold_recover(
                db_path=db,individual_id=identity(seed),
                runtime_factory=lambda:fresh(seed,identity(seed))):
                pass
        except RecoveryBlocked:pass
        else:raise AssertionError("uncertain life resumed")
        return {"pending":1,"committed":0,"continued":0,"forgeries":0,"identity_refused":0}
    original=receipts(rows)[0]
    forged=0
    for kind in ("position","attempt","world_step","adjacent"):
        fake=deepcopy(original)
        e=fake["causal_event"]
        if kind=="position":e["data"]["position"]["x"]+=1
        if kind=="attempt":e["attempt_ref"]="wrong"
        if kind=="world_step":e["data"]["capture_t_monde"]=99
        if kind=="adjacent":e["data"]["agency_visible_adjacent"][0]["passable"]=not e["data"]["agency_visible_adjacent"][0]["passable"]
        # Compare canonical serialized occurrence, not a fake's rewritten hash.
        from lab.determinism import canonical_causal_bytes
        assert canonical_causal_bytes(fake)!=canonical_causal_bytes(original)
        assert not any(canonical_causal_bytes(fake)==canonical_causal_bytes(x) for x in rows)
        forged+=1
    try:
        with M11TransactionalMortal.cold_recover(
            db_path=db,individual_id=identity(seed),
            runtime_factory=lambda:fresh(seed,"m11:stage12:a223b:wrong")):
            pass
    except RecoveryBlocked:bad_identity=1
    else:raise AssertionError("wrong identity resumed")
    with M11TransactionalMortal.cold_recover(
        db_path=db,individual_id=identity(seed),
        runtime_factory=lambda:fresh(seed,identity(seed))) as life:
        assert life.inspect()["world_step"]==1
        assert life.run_step().generation==2
    new_audit,new_rows=read(db,seed)
    assert new_audit.generation==2
    captures=verify(new_rows,new_audit,seed,2)
    assert captures[0]==original
    return {"pending":0,"committed":1,"continued":1,"forgeries":forged,"identity_refused":bad_identity}

def preseal_worker(db,seed):
    """Deliberate test-only compromised sensory source, never deploy to I0."""
    from unittest.mock import patch
    from dataclasses import replace as dc_replace
    from i0.modules.perception import SymbolicPerception
    original=SymbolicPerception.capture
    def compromised(self,*args,**kwargs):
        lived=original(self,*args,**kwargs)
        return dc_replace(lived,x=lived.x+1)
    with patch.object(SymbolicPerception,"capture",compromised):
        with M11TransactionalMortal.birth(
            db_path=db,runtime=fresh(seed,identity(seed)),
            individual_id=identity(seed)) as life:
            receipt=life.run_step()
            assert receipt.generation==1
    audit,rows=read(db,seed)
    assert audit.generation==1 and audit.may_recover
    raw=receipts(rows)
    assert len(raw)==1
    seen=raw[0]["causal_event"]["data"]["position"]
    assert seen["x"]==SEEDS[seed][0]+1 and seen["y"]==SEEDS[seed][1]
    # An external observer knows that physical initial position was not
    # modified; no Oracle facts or intervention labels enter the cognition.
    print("A223B_PRESEAL_ACCEPTED "+json.dumps({"seed":seed,"physical_initial":SEEDS[seed],"stored_capture":seen}))
    return

def main():
    p=argparse.ArgumentParser();p.add_argument("--output-dir",type=Path)
    p.add_argument("--worker",nargs=3)
    p.add_argument("--preseal",nargs=2)
    args=p.parse_args()
    if args.worker:
        worker(args.worker[0],args.worker[1],int(args.worker[2]));return
    if args.preseal:
        preseal_worker(args.preseal[0],int(args.preseal[1]));return
    args.output_dir.mkdir(parents=True,exist_ok=False)
    counts={"hard_exits":0,"pending":0,"committed":0,"continued":0,"forgeries":0,"identity_refused":0,"preseal_false_captures_committed":0}
    for seed in SEEDS:
        for point in POINTS:
            d=args.output_dir/f"{seed}-{point}";d.mkdir()
            db=str((d/"life.db").resolve())
            cmd=[sys.executable,__file__,"--worker",db,point,str(seed)]
            child=subprocess.run(cmd,capture_output=True,text=True,timeout=100)
            assert child.returncode==76,(seed,point,child.returncode,child.stderr[-2000:])
            counts["hard_exits"]+=1
            result=audit_run(db,point,seed)
            for key,value in result.items():counts[key]+=value
            (d/"audit.json").write_text(json.dumps(result,sort_keys=True)+"\n")
    for seed in SEEDS:
        folder=args.output_dir/f"{seed}-compromised-preseal"
        folder.mkdir()
        db=str((folder/"life.db").resolve())
        child=subprocess.run([sys.executable,__file__,"--preseal",db,str(seed)],capture_output=True,text=True,timeout=100)
        assert child.returncode==0,(seed,child.stderr[-2500:])
        assert "A223B_PRESEAL_ACCEPTED" in child.stdout
        counts["preseal_false_captures_committed"]+=1
        (folder/"verdict.json").write_text(child.stdout)
    assert counts=={"hard_exits":24,"pending":16,"committed":8,
                    "continued":8,"forgeries":32,"identity_refused":8,
                    "preseal_false_captures_committed":4},counts
    summary={"schema":"a223b-born-enabled-m11-v1","spatial_variants":SEEDS,
             "worlds":24,"production_policy_changed":False,"ga06_pairs":0,
             "operator_reception":False,"stage12":"PARTIAL",**counts}
    (args.output_dir/"summary.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print("A223B_SUMMARY "+json.dumps(summary,sort_keys=True),flush=True)
if __name__=="__main__":main()
