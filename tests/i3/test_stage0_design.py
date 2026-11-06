"""Stage-0 metadata/arithmetic checks. No new scientific or validation lives."""
from copy import deepcopy
from hashlib import sha1
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i3.lab import stage0_design as design


def complete_selection(population=0):
    """Synthetic scalar receipts, never output from an executed individual."""
    return [dict(candidate_seed=design.founder_seed(population, slot),
                 world_index=row["index"], terminal="dead", steps_lived=100)
            for slot in range(design.CANDIDATES)
            for row in design.world_rows("selection") if row["population"] == population]


class Stage0DesignTests(unittest.TestCase):
    def test_manifest_is_stable_detached_and_not_authorization(self):
        first = design.manifest()
        design.validate_manifest(json.loads(json.dumps(first)))
        self.assertEqual(first, design.manifest())
        self.assertFalse(first["execution_authorized"])
        first["founder_seeds"][0][0] = -1
        self.assertNotEqual(first, design.manifest())

    def test_eight_new_disjoint_founder_pools(self):
        pools = design.manifest()["founder_seeds"]
        self.assertEqual([len(p) for p in pools], [40] * 8)
        self.assertEqual(len({seed for pool in pools for seed in pool}), 320)
        self.assertFalse(set(range(100_000, 100_024)) & {s for p in pools for s in p})
        for p in range(8):
            self.assertEqual(pools[p], [design.founder_seed(p, s) for s in range(40)])

    def test_founder_bounds_and_bool_rejected(self):
        for p, s in [(-1, 0), (8, 0), (0, 40), (True, 0), (0, False), (0, 1.0)]:
            with self.subTest(p=p, s=s), self.assertRaises(ValueError):
                design.founder_seed(p, s)

    def test_allocations_and_ecological_balance(self):
        for cohort, start, stop in [("development", 44, 50), ("selection", 72, 120),
                                    ("validation", 120, 168)]:
            rows = design.world_rows(cohort)
            self.assertEqual({r["index"] for r in rows}, set(range(start, stop)))
            for p in ({None} if cohort == "development" else range(8)):
                block = [r for r in rows if r["population"] == p]
                self.assertEqual([(r["family"], r["repeat"]) for r in block],
                                 [(f, r) for f in design.FAMILIES for r in range(2)])

    def test_world_and_life_seeds_do_not_overlap_between_blocks(self):
        rows = [r for cohort in design.OFFSETS for r in design.world_rows(cohort)]
        self.assertEqual(len(rows), 102)
        self.assertEqual(len({r["world_seed"] for r in rows}), 102)
        self.assertEqual(len({r["life_seed"] for r in rows}), 102)
        self.assertFalse({r["world_seed"] for r in rows} & set(range(1_200_000, 1_200_200)))

    def test_reserve_and_unknown_cohort_not_available(self):
        for cohort in ["reserve", "R", "F1", "", None, 0]:
            with self.subTest(cohort=cohort), self.assertRaises(ValueError):
                design.world_rows(cohort)

    def test_new_allocation_collision_rejected_not_shifted(self):
        for cohort in design.OFFSETS:
            seed = design.world_rows(cohort)[0]["world_seed"]
            with self.subTest(cohort=cohort), self.assertRaisesRegex(ValueError, "occupied"):
                design.manifest([seed])
        self.assertEqual(design.manifest([1]), design.manifest())

    def test_invalid_collision_identifiers(self):
        for bad in [True, -1, 3.2, "30120", None]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                design.manifest([bad])

    def test_tampering_including_rehash_cannot_authorize_execution(self):
        for field, value in [("execution_authorized", True), ("populations", 4),
                              ("status", "PREREGISTERED")]:
            data = design.manifest()
            data[field] = value
            data.pop("sha256")
            data["sha256"] = design._digest(data)
            with self.subTest(field=field), self.assertRaises(ValueError):
                design.validate_manifest(data)
        data = design.manifest()
        data["worlds"]["validation"][0]["index"] = 119
        with self.assertRaises(ValueError):
            design.validate_manifest(data)

    def test_cost_envelope_is_planned_not_observed(self):
        data = design.manifest()
        self.assertEqual(data["planned_selection_lives_two_architectures"], 3840)
        self.assertEqual(data["planned_validation_lives_two_architectures"], 480)
        self.assertEqual(data["maximum_life_steps_excluding_development"], 1_728_000)
        self.assertIn("energetic_receipt_adapter", data["unresolved"])
        self.assertIn("family_R_and_revision_endpoint", data["unresolved"])

    def test_planning_process_never_imports_an_engine(self):
        script = ("import json, sys; from i3.lab.stage0_design import manifest; "
                  "m=manifest(); assert not any(k.startswith(('i3.modules', 'i3.runtime')) "
                  "for k in sys.modules); print(m['sha256'])")
        result = subprocess.run([sys.executable, "-c", script], cwd=ROOT / "src",
                                text=True, capture_output=True, check=True)
        self.assertEqual(result.stdout.strip(), design.manifest()["sha256"])


