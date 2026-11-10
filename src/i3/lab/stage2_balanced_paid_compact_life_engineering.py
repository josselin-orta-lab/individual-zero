"""Equal-inference and native-body-paid compact distress forecast engineering.

NEW fixed temporary engineering lives only, never closed scientific originals.
The reference P1.3 chooses the actual motor action before any optional work.
The same native CognitiveBudget funds all computations before their execution.
All instrumentation, proof hashes and method spies are external laboratory
custody, not an enacted endogenous ability or calibrated CPU->body model.
"""
from __future__ import annotations

from math import fsum, isfinite
from unittest.mock import patch
import json

from ..modules import stage2_replay_content_selection as selection
from ..modules.body import CognitiveWork, cognitive_cost
from ..modules.genome import midpoint
from ..modules.mind import Mind
from ..modules.world import World
from ..runtime.life import run_life
from .dev_worlds import dev_open_field
from .stage2_compact_distress_shadow import (
    CompactPersonalDistressHead, preauthorize, work_envelope)
from .stage2_compact_host_operator_coverage import balanced_refit_forecast
from .stage2_compact_paid_first_person_engineering import (
    MODES, PARITY_FIELDS, _source_seal)
from .stage2_repeated_paid_distress_prequential_engineering import (
    RepeatedPaidWitness, _sha, K, SLOTS, MIN_MEMORIES)

SCHEMA = "i3-stage2.1-balanced-paid-compact-first-person-engineering/v1"
SEEDS = (990041, 990042, 990043)
HORIZON = 80


