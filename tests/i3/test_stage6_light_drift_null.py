"""No-World tests for the frozen genome-only drift-null sizing model."""
import ast
from hashlib import sha256
from inspect import signature
from itertools import accumulate
import json
from pathlib import Path
import random
from statistics import NormalDist
import unittest
from unittest.mock import patch

from i3.lab import p3_schedule
from i3.lab import stage6_light_drift_null as E
from i3.modules import genome
from i3.modules.world import World

# Single frozen grid run (results of 13 November 2026) and reduced test grid.
EXPECTED_FULL_DIGEST = "21555983160ef21159062557723ee4d25a32cb8bc443d7f3cc9b0456d9a586e5"
EXPECTED_REDUCED_DIGEST = "9979486a45bf77fcd5ff94ecae1047b26cff8904d070964dd057284a2e4c3a50"
COMMITTED_REPORT = (Path(E.__file__).resolve().parents[1] / "docs" / "studies"
                    / "stage6-light-preparation"
                    / "STAGE6_LIGHT_DRIFT_NULL_REPORT_2026-11-13.json")


class Stage6LightDriftNullTests(unittest.TestCase):
    def test_frozen_constants_match_the_p3_lineage_rule(self):
        self.assertEqual(E.MUTATION_SCALE, p3_schedule.MUTATION_SCALE)
        self.assertEqual(signature(genome.mutate).parameters["scale"].default,
                         E.MUTATION_SCALE)
        self.assertEqual(E.ARMS, p3_schedule.ARMS)
        self.assertEqual(E.LIVES_PER_GENOME,
                         len(p3_schedule.FAMILIES) * p3_schedule.REPEATS)
        self.assertEqual(E.HORIZON, p3_schedule.HORIZON)
        # P3 rank weights N..1: six genomes give a total weight of 21.
        self.assertEqual(list(accumulate(range(6, 0, -1)))[-1], 21)
        self.assertAlmostEqual(E.SD_G0_BETA_U_EFF, (4 / 9) ** 0.5, places=12)
        self.assertEqual((E.GRID_N, E.GRID_G, E.REGIMES, E.REPLICATES),
                         ((6, 12, 24, 48), (3, 4, 6, 8),
                          ("fresh", "heritable"), 4000))

    def test_sign_thresholds_match_hand_computation(self):
        self.assertEqual(E.sign_threshold(8), (8, 2 / 256))
        self.assertEqual(E.sign_threshold(12), (10, 158 / 4096))
        self.assertEqual(E.sign_threshold(16), (13, 1394 / 65536))
        # Seven of eight is directional only, as DEVELOPMENT_PLAN.md states.
        self.assertAlmostEqual(2 * 9 / 256, 0.0703125, places=12)
        self.assertEqual(E.sign_threshold(4), (None, None))

    def test_detectable_ratio_matches_closed_form_for_eight(self):
        pi, ratio = E.detectable_ratio(8, 8)
        self.assertAlmostEqual(pi, 0.8 ** (1 / 8), places=6)
        self.assertAlmostEqual(ratio, NormalDist().inv_cdf(0.8 ** (1 / 8)), places=5)
        pi12, ratio12 = E.detectable_ratio(12, 10)
        self.assertTrue(0.85 < pi12 < 0.89 and 1.0 < ratio12 < 1.25)
        self.assertLess(ratio12, ratio)

    def test_paired_founders_and_single_lineage_invariants(self):
        rng = random.Random("unit-g0")
        pop = E.simulate_population(rng, 5, 1, "fresh")
        for q in E.QUANTITIES:
            self.assertEqual(pop["selected"][q], pop["random_parent"][q])
        self.assertEqual(pop["selected"]["founders"], 5)
        for regime in E.REGIMES:
            one = E.simulate_population(random.Random("unit-one"), 1, 6, regime)
            for arm in E.ARMS:
                self.assertEqual(one[arm]["founders"], 1)
                self.assertTrue(0.0 <= one[arm]["z"] <= 1.0)
                self.assertTrue(0.0 <= one[arm]["beta_u_eff"] <= 3.0)
        # Fully heritable rank: the top founder keeps the largest expected share,
        # so the selected arm cannot keep more founders than it started with.
        many = E.simulate_population(random.Random("unit-many"), 12, 8, "heritable")
        self.assertLessEqual(many["selected"]["founders"], 12)
        with self.assertRaises(ValueError):
            E.simulate_population(random.Random(0), 4, 2, "unknown")

    def test_reduced_grid_runs_without_world_or_life_and_is_deterministic(self):
        with patch.object(World, "__init__",
                          side_effect=AssertionError("no World allowed")), patch(
                              "i3.runtime.life.run_life",
                              side_effect=AssertionError("no new life")):
            first = E.audit(grid_n=(4,), grid_g=(2,), replicates=200)
            again = E.audit(grid_n=(4,), grid_g=(2,), replicates=200)
        self.assertEqual(first["digest_sha256"], again["digest_sha256"])
        self.assertEqual(first["digest_sha256"], EXPECTED_REDUCED_DIGEST)
        self.assertEqual(first["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual((first["worlds_opened"], first["lives_created"]), (0, 0))
        self.assertFalse(first["checks"]["s1_order_of_magnitude_evaluated"])
        self.assertEqual(len(first["configurations"]), 2)
        self.assertEqual(len(first["sizing_table"]), 2 * len(E.POPULATION_OPTIONS))
        row = next(r for r in first["sizing_table"]
                   if r["regime"] == "fresh" and r["populations"] == 8)
        self.assertEqual(row["lives"], 8 * 2 * 4 * 6 * 2)
        self.assertEqual(row["max_steps"], row["lives"] * 400)
        config = first["configurations"][0]
        ratio = first["criteria"][0]["detectable_ratio"]
        self.assertAlmostEqual(row["detectable_shift"]["z"],
                               ratio * config["contrast"]["z"]["sd"], places=7)
        for config in first["configurations"]:
            self.assertGreater(config["contrast"]["z"]["sd"], 0.0)
            self.assertLessEqual(config["mean_founders_left"]["selected"], 4.0)

    def test_committed_full_report_is_pinned_and_internally_consistent(self):
        report = json.loads(COMMITTED_REPORT.read_text(encoding="utf-8"))
        digest = report.pop("digest_sha256")
        self.assertEqual(digest, EXPECTED_FULL_DIGEST)
        self.assertEqual(sha256(json.dumps(
            report, sort_keys=True, separators=(",", ":"),
            allow_nan=False).encode("utf-8")).hexdigest(), digest)
        self.assertEqual(report["status"], "DRIFT_NULL_SIZING_COMPLETE")
        self.assertEqual(report["flags"], ["COMPOSITE_NULL_ASYMMETRY"])
        self.assertEqual(report["preflight_commit"], E.PREFLIGHT_COMMIT)
        params = report["parameters"]
        self.assertEqual((tuple(params["grid_n"]), tuple(params["grid_g"]),
                          tuple(params["regimes"]), params["replicates"]),
                         (E.GRID_N, E.GRID_G, E.REGIMES, E.REPLICATES))
        self.assertEqual(len(report["configurations"]), 32)
        chosen = report["recommendation"]["0.5"]
        self.assertEqual((chosen["populations"], chosen["n"], chosen["generations"],
                          chosen["threshold"], chosen["lives"]),
                         (16, 24, 3, 13, 13824))
        self.assertEqual(report["recommendation"]["0.25"], "NONE_IN_GRID")
        # The rule is re-applied to the committed table, not trusted.
        limit = 0.5 * E.SD_G0_BETA_U_EFF
        eligible = [row for row in report["sizing_table"]
                    if row["regime"] == "heritable"
                    and row["detectable_shift"]["beta_u_eff"] <= limit]
        self.assertEqual(min(eligible, key=lambda r: (
            r["lives"], r["generations"], r["n"], r["populations"])), chosen)

    def test_model_never_imports_world_mind_runtime_or_runners(self):
        tree = ast.parse(Path(E.__file__).read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {alias.name for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module or "")
        self.assertEqual([m for m in imported if m.startswith("i3")], [])


if __name__ == "__main__":
    unittest.main()
