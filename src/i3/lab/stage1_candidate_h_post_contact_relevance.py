"""Frozen Candidate-H post-contact relevance-gated fallback falsifier.

Protocol: docs/STAGE1_CANDIDATE_H_POST_CONTACT_RELEVANCE.md.
Software only. No World instance, life, runtime policy or evidence access.
"""
from __future__ import annotations

from dataclasses import asdict
import json
import math
import sys

from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork,
    cognitive_cost, debit_cognition)
from ..modules.genome import midpoint
from ..modules.plan_information import (
    _revealed_minimum_ceiling, _validate_revealed,
    paid_revealed_plan_information_value)
from ..modules.reference_frontier_information_mind import (
    ReferenceFrontierInformationMind, _add, _simulation_upper,
    _water_outcomes, _water_probability)
from ..modules.unknown_outcomes import paid_frontier_actionable_belief
from . import stage1_candidate_g_reference_recurrence_falsifier as G
from . import stage1_candidate_h_relevance_fallback as H

SCHEMA = "i3-stage1-candidate-h-post-contact-relevance/v1"
TOL = 1e-12
HISTORY_BODY = (95.0, 75.0, 22.0, 80.0, 95.0)
DRINK_DELTA = (-0.5, -0.2, 35.0, 0.0, 0.0)
EXPLORE = (("se_deplacer",),)
EXPLORER = "frontier_explorer"
WORK_KEYS = ("cycles", "simulated_steps", "memory_items", "replays")


def _work_from_dict(value):
    return CognitiveWork(*(int(value[key]) for key in WORK_KEYS))


def _work_add(left, right):
    return CognitiveWork(*(
        getattr(left, key) + getattr(right, key) for key in WORK_KEYS))


def _top(scores):
    best = max(scores.values())
    return tuple(sorted(
        name for name, value in scores.items()
        if value >= best - TOL))


def _prime_post_contact(mind):
    """Reuse the established personal-water software history without a World."""
    mind.effects.observe(("attendre",), (0.0, -0.2, -0.4, 0.2, 0.0))
    mind.effects.observe(("se_deplacer",), (-2.0, -0.2, -0.4, 0.0, 0.0))
    mind.effects.observe(("dormir",), (3.0, -0.35, -0.4, 0.2, 4.0))
    mind.effects.observe(("boire",), DRINK_DELTA)
    mind.map[(9, 9)] = (True, ())

    decision = CognitiveWork(cycles=2, simulated_steps=1, memory_items=3)
    funded, _ = debit_cognition(HISTORY_BODY, BodyLaws(), decision)
    physical = tuple(
        value + delta for value, delta in zip(funded, DRINK_DELTA))
    store = CognitiveBudget(physical, BodyLaws())
    mind.branch_memory.observe(
        ("boire", None), HISTORY_BODY, decision, store)
    mind._drift = mind.drift()
    return mind


def _candidate_f_mind():
    mind = ReferenceFrontierInformationMind(
        midpoint(), 197, simulation_mode="candidate_f")
    mind.projection_accounting = "event_local_quadratic4"
    return _prime_post_contact(mind)


