"""Full-life observer neutrality rehearsal, engineering only, no survival claims.

Two unused PUBLIC preview F0 units, two content policies, one observed and
one unobserved life per matched arm: 8 technical executions. Their complete
physical/trace identities MUST match, or the observer is rejected. These are
not fresh independent scientific World draws or biological evidence.
"""
from __future__ import annotations

import json
import sys

from . import stage2_survival_b1_sampling as SAMPLE
from . import stage2_survival_b1_worldspec_audit as SPECS
from . import stage2_survival_b1_engineering as SOURCE
from . import stage2_admission as GUARD
from ..modules.genome import generation_zero
from ..runtime.life import run_life
from ..runtime.replay_water_observer import first_divergences, SCHEMA

FIRST=180
PAIRS=2
HORIZON=200
PROTOCOL="I3_WATER_REPLAY_OBSERVER_NEUTRALITY_ENGINEERING_ONLY"
POLICIES=("p13_replay_gate_v1","p13_replay_gate_random_content_v1")


def cases():
    source=SAMPLE.preview(SAMPLE.PREVIEW_WITNESS)
    SAMPLE.verify_preview(source,SAMPLE.PREVIEW_WITNESS)
    units=source["proposed_units"][FIRST:FIRST+PAIRS]
    if len(units)!=PAIRS:
        raise ValueError("missing unexposed observer engineering World metadata")
    return [{**{
        "pair_id":x["pair_id"],"index":x["ordinal"],
        "cohort":"engineering","family":x["family"],
        "world_seed":x["world_seed"],"genome_seed":x["genome_seed"],
        "life_seed":x["life_seed"]},"policy":p}
        for x in units for p in POLICIES]


def match_case(case,fingerprint):
    if type(case) is not dict or type(case.get("index")) is not int:
        raise PermissionError("observer engineering exact case required")
    offset=case["index"]-FIRST
    if not 0<=offset<PAIRS or case.get("policy") not in POLICIES:
        raise PermissionError("wrong observer engineering index/policy")
    if case!=cases()[2*offset+POLICIES.index(case["policy"])]:
        raise PermissionError("observer engineering source identity changed")
    if fingerprint!=SOURCE.source_fingerprint():
        raise PermissionError("observer engineering code/source footprint changed")


def _run(case,fingerprint,enabled):
    match_case(case,fingerprint)
    spec=SPECS._construct_f0_spec(case["family"],case["world_seed"])
    ticket=GUARD.admit_water_replay_observer_engineering(
        case=case,spec=spec,transport_fingerprint=fingerprint)
    return run_life(generation_zero(case["genome_seed"]),spec,
                    case["life_seed"],HORIZON,protocol=PROTOCOL,
                    decision_policy=case["policy"],admission=ticket,
                    observer_replay_water=enabled)


def _same_life(a,b):
    # Exactly the same execution, not merely a same outcome. Elapsed runtime,
    # observer-only output, and evidence_head differ by output construction
    # only; trace_head captures the complete actual physical body/action path.
    names=("trace_head","terminal","steps_lived","death_causes",
           "actions","first_drink_step","drinks","meals","final_body",
           "cognitive_accounting","replay_gate","manifest_id","manifest")
    return all(a[k]==b[k] for k in names)


def rehearse():
    rows=cases()
    fingerprint=SOURCE.source_fingerprint()
    observed=[]
    for case in rows:
        plain=_run(case,fingerprint,False)
        watched=_run(case,fingerprint,True)
        if not _same_life(plain,watched):
            raise RuntimeError("OBSERVER_CAUSED_PHYSICAL_OR_DECISION_DIVERGENCE")
        if "observer_replay_water" in plain or "observer_replay_water" not in watched:
            raise RuntimeError("observer leaked into default runtime")
        report=watched["observer_replay_water"]
        if report["schema"]!=SCHEMA or report["lived_steps"]!=watched["steps_lived"]:
            raise RuntimeError("missing observed step")
        if report["replay_count_actual"]!=watched["cognitive_accounting"]["replays_executed"]:
            raise RuntimeError("observer missed physically prepaid replay")
        if any(step["paid_replays_actual"]!=len(step["replay_memory_indices"])
               for step in report["steps"]):
            raise RuntimeError("unpaid replay included in witness")
        if watched["cognitive_accounting"]["shortfall_steps"]!=0:
            raise RuntimeError("unpaid cognition in observed engineering life")
        observed.append(report)
    # Each of the 2 pairs was born twice per arm for the explicit observer-
    # neutral engineering demonstration, not a scientific replicate.
    comparisons=[first_divergences(observed[2*i],observed[2*i+1])
                 for i in range(PAIRS)]
    return {
        "schema":"i3-water-replay-observer-neutrality-engineering/v1",
        "status":"OBSERVER_NEUTRALITY_PASS",
        "pairs":PAIRS,"policies":list(POLICIES),
        "physical_life_executions":len(rows)*2,
        "matched_observed_policy_pairs":PAIRS,
        "identical_trace_and_funding_observer_on_off":True,
        "observer_passive":True,
        "zero_unpaid_replays":True,
        "source_fingerprint":fingerprint,
        # Only allowlisted structural chronology fields, not biological
        # terminal/survival, first-death, resource outcomes or body trajectories.
        "first_divergence_channels_present":sorted(
            comparisons[0]["first_differences"]),
        "first_divergence_report_kept_out_of_public_engineering_receipt":True,
        "biological_outcomes_published":False,
        "scientific_lives":0,"scientific_go":False,
    }


def main(argv=None):
    argv=sys.argv if argv is None else argv
    if len(argv)!=2 or argv[1]!="rehearse":
        raise SystemExit("usage: python -m i3.lab.stage2_water_replay_observer_engineering rehearse")
    print(json.dumps(rehearse(),sort_keys=True,indent=2))


if __name__=="__main__":
    main()
