"""First real-state replay-content fork neutrality: ENGINEERING ONLY.

2 unused PUBLIC synthetic F0 specs (ordinals 182..183) of the *same*
original random-content policy, observed/unobserved. Eight real physical
technical executions; compare complete live trace and funding. Never publish
survival, resource history, positions or observed per-life mechanisms.
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
from ..runtime.realstate_content_fork_observer import SCHEMA

FIRST = 182
PAIRS = 2
HORIZON = 240
POLICY = "p13_replay_gate_random_content_v1"
PROTOCOL = "I3_REALSTATE_CONTENT_FORK_ENGINEERING_ONLY"


def cases():
    sample=SAMPLE.preview(SAMPLE.PREVIEW_WITNESS)
    SAMPLE.verify_preview(sample,SAMPLE.PREVIEW_WITNESS)
    units=sample["proposed_units"][FIRST:FIRST+PAIRS]
    if len(units)!=PAIRS:
        raise ValueError("missing unused technical units")
    return [{"pair_id":x["pair_id"],"index":x["ordinal"],
             "cohort":"engineering","family":x["family"],
             "world_seed":x["world_seed"],"genome_seed":x["genome_seed"],
             "life_seed":x["life_seed"],"policy":POLICY} for x in units]


def match_case(case,fingerprint):
    if type(case) is not dict or type(case.get("index")) is not int:
        raise PermissionError("real-state engineering case required")
    offset=case["index"]-FIRST
    if not 0<=offset<PAIRS or case.get("policy")!=POLICY:
        raise PermissionError("outside new real-state public engineering scope")
    if case!=cases()[offset]:
        raise PermissionError("real-state synthetic engineering identity mutated")
    if fingerprint!=SOURCE.source_fingerprint():
        raise PermissionError("source fingerprint mismatch")


def _run(case,fingerprint,observe):
    match_case(case,fingerprint)
    spec=SPECS._construct_f0_spec(case["family"],case["world_seed"])
    ticket=GUARD.admit_realstate_content_fork_engineering(
        case=case,spec=spec,transport_fingerprint=fingerprint)
    return run_life(generation_zero(case["genome_seed"]),spec,
                    case["life_seed"],HORIZON,protocol=PROTOCOL,
                    decision_policy=POLICY,admission=ticket,
                    observer_realstate_content_fork=observe)


def _equal_life(a,b):
    keys=("trace_head","terminal","steps_lived","death_causes",
          "actions","first_drink_step","drinks","meals","final_body",
          "cognitive_accounting","replay_gate","manifest_id","manifest")
    return all(a[k]==b[k] for k in keys)


def rehearse():
    source=SOURCE.source_fingerprint()
    observer_count=0
    first_fork_captured=0
    for case in cases():
        plain=_run(case,source,False)
        watched=_run(case,source,True)
        if not _equal_life(plain,watched):
            raise RuntimeError("real-state detached probe changed live physics or cognition")
        if "observer_realstate_content_fork" in plain:
            raise RuntimeError("observer leaked into reference execution")
        if "observer_realstate_content_fork" not in watched:
            raise RuntimeError("observer missing in technical execution")
        receipt=watched["observer_realstate_content_fork"]
        if receipt["schema"]!=SCHEMA:
            raise RuntimeError("unknown realstate observer receipt")
        if receipt["status"]=="FIRST_DIFFERING_REPLAY_CAPTURED":
            fork=receipt["first_fork"]
            if (fork["prepaid_replays_in_each_detached_arm"]<=0
                    or fork["observer_physical_debit"] is not False
                    or fork["world_or_life_clone_created"] is not False):
                raise RuntimeError("fictitious or unpaid detached replay")
            first_fork_captured+=1
        observer_count+=1
    return {
        "schema":"i3-realstate-content-fork-neutrality-engineering/v1",
        "status":"OBSERVER_PHYSICAL_NEUTRALITY_PASS",
        "public_synthetic_source":True,"pairs":PAIRS,
        "observed_lives":observer_count,
        "real_full_life_executions":2*observer_count,
        "first_fork_captures":first_fork_captured,
        "physical_and_decision_trace_identical_on_off":True,
        "prepaid_replay_count_unchanged":True,
        "no_second_world":True,
        "biological_outcomes_published":False,
        "source_fingerprint":source,
        "scientific_lives":0,
        "scientific_verdict":"NOT_ISSUED",
    }


def main(argv=None):
    argv=sys.argv if argv is None else argv
    if len(argv)!=2 or argv[1]!="rehearse":
        raise SystemExit("usage: python -m i3.lab.stage2_realstate_content_fork_engineering rehearse")
    print(json.dumps(rehearse(),sort_keys=True,indent=2))


if __name__=="__main__":
    main()
