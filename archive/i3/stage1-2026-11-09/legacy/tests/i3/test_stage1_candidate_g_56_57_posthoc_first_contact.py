"""Adversarial synthetic tests for the 56/57 read-only first-contact audit.

These are synthetic receipts, never new experimental lives or replays.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i3.lab.stage1_candidate_g_56_57_posthoc_first_contact import (
    EVIDENCE_BRANCH, EXECUTION_SHA, drink_base_gap, is_water_option,
    load_archive, projection_label)


def score(option, base, **extra):
    return {"option": option, "base_return": base, **extra}


class FirstContactAuditHelpers(unittest.TestCase):
    def test_water_options_are_drink_or_travel_to_drink(self):
        self.assertTrue(is_water_option("boire"))
        self.assertTrue(is_water_option("goto-boire:1,-3"))
        self.assertFalse(is_water_option("goto-manger:tok0:1,0"))
        self.assertFalse(is_water_option("explorer:0,1"))

    def test_drink_gap_is_relative_to_best_other_base_value(self):
        scores = [score("boire", -1.2), score("attendre", -1.5),
                  score("dormir", -1.1)]
        self.assertAlmostEqual(drink_base_gap(scores), -0.1)
        self.assertIsNone(drink_base_gap([score("attendre", -1.0)]))
        self.assertIsNone(drink_base_gap([score("boire", -1.0)]))

    def test_identical_drink_and_wait_base_values_give_zero_gap(self):
        scores = [score("boire", -1.5943354840931943),
                  score("attendre", -1.5943354840931943)]
        self.assertEqual(drink_base_gap(scores), 0.0)

    def test_nonfinite_archived_base_value_fails_closed(self):
        with self.assertRaises(ValueError):
            drink_base_gap([score("boire", float("nan")),
                            score("attendre", -1.0)])

    def test_projector_labels_come_only_from_archived_fields(self):
        g_life = {"manifest": {"experimental_policy": {}}}
        self.assertEqual(projection_label(
            "Candidate-G", g_life,
            score("attendre", 0.0, decision_projection_mode="candidate_f")),
            "candidate_f")
        with self.assertRaises(ValueError):
            projection_label("Candidate-G", g_life, score("attendre", 0.0))
        f_life = {"manifest": {"experimental_policy": {
            "simulation_mode": "candidate_f"}}}
        self.assertEqual(
            projection_label("Candidate-F", f_life, score("attendre", 0.0)),
            "candidate_f")
        with self.assertRaises(ValueError):
            projection_label("P1.3", f_life, score("attendre", 0.0))
        self.assertEqual(
            projection_label("P1.3", {"manifest": {}}, score("attendre", 0.0)),
            "reference")


class FirstContactAuditCustody(unittest.TestCase):
    def _archive(self, root, *, execution=EXECUTION_SHA, tamper=False):
        cases = []
        (root / "cases.json").write_text(json.dumps(cases))
        meta = {"execution_sha": execution}
        (root / "registration.json").write_text(json.dumps(meta))
        (root / "results.json").write_text("{}")
        (root / "source.json").write_text("{}")
        (root / "TRANSPORT.json").write_text(json.dumps(
            {"execution_sha": execution, "evidence_branch": EVIDENCE_BRANCH}))
        listed = {name: sha256((root / name).read_bytes()).hexdigest()
                  for name in ("cases.json", "registration.json",
                               "results.json", "source.json")}
        if tamper:
            listed["results.json"] = "0" * 64
        (root / "SHA256.json").write_text(json.dumps(listed))

    def test_tampered_archive_digest_fails_before_any_life(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._archive(root, tamper=True)
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                next(load_archive(root))

    def test_foreign_execution_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._archive(root, execution="f" * 40)
            with self.assertRaisesRegex(ValueError, "frozen 56/57 execution"):
                next(load_archive(root))

    def test_incomplete_archive_is_not_reduced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._archive(root)
            with self.assertRaisesRegex(ValueError, "exactly 36"):
                next(load_archive(root))


if __name__ == "__main__":
    unittest.main()
