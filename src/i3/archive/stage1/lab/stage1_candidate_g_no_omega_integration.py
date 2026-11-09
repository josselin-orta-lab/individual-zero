"""Frozen software integration gate for personal-recurrence Candidate-G.

Protocol: docs/STAGE1_CANDIDATE_G_NO_OMEGA_INTEGRATION.md.
No World, life or runtime registration.
"""
from __future__ import annotations

import json
import sys

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork, W
from i3.modules.genome import midpoint, validate
from i3.archive.stage1.modules.personal_recurrence_candidate_g_mind import (
    PersonalRecurrenceCandidateGMind)
from i3.modules.water_recurrence_opportunity import (
    paid_water_personal_recurrence_value)
from i3.archive.stage1.lab import stage1_candidate_g_reference_recurrence_falsifier as G

SCHEMA = "i3-stage1-candidate-g-no-omega-integration/v1"
BODY = (100., 80., 30., 80., 100.)
BASE = (50., 50., 50., 50., 50.)


def genome(omega):
    g = midpoint()
    g["genes"]["omega"] = omega
    validate(g)
    return g


def cap(body=BODY):
    return {
        "body": body,
        "here": (False, ()),
        "neighbors": ((False, ()), None, None, None),
        "inventory": (),
    }


def _record(memory, key, delta):
    after = tuple(a + b for a, b in zip(BASE, delta))
    memory.observe(
        key, BASE, CognitiveWork(),
        CognitiveBudget(after, BodyLaws()))


def prime_generic(mind):
    for effect_key, branch_key, delta in (
        (("se_deplacer",), ("se_deplacer", None), (-2., -.2, -.4, 0., 0.)),
        (("attendre",), ("attendre", None), (-.35, -.2, -.4, .2, 0.)),
        (("dormir",), ("dormir", None), (3., -.35, -.4, 0., 4.)),
    ):
        mind.effects.observe(effect_key, delta)
        _record(mind.branch_memory, branch_key, delta)
    mind._drift = mind.drift()


def prime_personal_drink(mind, delta=(-.5, -.2, 35., 0., 0.)):
    mind.effects.observe(("boire",), delta)
    _record(mind.branch_memory, ("boire", None), delta)
    mind.map[(9, 9)] = (True, ())


def prime_recurrence(mind):
    mind.opportunity_memory = G.recurrence_2_6_10()


def make_mind(omega=0.0, seed=197, *, observer=False):
    mind = PersonalRecurrenceCandidateGMind(
        genome(omega), seed,
        observer_decision_diagnostics=observer)
    prime_generic(mind)
    return mind


def decision_fixture(*, recurrence=False, drink=False, omega=0.0):
    mind = make_mind(omega, 211, observer=True)
    if recurrence:
        prime_recurrence(mind)
    if drink:
        prime_personal_drink(mind)
    before = (mind.simulation_mode, mind.projection_accounting)
    result = mind.decide(cap(), CognitiveBudget(BODY, BodyLaws()))
    after = (mind.simulation_mode, mind.projection_accounting)
    info = result[3]
    witnesses = info.get("observer", {}).get("score_witness", [])
    modes = sorted(set(
        row.get("decision_projection_mode") for row in witnesses))
    omega_fields = sorted(set(
        key for row in witnesses for key in row if "omega" in key))
    return {
        "result": result,
        "before_mode": before,
        "after_mode": after,
        "frontier_phase": info.get("frontier_phase"),
        "decision_projection_mode": info.get("decision_projection_mode"),
        "recurrence_status": info.get("personal_recurrence_status"),
        "recurrence_probability": info.get("personal_recurrence_probability"),
        "score_modes": modes,
        "omega_witness_fields": omega_fields,
        "work": {
            "cycles": result[2].cycles,
            "simulated_steps": result[2].simulated_steps,
            "memory_items": result[2].memory_items,
            "replays": result[2].replays,
        },
        "funding": info.get("funding"),
        "option": info.get("option"),
    }


def kernel_mind():
    mind = make_mind(0.0, 197)
    mind.branch_memory = G.effect_memory()
    mind.opportunity_memory = G.recurrence_2_6_10()
    return mind


def evaluate_kernel():
    rows = []
    for channel, name in enumerate(G.CHANNEL_NAMES):
        for level in G.LEVELS:
            body = list(G.BASE_BODY)
            body[channel] = level
            body = tuple(body)
            for horizon in G.HORIZONS:
                mind = kernel_mind()
                budget = CognitiveBudget(body, BodyLaws())
                with mind.candidate_f_projection():
                    result = paid_water_personal_recurrence_value(
                        mind, mind.branch_memory, mind.opportunity_memory,
                        G.EXPLORE, G.ORDINARY, horizon, budget)
                if (mind.simulation_mode, mind.projection_accounting) != (
                        "reference", "chunk_end"):
                    raise RuntimeError("kernel projector leaked after context")
                for key, value in result["work"].items():
                    if value > result["forecast_work_ceiling"][key]:
                        raise RuntimeError("kernel work exceeded common ceiling")
                rows.append({
                    "channel": name,
                    "channel_index": channel,
                    "level": level,
                    "horizon": horizon,
                    "information_value": result["trial_information_value"],
                    "trial_advantage": result["trial_advantage"],
                    "target_choices": list(result["target_node_best_choices"]),
                    "work": dict(result["work"]),
                    "forecast_work_ceiling":
                        dict(result["forecast_work_ceiling"]),
                })

    selected = [
        row for row in rows
        if "TRIAL" in row["target_choices"]
        and row["information_value"] > 1e-12
        and row["trial_advantage"] > 1e-12
    ]
    keys = ("cycles", "simulated_steps", "memory_items", "replays")
    return rows, {
        "evaluated": len(rows),
        "selected_epistemic": len(selected),
        "selected_water_deficit": sum(
            row["channel_index"] == W for row in selected),
        "selected_other_deficit": sum(
            row["channel_index"] != W for row in selected),
        "declined": sum(
            row["target_choices"] == ["DECLINE_TRIAL"] for row in rows),
        "mean_work": {
            key: sum(row["work"][key] for row in rows) / len(rows)
            for key in keys},
        "max_work": {
            key: max(row["work"][key] for row in rows)
            for key in keys},
        "actual_work_ceiling_violations": sum(
            any(
                row["work"][key] > row["forecast_work_ceiling"][key]
                for key in keys)
            for row in rows),
    }


