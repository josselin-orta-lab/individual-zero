"""First genuinely body-paid compact distress head on technical I3 lives.

ENGINEERING ONLY. Scoped synchronous external observer after reference Mind
has chosen; the unchanged native allowance authorizes compact work, and
unchanged World.step actually debits the full decision work before the
original motor command. All resulting predictions are external to control.
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import isfinite
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

SCHEMA = "i3-stage2.1-compact-actually-paid-first-person-engineering/v1"
MODES = ("priority", "random", "discard")
SEEDS = (940041, 940042, 940043)
HORIZON = 80
K = 3
MIN_MEMORIES = 6
PARITY_FIELDS = ("trace_head", "evidence_head", "steps_lived", "terminal",
                 "death_causes", "actions", "final_body", "cognitive_accounting")


def _sha(record):
    return sha256(json.dumps(record, sort_keys=True, separators=(",", ":"),
                             allow_nan=False, default=str).encode()).hexdigest()


def _source_seal(mind):
    """Laboratory-only integrity witness. Not a live decision readout."""
    return _sha({
        "values": mind.values, "buffer": list(mind.buffer),
        "effects": repr(mind.effects.stats),
        "map": repr(mind.map), "hist": repr(mind.hist),
        "rng": repr(mind.rng.getstate()),
        "budget_rng": repr(mind._budget_rng.getstate()),
        "last": repr(mind.last),
    })


class CompactPaidFirstPersonWitness:
    def __init__(self, *, mode, seed):
        if mode not in MODES or type(seed) is not int or seed < 0:
            raise ValueError("exact engineering mode and life seed required")
        self.mode = mode
        self.seed = seed
        self.steps = 0
        self.first = None
        self.pending = None
        self._head = None
        self._attempted = False

    def after_choice(self, mind, capture, budget, action, param, work):
        if self.pending is not None:
            raise RuntimeError("a frozen first-person prediction has no actual outcome")
        if self._attempted or len(mind.buffer) < MIN_MEMORIES:
            return
        if type(mind) is not Mind or tuple(capture["body"]) != budget.body:
            raise PermissionError("reference Mind and its real perception required")
        if work != budget.work:
            raise RuntimeError("baseline choice work differs from native allowance")
        self._attempted = True
        original = _source_seal(mind)
        n = len(mind.buffer)
        before_work = budget.work
        incremental = work_envelope(n, K)
        energy, vigilance = cognitive_cost(budget.laws, incremental)

        # This is the one and only admission gate: perform no compact
        # constructor, selection, learning, or readout until it succeeds.
        if not preauthorize(budget, n=n, k=K, action=action):
            self.first = {
                "status": "NO_FUNDED_FORECAST", "step": self.steps + 1,
                "action_before_funding": action, "param_before_funding": param,
                "eligible_memories": n, "incremental_work": None,
                "energy_paid": 0.0, "vigilance_paid": 0.0,
                "prediction_sha256": None, "result": None}
            if budget.work != before_work or _source_seal(mind) != original:
                raise RuntimeError("rejected work mutated live Mind or allowance")
            return

        expected = CognitiveWork(
            cycles=before_work.cycles+incremental.cycles,
            simulated_steps=before_work.simulated_steps+incremental.simulated_steps,
            memory_items=before_work.memory_items+incremental.memory_items,
            replays=before_work.replays+incremental.replays)
        if budget.work != expected:
            raise RuntimeError("native preauthorization changed work categories")
        personal = tuple(mind.buffer)
        head = CompactPersonalDistressHead(mind)
        priority = tuple(sorted(range(n),
                                key=lambda i: -personal[i][0])[:K])
        random = random_content_indices(
            eligible=n, count=K, life_seed=self.seed,
            sleep_ordinal=self.steps+1)
        selection = priority if self.mode == "priority" else random
        # Identical ordering/selection and actual three training operations
        # in each arm, even when training is intentionally discarded.
        baseline_prediction = head.predict(capture["body"])
        head.apply(personal, selection)
        forecast = (baseline_prediction if self.mode == "discard"
                    else head.predict(capture["body"]))
        if not isfinite(forecast) or _source_seal(mind) != original:
            raise RuntimeError("shadow forecast nonfinite or mutated live cognition")
        seal_payload = {
            "schema": SCHEMA,
            "mode": self.mode, "seed": self.seed, "step": self.steps+1,
            "real_selected_action": action, "real_selected_param": param,
            "first_person_before_body": list(capture["body"]),
            "original_mind_sha256": original,
            "personal_buffer_sha256": _sha(personal),
            "both_selectors_executed": True,
            "priority_indices": list(priority),
            "random_indices": list(random),
            "trained_indices": list(selection),
            "trained_updates": head.training_updates,
            "frozen_prediction": forecast,
            "native_incremental_work": {
                "cycles": incremental.cycles,
                "simulated_steps": incremental.simulated_steps,
                "memory_items": incremental.memory_items,
                "replays": incremental.replays},
            "no_future_outcome_at_freeze": True,
        }
        digest = _sha(seal_payload)
        self.pending = (seal_payload, digest, expected)
        self._head = head
        self.first = {
            "status": "FUNDED_FROZEN_AWAITING_WORLD",
            "step": self.steps+1, "action_before_funding": action,
            "param_before_funding": param, "eligible_memories": n,
            "original_mind_sha256": original,
            "trained_updates": head.training_updates,
            "priority_indices": list(priority),
            "random_indices": list(random),
            "trained_indices": list(selection),
            "incremental_work": seal_payload["native_incremental_work"],
            "energy_paid": energy, "vigilance_paid": vigilance,
            "prediction_sha256": digest,
            "result": None,
        }

    def after_world(self, world, action, param, work, result):
        self.steps += 1
        if self.pending is None:
            return
        frozen, digest, expected = self.pending
        if (_sha(frozen) != digest or self.first["prediction_sha256"] != digest
                or self.first["step"] != self.steps or work != expected
                or action != frozen["real_selected_action"]
                or param != frozen["real_selected_param"]):
            raise RuntimeError("actual step disagrees with sealed paid choice")
        account = result.get("cognitive_accounting")
        if type(account) is not dict or type(result.get("dead")) not in (tuple, list):
            raise RuntimeError("missing native first-person payment/outcome receipt")
        actual_energy, actual_vigilance = cognitive_cost(world.laws, work)
        for currency, expected_paid in (("energy", actual_energy),
                                        ("vigilance", actual_vigilance)):
            receipt = account.get(currency)
            if (type(receipt) is not dict
                    or not isinstance(receipt.get("paid"), (int, float))
                    or abs(receipt["paid"]-expected_paid)>1e-10
                    or receipt.get("unpaid") != 0):
                raise RuntimeError("World.step did not physically pay the sealed work")
        target = self._head.target_from_actual_outcome(
            result["body"], bool(result["dead"]))
        loss = (frozen["frozen_prediction"]-target)**2
        if not isfinite(loss):
            raise RuntimeError("nonfinite direct factual forecast loss")
        self.first["result"] = {
            "status": "SCORED_ACTUAL_NEXT_FIRST_PERSON_BODY",
            "observed_intrinsic_reward": target,
            "frozen_prediction": frozen["frozen_prediction"],
            "squared_loss": loss,
            "terminal_observed": bool(result["dead"]),
            "native_world_paid_energy_full_step": actual_energy,
            "native_world_paid_vigilance_full_step": actual_vigilance,
            "native_world_unpaid": False,
            "same_factual_selected_motor_command": True,
        }
        self.first["status"] = "PAID_AND_SCORED"
        self.pending = None

    def report(self):
        if self.pending is not None:
            raise RuntimeError("frozen forecast was never settled by the World")
        return {
            "schema": SCHEMA,
            "mode": self.mode, "life_seed": self.seed, "steps": self.steps,
            "status": (self.first["status"] if self.first is not None
                       else "NO_ELIGIBLE_HISTORY"),
            "first": self.first, "scientific_lives": 0,
            "scientific_verdict": "NOT_ISSUED",
            "forecast_has_no_motor_authority": True,
            "laboratory_integrity_hashes_not_physically_priced": True,
            "compact_operator_tariff_not_cpu_to_energy_calibrated": True,
        }


def run_paid_compact(genome, spec, seed, mode, horizon=HORIZON):
    witness = CompactPaidFirstPersonWitness(mode=mode, seed=seed)
    original_decide = Mind.decide
    original_step = World.step

    def decide_spy(mind, capture, budget):
        action, param, work, info = original_decide(mind, capture, budget)
        witness.after_choice(mind, capture, budget, action, param, work)
        return action, param, budget.work, info

    def step_spy(world, action, param, work):
        outcome = original_step(world, action, param, work)
        witness.after_world(world, action, param, work, outcome)
        return outcome

    # Scope both hooks to this synchronous engineering-only run, restoring
    # them on success and exception without touching runtime/life.py.
    with patch.object(Mind, "decide", decide_spy), patch.object(
            World, "step", step_spy):
        life = run_life(genome, spec, seed, horizon)
    report = witness.report()
    if life["steps_lived"] != report["steps"]:
        raise RuntimeError("engineering World step accounting incomplete")
    return life, report


def rehearse():
    rows = []
    for seed in SEEDS:
        baseline = run_life(midpoint(), dev_open_field(), seed, HORIZON,
                            keep_trace=True)
        branches = []
        for mode in MODES:
            life, receipt = run_paid_compact(
                midpoint(), dev_open_field(), seed, mode, HORIZON)
            branches.append((mode, life, receipt))
        reference = branches[0][1]
        equal = all(all(life[key] == reference[key]
                        for key in PARITY_FIELDS)
                    for _, life, _ in branches)
        if not equal:
            raise RuntimeError("equal-paid compact heads changed live trajectories")
        events = [r["first"] for _, _, r in branches]
        if (any(e is None or e["status"] != "PAID_AND_SCORED"
                for e in events)
                or len({(e["energy_paid"], e["vigilance_paid"],
                         tuple(e["incremental_work"].items())) for e in events}) != 1):
            raise RuntimeError("missing or unequal paid first-person forecast")
        t = events[0]["step"]
        original_step = baseline["trace"][t-1]
        matched_initial_choice = all(
            e["action_before_funding"] == original_step["action"]
            and e["param_before_funding"] == original_step["param"]
            for e in events)
        if not matched_initial_choice:
            raise RuntimeError("compact observer changed selected motor command")
        rows.append({
            "seed": seed, "reference_life_steps": baseline["steps_lived"],
            "all_paid_physical_and_decision_traces_identical": equal,
            "precharge_motor_matches_unobserved_reference": matched_initial_choice,
            "actual_body_paid_energy": events[0]["energy_paid"],
            "actual_body_paid_vigilance": events[0]["vigilance_paid"],
            "first_event_step": t,
            "paid_arms": [{"mode": mode, "receipt": receipt}
                          for mode, _, receipt in branches],
        })
    return {
        "schema": SCHEMA,
        "status": "COMPACT_PAID_FIRST_PERSON_TECHNICAL_ONLY",
        "engineering_sources": len(rows),
        "engineering_actual_full_lives": len(rows)*(len(MODES)+1),
        "paid_forecasts_with_actual_next_outcomes": sum(
            b["receipt"]["status"] == "PAID_AND_SCORED"
            for row in rows for b in row["paid_arms"]),
        "paid_triplets_identical_full_physical_and_cognitive_traces": sum(
            row["all_paid_physical_and_decision_traces_identical"]
            for row in rows),
        "first_precharge_actions_match_reference": sum(
            row["precharge_motor_matches_unobserved_reference"]
            for row in rows),
        "priority_lower_squared_loss_than_random": sum(
            row["paid_arms"][0]["receipt"]["first"]["result"]["squared_loss"]
            < row["paid_arms"][1]["receipt"]["first"]["result"]["squared_loss"]
            for row in rows),
        "random_lower_squared_loss_than_priority": sum(
            row["paid_arms"][1]["receipt"]["first"]["result"]["squared_loss"]
            < row["paid_arms"][0]["receipt"]["first"]["result"]["squared_loss"]
            for row in rows),
        "rows": rows,
        "host_to_body_tariff_calibrated": False,
        "independent_iid_ecology_attested": False,
        "scientific_lives": 0, "scientific_verdict": "NOT_ISSUED",
        "stage2_2_go": False,
    }


if __name__ == "__main__":
    print("I3_COMPACT_PAID_FIRST_PERSON_RESULT="+json.dumps(rehearse(),sort_keys=True))
