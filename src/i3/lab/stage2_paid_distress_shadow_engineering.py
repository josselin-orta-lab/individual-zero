"""Three-arm, physically PAID I3 distress shadow; engineering reference ONLY.

Only externally wraps reference Mind.decide and World.step in synchronous
lab runs. The extra CognitiveWork is first granted by the SAME native v2
CognitiveBudget and then actually debited by the SAME original World.step.
No motor choice or action score is changed. A point forecast is sealed before
the actually observed next body; no counterfactual future is produced.

This category tariff is explicitly provisional, not measured wall-CPU work
or a scientific license to deploy the head in a born individual's policy.
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import isfinite
from unittest.mock import patch

from ..modules.body import ACTION_COSTS, CognitiveWork, cognitive_cost
from ..modules.genome import midpoint
from ..modules.mind import Mind
from ..modules.stage2_replay_content_selection import random_content_indices
from ..modules.world import World
from ..runtime.life import run_life
from .dev_worlds import dev_open_field
from .stage2_personal_distress_forecast_shadow import PersonalDistressHead

SCHEMA = "i3-stage2.1-paid-direct-distress-engineering/v1"
MODES = ("priority", "random", "discard")
SEEDS = (930041, 930042)
HORIZON = 80
REPLAYS = 3
MIN_MEMORY = 2 * REPLAYS


def _digest(record):
    return sha256(json.dumps(record, sort_keys=True, separators=(",", ":"),
                             allow_nan=False, default=str).encode("utf-8")).hexdigest()


def _mind_digest(mind):
    return _digest({
        "values": mind.values, "buffer": list(mind.buffer),
        "effects": repr(mind.effects.stats),
        "hist": repr(mind.hist), "map": repr(mind.map),
        "last": repr(mind.last),
        "rng": repr(mind.rng.getstate()),
        "budget_rng": repr(mind._budget_rng.getstate()),
    })


def _tariff(available):
    if type(available) is not int or available < MIN_MEMORY:
        raise ValueError("actual personally stored history required")
    # One direct-outcome head, 3 updates, 1 prediction. Declared minimum
    # category-level tariff, not calibrated wall CPU or future runtime cost.
    return CognitiveWork(cycles=5, memory_items=available + REPLAYS,
                         replays=REPLAYS)


class PaidDistressWitness:
    """Single prospectively frozen opportunity per temporary engineering life."""

    def __init__(self, mode, seed):
        if mode not in MODES or type(seed) is not int or seed < 0:
            raise ValueError("fixed engineering mode and life seed required")
        self.mode = mode
        self.seed = seed
        self.steps = 0
        self.first = None
        self.pending = None
        self._reference = None
        self._captured = False

    def after_choice_before_world(self, mind, cap, budget, action, param):
        if self.pending is not None:
            raise RuntimeError("previous forecast has no observed outcome")
        if self._captured or len(mind.buffer) < MIN_MEMORY:
            return
        if type(mind) is not Mind:
            raise PermissionError("reference I3 Mind only")
        if tuple(cap["body"]) != budget.body:
            raise RuntimeError("actual first-person body mismatches native allowance")

        self._captured = True  # at most one opportunity, including rejected ones
        original = _mind_digest(mind)
        before_work = budget.work
        tariff = _tariff(len(mind.buffer))
        energy, vigilance = cognitive_cost(budget.laws, tariff)
        # Protect the reference action after its normal paid decision. The
        # extra cognitive budget MUST NOT make the motor command impossible.
        after_energy = budget.remaining[0] - energy
        fundable = (budget.remaining[0] >= energy and
                    budget.remaining[4] >= vigilance and
                    (action is None or action == "dormir" or
                     after_energy >= ACTION_COSTS[action]))
        if not fundable:
            self.first = {
                "status": "NO_FUNDED_FORECAST",
                "step": self.steps + 1,
                "selected_action": action,
                "selected_param": param,
                "eligible_memory_count": len(mind.buffer),
                "shadow_work": {"cycles": 0, "simulated_steps": 0,
                                "memory_items": 0, "replays": 0},
                "energy_paid": 0.0, "vigilance_paid": 0.0,
                "prediction_sha256": None,
                "result": None,
            }
            if budget.work != before_work or _mind_digest(mind) != original:
                raise RuntimeError("unfunded attempt mutated action budget/mind")
            return
        if not budget.try_spend(tariff):
            raise RuntimeError("native prepayment refused a budget admissible by laws")

        # Critical: not a single shadow training/forecast operation is
        # performed until AFTER native pre-authorization succeeds.
        memories = tuple(mind.buffer)
        head = PersonalDistressHead(mind)
        ordered = tuple(sorted(range(len(memories)),
                               key=lambda i: -memories[i][0])[:REPLAYS])
        random = random_content_indices(
            eligible=len(memories), count=REPLAYS,
            life_seed=self.seed, sleep_ordinal=self.steps + 1)
        selected = ordered if self.mode == "priority" else random
        baseline_prediction = head.predict(cap["body"])
        head.apply(memories, selected)  # three actual updates in ALL modes
        forecast = (baseline_prediction if self.mode == "discard"
                    else head.predict(cap["body"]))
        if not isfinite(forecast):
            raise RuntimeError("nonfinite paid-body distress forecast")
        if _mind_digest(mind) != original:
            raise RuntimeError("shadow training changed live mind or RNG")
        if budget.work != CognitiveWork(
            cycles=before_work.cycles + tariff.cycles,
            simulated_steps=before_work.simulated_steps,
            memory_items=before_work.memory_items + tariff.memory_items,
            replays=before_work.replays + tariff.replays):
            raise RuntimeError("native budget did not prepay exactly declared head")
        self._reference = head
        identity = f"{self.seed}-{self.mode}-{self.steps + 1}"
        sealed = {
            "identity": identity, "mode": self.mode,
            "actual_first_person_body": tuple(cap["body"]),
            "actual_selected_action": action, "actual_selected_param": param,
            "past_buffer_digest": _digest(memories),
            "source_mind_digest": original,
            "trained_indices": head.trained_indices,
            "training_updates_actually_executed": head.training_updates,
            "prediction": forecast,
            "no_future_body_available": True,
        }
        signature = _digest(sealed)
        self.pending = (sealed, signature)
        self.first = {
            "status": "FUNDED_FROZEN_AWAITING_ACTUAL_OUTCOME",
            "step": self.steps + 1,
            "selected_action": action, "selected_param": param,
            "eligible_memory_count": len(memories),
            "training_updates_executed": head.training_updates,
            "trained_memory_indices": list(selected),
            "shadow_work": {
                "cycles": tariff.cycles, "simulated_steps": tariff.simulated_steps,
                "memory_items": tariff.memory_items, "replays": tariff.replays,
            },
            "energy_paid": energy, "vigilance_paid": vigilance,
            "prediction_sha256": signature,
            "result": None,
        }

    def after_actual_world_step(self, action, param, result):
        self.steps += 1
        if self.pending is None:
            return
        sealed, signature = self.pending
        if (_digest(sealed) != signature or self.first["prediction_sha256"] != signature
                or self.first["step"] != self.steps
                or action != sealed["actual_selected_action"]
                or param != sealed["actual_selected_param"]):
            raise RuntimeError("outcome cannot be matched to precommitted choice/forecast")
        if type(result.get("dead")) not in (tuple, list):
            raise ValueError("actual world death-cause sequence required")
        observed = self._reference.target_from_actual_outcome(
            result["body"], bool(result["dead"]))
        score = (sealed["prediction"] - observed) ** 2
        if not isfinite(score):
            raise RuntimeError("impossible first-person squared error")
        self.first["result"] = {
            "status": "ACTUAL_FIRST_PERSON_OUTCOME_SCORED",
            "terminal_observed": bool(result["dead"]),
            "observed_intrinsic_reward": observed,
            "frozen_prediction": sealed["prediction"],
            "squared_loss": score,
            "same_actual_live_action_not_off_policy": True,
        }
        self.first["status"] = "PAID_AND_SCORED"
        self.pending = None

    def report(self):
        if self.pending is not None:
            raise RuntimeError("paid prediction missing original outcome")
        return {
            "schema": SCHEMA, "mode": self.mode, "life_seed": self.seed,
            "steps": self.steps,
            "status": (self.first["status"] if self.first is not None
                       else "NO_ELIGIBLE_HISTORY"),
            "first": self.first,
            "fee_paid_in_native_world_step": bool(
                self.first and self.first["status"] == "PAID_AND_SCORED"),
            "no_shadow_to_action_control": True,
            "scientific_lives": 0,
            "scientific_verdict": "NOT_ISSUED",
        }


def run_paid_reference(genome, spec, seed, mode, horizon=HORIZON):
    if mode not in MODES:
        raise ValueError("unknown shadow content branch")
    monitor = PaidDistressWitness(mode, seed)
    original_decide = Mind.decide
    original_step = World.step

    def decide_spy(mind, cap, allowance):
        action, param, work, info = original_decide(mind, cap, allowance)
        monitor.after_choice_before_world(mind, cap, allowance, action, param)
        return action, param, allowance.work, info

    def step_spy(world, action, param, work):
        result = original_step(world, action, param, work)
        monitor.after_actual_world_step(action, param, result)
        return result

    # Scoped to one synchronous reference life; no scientific cohort or
    # modification of source modules/World physiology/action authority.
    with patch.object(Mind, "decide", decide_spy), patch.object(World, "step", step_spy):
        life = run_life(genome, spec, seed, horizon)
    report = monitor.report()
    if life["steps_lived"] != report["steps"]:
        raise RuntimeError("World steps missing from external engineering witness")
    return life, report


def rehearse():
    rows = []
    for seed in SEEDS:
        paired = []
        for mode in MODES:
            life, witness = run_paid_reference(
                midpoint(), dev_open_field(), seed, mode)
            paired.append((mode, life, witness))
        reference = paired[0][1]
        equal = all(all(life[k] == reference[k] for k in (
            "trace_head", "evidence_head", "steps_lived", "terminal",
            "death_causes", "actions", "final_body", "cognitive_accounting"))
            for _, life, _ in paired)
        if not equal:
            raise RuntimeError("equal-priced shadow branches changed physical decisions")
        firsts = [receipt["first"] for _, _, receipt in paired]
        if any(event is None or event["status"] != "PAID_AND_SCORED"
               for event in firsts):
            raise RuntimeError("fixed engineering pair lacked a funded, scored window")
        if len({(e["energy_paid"], e["vigilance_paid"],
                 tuple(e["shadow_work"].items())) for e in firsts}) != 1:
            raise RuntimeError("not equal physical tariffs across three branches")
        rows.append({
            "life_seed": seed,
            "branches": [dict(mode=mode, witness=receipt)
                         for mode, _, receipt in paired],
            "all_three_paid_branch_physical_trace_parity": equal,
            "actual_world_energy_paid_per_arm": firsts[0]["energy_paid"],
            "actual_world_vigilance_paid_per_arm": firsts[0]["vigilance_paid"],
            "reference_life_terminal": reference["terminal"],
        })
    return {
        "schema": SCHEMA, "status": "THREE_ARM_PAID_SHADOW_ENGINEERING_ONLY",
        "engineering_matched_triplets": len(rows),
        "funded_and_scored_events": sum(
            b["witness"]["status"] == "PAID_AND_SCORED"
            for row in rows for b in row["branches"]),
        "equal_cost_and_physical_triplets": sum(
            row["all_three_paid_branch_physical_trace_parity"] for row in rows),
        "priority_lower_sq_loss_than_random": sum(
            row["branches"][0]["witness"]["first"]["result"]["squared_loss"] <
            row["branches"][1]["witness"]["first"]["result"]["squared_loss"]
            for row in rows),
        "random_lower_sq_loss_than_priority": sum(
            row["branches"][1]["witness"]["first"]["result"]["squared_loss"] <
            row["branches"][0]["witness"]["first"]["result"]["squared_loss"]
            for row in rows),
        "rows": rows,
        "no_independently_witnessed_iid_ecology": True,
        "scientific_lives": 0, "scientific_verdict": "NOT_ISSUED",
        "no_stage2_2_activation": True,
        "cost_tariff_is_provisional_not_cpu_calibrated": True,
    }


def main():
    print(json.dumps(rehearse(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
