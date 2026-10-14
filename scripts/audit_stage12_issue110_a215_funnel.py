"""A2.15 external, WAL-independent semantic census of real lived agency pairs.

Operator-side only. The source is pre-existing sealed causal JSONL archives.
Never imports an I0 cognitive owner, a world simulator, Oracle or Bench.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from lab.independent_journal_audit import audit_export_bytes
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs

def census_one(path: Path) -> dict:
    raw=path.read_bytes()
    base=audit_export_bytes(raw)
    progress=audit_stage12_goal_progress(raw,expected_head=base.head_hash,
                                        expected_count=base.occurrences)
    agency=audit_stage12_first_person_agency(raw,expected_head=base.head_hash,
                                             expected_count=base.occurrences)
    pairs=audit_stage12_attribution_pairs(raw,expected_head=base.head_hash,
                                          expected_count=base.occurrences)
    ev=[{**row["causal_event"],"event_id":row["event_id"]}\n        for row in (json.loads(line) for line in raw.splitlines())]
    by_kind={}
    for e in ev:
        by_kind.setdefault(e["kind"],[]).append(e)
    def events(kind):
        return by_kind.get(kind,[])
    followups=Counter(e["data"].get("criterion_outcome","absent") for e in
                      events("stage12_goal_progress_followup"))
    judgements=Counter(e["data"].get("subjective_agency","absent") for e in
                       events("stage12_goal_agency_judgement"))
    admitted=events("stage12_attribution_pair_admitted")
    diagnostics=events("stage12_lived_diagnostics_published")
    accepted={e["data"]["attribution_pair_ref"] for e in diagnostics
              if e.get("data",{}).get("attribution_pair_ref") is not None}
    admitted_ids={e["event_id"] for e in admitted}
    if not accepted.issubset(admitted_ids):
        raise ValueError("diagnostic pair without admitted source")
    join_charges=[e["data"] for e in events("compute_charge")
                  if e.get("data",{}).get("operation")=="stage12_attribution_join"]
    diag_charges=[e["data"] for e in events("compute_charge")
                  if e.get("data",{}).get("operation")=="stage12_diagnostic_sample"]
    diagnostic_samples=[e for e in diagnostics if
                        "attribution_pair_ref" in e["data"]]
    window=[]
    max_window_success=max_window_failure=0
    count_evaluable=0
    for e in diagnostic_samples:
        data=e["data"]
        size=data["diagnostic_window"]
        minimum=data["bias_min_outcomes_each"]
        if size != 12 or minimum != 2:
            raise ValueError("unexpected 2+2/12 detector contract")
        ref=data["attribution_pair_ref"]
        window.append(ref)
        window=window[-size:]
        included=[next(p for p in admitted if p["event_id"]==r)["data"]
                  for r in window if r is not None]
        successes=sum(p["outcome"]=="success" for p in included)
        failures=sum(p["outcome"]=="failure" for p in included)
        if successes!=data["verified_successes"] or failures!=data["verified_failures"]:
            raise ValueError("unreproducible detector pair window")
        max_window_success=max(max_window_success,successes)
        max_window_failure=max(max_window_failure,failures)
        count_evaluable+=int(successes>=minimum and failures>=minimum)
        if (successes>=minimum and failures>=minimum)!=(data.get("attribution_bias") is not None):
            raise ValueError("misrepresented detector calibration")
    missed=events("stage12_attribution_sample_unavailable")
    remaining=pairs.admitted_pairs-pairs.applied_pairs-pairs.missed_pairs
    if remaining<0:
        raise ValueError("more consumed or missing pairs than admitted")
    if remaining and not any(e["kind"]=="stage12_attribution_pair_admitted" and
                             e["event_id"] not in accepted for e in ev):
        raise ValueError("terminal pending attribution accounting mismatch")
    if (len(admitted)!=pairs.admitted_pairs
        or len(accepted)!=pairs.applied_pairs
        or len(missed)!=pairs.missed_pairs
        or sum(followups.values())!=
           len(events("stage12_goal_progress_followup"))
        or judgements.get("self",0)!=agency.judgements_self
        or judgements.get("world",0)!=agency.judgements_world):
        raise ValueError("independent auditor counters disagree")
    if len(diagnostics)!=len(diagnostic_samples):
        raise ValueError("nonversioned diagnostics make window scope incomplete")
    closed=base.world_steps_closed
    report={
      "life":path.parent.name,
      "sha256":sha256(raw).hexdigest(),
      "world_steps":closed,
      "goal_preregistrations":len(events("stage12_goal_progress_preregistered")),
      "goal_followups":dict(sorted(followups.items())),
      "agency_precommits":len(events("stage12_goal_agency_precommitted")),
      "agency_judgements":dict(sorted(judgements.items())),
      "join_uc_accepted":sum(bool(c.get("accepted")) for c in join_charges),
      "join_uc_refused":sum(c.get("accepted") is False for c in join_charges),
      "join_deferred":len(events("stage12_attribution_join_deferred")),
      "diagnostic_uc_accepted":sum(bool(c.get("accepted")) for c in diag_charges),
      "diagnostic_uc_refused":sum(c.get("accepted") is False for c in diag_charges),
      "diagnostic_deferred":len(events("stage12_lived_diagnostics_deferred")),
      "pairs_admitted":len(admitted),
      "pairs_applied":len(accepted),
      "pairs_unavailable":len(missed),
      "pairs_terminal_pending":remaining,
      "pairs_consumed_success":pairs.applied_successes,
      "pairs_consumed_failure":pairs.applied_failures,
      "pairs_consumed_self":pairs.applied_self,
      "pairs_consumed_world":pairs.applied_world,
      "paid_diagnostic_samples":len(diagnostics),
      "window_max_success":max_window_success,
      "window_max_failure":max_window_failure,
      "calibrable_windows":count_evaluable,
      "reported_bias_labels":dict(sorted(Counter(e["data"]["attribution_bias"]
                for e in diagnostics if e["data"]["attribution_bias"] is not None).items())),
      "reduced_sleep_captures":len(events("stage10_reduced_capture")),
      "physical_meals":sum(e.get("effects",{}).get("ate") in ("berry_a","berry_b")
                          for e in events("world_transition_experienced")),
      "independently_audited":True,
    }
    return report

def run(root: Path) -> dict:
    paths=sorted(root.rglob("canonical.jsonl"))
    if not paths: raise ValueError("no canonical causal journals supplied")
    rows=[census_one(path) for path in paths]
    counts={
        "world_steps":sum(x["world_steps"] for x in rows),
        "goal_preregistrations":sum(x["goal_preregistrations"] for x in rows),
        "goal_followup_known":sum(sum(v for k,v in x["goal_followups"].items()
                                  if k in ("success","failure")) for x in rows),
        "agency_self_world":sum(x["agency_judgements"].get("self",0)+
                                 x["agency_judgements"].get("world",0) for x in rows),
        "joins_refused":sum(x["join_uc_refused"] for x in rows),
        "pairs_admitted":sum(x["pairs_admitted"] for x in rows),
        "pairs_applied":sum(x["pairs_applied"] for x in rows),
        "pairs_unavailable":sum(x["pairs_unavailable"] for x in rows),
        "pairs_terminal_pending":sum(x["pairs_terminal_pending"] for x in rows),
        "applied_successes":sum(x["pairs_consumed_success"] for x in rows),
        "applied_failures":sum(x["pairs_consumed_failure"] for x in rows),
        "calibrable_windows":sum(x["calibrable_windows"] for x in rows),
        "lives_calibrable":sum(x["calibrable_windows"]>0 for x in rows),
        "physical_meals":sum(x["physical_meals"] for x in rows),
    }
    return {"schema":"a215-lifetime-attribution-funnel-v1",
            "source":"sealed-worldly-causal-journals-a210b-38607070724",
            "lives":rows,"life_count":len(rows),"totals":counts,
            "stage12_verdict":"PARTIAL","operator_accepted":False,
            "normative_modified":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    result=run(args.input_dir)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("A215_SUMMARY "+json.dumps({k:v for k,v in result.items() if k!="lives"},
                                    sort_keys=True),flush=True)
    if result["life_count"]!=16 or result["totals"]["world_steps"]!=672:
        raise SystemExit(2)

if __name__=="__main__":
    main()