class BalancedPaidWitness(RepeatedPaidWitness):
    """Twelve predeclared paid/refused chronological opportunities per life."""

    def after_choice(self, mind, capture, budget, action, param, work):
        if self.pending is not None:
            raise RuntimeError("unsettled sealed first-person outcome")
        if len(self.slots) >= SLOTS or len(mind.buffer) < MIN_MEMORIES:
            return
        if (type(mind) is not Mind or tuple(capture["body"]) != budget.body
                or work != budget.work):
            raise PermissionError("actual reference first-person choice required")
        original = _source_seal(mind)
        n = len(mind.buffer)
        before_work = budget.work
        incremental = work_envelope(n, K)
        energy, vigilance = cognitive_cost(budget.laws, incremental)
        item = {
            "assigned_slot": len(self.slots) + 1,
            "actual_step": self.steps + 1,
            "before_action": action, "before_param": param,
            "eligible_memories": n,
            "status": "UNSETTLED",
            "incremental_work": None,
            "energy_paid": 0.0, "vigilance_paid": 0.0,
            "prediction_sha256": None,
            "selected_indices": None,
            "training_updates": 0,
            "pretraining_predict_calls": None,
            "priority_key_visits": None,
            "hmac_identity_messages": None,
            "result": None,
        }
        # Register before funding. A denied opportunity is permanently
        # retained; no shadow head, sorting, hashing or replay may happen.
        self.slots.append(item)
        if not preauthorize(budget, n=n, k=K, action=action):
            item["status"] = "NO_FUNDED_FORECAST"
            if budget.work != before_work or _source_seal(mind) != original:
                raise RuntimeError("unfunded attempt mutated Mind or allowance")
            return
        expected = CognitiveWork(
            cycles=before_work.cycles + incremental.cycles,
            simulated_steps=before_work.simulated_steps+incremental.simulated_steps,
            memory_items=before_work.memory_items+incremental.memory_items,
            replays=before_work.replays+incremental.replays)
        if budget.work != expected:
            raise RuntimeError("CognitiveBudget did not fund declared complete work")

        # NO optional operation above this line; this is the funded boundary.
        memory = tuple(mind.buffer)
        head = CompactPersonalDistressHead(mind)
        priority_visits = 0

        def priority_key(i):
            nonlocal priority_visits
            priority_visits += 1
            return -memory[i][0]

        priority = tuple(sorted(range(n), key=priority_key)[:K])
        actual_hmac_new = selection.hmac.new
        hmac_calls = 0

        def counted_hmac(*args, **kwargs):
            nonlocal hmac_calls
            hmac_calls += 1
            return actual_hmac_new(*args, **kwargs)

        with patch.object(selection.hmac, "new", counted_hmac):
            random = selection.random_content_indices(
                eligible=n, count=K, life_seed=self.seed,
                sleep_ordinal=self.steps+1)
        indices = priority if self.mode == "priority" else random

        actual_predict = CompactPersonalDistressHead.predict
        predict_calls = 0

        def counted_predict(head_instance, before):
            nonlocal predict_calls
            predict_calls += 1
            return actual_predict(head_instance, before)

        # All three modes ALWAYS perform pretraining inference, three
        # genuine personal updates, and posttraining inference.
        with patch.object(CompactPersonalDistressHead, "predict",
                          counted_predict):
            trained = balanced_refit_forecast(
                head=head, memory=memory, indices=indices,
                body=capture["body"], mode=self.mode)
        forecast = trained["forecast"]
        if (priority_visits != n or hmac_calls != n
                or predict_calls != K+2
                or trained["updates"] != K
                or head.trained_indices != indices
                or not trained["posttraining_forecast_computed"]
                or not isfinite(forecast)
                or _source_seal(mind) != original):
            raise RuntimeError("funded predictor violated actual-compute or source guard")

        payload = {
            "schema": SCHEMA, "seed": self.seed, "mode": self.mode,
            "slot": item["assigned_slot"], "actual_step": item["actual_step"],
            "action_before_funding": action, "param_before_funding": param,
            "body_before_world": tuple(capture["body"]),
            "mind_source_sha256": original,
            "actual_personal_history_sha256": _sha(memory),
            "priority_indices": priority, "random_indices": random,
            "selected_indices": indices,
            "training_updates": head.training_updates,
            "host_predict_calls": predict_calls,
            "host_priority_key_visits": priority_visits,
            "host_hmac_identity_messages": hmac_calls,
            "posttraining_inference_executed_even_if_discarded": True,
            "forecast": forecast,
            "work": {
                "cycles": incremental.cycles,
                "simulated_steps": incremental.simulated_steps,
                "memory_items": incremental.memory_items,
                "replays": incremental.replays},
            "no_future_outcome_at_freeze": True,
        }
        digest = _sha(payload)
        self.pending = (payload, digest, expected)
        self._head = head
        item.update({
            "status": "PAID_FROZEN_AWAITING_OUTCOME",
            "incremental_work": payload["work"],
            "energy_paid": energy, "vigilance_paid": vigilance,
            "prediction_sha256": digest,
            "selected_indices": list(indices),
            "priority_indices": list(priority),
            "random_indices": list(random),
            "training_updates": head.training_updates,
            "pretraining_predict_calls": predict_calls,
            "priority_key_visits": priority_visits,
            "hmac_identity_messages": hmac_calls,
            "posttraining_inference_executed": True,
        })

    def report(self):
        r = super().report()  # native World outcome settlement and null custody
        r["schema"] = SCHEMA
        r["actual_host_inference_count_prospectively_matched"] = all(
            s["pretraining_predict_calls"] == K+2 and
            s["priority_key_visits"] == s["eligible_memories"] and
            s["hmac_identity_messages"] == s["eligible_memories"] and
            s["training_updates"] == K
            for s in self.slots if s["status"] == "PAID_AND_SCORED")
        r["scope"] = "SYNCHRONOUS_ENGINEERING_REFERENCE_ONLY"
        r["full_host_cpu_to_body_calibration"] = False
        return r


def run_balanced(genome, spec, seed, mode, horizon=HORIZON):
    witness = BalancedPaidWitness(mode=mode, seed=seed)
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

    # No mutation of the original source modules and never concurrent.
    with patch.object(Mind, "decide", decide_spy), patch.object(
            World, "step", step_spy):
        life = run_life(genome, spec, seed, horizon)
    report = witness.report()
    if life["steps_lived"] != report["steps_lived"]:
        raise RuntimeError("World step witness and actual Life diverged")
    return life, report


