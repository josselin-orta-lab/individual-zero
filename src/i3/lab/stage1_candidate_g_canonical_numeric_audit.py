"""Declared Candidate-G canonical numerical-semantics audit.

Protocol: docs/STAGE1_CANDIDATE_G_CANONICAL_NUMERIC_AUDIT.md.
No World, life, runtime mode or changed work accounting.
"""
from __future__ import annotations

from dataclasses import asdict
import json
import sys

from . import projection_end_to_end_numeric_oracle as O
from . import stage1_candidate_g_projection_dependence as D
from . import stage1_candidate_g_reference_recurrence_falsifier as G
from ..modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from ..modules.forecast_work import projection_simulated_steps_ceiling
from ..modules.genome import midpoint
from ..modules.mind import Mind, W
from ..modules.water_recurrence_opportunity import (
    paid_water_personal_recurrence_value,
)

SCHEMA = "i3-stage1-candidate-g-canonical-numeric-audit/v1"
PER_STEP = (1,) * 255


class CanonicalHighPrecisionMind(Mind):
    """Reference Candidate-G mind with authorized Decimal end-to-end semantics."""

    def __init__(self):
        super().__init__(midpoint(), 197)
        self.proj_chunks = PER_STEP
        self.projection_accounting = "chunk_end"

    def simulate(self, body, plan, horizon, budget):
        return O.simulate_end_to_end(self, body, plan, horizon, budget)


