"""Prospective Stage-1 omega ADR-0015 design: arithmetic only, no lives."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage0_design as S
from i3.lab import stage1_omega_adr0015_design as D
from i3.modules.genome import GENE_ORDER, digest, generation_zero


def top_omega_seeds(population):
    seeds = D.founder_seeds(population)
    return tuple(sorted(
        seeds,
        key=lambda seed: (
            -generation_zero(seed)["genes"]["omega"], seed)
    )[:D.KEEP])


def selected_sets():
    reference = {
        p: D.founder_seeds(p)[:D.KEEP]
        for p in range(D.POPULATIONS)
    }
    candidate = {
        p: top_omega_seeds(p)
        for p in range(D.POPULATIONS)
    }
    return reference, candidate


def passing_validation():
    selected_reference, selected_candidate = selected_sets()
    rows = []
    validation = S.world_rows("validation")
    for arm in D.ARMS:
        for meta in validation:
            p = meta["population"]
            selected = (
                selected_reference[p] if arm == "reference"
                else selected_candidate[p])
            for seed in selected:
                terminal = "censored"
                steps = D.HORIZON
                # Equal-genome omega-zero loses one life per population.
                # Losses are spread across stable and pulse so the effect is
                # not carried by only one ecology.
                if arm == "omega_zero" and seed == selected[0]:
                    target_family = "stable" if p < 4 else "pulse"
                    if (meta["family"] == target_family
                            and meta["repeat"] == 0):
                        terminal, steps = "dead", D.HORIZON - 1

                if meta["family"] == "depletion":
                    if arm == "reference":
                        revision_status, latency = "REACQUIRED", 20
                    else:
                        revision_status, latency = "REACQUIRED", 10
                else:
                    revision_status = latency = None

                rows.append({
                    "arm": arm,
                    "population": p,
                    "family": meta["family"],
                    "world_index": meta["index"],
                    "founder_seed": seed,
                    "genome_digest": digest(D.genome_for_arm(arm, seed)),
                    "terminal": terminal,
                    "steps_lived": steps,
                    "revision_status": revision_status,
                    "revision_latency": latency,
                })
    return selected_reference, selected_candidate, rows


def custody(**updates):
    out = {name: True for name in D.CUSTODY_FIELDS}
    out.update(updates)
    return out


class OmegaAdr0015DesignTests(unittest.TestCase):
    def test_plan_reuses_unopened_stage0_selection_and_validation_contract(self):
        p = D.plan()
        self.assertFalse(p["execution_authorized"])
        self.assertEqual(p["populations"], 8)
        self.assertEqual(p["candidates_per_population"], 40)
        self.assertEqual(p["keep_per_architecture_population"], 5)
        self.assertEqual(p["horizon"], 400)
        self.assertEqual(
            {row["index"] for row in p["selection_worlds"]},
            set(range(72, 120)))
        self.assertEqual(
            {row["world_seed"] for row in p["selection_worlds"]},
            set(range(10072, 10120)))
        self.assertEqual(
            {row["index"] for row in p["validation_worlds"]},
            set(range(120, 168)))
        self.assertEqual(
            {row["world_seed"] for row in p["validation_worlds"]},
            set(range(30120, 30168)))
        self.assertEqual(p["selection_lives"], 3840)
        self.assertEqual(p["validation_main_lives"], 720)
        self.assertEqual(p["validation_replay_lives"], 144)
        self.assertEqual(p["maximum_lives"], 4704)
        self.assertEqual(p["maximum_life_steps"], 1881600)
        self.assertEqual(
            p["family_survival_noninferiority"]["max_survivor_deficit"], 2)
        self.assertEqual(
            p["omega_zero_selection"], "NEVER_INDEPENDENTLY_SELECTED")
        self.assertEqual(
            p["zero_step_physical_death"],
            "VALID_SELECTION_OUTCOME")
        self.assertEqual(p["reserve"]["policy"], "SEALED_NEVER_OPEN")

    def test_plan_rejects_collision_without_silently_shifting_worlds(self):
        with self.assertRaises(ValueError):
            D.plan([10072])
        with self.assertRaises(ValueError):
            D.plan([30167])
        self.assertEqual(
            D.plan([1])["selection_worlds"],
            D.plan()["selection_worlds"])

    def test_omega_zero_ablation_changes_only_omega_and_digest(self):
        seed = D.founder_seeds(0)[0]
        original = generation_zero(seed)
        ablated = D.omega_zero_genome(seed)
        self.assertEqual(ablated["genes"]["omega"], 0.0)
        self.assertNotEqual(digest(original), digest(ablated))
        for name in GENE_ORDER:
            if name != "omega":
                self.assertEqual(
                    original["genes"][name], ablated["genes"][name])
        self.assertEqual(
            D.genome_for_arm("reference", seed),
            D.genome_for_arm("candidate", seed))

    def test_selection_ranking_is_persistence_only_and_complete(self):
        p = 0
        worlds = [
            row for row in S.world_rows("selection")
            if row["population"] == p]
        receipts = []
        seeds = D.founder_seeds(p)
        for seed in seeds:
            for world in worlds:
                # Last seed is the only full survivor; otherwise all candidates
                # tie and founder seed is the final deterministic tie-break.
                survivor = seed == seeds[-1]
                receipts.append({
                    "candidate_seed": seed,
                    "world_index": world["index"],
                    "terminal": "censored" if survivor else "dead",
                    "steps_lived": 400 if survivor else 100,
                    "genome_digest": digest(generation_zero(seed)),
                })
        ranked = D.rank_selection(p, "candidate", receipts)
        self.assertEqual(ranked[0], seeds[-1])
        self.assertEqual(ranked[1:], seeds[:4])
        self.assertEqual(
            D.rank_selection(p, "reference", receipts), ranked)

        with self.assertRaises(ValueError):
            D.rank_selection(p, "candidate", receipts[:-1])

    def test_zero_step_physical_death_is_retained_in_selection_ranking(self):
        p = 0
        seeds = D.founder_seeds(p)
        worlds = [
            row for row in S.world_rows("selection")
            if row["population"] == p]
        rows = []
        for seed in seeds:
            for world in worlds:
                rows.append({
                    "candidate_seed": seed,
                    "world_index": world["index"],
                    "terminal": "dead",
                    "steps_lived": 0 if seed == seeds[0] else 1,
                    "genome_digest": digest(generation_zero(seed)),
                })
        ranked = D.rank_selection(p, "candidate", rows)
        self.assertNotIn(seeds[0], ranked)
        self.assertEqual(ranked, seeds[1:6])

    def test_revision_rank_keeps_no_exposure_and_failure_in_analysis(self):
        self.assertEqual(
            D._revision_rank("REACQUIRED", 17), 17)
        self.assertEqual(
            D._revision_rank("NO_EXPOSURE", None), 401)
        self.assertEqual(
            D._revision_rank("EXPOSED_NO_REACQUISITION", None), 401)
        with self.assertRaises(ValueError):
            D._revision_rank("NO_EXPOSURE", 0)

    def test_complete_synthetic_gate_can_pass_all_frozen_rules(self):
        ref, cand, rows = passing_validation()
        result = D.analyze_gate(ref, cand, rows, custody())
        self.assertTrue(result["would_pass_if_receipts_are_authentic"])
        self.assertTrue(all(result["rules"].values()))
        self.assertEqual(
            result["family_noninferiority_margin"], 2)
        self.assertGreater(
            result["omega_selection"]["pooled_candidate_selected_mean"], 0.)
        self.assertGreater(
            result["omega_selection"]["pooled_candidate_shift"], 0.)
        self.assertEqual(
            sum(x > 0 for x in
                result["omega0_population_survival_differences"].values()),
            8)
        self.assertEqual(
            sum(x > 0 for x in
                result["omega0_family_survival_differences"].values()),
            2)
        self.assertLess(
            result["revision"]["candidate"]["pooled_mean_complete_rank"],
            result["revision"]["reference"]["pooled_mean_complete_rank"])
        self.assertEqual(
            result["interpretation"],
            "SEVEN_OF_EIGHT_DIRECTIONAL_RULES_ARE_NOT_CONVENTIONAL_"
            "SIGNIFICANCE_CLAIMS")

    def test_survival_noninferiority_cannot_be_rescued_by_other_families(self):
        ref, cand, rows = passing_validation()
        changed = 0
        for row in rows:
            if (row["arm"] == "candidate"
                    and row["family"] == "stable"
                    and row["terminal"] == "censored"
                    and changed < 3):
                row["terminal"] = "dead"
                row["steps_lived"] = D.HORIZON
                changed += 1
        result = D.analyze_gate(ref, cand, rows, custody())
        self.assertFalse(
            result["rules"]["G1_family_survival_noninferiority"])
        self.assertEqual(changed, 3)

    def test_revision_gate_does_not_drop_no_exposure_lives(self):
        ref, cand, rows = passing_validation()
        for row in rows:
            if row["arm"] == "candidate" and row["family"] == "depletion":
                row["revision_status"] = "NO_EXPOSURE"
                row["revision_latency"] = None
        result = D.analyze_gate(ref, cand, rows, custody())
        self.assertFalse(
            result["rules"]["G2_revision_complete_rank_superiority"])
        self.assertEqual(
            result["revision"]["candidate"]["pooled_mean_complete_rank"],
            D.REVISION_FAILURE_RANK)
        self.assertEqual(result["revision"]["candidate"]["reacquired"], 0)

    def test_equal_genome_ablation_must_win_across_populations_and_families(self):
        ref, cand, rows = passing_validation()
        for row in rows:
            if row["arm"] == "omega_zero":
                row["terminal"] = "censored"
                row["steps_lived"] = D.HORIZON
        result = D.analyze_gate(ref, cand, rows, custody())
        self.assertFalse(
            result["rules"]["G4_equal_genome_omega0_ablation_beaten"])
        self.assertFalse(
            result["rules"]["G5_not_single_family_omega_calibration"])

    def test_custody_floor_failure_cannot_be_outvoted_by_behavior(self):
        ref, cand, rows = passing_validation()
        result = D.analyze_gate(
            ref, cand, rows,
            custody(observer_valid=False))
        self.assertFalse(result["rules"]["G6_custody_floors"])
        self.assertFalse(result["would_pass_if_receipts_are_authentic"])

    def test_validation_requires_exact_selected_genome_and_omega0_digest(self):
        ref, cand, rows = passing_validation()
        bad = deepcopy(rows)
        omega0 = next(row for row in bad if row["arm"] == "omega_zero")
        omega0["genome_digest"] = digest(
            generation_zero(omega0["founder_seed"]))
        with self.assertRaises(ValueError):
            D.analyze_gate(ref, cand, bad, custody())

    def test_incomplete_validation_never_analyzes_successful_subset(self):
        ref, cand, rows = passing_validation()
        with self.assertRaises(ValueError):
            D.analyze_gate(ref, cand, rows[:-1], custody())

    def test_final_step_physical_death_is_a_valid_outcome(self):
        ref, cand, rows = passing_validation()
        row = next(
            x for x in rows
            if x["arm"] == "reference"
            and x["family"] == "stable")
        row["terminal"] = "dead"
        row["steps_lived"] = D.HORIZON
        # The gate may fail behaviorally, but the receipt itself is physical.
        result = D.analyze_gate(ref, cand, rows, custody())
        self.assertEqual(
            result["status"], "ARITHMETIC_ONLY_NOT_SCIENTIFIC_EVIDENCE")

    def test_import_does_not_load_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_omega_adr0015_design; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
