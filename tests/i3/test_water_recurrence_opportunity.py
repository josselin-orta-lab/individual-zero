"""Personal recurrence composition with the water Stage-1 software kernel."""
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.opportunity_recurrence import OpportunityRecurrenceMemory
from i3.modules.reference_branches import ReferenceBranchMemory
from i3.modules.water_future_opportunity import (
    paid_water_one_future_opportunity_value)
from i3.modules.water_recurrence_opportunity import (
    paid_water_personal_recurrence_value)

BASE = (50., 50., 50., 50., 50.)
EXPLORE = (("se_deplacer",),)
STOP_AFTER_PREFIX = (("stop-after-prefix", ()),)


def record(memory, key, delta):
    after = tuple(a + b for a, b in zip(BASE, delta))
    memory.observe(
        key, BASE, CognitiveWork(),
        CognitiveBudget(after, BodyLaws()))


def realistic_effect_memory():
    memory = ReferenceBranchMemory()
    for key, delta in (
        (("se_deplacer", None), (-2., -.2, -.4, 0., 0.)),
        (("attendre", None), (-.35, -.2, -.4, .2, 0.)),
        (("dormir", None), (3., -.35, -.4, 0., 4.)),
    ):
        record(memory, key, delta)
    return memory


def recurrence_2_6_10():
    memory = OpportunityRecurrenceMemory()
    onsets = {1, 3, 9, 19}
    for step in range(1, 20):
        memory.observe(
            (step in onsets, False),
            CognitiveBudget((80., 80., 80., 80., 80.), BodyLaws()))
    return memory


def make_mind():
    mind = Mind(midpoint(), 197)
    mind.map = {}
    mind.effects.observe(
        ("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    mind.effects.observe(
        ("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(
        ("dormir",), (3., -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    return mind


class WaterPersonalRecurrenceTests(unittest.TestCase):
    def test_no_personal_recurrence_support_does_not_substitute_probability(self):
        body = (80., 80., 25., 80., 80.)
        recurrence = OpportunityRecurrenceMemory()
        result = paid_water_personal_recurrence_value(
            make_mind(), realistic_effect_memory(), recurrence,
            EXPLORE, STOP_AFTER_PREFIX, 6,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            result["status"], "NO_PERSONAL_FUTURE_OPPORTUNITY_SUPPORT")
        self.assertIsNone(result["future_water_opportunity_probability"])
        self.assertFalse(result["trial_evaluated"])
        self.assertIsNone(result["trial_information_value"])
        self.assertEqual(
            result["work"]["cycles"], 1)

    def test_fixed_personal_history_produces_expected_horizon_probabilities(self):
        recurrence = recurrence_2_6_10()
        expected = {4: 1. / 3., 6: 2. / 3., 8: 2. / 3., 12: 1.0}
        for horizon, probability in expected.items():
            result = recurrence.estimate(
                "water", horizon,
                CognitiveBudget((80., 80., 80., 80., 80.), BodyLaws()))
            self.assertAlmostEqual(
                result["future_matching_opportunity_probability"],
                probability)

    def test_recurrence_probability_replaces_modality_proxy_without_extra_leaf(self):
        body = (80., 80., 25., 80., 80.)
        result = paid_water_personal_recurrence_value(
            make_mind(), realistic_effect_memory(), recurrence_2_6_10(),
            EXPLORE, STOP_AFTER_PREFIX, 6,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            result["future_opportunity_probability_source"],
            "PAID_PERSONAL_ONSET_RECURRENCE")
        self.assertAlmostEqual(
            result["future_water_opportunity_probability"], 2. / 3.)
        self.assertEqual(result["subjective_leaf_count"], 3)
        self.assertTrue(result["future_availability_marginalized"])
        self.assertFalse(
            result["future_availability_simulated_as_extra_branch"])
        self.assertEqual(result["prior_expected_external_delta"], (0.,) * 5)

    def test_default_historical_kernel_keeps_modality_proxy_semantics(self):
        body = (80., 80., 25., 80., 80.)
        result = paid_water_one_future_opportunity_value(
            make_mind(), realistic_effect_memory(), EXPLORE,
            STOP_AFTER_PREFIX, 6,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            result["future_opportunity_probability_source"],
            "CURRENT_FIRST_PERSON_MODALITY_PROXY")
        self.assertEqual(
            result["future_water_opportunity_probability"],
            result["water_probability"])

    def test_exact_prefix_grid_characterizes_recurrence_decision_boundary(self):
        recurrence = recurrence_2_6_10()
        effect_memory = realistic_effect_memory()
        rows = []
        for channel in range(5):
            for level in (20., 30., 40., 50.):
                body = [80., 80., 80., 80., 80.]
                body[channel] = level
                body = tuple(body)
                for horizon in (4, 6, 8, 12):
                    try:
                        result = paid_water_personal_recurrence_value(
                            make_mind(), effect_memory, recurrence,
                            EXPLORE, STOP_AFTER_PREFIX, horizon,
                            CognitiveBudget(body, BodyLaws()))
                    except CognitiveFundingError:
                        continue
                    if not result["trial_evaluated"]:
                        continue
                    rows.append(result)

        selected = [
            row for row in rows
            if "TRIAL" in row["target_node_best_choices"]
            and row["trial_information_value"] > 1e-12
        ]
        declined = [
            row for row in rows
            if row["target_node_best_choices"] == ("DECLINE_TRIAL",)
        ]
        stats = {
            "evaluated": len(rows),
            "selected_epistemic": len(selected),
            "declined": len(declined),
            "max_information_value": (
                max(row["trial_information_value"] for row in rows)
                if rows else None),
            "best_trial_advantage": (
                max(row["trial_advantage"] for row in rows)
                if rows else None),
            "worst_trial_advantage": (
                min(row["trial_advantage"] for row in rows)
                if rows else None),
            "future_probabilities": sorted(set(
                row["future_water_opportunity_probability"]
                for row in rows)),
        }
        print("PERSONAL_RECURRENCE_WATER_SWEEP", stats)
        self.assertTrue(rows)
        # No positive selection requirement. A zero count is an admissible
        # falsification of recurrence as the missing Stage-1 prerequisite.
        self.assertTrue(all(
            row["future_opportunity_probability_source"] ==
            "PAID_PERSONAL_ONSET_RECURRENCE"
            for row in rows))

    def test_recurrence_read_is_included_in_total_paid_work(self):
        body = (100., 80., 25., 80., 100.)
        allowance = CognitiveBudget(body, BodyLaws())
        result = paid_water_personal_recurrence_value(
            make_mind(), realistic_effect_memory(), recurrence_2_6_10(),
            EXPLORE, STOP_AFTER_PREFIX, 6, allowance)
        self.assertEqual(result["work_breakdown"]["total"], result["work"])
        self.assertEqual(
            result["work_breakdown"]["recurrence"]["cycles"], 1)
        for key in ("cycles", "simulated_steps", "memory_items", "replays"):
            self.assertLessEqual(
                result["work"][key],
                result["forecast_work_ceiling"][key])

    def test_module_import_does_not_load_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.water_recurrence_opportunity; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
