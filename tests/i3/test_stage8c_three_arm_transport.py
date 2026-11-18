"""Pure Stage8-C 3-arm G/S/R tests: zero World or born native life."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import inspect
import json
import math
import unittest

from i3.lab import stage8c_three_arm_transport as C
from i3.lab import stage6_light_native_gsr_transport as S
from i3.modules.genome import digest, mutate

HEAD = "0123456789abcdef0123456789abcdef01234567"
SOURCE = "0123456789abcdef" * 4
ROOT = "0123456789abcdef" * 4
OTHER_ROOT = "fedcba9876543210" * 4


class Stage8CNativeThreeArmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = TemporaryDirectory()
        cls.path = str(Path(cls.tmp.name) / "originals")
        cls.plan = C.make_plan(ROOT, HEAD, SOURCE, cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_frozen_prospective_design_and_exact_native_budget(self):
        p = self.plan
        self.assertEqual(p["frozen_method"], C.METHOD)
        self.assertEqual(p["planned_original_lives"], 32256)
        self.assertEqual(p["planned_mutations"], 4608)
        self.assertEqual(p["planned_worlds"], 576)
        self.assertEqual(len(p["panels"]), 2)
        self.assertEqual(sum(t["planned_lives"] for t in p["panels"]), 32256)
        self.assertEqual(p["frozen_method"]["population_units"], 32)
        self.assertEqual(p["frozen_method"]["alpha_one_sided"], .025)
        self.assertEqual(p["frozen_method"]["t_critical"], 2.0395134463964077)
        self.assertEqual(p["frozen_method"]["planning_minimum_relevant_effect_steps"], 10)
        self.assertTrue(p["frozen_method"]["S_minus_M_SD_NOT_MEASURED"])
        self.assertFalse(p["scientific_admission"])
        self.assertTrue(p["science_generation_disabled"])
        self.assertEqual(C.verify_plan(p), p)
        self.assertEqual(C.make_plan(ROOT, HEAD, SOURCE, self.path), p)
        self.assertFalse(Path(self.path).exists())

    def test_192_G2_worlds_reserved_and_own_generation_holdouts(self):
        p = self.plan
        hold = p["g2_heldout_worlds_reserved"]
        self.assertEqual(len(hold), 192)
        self.assertEqual(len({(w["population"], w["family"], w["repeat"])
                              for w in hold}), 192)
        self.assertEqual(len({w["world_seed"] for w in hold}), 192)
        for i, panel in enumerate(p["panels"]):
            self.assertEqual(len(panel["worlds"]), 288)
            self.assertEqual(len(panel["founders"]), 384)
            self.assertEqual(len(panel["draws"]), 2304)
            self.assertEqual(panel["lives_per_generation"], [2304, 6912, 6912])
            self.assertEqual(set(r["arm"] for r in panel["draws"]), set(C.ARMS))
            self.assertEqual(len(panel["matched_permutations"]), 32)
            self.assertEqual(panel["scientific_admission"], False)
            for world in hold:
                if world["panel"] != i:
                    continue
                self.assertTrue(16*i <= world["population"] < 16*(i+1))
        self.assertEqual(C.S._sha(hold), p["g2_heldout_worlds_sha256"])

    def test_every_native_seed_and_perm_key_disjoint_between_two_panels(self):
        ids = set()
        perms = set()
        for p in self.plan["panels"]:
            keys = [r[k] for r in p["worlds"] for k in
                    ("world_index", "world_seed", "life_seed")]
            keys += [r["genome_seed"] for r in p["founders"]]
            keys += [r[k] for r in p["draws"]
                     for k in ("parent_draw_seed", "mutation_seed")]
            self.assertEqual(len(keys), len(set(keys)))
            self.assertTrue(ids.isdisjoint(keys))
            ids.update(keys)
            k = {r["key_hex"] for r in p["matched_permutations"]}
            self.assertEqual(len(k), 32)
            self.assertTrue(perms.isdisjoint(k))
            perms.update(k)

    def test_exact_cases_G0_then_all_three_G1_G2_no_birth(self):
        panel = self.plan["panels"][0]
        parents = S.founder_genomes(panel)
        g0 = C.generation_cases(panel, 0, parents)
        self.assertEqual(len(g0), 2304)
        self.assertEqual({r["arm"] for r in g0}, {"shared"})
        self.assertEqual(len({(r["population"], r["family"], r["repeat"])
                              for r in g0}), 96)
        fake_fitness = {(p, "shared", slot): (slot % 7, 900+slot)
                        for p in range(16) for slot in range(24)}
        kids, receipts = C.choose_three_arm_children(
            panel, 1, parents, fake_fitness, "a" * 64)
        self.assertEqual(len(kids), 16*3*24)
        self.assertEqual(len(receipts), len(kids))
        g1 = C.generation_cases(panel, 1, kids)
        self.assertEqual(len(g1), 6912)
        self.assertEqual({r["arm"] for r in g1}, set(C.ARMS))
        self.assertEqual(len({(r["population"], r["family"], r["repeat"])
                              for r in g1}), 96)
        self.assertEqual({r["source_sha256"] for r in []}, set())
        for population in range(16):
            for arm in C.ARMS:
                self.assertEqual(len([r for r in g1 if
                                      r["population"] == population
                                      and r["arm"] == arm]), 144)
        fake_fitness_g1 = {(p, arm, slot): (slot % 7, 800+slot)
                           for p in range(16) for arm in C.ARMS
                           for slot in range(24)}
        grandkids, second = C.choose_three_arm_children(
            panel, 2, kids, fake_fitness_g1, "b" * 64)
        self.assertEqual(len(grandkids), 16*3*24)
        self.assertEqual(len(second), 16*3*24)
        self.assertEqual(len(C.generation_cases(panel, 2, grandkids)), 6912)
        for rs in (receipts, second):
            for population in range(16):
                s = Counter(v["parent_slot"] for v in rs
                            if v["population"] == population and v["arm"] == "selected")
                m = Counter(v["parent_slot"] for v in rs
                            if v["population"] == population
                            and v["arm"] == "matched_multiplicity")
                self.assertEqual(sorted(s.values()), sorted(m.values()))
                self.assertEqual(len(s), len(m))
        for claim in second:
            if claim["arm"] == "matched_multiplicity":
                self.assertEqual(claim["parent_generation_arm"], "matched_multiplicity")
                parent = kids[claim["population"], "matched_multiplicity",
                              claim["parent_slot"]]
                self.assertEqual(claim["parent_genome_sha256"], digest(parent))
                child = grandkids[claim["population"], "matched_multiplicity",
                                  claim["slot"]]
                self.assertEqual(child, mutate(parent, claim["mutation_seed"], scale=.1))

    def test_malformed_and_science_admission_fail_closed(self):
        p = self.plan
        bad = deepcopy(p)
        bad["scientific_admission"] = True
        with self.assertRaises(PermissionError):
            C.verify_plan(bad)
        bad = deepcopy(p)
        bad["frozen_method"]["alpha_one_sided"] = .05
        with self.assertRaises(PermissionError):
            C.verify_plan(bad)
        bad = deepcopy(p)
        bad["panels"][0]["matched_permutations"][0]["key_hex"] = "f"*64
        with self.assertRaises(PermissionError):
            C.verify_plan(bad)
        bad = deepcopy(p)
        bad["g2_heldout_worlds_reserved"].pop()
        with self.assertRaises(PermissionError):
            C.verify_plan(bad)
        bad = deepcopy(p)
        bad["source_files_sha256"] = OTHER_ROOT
        with self.assertRaises(PermissionError):
            C.verify_plan(bad)
        bad = deepcopy(p)
        bad["schema"] = "i3-stage8b-ecology-interaction-science/v1"
        with self.assertRaises(PermissionError):
            C.verify_plan(bad)
        self.assertFalse(Path(self.path).exists())

    def test_native_offspring_rejects_missing_parents_or_fake_seal(self):
        panel = self.plan["panels"][0]
        original = S.founder_genomes(panel)
        fitness = {(p, "shared", s): (0, 1200) for p in range(16)
                   for s in range(24)}
        with self.assertRaises(ValueError):
            C.choose_three_arm_children(panel, 1, original, fitness, "not-a-sha")
        mutated = dict(original)
        mutated.pop((0, "shared", 0))
        with self.assertRaises(ValueError):
            C.choose_three_arm_children(panel, 1, mutated, fitness, "a"*64)
        with self.assertRaises(ValueError):
            C.generation_cases(panel, 2, original)

    def test_primary_is_single_cluster_student_lower_bound(self):
        self.assertEqual(C.reduce_primary_g2([float(10+i%9) for i in range(32)])["status"],
                         "STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_F0")
        result = C.reduce_primary_g2([float(-10+i%9) for i in range(32)])
        self.assertEqual(result["status"],
                         "STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_NOT_DEMONSTRATED_F0")
        self.assertEqual(result["population_units"], 32)
        self.assertEqual(result["positive_populations"], 0)
        self.assertEqual(len(result["all_population_contrasts"]), 32)
        for bad in [[1.]*31, [float("nan")]*32, [float("inf")]*32]:
            with self.assertRaises(ValueError):
                C.reduce_primary_g2(bad)
        self.assertEqual(C.reduce_primary_g2([9.0]*32)["status"],
                         "STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_NOT_DEMONSTRATED_F0")

    def test_two_rehearsals_require_distinct_source_exact_receipts(self):
        digest = lambda x: (str(x)*64)[:64]
        base = {
            "schema": C.RECEIPT_SCHEMA, "status": C.TECH_PASS,
            "workflow_run_id": 99, "source_git_head": HEAD,
            "source_files_sha256": SOURCE,
            "archive_root": "/tmp/a",
            "native_original_lives_rehashed": 32256,
            "native_mutations_reproduced": 4608,
            "phase_count": 18, "scientific_admission": False,
            "no_retry": True, "provenance": C.PROVENANCE,
            "allocation_sha256": digest("a"),
            "root_commitment_sha256": digest("b"),
            "g2_holdout_worlds_sha256": digest("c"),
            "panel_audit_sha256": digest("d"),
        }
        a = {**base, "python_version": "3.11"}
        b = {**base, "python_version": "3.12", "archive_root": "/tmp/b",
             "allocation_sha256": digest("e"),
             "root_commitment_sha256": digest("f"),
             "g2_holdout_worlds_sha256": digest("0")}
        # Distinct synthetic data must use 64-hex hashes.
        b["g2_holdout_worlds_sha256"] = digest("1")
        combined = C.combine_receipts(a, b)
        self.assertEqual(combined["native_original_lives_rehashed"], 64512)
        self.assertEqual(combined["science_lives_generated"], 0)
        for field in ("allocation_sha256", "g2_holdout_worlds_sha256",
                      "root_commitment_sha256", "archive_root"):
            broken = {**b, field:a[field]}
            with self.subTest(field=field), self.assertRaises(PermissionError):
                C.combine_receipts(a, broken)
        with self.assertRaises(PermissionError):
            C.combine_receipts(a, {**b, "native_original_lives_rehashed": 32255})
        with self.assertRaises(PermissionError):
            C.combine_receipts(a, {**b, "scientific_admission": True})

    def test_no_science_entrypoint_and_no_oracle(self):
        self.assertNotIn("run-science", inspect.getsource(C.main))
        self.assertNotIn("allocate-science", inspect.getsource(C.main))
        self.assertNotIn("run_life", inspect.getsource(C.make_plan))
        self.assertNotIn("world_for_stage6", inspect.getsource(C.make_plan))
        self.assertNotIn("score", inspect.signature(C.generation_cases).parameters)
        self.assertFalse(Path(self.path).exists())


if __name__ == "__main__":
    unittest.main()
