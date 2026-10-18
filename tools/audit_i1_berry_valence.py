#!/usr/bin/env python3
"""Audit physical berry damage and *subjective* TD valence from actual mortal WAL.

Operator-only postmortem reconstruction of the current I1 temperament and
Value/Needs contract; never supplies a prediction or lesson to the individual.
"""
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import json

GOALS = {"energy":50.0,"food":60.0,"water":60.0,"integrity":100.0}
SIGNATURE = "i1:affordance:manger:target=berry_b"
TEMPERAMENT = "i1-life-id-temperament-v1"

def num(value):
    if isinstance(value,dict) and set(value)=={"$f64"}:
        return float.fromhex(value["$f64"])
    if type(value) in (float,int):
        return float(value)
    raise ValueError("unrecognized WAL number")

def birth_integrity_weight(individual_id):
    if not individual_id.startswith("i1:"):
        raise ValueError("unexpected identity")
    h=sha256((TEMPERAMENT+":"+individual_id+":threat_sensitivity").encode()).digest()
    sensitivity=round(2.0*int.from_bytes(h[:8],"big")/(2**64-1)-1.0,6)
    weight=(1.0-0.5*(-sensitivity) if sensitivity<0
            else 1.0+0.8*sensitivity)
    return weight,sensitivity

def deviation(body,weight):
    return sum((weight if k=="integrity" else 1.0)*abs(num(body[k])-goal)
               for k,goal in GOALS.items())

def analyze(folder):
    report=json.loads((folder/"report.json").read_text(encoding="utf-8"))
    if (report.get("status")!="COMPLETED_WITHOUT_SCIENTIFIC_VERDICT"
        or report.get("engine")!="I1" or report["run"]["custody"]!="wal"
        or len(report["lives"])!=1):
        raise ValueError("incomplete mortal I1 WAL")
    life=report["lives"][0];damage=report["run"]["experimental_berry_b_damage"]
    if damage not in (-100.0,-10.0,0.0) or life["effective_berry_b_damage"]!=damage:
        raise ValueError("effective toxicity differs from declared intervention")
    walname=Path(life["custody_file"])
    if walname.is_absolute() or len(walname.parts)!=1:
        raise ValueError("unsafe WAL reference")
    wal=folder/walname
    if wal.is_symlink() or not wal.is_file():
        raise ValueError("missing sealed WAL")
    before={};after={};actions={};proposals=defaultdict(list);updates=defaultdict(list)
    count=0;head=None;closed=set()
    with wal.open("rb") as source:
        for raw in source:
            row=json.loads(raw);ev=row["causal_event"];t=ev["t_monde"];kind=ev["kind"]
            if head is not None and row["previous_hash"]!=head:
                raise ValueError("broken WAL link")
            head=row["event_hash"];count+=1
            if kind=="perceptual_capture":
                before[t]=ev["data"]["dual_scope_visible_body"]
            elif kind=="world_transition_experienced":
                after[t]=ev["body_after"]
            elif kind=="command_experienced":
                if t in actions:raise ValueError("multiple physical commands")
                actions[t]=(ev["primitive"],ev.get("parameters") or {})
            elif kind=="i1_unknown_affordance_proposed":
                d=ev["data"];c=d.get("command") or {}
                if c.get("primitive")=="manger" and (
                    c.get("parameters") or {}).get("target")=="berry_b":
                    proposals[t].append(d)
            elif kind=="td_update_published" and ev["data"]["previous_signature"]==SIGNATURE:
                updates[t].append(ev["data"])
            elif kind=="step_closed":
                if t in closed:raise ValueError("duplicate physical step")
                closed.add(t)
    if (count!=life["durable_entries"] or head!=life["journal_head"]
        or len(closed)!=len(life["steps"])):
        raise ValueError("WAL head/count/closed-step mismatch")
    weight,threat=birth_integrity_weight(life["individual_id"])
    ingestions=[]
    for t,(primitive,params) in sorted(actions.items()):
        if primitive!="manger" or params.get("target")!="berry_b":
            continue
        if t not in before or t not in after:
            raise ValueError("physical ingestion without before/after")
        reward=deviation(before[t],weight)-deviation(after[t],weight)
        td=updates.get(t+1,[])
        direct=td[0] if len(td)==1 else None
        observed=num(direct["return_g"]) if direct else None
        if direct and direct["segment_length"]==1 and abs(observed-reward)>1e-6:
            raise ValueError("TD return differs from lived homeostatic reward")
        ingestions.append({
            "step":t,"integrity_before":num(before[t]["integrity"]),
            "integrity_after":num(after[t]["integrity"]),
            "reward_subjective":reward,
            "direct_next_step_td_return":observed,
            "direct_td_credit_visible":direct is not None,
        })
    first=ingestions[0]["step"] if ingestions else None
    later=[(t,v) for t,v in sorted(proposals.items())
           if first is not None and t>first]
    first_learned=next((
        {"step":t,"value":num(rows[0]["learned_value"])}
        for t,rows in later if rows[0]["learned_value_status"]=="learned"
        and rows[0]["learned_value"] is not None),None)
    return {
        "schema":"i1-berry-valence-wal-v1",
        "source_sha":report["run"]["git_head"],
        "world_sha":report["source"]["sha256"],
        "seed":report["run"]["seed"],"variant":report["run"]["world_variant"],
        "individual_id":life["individual_id"],
        "toxicity":damage,"threat_sensitivity":threat,
        "integrity_weight":weight,"life_state":life["lifecycle"],
        "observed_steps":len(life["steps"]),"ingestions":ingestions,
        "first_post_ingestion_learned_proposal":first_learned,
        "post_ingestion_distinct_proposal_steps":len(later),
        "claim_of_causal_avoidance":"NOT_ESTABLISHED",
        "wal_head":head,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    result=analyze(args.input)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",
                           encoding="utf-8")
    print(json.dumps({"variant":result["variant"],"toxicity":result["toxicity"],
        "ingestions":len(result["ingestions"]),
        "first_reward":result["ingestions"][0]["reward_subjective"]
                         if result["ingestions"] else None,
        "status":result["claim_of_causal_avoidance"]}))
if __name__=="__main__":
    main()
