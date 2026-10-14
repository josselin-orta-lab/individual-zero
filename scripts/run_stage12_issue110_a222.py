"""A2.22 real os._exit crash matrix for a lab-only SQLite perception custodian."""
from __future__ import annotations
import argparse
from dataclasses import asdict, replace
from hashlib import sha256
import json
import os
from pathlib import Path
import random
import sqlite3
import subprocess
import sys
import tempfile

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.stage12_goal_agency import GoalAgencyService
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import Position, WorldBody, WorldLayout

SEEDS = range(131, 135)
POINTS = ("pre_intent", "after_intent", "after_premature_candidate",
          "before_seal_commit", "after_seal_commit", "after_ack")

def h(x):
    return sha256_hex(canonical_causal_bytes(x))

def capture(w, t):
    return SymbolicPerception().capture(
        local_state=w.capture_local(t_monde=t).as_dict(), telemetry=w.telemetry())

def physical(config, seed, cause, follow):
    rng = random.Random(seed * 991)
    start = Position(rng.randint(5, 17), rng.randint(5, 17))
    target = start.moved("east")
    w = WorldBody(config=replace(config, initial_position=start),
                  layout=WorldLayout(water_sources=frozenset({target})))
    initial = capture(w, 1)
    move = PrimitiveCommand("se_deplacer", {"direction": "east"})
    owner = GoalAgencyService()
    opaque = h(["a222-opaque", seed, cause, follow])
    owner.preregister(assessment_ref="assessment:"+opaque,
        intent_ref="intent:"+opaque, life_id="life:"+opaque,
        goal_ref="goal:water", option_ref="option:move",
        command_hash=h(move.as_dict()), world_step=1, measure="spatial_distance",
        command=move, capture=initial, spatial_target=(target.x,target.y,"water"))
    if cause == "confounded":
        w.apply_scenario_event("set_action_failure_schedule",
                               {"primitive":"se_deplacer","schedule":[True]})
    a = w.apply(move, t_monde=1)
    if cause == "confounded":
        assert a.effects.get("scenario_forced_failure") == "se_deplacer"
        w.apply_scenario_event("set_position", {"position":target.as_dict()})
    else:
        assert a.effects.get("movement") == "moved"
    middle = capture(w, 2)
    judged = owner.evaluate(capture=middle,world_step=2,
                            cue_ref="percept:"+opaque+":2",paid=True)
    assert judged and judged.subjective_agency == "self"
    wait = PrimitiveCommand("attendre", {})
    b = w.apply(wait,t_monde=2)
    assert b.effects.get("rest") == "attendre"
    if follow == "passive":
        w.apply_scenario_event("set_position",
                               {"position":w.position.moved("east").as_dict()})
    final = capture(w, 3)
    payload = {"life_ref":judged.life_id,
               "captures":[asdict(initial),asdict(middle),asdict(final)],
               "original":judged.as_dict()}
    return payload, [a.as_dict(),b.as_dict()]

def connect(path):
    db = sqlite3.connect(str(path),timeout=8,isolation_level=None)
    assert db.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower()=="wal"
    db.execute("PRAGMA synchronous=FULL")
    assert db.execute("PRAGMA synchronous").fetchone()[0]==2
    return db

def child(dbpath, candidate_path, point, srcpath):
    payload = json.loads(Path(srcpath).read_text())
    db=connect(dbpath)
    db.execute("CREATE TABLE custody(id INTEGER PRIMARY KEY CHECK(id=1), status TEXT NOT NULL, content TEXT, digest TEXT)")
    db.execute("INSERT INTO custody(id,status) VALUES(1,'fresh')")
    if point=="pre_intent":os._exit(76)
    db.execute("UPDATE custody SET status='pending' WHERE id=1")
    if point=="after_intent":os._exit(76)
    if point=="after_premature_candidate":
        with open(candidate_path,"w") as f:
            json.dump(payload,f,sort_keys=True)
            f.flush();os.fsync(f.fileno())
        os._exit(76)
    db.execute("BEGIN IMMEDIATE")
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"))
    db.execute("UPDATE custody SET status='sealed',content=?,digest=? WHERE id=1",
               (raw,sha256(raw.encode()).hexdigest()))
    if point=="before_seal_commit":os._exit(76)
    db.execute("COMMIT")
    if point=="after_seal_commit":os._exit(76)
    with open(candidate_path,"w") as f:
        json.dump(payload,f,sort_keys=True)
        f.flush();os.fsync(f.fileno())
    os._exit(76)

def cold(dbpath,candidate_path,expected_life):
    db=sqlite3.connect("file:"+str(dbpath)+"?mode=ro",uri=True)
    try:
        status,raw,digest=db.execute(
            "SELECT status,content,digest FROM custody WHERE id=1").fetchone()
    finally:db.close()
    exists=Path(candidate_path).is_file()
    authorized=False
    if status=="sealed" and exists:
        if sha256(raw.encode()).hexdigest()!=digest:
            raise AssertionError("corrupt sealed source")
        sealed=json.loads(raw)
        candidate=json.loads(Path(candidate_path).read_text())
        authorized=sealed==candidate and candidate["life_ref"]==expected_life
    return {"status":status,"candidate_exists":exists,"authorized":authorized}

