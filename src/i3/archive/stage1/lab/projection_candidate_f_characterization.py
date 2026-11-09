"""Frozen laboratory characterization of Candidate F.

Candidate F keeps Candidate E's sparse projector and changes only the numerical
state continuity across explicit plan simulation -> bootstrap.
"""
from __future__ import annotations

from decimal import Decimal, localcontext
import json
import sys

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.archive.stage1.lab import projection_candidate_e_characterization as ECHAR
from i3.lab import projection_consistency_characterization as P
from i3.lab import projection_end_to_end_numeric_oracle as O

SCHEMA = "i3-projection-candidate-f-characterization/v1"
BIAS_LIMIT = 1e-3
INVARIANT_LIMIT = 1e-3
BODY_LIMIT = 1e-10


def _project_sparse_decimal_state(mind, body, budget):
    """Candidate E local quadratic-4, starting from an existing Decimal body."""
    ret = [0.0, 0.0, 0.0]
    disc = [1.0, 1.0, 1.0]
    drift_raw, restore_raw = mind._drift
    drift = tuple(mind._projection_decimal(x) for x in drift_raw)
    restore = (
        tuple(mind._projection_decimal(x) for x in restore_raw)
        if restore_raw is not None else None)
    theta = tuple(mind._projection_decimal(x) for x in mind.theta)

    dead = mind._projection_decimal_dead(body)
    r_start = mind._projection_decimal_reward(body, dead, budget)

    for outer in mind.proj_chunks:
        remaining = outer
        while remaining > 0:
            if dead:
                for k, gamma in enumerate(mind.gammas):
                    g_run = gamma ** remaining
                    weight = (1.0 - g_run) / (1.0 - gamma)
                    ret[k] += disc[k] * (-mind.d_max) * weight
                    disc[k] *= g_run
                remaining = 0
                continue

            event_run = mind._projection_decimal_next_event_segment(
                body, drift, restore, theta, remaining)
            event_remaining = event_run

            while event_remaining > 0:
                block_run = min(4, event_remaining)
                if block_run == 1:
                    end_body, end_dead = mind._projection_decimal_advance(
                        body, drift, restore, theta, 1)
                    r_end = mind._projection_decimal_reward(
                        end_body, end_dead, budget)
                    r_mid = None
                else:
                    midpoint = Decimal(block_run) / Decimal(2)
                    mid_body, mid_dead = mind._projection_decimal_advance(
                        body, drift, restore, theta, midpoint)
                    if mid_dead:
                        raise RuntimeError(
                            "Candidate F block crossed death before endpoint")
                    r_mid = mind._projection_decimal_reward(
                        mid_body, mid_dead, budget)
                    end_body, end_dead = mind._projection_decimal_advance(
                        body, drift, restore, theta, block_run)
                    if end_dead:
                        raise RuntimeError(
                            "Candidate F multi-step block crossed death")
                    r_end = mind._projection_decimal_reward(
                        end_body, end_dead, budget)

                for k, gamma in enumerate(mind.gammas):
                    g_run = gamma ** block_run
                    segment = (
                        r_end if block_run == 1 else
                        mind._discounted_quadratic_sum(
                            r_start, r_mid, r_end,
                            block_run, gamma))
                    ret[k] += disc[k] * segment
                    disc[k] *= g_run

                body = list(end_body)
                dead = end_dead
                r_start = r_end
                remaining -= block_run
                event_remaining -= block_run

    r_tail = -mind.d_max if dead else r_start
    for k, gamma in enumerate(mind.gammas):
        ret[k] += disc[k] * (r_tail / (1.0 - gamma))
    return ret, body


def simulate(mind, body, plan, horizon, budget):
    """Canonical explicit plan state, continuous into unchanged E bootstrap."""
    with localcontext() as ctx:
        ctx.prec = 100
        state = [mind._projection_decimal(x) for x in body]
        steps = 0
        ret = [0.0, 0.0, 0.0]
        disc = [1.0, 1.0, 1.0]
        dead = False
        u_max = 0.0
        i, n = 0, len(plan)

        while i < n and steps < horizon:
            budget.spend(CognitiveWork(simulated_steps=1))
            key = plan[i]
            run = 1
            if key[0] == "se_deplacer":
                while (
                        i + run < n
                        and plan[i + run] == key
                        and run < horizon):
                    run += 1
            i += run

            mean, uncertainty = mind._read_plan_prediction(key)
            u_max = max(u_max, uncertainty)
            drun = Decimal(run)
            for channel in range(5):
                state[channel] += (
                    drun * mind._projection_decimal(mean[channel]))
            mind._projection_decimal_clamp(state)

            steps += 1
            dead = mind._projection_decimal_dead(state)
            reward = (
                -mind.d_max if dead else
                -mind.distress(
                    mind.feats(tuple(float(x) for x in state))))
            for k, gamma in enumerate(mind.gammas):
                g_run = gamma ** run
                ret[k] += (
                    disc[k] * reward
                    * ((1.0 - g_run) / (1.0 - gamma)))
                disc[k] *= g_run
            if dead:
                break

        phi = mind.feats(tuple(float(x) for x in state))
        projection = (
            None if dead else
            _project_sparse_decimal_state(
                mind, state, budget)[0])

        out = 0.0
        for k, gamma in enumerate(mind.gammas):
            boot = (
                -mind.d_max / (1.0 - gamma)
                if dead else mind.value(k, phi, projection))
            out += (1.0 - gamma) * (
                ret[k] + disc[k] * boot)
        return out / 3.0, steps, u_max


