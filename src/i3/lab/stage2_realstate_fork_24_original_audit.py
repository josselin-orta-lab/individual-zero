"""Independent read-only integrity/reduction audit of 96 new content lives.

Requires archived original files from the exact evidence commit. No imports
of I3 cognition, World, generator, or admission; no births or regeneration.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from math import fsum, isclose, isfinite
from pathlib import Path
import gzip
import json
import sys

SCHEMA="i3-stage2-1-realstate-fork-24-read-only-original-audit/v1"
SOURCE="24531b8a5033a2be1b738dd30734fac2f50a3a8b"
FINGERPRINT="097da962b6c28b80f0142ed2226a6c7f8d2214ae1b071d67159a48cbf73cf0a2"
PLAN_SHA="b545888f4485cfd8ef8ded6c6a9abab91e6aea5a1a808499ed5d7b0400db0350"
WITNESS_SHA="669af6b56e4dd055bad08d8c38f58de90d8e51a33a7cb8d6a861e078b1df21dd"
MANIFEST_SHA="dddf6d3de5f2caadbdd684941bc8155a1333f428a032ce34b8dc65b7109aa753"
POLICIES=("p13_replay_gate_v1","p13_replay_gate_random_content_v1")
FAMILIES=("stable","depletion","pulse")
IDENTITY=("pair_id","index","cohort","family","policy",
          "world_seed","genome_seed","life_seed")
PAIRS=24
HORIZON=400


def _hash(data):
    return sha256(data).hexdigest()


def _canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),
                      allow_nan=False).encode()


def _require(ok,message):
    if not ok:
        raise ValueError(message)


def _eq(a,b):
    return (type(a) in (float,int) and type(b) in (float,int)
            and isfinite(a) and isfinite(b)
            and isclose(a,b,rel_tol=1e-12,abs_tol=1e-8))


def _same_tree(a,b,prefix=""):
    _require(type(a) is dict and type(b) is dict and set(a)==set(b),
             "summary keys mismatch "+prefix)
    for key,value in a.items():
        actual=b[key]
        if isinstance(value,dict):
            _same_tree(value,actual,prefix+"."+key)
        elif type(value) in (int,float) and type(actual) in (int,float):
            _require(_eq(value,actual),"summary mismatch "+prefix+"."+key)
        else:
            _require(value==actual,"summary mismatch "+prefix+"."+key)


def _verify_one(identity,life,row):
    m=life["manifest"]
    r=life["admission_receipt"]
    a=life["cognitive_accounting"]
    _require(identity["cohort"]=="development" and
             identity["policy"] in POLICIES,"unknown cohort/policy")
    _require(all(row.get(k)==identity[k] for k in IDENTITY),
             "reduced assigned identity changed")
    _require(r["cohort"]=="development" and
             r["index"]==identity["index"] and
             r["family"]==identity["family"] and
             r["world_seed"]==identity["world_seed"] and
             r["world_sha256"]==m["world_sha256"] and
             r["world_name"]==life["world"] and
             r["transport_fingerprint"]==FINGERPRINT,
             "untrusted World/source ticket")
    _require(m["life_seed"]==identity["life_seed"] and
             m["experimental_policy"]["name"]==identity["policy"],
             "actual executed policy or seed mismatch")
    _require(a["status"]=="SETTLED_FOR_DECLARED_WORK" and
             a["shortfall_steps"]==0 and
             a["totals"]["energy"]["unpaid"]<=1e-12 and
             a["totals"]["vigilance"]["unpaid"]<=1e-12,
             "unpaid cognitive work in original")
    terminal=life["terminal"]
    steps=life["steps_lived"]
    _require(terminal in ("dead","censored") and
             type(steps) is int and 1<=steps<=HORIZON and
             (terminal!="censored" or steps==HORIZON),
             "incorrect terminal/horizon")
    _require(type(a["replays_executed"]) is int and
             a["replays_executed"]>=0,
             "invalid physically paid replay count")
    random=identity["policy"]==POLICIES[1]
    _require(life["replay_gate"]["mode"]==
             ("gate_random_content" if random else "gate"),
             "count policy changed")
    receipt=None
    if random:
        rc=life["replay_gate"]["random_content"]
        names=("paid_replay_opportunities","selected_replays_paid",
               "lived_sleep_ordinals","distinct_from_priority_subsets")
        _require(all(type(rc[k]) is int and rc[k]>=0 for k in names),
                 "invalid original replay-content receipts")
        opp,paid,sleep,diff=(rc[k] for k in names)
        _require(0<=diff<=opp<=sleep<=life["actions"].get("dormir",0) and
                 opp<=paid<=16*opp and paid==a["replays_executed"] and
                 rc["count_rule"]=="EXACT_ORIGINAL_GATE",
                 "replay-content selection unfinanced or count rule changed")
        receipt={k:rc[k] for k in names}
        fork=life.get("observer_realstate_content_fork")
        _require(type(fork) is dict,"real-state original observer missing")
        first=fork.get("first_fork")
        captured=fork.get("status")=="FIRST_DIFFERING_REPLAY_CAPTURED"
        if captured:
            _require(type(first) is dict and
                     first["schema"]=="i3-stage2.1-realstate-first-content-fork/v1" and
                     type(first["prepaid_replays_in_each_detached_arm"]) is int and
                     first["prepaid_replays_in_each_detached_arm"]>0 and
                     first["world_or_life_clone_created"] is False and
                     first["observer_physical_debit"] is False and
                     type(first["l1_value_difference_between_detached_updates"])
                     in (int,float) and
                     0<=first["l1_value_difference_between_detached_updates"]<float("inf") and
                     set(first["priority_memory_indices"])!=
                     set(first["random_memory_indices"]),
                     "detached first actual replay fork is malformed")
        else:
            _require(first is None and
                     fork.get("status")=="NO_DIFFERING_FUNDED_REPLAY_OBSERVED",
                     "null actual fork omitted or reclassified")
        _require(
            type(fork["prepaid_replay_opportunities_seen"]) is int and
            type(fork["differing_replay_opportunities_seen"]) is int and
            0<=fork["differing_replay_opportunities_seen"]<=
            fork["prepaid_replay_opportunities_seen"]<=opp and
            (not captured or fork["differing_replay_opportunities_seen"]>0),
            "invalid funded-fork chronology")
    else:
        _require("random_content" not in life["replay_gate"] and
                 "observer_realstate_content_fork" not in life,
                 "experimental content or fork leaked to priority arm")
        fork=None
    expected={
        **identity,
        "terminal":terminal,
        "steps_lived":steps,
        "dead_at_horizon":terminal=="dead" and steps==HORIZON,
        "death_causes":life["death_causes"],
        "paid_energy":a["totals"]["energy"]["paid"],
        "paid_vigilance":a["totals"]["vigilance"]["paid"],
        "replays_paid":a["replays_executed"],
        "sleep_steps":life["actions"].get("dormir",0),
        "random_content_receipt":receipt,
        "realstate_fork_receipt":(None if not random else {
            "status":fork["status"],
            "prepaid_replay_opportunities_seen":
                fork["prepaid_replay_opportunities_seen"],
            "differing_replay_opportunities_seen":
                fork["differing_replay_opportunities_seen"],
            "first_fork":fork["first_fork"]}),
        "world_sha256":m["world_sha256"],
        "genome_sha256":_hash(_canonical(m["genome"])),
        "source_sha256":m["source"]["sha256"],
    }
    _require(set(expected)==set(row),"missing/unexpected original reduced columns")
    for key,value in expected.items():
        if key in ("paid_energy","paid_vigilance"):
            _require(_eq(value,row[key]),"paid currency changed in reduction: "+key)
        else:
            _require(value==row[key],"original reduction mismatch: "+key)
    return expected


def _summaries(rows):
    pairs=[]
    for i in range(PAIRS):
        a,b=rows[2*i:2*i+2]
        _require((a["policy"],b["policy"])==POLICIES,
                 "wrong original policy order")
        _require(a["index"]==b["index"]==540000+i and
                 a["pair_id"]==b["pair_id"]==f"fork-dev-{i:06d}" and
                 a["cohort"]==b["cohort"]=="development",
                 "source-scoped pair missing or changed")
        _require(a["family"]==b["family"] and a["family"] in FAMILIES,
                 "family mismatch")
        for key in ("world_seed","genome_seed","life_seed",
                    "world_sha256","genome_sha256","source_sha256"):
            _require(a[key]==b[key],"paired starting source differs: "+key)
        pairs.append((a,b))
    _require(all(len({t[0][k] for t in pairs})==PAIRS for k in
                 ("world_seed","genome_seed","life_seed")),
             "reused World/genome/life seed")
    def arms(blocks,j):
        arm=[t[j] for t in blocks]
        n=len(arm)
        if not n:return {"assigned":0}
        d={
            "assigned":n,
            "survivors":sum(x["terminal"]=="censored" for x in arm),
            "deaths_at_step_400":sum(x["dead_at_horizon"] for x in arm),
            "mean_lived_steps":fsum(x["steps_lived"] for x in arm)/n,
            "mean_energy_paid":fsum(x["paid_energy"] for x in arm)/n,
            "mean_vigilance_paid":fsum(x["paid_vigilance"] for x in arm)/n,
            "mean_replays_paid":fsum(x["replays_paid"] for x in arm)/n,
            "mean_sleep_steps":fsum(x["sleep_steps"] for x in arm)/n}
        if j:
            d["random_content_distinct_subsets"]=sum(
                x["random_content_receipt"]["distinct_from_priority_subsets"]
                for x in arm)
            d["random_content_replay_opportunities"]=sum(
                x["random_content_receipt"]["paid_replay_opportunities"]
                for x in arm)
        return d
    def paired(blocks):
        n=len(blocks)
        if not n:return {"assigned_pairs":0}
        a=[x[0] for x in blocks]
        b=[x[1] for x in blocks]
        aa=[x["terminal"]=="censored" for x in a]
        bb=[x["terminal"]=="censored" for x in b]
        plus=sum(x and not y for x,y in zip(aa,bb))
        minus=sum(y and not x for x,y in zip(aa,bb))
        return {
            "assigned_pairs":n,
            "both_survive":sum(x and y for x,y in zip(aa,bb)),
            "priority_only_survives":plus,
            "random_content_only_survives":minus,
            "neither_survives":sum(not x and not y for x,y in zip(aa,bb)),
            "paired_risk_difference_priority_minus_random":(plus-minus)/n,
            "mean_lived_step_difference_priority_minus_random":
                fsum(x["steps_lived"]-y["steps_lived"] for x,y in zip(a,b))/n,
            "priority_longer":sum(x["steps_lived"]>y["steps_lived"] for x,y in zip(a,b)),
            "random_longer":sum(x["steps_lived"]<y["steps_lived"] for x,y in zip(a,b))}
    recorded=[b["realstate_fork_receipt"]["first_fork"] for a,b in pairs]
    first=[r for r in recorded if r is not None]
    positives=sum(
        r["l1_value_difference_between_detached_updates"]>1e-12
        for r in first)
    mechanism={
        "assigned_pairs":PAIRS,"first_fork_captured":len(first),
        "first_fork_absent":PAIRS-len(first),
        "positive_learned_value_difference":positives,
        "zero_learned_value_difference":len(first)-positives,
        "primary_fraction_per_assigned_pair":positives/PAIRS,
        "sum_first_fork_L1":fsum(
            r["l1_value_difference_between_detached_updates"] for r in first),
        "all_assigned_included":True,"observer_external_only":True,
        "no_second_world":True,"biological_mediation_claim":False,
        "by_family":{name:{
            "assigned":sum(a["family"]==name for a,b in pairs),
            "captured":sum(a["family"]==name and
                           b["realstate_fork_receipt"]["first_fork"] is not None
                           for a,b in pairs),
            "positive":sum(a["family"]==name and
                           b["realstate_fork_receipt"]["first_fork"] is not None and
                           b["realstate_fork_receipt"]["first_fork"]
                           ["l1_value_difference_between_detached_updates"]>1e-12
                           for a,b in pairs)}
            for name in FAMILIES}}
    return {
        "mechanism":mechanism,
        "overall":paired(pairs),
        "by_arm":{p:arms(pairs,j) for j,p in enumerate(POLICIES)},
        "by_family":{
            family:{"paired":paired([t for t in pairs if t[0]["family"]==family]),
                    "by_arm":{p:arms([t for t in pairs if t[0]["family"]==family],j)
                              for j,p in enumerate(POLICIES)}}
            for family in FAMILIES}}


def audit(path):
    root=Path(path).resolve()
    lock=json.loads((root/"SOURCE_LOCK.json").read_bytes())
    report=json.loads((root/"EXECUTION_REPORT.json").read_bytes())
    rows=json.loads((root/"REDUCED_ROWS.json").read_bytes())
    originals=root/"originals"
    manifest_bytes=(originals/"MANIFEST.json").read_bytes()
    digest=(originals/"MANIFEST.sha256").read_text().strip()
    _require(_hash(manifest_bytes)==digest==MANIFEST_SHA,
             "manifest SHA differs from pinned original")
    manifest=json.loads(manifest_bytes)
    _require(lock["status"]=="CONSUMED_BEFORE_FIRST_BIRTH" and
             lock["source_sha"]==report["source_sha"]==SOURCE and
             lock["source_fingerprint"]==report["source_fingerprint"]==FINGERPRINT
             and lock["plan_sha256"]==report["plan_sha256"]==PLAN_SHA and
             lock["witness_sha256"]==WITNESS_SHA and
             lock["pairs"]==PAIRS and lock["lives"]==2*PAIRS and
             lock["no_retry"] is True and
             lock["confirmatory_science_authorized"] is False,
             "untrusted source/plan/claim original")
    _require(report["status"]=="COMPLETE_EXPLORATORY_DEVELOPMENT_ONLY"
             and report["phase_G"]=="GENERATED" and report["phase_R"]=="COMPLETE"
             and report["planned"]==report["generated"]==report["reduced"]==2*PAIRS
             and report["scientific_verdict"]=="NOT_ISSUED",
             "incomplete original G/R or scientific promotion")
    _require(manifest["status"]=="GENERATED" and
             manifest["planned"]==manifest["generated"]==2*PAIRS and
             len(manifest["files"])==2*PAIRS and manifest["failure"] is None,
             "originals incomplete")
    _require(isinstance(rows,list) and len(rows)==2*PAIRS,
             "reduced original rows missing")
    names={f"life-{i:03d}.json.gz" for i in range(2*PAIRS)}
    _require({p.name for p in originals.glob("life-*.json.gz")}==names and
             {x["file"] for x in manifest["files"]}==names,
             "unexpected original file names")
    original_rows=[]
    for i,entry in enumerate(manifest["files"]):
        _require(entry["file"]==f"life-{i:03d}.json.gz",
                 "original order modified")
        packed=(originals/entry["file"]).read_bytes()
        _require(_hash(packed)==entry["sha256"],"packed SHA mismatch")
        raw=gzip.decompress(packed)
        _require(_hash(raw)==entry["uncompressed_sha256"],"unpacked SHA mismatch")
        obj=json.loads(raw)
        _require(obj["identity"]==entry["identity"],
                 "manifest identity changed")
        original_rows.append(_verify_one(obj["identity"],obj["life"],rows[i]))
    observed=_summaries(original_rows)
    published=report["analysis"]
    _require(published["primary"]==
             "FIRST_REALSTATE_DIFFERENT_CONTENT_DETACHED_TD_L1_PER_24_ASSIGNED" and
             published["scientific_verdict"]=="NOT_ISSUED" and
             published["independent_iid_ecology_attested"] is False and
             published["causal_fixed_replay_count_claim"] is False and
             published["scientific_go"] is False and
             published["noninferiority_margin_approved"] is False and
             published["selection_validation_reserve_executed"] is False,
             "posthoc claim invented")
    _same_tree(observed,
               {k:published[k] for k in
                ("mechanism","overall","by_arm","by_family")})
    _require(observed["mechanism"]["assigned_pairs"]==24 and
             observed["mechanism"]["first_fork_captured"]==17 and
             observed["mechanism"]["first_fork_absent"]==7 and
             observed["mechanism"]["positive_learned_value_difference"]==17 and
             observed["mechanism"]["zero_learned_value_difference"]==0,
             "original first same-state TD learning contrast changed")
    _require(observed["overall"]["both_survive"]==8 and
             observed["overall"]["priority_only_survives"]==0 and
             observed["overall"]["random_content_only_survives"]==2 and
             observed["overall"]["neither_survives"]==14,
             "historical secondary finite outcomes changed")
    _require(observed["by_arm"][POLICIES[0]]["survivors"]==8 and
             observed["by_arm"][POLICIES[1]]["survivors"]==10,
             "original finite secondary survival count changed")
    return {
        "schema":SCHEMA,
        "status":"READ_ONLY_ALL_ORIGINALS_AND_REDUCTIONS_PASS",
        "source":SOURCE,"source_fingerprint":FINGERPRINT,
        "manifest_sha256":MANIFEST_SHA,
        "packed_sha_verified":len(original_rows),
        "unpacked_sha_verified":len(original_rows),
        "complete_matched_pairs":PAIRS,
        "primary":observed["mechanism"],
        "secondary_survival":observed["overall"],
        "all_families":{family:observed["by_family"][family]["paired"]
                        for family in FAMILIES},
        "per_assigned_life":observed["by_arm"],
        "no_new_World_or_life":True,
        "iid_attested":False,"scientific_go":False,
    }


def main(argv=None):
    argv=sys.argv if argv is None else argv
    if len(argv)!=2:
        raise SystemExit("usage: python -m i3.lab.stage2_content_48_original_audit EVIDENCE_ROOT")
    print(json.dumps(audit(argv[1]),sort_keys=True,indent=2))


if __name__=="__main__":
    main()