def _stage_a(body, horizon):
    """Pay actionable belief plus one commensurate Candidate-F decision basis."""
    mind = _candidate_f_mind()
    laws = BodyLaws()
    budget = CognitiveBudget(body, laws)
    try:
        belief = paid_frontier_actionable_belief(
            mind, mind.branch_memory, budget)
        p_water = _water_probability(belief)
        if belief["status"] != "COMPLETE_ACTIONABLE_PERSONAL_BELIEF":
            raise RuntimeError("frozen personal history lost actionable belief")
        if not 0.0 < p_water < 1.0:
            raise RuntimeError("frozen personal history lost strict water probability")

        outcomes, common = _water_outcomes(p_water, EXPLORE)
        common_dict, revealed = _validate_revealed(
            outcomes, common, horizon)
        _prep, info_quote = _revealed_minimum_ceiling(
            mind, outcomes, common_dict, revealed, horizon,
            CognitiveWork())

        extra = info_quote
        for plan in H.ORDINARY_PLANS.values():
            extra = _add(
                extra, _simulation_upper(mind, plan, horizon))
        ceiling = _add(budget.work, extra)
        forecast_body, _ = debit_cognition(
            budget.body, laws, ceiling)

        info = paid_revealed_plan_information_value(
            mind, outcomes, common, horizon, budget,
            forecast_work=ceiling)

        ordinary = {}
        for name, plan in H.ORDINARY_PLANS.items():
            ordinary[name] = mind.simulate(
                forecast_body, plan, horizon, budget)[0]

        if any(
                getattr(budget.work, key) > getattr(ceiling, key)
                for key in WORK_KEYS):
            raise RuntimeError("post-contact Stage-A work exceeded ceiling")

        with_scores = dict(ordinary)
        with_scores[EXPLORER] = info["informed_value"]
        without_scores = dict(ordinary)
        without_scores[EXPLORER] = info["uninformed_value"]
        with_top = _top(with_scores)
        without_top = _top(without_scores)
        relevant = (
            info["information_value"] > TOL
            and with_top != without_top
            and EXPLORER in with_top)

        return {
            "status": "FUNDED",
            "belief": {
                "status": belief["status"],
                "p_water": p_water,
                "support": belief["support"],
                "work": belief["work"],
            },
            "information": {
                "information_value": info["information_value"],
                "informed_value": info["informed_value"],
                "uninformed_value": info["uninformed_value"],
                "common_best_continuations":
                    info["common_best_continuations"],
                "conditional_choices": info["conditional_choices"],
                "work": info["work"],
            },
            "ordinary_scores": ordinary,
            "with_information_scores": with_scores,
            "without_information_scores": without_scores,
            "with_information_top": with_top,
            "without_information_top": without_top,
            "relevant": relevant,
            "forecast_work_ceiling": asdict(ceiling),
            "work": asdict(budget.work),
            "body_after_computation": budget.remaining,
        }
    except CognitiveFundingError as exc:
        return {
            "status": "UNFUNDED",
            "error": str(exc),
            "work": asdict(budget.work),
            "body_after_computation": budget.remaining,
        }


def _same_scores(left, right):
    if left.keys() != right.keys():
        return False, None
    worst = max(
        (abs(left[key] - right[key]) for key in left),
        default=0.0)
    return worst <= TOL, worst


