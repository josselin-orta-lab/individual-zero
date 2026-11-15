"""Stage6 full native G/S/R engineering transport: pure, NO native lives.

Test roots and persistence are invented. These tests do not open a World or
admit a scientific study. Full 11,520-life engineering runs remain separate.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from i3.lab import stage6_light_native_gsr_transport as E
from i3.modules.genome import generation_zero, midpoint, validate

ROOT = "f5b19af3254e2eaaf8459ac7977f58a423dcacfeac141f7973705abcb354d012"
HEAD = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
SOURCE = "5a56a9e52d4d2909bf2dfa64a4ec0066e0b3e814da25fd4df70ee56cc180edbf"


class CountRead(dict):
    def __init__(self, d):
        super().__init__(d)
        self.count = 0

    def __getitem__(self, k):
        self.count += 1
        return super().__getitem__(k)


class Stage6FullEngineeringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.archive = str(Path(cls.tmp.name) / "full-originals")
        cls.plan = E.make_plan(ROOT, HEAD, SOURCE, cls.archive)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_exact_fixed_pre_exposure_contract_and_count(self):
        p = self.plan
        self.assertEqual(p["status"], "FULL_ENGINEERING_ALLOCATED_NOT_EXPOSED")
        self.assertEqual(p["planned_worlds"], 288)
        self.assertEqual(p["planned_lives"], 11520)
        self.assertEqual(p["lives_per_generation"], [2304, 4608, 4608])
        self.assertEqual(len(p["worlds"]), 288)
        self.assertEqual(len(p["founders"]), 384)
        self.assertEqual(len(p["draws"]), 1536)
        self.assertEqual(p["phases"], list(E.PHASES))
        self.assertFalse(p["scientific_admission"])
        self.assertEqual(E.verify_plan(p), p)
        self.assertEqual(E.make_plan(ROOT, HEAD, SOURCE, self.archive), p)
        all_seeds = [w[k] for w in p["worlds"]
                     for k in ("world_index", "world_seed", "life_seed")]
        all_seeds += [f["genome_seed"] for f in p["founders"]]
        all_seeds += [d[k] for d in p["draws"]
                      for k in ("parent_draw_seed", "mutation_seed")]
        self.assertEqual(len(all_seeds), len(set(all_seeds)))
        self.assertEqual(p["worlds"][0]["logical_world"], 0)
        self.assertEqual(p["worlds"][-1]["logical_world"], 287)

    def test_g0_shared_once_and_all_six_opportunities(self):
        founders = E.founder_genomes(self.plan)
        self.assertEqual(len(founders), 384)
        cases = E.generation_cases(self.plan, 0, founders)
        self.assertEqual(len(cases), 2304)
        self.assertEqual({x["arm"] for x in cases}, {"shared"})
        self.assertEqual(len({(r["population"], r["slot"], r["family"], r["repeat"])
                              for r in cases}), 2304)
        self.assertEqual(len({(r["population"], r["family"], r["repeat"])
                              for r in cases}), 96)
        with self.assertRaises(ValueError):
            E.generation_cases(self.plan, 1, founders)
        with self.assertRaises(ValueError):
            E.generation_cases(self.plan, 3, founders)

    def test_score_blind_random_parent_selection_and_ancestry(self):
        prior = E.founder_genomes(self.plan)
        persistence = CountRead({
            k: (6 if k[-1] == 0 else 0, 2400 if k[-1] == 0 else 6)
            for k in prior
        })
        children, draws = E.choose_descendants(self.plan, 1, prior, persistence)
        self.assertEqual(len(children), 16*2*24)
        self.assertEqual(len(draws), 16*2*24)
        # Selected arm reads each of 24 parent fitness tuples once per pop.
        # Uniform random arm never dereferences any fitness value.
        self.assertEqual(persistence.count, 16*24)
        self.assertEqual(len({(d["population"], d["arm"], d["slot"]) for d in draws}), 768)
        self.assertEqual({d["generation"] for d in draws}, {1})
        for d in draws:
            self.assertLess(d["parent_slot"], 24)
            validate(children[d["population"], d["arm"], d["slot"]])
        children2, draws2 = E.choose_descendants(
            self.plan, 1, prior,
            {k: (6 if k[-1] == 0 else 0, 2400 if k[-1] == 0 else 6)
             for k in prior})
        self.assertEqual(children, children2)
        self.assertEqual(draws, draws2)
        one = E.generation_cases(self.plan, 1, children)
        self.assertEqual(len(one), 4608)
        self.assertEqual({c["arm"] for c in one}, set(E.ARMS))
        second_scores = {(p, arm, slot): (slot % 6, 100 + slot)
                         for p in range(16) for arm in E.ARMS for slot in range(24)}
        grandchildren, g2_draws = E.choose_descendants(self.plan, 2, children,
                                                       second_scores)
        self.assertEqual(len(g2_draws), 768)
        self.assertEqual(len(E.generation_cases(self.plan, 2, grandchildren)), 4608)
        self.assertEqual(len(grandchildren), 768)

    def test_final_primary_sign_and_two_sentinel_invalidations(self):
        base = midpoint()
        genomes = {}
        for p in range(16):
            for arm in E.ARMS:
                for s in range(24):
                    genes = deepcopy(base)
                    genes["genes"]["beta_u"] = 1.5 if arm == "selected" else .5
                    genomes[p, arm, s] = validate(genes)
        positive = E.final_contrasts(genomes)
        self.assertEqual(positive["contrast"]["beta_u_eff"]["plus"], 16)
        self.assertEqual(positive["status"], "STAGE6_LIGHT_SIGN_CONCORDANCE_PASS")
        self.assertFalse(positive["invalid_neutral_markers"])
        for p in range(8):
            for s in range(24):
                genomes[p, "selected", s], genomes[p, "random_parent", s] = (
                    genomes[p, "random_parent", s], genomes[p, "selected", s])
        mixed = E.final_contrasts(genomes)
        self.assertEqual(mixed["contrast"]["beta_u_eff"]["plus"], 8)
        self.assertEqual(mixed["contrast"]["beta_u_eff"]["minus"], 8)
        self.assertEqual(mixed["status"], "STAGE6_LIGHT_NO_SIGN_CONCORDANCE")
        for p in range(16):
            for s in range(24):
                g = genomes[p, "selected", s]
                g["genes"]["omega"] = .5
                g["genes"]["temperament.affiliation"] = .5
                genomes[p, "random_parent", s]["genes"]["omega"] = -.5
                genomes[p, "random_parent", s]["genes"]["temperament.affiliation"] = -.5
        invalid = E.final_contrasts(genomes)
        self.assertTrue(invalid["invalid_neutral_markers"])
        self.assertEqual(invalid["status"], "STAGE6_LIGHT_INVALID")
        with self.assertRaises(ValueError):
            E.final_contrasts({k:v for k,v in genomes.items() if k != (0, "selected", 0)})

    def test_immutable_path_and_permission_not_claimed(self):
        altered = deepcopy(self.plan)
        for k, v in (("status", "ADMITTED"), ("scientific_admission", True),
                     ("planned_lives", 100), ("allocation_sha256", "0"*64),
                     ("archive_root", self.archive+"-retry")):
            candidate = deepcopy(altered)
            candidate[k] = v
            with self.subTest(key=k), self.assertRaises(PermissionError):
                E.verify_plan(candidate)
        with self.assertRaises(PermissionError):
            E.run_full(self.plan, self.archive+"-retry", self.plan["allocation_sha256"])
        with self.assertRaises(PermissionError):
            E.run_full(self.plan, self.archive, "0"*64)
        self.assertFalse(Path(self.archive).exists())

    def test_claim_precedes_any_life_and_is_irreversible(self):
        with patch.object(E.G0, "_verify_checkout", side_effect=PermissionError("dirty")):
            with self.assertRaises(PermissionError):
                E.run_full(self.plan, self.archive, self.plan["allocation_sha256"])
        self.assertFalse(Path(self.archive).exists())


if __name__ == "__main__":
    unittest.main()
