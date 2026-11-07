"""Development-only runtime wiring for the Candidate-F upper-cost falsifier."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import CognitiveWork
from i3.modules.candidate_f_upper_cost_reference_controller import POLICY
from i3.modules.genome import midpoint
from i3.modules.genomic_omega_frontier_information_mind import (
    GenomicOmegaFrontierInformationMind)
from i3.modules.world import WorldSpec
from i3.runtime.life import run_life

BODY = (100., 80., 70., 80., 100.)


def fixture(body=BODY):
    return WorldSpec(
        name="candidate-f-upper-cost-runtime-software",
        width=1, height=1, spawn=(0, 0), body=body)


def work(d):
    return CognitiveWork(**d)


def add(a, b):
    return CognitiveWork(
        cycles=a.cycles + b.cycles,
        simulated_steps=a.simulated_steps + b.simulated_steps,
        memory_items=a.memory_items + b.memory_items,
        replays=a.replays + b.replays,
    )


class CandidateFUpperCostRuntimeTests(unittest.TestCase):
    def test_explicit_policy_runs_and_reports_one_actor_upper_cost_custody(self):
        life = run_life(
            midpoint(), fixture(), 17, 3,
            keep_trace=True,
            observer_mind_digest=True,
            observer_decision_diagnostics=True,
            decision_policy=POLICY,
            protocol="CANDIDATE_F_UPPER_COST_RUNTIME_SOFTWARE_ONLY")
        policy = life["experimental_policy"]
        self.assertEqual(policy["name"], POLICY)
        self.assertEqual(policy["motor_authority"], "P1.3_REFERENCE_ONLY")
        self.assertEqual(
            policy["cost_matching_claim"], "UPPER_COST_NOT_EXACT_MATCH")
        self.assertEqual(
            policy["shadow_common_state"],
            "REALIGNED_TO_ACTUAL_P1.3_BEFORE_EACH_DECISION")

        custody = life["candidate_f_cost_control"]
        self.assertEqual(custody["motor_authority"], "P1.3_REFERENCE_ONLY")
        self.assertFalse(custody["shadow_motor_authority"])
        self.assertEqual(custody["decisions"], life["steps_lived"])
        self.assertEqual(
            custody["shadow_branch_commits"],
            life["branch_effect_memory"]["recorded"])
        self.assertEqual(
            custody["shadow_branch_retained"],
            life["branch_effect_memory"]["retained"])
        self.assertIn("branch_outcomes_sha256", life)
        self.assertIn("outcome_model_sha256", life)
        self.assertIn("spatial_beliefs_sha256", life)

    def test_every_trace_decision_bill_is_shadow_plus_reference_work(self):
        life = run_life(
            midpoint(), fixture(), 19, 3,
            keep_trace=True,
            observer_decision_diagnostics=True,
            decision_policy=POLICY,
            protocol="CANDIDATE_F_UPPER_COST_RUNTIME_SOFTWARE_ONLY")
        self.assertGreater(life["steps_lived"], 0)
        for row in life["trace"]:
            cc = row["info"]["cost_control"]
            total = add(
                work(cc["candidate_shadow_work"]),
                work(cc["reference_choice_work"]))
            self.assertEqual(
                total, work(cc["total_work"]))
            self.assertEqual(
                total, work(row["funding_phases"]["decision"]["work"]))
            self.assertEqual(
                cc["settlement_authority"],
                "CUMULATIVE_V2_PHASE_START_BODY")
            self.assertLessEqual(
                cc["sequential_settlement_max_abs_gap"], 1e-12)

    def test_shadow_forced_motor_never_overrides_reference_action(self):
        def forced_shadow(_self, _cap, budget):
            from i3.modules.body import CognitiveWork
            budget.spend(CognitiveWork(cycles=1, memory_items=1))
            return (
                "boire", None, budget.work,
                {"option": "forced-shadow-water", "funding": "FUNDED"})

        with patch.object(
                GenomicOmegaFrontierInformationMind,
                "decide", forced_shadow):
            life = run_life(
                midpoint(), fixture(), 23, 1,
                keep_trace=True,
                observer_decision_diagnostics=True,
                decision_policy=POLICY,
                protocol="CANDIDATE_F_UPPER_COST_RUNTIME_SOFTWARE_ONLY")
        row = life["trace"][0]
        self.assertEqual(
            row["info"]["cost_control"]["candidate_shadow_action"],
            "boire")
        self.assertNotEqual(row["action"], "boire")
        self.assertFalse(
            row["info"]["cost_control"]["candidate_motor_authority"])

    def test_full_competition_observer_authenticates_reference_choice_under_total_bill(self):
        life = run_life(
            midpoint(), fixture(), 29, 2,
            keep_trace=True,
            observer_full_competition=True,
            decision_policy=POLICY,
            protocol="CANDIDATE_F_UPPER_COST_RUNTIME_SOFTWARE_ONLY")
        witness = life["observer_full_competition"]["steps"]
        self.assertEqual(len(witness), life["steps_lived"])
        for row, observed in zip(life["trace"], witness):
            self.assertEqual(observed["physical_action"], row["action"])
            self.assertEqual(
                work(observed["paid_decision_work"]),
                work(row["funding_phases"]["decision"]["work"]))
            self.assertEqual(
                observed["chosen_option"], row["option"])

    def test_reference_runtime_has_no_implicit_upper_cost_controller(self):
        with patch(
            "i3.modules.candidate_f_upper_cost_reference_controller."
            "CandidateFUpperCostReferenceController.__init__",
            side_effect=AssertionError("unexpected upper-cost controller")):
            life = run_life(
                midpoint(), fixture(), 31, 2,
                decision_policy="reference",
                protocol="REFERENCE_PARITY_SOFTWARE_ONLY")
        self.assertNotIn("candidate_f_cost_control", life)
        self.assertNotIn("experimental_policy", life)

    def test_upper_cost_policy_rejects_historical_ablations_before_world(self):
        with patch(
                "i3.runtime.life.World",
                side_effect=AssertionError("world constructed too early")):
            for kwargs in (
                {"learning_mode": "discard_values"},
                {"effect_readout": "blind_all"},
                {"score_addend_mode": "discard_curiosity_bonus"},
            ):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    run_life(
                        midpoint(), fixture(), 37, 2,
                        decision_policy=POLICY, **kwargs)

    def test_dead_birth_has_no_decision_or_private_branch_record(self):
        life = run_life(
            midpoint(), fixture((100., 0., 70., 80., 100.)),
            41, 2,
            observer_mind_digest=True,
            decision_policy=POLICY,
            protocol="CANDIDATE_F_UPPER_COST_RUNTIME_SOFTWARE_ONLY")
        self.assertEqual(life["steps_lived"], 0)
        self.assertEqual(
            life["candidate_f_cost_control"]["decisions"], 0)
        self.assertEqual(
            life["branch_effect_memory"]["recorded"], 0)


if __name__ == "__main__":
    unittest.main()
