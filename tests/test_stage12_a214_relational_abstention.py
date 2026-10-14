"""A2.14 offline-only: empirical collisions must never become confident safety labels."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_a214 import (
    SEEDS,FAMILIES,TRANSLATED,HIDDEN,VISIBLE,
    positions_for,run_pair,ConflictAbstainingLookup,
)
from lab.stage11_reference_fixture import build_stage11_reference_runtime


class TranslationAndAbstentionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=build_stage11_reference_runtime().world.config

    def test_all_preregistered_families_seed61(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                row=run_pair(self.base,family,61)
                self.assertFalse(row["full_key_covered"])
                if family in TRANSLATED:
                    self.assertTrue(row["naive_correct"])
                    self.assertTrue(row["conflict_model_correct"])
                elif family in HIDDEN:
                    self.assertFalse(row["naive_correct"])
                    self.assertFalse(row["conflict_model_predicted"])
                    self.assertTrue(row["hidden_conflict_observed_prenatally"])
                else:
                    self.assertFalse(row["naive_predicted"])
                    self.assertFalse(row["conflict_model_predicted"])

    def test_heldout_seeds_have_nontrivial_translations(self):
        for family in FAMILIES:
            for seed in SEEDS:
                p,q,_,_=positions_for(seed,family)
                self.assertNotEqual(p,q)
                self.assertTrue(1<=p.x<31 and 1<=q.x<31)

    def test_unknown_and_contradictory_observations_abstain(self):
        lookup=ConflictAbstainingLookup()
        row={"relational_key":"k","outcome_hash":"a"}
        self.assertIsNone(lookup.predict(row))
        lookup.observe(row)
        self.assertEqual(lookup.predict(row),"a")
        lookup.observe({"relational_key":"k","outcome_hash":"b"})
        self.assertIsNone(lookup.predict(row))
        self.assertIsNone(lookup.predict(
            {"relational_key":"never-trained"}))

if __name__=="__main__":
    unittest.main()