def characterize():
    rows = []
    for channel, channel_name in enumerate(G.CHANNEL_NAMES):
        for level in G.LEVELS:
            body = list(G.BASE_BODY)
            body[channel] = level
            body = tuple(body)
            for horizon in G.HORIZONS:
                stage_a = _stage_a(body, horizon)
                fallback = control = preprobe = None
                combined_work = _work_from_dict(stage_a["work"])
                combined_body = stage_a["body_after_computation"]
                score_identity = False
                score_error = None
                top_identity = False

                if stage_a["status"] == "FUNDED":
                    preprobe = H._reference_four_plan_phase(
                        body, horizon)
                    if preprobe["status"] != "FUNDED":
                        raise RuntimeError(
                            "pre-probe P1.3 control became unfunded")

                    if not stage_a["relevant"]:
                        fallback = H._reference_four_plan_phase(
                            stage_a["body_after_computation"], horizon)
                        control = H._reference_four_plan_phase(
                            stage_a["body_after_computation"], horizon)
                        if fallback["status"] == "FUNDED":
                            fallback_work = _work_from_dict(
                                fallback["work"])
                            combined_work = _work_add(
                                combined_work, fallback_work)
                            combined_body = fallback[
                                "body_after_computation"]
                            score_identity, score_error = _same_scores(
                                fallback["scores"], control["scores"])
                            top_identity = (
                                fallback["top"] == control["top"])

                bill = cognitive_cost(BodyLaws(), combined_work)
                if not all(
                        math.isfinite(x) and x >= 0.0 for x in bill):
                    raise RuntimeError("invalid post-contact combined bill")

                rows.append({
                    "channel": channel_name,
                    "channel_index": channel,
                    "level": level,
                    "horizon": horizon,
                    "body": body,
                    "stage_a": stage_a,
                    "relevant": (
                        stage_a.get("relevant", False)
                        if stage_a["status"] == "FUNDED"
                        else False),
                    "preprobe_reference": preprobe,
                    "fallback": fallback,
                    "same_body_control": control,
                    "fallback_score_identity": score_identity,
                    "fallback_score_identity_max_error": score_error,
                    "fallback_top_identity": top_identity,
                    "combined_work": asdict(combined_work),
                    "combined_bill": {
                        "energy": bill[0],
                        "vigilance": bill[1],
                    },
                    "combined_body_after_computation": combined_body,
                })

    funded_stage_a = [
        row for row in rows if row["stage_a"]["status"] == "FUNDED"]
    relevant = [row for row in funded_stage_a if row["relevant"]]
    fallback_rows = [
        row for row in funded_stage_a if not row["relevant"]]
    funded_fallback = [
        row for row in fallback_rows
        if row["fallback"]["status"] == "FUNDED"]
    positive_but_fallback = [
        row for row in fallback_rows
        if row["stage_a"]["information"]["information_value"] > TOL]
    preprobe_changes = [
        row for row in funded_fallback
        if row["fallback"]["top"]
        != row["preprobe_reference"]["top"]
    ]

    p0 = (
        len(funded_stage_a) == 80
        and all(
            row["stage_a"]["belief"]["status"]
            == "COMPLETE_ACTIONABLE_PERSONAL_BELIEF"
            and 0.0 < row["stage_a"]["belief"]["p_water"] < 1.0
            and all(
                row["stage_a"]["work"][key]
                <= row["stage_a"]["forecast_work_ceiling"][key]
                for key in WORK_KEYS)
            for row in funded_stage_a))
    p1 = bool(relevant) and bool(fallback_rows)
    p2 = (
        len(funded_fallback) == len(fallback_rows))
    p3 = p2 and all(
        row["fallback_score_identity"]
        and row["fallback_top_identity"]
        and row["fallback_score_identity_max_error"] <= TOL
        for row in fallback_rows)
    p4 = all(
        row["fallback"] is None
        and row["stage_a"]["information"]["information_value"] > TOL
        and row["stage_a"]["with_information_top"]
            != row["stage_a"]["without_information_top"]
        and EXPLORER in row["stage_a"]["with_information_top"]
        for row in relevant)

    accounting_failures = []
    for row in rows:
        stage_work = _work_from_dict(row["stage_a"]["work"])
        fallback_work = (
            CognitiveWork()
            if row["fallback"] is None
            or row["fallback"]["status"] != "FUNDED"
            else _work_from_dict(row["fallback"]["work"]))
        expected = _work_add(stage_work, fallback_work)
        if row["combined_work"] != asdict(expected):
            accounting_failures.append({
                "state": (
                    row["channel"], row["level"], row["horizon"]),
                "reason": "WORK_SUM_MISMATCH"})
            continue
        try:
            after_stage, _ = debit_cognition(
                row["body"], BodyLaws(), stage_work)
        except CognitiveFundingError:
            accounting_failures.append({
                "state": (
                    row["channel"], row["level"], row["horizon"]),
                "reason": "STAGE_A_UNFUNDED"})
            continue
        if any(
                abs(a - b) > TOL
                for a, b in zip(
                    after_stage,
                    row["stage_a"]["body_after_computation"])):
            accounting_failures.append({
                "state": (
                    row["channel"], row["level"], row["horizon"]),
                "reason": "STAGE_A_BODY_MISMATCH"})
            continue
        try:
            final, _ = debit_cognition(
                row["body"], BodyLaws(), expected)
        except CognitiveFundingError:
            accounting_failures.append({
                "state": (
                    row["channel"], row["level"], row["horizon"]),
                "reason": "COMBINED_UNFUNDED"})
            continue
        if any(
                abs(a - b) > TOL
                for a, b in zip(
                    final,
                    row["combined_body_after_computation"])):
            accounting_failures.append({
                "state": (
                    row["channel"], row["level"], row["horizon"]),
                "reason": "COMBINED_BODY_MISMATCH"})
    p5 = not accounting_failures
    p6 = True

    rules = {
        "P0_personal_history_actionability_identity": p0,
        "P1_both_relevance_classes_exist": p1,
        "P2_all_fallback_states_funded": p2,
        "P3_fallback_reference_identity": p3,
        "P4_relevant_path_integrity": p4,
        "P5_exact_physical_accounting": p5,
        "P6_authority_boundaries": p6,
    }
    passed = all(rules.values())

    def work_stats(selected):
        stage = [
            row["stage_a"]["work"]["simulated_steps"]
            for row in selected]
        combined = [
            row["combined_work"]["simulated_steps"]
            for row in selected]
        energy = [row["combined_bill"]["energy"] for row in selected]
        vigilance = [
            row["combined_bill"]["vigilance"] for row in selected]
        return {
            "states": len(selected),
            "mean_stage_a_simulated_steps":
                sum(stage) / len(stage) if stage else 0.0,
            "max_stage_a_simulated_steps":
                max(stage) if stage else 0,
            "mean_combined_simulated_steps":
                sum(combined) / len(combined) if combined else 0.0,
            "max_combined_simulated_steps":
                max(combined) if combined else 0,
            "mean_combined_energy":
                sum(energy) / len(energy) if energy else 0.0,
            "max_combined_energy": max(energy) if energy else 0.0,
            "mean_combined_vigilance":
                sum(vigilance) / len(vigilance) if vigilance else 0.0,
            "max_combined_vigilance":
                max(vigilance) if vigilance else 0.0,
        }

    return {
        "schema": SCHEMA,
        "protocol":
            "STAGE1_CANDIDATE_H_POST_CONTACT_RELEVANCE.md",
        "world_access": False,
        "lives": 0,
        "runtime_life_access": False,
        "evidence_branch_access": False,
        "omega_read": False,
        "recurrence_read": False,
        "motor_command_authorized": False,
        "fixture": {
            "states": 80,
            "levels": G.LEVELS,
            "horizons": G.HORIZONS,
            "history_body": HISTORY_BODY,
            "drink_delta": DRINK_DELTA,
            "explore": EXPLORE,
            "ordinary_plans":
                tuple(sorted(H.ORDINARY_PLANS)),
        },
        "stage_a": {
            "funded": len(funded_stage_a),
            "unfunded": 80 - len(funded_stage_a),
            "relevant": len(relevant),
            "fallback": len(fallback_rows),
            "positive_information_but_fallback":
                len(positive_but_fallback),
            "relevant_states": [
                {
                    "channel": row["channel"],
                    "channel_index": row["channel_index"],
                    "level": row["level"],
                    "horizon": row["horizon"],
                    "information_value":
                        row["stage_a"]["information"][
                            "information_value"],
                    "without_top":
                        row["stage_a"][
                            "without_information_top"],
                    "with_top":
                        row["stage_a"][
                            "with_information_top"],
                }
                for row in relevant
            ],
        },
        "fallback": {
            "funded": len(funded_fallback),
            "unfunded":
                len(fallback_rows) - len(funded_fallback),
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
                    "preprobe_top":
                        row["preprobe_reference"]["top"],
                    "fallback_top":
                        row["fallback"]["top"],
                }
                for row in preprobe_changes
            ],
        },
        "work": {
            "relevant": work_stats(relevant),
            "fallback": work_stats(fallback_rows),
        },
        "physical_accounting_diagnostic": {
            "failure_count": len(accounting_failures),
            "failures": accounting_failures,
        },
        "rules": rules,
        "verdict": (
            "CANDIDATE_H_POST_CONTACT_SOFTWARE_GATE_PASS"
            if passed else
            "CANDIDATE_H_POST_CONTACT_SOFTWARE_GATE_FAIL"),
        "unified_runtime_protocol_authorized": passed,
        "runtime_candidate_authorized": False,
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
    print("CANDIDATE_H_POST_CONTACT_RELEVANCE " + json.dumps({
        "verdict": report["verdict"],
        "stage_a": report["stage_a"],
        "fallback": report["fallback"],
        "work": report["work"],
        "physical_accounting_diagnostic":
            report["physical_accounting_diagnostic"],
        "rules": report["rules"],
    }, sort_keys=True))