def values(genome, body, **fixture):
    out = {}
    for name, plan in P.PLANS.items():
        mind = P.make_mind(genome, **fixture)
        budget = CognitiveBudget(body, BodyLaws())
        out[name] = simulate(
            mind, body, plan, P.HORIZON, budget)[0]
    return out


def run(out_path):
    fixtures = {
        "sleep_learned": {"sleep_learned": True},
        "sleep_unlearned": {"sleep_learned": False},
        "projection_equivalent": {
            "sleep_learned": False,
            "projection_equivalent": True,
        },
    }
    stats = {
        "max_abs_prefix_error_vs_oracle": 0.0,
        "max_decision_bias_vs_oracle": 0.0,
        "max_direct_final_body_error_vs_oracle": 0.0,
    }
    invariant = 0.0
    paid_units = []
    cases = 0
    worst = {
        "prefix_error": None,
        "decision_bias": None,
        "direct_final_body": None,
    }

    for fixture_name, fixture in fixtures.items():
        for genome_name, genome in P.genomes():
            for body in P.bodies():
                cases += 1
                oracle = O.values(genome, body, **fixture)
                candidate = values(genome, body, **fixture)

                oracle_g1 = oracle["plus_1_wait"] - oracle["prefix"]
                oracle_g3 = oracle["plus_3_waits"] - oracle["prefix"]
                cand_g1 = candidate["plus_1_wait"] - candidate["prefix"]
                cand_g3 = candidate["plus_3_waits"] - candidate["prefix"]

                prefix_error = abs(
                    candidate["prefix"] - oracle["prefix"])
                if prefix_error > stats[
                        "max_abs_prefix_error_vs_oracle"]:
                    stats[
                        "max_abs_prefix_error_vs_oracle"
                    ] = prefix_error
                    worst["prefix_error"] = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "candidate": candidate["prefix"],
                        "oracle": oracle["prefix"],
                        "abs_error": prefix_error,
                    }

                bias_1 = abs(cand_g1 - oracle_g1)
                bias_3 = abs(cand_g3 - oracle_g3)
                decision_bias = max(bias_1, bias_3)
                if decision_bias > stats[
                        "max_decision_bias_vs_oracle"]:
                    stats["max_decision_bias_vs_oracle"] = (
                        decision_bias)
                    worst["decision_bias"] = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "comparison": (
                            "plus_1_wait"
                            if bias_1 >= bias_3
                            else "plus_3_waits"),
                        "candidate_gap": (
                            cand_g1 if bias_1 >= bias_3
                            else cand_g3),
                        "oracle_gap": (
                            oracle_g1 if bias_1 >= bias_3
                            else oracle_g3),
                        "abs_bias": decision_bias,
                    }

                if fixture_name == "projection_equivalent":
                    invariant = max(
                        invariant, abs(cand_g1), abs(cand_g3))

                _cp, candidate_body, paid = ECHAR.direct(
                    genome, body, **fixture)
                _op, oracle_body, oracle_paid = O.direct_projection(
                    genome, body, **fixture)
                if oracle_paid != len(P.PER_STEP):
                    raise RuntimeError("authorized oracle cost changed")
                paid_units.append(paid)

                body_errors = tuple(
                    abs(a - b) for a, b in zip(
                        candidate_body, oracle_body))
                body_error = max(body_errors)
                if body_error > stats[
                        "max_direct_final_body_error_vs_oracle"]:
                    stats[
                        "max_direct_final_body_error_vs_oracle"
                    ] = body_error
                    channel = body_errors.index(body_error)
                    worst["direct_final_body"] = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "channel": channel,
                        "candidate_final_body":
                            list(candidate_body),
                        "oracle_final_body": list(oracle_body),
                        "abs_error": body_error,
                    }

    max_paid = max(paid_units)
    passed = (
        stats["max_decision_bias_vs_oracle"] <= BIAS_LIMIT
        and invariant <= INVARIANT_LIMIT
        and stats[
            "max_direct_final_body_error_vs_oracle"
        ] <= BODY_LIMIT
        and max_paid < len(P.PER_STEP)
    )

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_PROJECTION_CANDIDATE_F.md",
        "world_access": False,
        "lives": 0,
        "cases": cases,
        "candidate":
            "end_to_end_canonical_plus_event_local_quadratic4",
        "truth":
            "end_to_end_high_precision_oracle_1117",
        "stats": stats,
        "projection_equivalent_invariant_max_gap": invariant,
        "paid_projection_units": {
            "min": min(paid_units),
            "mean": sum(paid_units) / len(paid_units),
            "max": max_paid,
            "oracle": len(P.PER_STEP),
        },
        "worst_cases": worst,
        "selection": {
            "decision_bias_limit": BIAS_LIMIT,
            "invariant_limit": INVARIANT_LIMIT,
            "final_body_limit": BODY_LIMIT,
            "decision_bias_pass":
                stats["max_decision_bias_vs_oracle"]
                <= BIAS_LIMIT,
            "invariant_pass": invariant <= INVARIANT_LIMIT,
            "final_body_pass":
                stats[
                    "max_direct_final_body_error_vs_oracle"
                ] <= BODY_LIMIT,
            "strictly_cheaper_than_oracle_every_case":
                max_paid < len(P.PER_STEP),
            "verdict": (
                "CANDIDATE_F_PASSES_LAB_SOFTWARE_GATE"
                if passed else "NO_CANDIDATE_PROMOTED"),
        },
        "mind_runtime_integration_authorized": passed,
        "omega_rerun_authorized": False,
        "reference_adoption_authorized": False,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1]), indent=1, sort_keys=True))
