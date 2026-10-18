#!/usr/bin/env python3
"""External observer: descriptive main-cohort analytics with fail-closed custody."""
from __future__ import annotations
import argparse,collections,json,pathlib
SHA="11fa9104e7e9d2c7ad70e837c80463fc4cbe4777"
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=pathlib.Path)
    p.add_argument("--output",required=True,type=pathlib.Path)
    args=p.parse_args()
    report=json.loads((args.input/"report.json").read_text())
    if (report.get("status")!="COMPLETED_WITHOUT_SCIENTIFIC_VERDICT"
        or report.get("engine")!="I1" or report.get("run",{}).get("git_head")!=SHA
        or report.get("run",{}).get("custody")!="wal"
        or not report.get("run",{}).get("observe_owner_digests")
        or len(report.get("lives",[]))!=3):
        raise ValueError("wrong subject, provenance or technical state")
    lives=[]
    for life in report["lives"]:
        evidence=args.input/life["custody_file"]
        if not evidence.is_file() or evidence.is_symlink():raise ValueError("WAL missing")
        records=[json.loads(line) for line in evidence.read_bytes().splitlines()]
        if len(records)!=life["durable_entries"] or not records or records[-1]["event_hash"]!=life["journal_head"]:
            raise ValueError("WAL count/head drift")
        kinds=collections.Counter(row["causal_event"].get("kind") for row in records)
        if len({row["causal_event"].get("t_monde") for row in records if row["causal_event"].get("kind")=="step_closed"})!=len(life["steps"]):
            raise ValueError("not all world steps closed")
        c=collections.Counter()
        age_bins=collections.defaultdict(lambda:{"steps":0,"actions":collections.Counter()})
        owner_windows=collections.Counter()
        commits=0
        for ix,step in enumerate(life["steps"]):
            sensor=step.get("owner_observation")
            if not isinstance(sensor,dict) or set(sensor["before"])!=set(sensor["after"]):
                raise ValueError("missing or unaligned owner sensors")
            changed=[n for n in sensor["before"] if sensor["before"][n]!=sensor["after"][n]]
            for n in changed:owner_windows[n]+=1
            commits+=len(sensor["stage10_commit_event_ids"])
            applied=step["execution"] in ("applied","dead")
            if applied:c[step["action_primitive"]]+=1
            age=ix+1
            binname=next(label for end,label in [(30,"1-30"),(60,"31-60"),(120,"61-120"),(180,"121-180"),(240,"181-240"),(300,"241-300")] if age<=end)
            age_bins[binname]["steps"]+=1
            if applied:age_bins[binname]["actions"][step["action_primitive"]]+=1
        if commits!=kinds["stage10_consolidation_committed"]:
            raise ValueError("owner observer and WAL Stage10 receipt mismatch")
        n=len(life["steps"]);total=sum(c.values())
        lives.append({"individual_id":life["individual_id"],"world":report["source"]["preset"],
                      "seed":report["run"]["seed"],"steps":n,"status":life["lifecycle"],
                      "applied_actions":total,"per_step":total/n if n else None,
                      "primitive_counts":dict(c),
                      "age_bins":{k:{"steps":v["steps"],"actions":dict(v["actions"])} for k,v in age_bins.items()},
                      "stage10_committed":commits,"stage10_technical_events":{k:v for k,v in kinds.items() if str(k).startswith("stage10_")},
                      "owner_hash_changed_world_steps":dict(owner_windows),
                      "semantic_publication":"NOT_ESTABLISHED_BY_HASH_ONLY",
                      "attributable_learning":"NOT_ESTABLISHED"})
    out={"subject_sha":SHA,"scientific_status":"DESCRIPTIVE_NO_GO","source_preset_digest":report["source"]["sha256"],
         "lives":lives,"owner_observer_interpretation":"Technical hashes do not establish causal learning"}
    args.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":"DESCRIPTIVE","lives":len(lives),"steps":sum(x["steps"] for x in lives)}))
if __name__=="__main__":main()
