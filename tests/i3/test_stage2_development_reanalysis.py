"""Read-only historical 80/81 analysis. No World/Mind or runner invocation."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from i3.lab import stage2_development_reanalysis as A


def frozen_rows():
    return json.loads((A.STUDY_DIR / "evidence" / "SCIENTIFIC_RESULT.json").read_bytes())["rows"]


class ArchivedPilotScientificReanalysis(unittest.TestCase):
    def test_all_36_sealed_originals_and_reductions_match(self):
        out = A.analyze_sealed_archive()
        self.assertEqual(out["schema"], A.SCHEMA)
        self.assertEqual(out["status"], A.STATUS)
        self.assertEqual(out["archive_gzip_sha256_verified_this_pass"], 36)
        self.assertEqual(out["originals_vs_frozen_reductions_matched"], 36)
        self.assertEqual(out["paired_blocks"], 12)
        self.assertEqual(out["historical_reduced_lives"], 36)
        self.assertEqual(out["source_pin_consistency"],
                         "MATCHES_PUBLISHED_HISTORICAL_PINS")
        self.assertEqual(out["external_pre_exposure_authority"],
                         "NOT_INDEPENDENTLY_REATTESTED")
        self.assertEqual(out["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(out["new_worlds_opened"], 0)
        self.assertEqual(out["new_scientific_lives"], 0)
        self.assertTrue(out["no_survival_noninferiority_gate"])

    def test_survival_and_physical_cost_per_assigned_life(self):
        out = A.analyze_reduced_rows(frozen_rows())
        all_ = out["overall"]
        self.assertAlmostEqual(all_["gate_minus_fixed_mean_lived_steps"], -29.4166666667)
        self.assertEqual(all_["gate_minus_fixed_worst_lived_steps"], -300)
        self.assertEqual(all_["gate_minus_fixed_best_lived_steps"], 136)
        self.assertEqual(all_["gate_longer_shorter_equal"],
                         {"longer": 3, "shorter": 3, "equal": 6})
        self.assertEqual(all_["survival_at_400"],
                         {A.FIXED: 4, A.GATE: 3, A.ZERO: 2})
        self.assertEqual(all_["fixed_only_survived"], 2)
        self.assertEqual(all_["gate_only_survived"], 1)
        self.assertEqual(all_["gate_shorter_and_lower_paid_energy"], 3)
        energy = all_["mean_paid_cognitive_energy_per_assigned_life"]
        vigilance = all_["mean_paid_cognitive_vigilance_per_assigned_life"]
        self.assertAlmostEqual(energy[A.FIXED], 162.09043333333)
        self.assertAlmostEqual(energy[A.GATE], 123.06116666667)
        self.assertAlmostEqual(vigilance[A.FIXED], 196.61633333333)
        self.assertAlmostEqual(vigilance[A.GATE], 157.15533333333)
        self.assertAlmostEqual(all_["gate_minus_fixed_energy_paid_per_assigned_life"],
                               -39.02926666666)
        self.assertAlmostEqual(all_["replays_per_reached_sleep_step"][A.GATE],
                               5532 / 867)

    def test_family_heterogeneity_and_single_block_sensitivity(self):
        out = A.analyze_reduced_rows(frozen_rows())
        family = out["by_family"]
        self.assertAlmostEqual(family["stable"]["gate_minus_fixed_mean_lived_steps"], -70.5)
        self.assertAlmostEqual(family["depletion"]["gate_minus_fixed_mean_lived_steps"], -31.25)
        self.assertAlmostEqual(family["pulse"]["gate_minus_fixed_mean_lived_steps"], 13.5)
        self.assertEqual(family["stable"]["fixed_only_survived"], 1)
        self.assertEqual(family["depletion"]["fixed_only_survived"], 1)
        self.assertEqual(family["pulse"]["gate_only_survived"], 1)
        self.assertEqual({x["matched_blocks"] for x in family.values()}, {4})
        sensitivity = out["sensitivity_not_inference"]
        self.assertAlmostEqual(sensitivity["leave_one_block_out_mean_lived_steps_min"],
                               -44.454545454545)
        self.assertAlmostEqual(sensitivity["leave_one_block_out_mean_lived_steps_max"],
                               -4.8181818181818)
        self.assertEqual(sensitivity["leave_one_family_out_mean_lived_steps"],
                         {"stable": -8.875, "depletion": -28.5, "pulse": -50.875})
        self.assertEqual(out["causal_replay_selection_effect"], "NOT_IDENTIFIED")

    def test_death_at_horizon_is_not_a_survivor(self):
        data = frozen_rows()
        idx = next(i for i, r in enumerate(data)
                   if r["policy"] == A.GATE and r["terminal"] == "censored")
        data[idx] = dict(data[idx], terminal="dead",
                         death_causes=["synthetic_test_only"])
        out = A.analyze_reduced_rows(data)
        self.assertEqual(out["overall"]["survival_at_400"][A.GATE], 2)
        self.assertEqual(out["overall"]["gate_minus_fixed_mean_lived_steps"],
                         -29.416666666666668)

    def test_incomplete_or_forged_reduced_rows_fail_closed(self):
        source = frozen_rows()
        for name in ("missing", "duplicate", "bad_family", "bad_life",
                     "false_censoring", "negative_paid", "nan_paid",
                     "bad_replay_count", "bool_step"):
            data = deepcopy(source)
            if name == "missing":
                data.pop()
            elif name == "duplicate":
                data[1] = data[0]
            elif name == "bad_family":
                data[0]["family"] = "unseen_ecology"
            elif name == "bad_life":
                data[0]["steps_lived"] = 0
            elif name == "false_censoring":
                data[0]["terminal"] = "censored"
            elif name == "negative_paid":
                data[0]["energy_per_step"] = -1.0
            elif name == "nan_paid":
                data[0]["vigilance_per_step"] = float("nan")
            elif name == "bad_replay_count":
                data[0]["replays"] = 999999
            elif name == "bool_step":
                data[0]["steps_lived"] = True
            with self.subTest(name=name), self.assertRaises(ValueError):
                A.analyze_reduced_rows(data)

    def test_frozen_original_tampering_is_detected_no_regeneration(self):
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "study"
            shutil.copytree(A.STUDY_DIR, copy)
            original = copy / "evidence" / "life-000.json.gz"
            original.write_bytes(b"tampered archived original")
            with self.assertRaisesRegex(ValueError, "original digest mismatch"):
                A.analyze_sealed_archive(copy)

    def test_historical_source_lock_change_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "study"
            shutil.copytree(A.STUDY_DIR, copy)
            lock_file = copy / "evidence" / "SOURCE_LOCK.json"
            lock = json.loads(lock_file.read_bytes())
            lock["source_sha"] = "0" * 40
            lock_file.write_text(json.dumps(lock))
            with self.assertRaisesRegex(ValueError, "source/custody pin mismatch"):
                A.analyze_sealed_archive(copy)


if __name__ == "__main__":
    unittest.main()
