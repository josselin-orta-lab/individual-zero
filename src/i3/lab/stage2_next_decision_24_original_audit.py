"""Independent read-only integrity/reduction audit of 48 next decision lives.

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

SCHEMA="i3-stage2-1-next-decision-24-read-only-original-audit/v1"
SOURCE="d86474d4eea47e8066169988c152f24c40f8efb6"
FINGERPRINT="469367d11a7866d715e4a4781b69d815f1f069ed88f2d03b8d457b4beb4852a9"
PLAN_SHA="8b7533a27699684b8d6a00b41f48f00862e1e0a453cc031aedfb9baaf479bd49"
WITNESS_SHA="eeed48c158e29c44fd8d5723b813f1673ae3ddbba719c22e8d9f26a4791f93f4"
MANIFEST_SHA="53fdea10f56994a9171d274ecc6388a3301128503b98c1572052ee4b780196b5"
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
        observer=life.get("observer_next_decision_replay")
        _require(type(observer) is dict and
                 observer.get("schema")==
                 "i3-stage2.1-next-decision-content-fork-observer/v1" and
                 observer.get("external_detached_work_only") is True and
                 observer.get("no_second_world") is True and
                 observer.get("no_survival_mediation_inference") is True and
                 observer.get("no_calibrated_predictive_accuracy_claim") is True,
                 "original next-decision observer missing or mutated")
        event=observer.get("first_fork")
        status=observer.get("status")
        different=status=="FIRST_FORK_AND_NEXT_DECISION_CAPTURED"
        no_next=status=="FIRST_FORK_WITHOUT_SUBSEQUENT_LIVE_DECISION"
        no_fork=status=="NO_DIFFERENT_FUNDED_REPLAY"
        _require(
            (no_fork and event is None) or
            (no_next and type(event) is dict and event.get("next_decision") is None) or
            (different and type(event) is dict and
             type(event.get("next_decision")) is dict and
             event["next_decision"].get(
                 "random_branch_matches_actual_live_decision_and_work") is True),
            "observer lost next-decision or null class")
        _require(type(observer.get("funded_opportunities")) is int and
                 type(observer.get("different_opportunities")) is int and
                 0<=observer["different_opportunities"]<=
                 observer["funded_opportunities"]<=opp and
                 (no_fork or observer["different_opportunities"]>0),
                 "prepaid memory opportunities changed")
        if event is not None:
            _require(type(event.get("replays_in_each_detached_copy")) is int and
                     1<=event["replays_in_each_detached_copy"]<=16 and
                     type(event.get("different_learned_values")) is bool and
                     set(event.get("priority_memory_indices",[]))!=
                     set(event.get("random_memory_indices",[])),
                     "invalid genuine same-count detached replay")
        if different:
            choice=event["next_decision"]
            _require(choice.get("observer_extra_physical_cost") is False and
                     type(choice.get("same_admitted_action_and_param")) is bool and
                     type(choice.get("same_decision_option")) is bool and
                     type(choice.get("priority_work")) is dict and
                     type(choice.get("random_work")) is dict,
                     "detached next decision not physically bound")
            residual=event.get("shared_actual_transition_td_residual")
            _require(residual is None or (
                     choice["same_admitted_action_and_param"] is True and
                     residual.get("same_actual_transition") is True and
                     residual.get("bootstrapped_not_calibrated_prediction") is True and
                     all(type(residual.get(k)) in (int,float) and
                         0<=residual[k]<float("inf")
                         for k in ("priority","random"))),
                     "reported TD score on unobserved alternative action")
        elif event is not None:
            _require(event.get("shared_actual_transition_td_residual") is None,
                     "invented off-horizon residual")
    else:
        _require("random_content" not in life["replay_gate"] and
                 "observer_next_decision_replay" not in life,
                 "content observer leaked to priority control")
        observer=None
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
        "next_decision_receipt":(None if not random else {
            "status":observer["status"],
            "funded_opportunities":observer["funded_opportunities"],
            "different_opportunities":observer["different_opportunities"],
            "first_fork":observer["first_fork"]}),
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
        _require(a["index"]==b["index"]==560000+i and
                 a["pair_id"]==b["pair_id"]==f"next-decision-{i:06d}" and
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
    original_events=[b["next_decision_receipt"]["first_fork"] for a,b in pairs]
    first=[e for e in original_events if e is not None]
    with_next=[e for e in first if e.get("next_decision") is not None]
    different=[e for e in with_next if not
               e["next_decision"]["same_admitted_action_and_param"]]
    same=[e for e in with_next if
          e["next_decision"]["same_admitted_action_and_param"]]
    shared=[e["shared_actual_transition_td_residual"] for e in same
            if e["shared_actual_transition_td_residual"] is not None]
    mechanism={
        "assigned_pairs":PAIRS,
        "first_different_funded_memory_fork":len(first),
        "no_different_funded_memory_fork":PAIRS-len(first),
        "first_fork_without_following_real_decision":len(first)-len(with_next),
        "first_fork_with_next_common_perception":len(with_next),
        "different_next_admitted_action_or_param":len(different),
        "same_next_admitted_action_and_param":len(same),
        "different_next_option":sum(not e["next_decision"]["same_decision_option"]
                                    for e in with_next),
        "primary_fraction_of_all_assigned":len(different)/PAIRS,
        "shared_action_nonterminal_bootstrapped_TD_receipts":len(shared),
        "sum_priority_shared_action_TD_residual":
            fsum(r["priority"] for r in shared),
        "sum_random_shared_action_TD_residual":
            fsum(r["random"] for r in shared),
        "all_assigned_included":True,"observer_external_only":True,
        "no_second_world":True,"calibrated_predictive_accuracy":False,
        "causal_biological_survival_mediation":False,
        "by_family":{fam:{
            "assigned":sum(a["family"]==fam for a,b in pairs),
            "fork":sum(a["family"]==fam and
                       b["next_decision_receipt"]["first_fork"] is not None
                       for a,b in pairs),
            "with_next":sum(a["family"]==fam and
                       b["next_decision_receipt"]["first_fork"] is not None and
                       b["next_decision_receipt"]["first_fork"].get("next_decision")
                       is not None for a,b in pairs),
            "changed_action":sum(a["family"]==fam and
                       b["next_decision_receipt"]["first_fork"] is not None and
                       b["next_decision_receipt"]["first_fork"].get("next_decision")
                       is not None and not
                       b["next_decision_receipt"]["first_fork"]["next_decision"]
                       ["same_admitted_action_and_param"] for a,b in pairs)
        } for fam in FAMILIES}}
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
             lock["scientific_go"] is False,
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
             "FIRST_SAME_NEXT_PERCEPTION_DIFFERENT_HYPOTHETICAL_ACTION_PER_24_ASSIGNED" and
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
             observed["mechanism"]["first_different_funded_memory_fork"]==20 and
             observed["mechanism"]["no_different_funded_memory_fork"]==4 and
             observed["mechanism"]["first_fork_with_next_common_perception"]==20 and
             observed["mechanism"]["first_fork_without_following_real_decision"]==0 and
             observed["mechanism"]["different_next_admitted_action_or_param"]==1 and
             observed["mechanism"]["same_next_admitted_action_and_param"]==19 and
             observed["mechanism"]["shared_action_nonterminal_bootstrapped_TD_receipts"]==19,
             "source first-decision exact mechanistic original evidence changed")
    _require(observed["overall"]["both_survive"]==10 and
             observed["overall"]["priority_only_survives"]==2 and
             observed["overall"]["random_content_only_survives"]==3 and
             observed["overall"]["neither_survives"]==9,
             "paired biological secondary original outcomes changed")
    _require(observed["by_arm"][POLICIES[0]]["survivors"]==12 and
             observed["by_arm"][POLICIES[1]]["survivors"]==13,
             "secondary source survival count changed")
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
