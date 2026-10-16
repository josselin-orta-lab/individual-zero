"""A2.39 read-only post-run integrity audit, executed in a fresh Python process."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

def validate(folder):
    from collections import Counter
    import sys
    from build_i1_fork import generate
    from tempfile import TemporaryDirectory
    folder=folder.resolve()
    manifest=json.loads((folder/"birth-manifest.json").read_text())
    rows=[json.loads(x) for x in (folder/"lives.jsonl").read_text().splitlines()]
    assert len(rows)==len(manifest["births"])==160,"incomplete cohort"
    assert len({x["life_id"] for x in rows})==160,"duplicate births"
    errors=[]
    with TemporaryDirectory() as tmp:
        built=Path(tmp)/"built"
        generate(built)
        sys.path.insert(0,str(built))
        from i1lab.independent_journal_audit import audit_export_bytes
        from i1lab.journal import HashChainedJournal
        for ref,row in zip(manifest["births"],rows):
            lid=ref["life_id"]
            p=folder/lid.replace(":","-")
            try:
                assert all(row[k]==ref[k] for k in ("life_id","ordinal","arm",
                    "stratum","case_index","physics_sha256","layout_sha256_operator_only"))
                assert json.loads((p/"life-result.json").read_text())==row
                canonical=(p/"canonical.jsonl").read_bytes()
                assert sha256(canonical).hexdigest()==row["journal_sha256"]
                journal=audit_export_bytes(canonical,expected_head=row["journal_head"],
                    expected_count=row["journal_entries"])
                wal=HashChainedJournal.audit_durable_wal(str((p/"life.wal").resolve()))
                assert wal["head_hash"]==row["journal_head"]
                assert wal["verified_entries"]==row["journal_entries"]
                assert journal.head_hash==row["journal_head"]
                assert not row["hard_violations"] and not row["failure"] and not row["audit_error"]
                assert len(row["steps"])<=20
                assert not any(s["execution_status"]=="dead" for s in row["steps"][:-1])
                accepted=0
                for s in row["steps"]:
                    for c in s["uc_charges"]:
                        if c.get("accepted") is True:
                            accepted+=int(c["requested_uc"])
                assert accepted==row["uc_accepted"],"UC event mismatch"
                if row["mortality"]=="dead":
                    assert row["steps"][-1]["execution_status"]=="dead"
                if row["h2_commits"]>2: raise AssertionError("H2 cap")
                if row["arm"]=="BASE" and row["uc_h1"]: raise AssertionError("H1 factor")
                if row["arm"]!="FOOD_FIRST_RISK" and row["uc_h2"]: raise AssertionError("H2 factor")
            except Exception as exc:
                errors.append({"life_id":lid,"error":type(exc).__name__+": "+str(exc)[:240]})
    audit={"schema":"i1-a239-separate-auditor-v1",
           "valid":not errors,"complete":len(rows)==160,
           "journal_and_wal_verified":160-len(errors),
           "errors":errors,"source_sha":manifest["source_sha"],
           "note":"Cryptographic/journal integrity does not alone prove physical causality."}
    (folder/"separate-audit.json").write_text(json.dumps(audit,sort_keys=True,indent=2)+"\n")
    return audit

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    a=p.parse_args()
    result=validate(a.input)
    print(json.dumps(result))
    if not result["valid"]:raise SystemExit(1)
if __name__=="__main__":main()
