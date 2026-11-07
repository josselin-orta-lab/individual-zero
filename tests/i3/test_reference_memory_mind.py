"""Storage-only P1.3 branch-memory control; software fixtures, not a study."""
from collections import deque
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.personal_outcomes import STORE_WORK
from i3.modules.reference_branches import CAPACITY
from i3.modules.reference_memory_mind import ReferenceBranchMemoryMind
from i3.modules.world import WaterSource, World, WorldSpec
from i3.runtime.life import run_life

BODY = (80., 70., 50., 80., 80.)
MODE = "reference_branch_memory_v1"


def fixture(body=BODY):
    return WorldSpec(
        name="reference-branch-memory-software",
        width=1, height=1, spawn=(0, 0), body=body,
        water={(0, 0): WaterSource(12., stock=None)})


class ReferenceMemoryMindTests(unittest.TestCase):
    def test_first_decision_is_exact_p13_path(self):
        w = World(fixture())
        cap = w.capture()
        a = Mind(midpoint(), 17, observer_decision_diagnostics=True,
                 observer_full_competition=True)
        b = ReferenceBranchMemoryMind(
            midpoint(), 17, observer_decision_diagnostics=True,
            observer_full_competition=True)
        ba, bb = CognitiveBudget(w.body, w.laws), CognitiveBudget(w.body, w.laws)
        self.assertEqual(a.decide(cap, ba), b.decide(cap, bb))
        self.assertEqual(a.rng.getstate(), b.rng.getstate())
        self.assertEqual(a._budget_rng.getstate(), b._budget_rng.getstate())
        self.assertEqual(a.m_max, b.m_max)
        self.assertEqual(len(b.branch_memory._samples), 0)

    def test_storage_is_added_after_identical_reference_learning_plan(self):
        g = midpoint()
        a, b = Mind(g, 3), ReferenceBranchMemoryMind(g, 3)
        before = BODY
        result = {"dead": (), "body": BODY}
        last = (before, ("dormir",), "dormir", None)
        sample = (1.0, before, BODY, False)
        for mind in (a, b):
            mind.last = last
            mind.buffer = deque([sample, sample, sample, sample])
        b._branch_decision_work = CognitiveWork(cycles=3)

        ba, bb = CognitiveBudget(BODY, BodyLaws()), CognitiveBudget(BODY, BodyLaws())
        ra = a.prepare_learning(result, ba)
        rb = b.prepare_learning(result, bb)
        self.assertEqual(ra, rb)
        self.assertEqual(bb.work.cycles, ba.work.cycles + STORE_WORK.cycles)
        self.assertEqual(
            bb.work.simulated_steps, ba.work.simulated_steps + STORE_WORK.simulated_steps)
        self.assertEqual(
            bb.work.memory_items, ba.work.memory_items + STORE_WORK.memory_items)
        self.assertEqual(bb.work.replays, ba.work.replays + STORE_WORK.replays)

        self.assertEqual(
            b.learn_from_outcome(result, replay_limit=rb), rb)
        self.assertEqual(b.branch_records, 1)
        self.assertEqual(len(b.branch_memory._samples), 1)
        self.assertEqual(b.m_max, a.m_max)

    def test_unaffordable_extra_store_never_steals_reference_learning(self):
        body = (.08, 40., 40., 80., .15)
        g = midpoint()
        a, b = Mind(g, 3), ReferenceBranchMemoryMind(g, 3)
        last = (body, ("attendre",), "attendre", None)
        result = {"dead": (), "body": body}
        a.last = last
        b.last = last
        b._branch_decision_work = CognitiveWork()
        ba, bb = CognitiveBudget(body, BodyLaws()), CognitiveBudget(body, BodyLaws())
        self.assertEqual(a.prepare_learning(result, ba), 0)
        self.assertEqual(b.prepare_learning(result, bb), 0)
        self.assertEqual(ba.work, bb.work)
        self.assertIsNone(b._pending_branch)
        self.assertEqual(b.branch_records, 0)

    def test_runtime_manifest_and_receipts_label_storage_control_only(self):
        life = run_life(
            midpoint(), fixture(), 17, 4, keep_trace=True,
            observer_mind_digest=True, decision_policy=MODE,
            protocol="REFERENCE_BRANCH_MEMORY_SOFTWARE_ONLY")
        self.assertEqual(life["experimental_policy"], {
            "name": MODE,
            "score": "P1.3_reference_unchanged",
            "branch_memory": "global18_recent_personal_effects_v1",
            "td_memory": "P1.3_unchanged"})
        memory = life["branch_effect_memory"]
        self.assertEqual(memory["capacity"], CAPACITY)
        self.assertGreater(memory["recorded"], 0)
        self.assertEqual(memory["recorded"], memory["retained"])
        self.assertEqual(memory["td_capacity"], round(midpoint()["genes"]["m_max"]))
        self.assertIn("branch_outcomes_sha256", life)
        self.assertNotIn("personal_effect_memory", life)

    def test_reference_runtime_has_no_implicit_branch_store(self):
        with patch(
            "i3.modules.reference_branches.ReferenceBranchMemory.__init__",
            side_effect=AssertionError("unexpected branch-memory control")):
            life = run_life(
                midpoint(), fixture(), 17, 3, keep_trace=True,
                observer_mind_digest=True, decision_policy="reference")
        self.assertNotIn("experimental_policy", life)
        self.assertNotIn("branch_effect_memory", life)
        self.assertNotIn("branch_outcomes_sha256", life)

    def test_storage_control_rejects_historical_ablation_before_world(self):
        with patch("i3.runtime.life.World", side_effect=AssertionError("born too soon")):
            for kwargs in (
                {"learning_mode": "discard_values"},
                {"effect_readout": "blind_all"},
                {"score_addend_mode": "discard_curiosity_bonus"},
            ):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    run_life(
                        midpoint(), fixture(), 17, 3,
                        decision_policy=MODE, **kwargs)

    def test_dead_birth_never_records_branch(self):
        life = run_life(
            midpoint(), fixture((80., 0., 50., 80., 80.)), 17, 3,
            decision_policy=MODE, observer_mind_digest=True)
        self.assertEqual(life["steps_lived"], 0)
        self.assertEqual(life["branch_effect_memory"]["recorded"], 0)
        self.assertEqual(life["branch_effect_memory"]["retained"], 0)


if __name__ == "__main__":
    unittest.main()
