"""Pre-outcome native effect forecast custody, strictly observer-only.

Source-frozen engineering grid: 2 existing dev Worlds x 2 seeds x horizon 80.
The observer never controls Mind, World, RNG, pricing, action or learning.
No scientific individual/source, independent ecology or cognitive utility.
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import fsum, isfinite
from unittest.mock import patch

from ..modules.body import cognitive_cost
from ..modules.genome import midpoint
from ..modules.mind import Mind
from ..modules.world import World
from ..runtime.life import run_life
from .dev_worlds import dev_open_field, dev_failing_well

SCHEMA = "i3-stage2.1-native-effects-prequential-engineering/v1"
WORLD_FACTORIES = (dev_open_field, dev_failing_well)
SEEDS = (840061, 840062)
HORIZON = 80


def _sha(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False, default=str).encode("utf-8")).hexdigest()


def _check_paid(laws, work, account):
    expected = cognitive_cost(laws, work)
    if type(account) is not dict:
        raise RuntimeError("missing actual cognitive World accounting")
    for currency, cost in zip(("energy", "vigilance"), expected):
        entry = account.get(currency)
        if (type(entry) is not dict
                or abs(entry.get("requested", -1.) - cost) > 1e-10
                or abs(entry.get("paid", -1.) - cost) > 1e-10
                or entry.get("unpaid") != 0):
            raise RuntimeError("unpaid or forged physical two-currency receipt")
    return expected


class PrequentialWitness:
    def __init__(self):
        self.events = []
        self.pending = None
        self.world = None
        self.observer_calls = 0

    def before_choice(self, mind, capture, allowance, action, param, work, info):
        if self.pending is not None:
            self.finish_no_learning()
        if work != allowance.work:
            raise RuntimeError("native decision work not matched to allowance")
        if action is None:
            if mind.last is not None:
                raise RuntimeError("null action kept fake first-person action")
            self.pending = {
                "phase": "FROZEN", "status": "NO_NATIVE_ACTION",
                "action": None, "key": None,
                "body_before": tuple(capture["body"]),
                "native_work": work, "mean": None, "reported_uncertainty": None,
                "n_exact": 0, "fallback": False,
                "world": None, "terminal": False,
            }
            return
        if (mind.last is None or mind.last[2:] != (action, param)
                or tuple(mind.last[0]) != tuple(capture["body"])):
            raise RuntimeError("not the actual native chosen action")
        key = tuple(mind.last[1])
        if action == "se_deplacer":
            key = ("se_deplacer",)
        mean, u = mind.effects.predict(key)
        n_exact = (mind.effects.stats.get(key) or [0.])[0]
        fallback = n_exact == 0 and len(mind.effects.stats) > 0
        if (len(mean) != 5 or any(not isfinite(x) for x in mean)
                or not isfinite(u)):
            raise RuntimeError("nonfinite first-person effect forecast")
        immutable = {
            "chosen_action": action, "param": param,
            "action_key": key, "body_before": tuple(capture["body"]),
            "predicted_delta": tuple(float(x) for x in mean),
            "uncertainty": float(u), "n_exact": n_exact,
            "native_work": (work.cycles, work.simulated_steps,
                            work.memory_items, work.replays),
            "index": len(self.events),
        }
        self.pending = {
            "phase": "FROZEN", "status": "PREDICTION_FROZEN",
            "action": action, "key": key,
            "body_before": tuple(capture["body"]),
            "native_work": work, "mean": tuple(mean),
            "reported_uncertainty": float(u), "n_exact": float(n_exact),
            "fallback": fallback, "seal": _sha(immutable),
            "frozen": immutable, "world": None, "terminal": False,
        }

    def after_world(self, world, action, param, work, result):
        item = self.pending
        if item is None or item["phase"] != "FROZEN":
            raise RuntimeError("World outcome before forecast freeze")
        if item["action"] != action or item["native_work"] != work:
            raise RuntimeError("original World action/bill not first-person decision")
        _check_paid(world.laws, work, result["cognitive_accounting"])
        item["world"] = world
        item["immediate"] = tuple(result["body"])
        item["terminal"] = bool(result["dead"])
        item["decision_bill"] = result["cognitive_accounting"]
        item["phase"] = "WORLD_SETTLED"

    def after_learning_payment(self, world, work, account):
        item = self.pending
        if item is None or item["phase"] != "WORLD_SETTLED" or item["terminal"]:
            raise RuntimeError("learning payment outside living settled World step")
        if item["world"] is not world or item.get("learning_bill") is not None:
            raise RuntimeError("wrong or duplicate learning World payment")
        _check_paid(world.laws, work, account)
        item["learning_bill"] = account
        item["learning_work"] = work

    def before_learn_update(self, mind, result, replay_limit):
        item = self.pending
        if item is None or item["phase"] != "WORLD_SETTLED":
            raise RuntimeError("learning without preoutcome forecast")
        if item.get("learning_bill") is None or item["terminal"]:
            raise RuntimeError("no funded learning bill or postmortem update")
        if tuple(item["world"].body) != tuple(result["body"]):
            raise RuntimeError("World post-payment body differs from learning input")
        self._settle(item, tuple(result["body"]), "PAID_LEARNING")
        item["phase"] = "SCORED"

    def finish_no_learning(self):
        item = self.pending
        if item is None:
            return
        if item["phase"] == "FROZEN":
            raise RuntimeError("preoutcome forecast never reached factual World")
        if item["phase"] == "WORLD_SETTLED":
            if item.get("learning_bill") is not None:
                raise RuntimeError("learning paid but no learned update executed")
            status = ("TERMINAL_NO_LEARNING" if item["terminal"] else
                      "NO_NATIVE_ACTION" if item["action"] is None else
                      "NO_FUNDED_LEARNING")
            self._settle(item, item["immediate"], status)
            item["phase"] = "SCORED"
        if item["phase"] != "SCORED":
            raise RuntimeError("unsettled forecast")
        self.pending = None

    def _settle(self, item, after, status):
        before = item["body_before"]
        if len(after) != 5:
            raise RuntimeError("invalid actual body")
        delta = tuple(x-y for x, y in zip(after, before))
        if item["action"] is None:
            sq = None
        else:
            if _sha(item["frozen"]) != item["seal"]:
                raise RuntimeError("preoutcome forecast custody tampered")
            sq = tuple((p-a)**2 for p, a in zip(item["mean"], delta))
            if any(not isfinite(v) or v < 0 for v in sq):
                raise RuntimeError("invalid proper point forecast score")
        self.events.append({
            "step": len(self.events)+1, "action": item["action"],
            "key": list(item["key"]) if item["key"] is not None else None,
            "source_count_exact": item["n_exact"],
            "fallback_available": item["fallback"],
            "reported_count_uncertainty": item["reported_uncertainty"],
            "preoutcome_forecast_sha256": item.get("seal"),
            "body_before": list(before),
            "immediate_post_world_body": list(item["immediate"]),
            "post_paid_learning_body": list(after),
            "actual_delta": list(delta),
            "forecast_delta": list(item["mean"]) if item["mean"] is not None else None,
            "squared_errors": list(sq) if sq is not None else None,
            "learning_status": status,
            "terminal": item["terminal"],
            "native_decision_bill": item["decision_bill"],
            "native_learning_bill": item.get("learning_bill"),
        })
        self.pending = None

    def report(self):
        self.finish_no_learning()
        by_bin = {}
        for name, predicate in (
                ("unseen_exact", lambda x: x["source_count_exact"] == 0),
                ("seen_exact", lambda x: x["source_count_exact"] > 0)):
            selected = [x for x in self.events if x["squared_errors"] is not None
                        and predicate(x)]
            by_bin[name] = {
                "events": len(selected),
                "mean_five_channel_squared_loss": (
                    fsum(fsum(x["squared_errors"]) / 5 for x in selected)/len(selected)
                    if selected else None),
                "distinct_reported_uncertainty": sorted(set(
                    x["reported_count_uncertainty"] for x in selected)),
            }
        return {
            "all_assigned": len(self.events),
            "native_actions": sum(x["action"] is not None for x in self.events),
            "null_decisions": sum(x["action"] is None for x in self.events),
            "terminal_outcomes": sum(x["terminal"] for x in self.events),
            "paid_learning_outcomes": sum(
                x["learning_status"] == "PAID_LEARNING" for x in self.events),
            "unfunded_learning_outcomes": sum(
                x["learning_status"] == "NO_FUNDED_LEARNING" for x in self.events),
            "scored_forecasts": sum(x["squared_errors"] is not None for x in self.events),
            "proper_point_mean_score_only": True,
            "prediction_error_not_uncertainty_calibration": True,
            "observer_cpu_not_billed_as_organism_work": True,
            "source_count_bins": by_bin,
            "events": self.events,
        }


def run_observed(factory, seed):
    if factory not in WORLD_FACTORIES or type(seed) is not int or seed not in SEEDS:
        raise ValueError("only source-frozen engineering Worlds/seeds allowed")
    observer = PrequentialWitness()
    decide, step = Mind.decide, World.step
    learn, pay = Mind.learn_from_outcome, World.pay_cognition

    def choice_spy(mind, capture, allowance):
        action, param, work, info = decide(mind, capture, allowance)
        observer.before_choice(mind, capture, allowance, action, param, work, info)
        return action, param, work, info

    def step_spy(world, action, param, work):
        result = step(world, action, param, work)
        observer.after_world(world, action, param, work, result)
        return result

    def pay_spy(world, work):
        receipt = pay(world, work)
        observer.after_learning_payment(world, work, receipt)
        return receipt

    def learn_spy(mind, result, *, replay_limit=0, **kw):
        observer.before_learn_update(mind, result, replay_limit)
        return learn(mind, result, replay_limit=replay_limit, **kw)

    with patch.object(Mind, "decide", choice_spy), patch.object(
            World, "step", step_spy), patch.object(
            World, "pay_cognition", pay_spy), patch.object(
            Mind, "learn_from_outcome", learn_spy):
        life = run_life(midpoint(), factory(), seed, HORIZON)
    report = observer.report()
    if report["all_assigned"] != life["steps_lived"]:
        raise RuntimeError("missing/duplicate factual World steps")
    return life, report


def audit():
    rows = []
    for constructor in WORLD_FACTORIES:
        for seed in SEEDS:
            life, readout = run_observed(constructor, seed)
            # Source, native action, native World and native learning remain
            # fully comparable to a control life with no observation.
            baseline = run_life(midpoint(), constructor(), seed, HORIZON)
            parity = ("trace_head", "evidence_head", "steps_lived",
                      "terminal", "final_body", "actions", "cognitive_accounting")
            if any(life[k] != baseline[k] for k in parity):
                raise RuntimeError("passive readout changed actual native trajectory")
            rows.append({
                "world": constructor().name,
                "seed": seed, "steps_lived": life["steps_lived"],
                "terminal": life["terminal"],
                "baseline_native_trajectory_unchanged": True,
                "report": readout,
            })
    structural = [{
        "world": r["world"], "seed": r["seed"], "steps_lived": r["steps_lived"],
        "terminal": r["terminal"], "report": r["report"],
    } for r in rows]
    return {
        "schema": SCHEMA, "status": "PREQUENTIAL_FIRST_PERSON_EFFECT_CUSTODY_PASS",
        "source_kind": "DEV_ENGINEERING_WORLDS_ONLY",
        "source_worlds": [f().name for f in WORLD_FACTORIES],
        "fixed_laboratory_seeds": list(SEEDS),
        "fixed_horizon": HORIZON,
        "engineering_full_lives": len(rows),
        "all_assigned_factual_steps": sum(r["report"]["all_assigned"] for r in rows),
        "scored_native_forecasts": sum(r["report"]["scored_forecasts"] for r in rows),
        "null_actions": sum(r["report"]["null_decisions"] for r in rows),
        "all_four_baseline_trace_and_accounting_equal": True,
        "deterministic_aggregate_sha256": _sha(structural),
        "scientific_lives": 0, "scientific_verdict": "NOT_ISSUED",
        "stage2_2_go": False,
        "rows": rows,
    }


if __name__ == "__main__":
    print("I3_PREQUENTIAL_NATIVE_EFFECT_RELIABILITY="+json.dumps(
        audit(), sort_keys=True, separators=(",", ":")))
