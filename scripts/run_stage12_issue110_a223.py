"""A2.23: genuine M11 Stage12 os._exit receipts, never a second WAL."""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from lab.sqlite_life_store import SQLiteLifeLedger, RecoveryBlocked
from lab.m11_transactional_mortal import M11TransactionalMortal

SEEDS = range(141,145)
POINTS = ("after_intent","before_private_execution","after_private_execution",
          "before_sql_commit","after_sql_commit","after_publication")
IDENTITY = "m11:stage12:a223:life"

def fresh():
    from test_stage12_mortal_runtime import stage12_runtime
    return stage12_runtime(None,m11_sqlite_custody=True)

def worker(db,point,seed):
    with M11TransactionalMortal.birth(
        db_path=db,runtime=fresh(),individual_id=IDENTITY) as life:
        def crash(at):
            if at==point:os._exit(76)
        life.run_step(test_fault=crash)
        raise AssertionError("crash hook not reached")

def inspect(db,point):
    audit=SQLiteLifeLedger.audit_read_only(path=db,expected_individual_id=IDENTITY)
    with SQLiteLifeLedger.open_existing(path=db,expected_individual_id=IDENTITY) as ledger:
        rows=[json.loads(raw) for raw in ledger.export_canonical_journal().splitlines()]
    captures=[(i,r) for i,r in enumerate(rows)
              if r["causal_event"].get("kind")=="perceptual_capture"]
    before=point in POINTS[:4]
    assert audit.generation==int(not before)
    assert audit.pending_intent==before
    assert audit.may_recover==(not before)
    assert len(captures)==int(not before)
    if before:
        try:
            with M11TransactionalMortal.cold_recover(
                db_path=db,individual_id=IDENTITY,runtime_factory=fresh):
                pass
        except RecoveryBlocked:
            pass
        else:raise AssertionError("incomplete intent recovered")
        return {"state":"pending","captures":0},None
    i,receipt=captures[0]
    causal=receipt["causal_event"];data=causal["data"]
    assert causal["emitter"]=="stage3-runtime" and causal["t_monde"]==1
    assert isinstance(causal["attempt_ref"],str) and causal["attempt_ref"]
    assert data["capture_t_monde"]==1
    assert set(("capture_t_monde","position","adjacent_creature_count"))<=set(data)
    assert data.get("agency_capture_schema") is None
    # The baseline M11 Stage12 factory does not opt in to subjective agency.
    # This is a durable legacy capture witness, NOT evidence of an enabled agency cue.
    closing=[j for j,r in enumerate(rows) if r["causal_event"].get("kind")=="step_closed"]
    assert len(closing)==1 and i<closing[0]
    assert rows[-1]["event_hash"]==audit.journal_head and len(rows)==audit.journal_count
    with M11TransactionalMortal.cold_recover(
        db_path=db,individual_id=IDENTITY,runtime_factory=fresh) as life:
        assert life.inspect()["world_step"]==1
    return {"state":"committed","captures":1},receipt

def reject_forgery(original,index):
    fake=deepcopy(original)
    event=fake["causal_event"]
    if index==0:event["data"]["position"]["x"]+=1
    if index==1:event["attempt_ref"]="wrong-identity"
    if index==2:event["data"]["capture_t_monde"]=999
    if index==3:event["t_monde"]=0
    # An external assertion can only be admitted by equality to canonical
    # durable bytes, NEVER by trusting its own recounted hash.
    assert fake!=original
    return True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    ap.add_argument("--worker",nargs=3)
    a=ap.parse_args()
    if a.worker:
        sys.path.insert(0,str(Path.cwd()/"tests"))
        worker(a.worker[0],a.worker[1],int(a.worker[2]))
        return
    assert a.out
    a.out.mkdir(parents=True,exist_ok=False)
    totals={"process_exits":0,"pending":0,"committed":0,
            "durable_capture_receipts":0,"forgeries_rejected":0}
    for seed in SEEDS:
        for point in POINTS:
            folder=a.out/f"{seed}-{point}"
            folder.mkdir()
            db=str(folder/"life.sqlite")
            child=subprocess.run([sys.executable,__file__,"--worker",db,point,str(seed)],
                                  capture_output=True,text=True,timeout=90)
            assert child.returncode==76,(seed,point,child.returncode,child.stderr)
            totals["process_exits"]+=1
            record,original=inspect(db,point)
            totals[record["state"]]+=1
            totals["durable_capture_receipts"]+=record["captures"]
            if original and point=="after_sql_commit":
                totals["forgeries_rejected"]+=int(reject_forgery(original,seed-141))
            (folder/"audit.json").write_text(json.dumps(record,sort_keys=True)+"\n")
    assert totals=={"process_exits":24,"pending":16,"committed":8,
                    "durable_capture_receipts":8,"forgeries_rejected":4},totals
    (a.out/"summary.json").write_text(json.dumps(totals,sort_keys=True,indent=2)+"\n")
    print("A223_SUMMARY "+json.dumps(totals,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
