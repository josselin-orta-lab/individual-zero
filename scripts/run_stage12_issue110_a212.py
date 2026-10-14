"""A2.12 read-only exact-key probe around unchanged physical A2.11b lives.

The external lab observes actual Equipment.predict calls. No result, refusal,
UC charge or cognitive state is changed and the probe is never sent to I0.
"""
from collections import Counter, defaultdict
from hashlib import sha256
import argparse
import json
from pathlib import Path
import subprocess

import run_stage12_issue110_a211b as baseline
from i0.equipment import FrozenTableEquipment
from lab.equipment_corpus import EquipmentCorpusRecorder

_original_predict = FrozenTableEquipment.predict
_original_record = EquipmentCorpusRecorder.record_transition
active = None


def record_training(self, **kwargs):
    example = _original_record(self, **kwargs)
    if active is not None:
        active["training"].append(example)
    return example


def observed_predict(self, *, state, command):
    if active is None:
        return _original_predict(self, state=state, command=command)
    key = self.input_digest(state, command)
    try:
        result = _original_predict(self, state=state, command=command)
    except LookupError:
        outcome = "unavailable"
        raise
    else:
        outcome = "available"
        return result
    finally:
        rec = active["queries"].get(key)
        if rec is None:
            # Query is a live Simulator input, not ground truth. It stays in
            # the external lab's file and is never used for further decisions.
            rec = {"input_hash":key,"command":command.as_dict(),
                   "state":state.as_dict(),"available":outcome=="available",
                   "count":0}
            active["queries"][key] = rec
        elif rec["available"] != (outcome=="available"):
            raise AssertionError("nondeterministic frozen Equipment coverage")
        rec["count"] += 1


def diff_features(query, examples):
    same_command = [e for e in examples
                    if e.command.as_dict()==query["command"]]
    fields=("x","y","body","inventory","current_water_source",
            "current_resources","adjacent","known_shelter_here","is_night")
    if not same_command:
        return {"category":"unseen_command","matching_command_examples":0,
                "closest_differing_fields":list(fields)}
    state=query["state"]
    candidates=[tuple(name for name in fields
                      if e.state.as_dict()[name]!=state[name])
                for e in same_command]
    best=min(candidates,key=lambda d:(len(d),d))
    if not best:
        raise AssertionError("same exact accessible input was marked unavailable")
    return {"category":"unseen_state_for_known_command",
            "matching_command_examples":len(same_command),
            "closest_differing_fields":list(best)}


def run(root, cohort):
    global active
    rows=[]
    root.mkdir(parents=True,exist_ok=False)
    for profile in baseline.PROFILES:
        for timing in baseline.TIMINGS:
            for extended in (False,True):
                active={"training":[],"queries":{}}
                try:
                    life=baseline.run_one(root,cohort,profile,timing,extended)
                    examples=active["training"]
                    queries=active["queries"]
                    misses=[]
                    for q in queries.values():
                        if q["available"]:
                            continue
                        details=diff_features(q,examples)
                        misses.append({**{k:v for k,v in q.items() if k!="state"},
                                       **details})
                    categories=Counter(q["category"] for q in misses)
                    field_counts=Counter(f for q in misses
                                         for f in q["closest_differing_fields"])
                    name=life["name"]
                    result={
                        "life":name,"model_sha256":life["equipment_sha256"],
                        "training_count":len(examples),
                        "training_unique_input_hashes":len({
                            FrozenTableEquipment.input_digest(e.state,e.command)
                            for e in examples}),
                        "query_unique_input_hashes":len(queries),
                        "query_attempts":sum(q["count"] for q in queries.values()),
                        "available_unique":sum(q["available"] for q in queries.values()),
                        "unavailable_unique":len(misses),
                        "unavailable_attempts":sum(q["count"] for q in queries.values()
                                                   if not q["available"]),
                        "failure_categories":dict(categories),
                        "nearest_input_differing_fields":dict(field_counts),
                        "unseen_input_details":misses,
                        "life_physical":life,
                    }
                    (root/name/"exact-key-audit.json").write_text(
                        json.dumps(result,sort_keys=True,indent=2)+"\n")
                    rows.append(result)
                    print("A212_LIFE "+json.dumps({k:v for k,v in result.items()
                         if k not in ("unseen_input_details","life_physical")},sort_keys=True),flush=True)
                finally:
                    active=None
    return rows


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--cohort-id",required=True)
    args=ap.parse_args()
    if not args.cohort_id.isascii() or not all(
        x.isalnum() or x in "._-" for x in args.cohort_id):
        ap.error("invalid cohort id")
    FrozenTableEquipment.predict=observed_predict
    EquipmentCorpusRecorder.record_transition=record_training
    try:
        rows=run(args.output_dir,args.cohort_id)
    finally:
        FrozenTableEquipment.predict=_original_predict
        EquipmentCorpusRecorder.record_transition=_original_record
    report={
        "schema":"a212-key-level-observer-v1",
        "code_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        "real_unique_lives":len(rows),
        "real_physical_steps":sum(x["life_physical"].get("world_steps",0) for x in rows),
        "technical_errors":sum(bool(x["life_physical"].get("failure") or
                                 x["life_physical"].get("audit_error")) for x in rows),
        "unique_unavailable_input_keys":sum(x["unavailable_unique"] for x in rows),
        "unknown_command_keys":sum(x["failure_categories"].get("unseen_command",0)
                                    for x in rows),
        "pairs":[{"profile":profile,"timing":timing,
            "control":next(x for x in rows if x["life"]==f"{profile}_{timing}_corpus_original")["unavailable_unique"],
            "expanded":next(x for x in rows if x["life"]==f"{profile}_{timing}_corpus_extended")["unavailable_unique"]}
            for profile in baseline.PROFILES for timing in baseline.TIMINGS],
        "operator_accepted":False,"stage12_verdict":"PARTIAL",
    }
    (args.output_dir/"a212-summary.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("A212_SUMMARY "+json.dumps(report,sort_keys=True),flush=True)
    return 0 if (report["real_unique_lives"]==8 and
                 report["real_physical_steps"]==336 and report["technical_errors"]==0) else 2


if __name__=="__main__":
    raise SystemExit(main())
