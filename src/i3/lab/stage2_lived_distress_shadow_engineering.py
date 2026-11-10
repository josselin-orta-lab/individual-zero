"""First REAL first-person outcome for the Stage-2.1 distress shadow (engineering).

A deliberately external, temporary method-spy observes the unchanged reference
Mind AFTER its own decision but BEFORE its actual World.step. It only copies
personal memories and commits two independent shadow forecasts. The same
actually executed step provides the outcome. No controller, runtime, World
laws, earned rewards or living cognition is modified.

The shadow CPU is UNPAID. This is non-evidentiary engineering, not a cohort,
a policy-off-policy comparison or an authorization to integrate this predictor.
The two method spies are scoped to a synchronous single-threaded run; never
use them to instrument scientific originals or concurrent executions.
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import isfinite
from unittest.mock import patch

from ..modules.genome import midpoint
from ..modules.mind import Mind
from ..modules.world import World
from ..runtime.life import run_life
from .dev_worlds import dev_open_field
from .stage2_personal_distress_forecast_shadow import (
    PersonalDistressHead, PrequentialDistressAudit, REPLAYS)
from ..modules.stage2_replay_content_selection import random_content_indices

SCHEMA = "i3-stage2.1-lived-first-person-shadow-engineering/v1"
HORIZON = 80
LIFE_SEEDS = (920041, 920042)
MEMORIES_REQUIRED = 2 * REPLAYS


def _hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False, default=str).encode()).hexdigest()


def _mind_seal(mind):
    """Only first-person learnt state and RNGs, never World internals."""
    return _hash({
        "values": mind.values, "buffer": list(mind.buffer),
        "effects": repr(mind.effects.stats), "map": repr(mind.map),
        "hist": repr(mind.hist), "rng": repr(mind.rng.getstate()),
        "budget_rng": repr(mind._budget_rng.getstate()),
    })


class LivedDistressShadowWitness:
    def __init__(self, life_seed):
        if type(life_seed) is not int or life_seed < 0:
            raise ValueError("engineering life seed required")
        self.life_seed = life_seed
        self.steps = 0
        self.event = None
        self.audit = None
        self.pending = False

    def before_actual_step(self, mind, capture, action):
        """Called strictly after a LIVE decision, before the real World step."""
        if self.pending:
            raise RuntimeError("unsettled shadow forecast at a new decision")
        if self.event is not None or len(mind.buffer) < MEMORIES_REQUIRED:
            return
        if type(mind) is not Mind:
            raise PermissionError("reference Mind only; no experimental controller")
        original = _mind_seal(mind)
        memories = tuple(mind.buffer)
        ranked = tuple(sorted(range(len(memories)),
                              key=lambda i: -memories[i][0])[:REPLAYS])
        random = random_content_indices(
            eligible=len(memories), count=REPLAYS,
            life_seed=self.life_seed, sleep_ordinal=self.steps + 1)
        priority_head = PersonalDistressHead(mind)
        random_head = PersonalDistressHead(mind)
        priority_head.apply(memories, ranked)
        random_head.apply(memories, random)
        monitor = PrequentialDistressAudit(mind)
        body = capture["body"]  # the individual's actual first-person capture
        frozen = monitor.freeze(
            identity=f"engineering-{self.life_seed}-{self.steps}",
            priority_head=priority_head, random_head=random_head,
            before_body=body)
        if _mind_seal(mind) != original:
            raise RuntimeError("observer changed living Mind or RNG")
        self.audit = monitor
        self.event = {
            "observed_step": self.steps + 1,
            "live_action_selected_before_world": action,
            "past_memories_available": len(memories),
            "shadow_replay_updates_per_arm": REPLAYS,
            "priority_memory_indices": list(ranked),
            "random_memory_indices": list(random),
            "different_memory_subsets": set(ranked) != set(random),
            "different_frozen_forecasts": frozen["different_forecast"],
            "preoutcome_prediction_sha256": frozen["preoutcome_prediction_sha256"],
            "frozen_before_actual_world_step": True,
            "actual_outcome": None,
        }
        self.pending = True

    def after_actual_step(self, action, result):
        """Called only on the actual World's returned first-person outcome."""
        self.steps += 1
        if not self.pending:
            return
        if self.event is None or action != self.event["live_action_selected_before_world"]:
            raise RuntimeError("outcome not matched to the sealed live action")
        if self.steps != self.event["observed_step"]:
            raise RuntimeError("outcome not matched to the sealed live step")
        if type(result.get("dead")) not in (tuple, list):
            raise ValueError("actual death cause list required")
        observed = self.audit.score(
            identity=f"engineering-{self.life_seed}-{self.steps - 1}",
            preoutcome_prediction_sha256=self.event["preoutcome_prediction_sha256"],
            actual_after_body=result["body"],
            actual_dead=bool(result["dead"]))
        self.event["actual_outcome"] = {
            "status": observed["status"],
            "terminal_observed": observed["terminal_observed"],
            "observed_next_intrinsic_reward":
                observed["observed_next_intrinsic_reward"],
            "priority_squared_error": observed["priority_squared_error"],
            "random_squared_error": observed["random_squared_error"],
        }
        self.pending = False

    def report(self):
        if self.pending:
            raise RuntimeError("first-person outcome not accounted after freeze")
        if self.event is None:
            status = "NO_ELIGIBLE_PERSONAL_HISTORY"
            frozen = scored = 0
        else:
            status = "ONE_REAL_FIRST_PERSON_OUTCOME_SCORED"
            r = self.audit.report()
            if (r["frozen_predictions"] != 1 or
                    r["scored_observed_outcomes"] != 1 or
                    not r["all_windows_accounted"]):
                raise RuntimeError("prequential first-person event missing")
            frozen = scored = 1
        return {
            "schema": SCHEMA, "status": status,
            "steps_lived_observed": self.steps,
            "frozen_first_person_forecasts": frozen,
            "scored_real_world_outcomes": scored,
            "first_event": self.event,
            "observer_cannot_choose_or_modify_action": True,
            "original_cognition_accounted_by_reference_only": True,
            "shadow_computation_physically_paid": False,
            "observer_saw_only_actual_capture_mind_and_step_result": True,
            "scientific_lives": 0,
            "independent_iid_ecology": False,
            "scientific_predictive_utility_or_survival_claim": False,
        }


