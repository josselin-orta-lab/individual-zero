"""Frozen exact death-truncated per-step projection characterization.

Protocol: docs/STAGE1_DEATH_TRUNCATED_PER_STEP.md.
Software only: no World, life, runtime mode or adoption.
"""
from __future__ import annotations

from itertools import combinations
import json
import sys

from . import projection_consistency_characterization as P
from . import stage1_affordable_projection_probes as A
from . import stage1_candidate_g_projection_dependence as D
from . import stage1_candidate_g_reference_recurrence_falsifier as G
from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork, E, F, W, I, V,
    cognitive_cost,
)
from ..modules.forecast_work import projection_simulated_steps_ceiling
from ..modules.genome import midpoint
from ..modules.mind import Mind

SCHEMA = "i3-stage1-death-truncated-per-step/v1"
STEPS = 255
ERROR_LIMIT = 1e-12
CANDIDATE_F_MEAN_BILL = {"energy": 1.3402, "vigilance": 1.840}


def _clamp(x):
    return 0.0 if x < 0.0 else 100.0 if x > 100.0 else x


class DeathTruncatedPerStepMind(Mind):
    """Reference-float per-step projection with exact absorbing-death truncation."""

    def __init__(self, genome, life_seed):
        super().__init__(genome, life_seed)
        self.proj_chunks = (1,) * STEPS
        self.projection_accounting = "chunk_end"
        self._death_stats = {
            "project_calls": 0,
            "paid_projection_steps": 0,
            "early_death_calls": 0,
            "no_death_calls": 0,
            "death_steps": [],
        }

    def projection_stats(self):
        out = dict(self._death_stats)
        out["death_steps"] = list(out["death_steps"])
        return out

    def project(self, body, drift, budget=None):
        if self.projection_accounting != "chunk_end":
            raise ValueError("death-truncated candidate requires chunk_end")
        if self.proj_chunks != (1,) * STEPS:
            raise ValueError("death-truncated candidate requires 255 unit chunks")

        drift, restore = drift
        th = self.theta
        b = list(body)
        ret = [0.0, 0.0, 0.0]
        disc = [1.0, 1.0, 1.0]
        r = 0.0

        self._death_stats["project_calls"] += 1

        for step in range(1, STEPS + 1):
            if budget is not None:
                budget.spend(CognitiveWork(simulated_steps=1))
            self._death_stats["paid_projection_steps"] += 1

            for c in (F, W, I):
                b[c] += drift[c]

            if restore is not None:
                need = max(0.0, th[E] - b[E]) / restore[0]
                if restore[1] > 0.0:
                    need = max(
                        need,
                        max(0.0, th[V] - b[V]) / restore[1])
                n = min(1.0, need)
                b[E] += n * restore[0]
                b[V] += n * restore[1]
                b[F] += n * restore[2]

            for c in range(5):
                b[c] = _clamp(b[c])

            dead = b[F] <= 0.0 or b[W] <= 0.0 or b[I] <= 0.0
            r = -self.d_max if dead else -self.distress(self.feats(b))

            for k, gamma in enumerate(self.gammas):
                ret[k] += disc[k] * r
                disc[k] *= gamma

            if dead:
                # Current death endpoint was already included. Every later
                # reward is the same absorbing -d_max value.
                for k, gamma in enumerate(self.gammas):
                    ret[k] += disc[k] * (r / (1.0 - gamma))
                self._death_stats["early_death_calls"] += 1
                self._death_stats["death_steps"].append(step)
                return ret, b

        for k, gamma in enumerate(self.gammas):
            ret[k] += disc[k] * (r / (1.0 - gamma))
        self._death_stats["no_death_calls"] += 1
        return ret, b


