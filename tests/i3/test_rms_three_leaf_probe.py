"""RMS three-leaf target prior and optional-trial software probe."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.reference_branches import ReferenceBranchMemory
from i3.modules.rms_three_leaf_target_prior import (
    paid_rms_three_leaf_target_prior)
from i3.modules.water_frontier_optional_trial import (
    paid_water_frontier_optional_trial_value)

BASE = (50., 50., 50., 50., 50.)
EXPLORE = (("se_deplacer",),)
COMMON = (
    ("ordinary-wait", (("attendre",),)),
    ("ordinary-sleep", (("dormir",),)),
)
POST = (
    ("post-wait", (("attendre",),)),
    ("post-sleep", (("dormir",),)),
)


def record(memory, key, delta):
    after = tuple(a + b for a, b in zip(BASE, delta))
    memory.observe(
        key, BASE, CognitiveWork(),
        CognitiveBudget(after, BodyLaws()))


def realistic_memory():
    memory = ReferenceBranchMemory()
    for key, delta in (
        (("se_deplacer", None), (-2., -.2, -.4, 0., 0.)),
        (("attendre", None), (-.35, -.2, -.4, .2, 0.)),
        (("dormir", None), (3., -.35, -.4, 0., 4.)),
    ):
        record(memory, key, delta)
    return memory


def high_scale_memory():
    memory = ReferenceBranchMemory()
    for key, delta in (
        (("se_deplacer", None), (35., 20., 20., 15., 25.)),
        (("attendre", None), (-40., -25., -30., -10., -30.)),
        (("dormir", None), (30., -20., 25., -20., 20.)),
    ):
        record(memory, key, delta)
    return memory


def make_mind():
    mind = Mind(midpoint(), 71)
    mind.map = {}
    mind.effects.observe(
        ("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    mind.effects.observe(
        ("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(
        ("dormir",), (3., -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    return mind


def injected_prior(memory):
    def build(personal_map, _body, _theta, _powers, _weights,
              target_modality, budget):
        return paid_rms_three_leaf_target_prior(
            personal_map, memory, target_modality, budget)
    return build


class RmsThreeLeafProbeTests(unittest.TestCase):
    def test_complete_prior_has_three_leaves_and_exact_zero_mean(self):
        result = paid_rms_three_leaf_target_prior(
            {}, realistic_memory(), "water",
            CognitiveBudget((80.,) * 5, BodyLaws()))
        self.assertEqual(
            result["status"],
            "COMPLETE_RMS_THREE_LEAF_TARGET_PRIOR")
        self.assertEqual(result["leaf_count"], 3)
        self.assertEqual(result["target_probability"], .25)
        self.assertEqual(result["expected_external_delta"], (0.,) * 5)
        self.assertEqual(
            tuple(row["probability"] for row in result["leaves"]),
            (.75, .125, .125))
        a = result["leaves"][1]["effect_delta"]
        b = result["leaves"][2]["effect_delta"]
        for x, y in zip(a, b):
            self.assertAlmostEqual(x, -y)

    def test_target_composition_preserves_recent_second_moment_scale(self):
        result = paid_rms_three_leaf_target_prior(
            {}, realistic_memory(), "water",
            CognitiveBudget((80.,) * 5, BodyLaws()))
        raw = result["recent_raw_second_moment"]
        branch = result["branch_second_moment"]
        for a, b in zip(raw, branch):
            self.assertAlmostEqual(a, b)
        self.assertEqual(
            result["cross_channel_approximation"],
            "SYMMETRIC_PLUS_MINUS_RMS_IMPOSES_RANK_ONE_COMMON_SIGN_STRUCTURE")

    def test_insufficient_support_never_invents_target_trial_leaves(self):
        memory = ReferenceBranchMemory()
        record(memory, ("attendre", None), (-.35, -.2, -.4, .2, 0.))
        result = paid_rms_three_leaf_target_prior(
            {}, memory, "water",
            CognitiveBudget((80.,) * 5, BodyLaws()))
        self.assertEqual(
            result["status"], "INSUFFICIENT_GENERIC_SUPPORT")
        self.assertEqual(result["leaves"], ())
        self.assertEqual(result["leaf_count"], 0)

    def test_realistic_rms_prior_must_show_selective_epistemic_trial(self):
        memory = realistic_memory()
        rows = []
        for channel in range(5):
            for level in (20., 30., 40., 50.):
                body = [80., 80., 80., 80., 80.]
                body[channel] = level
                body = tuple(body)
                for horizon in (4, 6, 8, 12):
                    try:
                        with patch(
                            "i3.modules.water_frontier_optional_trial."
                            "paid_three_leaf_target_prior",
                            side_effect=injected_prior(memory)):
                            result = paid_water_frontier_optional_trial_value(
                                make_mind(), EXPLORE, COMMON, POST, horizon,
                                CognitiveBudget(body, BodyLaws()))
                    except CognitiveFundingError:
                        continue
                    rows.append((
                        body,
                        horizon,
                        result["target_node_best_choices"],
                        result["trial_information_value"],
                        result["trial_advantage"],
                    ))
        self.assertTrue(rows)
        selected_epistemic = [
            row for row in rows
            if "TRIAL" in row[2] and row[3] > 1e-12
        ]
        declined = [
            row for row in rows
            if row[2] == ("DECLINE_TRIAL",)
        ]
        stats = {
            "evaluated": len(rows),
            "selected_epistemic": len(selected_epistemic),
            "declined": len(declined),
            "max_information_value": max(row[3] for row in rows),
            "best_trial_advantage": max(row[4] for row in rows),
            "worst_trial_advantage": min(row[4] for row in rows),
        }
        print("RMS_OPTIONAL_TRIAL_SWEEP", stats)
        self.assertTrue(
            selected_epistemic,
            "RMS prior never selects a trial for positive information: "
            + repr(stats))
        self.assertTrue(
            declined,
            "RMS prior acts like forced experimentation: " + repr(stats))

    def test_high_personal_uncertainty_can_still_reject_trial(self):
        body = (80., 80., 25., 80., 80.)
        with patch(
            "i3.modules.water_frontier_optional_trial."
            "paid_three_leaf_target_prior",
            side_effect=injected_prior(high_scale_memory())):
            result = paid_water_frontier_optional_trial_value(
                make_mind(), EXPLORE, COMMON, POST, 6,
                CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            result["target_node_best_choices"], ("DECLINE_TRIAL",))
        self.assertLess(result["trial_advantage"], 0.)

    def test_test_only_probe_does_not_mutate_memory_or_mind(self):
        body = (20., 80., 80., 80., 80.)
        memory = realistic_memory()
        mind = make_mind()
        before_memory = tuple(
            (sample.key, sample.delta) for sample in memory._samples)
        before = {
            "effects": deepcopy(mind.effects.stats),
            "values": deepcopy(mind.values),
            "buffer": tuple(mind.buffer),
            "map": deepcopy(mind.map),
            "hist": deepcopy(mind.hist),
            "rng": mind.rng.getstate(),
            "budget_rng": mind._budget_rng.getstate(),
        }
        with patch(
            "i3.modules.water_frontier_optional_trial."
            "paid_three_leaf_target_prior",
            side_effect=injected_prior(memory)):
            paid_water_frontier_optional_trial_value(
                mind, EXPLORE, COMMON, POST, 6,
                CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            tuple((sample.key, sample.delta) for sample in memory._samples),
            before_memory)
        self.assertEqual(mind.effects.stats, before["effects"])
        self.assertEqual(mind.values, before["values"])
        self.assertEqual(tuple(mind.buffer), before["buffer"])
        self.assertEqual(mind.map, before["map"])
        self.assertEqual(mind.hist, before["hist"])
        self.assertEqual(mind.rng.getstate(), before["rng"])
        self.assertEqual(mind._budget_rng.getstate(), before["budget_rng"])

    def test_module_import_does_not_load_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.rms_three_leaf_target_prior; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