def make_high_precision_mind():
    mind = CanonicalHighPrecisionMind()
    mind.map = {}
    mind.effects.observe(
        ("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    mind.effects.observe(
        ("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(
        ("dormir",), (3., -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    if projection_simulated_steps_ceiling(mind) != 255:
        raise RuntimeError("canonical oracle must retain 255-unit forecast")
    return mind


def _selected(rows):
    return [
        row for row in rows
        if "TRIAL" in row["target_choices"]
        and row["information_value"] > 1e-12
        and row["trial_advantage"] > 1e-12
    ]


def _key(row):
    return (
        row["channel"],
        float(row["level"]),
        int(row["horizon"]),
    )


def _mean_work(rows):
    keys = ("cycles", "simulated_steps", "memory_items", "replays")
    return {
        key: sum(row["work"][key] for row in rows) / len(rows)
        for key in keys
    }


def _max_work(rows):
    keys = ("cycles", "simulated_steps", "memory_items", "replays")
    return {
        key: max(row["work"][key] for row in rows)
        for key in keys
    }


def evaluate_high_precision():
    recurrence = G.recurrence_2_6_10()
    memory = G.effect_memory()
    rows = []

    for channel, channel_name in enumerate(G.CHANNEL_NAMES):
        for level in G.LEVELS:
            body = list(G.BASE_BODY)
            body[channel] = level
            body = tuple(body)
            for horizon in G.HORIZONS:
                mind = make_high_precision_mind()
                budget = CognitiveBudget(body, BodyLaws())
                result = paid_water_personal_recurrence_value(
                    mind, memory, recurrence,
                    G.EXPLORE, G.ORDINARY, horizon, budget)
                for key, value in result["work"].items():
                    if value > result["forecast_work_ceiling"][key]:
                        raise RuntimeError(
                            "canonical oracle work exceeded common ceiling")
                rows.append({
                    "channel": channel_name,
                    "channel_index": channel,
                    "level": level,
                    "horizon": horizon,
                    "information_value": result[
                        "trial_information_value"],
                    "trial_advantage": result["trial_advantage"],
                    "target_choices": list(
                        result["target_node_best_choices"]),
                    "work": dict(result["work"]),
                    "forecast_work_ceiling": dict(
                        result["forecast_work_ceiling"]),
                })
    return rows


def _summary(rows):
    selected = _selected(rows)
    return {
        "evaluated": len(rows),
        "selected_epistemic": len(selected),
        "selected_water_deficit": sum(
            row["channel_index"] == W for row in selected),
        "selected_other_deficit": sum(
            row["channel_index"] != W for row in selected),
        "declined": sum(
            row["target_choices"] == ["DECLINE_TRIAL"]
            for row in rows),
        "selected_states": [
            {
                "channel": row["channel"],
                "level": row["level"],
                "horizon": row["horizon"],
                "information_value": row["information_value"],
                "trial_advantage": row["trial_advantage"],
            }
            for row in selected
        ],
        "mean_work": _mean_work(rows),
        "max_work": _max_work(rows),
        "actual_work_ceiling_violations": (
            sum(
                any(
                    row["work"][key] > row["forecast_work_ceiling"][key]
                    for key in row["work"])
                for row in rows)
            if all("forecast_work_ceiling" in row for row in rows)
            else None),
    }


def _state_map(rows):
    return {_key(row): row for row in rows}


def _set_diff(a, b):
    return [
        {"channel": key[0], "level": key[1], "horizon": key[2]}
        for key in sorted(a - b)
    ]


def run(out_path):
    historical_rows, historical_existing = D.evaluate("per_step")
    candidate_f_rows, candidate_f_existing = D.evaluate(
        "candidate_f_projection")
    canonical_rows = evaluate_high_precision()

    historical = _summary(historical_rows)
    canonical = _summary(canonical_rows)
    candidate_f = _summary(candidate_f_rows)

    historical_set = {_key(row) for row in _selected(historical_rows)}
    canonical_set = {_key(row) for row in _selected(canonical_rows)}
    candidate_f_set = {_key(row) for row in _selected(candidate_f_rows)}

    historical_water = {
        key for key in historical_set if key[0] == "water"}
    canonical_water = {
        key for key in canonical_set if key[0] == "water"}
    candidate_f_water = {
        key for key in candidate_f_set if key[0] == "water"}

    hm = _state_map(historical_rows)
    cm = _state_map(canonical_rows)
    max_info_diff = 0.0
    max_adv_diff = 0.0
    worst_info = None
    worst_adv = None
    for key in hm:
        info = abs(
            hm[key]["information_value"] - cm[key]["information_value"])
        adv = abs(
            hm[key]["trial_advantage"] - cm[key]["trial_advantage"])
        if info > max_info_diff:
            max_info_diff = info
            worst_info = key
        if adv > max_adv_diff:
            max_adv_diff = adv
            worst_adv = key

    if not canonical_water:
        classification = "HISTORICAL_WATER_SELECTIONS_NUMERIC_ARTIFACT"
    elif canonical_water == historical_water:
        classification = "WATER_SELECTIONS_SURVIVE_CANONICAL_NUMERICS"
    else:
        classification = "MIXED_WATER_NUMERIC_SEMANTICS"

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_CANDIDATE_G_CANONICAL_NUMERIC_AUDIT.md",
        "world_access": False,
        "lives": 0,
        "arms": {
            "historical_float_per_step": historical,
            "canonical_high_precision_per_step": canonical,
            "candidate_f_projection": candidate_f,
        },
        "historical_existing_summary": historical_existing,
        "candidate_f_existing_summary": candidate_f_existing,
        "historical_vs_canonical": {
            "selected_only_historical": _set_diff(
                historical_set, canonical_set),
            "selected_only_canonical": _set_diff(
                canonical_set, historical_set),
            "water_only_historical": _set_diff(
                historical_water, canonical_water),
            "water_only_canonical": _set_diff(
                canonical_water, historical_water),
            "max_information_value_difference": max_info_diff,
            "max_information_difference_state": (
                None if worst_info is None else
                {"channel": worst_info[0],
                 "level": worst_info[1],
                 "horizon": worst_info[2]}),
            "max_trial_advantage_difference": max_adv_diff,
            "max_trial_advantage_difference_state": (
                None if worst_adv is None else
                {"channel": worst_adv[0],
                 "level": worst_adv[1],
                 "horizon": worst_adv[2]}),
        },
        "canonical_vs_candidate_f": {
            "selected_overlap": len(
                canonical_set & candidate_f_set),
            "selected_only_canonical": _set_diff(
                canonical_set, candidate_f_set),
            "selected_only_candidate_f": _set_diff(
                candidate_f_set, canonical_set),
            "water_overlap": len(
                canonical_water & candidate_f_water),
            "water_only_canonical": _set_diff(
                canonical_water, candidate_f_water),
            "water_only_candidate_f": _set_diff(
                candidate_f_water, canonical_water),
        },
        "classification": classification,
        "historical_gates_changed": False,
        "candidate_promoted": False,
        "runtime_integration_authorized": False,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    rep = run(sys.argv[1])
    print("CANDIDATE_G_CANONICAL_NUMERIC_AUDIT " + json.dumps({
        "classification": rep["classification"],
        "arms": {
            name: {
                key: arm[key]
                for key in (
                    "evaluated", "selected_epistemic",
                    "selected_water_deficit",
                    "selected_other_deficit", "declined",
                    "mean_work", "max_work",
                    "actual_work_ceiling_violations")
            }
            for name, arm in rep["arms"].items()
        },
        "historical_vs_canonical":
            rep["historical_vs_canonical"],
        "canonical_vs_candidate_f":
            rep["canonical_vs_candidate_f"],
    }, sort_keys=True))
