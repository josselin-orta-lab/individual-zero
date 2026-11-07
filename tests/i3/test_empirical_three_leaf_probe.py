"""Empirical three-leaf target prior and optional-trial software probe."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork)
from i3.modules.empirical_three_leaf_target_prior import (
    paid_empirical_three_leaf_target_prior)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.reference_branches import ReferenceBranchMemory
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


def harmful_memory():
    memory = ReferenceBranchMemory()
    for key, delta in (
        (("se_deplacer", None), (-2., -.2, -.4, 0., 0.)),
        (("attendre", None), (-1., -1., -1., -.5, -.5)),
        (("dormir", None), (-3., -.5, -2., -.2, -1.)),
    ):
        record(memory, key, delta)
    return memory


def make_mind():
    mind = Mind(midpoint(), 59)
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
        return paid_empirical_three_leaf_target_prior(
            personal_map, memory, target_modality, budget)
    return build


class EmpiricalThreeLeafPriorTests(unittest.TestCase):
    def test_three_recent_effects_fit_exactly_three_target_leaves(self):
        result = paid_empirical_three_leaf_target_prior(
            {}, realistic_memory(), "water",
            CognitiveBudget((80.,) * 5, BodyLaws()))
        self.assertEqual(
            result["status"],
            "COMPLETE_EMPIRICAL_THREE_LEAF_TARGET_PRIOR")
        self.assertEqual(result["leaf_count"], 3)
        self.assertEqual(result["target_probability"], .25)
        probs = tuple(row["probability"] for row in result["leaves"])
        self.assertAlmostEqual(probs[0], .75)
        self.assertAlmostEqual(probs[1], 1. / 6.)
        self.assertAlmostEqual(probs[2], 1. / 12.)
        self.assertEqual(result["effect_support_records"], 3)
        self.assertEqual(
            result["effect_compression"],
            "CLOSEST_PAIR_MEAN_PLUS_SINGLETON")

    def test_whole_tree_mean_is_target_weighted_personal_mean(self):
        result = paid_empirical_three_leaf_target_prior(
            {}, realistic_memory(), "water",
            CognitiveBudget((80.,) * 5, BodyLaws()))
        for a, b in zip(
                result["expected_external_delta"],
                result["target_weighted_personal_mean"]):
            self.assertAlmostEqual(a, b)
        self.assertNotEqual(result["expected_external_delta"], (0.,) * 5)
        self.assertFalse(result["body_need_used"])

    def test_insufficient_personal_support_creates_no_target_trial_leaves(self):
        memory = ReferenceBranchMemory()
        record(memory, ("attendre", None), (-.35, -.2, -.4, .2, 0.))
        result = paid_empirical_three_leaf_target_prior(
            {}, memory, "water",
            CognitiveBudget((80.,) * 5, BodyLaws()))
        self.assertEqual(
            result["status"], "INSUFFICIENT_GENERIC_SUPPORT")
        self.assertEqual(result["leaves"], ())
        self.assertEqual(result["leaf_count"], 0)

    def test_action_and_token_renaming_do_not_change_composed_prior(self):
        deltas = (
            (-2., -.2, -.4, 0., 0.),
            (-.35, -.2, -.4, .2, 0.),
            (3., -.35, -.4, 0., 4.),
        )
        a = ReferenceBranchMemory()
        b = ReferenceBranchMemory()
        for key, delta in zip(
                (("se_deplacer", None), ("manger", "tok0"), ("boire", None)),
                deltas):
            record(a, key, delta)
        for key, delta in zip(
                (("attendre", None), ("manger", "renamed"), ("dormir", None)),
                deltas):
            record(b, key, delta)
        ra = paid_empirical_three_leaf_target_prior(
            {}, a, "water", CognitiveBudget((80.,) * 5, BodyLaws()))
        rb = paid_empirical_three_leaf_target_prior(
            {}, b, "water", CognitiveBudget((80.,) * 5, BodyLaws()))
        for key in (
                "leaves", "expected_external_delta",
                "effect_empirical_mean", "effect_compression", "work"):
            self.assertEqual(ra[key], rb[key])
        self.assertFalse(ra["action_identity_used"])
        self.assertFalse(ra["token_identity_used"])

    def test_realistic_empirical_prior_selects_some_trials_and_declines_others(self):
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
                        body, horizon, result["target_node_best_choices"],
                        result["trial_information_value"],
                        result["trial_advantage"]))
        self.assertTrue(rows)
        selected = [row for row in rows if "TRIAL" in row[2]]
        declined = [row for row in rows if row[2] == ("DECLINE_TRIAL",)]
        print("EMPIRICAL_OPTIONAL_TRIAL_SWEEP", {
            "evaluated": len(rows),
            "selected": len(selected),
            "declined": len(declined),
            "best_trial_advantage": max(row[4] for row in rows),
            "worst_trial_advantage": min(row[4] for row in rows),
            "max_information_value": max(row[3] for row in rows),
        })
        self.assertTrue(selected, "empirical prior never initiates a trial")
        self.assertTrue(declined, "empirical prior acts like forced curiosity")

    def test_personally_harmful_empirical_prior_declines_unknown_trial(self):
        body = (80., 80., 40., 80., 80.)
        memory = harmful_memory()
        with patch(
            "i3.modules.water_frontier_optional_trial."
            "paid_three_leaf_target_prior",
            side_effect=injected_prior(memory)):
            result = paid_water_frontier_optional_trial_value(
                make_mind(), EXPLORE, COMMON, POST, 6,
                CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            result["target_node_best_choices"], ("DECLINE_TRIAL",))
        self.assertLess(result["trial_advantage"], 0.)

    def test_probe_does_not_mutate_memory_or_mind_state(self):
        body = (20., 80., 80., 80., 80.)
        memory = realistic_memory()
        mind = make_mind()
        before_memory = tuple(
            (s.key, s.delta) for s in memory._samples)
        before = {
            "effects": deepcopy(mind.effects.stats),
            "values": deepcopy(mind.values),
            "buffer": tuple(mind.buffer),
            "rng": mind.rng.getstate(),
        }
        with patch(
            "i3.modules.water_frontier_optional_trial."
            "paid_three_leaf_target_prior",
            side_effect=injected_prior(memory)):
            paid_water_frontier_optional_trial_value(
                mind, EXPLORE, COMMON, POST, 6,
                CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            tuple((s.key, s.delta) for s in memory._samples),
            before_memory)
        self.assertEqual(mind.effects.stats, before["effects"])
        self.assertEqual(mind.values, before["values"])
        self.assertEqual(tuple(mind.buffer), before["buffer"])
        self.assertEqual(mind.rng.getstate(), before["rng"])

    def test_module_import_does_not_load_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.empirical_three_leaf_target_prior; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
