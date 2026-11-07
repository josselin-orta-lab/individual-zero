"""Storage-only P1.3 opportunity-recurrence control; software fixtures only."""
from collections import deque
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.genome import midpoint
from i3.modules.opportunity_recurrence import OBSERVE_WORK
from i3.modules.reference_memory_mind import ReferenceBranchMemoryMind
from i3.modules.reference_opportunity_memory_mind import (
    ReferenceOpportunityMemoryMind)
from i3.modules.world import WaterSource, World, WorldSpec
from i3.runtime.life import run_life

BODY = (80., 70., 50., 80., 80.)
MODE = "reference_opportunity_memory_v1"


def fixture(body=BODY):
    return WorldSpec(
        name="reference-opportunity-memory-software",
        width=1, height=1, spawn=(0, 0), body=body,
        water={(0, 0): WaterSource(12., stock=None)})


class ReferenceOpportunityMemoryMindTests(unittest.TestCase):
    def test_first_decision_is_exact_branch_memory_control_path(self):
        w = World(fixture())
        cap = w.capture()
        a = ReferenceBranchMemoryMind(
            midpoint(), 17, observer_decision_diagnostics=True,
            observer_full_competition=True)
        b = ReferenceOpportunityMemoryMind(
            midpoint(), 17, observer_decision_diagnostics=True,
            observer_full_competition=True)
        ba = CognitiveBudget(w.body, w.laws)
        bb = CognitiveBudget(w.body, w.laws)

        self.assertEqual(a.decide(cap, ba), b.decide(cap, bb))
        self.assertEqual(ba.work, bb.work)
        self.assertEqual(a.rng.getstate(), b.rng.getstate())
        self.assertEqual(a._budget_rng.getstate(), b._budget_rng.getstate())
        self.assertEqual(b.opportunity_records, 0)
        self.assertEqual(
            b.opportunity_memory.snapshot()["personal_step"], 0)
        self.assertEqual(
            b._pending_opportunity_presence, (True, False))

    def test_recurrence_store_is_bought_after_existing_learning_and_branch_store(self):
        g = midpoint()
        a = ReferenceBranchMemoryMind(g, 3)
        b = ReferenceOpportunityMemoryMind(g, 3)
        result = {"dead": (), "body": BODY}
        last = (BODY, ("dormir",), "dormir", None)
        sample = (1.0, BODY, BODY, False)
        for mind in (a, b):
            mind.last = last
            mind.buffer = deque([sample, sample, sample, sample])
            mind._branch_decision_work = CognitiveWork(cycles=3)
        b._pending_opportunity_presence = (True, False)

        ba = CognitiveBudget(BODY, BodyLaws())
        bb = CognitiveBudget(BODY, BodyLaws())
        ra = a.prepare_learning(result, ba)
        rb = b.prepare_learning(result, bb)

        self.assertEqual(ra, rb)
        for key in ("cycles", "simulated_steps", "memory_items", "replays"):
            self.assertEqual(
                getattr(bb.work, key),
                getattr(ba.work, key) + getattr(OBSERVE_WORK, key))

        self.assertEqual(
            b.learn_from_outcome(result, replay_limit=rb), rb)
        self.assertEqual(b.branch_records, 1)
        self.assertEqual(b.opportunity_records, 1)
        snap = b.opportunity_memory.snapshot()
        self.assertEqual(snap["personal_step"], 1)
        self.assertEqual(snap["last_onset"][0], 1)
        self.assertEqual(snap["gaps"]["water"], ())

    def test_no_processing_budget_creates_no_pending_personal_observation(self):
        body = (.001, 40., 40., 80., .001)
        w = World(fixture(body))
        mind = ReferenceOpportunityMemoryMind(midpoint(), 9)
        allowance = CognitiveBudget(w.body, w.laws)
        _action, _param, _work, info = mind.decide(w.capture(), allowance)
        self.assertEqual(info["funding"], "NO_PROCESSING_BUDGET")
        self.assertIsNone(mind._pending_opportunity_presence)
        self.assertEqual(mind.opportunity_records, 0)

    def test_runtime_manifest_and_receipts_label_storage_only_control(self):
        life = run_life(
            midpoint(), fixture(), 17, 4, keep_trace=True,
            observer_mind_digest=True, decision_policy=MODE,
            protocol="REFERENCE_OPPORTUNITY_MEMORY_SOFTWARE_ONLY")

        self.assertEqual(life["experimental_policy"], {
            "name": MODE,
            "score": "P1.3_reference_unchanged",
            "branch_memory": "global18_recent_personal_effects_v1",
            "opportunity_memory": "generic_onset_recurrence_latest3_v1",
            "opportunity_use": "STORAGE_ONLY_NOT_READ_BY_DECISION",
            "td_memory": "P1.3_unchanged"})

        self.assertIn("branch_effect_memory", life)
        rec = life["opportunity_recurrence_memory"]
        self.assertEqual(
            rec["decision_use"], "STORAGE_ONLY_NOT_READ_BY_DECISION")
        self.assertGreater(rec["recorded"], 0)
        self.assertEqual(
            rec["recorded"], rec["snapshot"]["personal_step"])
        self.assertIn("opportunity_recurrence_sha256", life)

    def test_old_branch_memory_runtime_has_no_recurrence_store(self):
        life = run_life(
            midpoint(), fixture(), 17, 3,
            observer_mind_digest=True,
            decision_policy="reference_branch_memory_v1")
        self.assertNotIn("opportunity_recurrence_memory", life)
        self.assertNotIn("opportunity_recurrence_sha256", life)

    def test_storage_control_rejects_historical_ablation_before_world(self):
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
                        midpoint(), fixture(), 17, 3,
                        decision_policy=MODE, **kwargs)

    def test_dead_birth_never_records_recurrence(self):
        life = run_life(
            midpoint(), fixture((80., 0., 50., 80., 80.)), 17, 3,
            decision_policy=MODE, observer_mind_digest=True)
        self.assertEqual(life["steps_lived"], 0)
        self.assertEqual(
            life["opportunity_recurrence_memory"]["recorded"], 0)
        self.assertEqual(
            life["opportunity_recurrence_memory"][
                "snapshot"]["personal_step"], 0)


if __name__ == "__main__":
    unittest.main()
