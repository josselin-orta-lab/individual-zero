"""A2.11 independent receipt-only Equipment/UC diagnostic; never modifies I0."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

def analyze(root):
    items=[]
    for file in sorted(root.glob("*/canonical.jsonl")):
        raw=file.read_bytes()
        ev=[json.loads(line)["causal_event"] for line in raw.splitlines()]
        plans=[e for e in ev if e["kind"]=="stage6_planning_result"]
        uc=[e for e in ev if e["kind"]=="compute_charge" and
            e.get("data",{}).get("module")=="planning"]
        motives=[e for e in ev if e["kind"]=="stage12_action_motive_attested"]
        evals=[e for e in ev if e["kind"]=="stage8_option_evaluation"]
        transitions=[e for e in ev if e["kind"]=="world_transition_experienced"]
        admissions=Counter(e["data"].get("progressive_search_diagnostic",{}).get("status","not_reported") for e in plans)
        row={
            "life":file.parent.name,
            "journal_sha256":sha256(raw).hexdigest(),
            "planning_statuses":dict(sorted(admissions.items())),
            "planning_uc_accepted":sum(e["data"].get("requested_uc",0) for e in uc if e["data"].get("accepted")),
            "planning_uc_rejected_count":sum(not e["data"].get("accepted") for e in uc),
            "plan_evaluations_unavailable":sum(e.get("data",{}).get("status")=="not_evaluated" for e in evals),
            "goal_motives":sum(bool(e["data"].get("goal_ref")) for e in motives),
            "exploration_motives":sum(e["data"].get("motive_type")=="cible_exploration" for e in motives),
            "confirmed_ingestions":sum(bool(e.get("effects",{}).get("ate")) for e in transitions),
            "complete_input_digest_observable_from_this_receipt":False,
        }
        items.append(row)
    if not items:
        raise ValueError("no independently verified journals")
    return {"schema":"a211-equipment-uc-independent-read-only-v1",
            "lives":items,"count":len(items),
            "total_incomplete_model":sum(x["planning_statuses"].get("incomplete_model",0) for x in items),
            "total_planning_uc_rejections":sum(x["planning_uc_rejected_count"] for x in items),
            "exact_key_coverage":"not_evaluable_from_public_receipts",
            "scientific_verdict":"PARTIAL","operator_accepted":False}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    report=analyze(args.input_dir)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("A211_SUMMARY "+json.dumps({
        k:v for k,v in report.items() if k!="lives"},sort_keys=True))
    if report["count"]!=16:
        raise SystemExit(2)
if __name__=="__main__":main()
