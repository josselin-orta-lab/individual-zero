"""Lab-only native paid uncertainty from own previous actual prediction errors.

All native options, value, Competition and motor authority remain Mind's.
The uncertainty readout is computed and paid in BOTH VISIBLE/PAID_DISCARD;
only its return scalar differs. The error ledger is owned by this Mind
instance and was physically World-paid before every append.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from math import fsum, isfinite, sqrt

from ..modules.body import (
    ACTION_COSTS, CognitiveBudget, CognitiveWork, cognitive_cost)
from ..modules.genome import midpoint
from ..modules.mind import Mind
from ..modules.world import World
from .dev_worlds import dev_open_field, dev_failing_well
from .stage2_native_effect_reliability_observer import _check_paid
from .stage2_actual_paid_error_ledger_engineering import (
    FORECAST_WORK, STORE_WORK, _can_purchase, _record_error, _empty_receipt,
)

SCHEMA = "i3-stage2.1-paid-private-error-native-uncertainty-engineering/v1"
FACTORIES = (dev_open_field, dev_failing_well)
SEEDS = (840061, 840062)
HORIZON = 12
MODES = ("VISIBLE", "PAID_DISCARD")


def _hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()).hexdigest()


class PaidResidualResearchMind(Mind):
    """Opt-in experiment. The original Mind still decides and controls motor."""

    def __init__(self, genome, life_seed, *, mode):
        if type(mode) is not str or mode not in MODES:
            raise ValueError("unknown finite risk delivery arm")
        super().__init__(genome, life_seed)
        self.research_mode = mode
        self.error_history = []  # (actual native action, own squared error)
        self.risk_events = []
        self._risk_budget = None

    def simulate(self, body, plan, horizon, budget):
        if self._risk_budget is not None:
            raise RuntimeError("nested risk simulation budget")
        self._risk_budget = budget
        try:
            return super().simulate(body, plan, horizon, budget)
        finally:
            self._risk_budget = None

    def _read_plan_prediction(self, key):
        # The original predictor's mean and uncertainty always execute.
        mean, native_u = super()._read_plan_prediction(key)
        budget = self._risk_budget
        if not isinstance(budget, CognitiveBudget):
            raise RuntimeError("risk readout outside native simulation budget")
        n = len(self.error_history)
        work = CognitiveWork(cycles=1, memory_items=2*n+2)
        entry = {
            "native_action_key": key[0],
            "previous_paid_records": n,
            "original_uncertainty": native_u,
            "status": "DENIED_BEFORE_LEDGER_READ",
            "operator_visits": 0,
            "same_action_count": 0,
            "computed_uncertainty": None,
            "returned_uncertainty": native_u,
            "modeled_work": asdict(CognitiveWork()),
        }
        if not budget.try_spend(work):
            self.risk_events.append(entry)
            return mean, native_u

        # The optional source read executes only after admission.
        visits = 0
        pooled_sum = same_sum = 0.0
        same_count = 0
        for action, error in self.error_history:
            visits += 1
            if type(action) is not str or not action or (
                    type(error) not in (int, float) or not isfinite(error)
                    or error < 0):
                raise RuntimeError("invalid paid personal error record")
            pooled_sum += error
            if action == key[0]:
                same_sum += error
                same_count += 1
        if visits != n:
            raise RuntimeError("incomplete actual risk scan")
        pooled_mean = pooled_sum / n if n else 0.
        risk = (same_sum + pooled_mean)/(same_count + 1)
        calculated = sqrt(risk/(1. + risk))
        if not isfinite(calculated) or not 0 <= calculated < 1.:
            raise RuntimeError("invalid uncertainty transform")
        supported = same_count > 0
        returned = (calculated if self.research_mode == "VISIBLE"
                    and supported else native_u)
        entry.update({
            "status": "PAID_SUPPORTED_RISK" if supported
                      else "PAID_NO_SAME_ACTION_SUPPORT",
            "operator_visits": visits,
            "same_action_count": same_count,
            "computed_uncertainty": calculated,
            "returned_uncertainty": returned,
            "modeled_work": asdict(work),
        })
        self.risk_events.append(entry)
        return mean, returned


def run_arm(factory, seed, mode):
    if factory not in FACTORIES or type(seed) is not int or seed not in SEEDS:
        raise ValueError("outside frozen DEV grid")
    if type(mode) is not str or mode not in MODES:
        raise ValueError("unknown risk visibility mode")
    world = World(factory())
    mind = PaidResidualResearchMind(midpoint(), seed, mode=mode)
    rows = []
    while world.t < HORIZON and not world.dead:
        body = tuple(world.body)
        budget = CognitiveBudget(body, world.laws)
        prior_errors = tuple(mind.error_history)
        risk_start = len(mind.risk_events)
        action, param, original_work, info = mind.decide(
            world.capture(), budget)
        risk_events = mind.risk_events[risk_start:]
        if budget.work != original_work:
            raise RuntimeError("unpaid declared native decision")
        if action is None and mind.last is not None:
            raise RuntimeError("null motor but recorded native last action")
        if action is not None and (
                mind.last is None or mind.last[2:] != (action,param)
                or tuple(mind.last[0]) != body):
            raise RuntimeError("motor bypassed native Mind")
        if any(e["previous_paid_records"] != len(prior_errors)
               for e in risk_events):
            raise RuntimeError("risk read accessed an unfunded/current outcome")
        risk_paid = sum(e["status"] != "DENIED_BEFORE_LEDGER_READ"
                        for e in risk_events)
        source_visits = sum(e["operator_visits"] for e in risk_events)
        key = (("se_deplacer",) if action == "se_deplacer" else
               tuple(mind.last[1]) if action is not None else None)
        predicted = None
        forecast_funded = False
        if action is not None:
            forecast_funded = _can_purchase(budget, FORECAST_WORK, action)
            if forecast_funded:
                pred, u = mind.effects.predict(key)
                predicted = tuple(pred)
                if len(predicted) != 5 or not all(isfinite(v)
                        for v in predicted) or not isfinite(u):
                    raise RuntimeError("unusable original paid effect forecast")
        factual = world.step(action, param, budget.work)
        _check_paid(world.laws, budget.work, factual["cognitive_accounting"])
        if tuple(world.body) != tuple(factual["body"]):
            raise RuntimeError("native World returned mismatched body")
        after_motor = tuple(world.body)
        learning = CognitiveBudget(after_motor, world.laws)
        learning_paid = _empty_receipt()
        learned = False
        if not factual["dead"] and mind.last is not None:
            mind.observe_outcome(factual)
            limit = mind.prepare_learning(factual, learning)
            if limit is not None:
                learning_paid = world.pay_cognition(learning.work)
                _check_paid(world.laws, learning.work, learning_paid)
                factual["body"] = world.body
                if mind.learn_from_outcome(
                        factual, replay_limit=limit) != limit:
                    raise RuntimeError("reference outcome learning not prepaid")
                learned = True
        if not learned and learning.work != CognitiveWork():
            raise RuntimeError("unfunded original learning consumed work")
        _check_paid(world.laws, learning.work, learning_paid)
        after_learning = tuple(world.body)
        storage_paid = _empty_receipt()
        stored = False
        recorded = None
        if not factual["dead"] and forecast_funded:
            allowance = CognitiveBudget(world.body, world.laws)
            if _can_purchase(allowance, STORE_WORK):
                storage_paid = world.pay_cognition(allowance.work)
                _check_paid(world.laws, allowance.work, storage_paid)
                recorded = _record_error(
                    mind.error_history, action, predicted, body,
                    after_learning, "RETAIN")
                stored = True
            elif allowance.work != CognitiveWork():
                raise RuntimeError("unfunded error recorded")
        _check_paid(world.laws, STORE_WORK if stored else
                    CognitiveWork(), storage_paid)
        if len(mind.error_history) > HORIZON:
            raise RuntimeError("error history overflow")
        if tuple(mind.error_history[:len(prior_errors)]) != prior_errors:
            raise RuntimeError("past personally paid errors were changed")
        if factual["dead"] and stored:
            raise RuntimeError("memory write after death")
        rows.append({
            "step": world.t, "native_action": action, "native_param": param,
            "native_option": info.get("option"),
            "native_funding": info.get("funding"),
            "decision_work": asdict(budget.work),
            "world_receipt": factual["cognitive_accounting"],
            "risk_reads_funded": risk_paid,
            "risk_reads_attempted": len(risk_events),
            "risk_source_visits": source_visits,
            "risk_events": risk_events,
            "source_digest_before_decision": _hash(prior_errors),
            "source_records_before_decision": len(prior_errors),
            "forecast_funded": forecast_funded,
            "preoutcome_point_forecast": predicted,
            "after_world_body": after_motor,
            "native_learning_funded": learned,
            "native_learning_work": asdict(learning.work),
            "native_learning_receipt": learning_paid,
            "after_learning_body": after_learning,
            "record_funded": stored,
            "record_value": recorded,
            "storage_receipt": storage_paid,
            "after_storage_body": tuple(world.body),
            "terminal": bool(factual["dead"]),
        })
    return {
        "world": world.spec.name, "seed": seed, "mode": mode,
        "steps": rows, "steps_lived": len(rows),
        "terminal": bool(world.dead), "final_body": tuple(world.body),
        "final_private_error_records": len(mind.error_history),
    }


def audit():
    paired = []
    for factory in FACTORIES:
        for seed in SEEDS:
            visible = run_arm(factory, seed, "VISIBLE")
            discard = run_arm(factory, seed, "PAID_DISCARD")
            first_difference = None
            for a,b in zip(visible["steps"], discard["steps"]):
                # Prior to the first decision divergence, both worlds have
                # the same history, body, actual work and source records.
                same_motor = ((a["native_action"],a["native_param"]) ==
                              (b["native_action"],b["native_param"]))
                if a["source_digest_before_decision"] != b[
                        "source_digest_before_decision"]:
                    if first_difference is None:
                        raise RuntimeError("private source divergence without motor")
                    break
                if (a["risk_reads_attempted"] != b["risk_reads_attempted"]
                        or a["risk_reads_funded"] != b["risk_reads_funded"]
                        or a["risk_source_visits"] != b["risk_source_visits"]):
                    if first_difference is None:
                        raise RuntimeError("unequal paid risk work before first motor difference")
                    break
                for x,y in zip(a["risk_events"],b["risk_events"]):
                    if any(x[k] != y[k] for k in (
                            "native_action_key", "previous_paid_records",
                            "status", "operator_visits", "same_action_count",
                            "computed_uncertainty", "modeled_work")):
                        if first_difference is None:
                            raise RuntimeError("different executed optional work")
                if first_difference is None and not same_motor:
                    first_difference = {
                        "step": a["step"],
                        "original_native_motors": {
                            "visible": [a["native_action"],a["native_param"]],
                            "discard": [b["native_action"],b["native_param"]]},
                        "source_digest": a["source_digest_before_decision"],
                        "risk_reads_funded_visible": a["risk_reads_funded"],
                        "risk_reads_funded_discard": b["risk_reads_funded"],
                        "full_decision_work_visible": a["decision_work"],
                        "full_decision_work_discard": b["decision_work"],
                    }
                if first_difference is None and a["after_storage_body"] != b[
                        "after_storage_body"]:
                    raise RuntimeError("matched native motor nevertheless diverged bodily")
            paired.append({
                "world": visible["world"], "seed": seed,
                "visible": visible, "discard": discard,
                "first_motor_difference": first_difference})
    return {
        "schema": SCHEMA,
        "status": ("PAID_RESIDUAL_READOUT_ENGINEERING_PASS_MOTOR_MEDIATION"
                   if any(p["first_motor_difference"] is not None for p in paired)
                   else "PAID_RESIDUAL_READOUT_ENGINEERING_PASS_NO_MOTOR_MEDIATION"),
        "engineering_worlds": 8,
        "engineering_world_steps": sum(
            p[m]["steps_lived"] for p in paired for m in ("visible","discard")),
        "first_differences": sum(p["first_motor_difference"] is not None
                                 for p in paired),
        "private_readout_funded_total": sum(
            sum(s["risk_reads_funded"] for s in p[m]["steps"])
            for p in paired for m in ("visible","discard")),
        "private_error_stores_funded_total": sum(
            sum(s["record_funded"] for s in p[m]["steps"])
            for p in paired for m in ("visible","discard")),
        "original_native_mind_and_control": True,
        "additional_computation_is_laboratory_requested": True,
        "CPU_joules_calibrated": False,
        "scientific_worlds": 0, "scientific_lives": 0,
        "scientific_verdict": "NOT_ISSUED",
        "stage2_2_go": False,
        "deterministic_aggregate_sha256": _hash(paired),
        "pair_results": [{
            "world": p["world"], "seed": p["seed"],
            "visible_steps": p["visible"]["steps_lived"],
            "discard_steps": p["discard"]["steps_lived"],
            "visible_end_body": p["visible"]["final_body"],
            "discard_end_body": p["discard"]["final_body"],
            "first_motor_difference": p["first_motor_difference"],
            "visible_error_records": p["visible"]["final_private_error_records"],
            "discard_error_records": p["discard"]["final_private_error_records"],
            "visible_funded_reads": sum(s["risk_reads_funded"]
                                       for s in p["visible"]["steps"]),
            "discard_funded_reads": sum(s["risk_reads_funded"]
                                       for s in p["discard"]["steps"]),
        } for p in paired],
    }


if __name__ == "__main__":
    print("I3_PAID_RESIDUAL_NATIVE_UNCERTAINTY="+json.dumps(audit(),sort_keys=True))
