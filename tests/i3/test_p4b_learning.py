"""P4b software and nonexposure checks. NO validation study world opened."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p2_ecologies, p4a_validation, p4b_schedule, p4b_validation
from i3.modules.genome import generation_zero
from i3.runtime.life import run_life


class P4bPaidLearningTests(unittest.TestCase):
    def test_fresh_worlds_never_overlap_p4a_or_p4_reserve(self):
        m = p4b_schedule.manifest()
        self.assertEqual(m, p4b_schedule.manifest())
        self.assertEqual(m["total_lives"], 576)
        self.assertEqual(len(m["allocation"]), 24)
        self.assertEqual(set(x["index"] for x in m["allocation"]), set(range(24, 48)))
        self.assertTrue(all(x["world_seed"] in p2_ecologies.COHORTS["validation"]
                            for x in m["allocation"]))
        self.assertTrue(all(x["life_seed"] >= 260024 for x in m["allocation"]))
        self.assertEqual(m["modes"], ["normal", "shadow_discard"])

    def test_preflight_reads_genomes_without_opening_study_worlds(self):
        with patch.object(p2_ecologies, "world_for",
                          side_effect=AssertionError("no P4b world")):
            frozen = p4a_validation.verify_frozen_genomes()
            self.assertEqual(len(frozen), 48)
            self.assertEqual(len(p4b_schedule.manifest()["allocation"]), 24)

    def test_launch_denied_without_exact_source_locks(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(p2_ecologies, "world_for",
                              side_effect=AssertionError("world opened prematurely")):
                with self.assertRaises(RuntimeError):
                    p4b_validation.run()

    def test_paid_shadow_learning_is_computed_but_not_retained(self):
        # Explicitly DEVELOPMENT-only world, never any validation/reserve use.
        spec = p2_ecologies.world_for("stable", "development", 12)
        genome = generation_zero(6000)
        normal = run_life(genome, spec, 100, 80, learning_mode="normal",
                          observer_mind_digest=True, keep_trace=True)
        shadow = run_life(genome, spec, 100, 80, learning_mode="shadow_discard",
                          observer_mind_digest=True, keep_trace=True)
        self.assertGreater(normal["retained_outcome_learning_updates"], 0)
        self.assertEqual(normal["shadow_discarded_outcome_updates"], 0)
        self.assertEqual(shadow["retained_outcome_learning_updates"], 0)
        self.assertGreater(shadow["shadow_discarded_outcome_updates"], 0)
        self.assertNotEqual(normal["outcome_model_sha256"],
                            shadow["outcome_model_sha256"])
        self.assertTrue(shadow["spatial_beliefs_sha256"])
        self.assertEqual(normal["manifest"]["world_sha256"],
                         shadow["manifest"]["world_sha256"])
        for out in (normal, shadow):
            self.assertEqual(out["cognitive_accounting"]["shortfall_steps"], 0)
            self.assertEqual(out["cognitive_accounting"]["pending_replays"], 0)
            self.assertTrue(all(
                row["funding_phases"]["learning"]["accounting"][ch]["unpaid"] == 0
                for row in out["trace"] for ch in ("energy", "vigilance")))
            self.assertTrue(all(
                not row["dead"] or
                not any(row["funding_phases"]["learning"]["work"].values())
                for row in out["trace"]))
        self.assertEqual(len(shadow["observer_internal_position"]), 2)

    def test_default_runtime_unchanged_when_no_intervention(self):
        spec = p2_ecologies.world_for("stable", "development", 13)
        genome = generation_zero(6001)
        base = run_life(genome, spec, 99, 25)
        control = run_life(genome, spec, 99, 25, learning_mode="normal")
        for key in ("evidence_head", "trace_head", "terminal", "steps_lived",
                    "actions", "final_body", "cognitive_accounting"):
            self.assertEqual(base[key], control[key])
        self.assertNotIn("outcome_model_sha256", base)
        self.assertNotIn("learning_intervention", base)

    def test_invalid_intervention_fails_before_birth(self):
        spec = p2_ecologies.world_for("stable", "development", 14)
        with self.assertRaises(ValueError):
            run_life(generation_zero(10), spec, 2, 10, learning_mode="free_cognition")

    def test_same_genome_same_experience_is_reproducible(self):
        spec = p2_ecologies.world_for("depletion", "development", 15)
        genome = generation_zero(9)
        one = run_life(genome, spec, 101, 70, observer_mind_digest=True)
        two = run_life(genome, spec, 101, 70, observer_mind_digest=True)
        for key in ("outcome_model_sha256", "spatial_beliefs_sha256",
                    "evidence_head", "steps_lived"):
            self.assertEqual(one[key], two[key])


if __name__ == "__main__":
    unittest.main()
