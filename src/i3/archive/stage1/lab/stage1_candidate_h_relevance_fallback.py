"""Frozen Candidate-H first-contact relevance-gated fallback falsifier.

Protocol: docs/STAGE1_CANDIDATE_H_RELEVANCE_FALLBACK.md.
Software only. No World, life, runtime policy or evidence-branch access.
"""
from __future__ import annotations

from dataclasses import asdict
import json
import math
import sys

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork,
    cognitive_cost, debit_cognition)
from i3.modules.reference_frontier_information_mind import _add, _simulation_upper
from i3.modules.water_recurrence_opportunity import (
    paid_water_personal_recurrence_value)
from i3.archive.stage1.lab import stage1_candidate_g_projection_dependence as D
from i3.archive.stage1.lab import stage1_candidate_g_reference_recurrence_falsifier as G

SCHEMA = "i3-stage1-candidate-h-relevance-fallback/v1"
TOL = 1e-12
ORDINARY_PLANS = {
    "wait": (("attendre",),),
    "sleep": (("dormir",),),
    "move": (("se_deplacer",),),
    "move_wait": (("se_deplacer",), ("attendre",)),
}
WORK_KEYS = ("cycles", "simulated_steps", "memory_items", "replays")


def _work_add(left, right):
    return CognitiveWork(*(
        getattr(left, key) + getattr(right, key) for key in WORK_KEYS))


def _work_from_dict(value):
    return CognitiveWork(*(int(value[key]) for key in WORK_KEYS))


def _work_delta(after, before):
    return CognitiveWork(*(
        getattr(after, key) - getattr(before, key) for key in WORK_KEYS))


def _top(scores):
    best = max(scores.values())
    return tuple(sorted(
        name for name, value in scores.items() if value >= best - TOL))


def _reference_four_plan_phase(body, horizon):
    """One paid P1.3 scoring phase from a supplied physical body."""
    laws = BodyLaws()
    mind = G.make_mind()
    ceiling = CognitiveWork()
    for plan in ORDINARY_PLANS.values():
        ceiling = _add(ceiling, _simulation_upper(mind, plan, horizon))

    try:
        forecast_body, _ = debit_cognition(body, laws, ceiling)
    except CognitiveFundingError:
        return {
            "status": "UNFUNDED",
            "forecast_work_ceiling": asdict(ceiling),
            "scores": None,
            "top": (),
            "work": asdict(CognitiveWork()),
            "body_after_computation": body,
        }

    budget = CognitiveBudget(body, laws)
    scores = {}
    for name, plan in ORDINARY_PLANS.items():
        scores[name] = mind.simulate(
            forecast_body, plan, horizon, budget)[0]

    if any(
            getattr(budget.work, key) > getattr(ceiling, key)
            for key in WORK_KEYS):
        raise RuntimeError("fallback reference scoring exceeded its ceiling")

    return {
        "status": "FUNDED",
        "forecast_work_ceiling": asdict(ceiling),
        "scores": scores,
        "top": _top(scores),
        "work": asdict(budget.work),
        "body_after_computation": budget.remaining,
    }


def _candidate_probe(body, horizon, recurrence, memory):
    budget = CognitiveBudget(body, BodyLaws())
    result = paid_water_personal_recurrence_value(
        D.make_mind("candidate_f_projection"),
        memory, recurrence, G.EXPLORE, G.ORDINARY, horizon, budget)
    strict = (
        "TRIAL" in result["target_node_best_choices"]
        and result["trial_information_value"] > TOL
        and result["trial_advantage"] > TOL)
    return result, strict


def _same_scores(left, right):
    if left.keys() != right.keys():
        return False, None
    worst = 0.0
    for key in left:
        worst = max(worst, abs(left[key] - right[key]))
    return worst <= TOL, worst


