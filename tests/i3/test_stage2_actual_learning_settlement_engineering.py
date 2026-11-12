"""Native World/learning settlement of four source-frozen engineering cases."""
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_actual_learning_settlement_engineering as E
from i3.lab import stage2_readout_learning_affordability as OLD
from i3.modules.body import BodyLaws, CognitiveWork
from i3.modules.mind import Mind
from i3.modules.world import World


class Stage2ActualLearningSettlementTests(unittest.TestCase):
    def test_fixed_eight_actual_world_steps_and_learning_phases(self):
        original_step = World.step
        original_pay = World.pay_cognition
        original_learn = Mind.learn_from_outcome
        counters = {"steps": 0, "learning_payments": 0, "learn_calls": 0}

        def step(w, action, param, work):
            counters["steps"] += 1
            return original_step(w, action, param, work)

        def pay(w, work):
            counters["learning_payments"] += 1
            return original_pay(w, work)

        def learn(m, result, *, replay_limit=0, **kwargs):
            counters["learn_calls"] += 1
            return original_learn(m, result, replay_limit=replay_limit, **kwargs)

        with patch("i3.runtime.life.run_life",
                   side_effect=AssertionError("scientific life runner forbidden")), patch.object(
                       World, "step", step), patch.object(
                       World, "pay_cognition", pay), patch.object(
                       Mind, "learn_from_outcome", learn):
            result = E.audit()
        print("I3_STAGE2_ACTUAL_LEARNING_SETTLEMENT=" +
              json.dumps(result, sort_keys=True, separators=(",", ":")))
        self.assertEqual(result["status"], "ACTUAL_WORLD_LEARNING_SETTLEMENT_PASS")
        self.assertEqual(result["frozen_cases"], 4)
        self.assertEqual(result["engineering_Worlds_constructed"], 8)
        self.assertEqual(result["engineering_World_steps_executed"], 8)
        self.assertEqual(counters["steps"], 8)
        self.assertEqual(counters["learning_payments"], 6)
        self.assertEqual(counters["learn_calls"], 6)
        self.assertEqual(result["optional_actual_readouts_executed"], 3)
        self.assertEqual(result["actual_lost_learning_opportunities"],
                         ["energy_boundary", "vigilance_boundary"])
        self.assertFalse(result["baseline_action_selected_by_Mind"])
        self.assertFalse(result["stage2_2_go"])
        self.assertEqual(result["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(result["scientific_lives"], 0)
        self.assertEqual(len(result["deterministic_aggregate_sha256"]), 64)
        self.assertEqual([r["case"] for r in result["rows"]],
                         [name for name, _ in OLD.CASES])
        for r in result["rows"]:
            for mode in ("baseline", "optional"):
                arm = r[mode]
                self.assertEqual(arm["world_steps"], 1)
                self.assertEqual(arm["factual_motor"], "attendre")
                self.assertEqual(
                    arm["motor_source"], "FIXED_ENGINEERING_COMMAND_NOT_NATIVE_DECISION")
                self.assertEqual(len(arm["immediate_post_world_body"]), 5)
                self.assertEqual(len(arm["post_paid_learning_body"]), 5)
                self.assertTrue(arm["pure_contract_matches_actual_world"])
                self.assertTrue(arm["source_unchanged_before_outcome"])
                for phase in ("world_decision_accounting", "world_learning_accounting"):
                    for currency in ("energy", "vigilance"):
                        receipt = arm[phase][currency]
                        self.assertEqual(receipt["requested"], receipt["paid"])
                        self.assertEqual(receipt["unpaid"], 0.)

    def test_no_optional_operation_when_energy_or_motor_reserve_denies_it(self):
        name, body = OLD.CASES[3]
        with patch.object(
                E, "passive_readouts",
                side_effect=AssertionError("unfunded readout invoked")):
            no_bill = E.settle_one(name, body, extra_requested=True)
        self.assertFalse(no_bill["optional_funded"])
        self.assertEqual(no_bill["optional_readouts_executed"], 0)
        self.assertEqual(no_bill["decision_work"],
                         {"cycles": 3, "simulated_steps": 0,
                          "memory_items": 12, "replays": 0})
        self.assertEqual(no_bill["learning_status"], "PAID_LEARNING")

    def test_forged_accounting_refused_by_reconciliation(self):
        work = CognitiveWork(cycles=3, memory_items=12)
        from i3.modules.body import cognitive_cost
        e, v = cognitive_cost(BodyLaws(), work)
        receipt = {
            "energy": {"requested": e, "paid": e, "unpaid": 0.},
            "vigilance": {"requested": v, "paid": v, "unpaid": 0.},
        }
        self.assertEqual(E._assert_paid(work, BodyLaws(), receipt), (e, v))
        receipt["vigilance"]["paid"] = 0.
        with self.assertRaisesRegex(RuntimeError, "forged or unpaid"):
            E._assert_paid(work, BodyLaws(), receipt)

    def test_cases_cannot_be_reselected_after_seeing_world_result(self):
        n, body = OLD.CASES[0]
        with self.assertRaises(PermissionError):
            E.settle_one(n, (5., 60., 60., 90., 80.),
                         extra_requested=True)
        with self.assertRaises(ValueError):
            E.settle_one("new_favorable_body", body, extra_requested=False)
        with self.assertRaises(TypeError):
            E.settle_one(n, body, extra_requested=1)


if __name__ == "__main__":
    unittest.main()