def invoke_cold(dbpath,candidate_path,life):
    done=subprocess.run([sys.executable,__file__,"--cold",str(dbpath),
                         str(candidate_path),life],capture_output=True,text=True,timeout=25)
    if done.returncode:
        raise RuntimeError(done.stderr)
    return json.loads(done.stdout)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path)
    ap.add_argument("--child",nargs=4,metavar=("DB","CANDIDATE","POINT","SOURCE"))
    ap.add_argument("--cold",nargs=3,metavar=("DB","CANDIDATE","LIFE"))
    arg=ap.parse_args()
    if arg.child:
        child(*arg.child)
        return
    if arg.cold:
        print(json.dumps(cold(*arg.cold),sort_keys=True))
        return
    assert arg.output_dir
    arg.output_dir.mkdir(parents=True,exist_ok=False)
    config=build_stage11_reference_runtime().world.config
    counts={"fresh":0,"pending":0,"sealed":0,"authorized":0,
            "premature_refused":0,"candidate_corrupt_refused":0,"preseal_forgery_accepted":0}
    transitions=0;worlds=0
    paths={}
    for seed in SEEDS:
        for follow in ("stay","passive"):
            for cause in ("normal","confounded"):
                # One physical world per failure boundary, never replaying a dead I0.
                for point in POINTS:
                    payload,effects=physical(config,seed,cause,follow)
                    worlds+=1;transitions+=len(effects)
                    path=arg.output_dir/f"{seed}-{follow}-{cause}-{point}"
                    path.mkdir()
                    db=path/"custodian.sqlite"
                    cand=path/"candidate.json"
                    source=path/"percepts.json"
                    source.write_text(json.dumps(payload,sort_keys=True))
                    proc=subprocess.run([sys.executable,__file__,"--child",
                        str(db),str(cand),point,str(source)],
                        capture_output=True,text=True,timeout=25)
                    assert proc.returncode==76,(point,proc.returncode,proc.stderr)
                    audit=invoke_cold(db,cand,payload["life_ref"])
                    expected=("fresh" if point=="pre_intent" else
                              "pending" if point in ("after_intent",
                              "after_premature_candidate","before_seal_commit")
                              else "sealed")
                    assert audit["status"]==expected,(point,audit)
                    assert audit["authorized"]==(point=="after_ack"),(point,audit)
                    counts[expected]+=1
                    counts["authorized"]+=int(audit["authorized"])
                    if point=="after_premature_candidate":
                        assert audit["candidate_exists"]
                        counts["premature_refused"]+=1
                    if point=="after_ack":
                        changed=json.loads(cand.read_text())
                        changed["captures"][2]["x"]+=1
                        cand.write_text(json.dumps(changed,sort_keys=True))
                        assert not invoke_cold(db,cand,payload["life_ref"])["authorized"]
                        counts["candidate_corrupt_refused"]+=1
                    (path/"verdict.json").write_text(json.dumps(
                        {"crash":point,"status":audit["status"],
                         "authorized":audit["authorized"],
                         "physical_effect_sha":[h(e) for e in effects]},sort_keys=True))
                    if seed==131 and cause=="normal" and point=="after_ack":
                        paths[follow]=payload
    # Four explicitly untrusted preseal inputs, never counted as physical worlds.
    original=paths["stay"]
    for n in range(4):
        forged=json.loads(json.dumps(original))
        forged["captures"][2]["x"]+=n+1
        path=arg.output_dir/f"forged-preseal-{n}"
        path.mkdir()
        src=path/"source.json";src.write_text(json.dumps(forged))
        db=path/"custodian.sqlite";cand=path/"candidate.json"
        proc=subprocess.run([sys.executable,__file__,"--child",
            str(db),str(cand),"after_ack",str(src)],
            capture_output=True,text=True,timeout=25)
        assert proc.returncode==76,proc.stderr
        assert invoke_cold(db,cand,forged["life_ref"])["authorized"]
        assert forged["captures"]!=original["captures"]
        counts["preseal_forgery_accepted"]+=1
    assert (worlds,transitions)==(96,192)
    assert counts=={"fresh":16,"pending":48,"sealed":32,"authorized":16,
                    "premature_refused":16,"candidate_corrupt_refused":16,
                    "preseal_forgery_accepted":4},counts
    summary={"schema":"a222-crash-custody-v1",
             "code_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
             "worlds":worlds,"real_physical_transitions":transitions,
             "hard_process_exits":worlds+4,"cold_process_audits":worlds+16+4,
             "seeds":list(SEEDS),**counts,"stage12":"PARTIAL",
             "production_cognition_changed":False,"ga06_pairs":0,"autonomous_lives":0}
    (arg.output_dir/"a222-summary.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print("A222_SUMMARY "+json.dumps(summary,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
