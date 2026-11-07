"""Recent RMS zero-mean effect prior: software only."""
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.recent_rms_effect_prior import (
    paid_recent_rms_zero_mean_effect_prior)
from i3.modules.reference_branches import ReferenceBranchMemory

BASE = (50., 50., 50., 50., 50.)


def record(memory, key, delta):
    after = tuple(a + b for a, b in zip(BASE, delta))
    memory.observe(
        key, BASE, CognitiveWork(),
        CognitiveBudget(after, BodyLaws()))


def allowance():
    return CognitiveBudget((80., 80., 80., 80., 80.), BodyLaws())


class RecentRmsEffectPriorTests(unittest.TestCase):
    def test_two_samples_preserve_zero_mean_and_raw_second_moment(self):
        memory = ReferenceBranchMemory()
        rows = (
            (-2., -.2, -.4, 0., 0.),
            (3., -.35, -.4, 0., 4.),
        )
        record(memory, ("se_deplacer", None), rows[0])
        record(memory, ("dormir", None), rows[1])
        result = paid_recent_rms_zero_mean_effect_prior(
            memory, allowance())
        self.assertEqual(
            result["status"],
            "COMPLETE_TWO_BRANCH_RMS_ZERO_MEAN_PRIOR")
        self.assertEqual(result["branch_count"], 2)
        self.assertEqual(result["expected_external_delta"], (0.,) * 5)
        expected_second = tuple(
            (rows[0][c] ** 2 + rows[1][c] ** 2) / 2.
            for c in range(5))
        for got, expected in zip(
                result["recent_raw_second_moment"], expected_second):
            self.assertAlmostEqual(got, expected)
        for got, expected in zip(
                result["branch_second_moment"], expected_second):
            self.assertAlmostEqual(got, expected)
        plus, minus = result["outcomes"]
        self.assertEqual(plus.probability, .5)
        self.assertEqual(minus.probability, .5)
        for a, b in zip(plus.probe_delta, minus.probe_delta):
            self.assertAlmostEqual(a, -b)
        self.assertFalse(result["mean_transfer"])

    def test_three_samples_use_all_recent_records_for_scale(self):
        memory = ReferenceBranchMemory()
        rows = (
            (-2., -.2, -.4, 0., 0.),
            (-.35, -.2, -.4, .2, 0.),
            (3., -.35, -.4, 0., 4.),
        )
        for action, delta in zip(
                ("se_deplacer", "attendre", "dormir"), rows):
            record(memory, (action, None), delta)
        result = paid_recent_rms_zero_mean_effect_prior(
            memory, allowance())
        expected = tuple(
            sum(row[c] ** 2 for row in rows) / 3.
            for c in range(5))
        self.assertEqual(result["support_records"], 3)
        for got, target in zip(
                result["recent_raw_second_moment"], expected):
            self.assertAlmostEqual(got, target)
        for got, target in zip(
                result["branch_second_moment"], expected):
            self.assertAlmostEqual(got, target)
        self.assertEqual(result["expected_external_delta"], (0.,) * 5)

    def test_sign_and_action_identity_do_not_change_scale_prior(self):
        a = ReferenceBranchMemory()
        b = ReferenceBranchMemory()
        rows_a = (
            (("se_deplacer", None), (-2., -.2, -.4, 0., 0.)),
            (("manger", "tok0"), (3., -.35, -.4, 0., 4.)),
        )
        rows_b = (
            (("attendre", None), (2., .2, .4, 0., 0.)),
            (("manger", "renamed"), (-3., .35, .4, 0., -4.)),
        )
        for key, delta in rows_a:
            record(a, key, delta)
        for key, delta in rows_b:
            record(b, key, delta)
        ra = paid_recent_rms_zero_mean_effect_prior(a, allowance())
        rb = paid_recent_rms_zero_mean_effect_prior(b, allowance())
        for key in (
                "rms_scale", "recent_raw_second_moment",
                "branch_second_moment", "expected_external_delta"):
            self.assertEqual(ra[key], rb[key])
        self.assertFalse(ra["action_identity_used"])
        self.assertFalse(ra["token_identity_used"])
        self.assertFalse(ra["body_need_used"])

    def test_fewer_than_two_records_never_invent_scale(self):
        for count in (0, 1):
            memory = ReferenceBranchMemory()
            if count:
                record(
                    memory, ("attendre", None),
                    (-.35, -.2, -.4, .2, 0.))
            result = paid_recent_rms_zero_mean_effect_prior(
                memory, allowance())
            self.assertEqual(
                result["status"], "INSUFFICIENT_GENERIC_SUPPORT")
            self.assertEqual(result["outcomes"], ())
            self.assertEqual(result["branch_count"], 0)
            self.assertEqual(result["expected_external_delta"], (0.,) * 5)

    def test_all_zero_history_creates_no_fake_uncertainty(self):
        memory = ReferenceBranchMemory()
        record(memory, ("attendre", None), (0.,) * 5)
        record(memory, ("dormir", None), (0.,) * 5)
        result = paid_recent_rms_zero_mean_effect_prior(
            memory, allowance())
        self.assertEqual(result["status"], "NO_EMPIRICAL_SCALE")
        self.assertEqual(result["outcomes"], ())
        self.assertEqual(result["rms_scale"], (0.,) * 5)
        self.assertEqual(result["branch_count"], 0)

    def test_exact_work_for_three_sample_scale(self):
        memory = ReferenceBranchMemory()
        for action, delta in (
            ("se_deplacer", (-2., -.2, -.4, 0., 0.)),
            ("attendre", (-.35, -.2, -.4, .2, 0.)),
            ("dormir", (3., -.35, -.4, 0., 4.)),
        ):
            record(memory, (action, None), delta)
        result = paid_recent_rms_zero_mean_effect_prior(
            memory, allowance())
        self.assertEqual(
            result["work_breakdown"]["memory_read"],
            {"cycles": 1, "simulated_steps": 0,
             "memory_items": 23, "replays": 0})
        self.assertEqual(
            result["work_breakdown"]["scale_construction"],
            {"cycles": 2, "simulated_steps": 0,
             "memory_items": 27, "replays": 0})
        self.assertEqual(
            result["work"],
            {"cycles": 3, "simulated_steps": 0,
             "memory_items": 50, "replays": 0})
        self.assertFalse(result["world_access"])
        self.assertFalse(result["cost_is_physical_settlement_receipt"])

    def test_wrong_memory_fails_before_spending(self):
        b = allowance()
        with self.assertRaises(ValueError):
            paid_recent_rms_zero_mean_effect_prior(object(), b)
        self.assertEqual(b.work, CognitiveWork())

    def test_module_import_does_not_load_mind_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.recent_rms_effect_prior; "
            "assert 'i3.modules.mind' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
