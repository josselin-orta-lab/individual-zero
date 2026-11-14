"""Adversarial toy G/S parent selection to native genome-v4 ancestry chain.

No Worlds, births, original data or actual prospective seeds are involved.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import random
import runpy
import unittest
from unittest.mock import patch

from i3.lab import stage6_light_selection_parent_preflight as v
fake_lineage = runpy.run_path(str(Path(__file__).with_name(
    "test_stage6_light_genome_lineage_preflight.py")))["fake_lineage"]


def fixture(populations=(0,)):
    founders, offspring, genotype_index = fake_lineage(populations)
    persist = []
    for p in populations:
        for g in (0, 1):
            for arm in (("shared",) if g == 0 else v.ARMS):
                for slot in range(24):
                    for f in v.FAMILIES:
                        for repeat in (0, 1):
                            # Constructed scores, not observed biology.
                            steps = 400 if slot % 7 == 0 else 60 + (slot * 11) % 310
                            persist.append({"kind": v.KIND, "population": p,
                                            "generation": g, "arm": arm, "slot": slot,
                                            "family": f, "repeat": repeat,
                                            "censored": steps == 400, "steps_lived": steps})
    source = {}
    for row in persist:
        source.setdefault((row["population"], row["generation"], row["arm"], row["slot"]), []).append(row)
    genodigests = {(row["population"], row["generation"], row["arm"], row["slot"]): row["genome_sha256"] for row in genotype_index}
    draws = []
    # Original fake_lineage deliberately uses fixed parent slots; search mock
    # RNG seeds only in test fixtures, NEVER in an execution allocation.
    for child in offspring:
        p, g, arm, slot, parent_slot = (child[k] for k in
                                      ("population", "generation", "arm", "slot", "parent_slot"))
        prev_arm = "shared" if g == 1 else arm
        prev = [source[(p, g-1, prev_arm, s)] for s in range(24)]
        ranked = sorted(range(24), key=lambda s: (
            -sum(x["censored"] for x in prev[s]),
            -sum(x["steps_lived"] for x in prev[s]), s))
        # Distinct fake-only integer draw seeds, search deterministic candidates
        # to match the deliberately arbitrary fixture parent choice.
        seed = 2_000_000 + p * 1_000_000 + g * 100_000 + (0 if arm == "selected" else 30_000) + slot*1000
        while True:
            rng = random.Random(seed)
            drawn = (rng.choices(ranked, weights=range(24, 0, -1), k=1)[0]
                     if arm == "selected" else rng.randrange(24))
            if drawn == parent_slot:
                break
            seed += 1
        draws.append({"kind": v.KIND, "population": p,
                      "generation": g, "arm": arm, "slot": slot,
                      "parent_slot": parent_slot, "draw_seed": seed,
                      "parent_genome_sha256": genodigests[p, g-1, prev_arm, parent_slot],
                      "genome_sha256": genodigests[p, g, arm, slot]})
    return founders, offspring, genotype_index, persist, draws


class Stage6ParentChoiceOfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.small = fixture()

    def audit(self, sample=None):
        f, d, n, p, r = deepcopy(self.small if sample is None else sample)
        return v.inspect_mock_parent_selection(f, d, n, p, r, fixture_populations=(0,))

    def test_full_toy_selection_and_ancestry_shape(self):
        result = v.inspect_mock_parent_selection(*fixture(tuple(range(16))))
        self.assertEqual(result["status"], "TOY_PARENT_SELECTION_LINEAGE_MATCH_NOT_ADMITTED")
        self.assertEqual(result["checked_persistence_receipts"], 6912)
        self.assertEqual(result["checked_draws"], 1536)
        self.assertEqual(result["checked_mutations"], 1536)
        self.assertEqual(result["new_worlds_opened"], 0)
        self.assertFalse(result["parent_draw_seeds_independently_committed"])
        self.assertFalse(result["original_biological_lives_verified"])

    def test_partial_fixture_cannot_become_full_panel(self):
        r = self.audit()
        self.assertEqual(r["status"], "PARTIAL_TOY_PARENT_SELECTION_LINEAGE_MATCH_NOT_ADMITTED")
        with self.assertRaises(ValueError):
            v.inspect_mock_parent_selection(*self.small)

    def test_weighted_selected_parent_tamper_rejected(self):
        f, d, n, p, draws = deepcopy(self.small)
        row = next(x for x in draws if x["arm"] == "selected")
        row["parent_slot"] = (row["parent_slot"] + 1) % 24
        with self.assertRaises(ValueError):
            self.audit((f, d, n, p, draws))

    def test_uniform_parent_seed_tamper_rejected(self):
        f, d, n, p, draws = deepcopy(self.small)
        row = next(x for x in draws if x["arm"] == "random_parent")
        # Force a different RNG outcome without modifying the parent slot.
        alt = row["draw_seed"] + 1
        while random.Random(alt).randrange(24) == row["parent_slot"]:
            alt += 1
        row["draw_seed"] = alt
        with self.assertRaises(ValueError):
            self.audit((f, d, n, p, draws))

    def test_fake_parent_selection_cannot_masquerade_as_another_genome(self):
        f, d, n, p, draws = deepcopy(self.small)
        draws[0]["genome_sha256"] = "0"*64
        with self.assertRaises(ValueError):
            self.audit((f, d, n, p, draws))

    def test_missing_duplicate_or_invalid_persistence_rejected(self):
        for action in (lambda x: x.pop(), lambda x: x.append(deepcopy(x[0])),
                       lambda x: x[0].update({"censored": True, "steps_lived": 399}),
                       lambda x: x[0].update({"hidden_world": 2})):
            f, d, n, p, draws = deepcopy(self.small)
            action(p)
            with self.subTest(action=str(action)), self.assertRaises(ValueError):
                self.audit((f, d, n, p, draws))

    def test_boolean_population_identifiers_not_admitted(self):
        sample = deepcopy(self.small)
        sample[3][0]["population"] = False
        with self.assertRaises(ValueError):
            self.audit(sample)
        sample = deepcopy(self.small)
        sample[4][0]["population"] = False
        with self.assertRaises(ValueError):
            self.audit(sample)

    def test_parent_mutation_chain_tamper_rejected(self):
        f, d, n, p, draws = deepcopy(self.small)
        d[0]["parent_slot"] = (d[0]["parent_slot"] + 1) % 24
        with self.assertRaises(ValueError):
            self.audit((f, d, n, p, draws))

    def test_no_cross_arm_or_duplicate_draw_seeds(self):
        f, d, n, p, draws = deepcopy(self.small)
        draws[1]["draw_seed"] = draws[0]["draw_seed"]
        with self.assertRaises(ValueError):
            self.audit((f, d, n, p, draws))

    def test_permission_denial_and_no_execution_endpoints(self):
        with patch.object(v.ancestry.custody, "_assert_inert", side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                self.audit()
        for fn in (v.run_life, v.authorize_science):
            with self.assertRaises(PermissionError):
                fn()


if __name__ == "__main__":
    unittest.main()
