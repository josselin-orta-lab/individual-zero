"""Read-only A2.10b opportunity/equipment audit of genuine sealed life exports.

Never imports a world, oracle, simulator or cognitive owner.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

def audit_folder(root: Path):
    rows=[]
    for path in sorted(root.glob("*/canonical.jsonl")):
        events=[json.loads(line)["causal_event"] for line in path.read_bytes().splitlines()]
        captured={e["t_monde"]:e["data"] for e in events if e["kind"]=="perceptual_capture"}
        witnessed=set()
        stepped=Counter(e["kind"] for e in events)
        result={"life":path.parent.name,"sha256":sha256(path.read_bytes()).hexdigest(),
                "world_steps":stepped["step_closed"],
                "first_local_berry":None,"local_berry_steps":[],
                "berry_st_steps":[],
                "incomplete_model_steps":[],
                "verified_eats":sum(e["kind"]=="world_transition_experienced"
                    and bool(e.get("effects",{}).get("ate")) for e in events)}
        for t,d in sorted(captured.items()):
            origin=d["position"]
            for neighbor in d.get("agency_visible_adjacent",[]):
                if any(r in ("berry_a","berry_b") for r in neighbor["resources"]):
                    if abs(neighbor["x"]-origin["x"])+abs(neighbor["y"]-origin["y"])!=1:
                        raise ValueError("remote berry falsely in local adjacency")
                    for berry in neighbor["resources"]:
                        if berry in ("berry_a","berry_b"):
                            witnessed.add((berry,neighbor["x"],neighbor["y"],t))
                    if t not in result["local_berry_steps"]:
                        result["local_berry_steps"].append(t)
            if result["first_local_berry"] is None and t in result["local_berry_steps"]:
                result["first_local_berry"]=t
        for e in events:
            if e["kind"]=="s_t_published":
                for ref in e["data"].get("competitive_refs",[]):
                    if not ref.startswith("observation:berry_"):
                        continue
                    parts=ref.split(":")
                    if len(parts)!=6:
                        raise ValueError("malformed berry observation reference")
                    berry, x, y, t, cycle=parts[1:]
                    authored=int(t)
                    if (authored > e["t_monde"] or
                        (berry,int(x),int(y),authored) not in witnessed):
                        raise ValueError("S_t berry without prior local perceptual witness")
                    # TTL can retain a genuine earlier observation, but it
                    # does not certify continued resource availability.
                    if e["t_monde"] not in result["berry_st_steps"]:
                        result["berry_st_steps"].append(e["t_monde"])
            if (e["kind"]=="stage6_planning_result" and
                e["data"].get("progressive_search_diagnostic",{}).get("status")=="incomplete_model"):
                if e["t_monde"] not in result["incomplete_model_steps"]:
                    result["incomplete_model_steps"].append(e["t_monde"])
        rows.append(result)
    if not rows: raise ValueError("no real-life journals")
    return {"schema":"a210b-observer-only-v1","total_lives":len(rows),
            "actual_world_steps":sum(x["world_steps"] for x in rows),
            "operator_accepted":False,"scientific_stage12_verdict":"PARTIAL",
            "lives":rows}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    report=audit_folder(args.input_dir)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("A210B_AUDIT "+json.dumps({"lives":report["total_lives"],
           "steps":report["actual_world_steps"],"verdict":"PARTIAL"}),flush=True)
    if report["total_lives"] != 16 or report["actual_world_steps"] != 672:
        raise SystemExit(2)

if __name__=="__main__":main()
