"""Prospective longitudinal body-paid compact self-distress forecasts.

Engineering-only synchronous observer; never feeds a forecast to action control.
The observer refits on the current actual personal memories at each of twelve
predeclared chronological eligible steps, pays native two-currency World work
BEFORE computation and seals every forecast BEFORE the actual next outcome.
No original/scientific World source or policy is changed.
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import fsum, isfinite
from unittest.mock import patch

from ..modules.body import CognitiveWork, cognitive_cost
from ..modules.genome import midpoint
from ..modules.mind import Mind
from ..modules.stage2_replay_content_selection import random_content_indices
from ..modules.world import World
from ..runtime.life import run_life
from .dev_worlds import dev_open_field
from .stage2_compact_distress_shadow import (
    CompactPersonalDistressHead, preauthorize, work_envelope)
from .stage2_compact_paid_first_person_engineering import (
    MODES, PARITY_FIELDS, _source_seal)

SCHEMA = "i3-stage2.1-repeated-paid-compact-prequential-engineering/v1"
SEEDS = (950041, 950042, 950043)
HORIZON = 80
SLOTS = 12
K = 3
MIN_MEMORIES = 6


def _sha(record):
    return sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":"), allow_nan=False,
        default=str).encode("utf-8")).hexdigest()


class RepeatedPaidWitness:
    """At most twelve chronological eligible slots, paid or refused."""

    def __init__(self, *, mode, seed):
        if mode not in MODES or type(seed) is not int or seed < 0:
            raise ValueError("explicit engineering mode and seed required")
        self.mode = mode
        self.seed = seed
        self.steps = 0
        self.slots = []
        self.pending = None
        self._head = None

    def after_choice(self, mind, capture, budget, action, param, work):
        if self.pending is not None:
            raise RuntimeError("prior sealed prediction missing factual outcome")
        if len(self.slots) >= SLOTS or len(mind.buffer) < MIN_MEMORIES:
            return
        if (type(mind) is not Mind or tuple(capture["body"]) != budget.body
                or work != budget.work):
            raise PermissionError("actual reference first-person choice required")

        original = _source_seal(mind)
        before_work = budget.work
        n = len(mind.buffer)
        incremental = work_envelope(n, K)
        energy, vigilance = cognitive_cost(budget.laws, incremental)
        item = {
            "assigned_slot": len(self.slots) + 1,
            "actual_step": self.steps + 1,
            "before_action": action,
            "before_param": param,
            "eligible_memories": n,
            "status": "UNSETTLED",
            "incremental_work": None,
            "energy_paid": 0.0,
            "vigilance_paid": 0.0,
            "prediction_sha256": None,
            "selected_indices": None,
            "training_updates": 0,
            "result": None,
        }
        # Reserve slot before touching the optional learner. A denied
        # opportunity remains in the 12-slot denominator and is never rerun.
        self.slots.append(item)
        if not preauthorize(budget, n=n, k=K, action=action):
            item["status"] = "NO_FUNDED_FORECAST"
            if budget.work != before_work or _source_seal(mind) != original:
                raise RuntimeError("denied head changed original cognition/bill")
            return
        expected = CognitiveWork(
            cycles=before_work.cycles + incremental.cycles,
            simulated_steps=before_work.simulated_steps + incremental.simulated_steps,
            memory_items=before_work.memory_items + incremental.memory_items,
            replays=before_work.replays + incremental.replays)
        if budget.work != expected:
            raise RuntimeError("native allowance changed charged work categories")

        # Everything below this line happens AFTER the native allowance grant.
        memory = tuple(mind.buffer)
        head = CompactPersonalDistressHead(mind)
        priority = tuple(sorted(
            range(n), key=lambda i: -memory[i][0])[:K])
        random = random_content_indices(
            eligible=n, count=K, life_seed=self.seed,
            sleep_ordinal=self.steps + 1)
        indices = priority if self.mode == "priority" else random
        without_learning = head.predict(capture["body"])
        head.apply(memory, indices)
        forecast = (without_learning if self.mode == "discard"
                    else head.predict(capture["body"]))
        if not isfinite(forecast) or _source_seal(mind) != original:
            raise RuntimeError("nonfinite forecast or changed living Mind")

        payload = {
            "schema": SCHEMA, "seed": self.seed, "mode": self.mode,
            "slot": item["assigned_slot"], "actual_step": item["actual_step"],
            "action_before_funding": action, "param_before_funding": param,
            "body_before_world": tuple(capture["body"]),
            "mind_source_sha256": original,
            "actual_personal_history_sha256": _sha(memory),
            "priority_indices": priority,
            "random_indices": random,
            "selected_indices": indices,
            "training_updates": head.training_updates,
            "forecast": forecast,
            "work": {
                "cycles": incremental.cycles,
                "simulated_steps": incremental.simulated_steps,
                "memory_items": incremental.memory_items,
                "replays": incremental.replays,
            },
            "no_future_outcome_at_freeze": True,
        }
        digest = _sha(payload)
        self.pending = (payload, digest, expected)
        self._head = head
        item.update({
            "status": "PAID_FROZEN_AWAITING_OUTCOME",
            "incremental_work": payload["work"],
            "energy_paid": energy,
            "vigilance_paid": vigilance,
            "prediction_sha256": digest,
            "selected_indices": list(indices),
            "priority_indices": list(priority),
            "random_indices": list(random),
            "training_updates": head.training_updates,
        })

    def after_world(self, world, action, param, work, result):
        self.steps += 1
        if self.pending is None:
            return
        sealed, digest, expected = self.pending
        item = self.slots[-1]
        if (_sha(sealed) != digest or item["prediction_sha256"] != digest
                or item["actual_step"] != self.steps
                or action != sealed["action_before_funding"]
                or param != sealed["param_before_funding"]
                or work != expected):
            raise RuntimeError("actual outcome mismatched frozen personal forecast")
        if type(result.get("dead")) not in (tuple, list):
            raise RuntimeError("missing genuine observed terminal result")
        account = result.get("cognitive_accounting")
        if type(account) is not dict:
            raise RuntimeError("native bodily cost receipt missing")
        e, v = cognitive_cost(world.laws, expected)
        for currency, amount in (("energy", e), ("vigilance", v)):
            receipt = account.get(currency)
            if (type(receipt) is not dict
                    or type(receipt.get("paid")) not in (int, float)
                    or abs(receipt["paid"] - amount) > 1e-10
                    or receipt.get("unpaid") != 0):
                raise RuntimeError("World did not fully debit native cognitive work")
        target = self._head.target_from_actual_outcome(
            result["body"], bool(result["dead"]))
        loss = (sealed["forecast"] - target) ** 2
        if not isfinite(loss):
            raise RuntimeError("invalid proper factual next-body squared loss")
        item["result"] = {
            "status": "SCORED_ACTUAL_NEXT_BODY",
            "terminal_observed": bool(result["dead"]),
            "target": target, "forecast": sealed["forecast"],
            "squared_loss": loss,
            "full_step_world_energy_paid": e,
            "full_step_world_vigilance_paid": v,
            "native_unpaid": False,
            "factual_executed_action_only": True,
        }
        item["status"] = "PAID_AND_SCORED"
        self.pending = None
        self._head = None

    def report(self):
        if self.pending is not None:
            raise RuntimeError("prospectively frozen event has no actual World receipt")
        observed = [x for x in self.slots if x["status"] == "PAID_AND_SCORED"]
        refused = [x for x in self.slots if x["status"] == "NO_FUNDED_FORECAST"]
        if len(observed) + len(refused) != len(self.slots):
            raise RuntimeError("unaccounted assigned longitudinal opportunity")
        return {
            "schema": SCHEMA, "mode": self.mode, "life_seed": self.seed,
            "steps_lived": self.steps,
            "eligible_assigned_slots": len(self.slots),
            "scored_actual_next_bodies": len(observed),
            "unfunded_slots": len(refused),
            "unrealized_terminal_or_horizon_slots": SLOTS - len(self.slots),
            "distinct_observed_targets": len({
                x["result"]["target"] for x in observed}),
            "sum_observed_squared_loss": fsum(
                x["result"]["squared_loss"] for x in observed),
            "slots": self.slots,
            "predictions_never_control_actions": True,
            "laboratory_digest_work_not_charged": True,
            "host_cpu_to_body_calibration": False,
            "scientific_lives": 0, "scientific_verdict": "NOT_ISSUED",
        }


def run_repeated(genome, spec, seed, mode, horizon=HORIZON):
    witness = RepeatedPaidWitness(mode=mode, seed=seed)
    decide = Mind.decide
    step = World.step

    def decide_spy(mind, capture, allowance):
        action, param, work, info = decide(mind, capture, allowance)
        witness.after_choice(mind, capture, allowance, action, param, work)
        return action, param, allowance.work, info

    def step_spy(world, action, param, work):
        result = step(world, action, param, work)
        witness.after_world(world, action, param, work, result)
        return result

    with patch.object(Mind, "decide", decide_spy), patch.object(
            World, "step", step_spy):
        life = run_life(genome, spec, seed, horizon)
    report = witness.report()
    if life["steps_lived"] != report["steps_lived"]:
        raise RuntimeError("engineering step audit differs from actual World")
    return life, report


def rehearse():
    rows = []
    for seed in SEEDS:
        reference = run_life(
            midpoint(), dev_open_field(), seed, HORIZON, keep_trace=True)
        branches = []
        for mode in MODES:
            life, report = run_repeated(
                midpoint(), dev_open_field(), seed, mode, HORIZON)
            branches.append((mode, life, report))
        first_life = branches[0][1]
        parity = all(all(life[k] == first_life[k] for k in PARITY_FIELDS)
                     for _, life, _ in branches)
        if not parity:
            raise RuntimeError("equal paid longitudinal arms changed physical path")
        controls = [receipt for _, _, receipt in branches]
        if len({tuple(s["actual_step"] for s in c["slots"]) for c in controls}) != 1:
            raise RuntimeError("assigned slot chronology not matched")
        if len({tuple((s["status"], s["energy_paid"], s["vigilance_paid"])
                     for s in c["slots"]) for c in controls}) != 1:
            raise RuntimeError("different paid admissions despite identical bodies")
        for slots in zip(*(c["slots"] for c in controls)):
            if any(s["status"] == "PAID_AND_SCORED" for s in slots):
                if any(s["status"] != "PAID_AND_SCORED" for s in slots):
                    raise RuntimeError("missing matched factual prequential outcome")
                if len({s["result"]["target"] for s in slots}) != 1:
                    raise RuntimeError("matched paid arms saw differing outcomes")
            if len({tuple(s["selected_indices"] or ()) for s in slots}) < 1:
                raise RuntimeError("unmatched selected history")
        first = controls[0]["slots"]
        initial_choice_matches = True
        if first:
            t = first[0]["actual_step"]
            if t > len(reference["trace"]):
                raise RuntimeError("unpriced reference ended before first eligible choice")
            baseline_step = reference["trace"][t - 1]
            initial_choice_matches = all(
                c["slots"][0]["before_action"] == baseline_step["action"]
                and c["slots"][0]["before_param"] == baseline_step["param"]
                for c in controls)
            if not initial_choice_matches:
                raise RuntimeError("first prepayment changed action already selected")
        rows.append({
            "seed": seed, "paid_triplet_full_physical_cognition_parity": parity,
            "first_precharge_motor_matches_reference": initial_choice_matches,
            "reference_steps_lived": reference["steps_lived"],
            "arms": [{"mode": mode, "report": report}
                     for mode, _, report in branches],
        })
    scored = sum(b["report"]["scored_actual_next_bodies"]
                 for row in rows for b in row["arms"])
    refusals = sum(b["report"]["unfunded_slots"]
                   for row in rows for b in row["arms"])
    missing = sum(b["report"]["unrealized_terminal_or_horizon_slots"]
                  for row in rows for b in row["arms"])
    priority_wins = random_wins = ties = 0
    distinct_targets = set()
    for row in rows:
        streams = [b["report"]["slots"] for b in row["arms"]]
        for triple in zip(*streams):
            if triple[0]["status"] != "PAID_AND_SCORED":
                continue
            a, b = (triple[i]["result"]["squared_loss"] for i in (0, 1))
            priority_wins += a < b
            random_wins += b < a
            ties += a == b
            distinct_targets.add(triple[0]["result"]["target"])
    return {
        "schema": SCHEMA,
        "status": "REPEATED_COMPACT_PAID_ENGINEERING_ONLY",
        "fixed_engineering_source_units": len(rows),
        "engineering_full_lives": len(rows) * (len(MODES) + 1),
        "predeclared_eligible_slots_per_paid_arm": SLOTS,
        "assigned_paid_slots": scored + refusals,
        "actual_scored_first_person_forecasts": scored,
        "unfunded_attempts": refusals,
        "censored_missing_slots": missing,
        "paid_triplet_physical_parity": sum(
            r["paid_triplet_full_physical_cognition_parity"] for r in rows),
        "first_choice_reference_parity": sum(
            r["first_precharge_motor_matches_reference"] for r in rows),
        "distinct_actual_target_values": len(distinct_targets),
        "matched_observed_priority_lower_loss": priority_wins,
        "matched_observed_random_lower_loss": random_wins,
        "matched_observed_ties": ties,
        "rows": rows,
        "calibrated_host_cpu_to_body": False,
        "independent_iid_ecology": False,
        "scientific_lives": 0, "scientific_verdict": "NOT_ISSUED",
        "stage2_2_go": False,
    }


if __name__ == "__main__":
    print("I3_REPEATED_PAID_PREQUENTIAL_RESULT="+json.dumps(
        rehearse(), sort_keys=True))
