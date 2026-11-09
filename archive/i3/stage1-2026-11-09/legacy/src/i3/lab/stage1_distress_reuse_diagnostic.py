"""Declared descriptive probe of exact distress-evaluation reuse.

Protocol: docs/STAGE1_DISTRESS_REUSE_DIAGNOSTIC.md.
No cognition, work accounting, World or life is changed.
"""
from __future__ import annotations

import json
import sys

from . import stage1_candidate_g_reference_recurrence_falsifier as G
from . import stage1_death_truncated_per_step as T
from ..modules.body import BodyLaws, CognitiveBudget
from ..modules.genome import midpoint
from ..modules.mind import W

SCHEMA = "i3-stage1-distress-reuse-diagnostic/v1"
CANDIDATE_F_MEAN_SIMULATED_STEPS = 470.0


class DistressReuseProbeMind(T.DeathTruncatedPerStepMind):
    """Observe only the feature tuples already evaluated by #1153."""

    def __init__(self, genome, life_seed):
        super().__init__(genome, life_seed)
        self._probe_in_project = False
        self._probe_current = None
        self.project_feature_calls = []

    def distress(self, features):
        if self._probe_in_project:
            self._probe_current.append(tuple(features))
        return super().distress(features)

    def project(self, body, drift, budget=None):
        if self._probe_in_project:
            raise RuntimeError("nested project probe")
        self._probe_in_project = True
        self._probe_current = []
        try:
            return super().project(body, drift, budget)
        finally:
            self.project_feature_calls.append(tuple(self._probe_current))
            self._probe_current = None
            self._probe_in_project = False


def make_mind():
    mind = DistressReuseProbeMind(midpoint(), 197)
    mind.map = {}
    mind.effects.observe(
        ("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    mind.effects.observe(
        ("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(
        ("dormir",), (3., -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    return mind


def _runs(seq):
    if not seq:
        return 0
    return 1 + sum(a != b for a, b in zip(seq, seq[1:]))


def evaluate_state(body, horizon):
    mind = make_mind()
    recurrence = G.recurrence_2_6_10()
    memory = G.effect_memory()
    budget = CognitiveBudget(body, BodyLaws())

    result = G.paid_water_personal_recurrence_value(
        mind, memory, recurrence,
        G.EXPLORE, G.ORDINARY, horizon, budget)

    feature_calls = mind.project_feature_calls
    projection = mind.projection_stats()
    total_feature_evals = sum(len(call) for call in feature_calls)
    consecutive_runs = sum(_runs(call) for call in feature_calls)
    unique_features = len({
        feature
        for call in feature_calls
        for feature in call
    })

    projection_paid = projection["paid_projection_steps"]
    death_endpoint_units = projection_paid - total_feature_evals
    if death_endpoint_units < 0:
        raise RuntimeError("distress evaluations exceed paid projection endpoints")

    actual_sim = result["work"]["simulated_steps"]
    nonprojection = actual_sim - projection_paid
    if nonprojection < 0:
        raise RuntimeError("projection work exceeds total simulated work")

    last_total = nonprojection + consecutive_runs + death_endpoint_units
    memo_total = nonprojection + unique_features + death_endpoint_units

    return {
        "body": body,
        "horizon": horizon,
        "target_choices": list(result["target_node_best_choices"]),
        "information_value": result["trial_information_value"],
        "trial_advantage": result["trial_advantage"],
        "actual_simulated_steps": actual_sim,
        "projection_paid_endpoints": projection_paid,
        "nonprojection_simulated_steps": nonprojection,
        "project_calls": len(feature_calls),
        "feature_evaluations": total_feature_evals,
        "consecutive_feature_runs": consecutive_runs,
        "unique_feature_tuples": unique_features,
        "death_endpoint_units": death_endpoint_units,
        "duplicates_consecutive_only": total_feature_evals - consecutive_runs,
        "duplicates_ideal_decision_memo": total_feature_evals - unique_features,
        "last_feature_reuse_total": last_total,
        "decision_memo_lower_total": memo_total,
        "max_features_in_one_project": max(
            (len(call) for call in feature_calls), default=0),
        "max_unique_features_live": unique_features,
        "projection_death_steps": list(projection["death_steps"]),
        "work_unchanged": dict(result["work"]),
        "forecast_work_ceiling": dict(result["forecast_work_ceiling"]),
    }


def run(out_path):
    rows = []
    for channel, channel_name in enumerate(G.CHANNEL_NAMES):
        for level in G.LEVELS:
            body = list(G.BASE_BODY)
            body[channel] = level
            body = tuple(body)
            for horizon in G.HORIZONS:
                row = evaluate_state(body, horizon)
                row["channel"] = channel_name
                row["channel_index"] = channel
                row["level"] = level
                rows.append(row)

    def mean(key):
        return sum(row[key] for row in rows) / len(rows)

    def maximum(key):
        return max(row[key] for row in rows)

    actual = mean("actual_simulated_steps")
    last = mean("last_feature_reuse_total")
    memo = mean("decision_memo_lower_total")

    if last <= CANDIDATE_F_MEAN_SIMULATED_STEPS:
        classification = "LAST_FEATURE_REUSE_PLAUSIBLE"
    elif memo <= CANDIDATE_F_MEAN_SIMULATED_STEPS:
        classification = "DECISION_LOCAL_FEATURE_MEMO_PLAUSIBLE"
    else:
        classification = "FEATURE_REUSE_INSUFFICIENT"

    selected = [
        row for row in rows
        if "TRIAL" in row["target_choices"]
        and row["information_value"] > 1e-12
        and row["trial_advantage"] > 1e-12
    ]

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_DISTRESS_REUSE_DIAGNOSTIC.md",
        "world_access": False,
        "lives": 0,
        "candidate_f_mean_simulated_steps": CANDIDATE_F_MEAN_SIMULATED_STEPS,
        "summary": {
            "evaluated": len(rows),
            "selected_epistemic": len(selected),
            "selected_water_deficit": sum(
                row["channel_index"] == W for row in selected),
            "actual_mean_simulated_steps": actual,
            "last_feature_reuse_mean_total": last,
            "decision_memo_lower_mean_total": memo,
            "actual_mean_projection_endpoints":
                mean("projection_paid_endpoints"),
            "actual_mean_nonprojection_steps":
                mean("nonprojection_simulated_steps"),
            "mean_feature_evaluations": mean("feature_evaluations"),
            "mean_consecutive_feature_runs":
                mean("consecutive_feature_runs"),
            "mean_unique_feature_tuples":
                mean("unique_feature_tuples"),
            "mean_consecutive_duplicates_removed":
                mean("duplicates_consecutive_only"),
            "mean_ideal_memo_duplicates_removed":
                mean("duplicates_ideal_decision_memo"),
            "max_unique_feature_tuples":
                maximum("unique_feature_tuples"),
            "max_features_in_one_project":
                maximum("max_features_in_one_project"),
            "classification": classification,
        },
        "rows": rows,
        "work_accounting_changed": False,
        "lower_estimates_are_cognitive_work_receipts": False,
        "verdict": classification,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    rep = run(sys.argv[1])
    print("DISTRESS_REUSE_DIAGNOSTIC " + json.dumps(
        rep["summary"], sort_keys=True))
