"""Recent generic empirical effect prior: no live policy."""
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.recent_generic_effect_prior import (
    paid_recent_generic_effect_prior)
from i3.modules.reference_branches import ReferenceBranchMemory

BASE = (50., 50., 50., 50., 50.)


def record(memory, key, delta):
    after = tuple(a + b for a, b in zip(BASE, delta))
    budget = CognitiveBudget(after, BodyLaws())
    memory.observe(key, BASE, CognitiveWork(), budget)


def read_budget():
    return CognitiveBudget((80., 80., 80., 80., 80.), BodyLaws())


class RecentGenericEffectPriorTests(unittest.TestCase):
    def test_generic_read_returns_last_three_deltas_without_keys(self):
        memory = ReferenceBranchMemory()
        rows = (
            (("attendre", None), (-1., 0., 0., 0., 0.)),
            (("dormir", None), (3., -1., 0., 0., 4.)),
            (("se_deplacer", None), (-2., 0., -1., 0., 0.)),
            (("boire", None), (0., 0., 8., 0., 0.)),
        )
        for key, delta in rows:
            record(memory, key, delta)
        budget = read_budget()
        receipt = {}
        out = memory.recent_generic_effects(
            budget, work_receipt=receipt)
        self.assertEqual(out, tuple(delta for _, delta in rows[-3:]))
        self.assertEqual(receipt["records"], 3)
        self.assertFalse(receipt["action_identity_returned"])
        self.assertFalse(receipt["token_identity_returned"])
        self.assertEqual(
            receipt["work"],
            {"cycles": 1, "simulated_steps": 0,
             "memory_items": 30, "replays": 0})

    def test_two_recent_effects_form_equal_empirical_branches(self):
        memory = ReferenceBranchMemory()
        a = (-1., 0., 0., 0., 0.)
        b = (3., -1., 0., 0., 4.)
        record(memory, ("attendre", None), a)
        record(memory, ("dormir", None), b)
        result = paid_recent_generic_effect_prior(
            memory, read_budget())
        self.assertEqual(
            result["status"], "COMPLETE_TWO_BRANCH_EMPIRICAL_PRIOR")
        self.assertEqual(result["branch_count"], 2)
        self.assertEqual(
            tuple((o.probability, o.probe_delta) for o in result["outcomes"]),
            ((.5, a), (.5, b)))
        self.assertEqual(result["expected_external_delta"], (1., -.5, 0., 0., 2.))
        self.assertEqual(result["empirical_mean"], result["expected_external_delta"])

    def test_three_to_two_closest_pair_preserves_empirical_mean_exactly(self):
        memory = ReferenceBranchMemory()
        rows = (
            (0., 0., 0., 0., 0.),
            (1., 0., 0., 0., 0.),
            (10., 0., 0., 0., 0.),
        )
        for action, delta in zip(
                ("attendre", "dormir", "se_deplacer"), rows):
            record(memory, (action, None), delta)
        result = paid_recent_generic_effect_prior(
            memory, read_budget())
        self.assertEqual(
            result["compression"], "CLOSEST_PAIR_MEAN_PLUS_SINGLETON")
        self.assertEqual(
            tuple((o.probability, o.probe_delta) for o in result["outcomes"]),
            ((2. / 3., (.5, 0., 0., 0., 0.)),
             (1. / 3., (10., 0., 0., 0., 0.))))
        self.assertAlmostEqual(result["empirical_mean"][0], 11. / 3.)
        self.assertAlmostEqual(
            result["expected_external_delta"][0], 11. / 3.)
        for a, b in zip(
                result["empirical_mean"],
                result["expected_external_delta"]):
            self.assertAlmostEqual(a, b)

    def test_closest_pair_tie_resolves_by_chronological_pair_index(self):
        memory = ReferenceBranchMemory()
        rows = (
            (0., 0., 0., 0., 0.),
            (2., 0., 0., 0., 0.),
            (4., 0., 0., 0., 0.),
        )
        for action, delta in zip(
                ("attendre", "dormir", "se_deplacer"), rows):
            record(memory, (action, None), delta)
        result = paid_recent_generic_effect_prior(
            memory, read_budget())
        self.assertEqual(
            result["outcomes"][0].probe_delta,
            (1., 0., 0., 0., 0.))
        self.assertEqual(
            result["outcomes"][1].probe_delta,
            (4., 0., 0., 0., 0.))

    def test_action_and_token_renaming_do_not_change_prior(self):
        deltas = (
            (-1., 0., 0., 0., 0.),
            (3., -1., 0., 0., 4.),
            (-2., 0., -1., 0., 0.),
        )
        a = ReferenceBranchMemory()
        b = ReferenceBranchMemory()
        keys_a = (
            ("attendre", None),
            ("manger", "tok0"),
            ("boire", None),
        )
        keys_b = (
            ("dormir", None),
            ("manger", "renamed-token"),
            ("se_deplacer", None),
        )
        for key, delta in zip(keys_a, deltas):
            record(a, key, delta)
        for key, delta in zip(keys_b, deltas):
            record(b, key, delta)
        ra = paid_recent_generic_effect_prior(a, read_budget())
        rb = paid_recent_generic_effect_prior(b, read_budget())
        for key in (
                "outcomes", "raw_recent_deltas", "empirical_mean",
                "expected_external_delta", "compression", "work"):
            self.assertEqual(ra[key], rb[key])
        self.assertFalse(ra["action_identity_used"])
        self.assertFalse(ra["token_identity_used"])

    def test_fewer_than_two_samples_never_invent_support(self):
        for count in (0, 1):
            memory = ReferenceBranchMemory()
            if count:
                record(memory, ("attendre", None), (-1., 0., 0., 0., 0.))
            result = paid_recent_generic_effect_prior(
                memory, read_budget())
            self.assertEqual(
                result["status"], "INSUFFICIENT_GENERIC_SUPPORT")
            self.assertEqual(result["outcomes"], ())
            self.assertEqual(result["branch_count"], 0)

    def test_duplicate_only_recent_history_has_no_fake_information(self):
        memory = ReferenceBranchMemory()
        delta = (-1., 0., 0., 0., 0.)
        for action in ("attendre", "se_deplacer", "dormir"):
            record(memory, (action, None), delta)
        result = paid_recent_generic_effect_prior(
            memory, read_budget())
        self.assertEqual(result["status"], "NO_EMPIRICAL_DIVERSITY")
        self.assertEqual(result["outcomes"], ())
        self.assertEqual(result["branch_count"], 0)
        self.assertEqual(result["empirical_mean"], delta)

    def test_scan_and_compression_are_both_paid(self):
        memory = ReferenceBranchMemory()
        for action, delta in (
            ("attendre", (-1., 0., 0., 0., 0.)),
            ("dormir", (3., -1., 0., 0., 4.)),
            ("se_deplacer", (-2., 0., -1., 0., 0.)),
        ):
            record(memory, (action, None), delta)
        result = paid_recent_generic_effect_prior(
            memory, read_budget())
        self.assertEqual(
            result["work_breakdown"]["memory_read"],
            {"cycles": 1, "simulated_steps": 0,
             "memory_items": 23, "replays": 0})
        self.assertEqual(
            result["work_breakdown"]["compression"],
            {"cycles": 4, "simulated_steps": 0,
             "memory_items": 27, "replays": 0})
        self.assertEqual(
            result["work"],
            {"cycles": 5, "simulated_steps": 0,
             "memory_items": 50, "replays": 0})
        self.assertFalse(result["cost_is_physical_settlement_receipt"])
        self.assertFalse(result["world_access"])
        self.assertFalse(result["body_need_used"])
        self.assertFalse(result["point_prior"])

    def test_wrong_memory_fails_before_spending(self):
        budget = read_budget()
        with self.assertRaises(ValueError):
            paid_recent_generic_effect_prior(object(), budget)
        self.assertEqual(budget.work, CognitiveWork())

    def test_module_import_does_not_load_mind_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.recent_generic_effect_prior; "
            "assert 'i3.modules.mind' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
