"""Synthetic B1 WorldSpec generation only, never run a scientific life."""
from copy import deepcopy
from dataclasses import replace
import inspect
import unittest

from i3.lab import p2_ecologies as P2
from i3.lab import stage2_survival_b1_sampling as B1
from i3.lab import stage2_survival_b1_worldspec_audit as A
from i3.lab.worldgen import generate


class B1ProspectiveWorldSpecDryRun(unittest.TestCase):
    def test_adapter_preserves_frozen_p2_snapshot_on_legacy_safe_seeds(self):
        # Compare the *whole initial spec* at original non-reserve seeds;
        # no historical life is run or converted to prospective evidence.
        for cohort in ("development", "selection", "validation"):
            for index in (0, 1):
                seed = P2.COHORTS[cohort][index]
                for family in P2.FAMILIES:
                    with self.subTest(cohort=cohort, index=index, family=family):
                        expected = P2.world_for(family, cohort, index)
                        proposed = A._construct_f0_spec(family, seed)
                        self.assertEqual(P2.fingerprint(proposed),
                                         P2.fingerprint(expected))
                        self.assertEqual(A._snapshot_digests(proposed),
                                         A._snapshot_digests(expected))

    def test_high_seed_guard_is_preserved_but_candidate_adapter_is_structural(self):
        rows = B1.preview(B1.PREVIEW_WITNESS, pairs=3)["proposed_units"]
        for family, row in zip(P2.FAMILIES, rows):
            seed = row["world_seed"]
            with self.subTest(family=family):
                with self.assertRaises(ValueError):
                    generate("dev" if family != "depletion" else "R", seed)
                # Intentional non-development path; still no stepping/life.
                spec = A._construct_f0_spec(family, seed)
                P2.validate_ecology(spec, family)
                self.assertTrue(spec.name.startswith("p2-"+family+"-"))
        for family, seed in ((None, B1.WORLD_BASE),
                             ("unknown", B1.WORLD_BASE),
                             ("stable", False), ("stable", -1)):
            with self.subTest(family=family, seed=seed), self.assertRaises(ValueError):
                A._construct_f0_spec(family, seed)

    def test_structural_digest_ignores_name_not_real_resources(self):
        spec = A._construct_f0_spec("stable", B1.WORLD_BASE + 123)
        renamed = replace(spec, name="different-seed-bearing-display-name")
        full, unnamed = A._snapshot_digests(spec)
        renamed_full, renamed_unnamed = A._snapshot_digests(renamed)
        self.assertNotEqual(full, renamed_full)
        self.assertEqual(unnamed, renamed_unnamed)
        with self.assertRaisesRegex(ValueError, "duplicate ecological structure"):
            seen = {unnamed: "b1-000000"}
            A._reject_spec_collision(seen, renamed_unnamed, "b1-000001")
        with self.assertRaises(ValueError):
            A._reject_spec_collision({full: "b1-000000"},
                                      full, "b1-000002")

    def test_all_1500_synthetic_worldspecs_audited_without_lives(self):
        outcome = A.audit_synthetic_preview()
        self.assertEqual(outcome["schema"], A.SCHEMA)
        self.assertEqual(outcome["status"], A.STATUS)
        self.assertEqual(outcome["worldspec_structures_generated"], 1500)
        self.assertEqual(outcome["structural_world_validations"], 1500)
        self.assertEqual(outcome["unique_full_worldspec_digests"], 1500)
        self.assertEqual(outcome["unique_name_independent_worldspec_digests"], 1500)
        self.assertEqual(sum(outcome["ecological_families"].values()), 1500)
        self.assertEqual(outcome["worlds_stepped"], 0)
        self.assertEqual(outcome["scientific_lives_executed"], 0)
        self.assertEqual(outcome["originals_written"], 0)
        self.assertEqual(outcome["scientific_verdict"], "NOT_ISSUED")
        self.assertFalse(outcome["independent_world_sampling_verified"])
        self.assertFalse(outcome["external_witness_and_owner_admission"])
        self.assertFalse(outcome["scientific_margin_approved"])
        self.assertEqual(len(outcome["aggregate_worldspec_digest_sha256"]), 64)
        self.assertEqual(
            outcome["public_synthetic_allocation_sha256"],
            B1.preview(B1.PREVIEW_WITNESS)["allocation_sha256"])
        self.assertEqual(outcome, A.audit_synthetic_preview())

    def test_tampered_allocation_cannot_be_disguised_as_real_worlds(self):
        wrong = B1.preview(B1.PREVIEW_WITNESS)
        wrong["proposed_units"][0]["world_seed"] += 1
        with self.assertRaisesRegex(ValueError, "preview"):
            A.audit_synthetic_preview(wrong)
        wrong = B1.preview(B1.PREVIEW_WITNESS)
        wrong["witness_is_external_signed_source"] = True
        with self.assertRaises(ValueError):
            A.audit_synthetic_preview(wrong)
        wrong = B1.preview(B1.PREVIEW_WITNESS, pairs=6)
        with self.assertRaises(ValueError):
            A.audit_synthetic_preview(wrong)

    def test_adapter_has_no_scientific_runner_or_mutable_world_state(self):
        source = inspect.getsource(A)
        for forbidden in ("run_life(", "World.step(", "World.capture(",
                          "generation_zero(", "P2.world_for(", "scientific_admit("):
            self.assertNotIn(forbidden, source)
        self.assertNotIn("run_life", A.audit_synthetic_preview.__code__.co_names)
        self.assertFalse(any("run" in key.lower()
                             for key in A.audit_synthetic_preview().__iter__()
                             if key not in ("worlds_stepped",)))


if __name__ == "__main__":
    unittest.main()
