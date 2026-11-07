"""Reference-preserving frontier-water information probe; software only."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork, debit_cognition)
from i3.modules.genome import midpoint
from i3.modules.reference_frontier_information_mind import (
    POLICY, ReferenceFrontierInformationMind)
from i3.modules.reference_memory_mind import ReferenceBranchMemoryMind
from i3.modules.world import World, WorldSpec
from i3.runtime.life import run_life

BODY = (95., 75., 22., 80., 95.)


def fixture(body=BODY):
    return WorldSpec(
        name="reference-frontier-information-software",
        width=5, height=1, spawn=(2, 0), body=body)


def prime_water_model(mind):
    """Only personally represent generic movement/wait/water consequences."""
    mind.effects.observe(("attendre",), (0., -.2, -.4, .2, 0.))
    mind.effects.observe(("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    mind.effects.observe(("dormir",), (3., -.35, -.4, .2, 4.))
    mind.effects.observe(("boire",), (-.5, -.2, 35., 0., 0.))
    # Retain one personally seen water-bearing cell, disconnected from the
    # current local frontier so it contributes belief but not a goto source.
    mind.map[(9, 9)] = (True, ())

    decision = CognitiveWork(cycles=2, simulated_steps=1, memory_items=3)
    funded, _ = debit_cognition(BODY, BodyLaws(), decision)
    physical = tuple(
        value + delta for value, delta in zip(
            funded, (0., 0., 35., 0., 0.)))
    store = CognitiveBudget(physical, BodyLaws())
    mind.branch_memory.observe(
        ("boire", None), BODY, decision, store)


class ReferenceFrontierInformationTests(unittest.TestCase):
    def test_policy_inherits_storage_control_without_replacing_learning_rule(self):
        self.assertTrue(issubclass(
            ReferenceFrontierInformationMind, ReferenceBranchMemoryMind))
        self.assertIs(
            ReferenceFrontierInformationMind.prepare_learning,
            ReferenceBranchMemoryMind.prepare_learning)
        self.assertIs(
            ReferenceFrontierInformationMind.learn_from_outcome,
            ReferenceBranchMemoryMind.learn_from_outcome)

    def test_newborn_frontier_has_no_invented_information_gain(self):
        world = World(fixture())
        mind = ReferenceFrontierInformationMind(
            midpoint(), 41, observer_decision_diagnostics=True)
        budget = CognitiveBudget(world.body, world.laws)
        action, param, work, info = mind.decide(world.capture(), budget)
        self.assertEqual(work, budget.work)
        self.assertIsNotNone(action)
        self.assertEqual(info["frontier_belief_status"],
                         "NO_ACTIONABLE_PERSONAL_MODEL")
        explorers = [
            row for row in info["observer"]["score_witness"]
            if row["option"].startswith("explorer:")]
        self.assertGreater(len(explorers), 0)
        self.assertTrue(all(row["information_value"] == 0.0
                            for row in explorers))
        self.assertTrue(all(row["curiosity_bonus_applied"] == 0.0
                            for row in explorers))
        self.assertEqual(mind.positive_information_options, 0)

    def test_personal_water_experience_creates_positive_frontier_information(self):
        world = World(fixture())
        mind = ReferenceFrontierInformationMind(
            midpoint(), 43, observer_decision_diagnostics=True)
        prime_water_model(mind)
        budget = CognitiveBudget(world.body, world.laws)
        _action, _param, work, info = mind.decide(
            world.capture(), budget)
        self.assertEqual(work, budget.work)
        self.assertEqual(
            info["frontier_belief_status"],
            "COMPLETE_ACTIONABLE_PERSONAL_BELIEF")
        explorers = [
            row for row in info["observer"]["score_witness"]
            if row["option"].startswith("explorer:")]
        self.assertGreater(len(explorers), 0)
        self.assertTrue(any(row["information_value"] > 1e-12
                            for row in explorers))
        self.assertTrue(any(row["total_score"] > row["base_return"]
                            for row in explorers))
        self.assertGreater(mind.actionable_water_queries, 0)
        self.assertGreater(mind.frontier_options_scored, 0)
        self.assertGreater(mind.positive_information_options, 0)

    def test_all_scores_use_one_common_forecast_ceiling_and_no_old_addends(self):
        world = World(fixture())
        mind = ReferenceFrontierInformationMind(
            midpoint(), 47, observer_decision_diagnostics=True)
        prime_water_model(mind)
        budget = CognitiveBudget(world.body, world.laws)
        _action, _param, work, info = mind.decide(
            world.capture(), budget)
        witnesses = info["observer"]["score_witness"]
        self.assertGreater(len(witnesses), 0)
        ceilings = {
            tuple(sorted(row["common_forecast_work_ceiling"].items()))
            for row in witnesses}
        self.assertEqual(len(ceilings), 1)
        ceiling = dict(next(iter(ceilings)))
        for name in ("cycles", "simulated_steps", "memory_items", "replays"):
            self.assertLessEqual(getattr(work, name), ceiling[name])
        for row in witnesses:
            self.assertEqual(row["curiosity_bonus_computed"], 0.0)
            self.assertEqual(row["curiosity_bonus_applied"], 0.0)
            self.assertEqual(row["risk_penalty_computed"], 0.0)
            self.assertEqual(row["risk_penalty_applied"], 0.0)
            self.assertEqual(row["curiosity_risk_bonus"], 0.0)

    def test_forced_explorer_winner_uses_existing_p13_motor_direction(self):
        world = World(fixture())
        mind = ReferenceFrontierInformationMind(
            midpoint(), 53, observer_decision_diagnostics=True)
        prime_water_model(mind)

        def choose_explorer(scored, cycles, budget):
            winner = next(name for name, _ in scored
                          if name.startswith("explorer:"))
            return winner, 0

        with patch.object(mind, "_compete", side_effect=choose_explorer):
            action, param, _work, info = mind.decide(
                world.capture(), CognitiveBudget(world.body, world.laws))
        self.assertEqual(action, "se_deplacer")
        self.assertIn(param, ("E", "W"))
        self.assertTrue(info["option"].startswith("explorer:"))
        self.assertNotIn("water", info["option"])
        self.assertNotIn("boire", info["option"])

    def test_runtime_manifest_is_explicitly_partial_and_reports_branch_memory(self):
        life = run_life(
            midpoint(), fixture((100., 80., 70., 80., 100.)),
            61, 4, keep_trace=True, observer_mind_digest=True,
            observer_decision_diagnostics=True, decision_policy=POLICY,
            protocol="REFERENCE_FRONTIER_INFO_SOFTWARE_ONLY")
        policy = life["experimental_policy"]
        self.assertEqual(policy["name"], POLICY)
        self.assertEqual(
            policy["old_addends"],
            "curiosity_relevance_prudence_removed")
        self.assertEqual(
            policy["frontier_scope"],
            "one_generic_new_cell_water_only")
        self.assertEqual(policy["food_information"], "NOT_IMPLEMENTED")
        self.assertEqual(
            policy["multi_cell_joint_outcomes"], "NOT_IMPLEMENTED")
        self.assertIn("branch_effect_memory", life)
        self.assertIn("branch_outcomes_sha256", life)
        self.assertEqual(
            life["frontier_information"]["scope"],
            "one_generic_new_cell_water_only")
        self.assertEqual(
            life["frontier_information"]["food_information"],
            "NOT_IMPLEMENTED")

    def test_default_reference_never_constructs_frontier_candidate(self):
        with patch(
            "i3.modules.reference_frontier_information_mind."
            "ReferenceFrontierInformationMind.__init__",
            side_effect=AssertionError("implicit frontier candidate")):
            life = run_life(
                midpoint(), fixture((100., 80., 70., 80., 100.)),
                67, 3, decision_policy="reference",
                observer_mind_digest=True)
        self.assertNotIn("experimental_policy", life)
        self.assertNotIn("frontier_information", life)
        self.assertNotIn("branch_effect_memory", life)

    def test_historical_ablations_fail_before_birth(self):
        with patch(
            "i3.runtime.life.World",
            side_effect=AssertionError("born too soon")):
            for kwargs in (
                {"learning_mode": "discard_values"},
                {"effect_readout": "blind_all"},
                {"score_addend_mode": "discard_curiosity_bonus"},
            ):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    run_life(
                        midpoint(), fixture(), 71, 3,
                        decision_policy=POLICY, **kwargs)

    def test_dead_birth_has_no_frontier_computation_or_storage(self):
        life = run_life(
            midpoint(), fixture((80., 0., 50., 80., 80.)),
            73, 3, decision_policy=POLICY,
            observer_mind_digest=True)
        self.assertEqual(life["steps_lived"], 0)
        self.assertEqual(
            life["frontier_information"]["belief_queries"], 0)
        self.assertEqual(
            life["branch_effect_memory"]["recorded"], 0)

    def test_existing_development_fixture_is_software_only_and_settled(self):
        from i3.lab.p2_ecologies import world_for
        spec = world_for("stable", "development", 0)
        life = run_life(
            midpoint(), spec, 79, 6, keep_trace=True,
            decision_policy=POLICY,
            protocol="REFERENCE_FRONTIER_INFO_SOFTWARE_ONLY")
        self.assertIn(life["terminal"], ("dead", "censored"))
        self.assertEqual(
            life["cognitive_accounting"]["status"],
            "SETTLED_FOR_DECLARED_WORK")
        self.assertEqual(
            life["experimental_policy"]["frontier_scope"],
            "one_generic_new_cell_water_only")


if __name__ == "__main__":
    unittest.main()
