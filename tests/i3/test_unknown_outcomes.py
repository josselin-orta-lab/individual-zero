"""Unsupported-outcome belief tests: no study worlds or live policy."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork, debit_cognition)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.reference_branches import ReferenceBranchMemory
from i3.modules.unknown_outcomes import paid_frontier_actionable_belief

BODY = (50., 50., 50., 80., 50.)


def record(mind, memory, key, delta):
    """Create one personally lived effect in both old mean and new ring.

    P1.3 EffectsModel uses one-field keys for non-token actions, while the
    branch-memory custody key is always (action, token-or-None).
    """
    effect_key = key if key[0] in ("manger", "collecter") else (key[0],)
    mind.effects.observe(effect_key, delta)
    work = CognitiveWork(cycles=2, simulated_steps=1, memory_items=3)
    funded, _ = debit_cognition(BODY, BodyLaws(), work)
    after = tuple(x + d for x, d in zip(funded, delta))
    budget = CognitiveBudget(after, BodyLaws())
    memory.observe(key, BODY, work, budget)
    return budget


class FrontierActionableBeliefTests(unittest.TestCase):
    def test_newborn_has_structural_half_prior_but_no_invented_actionable_branch(self):
        mind = Mind(midpoint(), 1)
        memory = ReferenceBranchMemory()
        budget = CognitiveBudget(BODY, BodyLaws())
        result = paid_frontier_actionable_belief(mind, memory, budget)
        self.assertEqual(result["status"], "NO_ACTIONABLE_PERSONAL_MODEL")
        self.assertEqual(result["resource_base_rate"], .5)
        self.assertEqual(result["branches"], ())
        self.assertEqual(result["conditional_modality"], {
            "water": 0.0, "food_token": 0.0})
        self.assertEqual(result["work"], {
            "cycles": 1, "simulated_steps": 0,
            "memory_items": 4, "replays": 0})

    def test_water_prior_reuses_exact_p13_resource_base_rate(self):
        mind = Mind(midpoint(), 2)
        memory = ReferenceBranchMemory()
        mind.map = {
            (0, 0): (True, ()),
            (1, 0): (False, ()),
        }
        record(mind, memory, ("boire", None), (0., 0., 10., 0., 0.))
        result = paid_frontier_actionable_belief(
            mind, memory, CognitiveBudget(BODY, BodyLaws()))
        self.assertEqual(result["resource_base_rate"], .5)
        self.assertEqual(result["conditional_modality"], {
            "water": 1.0, "food_token": 0.0})
        self.assertEqual(result["support"]["water"], "SUPPORTED")
        self.assertEqual(
            [(r["signal"], r["probability"]) for r in result["branches"]],
            [("NO_ACTIONABLE_PERSONAL_MODEL", .5),
             ("ACTIONABLE_WATER", .5)])
        self.assertEqual(
            result["branches"][1]["resource_effects"],
            ((0., 0., 10., 0., 0.),))

    def test_water_and_food_make_at_most_three_normalized_branches(self):
        mind = Mind(midpoint(), 3)
        memory = ReferenceBranchMemory()
        mind.map = {
            (0, 0): (True, ()),
            (1, 0): (False, ("tok0",)),
            (2, 0): (False, ()),
        }
        record(mind, memory, ("boire", None), (0., 0., 9., 0., 0.))
        record(mind, memory, ("manger", "tok0"), (0., 8., 0., -1., 0.))
        result = paid_frontier_actionable_belief(
            mind, memory, CognitiveBudget(BODY, BodyLaws()))
        self.assertEqual(result["resource_base_rate"], .6)
        self.assertEqual(result["conditional_modality"], {
            "water": .5, "food_token": .5})
        rows = result["branches"]
        self.assertEqual(len(rows), 3)
        self.assertAlmostEqual(sum(x["probability"] for x in rows), 1.0)
        self.assertEqual(
            [(x["signal"], round(x["probability"], 10)) for x in rows],
            [("NO_ACTIONABLE_PERSONAL_MODEL", .4),
             ("ACTIONABLE_WATER", .3),
             ("ACTIONABLE_FOOD_TOKEN", .3)])
        self.assertEqual(
            rows[2]["resource_effects"],
            ((0., 8., 0., -1., 0.),))

    def test_unsupported_modality_mass_collapses_to_nonactionable(self):
        mind = Mind(midpoint(), 4)
        memory = ReferenceBranchMemory()
        mind.map = {
            (0, 0): (True, ("tok0",)),
            (1, 0): (False, ()),
        }
        record(mind, memory, ("boire", None), (0., 0., 10., 0., 0.))
        result = paid_frontier_actionable_belief(
            mind, memory, CognitiveBudget(BODY, BodyLaws()))
        # p_resource=.5 and observed modality incidence is half water, half token.
        # The unsupported token half is deliberately merged into nonactionable.
        self.assertEqual(
            [(x["signal"], x["probability"]) for x in result["branches"]],
            [("NO_ACTIONABLE_PERSONAL_MODEL", .75),
             ("ACTIONABLE_WATER", .25)])
        self.assertEqual(
            result["support"]["food"], "NO_PERSONAL_POSITIVE_EFFECT")

    def test_positive_old_mean_without_paid_recent_branch_is_not_actionable(self):
        mind = Mind(midpoint(), 5)
        memory = ReferenceBranchMemory()
        mind.map = {(0, 0): (True, ())}
        mind.effects.observe(("boire",), (0., 0., 10., 0., 0.))
        result = paid_frontier_actionable_belief(
            mind, memory, CognitiveBudget(BODY, BodyLaws()))
        self.assertEqual(result["support"]["water"], "NO_EMPIRICAL_BRANCH_SUPPORT")
        self.assertEqual(result["branches"], ())
        self.assertEqual(result["status"], "NO_ACTIONABLE_PERSONAL_MODEL")

    def test_food_token_renaming_does_not_change_prior_or_effect_arithmetic(self):
        outputs = []
        for seed, token in ((6, "tok0"), (7, "renamed-internal-token")):
            mind = Mind(midpoint(), seed)
            memory = ReferenceBranchMemory()
            mind.map = {
                (0, 0): (False, (token,)),
                (1, 0): (False, ()),
            }
            for delta in ((0., 6., 0., -1., 0.),
                          (0., -2., 0., -3., 0.),
                          (0., 9., 0., 0., 0.)):
                record(mind, memory, ("manger", token), delta)
            result = paid_frontier_actionable_belief(
                mind, memory, CognitiveBudget(BODY, BodyLaws()))
            outputs.append(result)
        self.assertEqual(outputs[0], outputs[1])

    def test_paid_scan_and_shared_branch_index_have_exact_work(self):
        mind = Mind(midpoint(), 8)
        memory = ReferenceBranchMemory()
        mind.map = {
            (0, 0): (True, ()),
            (1, 0): (False, ("tok0",)),
        }
        record(mind, memory, ("boire", None), (0., 0., 10., 0., 0.))
        record(mind, memory, ("manger", "tok0"), (0., 7., 0., 0., 0.))
        # EffectsModel has five entries:
        # boire, global, manger:tok0, manger:None, with global reused.
        self.assertEqual(len(mind.effects.stats), 4)
        budget = CognitiveBudget(BODY, BodyLaws())
        receipt = {}
        result = paid_frontier_actionable_belief(
            mind, memory, budget, work_receipt=receipt)
        # Personal scan: 2*2 map + 3*4 effects + 4 = 20 memory items.
        # First branch read: 7*2 + 2 = 16; second indexed lookup: 2.
        self.assertEqual(result["work"], {
            "cycles": 3, "simulated_steps": 0,
            "memory_items": 38, "replays": 0})
        self.assertEqual(receipt["work"], result["work"])
        self.assertEqual(receipt["status"],
                         "COMPLETE_ACTIONABLE_PERSONAL_BELIEF")

    def test_read_is_observer_free_and_does_not_mutate_personal_state(self):
        mind = Mind(midpoint(), 9)
        memory = ReferenceBranchMemory()
        mind.map = {(0, 0): (True, ())}
        record(mind, memory, ("boire", None), (0., 0., 8., 0., 0.))
        before_map = deepcopy(mind.map)
        before_stats = deepcopy(mind.effects.stats)
        before_samples = tuple(memory._samples)
        paid_frontier_actionable_belief(
            mind, memory, CognitiveBudget(BODY, BodyLaws()))
        self.assertEqual(mind.map, before_map)
        self.assertEqual(mind.effects.stats, before_stats)
        self.assertEqual(tuple(memory._samples), before_samples)

    def test_no_frontier_belief_after_physical_death(self):
        mind = Mind(midpoint(), 10)
        memory = ReferenceBranchMemory()
        budget = CognitiveBudget((50., 0., 50., 80., 50.), BodyLaws())
        with self.assertRaises(ValueError):
            paid_frontier_actionable_belief(mind, memory, budget)
        self.assertEqual(budget.work, CognitiveWork())

    def test_module_import_does_not_load_world_or_runtime_policy(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.unknown_outcomes; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.modules.mind' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
