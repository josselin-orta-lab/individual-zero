"""B1 future sample-frame metadata, not future-world generation/admission."""
from copy import deepcopy
from hashlib import sha256
import inspect
import json
import unittest

from i3.lab import stage0_design as F0
from i3.lab import stage2_survival_b1_sampling as S


class B1ProspectiveAllocationDryRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = S.preview(S.PREVIEW_WITNESS)

    def test_1500_preview_metadata_is_deterministic_and_not_exposure(self):
        data = self.data
        self.assertEqual(data["schema"], S.SCHEMA)
        self.assertEqual(data["status"], S.STATUS)
        self.assertEqual(data["pair_count"], 1500)
        self.assertEqual(data["maximum_proposed_lives"], 3000)
        self.assertEqual(data["maximum_horizon_steps"], 1200000)
        self.assertEqual(data["world_instances_created"], 0)
        self.assertEqual(data["individual_lives_executed"], 0)
        self.assertFalse(data["witness_is_authorized_for_scientific_births"])
        self.assertFalse(data["worldspec_generation_permitted"])
        self.assertFalse(data["independent_iid_world_pairs_verified"])
        self.assertFalse(data["world_spec_digest_collisions_checked"])
        self.assertFalse(data["scientific_allocation_claimed"])
        self.assertEqual(data["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(data, S.preview(S.PREVIEW_WITNESS))
        self.assertEqual(len(data["proposed_units"]), 1500)
        self.assertEqual(set(data["policies_per_pair"]),
                         {"reference", "p13_replay_gate_v1"})
        S.verify_preview(data, S.PREVIEW_WITNESS)

    def test_synthetic_family_draw_is_unbiased_rule_not_forced_balance(self):
        data = self.data
        sizes = data["family_counts"]
        self.assertEqual(set(sizes), set(F0.FAMILIES))
        self.assertEqual(sum(sizes.values()), 1500)
        self.assertTrue(all(n > 0 for n in sizes.values()))
        self.assertEqual(sizes,
                         {f: sum(x["family"] == f for x in data["proposed_units"])
                          for f in F0.FAMILIES})
        self.assertEqual(data["family_rule"],
                         "HMAC_SHA256_BYTE_REJECTION_THEN_MOD3_NO_FORCED_BALANCING")

    def test_no_pseudoreplicated_world_or_genome_and_no_old_allocations(self):
        rows = self.data["proposed_units"]
        expected_names = [f"b1-{i:06d}" for i in range(1500)]
        self.assertEqual([r["pair_id"] for r in rows], expected_names)
        self.assertEqual([r["ordinal"] for r in rows], list(range(1500)))
        for key, base in (("world_seed", S.WORLD_BASE),
                          ("genome_seed", S.GENOME_BASE),
                          ("life_seed", S.LIFE_BASE)):
            vals = [row[key] for row in rows]
            self.assertEqual(len(set(vals)), 1500)
            self.assertTrue(all(base <= v < base + (1 << S.SEED_BITS)
                                for v in vals))
            self.assertTrue(all(not a <= v < b for v in vals
                                for a, b in S.OLD_SEED_RANGES))
        self.assertTrue(all(x["world_seed"] != x["genome_seed"] != x["life_seed"]
                            for x in rows))
        self.assertTrue(all(x["family"] in S.FAMILIES for x in rows))

    def test_no_reseed_on_tampered_or_duplicate_unit(self):
        for label, mutator in (
            ("edited_world", lambda d: d["proposed_units"][0].update(world_seed=17)),
            ("changed_family", lambda d: d["proposed_units"][0].update(family="stable")),
            ("duplicated_seed", lambda d: d["proposed_units"][1].update(
                world_seed=d["proposed_units"][0]["world_seed"])),
            ("deleted_unit", lambda d: d["proposed_units"].pop()),
            ("false_authorization", lambda d: d.update(
                scientific_allocation_claimed=True)),
            ("forged_digest", lambda d: d.update(allocation_sha256="0"*64)),
        ):
            data = deepcopy(self.data)
            mutator(data)
            with self.subTest(case=label), self.assertRaises(ValueError):
                S.verify_preview(data, S.PREVIEW_WITNESS)
        different_root = sha256(b"ANOTHER PUBLIC SYNTHETIC PREVIEW").hexdigest()
        with self.assertRaises(ValueError):
            S.verify_preview(self.data, different_root)

    def test_bad_or_unauthorized_witness_and_count_fail_closed(self):
        for root in (None, "", "1234", "f"*64, "0"*64, "z"*64,
                     S.PREVIEW_WITNESS.upper(), False):
            with self.subTest(root=str(root)[:10]), self.assertRaises(ValueError):
                S.preview(root)
        for count in (None, 0, -1, 10001, True, 1.4):
            with self.subTest(n=count), self.assertRaises(ValueError):
                S.preview(S.PREVIEW_WITNESS, pairs=count)

    def test_zero_world_imports_and_only_structural_cli(self):
        source = inspect.getsource(S)
        for forbidden in ("from ..runtime", "from i3.runtime",
                          "from ..modules.world", "run_life(",
                          "world_for(", "_generate_ecology("):
            self.assertNotIn(forbidden, source)
        small = S.preview(S.PREVIEW_WITNESS, pairs=6)
        small_summary = S.structural_summary(small)
        self.assertEqual(small_summary["pair_count"], 6)
        self.assertEqual(small_summary["world_instances_created"], 0)
        self.assertNotIn("proposed_units", small_summary)
        self.assertNotIn("policies_per_pair", small_summary)
        self.assertEqual(small["maximum_proposed_lives"], 12)
        self.assertEqual(small["maximum_horizon_steps"], 4800)


if __name__ == "__main__":
    unittest.main()
