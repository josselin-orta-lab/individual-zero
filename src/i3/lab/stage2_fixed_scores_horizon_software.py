"""Software-only Stage-2 marginal work characterization, not a living policy.

Prospective protocol:
docs/studies/stage2-replay-gate-selected-design/
PAID_COMPETITION_VS_HORIZON_SOFTWARE_PREFLIGHT_2026-11-11.md

The synthetic effects below were never acquired in a World or paid by an
individual. This helper never calls run_life or constructs a World. It does
not identify a value-of-computation benefit or authorize Stage 2.2/2.3.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from math import isfinite

from ..modules.body import BodyLaws, CognitiveBudget, cognitive_cost, debit_cognition
from ..modules.genome import midpoint
from ..modules.mind import Mind

SCHEMA = "i3-stage2-fixed-evidence-vs-depth-software/v1"
SEED = 211
BODIES = (
    (80.0, 60.0, 60.0, 80.0, 80.0),
    (45.0, 40.0, 40.0, 75.0, 70.0),
    (30.0, 25.0, 25.0, 70.0, 50.0),
)
HORIZONS = (1, 4, 8)
CYCLE_CEILINGS = (0, 1, 4)
PLANS = (
    ("wait", (("attendre",),) * 8),
    ("sleep", (("dormir",),) * 8),
)
SYNTHETIC_UNPAID_EFFECTS = (
    (("attendre",), (-0.35, -0.2, -0.4, 0.2, 0.0)),
    (("dormir",), (3.0, -0.35, -0.4, 0.0, 4.0)),
)


def _source() -> Mind:
    """Fixed artificial prior, transparently NOT a personally born history."""
    mind = Mind(midpoint(), SEED)
    for action, delta in SYNTHETIC_UNPAID_EFFECTS:
        mind.effects.observe(action, delta)
    mind._drift = mind.drift()
    return mind


def _model_forecast(body, plan, horizon):
    mind = _source()
    laws = BodyLaws()
    budget = CognitiveBudget(body, laws)
    value, modeled_plan_steps, uncertainty = mind.simulate(
        body, plan, horizon, budget
    )
    energy, vigilance = cognitive_cost(laws, budget.work)
    post, settled = debit_cognition(body, laws, budget.work)
    if not isfinite(value) or not isfinite(uncertainty):
        raise AssertionError("nonfinite software-only forecast")
    if not (0 <= modeled_plan_steps <= horizon):
        raise AssertionError("invalid modeled plan-step count")
    if budget.work.simulated_steps < modeled_plan_steps:
        raise AssertionError("self-projection simulated work not prepaid")
    if any(settled[c]["unpaid"] != 0.0 for c in ("energy", "vigilance")):
        raise AssertionError("unpaid hypothetical model work")
    if post != budget.remaining:
        raise AssertionError("CognitiveBudget and native debit disagree")
    return {
        "horizon": horizon,
        "value": value,
        "uncertainty": uncertainty,
        "modeled_plan_steps": modeled_plan_steps,
        "work": asdict(budget.work),
        "paid_energy": energy,
        "paid_vigilance": vigilance,
        "post_model_budget_body": post,
    }


def _strict_top(rows):
    if not rows:
        return None
    a = sorted(rows, key=lambda x: -x[1])
    if len(a) > 1 and abs(a[0][1] - a[1][1]) <= 1e-12:
        return None
    return a[0][0]


def _competition(body, scores, ceiling):
    # A fresh Mind has exactly the same internal model and RNG as the
    # untouched synthetic source; only the announced maximum cycles varies.
    mind = _source()
    frozen = tuple(scores)
    budget = CognitiveBudget(body, BodyLaws())
    winner, used = mind._compete(list(frozen), ceiling, budget)
    if tuple(scores) != frozen:
        raise AssertionError("Competition altered its input scores")
    if winner not in dict(frozen):
        raise AssertionError("Competition fabricated a new option")
    if not (0 <= used <= ceiling):
        raise AssertionError("Competition exceeded the fixed ceiling")
    if budget.work.cycles != used or (
        budget.work.simulated_steps or budget.work.memory_items or budget.work.replays
    ):
        raise AssertionError("Competition work was not exactly model-prepaid")
    raw_best = max(dict(scores).values())
    selected_score = dict(scores)[winner]
    if selected_score > raw_best + 1e-12:
        raise AssertionError("fixed evidence obtained a better-than-best score")
    energy, vigilance = cognitive_cost(BodyLaws(), budget.work)
    return {
        "cycles_ceiling": ceiling,
        "cycles_paid": used,
        "chosen": winner,
        "chosen_score": selected_score,
        "raw_best_score": raw_best,
        "score_gap_from_raw_best": selected_score - raw_best,
        "paid_energy": energy,
        "paid_vigilance": vigilance,
        "work": asdict(budget.work),
    }


def audit():
    rows = []
    competition = []
    changed_forecast_bodies = 0
    changed_top_bodies = 0
    for index, body in enumerate(BODIES):
        by_horizon = {}
        for horizon in HORIZONS:
            scored = []
            for name, plan in PLANS:
                outcome = _model_forecast(body, plan, horizon)
                rows.append({"body_index": index, "plan": name, **outcome})
                scored.append((name, outcome["value"]))
            by_horizon[horizon] = tuple(scored)

        low, high = by_horizon[HORIZONS[0]], by_horizon[HORIZONS[-1]]
        if any(abs(dict(low)[name] - dict(high)[name]) > 1e-9
               for name, _plan in PLANS):
            changed_forecast_bodies += 1
        if _strict_top(low) != _strict_top(high):
            changed_top_bodies += 1

        for ceiling in CYCLE_CEILINGS:
            competition.append({
                "body_index": index,
                **_competition(body, by_horizon[HORIZONS[-1]], ceiling),
            })

    payload = {
        "schema": SCHEMA,
        "source_kind": "SYNTHETIC_UNPAID_FIXTURE_NOT_BORN",
        "body_count": len(BODIES),
        "forecast_rows": rows,
        "competition_rows": competition,
        "bodies_with_changed_depth_forecasts": changed_forecast_bodies,
        "bodies_with_changed_raw_top": changed_top_bodies,
        "fixed_competition_scores": True,
        "worlds_opened": 0,
        "scientific_lives": 0,
        "scientific_verdict": "NOT_ISSUED",
        "stage2_2_go": False,
        "stage2_3_go": False,
    }
    checksum = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                 allow_nan=False).encode("utf-8")).hexdigest()
    return {**payload, "deterministic_software_sha256": checksum}


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, indent=2, allow_nan=False))
