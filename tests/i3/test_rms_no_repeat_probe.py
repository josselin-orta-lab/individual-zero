"""Persistence-free RMS information probe: no post-trial drink reuse."""
from itertools import combinations, product
from pathlib import Path
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
POST_NO_REPEAT = (
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


def make_mind():
    mind = Mind(midpoint(), 83)
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


class RmsNoRepeatProbeTests(unittest.TestCase):
    def test_competing_needs_can_create_information_without_repeat_drink(self):
        memory = realistic_memory()
        rows = []
        for a, b in combinations(range(5), 2):
            for level_a, level_b in product((25., 45.), repeat=2):
                body = [80., 80., 80., 80., 80.]
                body[a] = level_a
                body[b] = level_b
                body = tuple(body)
                for horizon in (4, 6, 8, 12):
                    try:
                        with patch(
                            "i3.modules.water_frontier_optional_trial."
                            "paid_three_leaf_target_prior",
                            side_effect=injected_prior(memory)):
                            result = paid_water_frontier_optional_trial_value(
                                make_mind(), EXPLORE, COMMON, POST_NO_REPEAT,
                                horizon, CognitiveBudget(body, BodyLaws()))
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
        informative = [row for row in rows if row[3] > 1e-12]
        selected_epistemic = [
            row for row in rows
            if "TRIAL" in row[2] and row[3] > 1e-12
        ]
        stats = {
            "evaluated": len(rows),
            "informative": len(informative),
            "selected_epistemic": len(selected_epistemic),
            "max_information_value": max(row[3] for row in rows),
            "best_trial_advantage": max(row[4] for row in rows),
            "worst_trial_advantage": min(row[4] for row in rows),
        }
        print("RMS_NO_REPEAT_SWEEP", stats)
        self.assertTrue(
            informative,
            "competing needs never create immediate-body information: "
            + repr(stats))


if __name__ == "__main__":
    unittest.main()