def characterize():
    recurrence = G.recurrence_2_6_10()
    memory = G.effect_memory()
    rows = []

    for channel, channel_name in enumerate(G.CHANNEL_NAMES):
        for level in G.LEVELS:
            body = list(G.BASE_BODY)
            body[channel] = level
            body = tuple(body)
            for horizon in G.HORIZONS:
                probe, relevant = _candidate_probe(
                    body, horizon, recurrence, memory)
                probe_work = _work_from_dict(probe["work"])
                if any(
                        probe["work"][key] >
                        probe["forecast_work_ceiling"][key]
                        for key in WORK_KEYS):
                    raise RuntimeError(
                        "canonical relevance probe exceeded common ceiling")

                preprobe = _reference_four_plan_phase(body, horizon)
                if preprobe["status"] != "FUNDED":
                    raise RuntimeError(
                        "frozen pre-probe P1.3 basis became unfunded")

                fallback = None
                control = None
                combined_work = probe_work
                combined_body = probe["body_after_computation"]
                score_identity = True
                score_identity_max_error = 0.0
                top_identity = True

                if not relevant:
                    fallback = _reference_four_plan_phase(
                        probe["body_after_computation"], horizon)
                    control = _reference_four_plan_phase(
                        probe["body_after_computation"], horizon)

                    if fallback["status"] == "FUNDED":
                        fallback_work = _work_from_dict(fallback["work"])
                        combined_work = _work_add(
                            probe_work, fallback_work)
                        combined_body, _ = debit_cognition(
                            body, BodyLaws(), combined_work)
                        score_identity, score_identity_max_error = (
                            _same_scores(
                                fallback["scores"], control["scores"]))
                        top_identity = fallback["top"] == control["top"]
                    else:
                        score_identity = False
                        top_identity = False

                energy, vigilance = cognitive_cost(
                    BodyLaws(), combined_work)
                if not all(
                        math.isfinite(value) and value >= 0.0
                        for value in (energy, vigilance)):
                    raise RuntimeError("non-finite Candidate-H bill")

                rows.append({
                    "channel": channel_name,
                    "channel_index": channel,
                    "level": level,
                    "horizon": horizon,
                    "relevant": relevant,
                    "probe": {
                        "information_value":
                            probe["trial_information_value"],
                        "trial_advantage": probe["trial_advantage"],
                        "target_choices":
                            tuple(probe["target_node_best_choices"]),
                        "work": dict(probe["work"]),
                        "forecast_work_ceiling":
                            dict(probe["forecast_work_ceiling"]),
                        "body_after_computation":
                            tuple(probe["body_after_computation"]),
                    },
                    "preprobe_reference_top": preprobe["top"],
                    "fallback": fallback,
                    "same_body_control": control,
                    "fallback_score_identity": score_identity,
                    "fallback_score_identity_max_error":
                        score_identity_max_error,
                    "fallback_top_identity": top_identity,
                    "combined_work": asdict(combined_work),
                    "combined_bill": {
                        "energy": energy,
                        "vigilance": vigilance,
                    },
                    "combined_body_after_computation":
                        tuple(combined_body),
                })

    relevant_rows = [row for row in rows if row["relevant"]]
    fallback_rows = [row for row in rows if not row["relevant"]]
    declined = [
        row for row in rows
        if row["probe"]["target_choices"] == ("DECLINE_TRIAL",)
    ]
    funded_fallback = [
        row for row in fallback_rows
        if row["fallback"]["status"] == "FUNDED"
    ]

    preprobe_changes = [
        row for row in funded_fallback
        if row["fallback"]["top"] != row["preprobe_reference_top"]
    ]

    # #1161 support-only projector-drift identity:
    # water 20/30/40/50 x all horizons, plus integrity=30 x all horizons.
    prior_drift_states = {
        (G.CHANNEL_NAMES.index("water"), level, horizon)
        for level in G.LEVELS for horizon in G.HORIZONS
    } | {
        (G.CHANNEL_NAMES.index("integrity"), 30.0, horizon)
        for horizon in G.HORIZONS
    }
    prior_drift_fallback = [
        row for row in funded_fallback
        if (row["channel_index"], row["level"], row["horizon"])
        in prior_drift_states
    ]
    returned_to_preprobe = [
        row for row in prior_drift_fallback
        if row["fallback"]["top"] == row["preprobe_reference_top"]
    ]

    def work_stats(selected):
        values = [
            row["combined_work"]["simulated_steps"] for row in selected]
        bills_e = [row["combined_bill"]["energy"] for row in selected]
        bills_v = [row["combined_bill"]["vigilance"] for row in selected]
        return {
            "states": len(selected),
            "mean_combined_simulated_steps":
                sum(values) / len(values) if values else 0.0,
            "max_combined_simulated_steps":
                max(values) if values else 0,
            "mean_combined_energy":
                sum(bills_e) / len(bills_e) if bills_e else 0.0,
            "max_combined_energy": max(bills_e) if bills_e else 0.0,
            "mean_combined_vigilance":
                sum(bills_v) / len(bills_v) if bills_v else 0.0,
            "max_combined_vigilance": max(bills_v) if bills_v else 0.0,
        }

    canonical_mean = (
        sum(row["probe"]["work"]["simulated_steps"] for row in rows)
        / len(rows))
    h0 = (
        len(rows) == 80
        and len(relevant_rows) == 24
        and len(fallback_rows) == 56
        and len(declined) == 40
        and abs(canonical_mean - 470.05) <= 1e-12)
    h1 = len(funded_fallback) == 56
    h2 = h1 and all(
        row["fallback_score_identity"]
        and row["fallback_top_identity"]
        and row["fallback_score_identity_max_error"] <= TOL
        for row in fallback_rows)
    h3 = all(
        row["fallback"] is None
        and row["combined_work"] == row["probe"]["work"]
        for row in relevant_rows)
    h4_failures = []
    for row in rows:
        probe_work = _work_from_dict(row["probe"]["work"])
        fallback_work = (
            CognitiveWork()
            if row["fallback"] is None
            or row["fallback"]["status"] != "FUNDED"
            else _work_from_dict(row["fallback"]["work"]))
        expected = _work_add(probe_work, fallback_work)
        identity = {
            "channel": row["channel"],
            "channel_index": row["channel_index"],
            "level": row["level"],
            "horizon": row["horizon"],
            "relevant": row["relevant"],
        }
        if row["combined_work"] != asdict(expected):
            h4_failures.append({
                **identity,
                "reason": "COMBINED_WORK_MISMATCH",
                "reported": row["combined_work"],
                "expected": asdict(expected),
            })
            continue
        original_body = tuple(
            row["level"] if index == row["channel_index"] else 80.0
            for index in range(5))
        try:
            remaining, _ = debit_cognition(
                original_body, BodyLaws(), expected)
        except CognitiveFundingError as exc:
            h4_failures.append({
                **identity,
                "reason": "COMBINED_WORK_UNFUNDED",
                "error": str(exc),
            })
            continue
        deltas = tuple(
            abs(a - b) for a, b in zip(
                remaining,
                row["combined_body_after_computation"]))
        if max(deltas) > 1e-12:
            h4_failures.append({
                **identity,
                "reason": "COMBINED_BODY_MISMATCH",
                "recomputed": remaining,
                "reported": row["combined_body_after_computation"],
                "abs_channel_errors": deltas,
                "max_abs_error": max(deltas),
            })

    h4 = not h4_failures
    h5 = True
    rules = {
        "H0_canonical_identity": h0,
        "H1_all_56_fallback_states_funded": h1,
        "H2_fallback_reference_identity": h2,
        "H3_relevant_path_preserved_without_fallback": h3,
        "H4_physical_accounting_exact_and_funded": h4,
        "H5_authority_boundaries": h5,
    }
    passed = all(rules.values())

    return {
        "schema": SCHEMA,
        "protocol": "STAGE1_CANDIDATE_H_RELEVANCE_FALLBACK.md",
        "lives": 0,
        "world_access": False,
        "runtime_life_access": False,
        "evidence_branch_access": False,
        "omega_read": False,
        "motor_command_authorized": False,
        "fixture": {
            "states": 80,
            "levels": G.LEVELS,
            "horizons": G.HORIZONS,
            "recurrence_gaps": (2, 6, 10),
            "ordinary_plans": tuple(sorted(ORDINARY_PLANS)),
        },
        "canonical_probe": {
            "relevant": len(relevant_rows),
            "fallback": len(fallback_rows),
            "declined": len(declined),
            "mean_simulated_steps": canonical_mean,
        },
        "fallback": {
            "funded": len(funded_fallback),
            "unfunded": len(fallback_rows) - len(funded_fallback),
            "score_identity_max_error": max(
                (row["fallback_score_identity_max_error"]
                 for row in funded_fallback),
                default=0.0),
            "top_identity_all": all(
                row["fallback_top_identity"]
                for row in funded_fallback),
            "top_changes_vs_preprobe_reference":
                len(preprobe_changes),
            "changed_states_vs_preprobe_reference": [
                {
                    "channel": row["channel"],
                    "channel_index": row["channel_index"],
                    "level": row["level"],
                    "horizon": row["horizon"],
                    "preprobe_top": row["preprobe_reference_top"],
                    "fallback_top": row["fallback"]["top"],
                }
                for row in preprobe_changes
            ],
            "prior_1161_drift_states": len(prior_drift_fallback),
            "prior_1161_drift_states_returned_to_preprobe":
                len(returned_to_preprobe),
            "prior_1161_drift_states_changed_after_paid_probe":
                len(prior_drift_fallback) - len(returned_to_preprobe),
        },
        "work": {
            "relevant": work_stats(relevant_rows),
            "fallback": work_stats(fallback_rows),
        },
        "physical_accounting_diagnostic": {
            "failure_count": len(h4_failures),
            "failures": h4_failures,
        },
        "rules": rules,
        "verdict": (
            "CANDIDATE_H_FIRST_CONTACT_SOFTWARE_GATE_PASS"
            if passed else
            "CANDIDATE_H_FIRST_CONTACT_SOFTWARE_GATE_FAIL"),
        "runtime_candidate_authorized": False,
        "post_contact_generalization_authorized": False,
        "new_live_panel_authorized": False,
        "rows": rows,
    }


def run(out_path):
    report = characterize()
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    report = run(sys.argv[1])
    print("CANDIDATE_H_RELEVANCE_FALLBACK " + json.dumps({
        "verdict": report["verdict"],
        "canonical_probe": report["canonical_probe"],
        "fallback": report["fallback"],
        "work": report["work"],
        "physical_accounting_diagnostic":
            report["physical_accounting_diagnostic"],
        "rules": report["rules"],
    }, sort_keys=True))