class Stage0RankingTests(unittest.TestCase):
    def test_complete_tie_resolves_by_seed_not_input_order(self):
        rows = complete_selection()
        expected = tuple(design.founder_seed(0, slot) for slot in range(5))
        self.assertEqual(design.rank_candidates(0, rows), expected)
        self.assertEqual(design.rank_candidates(0, reversed(rows)), expected)

    def test_censored_count_precedes_total_steps_then_seed(self):
        rows = complete_selection()
        # Candidate 39 has one censored life and five short deaths.
        # Candidate 38 has no censored life, but a longer total lifespan.
        for row in rows:
            if row["candidate_seed"] == design.founder_seed(0, 38):
                row["steps_lived"] = 399
            if row["candidate_seed"] == design.founder_seed(0, 39):
                row["steps_lived"] = 1
                if row["world_index"] == 72:
                    row.update(terminal="censored", steps_lived=400)
        ranking = design.rank_candidates(0, rows)
        self.assertEqual(ranking[:2], (design.founder_seed(0, 39), design.founder_seed(0, 38)))

    def test_missing_and_duplicate_receipts_block_selection(self):
        rows = complete_selection()
        for changed in [rows[:-1], rows + [rows[0]], rows[:-1] + [rows[0]], []]:
            with self.subTest(length=len(changed)), self.assertRaises(ValueError):
                design.rank_candidates(0, changed)

    def test_no_validation_other_population_or_foreign_founder(self):
        for field, bad in [("world_index", 120), ("world_index", 78),
                           ("candidate_seed", design.founder_seed(1, 0)),
                           ("candidate_seed", 100_000), ("world_index", True)]:
            rows = complete_selection()
            rows[0][field] = bad
            with self.subTest(field=field, bad=bad), self.assertRaises(ValueError):
                design.rank_candidates(0, rows)

    def test_crashes_and_unfinished_lives_are_not_deaths(self):
        for terminal, steps in [("crashed", 10), ("missing", 0), ("censored", 399),
                                ("dead", 0), ("dead", 401), ("dead", True),
                                ("dead", float("nan"))]:
            rows = complete_selection()
            rows[0].update(terminal=terminal, steps_lived=steps)
            with self.subTest(terminal=terminal, steps=steps), self.assertRaises(ValueError):
                design.rank_candidates(0, rows)

    def test_dead_at_horizon_is_not_censored(self):
        rows = complete_selection()
        rows[0]["steps_lived"] = 400
        self.assertEqual(design.rank_candidates(0, rows)[0], design.founder_seed(0, 0))

    def test_invalid_population_and_fields(self):
        with self.assertRaises(ValueError):
            design.rank_candidates(True, complete_selection())
        rows = complete_selection()
        rows[0]["hidden_memory"] = {}
        with self.assertRaises(ValueError):
            design.rank_candidates(0, rows)


