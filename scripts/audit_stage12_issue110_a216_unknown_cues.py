"""A2.16: independent read-only cue analysis of first-person unknown agency.

Input is immutable canonically audited journal exports, never hidden world truth.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import json

from lab.independent_journal_audit import audit_export_bytes
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs

def analyze_life(file):
    raw=file.read_bytes()
    base=audit_export_bytes(raw)
    anchor={"expected_head":base.head_hash,"expected_count":base.occurrences}
    progress=audit_stage12_goal_progress(raw,**anchor)
    agency=audit_stage12_first_person_agency(raw,**anchor)
    pairs=audit_stage12_attribution_pairs(raw,**anchor)
    events=[dict(row["causal_event"],event_id=row["event_id"])
            for row in (json.loads(x) for x in raw.splitlines())]
    pre={x["data"]["assessment_ref"]:x for x in events
         if x["kind"]=="stage12_goal_agency_precommitted"}
    judgements=[x for x in events if x["kind"]=="stage12_goal_agency_judgement"]
    follow={x["data"]["intent_ref"]:x for x in events
            if x["kind"]=="stage12_goal_progress_followup"}
    records=[]
    seen=set()
    for judgement in judgements:
        d=judgement["data"]
        ref=d["assessment_ref"]
        if ref in seen or ref not in pre:
            raise ValueError("duplicate or missing original subjective agency commitment")
        seen.add(ref)
        old=pre[ref]
        intent=old["data"]["intent_ref"]
        goal=follow.get(intent)
        if (old["t_monde"] >= judgement["t_monde"]
            or d["intent_ref"]!=intent or goal is None
            or goal["data"]["criterion_outcome"] not in ("success","failure")
            or old["data"]["life_id"]!=d["life_id"]
            or (d["subjective_agency"]=="unknown" and not d.get("cue_ref"))):
            raise ValueError("unknown judgement without valid lived cue and followup")
        records.append({
            "observed_step":judgement["t_monde"],
            "judgement":d["subjective_agency"],
            "reason":d["reason"],
            "mechanism":old["data"]["mechanism"],
            "command":old["data"]["action_primitive"],
            "goal_measure":old["data"]["goal_measure"],
            "criterion_outcome":goal["data"]["criterion_outcome"],
            "perceptual_cue_attested":bool(d["cue_ref"]),
            "observation_paid":d["subjective_agency"]!="unavailable",
        })
    if len(pre)!=agency.precommits or len(judgements)!=sum(
        (agency.judgements_self,agency.judgements_world,
         agency.judgements_unknown,agency.unavailable)):
        raise ValueError("first-person audit count mismatch")
    return {"life":file.parent.name,"sha256":sha256(raw).hexdigest(),
            "world_steps":base.world_steps_closed,
            "original_commitments":len(pre),
            "judgements":records,
            "independent_pairs_applied":pairs.applied_pairs}

def analyze(root):
    paths=sorted(root.rglob("canonical.jsonl"))
    if not paths: raise ValueError("no physical journals")
    rows=[analyze_life(x) for x in paths]
    values=[record for row in rows for record in row["judgements"]]
    unknown=[x for x in values if x["judgement"]=="unknown"]
    return {
        "schema":"a216-lived-unknown-cue-audit-v1",
        "lives":rows,"life_count":len(rows),
        "physical_steps":sum(x["world_steps"] for x in rows),
        "unknown_count":len(unknown),
        "known_self_world_count":sum(v["judgement"] in ("self","world") for v in values),
        "unknown_by_reason":dict(sorted(Counter(v["reason"] for v in unknown).items())),
        "unknown_by_mechanism":dict(sorted(Counter(v["mechanism"] for v in unknown).items())),
        "unknown_by_command":dict(sorted(Counter(v["command"] for v in unknown).items())),
        "unknown_by_goal_measure":dict(sorted(Counter(v["goal_measure"] for v in unknown).items())),
        "unknown_by_verified_goal_outcome":dict(sorted(
            Counter(v["criterion_outcome"] for v in unknown).items())),
        "unknown_without_perceptual_cue":sum(not v["perceptual_cue_attested"]
                                              for v in unknown),
        "scientific_stage12_verdict":"PARTIAL","operator_accepted":False,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    d=analyze(args.input_dir)
    args.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("A216_SUMMARY "+json.dumps({k:v for k,v in d.items() if k!="lives"},sort_keys=True))
    if d["life_count"]!=16 or d["physical_steps"]!=672 or d["unknown_count"]!=8 or d["known_self_world_count"]!=14:
        raise SystemExit(2)
if __name__=="__main__":main()
