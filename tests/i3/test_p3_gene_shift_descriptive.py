"""No-World tests for the frozen, read-only P3 gene-shift descriptive reducer."""
import ast
import gzip
from hashlib import sha256
import json
from math import fsum
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from i3.lab import p3_gene_shift_descriptive as E
from i3.modules.genome import (
    HISTORICAL_V3_BOUNDS,
    HISTORICAL_V3_SCHEMA,
    digest_historical_v3,
    historical_v3_generation_zero,
    historical_v3_mutate,
)
from i3.modules.world import World

# Canonical report of the single frozen reading (results of 13 November 2026).
EXPECTED_REPORT_DIGEST = "9206245d59bfdfb08ec71600686810639181541ad34f007fe1bceba4e736987a"
COMMITTED_REPORT = (Path(E.__file__).resolve().parents[1] / "docs" / "studies"
                    / "stage6-light-preparation"
                    / "P3_GENE_SHIFT_DESCRIPTIVE_REPORT_2026-11-13.json")


def _synthetic(*, break_g0_pairing=False, bad_mutation_seed=False):
    """A lineage with the archived layout and known parent links.

    ``selected`` always descends from slot 0; ``random_parent`` keeps slot
    identity. Returns the archive and the genomes used to build it.
    """
    populations, built = [], {}
    for p in range(E.POPULATIONS):
        generations = []
        for g in range(E.GENERATIONS):
            arms = {}
            for arm in E.ARMS:
                rows = []
                for slot in range(E.GENOTYPES):
                    if g == 0:
                        seed = 900_000 + p * E.GENOTYPES + slot
                        if break_g0_pairing and arm == "random_parent" and (p, slot) == (1, 2):
                            seed += 50_000
                        genome = historical_v3_generation_zero(seed)
                        row = {"slot": slot, "genome_seed": seed,
                               "parent_slot": None}
                    else:
                        parent_slot = 0 if arm == "selected" else slot
                        parent = built[(p, arm, g - 1, parent_slot)]
                        seed = (700_000 + p * 1_000 + g * 100
                                + slot * len(E.ARMS) + E.ARMS.index(arm))
                        genome = historical_v3_mutate(parent, seed,
                                                      scale=E.MUTATION_SCALE)
                        row = {"slot": slot, "mutation_seed": seed,
                               "parent_slot": parent_slot,
                               "parent_genome_sha256": digest_historical_v3(parent)}
                        if bad_mutation_seed and (p, arm, g, slot) == (2, "selected", 2, 4):
                            row["mutation_seed"] = seed + 1
                    row["genome_sha256"] = digest_historical_v3(genome)
                    built[(p, arm, g, slot)] = genome
                    rows.append(row)
                arms[arm] = rows
            generations.append({"generation": g, "arms": arms,
                                "world_indices": []})
        populations.append({"population": p, "generations": generations})
    archive = {"schema": E.ARCHIVE_SCHEMA, "source_sha": "synthetic-source",
               "total_lives": 0, "populations": populations}
    return archive, built


def _write(folder, archive):
    raw = json.dumps(archive, sort_keys=True).encode("utf-8")
    path = Path(folder) / "synthetic.json.gz"
    with gzip.open(path, "wb") as handle:
        handle.write(raw)
    return path, sha256(raw).hexdigest()


def _audit_synthetic(archive):
    with tempfile.TemporaryDirectory() as folder:
        path, digest = _write(folder, archive)
        return E.audit(path, digest, None,
                       expected_source_sha="synthetic-source",
                       expected_total_lives=0)