def run_observed_reference(genome, spec, life_seed, horizon=HORIZON):
    """Instrument exactly one *engineering reference* life with scoped spies."""
    witness = LivedDistressShadowWitness(life_seed)
    real_decide = Mind.decide
    real_step = World.step

    def decide_spy(mind, capture, budget):
        action, param, work, info = real_decide(mind, capture, budget)
        witness.before_actual_step(mind, capture, action)
        return action, param, work, info

    def step_spy(world, action, param, work):
        result = real_step(world, action, param, work)
        witness.after_actual_step(action, result)
        return result

    # No alteration to source or runtime/life.py. The hooks cannot feed back
    # into Mind.decide, World.step or the existing cognition debit.
    with patch.object(Mind, "decide", decide_spy), patch.object(World, "step", step_spy):
        life = run_life(genome, spec, life_seed, horizon)
    report = witness.report()
    if life["steps_lived"] != report["steps_lived_observed"]:
        raise RuntimeError("one spy receipt missing from actual World steps")
    return life, report


def rehearse():
    """Two fixed NON-EVIDENTIARY engineering lives, matched observer ON/OFF."""
    rows = []
    for life_seed in LIFE_SEEDS:
        genome = midpoint()
        plain = run_life(genome, dev_open_field(), life_seed, HORIZON)
        live, report = run_observed_reference(
            genome, dev_open_field(), life_seed, HORIZON)
        parity = all(plain[key] == live[key] for key in (
            "trace_head", "evidence_head", "steps_lived", "terminal",
            "death_causes", "actions", "final_body", "cognitive_accounting"))
        if not parity:
            raise RuntimeError("unpaid observer changed the actual living trajectory")
        rows.append({
            "life_seed": life_seed,
            "observer_on_off_physical_and_decision_parity": parity,
            "steps_lived": live["steps_lived"],
            "first_event": report["first_event"],
            "observer_status": report["status"],
        })
    return {
        "schema": SCHEMA,
        "status": "REAL_FIRST_PERSON_ENGINEERING_SHADOW_ONLY",
        "engineering_matched_on_off_pairs": len(rows),
        "physical_and_decision_parity_pairs": sum(
            x["observer_on_off_physical_and_decision_parity"] for x in rows),
        "real_first_person_scored_windows": sum(
            x["first_event"] is not None and
            x["first_event"]["actual_outcome"] is not None for x in rows),
        "different_memory_subsets": sum(
            x["first_event"] is not None and
            x["first_event"]["different_memory_subsets"] for x in rows),
        "different_frozen_forecasts": sum(
            x["first_event"] is not None and
            x["first_event"]["different_frozen_forecasts"] for x in rows),
        "priority_lower_realized_sq_loss": sum(
            x["first_event"] is not None and
            x["first_event"]["actual_outcome"] is not None and
            x["first_event"]["actual_outcome"]["priority_squared_error"] <
            x["first_event"]["actual_outcome"]["random_squared_error"]
            for x in rows),
        "random_lower_realized_sq_loss": sum(
            x["first_event"] is not None and
            x["first_event"]["actual_outcome"] is not None and
            x["first_event"]["actual_outcome"]["random_squared_error"] <
            x["first_event"]["actual_outcome"]["priority_squared_error"]
            for x in rows),
        "rows": rows,
        "shadow_cpu_physically_paid": False,
        "independent_iid_ecology_attested": False,
        "scientific_lives": 0,
        "scientific_verdict": "NOT_ISSUED",
        "stage2_2_activation": False,
    }


if __name__ == "__main__":
    print(json.dumps(rehearse(), sort_keys=True, indent=2))
