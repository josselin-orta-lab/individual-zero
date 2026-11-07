"""Frozen decomposition of Stage-1 event-projection residual error.

Protocol: docs/STAGE1_PROJECTION_ERROR_DECOMPOSITION.md.
Software only. No World, life, runtime policy or scientific allocation.
"""
from __future__ import annotations

import json
import sys

from ..modules.body import BodyLaws, CognitiveBudget, CognitiveWork, F, W, I
from . import projection_consistency_characterization as P
from . import projection_event_quartic_characterization as D

SCHEMA = "i3-projection-event-error-decomposition/v1"
NUMERICAL_TOLERANCE = 1e-10


class _EventExactView:
    __slots__ = ("owner",)

    def __init__(self, owner):
        self.owner = owner

    def __getattr__(self, name):
        return getattr(self.owner, name)

    def project(self, body, drift, budget=None):
        return project_event_exact(self.owner, body, drift, budget)


def project_event_exact(mind, b, drift_spec, budget=None):
    """Evaluate every discrete endpoint inside Candidate-C/D event segments."""
    drift, restore = drift_spec
    body = list(b)
    ret = [0.0, 0.0, 0.0]
    disc = [1.0, 1.0, 1.0]
    dead = body[F] <= 0.0 or body[W] <= 0.0 or body[I] <= 0.0
    last_reward = -mind.d_max if dead else -mind.distress(mind.feats(body))

    for outer in mind.proj_chunks:
        remaining = outer
        while remaining > 0:
            if dead:
                if budget is not None:
                    budget.spend(CognitiveWork(simulated_steps=remaining))
                for k, gk in enumerate(mind.gammas):
                    g_run = gk ** remaining
                    weight = (1.0 - g_run) / (1.0 - gk)
                    ret[k] += disc[k] * (-mind.d_max) * weight
                    disc[k] *= g_run
                last_reward = -mind.d_max
                remaining = 0
                continue

            run = mind._projection_next_event_segment(
                body, drift, restore, remaining)
            end_body = list(body)
            end_dead = False
            for step in range(1, run + 1):
                sample_body, sample_dead = mind._projection_advance(
                    body, drift, restore, step)
                if budget is not None:
                    budget.spend(CognitiveWork(simulated_steps=1))
                reward = (
                    -mind.d_max if sample_dead
                    else -mind.distress(mind.feats(sample_body)))
                for k, gk in enumerate(mind.gammas):
                    ret[k] += disc[k] * reward
                    disc[k] *= gk
                end_body = sample_body
                end_dead = sample_dead
                last_reward = reward
                if sample_dead and step < run:
                    tail = run - step
                    if budget is not None:
                        budget.spend(CognitiveWork(simulated_steps=tail))
                    for k, gk in enumerate(mind.gammas):
                        g_run = gk ** tail
                        weight = (1.0 - g_run) / (1.0 - gk)
                        ret[k] += disc[k] * (-mind.d_max) * weight
                        disc[k] *= g_run
                    last_reward = -mind.d_max
                    break

            body = list(end_body)
            dead = end_dead
            remaining -= run

    for k, gk in enumerate(mind.gammas):
        ret[k] += disc[k] * (last_reward / (1.0 - gk))
    return ret, body


def event_exact_values(genome, body, **fixture):
    out = {}
    for name, plan in P.PLANS.items():
        mind = P.make_mind(genome, **fixture)
        view = _EventExactView(mind)
        budget = CognitiveBudget(body, BodyLaws())
        out[name] = type(mind).simulate(
            view, body, plan, P.HORIZON, budget)[0]
    return out


def direct_event_exact(genome, body, **fixture):
    mind = P.make_mind(genome, **fixture)
    budget = CognitiveBudget(body, BodyLaws())
    values, final_body = project_event_exact(
        mind, body, mind._drift, budget)
    return values, tuple(final_body), budget.work.simulated_steps


def direct_per_step(genome, body, **fixture):
    mind = P.configure(P.make_mind(genome, **fixture), "per_step")
    budget = CognitiveBudget(body, BodyLaws())
    values, final_body = mind.project(body, mind._drift, budget)
    return values, tuple(final_body), budget.work.simulated_steps


