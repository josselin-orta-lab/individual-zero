"""Multi-step Candidate-F upper-cost controller: software fixtures only."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork)
from i3.modules.candidate_f_cost_control import _validate_pair
from i3.modules.candidate_f_upper_cost_reference_controller import (
    CandidateFUpperCostReferenceController, POLICY)
from i3.modules.genome import midpoint
from i3.modules.personal_outcomes import STORE_WORK
from i3.modules.world import World, WorldSpec
from i3.runtime.life import run_life

BODY = (100., 80., 70., 80., 100.)


def fixture(body=BODY):
    return WorldSpec(
        name="candidate-f-upper-cost-controller-software",
        width=1, height=1, spawn=(0, 0), body=body)


def add(a, b):
    return CognitiveWork(
        cycles=a.cycles + b.cycles,
        simulated_steps=a.simulated_steps + b.simulated_steps,
        memory_items=a.memory_items + b.memory_items,
        replays=a.replays + b.replays,
    )


def physical_step(controller, world):
    cap = world.capture()
    decision = CognitiveBudget(world.body, world.laws)
    action, param, work, info = controller.decide(cap, decision)
    result = world.step(action, param, work)
    learning = CognitiveBudget(result["body"], world.laws)
    replay_limit = None
    if not result["dead"] and controller.last is not None:
        controller.observe_outcome(result)
        replay_limit = controller.prepare_learning(result, learning)
    if replay_limit is not None:
        world.pay_cognition(learning.work)
        result["body"] = world.body
        replays = controller.learn_from_outcome(
            result, replay_limit=replay_limit)
        if replays != replay_limit:
            raise AssertionError("replay mismatch")
    return action, param, work, info, result, learning, replay_limit


class CandidateFUpperCostControllerTests(unittest.TestCase):
    def test_three_real_steps_keep_one_actor_and_private_shadow_history(self):
        controller = CandidateFUpperCostReferenceController(
            midpoint(), 17, observer_decision_diagnostics=True)
        world = World(fixture())
        actual_actions = []
        for _ in range(3):
            action, _param, work, info, result, _learning, _limit = (
                physical_step(controller, world))
            actual_actions.append(action)
            self.assertEqual(
                info["cost_control"]["motor_authority"],
                "P1.3_REFERENCE_ONLY")
            self.assertEqual(info["experimental_policy"], POLICY)
            self.assertEqual(work, CognitiveWork(
                **info["cost_control"]["total_work"]))
            if result["dead"]:
                break

        self.assertEqual(controller.decisions, len(actual_actions))
        self.assertGreater(controller.shadow_branch_commits, 0)
        self.assertEqual(
            controller.shadow_branch_commits,
            controller.branch_records)
        stored_actions = [
            sample.key[0] for sample in controller.branch_memory._samples]
        self.assertTrue(stored_actions)
        self.assertTrue(all(action in actual_actions for action in stored_actions))
        self.assertEqual(
            controller.custody_summary()["motor_authority"],
            "P1.3_REFERENCE_ONLY")

    def test_shadow_is_re_aligned_before_each_candidate_computation(self):
        controller = CandidateFUpperCostReferenceController(midpoint(), 23)
        controller.shadow.map[(9, 9)] = (True, ())
        controller.shadow.effects.observe(
            ("attendre",), (0., -9., -9., 0., 0.))
        controller.shadow.rng.random()

        original = controller.shadow.decide

        def asserting_decide(cap, budget):
            _validate_pair(controller.reference, controller.shadow)
            return original(cap, budget)

        with patch.object(
                controller.shadow, "decide", side_effect=asserting_decide):
            controller.decide(
                {
                    "body": BODY,
                    "here": (False, ()),
                    "neighbors": (None, None, None, None),
                    "inventory": (),
                },
                CognitiveBudget(BODY, BodyLaws()))

    def test_shadow_choice_never_becomes_motor_action_or_branch_history(self):
        controller = CandidateFUpperCostReferenceController(midpoint(), 29)
        world = World(fixture())

        def fake_shadow(_cap, budget):
            budget.spend(CognitiveWork(cycles=1, memory_items=1))
            return (
                "boire", None, budget.work,
                {"option": "forced-shadow-water", "funding": "FUNDED"})

        with patch.object(controller.shadow, "decide", side_effect=fake_shadow):
            action, _param, _work, info, _result, _learning, _limit = (
                physical_step(controller, world))

        self.assertNotEqual(action, "boire")
        self.assertEqual(
            info["cost_control"]["candidate_shadow_action"], "boire")
        self.assertGreater(controller.branch_records, 0)
        self.assertEqual(
            controller.branch_memory._samples[-1].key[0], action)

    def test_learning_purchase_is_reference_plan_plus_optional_private_store(self):
        controller = CandidateFUpperCostReferenceController(midpoint(), 31)
        world = World(fixture())
        cap = world.capture()
        db = CognitiveBudget(world.body, world.laws)
        action, param, work, _info = controller.decide(cap, db)
        result = world.step(action, param, work)
        self.assertFalse(result["dead"])
        controller.observe_outcome(result)

        expected = CognitiveBudget(result["body"], world.laws)
        expected_limit = controller.reference.prepare_learning(
            result, expected)

        actual = CognitiveBudget(result["body"], world.laws)
        actual_limit = controller.prepare_learning(result, actual)
        self.assertEqual(actual_limit, expected_limit)
        self.assertIsNotNone(actual_limit)
        self.assertEqual(actual.work, add(expected.work, STORE_WORK))

    def test_unfunded_private_store_does_not_change_reference_learning_purchase(self):
        controller = CandidateFUpperCostReferenceController(midpoint(), 37)
        reference = controller.reference
        body = (.03, 70., 70., 80., .06)
        reference.last = (body, ("attendre",), "attendre", None)
        controller._last_reference_decision_work = CognitiveWork()
        result = {"body": body, "dead": ()}

        expected = CognitiveBudget(body, BodyLaws())
        expected_limit = reference.prepare_learning(result, expected)
        actual = CognitiveBudget(body, BodyLaws())
        actual_limit = controller.prepare_learning(result, actual)

        self.assertEqual(actual_limit, expected_limit)
        self.assertEqual(actual.work, expected.work)
        self.assertIsNone(controller._pending_shadow_branch)

    def test_next_decision_discards_shadow_common_drift_but_keeps_private_samples(self):
        controller = CandidateFUpperCostReferenceController(midpoint(), 41)
        world = World(fixture())
        physical_step(controller, world)
        self.assertGreater(controller.branch_records, 0)
        samples = tuple(controller.branch_memory._samples)

        controller.shadow.effects.observe(
            ("attendre",), (0., -20., -20., 0., 0.))
        controller.shadow.map[(7, 7)] = (True, ())
        controller.shadow.values[0][0] += 999.

        cap = world.capture()
        controller.decide(cap, CognitiveBudget(world.body, world.laws))

        self.assertEqual(
            controller.shadow.effects.stats,
            controller.reference.effects.stats)
        self.assertEqual(controller.shadow.map, controller.reference.map)
        self.assertEqual(controller.shadow.values, controller.reference.values)
        self.assertEqual(tuple(controller.branch_memory._samples), samples)

    def test_controller_keeps_reference_state_authoritative_after_learning(self):
        controller = CandidateFUpperCostReferenceController(midpoint(), 43)
        world = World(fixture())
        physical_step(controller, world)
        reference_snapshot = {
            "effects": deepcopy(controller.reference.effects.stats),
            "map": deepcopy(controller.reference.map),
            "values": deepcopy(controller.reference.values),
            "buffer": tuple(controller.reference.buffer),
            "pos": controller.reference.pos,
        }
        # Shadow is allowed to diverge after its computation.
        controller.shadow.effects.observe(
            ("attendre",), (0., -5., -5., 0., 0.))
        self.assertNotEqual(
            controller.shadow.effects.stats,
            controller.reference.effects.stats)

        controller.decide(
            world.capture(),
            CognitiveBudget(world.body, world.laws))
        self.assertEqual(controller.reference.effects.stats,
                         reference_snapshot["effects"])
        self.assertEqual(controller.reference.map, reference_snapshot["map"])
        self.assertEqual(controller.reference.values, reference_snapshot["values"])
        self.assertEqual(tuple(controller.reference.buffer),
                         reference_snapshot["buffer"])
        self.assertEqual(controller.reference.pos, reference_snapshot["pos"])

    def test_controller_is_not_registered_runtime_policy(self):
        with patch(
                "i3.runtime.life.World",
                side_effect=AssertionError("world must not be constructed")):
            with self.assertRaisesRegex(ValueError, "unknown decision policy"):
                run_life(
                    midpoint(), fixture(), 1, 1,
                    decision_policy=POLICY)

    def test_module_import_does_not_load_mind_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.candidate_f_upper_cost_reference_controller; "
            "assert 'i3.modules.mind' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
