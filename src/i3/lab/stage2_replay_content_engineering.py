"""First full-life replay-*content* ablation: ENGINEERING ONLY.

12 unused public-synthetic B1 F0 units x identical newborn genome, WorldSpec,
and life seed. Both policies use the same funded GATE decision for replay
QUANTITY; only TD-priority vs independently seeded uniform memory identity
changes. Full lives are temporary sealed G/R originals, not survival data.
"""
from __future__ import annotations

import json
import sys
from hashlib import sha256

from . import stage2_survival_b1_sampling as SAMPLE
from . import stage2_survival_b1_worldspec_audit as SPECS
from . import stage2_survival_b1_engineering as SOURCE
from . import stage2_admission as GUARD
from . import two_phase_panel as TP
from ..modules.genome import generation_zero
from ..runtime.life import run_life

SCHEMA = "i3-stage2-1-replay-content-full-life-engineering/v1"
PROTOCOL = "I3_REPLAY_CONTENT_MATCHED_ENGINEERING_NEVER_SCIENCE"
COHORT = "engineering"
FIRST = 144
PAIRS = 12
HORIZON = 400
POLICIES = ("p13_replay_gate_v1", "p13_replay_gate_random_content_v1")


def cases():
    preview = SAMPLE.preview(SAMPLE.PREVIEW_WITNESS)
    SAMPLE.verify_preview(preview, SAMPLE.PREVIEW_WITNESS)
    units = preview["proposed_units"][FIRST:FIRST + PAIRS]
    if len(units) != PAIRS:
        raise ValueError("missing fixed replay-content engineering units")
    return [{"pair_id": u["pair_id"], "index": u["ordinal"],
             "cohort": COHORT, "family": u["family"],
             "world_seed": u["world_seed"],
             "genome_seed": u["genome_seed"], "life_seed": u["life_seed"],
             "policy": arm}
            for u in units for arm in POLICIES]


def match_case(case, fingerprint):
    if type(case) is not dict or type(case.get("index")) is not int:
        raise PermissionError("exact engineering case required")
    offset=case["index"]-FIRST
    if not 0 <= offset < PAIRS or case.get("policy") not in POLICIES:
        raise PermissionError("outside unused replay-content engineering allocation")
    if case != cases()[2*offset + POLICIES.index(case["policy"])]:
        raise PermissionError("replay-content engineering case mutated")
    if fingerprint != SOURCE.source_fingerprint():
        raise PermissionError("replay-content engineering source mismatch")


def _run_case(scheduled, fingerprint):
    def run(case):
        match_case(case,fingerprint)
        offset=case["index"]-FIRST
        if case != scheduled[2*offset+POLICIES.index(case["policy"])]:
            raise PermissionError("not in original engineering order")
        spec=SPECS._construct_f0_spec(case["family"],case["world_seed"])
        ticket=GUARD.admit_replay_content_newworld_engineering(
            case=case,spec=spec,transport_fingerprint=fingerprint)
        life=run_life(generation_zero(case["genome_seed"]),spec,
                      case["life_seed"],HORIZON,protocol=PROTOCOL,
                      decision_policy=case["policy"],admission=ticket)
        life["admission_receipt"]=ticket.receipt()
        return life
    return run


def _reduce_structural(identity,life):
    m=life["manifest"]
    return {
        "pair_id":identity["pair_id"],
        "policy":identity["policy"],
        "source_sha256":m["source"]["sha256"],
        "world_sha256":m["world_sha256"],
        "genome_sha256":sha256(json.dumps(
            m["genome"],sort_keys=True,separators=(",",":")).encode()).hexdigest(),
        "life_seed":m["life_seed"],
    }


def _invariants(fingerprint):
    def check(identity,life):
        ca=life["cognitive_accounting"]
        r=life["admission_receipt"]
        m=life["manifest"]
        content=identity["policy"]==POLICIES[1]
        observed=m.get("experimental_policy",{}).get("name")
        checks={
            "energy_paid":ca["totals"]["energy"]["unpaid"]<=1e-12,
            "vigilance_paid":ca["totals"]["vigilance"]["unpaid"]<=1e-12,
            "no_shortfall":ca["shortfall_steps"]==0,
            "settled":ca["status"]=="SETTLED_FOR_DECLARED_WORK",
            "terminal":life["terminal"] in ("dead","censored"),
            "within_horizon":type(life["steps_lived"]) is int
                             and 1<=life["steps_lived"]<=HORIZON,
            "censored_at_horizon":life["terminal"]!="censored" or
                                  life["steps_lived"]==HORIZON,
            "exact_policy":observed==identity["policy"],
            "gate_present":"replay_gate" in life,
            "cohort":r["cohort"]=="engineering",
            "index_family":r["index"]==identity["index"] and
                           r["family"]==identity["family"],
            "world_binding":r["world_seed"]==identity["world_seed"] and
                            r["world_sha256"]==m["world_sha256"] and
                            r["world_name"]==life["world"],
            "source_binding":r["transport_fingerprint"]==fingerprint,
            "life_seed":m["life_seed"]==identity["life_seed"],
            "gate_count_rule":life["replay_gate"]["mode"]==
                ("gate_random_content" if content else "gate"),
        }
        if content:
            record=life["replay_gate"].get("random_content",{})
            ordinal=record.get("lived_sleep_ordinals")
            opp=record.get("paid_replay_opportunities")
            paid=record.get("selected_replays_paid")
            diff=record.get("distinct_from_priority_subsets")
            valid=all(type(x) is int and x>=0
                      for x in (ordinal,opp,paid,diff))
            checks.update({
                "random_content_receipt":valid,
                "actual_content_replays_paid":valid and
                    paid==ca["replays_executed"],
                "content_subset_bounds":valid and
                    0<=diff<=opp<=ordinal<=life["actions"].get("dormir",0),
                "content_payment_bounded":valid and
                    opp<=paid<=16*opp,
                "historical_gate_count_preserved":
                    record.get("count_rule")=="EXACT_ORIGINAL_GATE",
            })
        else:
            checks["no_random_content_receipt"]=(
                "random_content" not in life["replay_gate"])
        return checks
    return check


def rehearse():
    scheduled=cases()
    fingerprint=SOURCE.source_fingerprint()
    report=TP.sealed_rehearsal(scheduled,_run_case(scheduled,fingerprint),
                               _reduce_structural,_invariants(fingerprint))
    report.update({
        "runner":SCHEMA,"protocol":PROTOCOL,
        "cohort":COHORT,"pair_count":PAIRS,
        "policies":list(POLICIES),
        "source_fingerprint":fingerprint,
        "no_world_outcomes_published":True,
        "originals_temporary_only":True,
        "scientific_lives":0,"scientific_verdict":"NOT_ISSUED",
        "scientific_registration":False,
    })
    return report


def execute(*args,**kwargs):
    raise PermissionError("new scientific replay-content cohort not admitted")


def main(argv=None):
    argv=sys.argv if argv is None else argv
    if len(argv)!=2 or argv[1]!="rehearse":
        raise SystemExit("usage: python -m i3.lab.stage2_replay_content_engineering rehearse")
    print(json.dumps(rehearse(),sort_keys=True,indent=2))


if __name__=="__main__":
    main()
