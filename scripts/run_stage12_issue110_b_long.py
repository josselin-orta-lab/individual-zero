"""Prospectively registered born-enabled B long WAL and cold M11 cohorts."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tests"))
from test_stage12_dual_scope_runtime import born
from lab.independent_journal_audit import audit_export_bytes
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_dual_scope_audit import audit_stage12_dual_scope
from lab.journal import HashChainedJournal
from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.sqlite_life_store import SQLiteLifeLedger

def evidence(raw,head,count):
    base=audit_export_bytes(raw,expected_head=head,expected_count=count)
    proximal=audit_stage12_first_person_agency(raw,expected_head=head,expected_count=count)
    dual=audit_stage12_dual_scope(raw,expected_head=head,expected_count=count)
    assert dual.precommits>0 and dual.judgements>0
    rows=[json.loads(line)["causal_event"] for line in raw.splitlines()]
    assert not any(e["kind"] in ("stage12_attribution_pair_admitted",
                   "stage12_attribution_pair_applied") for e in rows)
    assert not any(e["kind"]=="stage12_outcome_responsibility_judgement"
            and e["data"].get("subjective_responsibility") not in
            ("unknown","unavailable") for e in rows)
    return {"world_steps":base.world_steps_closed,
            "dual_precommits":dual.precommits,"dual_judgements":dual.judgements,
            "dual_unavailable":dual.unavailable,"dual_pending":dual.unresolved,
            "journal_head":head,"journal_count":count,
            "journal_export_sha256":sha256(raw).hexdigest()}

def wal_life(folder):
    folder.mkdir()
    path=folder/"individual.wal"
    life=born(path,dual=True,join=False,life_id="stage12:b:l600",m11=False)
    steps=0;status="active"
    for _ in range(600):
        if life.stage3.substrate.mortal_status.value!="active":break
        result=life.run_step()
        if result.execution_status!="applied":break
        steps+=1
    status=life.stage3.substrate.mortal_status.value
    raw=life.journal.canonical_bytes()
    (folder/"canonical.jsonl").write_bytes(raw)
    receipt=HashChainedJournal.audit_durable_wal(str(path))
    assert receipt["verified_entries"]==len(life.journal.entries)
    assert receipt["head_hash"]==life.journal.head_hash
    report=evidence(raw,life.journal.head_hash,len(life.journal.entries))
    report.update({"mode":"born-enabled-wal","executed_steps":steps,"lifecycle":status,
                   "wal_sha256":sha256(path.read_bytes()).hexdigest()})
    (folder/"summary.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    assert steps==600,("incomplete genuine B WAL world",steps,status)
    return report

def m11_life(folder):
    folder.mkdir()
    db=str((folder/"individual.sqlite").resolve())
    ident="stage12:b:m48"
    mk=lambda:born(folder/"unused",dual=True,join=False,life_id=ident,m11=True)
    steps=0;prior_rows=b"";prior_head=""
    with M11TransactionalMortal.birth(db_path=db,runtime=mk(),individual_id=ident) as owner:
        for t in range(1,25):
            x=owner.run_step()
            steps=t
            assert x.generation==t and x.world_step==t and x.status=="active"
    before=SQLiteLifeLedger.audit_read_only(path=db,expected_individual_id=ident)
    assert before.generation==24 and before.may_recover
    with SQLiteLifeLedger.open_existing(path=db,expected_individual_id=ident) as ledger:
        prior_rows=ledger.export_canonical_journal()
    prior_head=before.journal_head
    with M11TransactionalMortal.cold_recover(db_path=db,
            individual_id=ident,runtime_factory=mk) as owner:
        assert owner.inspect()["world_step"]==24
        for t in range(25,49):
            x=owner.run_step()
            steps=t
            assert x.generation==t and x.world_step==t and x.status=="active"
    receipt=SQLiteLifeLedger.audit_read_only(path=db,expected_individual_id=ident)
    assert receipt.generation==48 and not receipt.pending_intent
    with SQLiteLifeLedger.open_existing(path=db,expected_individual_id=ident) as ledger:
        raw=ledger.export_canonical_journal()
    (folder/"canonical.jsonl").write_bytes(raw+b"\n")
    assert raw.startswith(prior_rows)
    old=[json.loads(x) for x in prior_rows.splitlines()]
    new=[json.loads(x) for x in raw.splitlines()]
    assert new[len(old)-1]["event_hash"]==prior_head
    report=evidence(raw,receipt.journal_head,receipt.journal_count)
    report.update({"mode":"born-enabled-m11","executed_steps":steps,
                   "cold_recovered_after_generation":24,
                   "first_half_head":prior_head,
                   "second_half_head":receipt.journal_head,
                   "lifecycle":receipt.status})
    (folder/"summary.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    assert steps==48,("incomplete genuine B M11 world",steps)
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--mode",choices=("wal","m11"),required=True)
    a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=False)
    try:
        report=wal_life(a.output_dir/"wal") if a.mode=="wal" else m11_life(a.output_dir/"m11")
        report.update({"source_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
                      "operator_accepted":False,"scientific_validation_claimed":False})
        (a.output_dir/"result.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
        print("B_LONG_SUMMARY "+json.dumps(report,sort_keys=True),flush=True)
    except BaseException as exc:
        (a.output_dir/"failure.json").write_text(json.dumps(
            {"type":type(exc).__name__,"detail":str(exc)},sort_keys=True)+"\n")
        raise
if __name__=="__main__":main()