def run(out_path):
    fixtures = {
        "sleep_learned": {"sleep_learned": True},
        "sleep_unlearned": {"sleep_learned": False},
        "projection_equivalent": {
            "sleep_learned": False,
            "projection_equivalent": True,
        },
    }
    exact = {
        "max_abs_prefix_error_vs_per_step": 0.0,
        "max_decision_bias_vs_per_step": 0.0,
        "projection_equivalent_invariant_max_gap": 0.0,
        "max_final_body_channel_error_vs_per_step": 0.0,
    }
    quartic_vs_exact = {
        "max_abs_prefix_difference": 0.0,
        "max_decision_difference": 0.0,
    }
    units = []
    cases = 0
    worst = {
        "prefix_error": None,
        "decision_bias": None,
        "final_body_error": None,
        "quartic_decision_difference": None,
    }

    for fixture_name, fixture in fixtures.items():
        for genome_name, genome in P.genomes():
            for body in P.bodies():
                cases += 1
                truth = P.values(genome, body, "per_step", **fixture)
                event = event_exact_values(genome, body, **fixture)
                quartic = D.values(
                    genome, body, D.CANDIDATE, **fixture)

                truth_g1 = truth["plus_1_wait"] - truth["prefix"]
                truth_g3 = truth["plus_3_waits"] - truth["prefix"]
                event_g1 = event["plus_1_wait"] - event["prefix"]
                event_g3 = event["plus_3_waits"] - event["prefix"]
                quartic_g1 = quartic["plus_1_wait"] - quartic["prefix"]
                quartic_g3 = quartic["plus_3_waits"] - quartic["prefix"]

                prefix_error = abs(event["prefix"] - truth["prefix"])
                if prefix_error > exact["max_abs_prefix_error_vs_per_step"]:
                    exact["max_abs_prefix_error_vs_per_step"] = prefix_error
                    worst["prefix_error"] = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "event_exact": event["prefix"],
                        "per_step": truth["prefix"],
                        "abs_error": prefix_error,
                    }

                bias_1 = abs(event_g1 - truth_g1)
                bias_3 = abs(event_g3 - truth_g3)
                decision_bias = max(bias_1, bias_3)
                if decision_bias > exact["max_decision_bias_vs_per_step"]:
                    exact["max_decision_bias_vs_per_step"] = decision_bias
                    worst["decision_bias"] = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "comparison": (
                            "plus_1_wait" if bias_1 >= bias_3
                            else "plus_3_waits"),
                        "event_exact_gap": (
                            event_g1 if bias_1 >= bias_3 else event_g3),
                        "per_step_gap": (
                            truth_g1 if bias_1 >= bias_3 else truth_g3),
                        "abs_bias": decision_bias,
                    }
                if fixture_name == "projection_equivalent":
                    exact["projection_equivalent_invariant_max_gap"] = max(
                        exact["projection_equivalent_invariant_max_gap"],
                        abs(event_g1), abs(event_g3))

                quartic_vs_exact["max_abs_prefix_difference"] = max(
                    quartic_vs_exact["max_abs_prefix_difference"],
                    abs(quartic["prefix"] - event["prefix"]))
                qdiff_1 = abs(quartic_g1 - event_g1)
                qdiff_3 = abs(quartic_g3 - event_g3)
                qdiff = max(qdiff_1, qdiff_3)
                if qdiff > quartic_vs_exact["max_decision_difference"]:
                    quartic_vs_exact["max_decision_difference"] = qdiff
                    worst["quartic_decision_difference"] = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "comparison": (
                            "plus_1_wait" if qdiff_1 >= qdiff_3
                            else "plus_3_waits"),
                        "quartic_gap": (
                            quartic_g1 if qdiff_1 >= qdiff_3
                            else quartic_g3),
                        "event_exact_gap": (
                            event_g1 if qdiff_1 >= qdiff_3
                            else event_g3),
                        "abs_difference": qdiff,
                    }

                _ev, event_body, paid = direct_event_exact(
                    genome, body, **fixture)
                _tr, truth_body, truth_paid = direct_per_step(
                    genome, body, **fixture)
                if truth_paid != len(P.PER_STEP):
                    raise RuntimeError("per-step truth cost changed")
                units.append(paid)
                body_errors = tuple(
                    abs(a - b) for a, b in zip(event_body, truth_body))
                body_error = max(body_errors)
                if body_error > exact[
                        "max_final_body_channel_error_vs_per_step"]:
                    channel = body_errors.index(body_error)
                    exact["max_final_body_channel_error_vs_per_step"] = (
                        body_error)
                    worst["final_body_error"] = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "channel": channel,
                        "event_exact_final_body": list(event_body),
                        "per_step_final_body": list(truth_body),
                        "abs_error": body_error,
                    }

    trajectory_same = (
        exact["max_decision_bias_vs_per_step"] <= NUMERICAL_TOLERANCE
        and exact["projection_equivalent_invariant_max_gap"]
            <= NUMERICAL_TOLERANCE
        and exact["max_final_body_channel_error_vs_per_step"]
            <= NUMERICAL_TOLERANCE
    )
    interpolation_material = (
        quartic_vs_exact["max_decision_difference"]
        > NUMERICAL_TOLERANCE
    )
    if trajectory_same and interpolation_material:
        classification = "INTERPOLATION_SOURCE_CONFIRMED_ON_FROZEN_GRID"
    elif trajectory_same:
        classification = "NO_MATERIAL_RESIDUAL_AT_NUMERICAL_TOLERANCE"
    else:
        classification = "SEGMENTED_BODY_EVOLUTION_CONTRIBUTES"

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_PROJECTION_ERROR_DECOMPOSITION.md",
        "world_access": False,
        "lives": 0,
        "cases": cases,
        "numerical_tolerance": NUMERICAL_TOLERANCE,
        "event_exact_vs_per_step": exact,
        "event_quartic_vs_event_exact": quartic_vs_exact,
        "paid_event_exact_projection_units": {
            "min": min(units),
            "mean": sum(units) / len(units),
            "max": max(units),
            "per_step_truth": len(P.PER_STEP),
        },
        "classification": classification,
        "worst_cases": worst,
        "candidate_promoted": False,
        "omega_rerun_authorized": False,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    report = run(sys.argv[1])
    print(json.dumps(report, indent=1, sort_keys=True))