class Stage0StatisticsTests(unittest.TestCase):
    def test_unanimity_and_seven_of_eight_are_distinct(self):
        unanimous = design.population_sign_test(dict.fromkeys(range(8), 1))
        seven = design.population_sign_test({p: 1 if p < 7 else -1 for p in range(8)})
        self.assertEqual(unanimous["p_two_sided"], 0.0078125)
        self.assertEqual(seven["p_two_sided"], 0.0703125)
        self.assertEqual(seven["effective_n"], 8)

    def test_sign_symmetry_and_magnitude_invariance(self):
        a = design.population_sign_test({p: 0.3 if p < 6 else -0.1 for p in range(8)})
        b = design.population_sign_test({p: -2 if p < 6 else 7 for p in range(8)})
        self.assertEqual(a["p_two_sided"], b["p_two_sided"])
        self.assertEqual(a["wins"], b["losses"])

    def test_ties_reduce_effective_sample_and_resolution(self):
        result = design.population_sign_test({p: 1 if p < 4 else 0 for p in range(8)})
        self.assertEqual((result["effective_n"], result["ties"]), (4, 4))
        self.assertEqual(result["p_two_sided"], 0.125)
        self.assertEqual(result["minimum_p_at_effective_n"], 0.125)

    def test_all_ties_and_balanced_signs(self):
        for differences in [dict.fromkeys(range(8), 0), {p: (-1)**p for p in range(8)}]:
            result = design.population_sign_test(differences)
            self.assertEqual(result["p_two_sided"], 1)
            self.assertEqual(result["status"], "ARITHMETIC_ONLY_NOT_A_SCIENTIFIC_VERDICT")

    def test_reject_pseudoreplication_missing_population_and_bool_id(self):
        for differences in [dict.fromkeys(range(288), 1), dict.fromkeys(range(7), 1),
                            [1] * 8, {True: 1, **{p: 1 for p in [0, 2, 3, 4, 5, 6, 7]}}]:
            with self.subTest(differences=str(differences)[:80]), self.assertRaises(ValueError):
                design.population_sign_test(differences)

    def test_reject_nonfinite_bool_and_non_numeric_values(self):
        for bad in [float("nan"), float("inf"), float("-inf"), True, "1", None]:
            differences = dict.fromkeys(range(8), 1)
            differences[0] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                design.population_sign_test(differences)


class Stage0RepositoryIntegrationTests(unittest.TestCase):
    """Run only in a full checkout; no skip hiding missing dependencies in CI."""
    def test_p2_snapshot_and_source_pin_match(self):
        from i3.lab import p2_ecologies
        self.assertEqual(design.FAMILIES, p2_ecologies.FAMILIES)
        self.assertEqual(design.HORIZON, p2_ecologies.HORIZON)
        self.assertEqual(design.COHORT_BOUNDS,
                         {k: (v.start, v.stop) for k, v in p2_ecologies.COHORTS.items()})
        content = (ROOT / "src/i3/lab/p2_ecologies.py").read_bytes()
        self.assertEqual(sha1(f"blob {len(content)}\0".encode() + content).hexdigest(), design.ECOLOGY_BLOB)
        for cohort in design.OFFSETS:
            for row in design.world_rows(cohort):
                self.assertEqual(row["world_seed"], p2_ecologies.COHORTS[cohort][row["index"]])

    def test_all_previous_schedule_allocations_are_excluded(self):
        from i3.lab import p3_schedule, p4a_schedule, p4b_schedule, p5a_schedule, p5b_schedule, p5c_schedule
        snapshots = [p3_schedule.schedule_manifest(), p4a_schedule.schedule_manifest(),
                     p4b_schedule.manifest(), p5a_schedule.manifest(),
                     p5b_schedule.manifest(), p5c_schedule.manifest()]
        def historical_seeds(value):
            if isinstance(value, dict):
                if value.get("cohort") in design.COHORT_BOUNDS and "index" in value:
                    yield design.COHORT_BOUNDS[value["cohort"]][0] + value["index"]
                for child in value.values():
                    yield from historical_seeds(child)
            elif isinstance(value, list):
                for child in value:
                    yield from historical_seeds(child)
        occupied = set(historical_seeds(snapshots))
        self.assertTrue(set(range(30_000, 30_120)) <= occupied)
        self.assertTrue(set(range(10_000, 10_072)) <= occupied)
        design.validate_manifest(design.manifest(), occupied)
        old = {s for pool in snapshots[0]["generation_zero_seeds"] for s in pool}
        new = {s for pool in design.manifest()["founder_seeds"] for s in pool}
        self.assertFalse(old & new)


if __name__ == "__main__":
    unittest.main()
