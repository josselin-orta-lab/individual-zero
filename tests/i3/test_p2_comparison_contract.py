"""P2 exit: equal opportunity and falsifiable probe cost-matching claims."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i3.lab import p2_ecologies, p2_comparison_contract as contract
from i3.lab.probes import reference_survival, IDLE
from i3.modules.genome import generation_zero
from i3.modules.world import World
from i3.modules.body import CognitiveWork
from i3.runtime.life import run_life


class EqualOpportunityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = p2_ecologies.world_for("stable", "development", 10)
        cls.a = run_life(generation_zero(1), cls.spec, 55, 35, keep_trace=True)
        cls.b = run_life(generation_zero(2), cls.spec, 55, 35, keep_trace=True)

    def test_distinct_genomes_share_initial_opportunity_without_equal_work(self):
        result = contract.compare_equal_opportunity(self.a, self.b)
        self.assertTrue(result["equal_initial_opportunity"])
        self.assertEqual(result["interpretation"],
                         "equal_opportunity_not_equal_realized_spending")
        self.assertFalse(result["cost_matched_probe_ceiling"])
        self.assertIn("paid_cognitive_difference_a_minus_b", result)

    def test_unequal_initial_body_rejected(self):
        other = replace(self.spec, body=(50., 50., 50., 50., 50.))
        mismatched = run_life(generation_zero(2), other, 55, 35)
        with self.assertRaises(ValueError):
            contract.compare_equal_opportunity(self.a, mismatched)

    def test_different_life_seed_rejected(self):
        changed = run_life(generation_zero(2), self.spec, 56, 35)
        with self.assertRaises(ValueError):
            contract.compare_equal_opportunity(self.a, changed)

    def test_censored_life_cannot_be_reported_short(self):
        fake = deepcopy(self.a)
        fake["terminal"] = "censored"
        fake["steps_lived"] = fake["horizon"] - 1
        with self.assertRaises(ValueError):
            contract.compare_equal_opportunity(fake, self.b)

    def test_unpaid_cognition_rejected(self):
        fake = deepcopy(self.a)
        fake["cognitive_accounting"]["totals"]["energy"]["unpaid"] = 1.0
        with self.assertRaises(ValueError):
            contract.compare_equal_opportunity(fake, self.b)

    def test_probe_truncated_prefix_never_cost_matched(self):
        audit = []
        reference_survival(self.spec, 10, work_schedule=((IDLE, IDLE),) * 3,
                           audit=audit)
        decision = contract.audit_probe_exact_work(self.spec, self.a, audit, 35)
        self.assertFalse(decision["full_horizon_cost_match"])
        self.assertEqual(decision["meaning"], "NOT_COST_MATCHED")

    def test_probe_unpaid_tick_never_cost_matched(self):
        audit = []
        expensive = CognitiveWork(cycles=100000)
        reference_survival(self.spec, 35, work_schedule=((expensive, IDLE),) * 35,
                           audit=audit)
        decision = contract.audit_probe_exact_work(self.spec, self.a, audit, 35)
        self.assertFalse(decision["full_horizon_cost_match"])

    def test_probe_mismatched_initial_body_rejected(self):
        spec = replace(self.spec, body=(30., 60., 40., 80., 90.))
        audit = []
        reference_survival(spec, 4, audit=audit)
        with self.assertRaises(ValueError):
            contract.audit_probe_exact_work(self.spec, self.a, audit, 35)

    def test_refuse_fabricated_postmortem_learning(self):
        audit = []
        reference_survival(self.spec, 2, audit=audit)
        bad = dict(audit[0])
        bad["dead"] = True
        bad["paid_learning"] = CognitiveWork(cycles=1)
        with self.assertRaises(ValueError):
            contract.audit_probe_exact_work(self.spec, self.a, [bad], 35)

    def test_complete_reference_trace_not_necessarily_equal_cost(self):
        audit = []
        reference_survival(self.spec, 35, audit=audit)
        result = contract.audit_probe_exact_work(self.spec, self.a, audit, 35)
        self.assertFalse(result["full_horizon_cost_match"])
        self.assertEqual(result["compared_ticks"], len(audit))


if __name__ == "__main__":
    unittest.main()
