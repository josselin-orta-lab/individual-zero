"""P4a preregistration controls: NO held-out world is instantiated by tests."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i3.lab import p4a_schedule, p4a_validation, p2_ecologies, p3_schedule


class P4aRegistrationTests(unittest.TestCase):
    def test_disjoint_unopened_heldout_schedule(self):
        schedule = p4a_schedule.schedule_manifest()
        self.assertEqual(schedule, p4a_schedule.schedule_manifest())
        self.assertEqual(schedule["total_lives"], 288)
        self.assertEqual(len(schedule["allocation"]), 24)
        self.assertEqual(schedule["horizon"], 400)
        self.assertEqual(set(x["cohort"] for x in schedule["allocation"]), {"validation"})
        self.assertEqual(len(set((x["family"], x["world_seed"])
                                 for x in schedule["allocation"])), 24)
        self.assertTrue(all(x["world_seed"] in p2_ecologies.COHORTS["validation"]
                            for x in schedule["allocation"]))
        self.assertTrue(all(x["life_seed"] >= 160000 for x in schedule["allocation"]))
        self.assertEqual(schedule["allocation_policy"],
                         "all_48_previously_frozen_genomes_no_selection_or_mutation")

    def test_all_original_48_genotypes_verified_without_worlds(self):
        with patch.object(p2_ecologies, "world_for",
                          side_effect=AssertionError("forbidden to open worlds")):
            genotypes = p4a_validation.verify_frozen_genomes()
        self.assertEqual(len(genotypes), 48)
        self.assertEqual({key[1] for key in genotypes}, set(p3_schedule.ARMS))

    def test_tampered_genome_rejected_before_simulation(self):
        path = p4a_validation.G2_PATH
        orig = path.read_bytes()
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as folder:
            corrupted = Path(folder) / "altered.json"
            data = json.loads(orig)
            data["genomes"][0]["genome"]["genes"]["alpha"] = 0.015
            corrupted.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                p4a_validation.verify_frozen_genomes(corrupted)

    def test_run_denied_without_all_prospective_locks(self):
        with patch.object(p2_ecologies, "world_for",
                          side_effect=AssertionError("forbidden cohort access")):
            with self.assertRaises(RuntimeError):
                p4a_validation.run()

    def test_summary_is_population_level_not_pseudoreplicated(self):
        fake = {"total_lives": 288, "schedule_sha256": "f"*64,
                "source_sha": "e"*40, "sha256": "d"*64,
                "status": "P4A_VALIDATION_ONLY_P4B_AND_RESERVE_NOT_RUN",
                "lives": []}
        for p in range(4):
            for arm in p4a_schedule.ARMS:
                for i in range(36):
                    fake["lives"].append({
                        "population": p, "arm": arm, "censored": i < 10,
                        "steps_lived": 400 if i < 10 else 50,
                        "paid_energy": 4.0, "paid_vigilance": 7.0,
                        "inactive_steps": 2})
        summary = p4a_validation.summarize(fake)
        self.assertEqual(len(summary["population_results"]), 4)
        self.assertTrue(all(x["selected_minus_random_survivors"] == 0
                            for x in summary["population_results"]))


if __name__ == "__main__":
    unittest.main()