def run(out_path):
    no_support = decision_fixture(recurrence=False, omega=-1.0)
    supported_low = decision_fixture(recurrence=True, omega=-1.0)
    supported_high = decision_fixture(recurrence=True, omega=1.0)
    post_low = decision_fixture(drink=True, omega=-1.0)
    post_high = decision_fixture(drink=True, omega=1.0)
    _rows, kernel = evaluate_kernel()

    omega_invariant_first = (
        supported_low["result"] == supported_high["result"])
    omega_invariant_post = post_low["result"] == post_high["result"]

    rules = {
        "R0_no_first_contact_omega_attribute":
            not hasattr(make_mind(), "first_contact_omega"),
        "R1_persistent_mode_reference":
            all(fx["before_mode"] == ("reference", "chunk_end")
                and fx["after_mode"] == ("reference", "chunk_end")
                for fx in (
                    no_support, supported_low, supported_high,
                    post_low, post_high)),
        "R2_no_support_stays_reference":
            no_support["frontier_phase"]
            == "FIRST_CONTACT_NO_RECURRENCE_SUPPORT"
            and no_support["decision_projection_mode"] == "reference"
            and no_support["score_modes"] == ["reference"],
        "R3_recurrence_support_uses_candidate_f_for_all_scores":
            supported_low["frontier_phase"]
            == "FIRST_CONTACT_PERSONAL_RECURRENCE"
            and supported_low["decision_projection_mode"] == "candidate_f"
            and supported_low["score_modes"] == ["candidate_f"]
            and supported_low["recurrence_status"]
            == "COMPLETE_EMPIRICAL_RECURRENCE_ESTIMATE",
        "R4_first_contact_omega_invariant":
            omega_invariant_first
            and not supported_low["omega_witness_fields"]
            and not supported_high["omega_witness_fields"],
        "R5_post_contact_omega_invariant":
            omega_invariant_post
            and post_low["frontier_phase"] == "POST_CONTACT_PERSONAL"
            and post_low["decision_projection_mode"] == "candidate_f",
        "R6_recurrence_empty_at_birth":
            make_mind().opportunity_memory.snapshot()["gaps"]["water"] == (),
        "R7_kernel_canonical_counts":
            kernel["selected_epistemic"] == 24
            and kernel["selected_water_deficit"] == 0
            and kernel["selected_other_deficit"] == 24
            and kernel["declined"] == 40,
        "R8_kernel_mean_candidate_f_cost":
            abs(kernel["mean_work"]["simulated_steps"] - 470.05) <= 1e-9,
        "R9_kernel_common_ceiling_covers_actual":
            kernel["actual_work_ceiling_violations"] == 0,
    }
    passed = all(rules.values())

    # Results contain no object-bearing full tuples.
    def serial_fixture(fx):
        return {k: v for k, v in fx.items() if k != "result"}

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_CANDIDATE_G_NO_OMEGA_INTEGRATION.md",
        "world_access": False,
        "lives": 0,
        "fixtures": {
            "no_recurrence_support": serial_fixture(no_support),
            "recurrence_omega_minus1": serial_fixture(supported_low),
            "recurrence_omega_plus1": serial_fixture(supported_high),
            "post_contact_omega_minus1": serial_fixture(post_low),
            "post_contact_omega_plus1": serial_fixture(post_high),
        },
        "omega_invariance": {
            "first_contact": omega_invariant_first,
            "post_contact": omega_invariant_post,
        },
        "kernel": kernel,
        "rules": rules,
        "verdict": (
            "PERSONAL_RECURRENCE_CANDIDATE_G_INTEGRATION_PASS"
            if passed else
            "PERSONAL_RECURRENCE_CANDIDATE_G_INTEGRATION_FAIL"),
        "runtime_registered": False,
        "live_development_authorized": passed,
        "selection_validation_reserve_authorized": False,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    rep = run(sys.argv[1])
    print("PERSONAL_RECURRENCE_CANDIDATE_G_INTEGRATION " + json.dumps({
        "verdict": rep["verdict"],
        "rules": rep["rules"],
        "fixtures": rep["fixtures"],
        "kernel": rep["kernel"],
        "omega_invariance": rep["omega_invariance"],
    }, sort_keys=True))
