"""Opportunity recurrence memory: first-person software substrate only."""
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork)
from i3.modules.opportunity_recurrence import (
    OBSERVE_WORK, OpportunityRecurrenceMemory, WINDOW)

BODY = (80., 80., 80., 80., 80.)


def budget(body=BODY):
    return CognitiveBudget(body, BodyLaws())


def observe(memory, water, token):
    return memory.observe((water, token), budget())


class OpportunityRecurrenceMemoryTests(unittest.TestCase):
    def test_empty_birth_has_no_numeric_recurrence_prior(self):
        memory = OpportunityRecurrenceMemory()
        result = memory.estimate("water", 8, budget())
        self.assertEqual(result["status"], "NO_PERSONAL_RECURRENCE_SUPPORT")
        self.assertIsNone(result["future_matching_opportunity_probability"])
        self.assertEqual(result["retained_gaps"], ())
        self.assertFalse(result["current_source_persistence_assumed"])

    def test_continuous_visibility_creates_only_one_onset(self):
        memory = OpportunityRecurrenceMemory()
        first = observe(memory, True, False)
        second = observe(memory, True, False)
        third = observe(memory, True, False)
        self.assertEqual(first["onsets"], ("water",))
        self.assertEqual(second["onsets"], ())
        self.assertEqual(third["onsets"], ())
        estimate = memory.estimate("water", 100, budget())
        self.assertEqual(estimate["support_count"], 0)
        self.assertIsNone(
            estimate["future_matching_opportunity_probability"])

    def test_disappear_and_reappear_creates_personal_gap(self):
        memory = OpportunityRecurrenceMemory()
        observe(memory, True, False)    # onset at 1
        observe(memory, False, False)
        row = observe(memory, True, False)  # onset at 3
        self.assertEqual(row["completed_gaps"], (("water", 2),))
        short = memory.estimate("water", 1, budget())
        long = memory.estimate("water", 2, budget())
        self.assertEqual(short["future_matching_opportunity_probability"], 0.0)
        self.assertEqual(long["future_matching_opportunity_probability"], 1.0)

    def test_water_and_token_recurrence_are_independent(self):
        memory = OpportunityRecurrenceMemory()
        observe(memory, True, False)     # water onset 1
        observe(memory, False, True)     # token onset 2
        observe(memory, True, True)      # water onset 3, token continuous
        observe(memory, False, False)
        observe(memory, False, True)     # token onset 5

        water = memory.estimate("water", 2, budget())
        token = memory.estimate("token", 2, budget())
        self.assertEqual(water["retained_gaps"], (2,))
        self.assertEqual(token["retained_gaps"], (3,))
        self.assertEqual(
            water["future_matching_opportunity_probability"], 1.0)
        self.assertEqual(
            token["future_matching_opportunity_probability"], 0.0)

    def test_latest_three_gaps_evict_deterministically(self):
        memory = OpportunityRecurrenceMemory()
        # Onsets at 1, 3, 6, 10, 15 -> gaps 2,3,4,5; retain latest 3.
        pattern = {
            1: True, 2: False,
            3: True, 4: False, 5: False,
            6: True, 7: False, 8: False, 9: False,
            10: True, 11: False, 12: False, 13: False, 14: False,
            15: True,
        }
        for step in range(1, 16):
            observe(memory, pattern.get(step, False), False)
        result = memory.estimate("water", 4, budget())
        self.assertEqual(result["retained_gaps"], (3, 4, 5))
        self.assertEqual(result["support_count"], WINDOW)
        self.assertEqual(
            result["future_matching_opportunity_probability"], 2.0 / 3.0)

    def test_probability_is_monotone_in_planning_horizon(self):
        memory = OpportunityRecurrenceMemory()
        for present in (
                True, False, True, False, False, True,
                False, False, False, True):
            observe(memory, present, False)
        values = [
            memory.estimate("water", horizon, budget())[
                "future_matching_opportunity_probability"]
            for horizon in (1, 2, 3, 4, 8)
        ]
        self.assertEqual(values, sorted(values))

    def test_api_state_contains_no_position_token_identity_or_world_time(self):
        memory = OpportunityRecurrenceMemory()
        row = observe(memory, True, True)
        snap = memory.snapshot()
        self.assertFalse(row["position_input"])
        self.assertFalse(row["token_identity_input"])
        self.assertFalse(row["world_time_input"])
        flat = repr(snap).lower()
        for forbidden in ("position", "source", "stock", "schedule", "world"):
            self.assertNotIn(forbidden, flat)

    def test_observe_and_estimate_have_explicit_fixed_paid_work(self):
        memory = OpportunityRecurrenceMemory()
        allowance = budget()
        receipt = {}
        row = memory.observe((True, False), allowance, work_receipt=receipt)
        self.assertEqual(allowance.work, OBSERVE_WORK)
        self.assertEqual(row["work"], {
            "cycles": 1, "simulated_steps": 0,
            "memory_items": 8, "replays": 0})
        self.assertEqual(receipt["work"], row["work"])

        observe(memory, False, False)
        observe(memory, True, False)
        read = budget()
        estimate = memory.estimate("water", 2, read)
        self.assertEqual(read.work, CognitiveWork(cycles=1, memory_items=3))
        self.assertEqual(estimate["work"], {
            "cycles": 1, "simulated_steps": 0,
            "memory_items": 3, "replays": 0})

    def test_unfunded_observation_does_not_advance_chronology(self):
        memory = OpportunityRecurrenceMemory()
        low = (.001, 80., 80., 80., .001)
        allowance = budget(low)
        before = memory.snapshot()
        with self.assertRaises(CognitiveFundingError):
            memory.observe((True, False), allowance)
        self.assertEqual(allowance.work, CognitiveWork())
        self.assertEqual(memory.snapshot(), before)

    def test_dead_body_and_invalid_inputs_fail_closed(self):
        memory = OpportunityRecurrenceMemory()
        dead = budget((80., 80., 0., 80., 80.))
        with self.assertRaises(ValueError):
            memory.observe((True, False), dead)
        self.assertEqual(dead.work, CognitiveWork())

        with self.assertRaises(ValueError):
            memory.observe((1, False), budget())
        with self.assertRaises(ValueError):
            memory.estimate("food-name", 4, budget())
        with self.assertRaises(ValueError):
            memory.estimate("water", 0, budget())

    def test_module_import_does_not_load_mind_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.opportunity_recurrence; "
            "assert 'i3.modules.mind' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