class P3GeneShiftDescriptiveTests(unittest.TestCase):
    def test_exact_p3_original_is_verified_without_world_or_life(self):
        with patch.object(World, "__init__",
                          side_effect=AssertionError("no World allowed")), patch(
                              "i3.runtime.life.run_life",
                              side_effect=AssertionError("no new life")):
            report = E.audit()
            again = E.audit()
        print("I3_P3_GENE_SHIFT_DESCRIPTIVE=" + json.dumps(
            report, sort_keys=True, separators=(",", ":")))
        self.assertEqual(report["status"],
                         "P3_GENE_SHIFT_DESCRIPTIVE_READ_COMPLETE")
        self.assertEqual(report["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(report["inference"],
                         "NONE_FOUR_POPULATIONS_DESCRIPTIVE_ONLY")
        self.assertEqual(report["archive_sha256"], E.ARCHIVE_SHA256)
        self.assertEqual(report["archive_source_sha"], E.SOURCE_SHA)
        self.assertEqual(report["genomes_verified"], 144)
        self.assertEqual(report["frozen_g2_genomes_matched"], 48)
        self.assertTrue(report["generation_zero_identical_between_arms"])
        self.assertEqual((report["worlds_opened"], report["lives_created"],
                          report["lives_rerun"]), (0, 0, 0))
        self.assertEqual(set(report["reduction"]["quantities"]),
                         set(E.QUANTITIES))
        self.assertEqual(len(E.QUANTITIES), 31)
        for entry in report["reduction"]["quantities"].values():
            for g in (1, 2):
                summary = entry[f"contrast_g{g}"]
                self.assertEqual(len(summary["per_population"]), 4)
                self.assertEqual(summary["positive"] + summary["negative"]
                                 + summary["zero"], 4)
        self.assertEqual(report["digest_sha256"], again["digest_sha256"])
        self.assertEqual(report["digest_sha256"], EXPECTED_REPORT_DIGEST)
        self.assertEqual(
            json.loads(COMMITTED_REPORT.read_text(encoding="utf-8")), report)

    def test_wrong_archive_pin_fails_closed_before_any_value(self):
        with self.assertRaisesRegex(E.IntegrityError, "archive SHA-256"):
            E.audit(expected_sha256="0" * 64)

    def test_synthetic_lineage_matches_independent_recomputation(self):
        archive, built = _synthetic()
        report = _audit_synthetic(archive)
        self.assertEqual(report["genomes_verified"], 144)
        self.assertIsNone(report["frozen_g2_genomes_matched"])

        def mean_eff(p, arm, g):
            return fsum(
                built[(p, arm, g, s)]["genes"]["beta_u"]
                * (1.0 + 0.5 * built[(p, arm, g, s)]["genes"]["temperament.exploration"])
                for s in range(E.GENOTYPES)) / E.GENOTYPES

        primary = report["reduction"]["quantities"][E.PRIMARY]
        for p in range(E.POPULATIONS):
            for g in (1, 2):
                expected = mean_eff(p, "selected", g) - mean_eff(p, "random_parent", g)
                self.assertAlmostEqual(
                    primary[f"contrast_g{g}"]["per_population"][p], expected, places=8)
            self.assertAlmostEqual(
                primary["drift_g0_to_g2"]["selected"][p],
                mean_eff(p, "selected", 2) - mean_eff(p, "selected", 0), places=8)

        lo, hi = HISTORICAL_V3_BOUNDS["beta_u"]
        values = [built[(p, "selected", 2, s)]["genes"]["beta_u"]
                  for p in range(E.POPULATIONS) for s in range(E.GENOTYPES)]
        at_bound = sum(1 for v in values if v in (lo, hi)) / len(values)
        self.assertAlmostEqual(
            report["reduction"]["bounds"]["beta_u"]["selected"][2], at_bound, places=8)

        for row in report["reduction"]["genealogy"]["selected"]:
            self.assertEqual((row["distinct_g0_ancestors"], row["top_ancestor_share"],
                              row["distinct_g1_parents"]), (1, 1.0, 1))
        for row in report["reduction"]["genealogy"]["random_parent"]:
            self.assertEqual((row["distinct_g0_ancestors"],
                              row["distinct_g1_parents"]), (6, 6))
            self.assertAlmostEqual(row["top_ancestor_share"], 1 / 6, places=8)

    def test_hand_computed_summary_and_quantities(self):
        summary = E.summarize([0.1, -0.2, 0.0, 0.3])
        self.assertEqual((summary["positive"], summary["negative"],
                          summary["zero"]), (2, 1, 1))
        self.assertAlmostEqual(summary["mean"], 0.05, places=9)
        self.assertAlmostEqual(summary["sample_sd"], (0.13 / 3) ** 0.5, places=8)
        self.assertEqual((summary["min"], summary["max"]), (-0.2, 0.3))

        midpoint = {"schema": HISTORICAL_V3_SCHEMA, "genes": {
            k: (lo + hi) / 2 for k, (lo, hi) in HISTORICAL_V3_BOUNDS.items()}}
        values = E.quantities(midpoint)
        for name in HISTORICAL_V3_BOUNDS:
            self.assertAlmostEqual(values[name], 0.5, places=12)
        self.assertAlmostEqual(values[E.PRIMARY], 1.0, places=12)

        edge = json.loads(json.dumps(midpoint))
        edge["genes"]["beta_u"] = 2.0
        edge["genes"]["temperament.exploration"] = 1.0
        values = E.quantities(edge)
        self.assertAlmostEqual(values["beta_u"], 1.0, places=12)
        self.assertAlmostEqual(values[E.PRIMARY], 3.0, places=12)

    def test_unreproduced_genome_digest_fails_closed(self):
        archive, _ = _synthetic(bad_mutation_seed=True)
        with self.assertRaisesRegex(E.IntegrityError, "genome digest"):
            _audit_synthetic(archive)

    def test_unpaired_generation_zero_fails_closed(self):
        archive, _ = _synthetic(break_g0_pairing=True)
        with self.assertRaisesRegex(E.IntegrityError, "generation zero differs"):
            _audit_synthetic(archive)

    def test_tampered_frozen_g2_record_fails_closed(self):
        archive, built = _synthetic()
        cells, _ = E.reconstruct(archive)
        entries = [{"population": p, "arm": arm, "slot": s,
                    "genome": built[(p, arm, 2, s)],
                    "genome_sha256": digest_historical_v3(built[(p, arm, 2, s)])}
                   for p in range(E.POPULATIONS) for arm in E.ARMS
                   for s in range(E.GENOTYPES)]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "g2.json"
            raw = json.dumps({"genomes": entries}).encode("utf-8")
            path.write_bytes(raw)
            self.assertEqual(
                E.check_frozen_g2(cells, path, sha256(raw).hexdigest()), 48)
            with self.assertRaisesRegex(E.IntegrityError, "frozen G2 record SHA-256"):
                E.check_frozen_g2(cells, path, "0" * 64)
            entries[7]["genome"] = built[(0, "selected", 2, 0)]
            raw = json.dumps({"genomes": entries}).encode("utf-8")
            path.write_bytes(raw)
            with self.assertRaisesRegex(E.IntegrityError, "not reproduced"):
                E.check_frozen_g2(cells, path, sha256(raw).hexdigest())

    def test_reducer_never_imports_world_mind_runtime_or_runners(self):
        tree = ast.parse(Path(E.__file__).read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {alias.name for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module or "")
        forbidden = ("i3.modules.world", "i3.modules.mind", "i3.runtime",
                     "i3.lab.p3_pilot", "i3.lab.p3_schedule",
                     "i3.lab.worldgen", "i3.lab.p2_ecologies", "i3.archive")
        self.assertEqual([m for m in imported if m.startswith(forbidden)], [])


if __name__ == "__main__":
    unittest.main()
