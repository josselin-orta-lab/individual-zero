"""Exact public F0 184-185 next-decision observer on/off neutrality.

No scientific or survival inference. Two new PUBLIC preview ordinals, one
random-content policy, no index repeats from the prior realstate fork 182-183.
Every observed/unobserved actual life must have identical physical and
decision trace, replay count, funding, original manifest and RNG authority.
Only structural counters may be published; never individual lives/outcomes.
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
from ..runtime.next_decision_replay_observer import SCHEMA

FIRST=184
UNITS=2
HORIZON=260
POLICY="p13_replay_gate_random_content_v1"
PROTOCOL="I3_NEXT_DECISION_REPLAY_OBSERVER_ENGINEERING_ONLY"


def cases():
    preview=SAMPLE.preview(SAMPLE.PREVIEW_WITNESS)
    SAMPLE.verify_preview(preview,SAMPLE.PREVIEW_WITNESS)
    rows=preview["proposed_units"][FIRST:FIRST+UNITS]
    if len(rows)!=UNITS:
        raise PermissionError("unallocated public engineering source")
    return [{"pair_id":x["pair_id"],"index":x["ordinal"],
             "cohort":"engineering","family":x["family"],
             "world_seed":x["world_seed"],"genome_seed":x["genome_seed"],
             "life_seed":x["life_seed"],"policy":POLICY} for x in rows]


def match_case(case,fingerprint):
    if type(case) is not dict or type(case.get("index")) is not int:
        raise PermissionError("exact next-decision technical allocation required")
    index=case["index"]-FIRST
    if not 0<=index<UNITS or case.get("policy")!=POLICY:
        raise PermissionError("unallocated technical source or policy")
    if case!=cases()[index] or fingerprint!=SOURCE.source_fingerprint():
        raise PermissionError("changed technical source")


def _run(case,fingerprint,observe):
    match_case(case,fingerprint)
    spec=SPECS._construct_f0_spec(case["family"],case["world_seed"])
    ticket=GUARD.admit_next_decision_replay_engineering(
        case=case,spec=spec,transport_fingerprint=fingerprint)
    return run_life(generation_zero(case["genome_seed"]),spec,
                    case["life_seed"],HORIZON,protocol=PROTOCOL,
                    decision_policy=POLICY,admission=ticket,
                    observer_next_decision_replay=observe)


def _same_life(a,b):
    keys=("trace_head","terminal","steps_lived","death_causes","actions",
          "first_drink_step","drinks","meals","final_body",
          "cognitive_accounting","replay_gate","manifest_id","manifest")
    return all(a[k]==b[k] for k in keys)


def rehearse():
    fingerprint=SOURCE.source_fingerprint()
    captures=0
    next_decisions=0
    shared_action_residuals=0
    for case in cases():
        plain=_run(case,fingerprint,False)
        observed=_run(case,fingerprint,True)
        if not _same_life(plain,observed):
            raise RuntimeError("next-decision observer changed actual lived history")
        if ("observer_next_decision_replay" in plain or
                "observer_next_decision_replay" not in observed):
            raise RuntimeError("observer leaked into baseline or missing on observed arm")
        report=observed["observer_next_decision_replay"]
        if report["schema"]!=SCHEMA or not report["external_detached_work_only"]:
            raise RuntimeError("invalid detached next decision report")
        if report["funded_opportunities"]>observed["replay_gate"]["random_content"]["paid_replay_opportunities"]:
            raise RuntimeError("unfunded replay was observed")
        event=report["first_fork"]
        if event is not None:
            captures+=1
            if report["status"]=="FIRST_FORK_AND_NEXT_DECISION_CAPTURED":
                next_decisions+=1
                next_decision=event["next_decision"]
                if not next_decision["random_branch_matches_actual_live_decision_and_work"]:
                    raise RuntimeError("random branch failed live equality")
                if event["shared_actual_transition_td_residual"] is not None:
                    if not next_decision["same_admitted_action_and_param"]:
                        raise RuntimeError("off-policy TD residual mislabeled shared action")
                    shared_action_residuals+=1
    return {
        "schema":"i3-next-decision-replay-neutrality-engineering/v1",
        "status":"OBSERVER_PHYSICAL_AND_DECISION_NEUTRALITY_PASS",
        "public_synthetic_source":True,
        "technical_units":UNITS,
        "actual_technical_life_executions":2*UNITS,
        "first_detached_forks":captures,
        "next_decisions_observed":next_decisions,
        "shared_action_residuals":shared_action_residuals,
        "identical_physical_and_decision_traces_on_off":True,
        "no_observer_work_billed_to_organism":True,
        "no_new_scientific_lives":True,
        "no_survival_outcomes_published":True,
        "scientific_verdict":"NOT_ISSUED",
        "source_fingerprint":fingerprint,
    }


def main(argv=None):
    argv=sys.argv if argv is None else argv
    if len(argv)!=2 or argv[1]!="rehearse":
        raise SystemExit("usage: python -m i3.lab.stage2_next_decision_replay_engineering rehearse")
    print(json.dumps(rehearse(),sort_keys=True,indent=2))


if __name__=="__main__":
    main()
