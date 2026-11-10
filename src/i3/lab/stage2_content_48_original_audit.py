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

SCHEMA="i3-stage2-1-content-48-read-only-original-audit/v1"
SOURCE="d7ea5a3be79fc7eb380aa6ce751df42474ab5ed3"
FINGERPRINT="b49a6da06184331fad78ffe536ede733d95ee771ce6e393a5a05b63a512ea840"
PLAN_SHA="7f982390b7a1b9e3b5192971d835f4b3503a1f0add518e3a104eec2712b53b68"
WITNESS_SHA="6e7683b24d6c030c6f854c06da3ed825eeba77691e7ff7cef567f9f8d5cd147f"
MANIFEST_SHA="75d0b29136d6c872fcf379ae76498d02b7c77989c3f3e337dca42098e5d98a36"
POLICIES=("p13_replay_gate_v1","p13_replay_gate_random_content_v1")
FAMILIES=("stable","depletion","pulse")
IDENTITY=("pair_id","index","cohort","family","policy",
          "world_seed","genome_seed","life_seed")
PAIRS=48
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
    else:
        _require("random_content" not in life["replay_gate"],
                 "random-content receipt leaked into historical policy")
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
        _require(a["index"]==b["index"]==480000+i and
                 a["pair_id"]==b["pair_id"]==f"content-dev-{i:06d}" and
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
    return {
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
             "GATE_TD_PRIORITY_MINUS_GATE_RANDOM_CONTENT_HORIZON400" and
             published["scientific_verdict"]=="NOT_ISSUED" and
             published["independent_iid_ecology_attested"] is False and
             published["causal_fixed_replay_count_claim"] is False and
             published["scientific_go"] is False and
             published["noninferiority_margin_approved"] is False and
             published["selection_validation_reserve_executed"] is False,
             "posthoc claim invented")
    _same_tree(observed,
               {k:published[k] for k in ("overall","by_arm","by_family")})
    _require(observed["overall"]["both_survive"]==16 and
             observed["overall"]["priority_only_survives"]==1 and
             observed["overall"]["random_content_only_survives"]==7 and
             observed["overall"]["neither_survives"]==24,
             "full original outcome differs from published finding")
    _require(observed["by_arm"][POLICIES[0]]["survivors"]==17 and
             observed["by_arm"][POLICIES[1]]["survivors"]==23,
             "source-bound survivor count changed")
    return {
        "schema":SCHEMA,
        "status":"READ_ONLY_ALL_ORIGINALS_AND_REDUCTIONS_PASS",
        "source":SOURCE,"source_fingerprint":FINGERPRINT,
        "manifest_sha256":MANIFEST_SHA,
        "packed_sha_verified":len(original_rows),
        "unpacked_sha_verified":len(original_rows),
        "complete_matched_pairs":PAIRS,
        "primary":observed["overall"],
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