def rehearse():
    rows = []
    for seed in SEEDS:
        unpaid_reference = run_life(
            midpoint(), dev_open_field(), seed, HORIZON, keep_trace=True)
        branches = []
        for mode in MODES:
            life, receipt = run_balanced(
                midpoint(), dev_open_field(), seed, mode, HORIZON)
            branches.append((mode, life, receipt))
        first_life = branches[0][1]
        equal = all(all(life[k] == first_life[k] for k in PARITY_FIELDS)
                    for _, life, _ in branches)
        if not equal:
            raise RuntimeError("balanced equally-paid modes changed life trajectory")
        receipts = [r for _, _, r in branches]
        if len({tuple(s["actual_step"] for s in r["slots"])
                for r in receipts}) != 1:
            raise RuntimeError("chronological assigned opportunities disagree")
        if len({tuple((s["status"], s["energy_paid"], s["vigilance_paid"])
                      for s in r["slots"]) for r in receipts}) != 1:
            raise RuntimeError("native physical tariffs or funding admissions differ")
        for triple in zip(*(r["slots"] for r in receipts)):
            if any(s["status"] == "PAID_AND_SCORED" for s in triple):
                if (any(s["status"] != "PAID_AND_SCORED" for s in triple)
                        or len({s["result"]["target"] for s in triple}) != 1
                        or len({s["pretraining_predict_calls"] for s in triple}) != 1
                        or len({s["priority_key_visits"] for s in triple}) != 1
                        or len({s["hmac_identity_messages"] for s in triple}) != 1):
                    raise RuntimeError("mismatched equally-paid observed computation")
            if any(s["status"] == "NO_FUNDED_FORECAST" for s in triple):
                if any(s["status"] != "NO_FUNDED_FORECAST" for s in triple):
                    raise RuntimeError("funding rejection not matched")
        initial_choice_equal = True
        if receipts[0]["slots"]:
            t = receipts[0]["slots"][0]["actual_step"]
            if t > len(unpaid_reference["trace"]):
                raise RuntimeError("reference ends before first funded opportunity")
            ref = unpaid_reference["trace"][t-1]
            initial_choice_equal = all(
                r["slots"][0]["before_action"] == ref["action"] and
                r["slots"][0]["before_param"] == ref["param"]
                for r in receipts)
            if not initial_choice_equal:
                raise RuntimeError("extra cognition changed precharge motor choice")
        rows.append({
            "seed": seed,
            "paid_three_arm_full_trajectory_parity": equal,
            "first_precharge_motor_matches_unpriced_reference":
                initial_choice_equal,
            "unpriced_reference_steps_lived": unpaid_reference["steps_lived"],
            "arms": [{"mode": mode, "report": report}
                     for mode, _, report in branches],
        })

    scored = sum(a["report"]["scored_actual_next_bodies"]
                 for row in rows for a in row["arms"])
    refused = sum(a["report"]["unfunded_slots"]
                  for row in rows for a in row["arms"])
    censored = sum(a["report"]["unrealized_terminal_or_horizon_slots"]
                   for row in rows for a in row["arms"])
    pwins = rwins = ties = 0
    observed_targets = set()
    for row in rows:
        for triple in zip(*(a["report"]["slots"] for a in row["arms"])):
            if triple[0]["status"] != "PAID_AND_SCORED":
                continue
            p, r = [triple[i]["result"]["squared_loss"] for i in (0, 1)]
            pwins += p < r
            rwins += r < p
            ties += p == r
            observed_targets.add(triple[0]["result"]["target"])
    return {
        "schema": SCHEMA, "status": "BALANCED_PAID_REFERENCE_ENGINEERING_ONLY",
        "fixed_engineering_source_seeds": list(SEEDS),
        "engineering_full_lives": len(rows)*(len(MODES)+1),
        "chronological_eligible_slots_per_paid_life": SLOTS,
        "all_assigned_slots": scored+refused,
        "actually_funded_scored_future_first_person_outcomes": scored,
        "refused_funding_slots": refused,
        "censored_missing_slots": censored,
        "paid_full_trajectory_equal_triplets":
            sum(row["paid_three_arm_full_trajectory_parity"] for row in rows),
        "first_precharge_action_equal_reference_triplets":
            sum(row["first_precharge_motor_matches_unpriced_reference"]
                for row in rows),
        "distinct_actual_factual_target_values": len(observed_targets),
        "matched_observed_priority_lower_sq_loss": pwins,
        "matched_observed_random_lower_sq_loss": rwins,
        "matched_observed_ties": ties,
        "rows": rows,
        "counted_host_inference_paths_equal": all(
            arm["report"]["actual_host_inference_count_prospectively_matched"]
            for row in rows for arm in row["arms"]),
        "real_native_energy_vigilance_debit": True,
        "full_cpu_memory_hash_cost_calibrated_to_body": False,
        "no_independent_iid_ecology": True,
        "scientific_lives": 0, "scientific_verdict": "NOT_ISSUED",
        "stage2_2_go": False,
    }


if __name__ == "__main__":
    print("I3_BALANCED_PAID_COMPACT_LIFE_RESULT="+json.dumps(
        rehearse(), sort_keys=True))