def make_mind(
        genome=None, life_seed=197, *,
        sleep_learned=True, projection_equivalent=False):
    if genome is None:
        genome = midpoint()
    mind = DeathTruncatedPerStepMind(genome, life_seed)
    mind.map = {}
    mind.effects.observe(("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    if projection_equivalent:
        mind.effects.observe(("attendre",), (0., -.2, -.4, .2, 0.))
    else:
        mind.effects.observe(("attendre",), (-.35, -.2, -.4, .2, 0.))
    if sleep_learned:
        mind.effects.observe(("dormir",), (3., -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    if projection_simulated_steps_ceiling(mind) != STEPS:
        raise RuntimeError("death-truncated candidate must keep 255-unit quote")
    return mind


def _candidate_values(genome, body, **fixture):
    out = {}
    for name, plan in P.PLANS.items():
        mind = make_mind(genome, 97, **fixture)
        out[name] = mind.simulate(
            body, plan, P.HORIZON,
            CognitiveBudget(body, BodyLaws()))[0]
    return out


def _pairwise_bias(candidate, truth):
    worst = 0.0
    meta = None
    for a, b in combinations(candidate, 2):
        err = abs(
            (candidate[a] - candidate[b])
            - (truth[a] - truth[b]))
        if err > worst:
            worst = err
            meta = (a, b)
    return worst, meta


def characterize_projection_grid():
    fixtures = {
        "sleep_learned": {"sleep_learned": True},
        "sleep_unlearned": {"sleep_learned": False},
        "projection_equivalent": {
            "sleep_learned": False,
            "projection_equivalent": True,
        },
    }
    max_value_error = 0.0
    max_bias = 0.0
    max_body_error = 0.0
    worst_value = None
    worst_bias = None
    worst_body = None
    cases = 0

    for fixture_name, fixture in fixtures.items():
        for genome_name, genome in P.genomes():
            for body in P.bodies():
                cases += 1
                candidate = _candidate_values(genome, body, **fixture)
                truth = P.values(genome, body, "per_step", **fixture)

                for name in candidate:
                    err = abs(candidate[name] - truth[name])
                    if err > max_value_error:
                        max_value_error = err
                        worst_value = {
                            "fixture": fixture_name,
                            "genome": genome_name,
                            "body": list(body),
                            "option": name,
                            "candidate": candidate[name],
                            "truth": truth[name],
                            "abs_error": err,
                        }

                bias, pair = _pairwise_bias(candidate, truth)
                if bias > max_bias:
                    max_bias = bias
                    worst_bias = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "pair": list(pair) if pair else None,
                        "abs_bias": bias,
                    }

                cm = make_mind(genome, 97, **fixture)
                tm = P.configure(P.make_mind(genome, **fixture), "per_step")
                cb = cm.project(body, cm._drift)[1]
                tb = tm.project(body, tm._drift)[1]
                errs = [abs(a - b) for a, b in zip(cb, tb)]
                err = max(errs)
                if err > max_body_error:
                    max_body_error = err
                    worst_body = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "channel": errs.index(err),
                        "candidate": list(cb),
                        "truth": list(tb),
                        "abs_error": err,
                    }

    return {
        "cases": cases,
        "max_abs_option_value_error": max_value_error,
        "max_pairwise_decision_bias": max_bias,
        "max_final_body_channel_error": max_body_error,
        "worst": {
            "option_value": worst_value,
            "decision_bias": worst_bias,
            "final_body": worst_body,
        },
    }


def _probe_values(mind, body):
    return {
        name: A.plan_value(
            mind, body, plan,
            lambda b, _length: mind.project(b, mind._drift)[0])
        for name, plan in A.PLANS.items()
    }


def characterize_nonlinear_set():
    max_value_error = 0.0
    max_bias = 0.0
    max_body_error = 0.0
    worst_value = None
    worst_bias = None
    worst_body = None

    for body in A.BODIES:
        candidate_mind = make_mind(midpoint(), 197)
        candidate = _probe_values(candidate_mind, body)

        truth_mind = D.make_mind("per_step")
        truth = {
            name: A.plan_value(
                truth_mind, body, plan,
                lambda b, _length, m=truth_mind:
                    m.project(b, m._drift)[0])
            for name, plan in A.PLANS.items()
        }

        for name in candidate:
            err = abs(candidate[name] - truth[name])
            if err > max_value_error:
                max_value_error = err
                worst_value = {
                    "body": list(body),
                    "option": name,
                    "candidate": candidate[name],
                    "truth": truth[name],
                    "abs_error": err,
                }

        bias, pair = _pairwise_bias(candidate, truth)
        if bias > max_bias:
            max_bias = bias
            worst_bias = {
                "body": list(body),
                "pair": list(pair) if pair else None,
                "abs_bias": bias,
            }

        cm = make_mind(midpoint(), 197)
        tm = D.make_mind("per_step")
        cb = cm.project(body, cm._drift)[1]
        tb = tm.project(body, tm._drift)[1]
        errs = [abs(a - b) for a, b in zip(cb, tb)]
        err = max(errs)
        if err > max_body_error:
            max_body_error = err
            worst_body = {
                "body": list(body),
                "channel": errs.index(err),
                "candidate": list(cb),
                "truth": list(tb),
                "abs_error": err,
            }

    return {
        "bodies": len(A.BODIES),
        "plans_per_body": len(A.PLANS),
        "max_abs_option_value_error": max_value_error,
        "max_pairwise_decision_bias": max_bias,
        "max_final_body_channel_error": max_body_error,
        "worst": {
            "option_value": worst_value,
            "decision_bias": worst_bias,
            "final_body": worst_body,
        },
    }


def evaluate_candidate_g():
    recurrence = G.recurrence_2_6_10()
    memory = G.effect_memory()
    rows = []

    total_projection = {
        "project_calls": 0,
        "paid_projection_steps": 0,
        "early_death_calls": 0,
        "no_death_calls": 0,
        "death_steps": [],
    }

    for channel, channel_name in enumerate(G.CHANNEL_NAMES):
        for level in G.LEVELS:
            body = list(G.BASE_BODY)
            body[channel] = level
            body = tuple(body)
            for horizon in G.HORIZONS:
                mind = make_mind()
                budget = CognitiveBudget(body, BodyLaws())
                result = G.paid_water_personal_recurrence_value(
                    mind, memory, recurrence,
                    G.EXPLORE, G.ORDINARY, horizon, budget)
                for key, value in result["work"].items():
                    if value > result["forecast_work_ceiling"][key]:
                        raise RuntimeError(
                            "actual death-truncated work exceeded ceiling")

                bill = cognitive_cost(
                    BodyLaws(),
                    CognitiveWork(**result["work"]))
                stats = mind.projection_stats()
                for key in (
                        "project_calls", "paid_projection_steps",
                        "early_death_calls", "no_death_calls"):
                    total_projection[key] += stats[key]
                total_projection["death_steps"].extend(stats["death_steps"])

                rows.append({
                    "channel": channel_name,
                    "channel_index": channel,
                    "level": level,
                    "horizon": horizon,
                    "information_value": result["trial_information_value"],
                    "trial_advantage": result["trial_advantage"],
                    "target_choices": list(
                        result["target_node_best_choices"]),
                    "work": dict(result["work"]),
                    "forecast_work_ceiling": dict(
                        result["forecast_work_ceiling"]),
                    "bill": {
                        "energy": bill[0],
                        "vigilance": bill[1],
                    },
                    "projection": stats,
                })

    selected = [
        r for r in rows
        if "TRIAL" in r["target_choices"]
        and r["information_value"] > 1e-12
        and r["trial_advantage"] > 1e-12
    ]

    work_keys = ("cycles", "simulated_steps", "memory_items", "replays")
    mean_work = {
        k: sum(r["work"][k] for r in rows) / len(rows)
        for k in work_keys}
    max_work = {
        k: max(r["work"][k] for r in rows)
        for k in work_keys}
    mean_ceiling = {
        k: sum(r["forecast_work_ceiling"][k] for r in rows) / len(rows)
        for k in work_keys}
    max_ceiling = {
        k: max(r["forecast_work_ceiling"][k] for r in rows)
        for k in work_keys}

    death_steps = total_projection["death_steps"]
    total_projection["mean_paid_steps_per_projection"] = (
        total_projection["paid_projection_steps"]
        / total_projection["project_calls"])
    total_projection["death_step_min"] = (
        min(death_steps) if death_steps else None)
    total_projection["death_step_mean"] = (
        sum(death_steps) / len(death_steps)
        if death_steps else None)
    total_projection["death_step_max"] = (
        max(death_steps) if death_steps else None)

    mean_bill = {
        key: sum(r["bill"][key] for r in rows) / len(rows)
        for key in ("energy", "vigilance")}
    max_bill = {
        key: max(r["bill"][key] for r in rows)
        for key in ("energy", "vigilance")}

    summary = {
        "evaluated": len(rows),
        "complete": len(rows),
        "selected_epistemic": len(selected),
        "selected_water_deficit": sum(
            r["channel_index"] == W for r in selected),
        "selected_other_deficit": sum(
            r["channel_index"] != W for r in selected),
        "declined": sum(
            r["target_choices"] == ["DECLINE_TRIAL"] for r in rows),
        "max_information_value": max(
            r["information_value"] for r in rows),
        "best_trial_advantage": max(
            r["trial_advantage"] for r in rows),
        "worst_trial_advantage": min(
            r["trial_advantage"] for r in rows),
        "mean_work": mean_work,
        "max_work": max_work,
        "mean_forecast_ceiling": mean_ceiling,
        "max_forecast_ceiling": max_ceiling,
        "mean_bill": mean_bill,
        "max_bill": max_bill,
        "projection": total_projection,
        "actual_work_ceiling_violations": 0,
    }
    return rows, summary


def run(out_path):
    grid = characterize_projection_grid()
    nonlinear = characterize_nonlinear_set()
    rows, candidate_g = evaluate_candidate_g()

    structural_pass = all((
        grid["max_abs_option_value_error"] <= ERROR_LIMIT,
        grid["max_pairwise_decision_bias"] <= ERROR_LIMIT,
        grid["max_final_body_channel_error"] <= ERROR_LIMIT,
        nonlinear["max_abs_option_value_error"] <= ERROR_LIMIT,
        nonlinear["max_pairwise_decision_bias"] <= ERROR_LIMIT,
        nonlinear["max_final_body_channel_error"] <= ERROR_LIMIT,
        candidate_g["complete"] == 80,
        candidate_g["selected_epistemic"] == 32,
        candidate_g["selected_water_deficit"] == 8,
        candidate_g["selected_other_deficit"] == 24,
        candidate_g["declined"] == 40,
        candidate_g["actual_work_ceiling_violations"] == 0,
        candidate_g["mean_work"]["simulated_steps"] < 1288,
    ))

    candidate_f_cost_parity = (
        candidate_g["mean_bill"]["energy"]
        <= CANDIDATE_F_MEAN_BILL["energy"]
        and candidate_g["mean_bill"]["vigilance"]
        <= CANDIDATE_F_MEAN_BILL["vigilance"]
    )

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_DEATH_TRUNCATED_PER_STEP.md",
        "world_access": False,
        "lives": 0,
        "projection_grid": grid,
        "nonlinear_option_set": nonlinear,
        "candidate_g": candidate_g,
        "rows": rows,
        "forecast_quote_per_projection": STEPS,
        "baselines": {
            "candidate_f": {
                "selected_epistemic": 24,
                "mean_simulated_steps": 470,
                "mean_bill": dict(CANDIDATE_F_MEAN_BILL),
            },
            "per_step": {
                "selected_epistemic": 32,
                "selected_water_deficit": 8,
                "selected_other_deficit": 24,
                "declined": 40,
                "mean_simulated_steps": 1288,
                "mean_bill": {
                    "energy": 2.9762,
                    "vigilance": 3.476,
                },
            },
        },
        "candidate_f_cost_parity": candidate_f_cost_parity,
        "runtime_candidate_authorized": (
            structural_pass and candidate_f_cost_parity),
        "verdict": (
            "DEATH_TRUNCATED_PER_STEP_EXACT_PASS"
            if structural_pass else
            "DEATH_TRUNCATED_PER_STEP_EXACT_FAIL"),
    }

    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    rep = run(sys.argv[1])
    print(json.dumps({
        "verdict": rep["verdict"],
        "candidate_f_cost_parity": rep["candidate_f_cost_parity"],
        "runtime_candidate_authorized":
            rep["runtime_candidate_authorized"],
        "projection_grid": rep["projection_grid"],
        "nonlinear_option_set": rep["nonlinear_option_set"],
        "candidate_g": rep["candidate_g"],
    }, indent=1, sort_keys=True))
