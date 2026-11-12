"""Fixed-body native Mind choice -> optional cost -> true World settlement.

A real chosen motor is different from an autonomous choice to buy reflection.
No birth, science cohort or action-inducing synthetic evidence is permitted.
"""
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_native_choice_cost_bridge_engineering as E
from i3.lab import stage2_readout_learning_affordability as F
from i3.modules.mind import Mind
from i3.modules.world import World


class NativeChoiceCostBridgeTests(unittest.TestCase):
    def test_all_eight_frozen_arms_really_use_native_mind_and_world(self):
        native_decide = Mind.decide
        native_step = World.step
        counters = {"decisions": 0, "steps": 0}

        def decision(mind, cap, budget):
            counters["decisions"] += 1
            return native_decide(mind, cap, budget)

        def step(world, action, param, work):
            counters["steps"] += 1
            return native_step(world, action, param, work)

        with patch.object(Mind, "decide", decision), patch.object(
                World, "step", step), patch(
                    "i3.runtime.life.run_life",
                    side_effect=AssertionError("full lives prohibited")):
            report = E.audit()
        print("I3_NATIVE_CHOICE_COST_BRIDGE="+json.dumps(
            report, sort_keys=True, separators=(",", ":")))
        self.assertEqual(report["status"], "NATIVE_CHOICE_COST_BRIDGE_PASS")
        self.assertEqual(report["action_mediation"],
                         "NO_ACTION_MEDIATION_OBSERVED")
        self.assertEqual(report["native_choice_source"],
                         "ORIGINAL_MIND_DECIDE_ON_EACH_ARM")
        self.assertEqual(report["frozen_body_cases"], 4)
        self.assertEqual(report["engineering_Worlds_constructed"], 8)
        self.assertEqual(report["engineering_World_steps"], 8)
        self.assertEqual(report["science_lives"], 0)
        self.assertEqual(report["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(report["actual_optional_readouts_delivered_to_policy"], 0)
        self.assertEqual(counters, {"decisions": 8, "steps": 8})
        self.assertEqual(len(report["deterministic_aggregate_sha256"]), 64)
        self.assertEqual(
            [r["case"] for r in report["rows"]],
            [case for case, _ in F.CASES])
        self.assertEqual(
            sum(report["optional_status_counts"].values()), 4)
        for pair in report["rows"]:
            baseline, optional = pair["reference"], pair["optional"]
            for field in ("native_motor", "native_param", "native_funding",
                          "native_pre_optional_work", "native_selected_option"):
                self.assertEqual(baseline[field], optional[field])
            self.assertFalse(baseline["request_optional"])
            self.assertTrue(optional["request_optional"])
            self.assertEqual(baseline["optional_status"], "NOT_REQUESTED")
            for row in (baseline, optional):
                self.assertEqual(row["world_steps"], 1)
                self.assertTrue(row["pre_optional_source_unchanged"])
                self.assertEqual(len(row["immediate_post_world_body"]), 5)
                self.assertEqual(len(row["post_paid_learning_body"]), 5)
                for currency, expected_price in (
                        ("energy", row["actual_decision_model_energy"]),
                        ("vigilance", row["actual_decision_model_vigilance"])):
                    receipt = row["world_decision_receipt"][currency]
                    self.assertAlmostEqual(receipt["paid"], expected_price)
                    self.assertEqual(receipt["requested"], receipt["paid"])
                    self.assertEqual(receipt["unpaid"], 0)
            if optional["optional_status"] == "NO_NATIVE_MOTOR":
                self.assertIsNone(optional["native_motor"])
                self.assertEqual(optional["optional_readouts_executed"], 0)
                self.assertFalse(optional["optional_paid"])
            elif optional["optional_status"] == "OPTIONAL_DENIED":
                self.assertEqual(optional["optional_readouts_executed"], 0)
                self.assertFalse(optional["optional_paid"])
            else:
                self.assertEqual(optional["optional_status"],
                                 "OPTIONAL_PAID_AND_DISCARDED")
                self.assertEqual(optional["optional_readouts_executed"], 1)
                self.assertTrue(optional["optional_paid"])

    def test_frozen_bodies_and_strict_request_type(self):
        name, body = F.CASES[0]
        with self.assertRaises(PermissionError):
            E.run_arm(name, (99.,60.,60.,90.,80.), request_optional=True)
        with self.assertRaises(ValueError):
            E.run_arm("unregistered", body, request_optional=False)
        with self.assertRaises(TypeError):
            E.run_arm(name, body, request_optional=1)

    def test_no_optional_result_can_feed_native_motor(self):
        original = E.passive_readouts
        def run_readout(*args, **kwargs):
            x = original(*args, **kwargs)
            return {**x, "scalar_forecasts": {"action": -987654.0}}
        # A wildly altered, discarded output cannot modify a decision
        # that was already made, nor its native choice source.
        with patch.object(E, "passive_readouts", side_effect=run_readout):
            r = E.audit()
        self.assertTrue(r["original_native_motor_pair_parity"])
        self.assertTrue(r["original_decision_model_cost_pair_parity"])
        self.assertEqual(r["actual_optional_readouts_delivered_to_policy"], 0)

    def test_no_postmortem_learning_or_refused_cognition_write(self):
        r = E.audit()
        for pair in r["rows"]:
            for arm in (pair["reference"], pair["optional"]):
                if arm["native_outcome_terminal"]:
                    self.assertEqual(arm["learning_status"],
                                     "TERMINAL_NO_LEARNING")
                    self.assertFalse(arm["actual_native_learning_executed"])
                if not arm["actual_native_learning_executed"]:
                    self.assertEqual(arm["native_learning_work"], {
                        "cycles": 0, "simulated_steps": 0,
                        "memory_items": 0, "replays": 0})
                    self.assertEqual(arm["post_paid_learning_body"],
                                     arm["immediate_post_world_body"])


if __name__ == "__main__":
    unittest.main()
