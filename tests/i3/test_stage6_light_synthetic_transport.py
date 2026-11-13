"""Stage-6-light toy-only rehearsal: no individual, World, science or index.

Unlike a live engineering rehearsal, these invented numerical rows can be
constructed without importing I3's motor, body, World, genome or life runner.
They test receipts, phase order and denial of authority, NOT scientific power.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import inspect
import itertools
import math
from pathlib import Path
import unittest

from i3.lab import stage6_light_synthetic_transport as t


def toy_rows(generation: int) -> list[dict]:
    """Create invented persistence counters, never born individual lives."""
    out = []
    for population, g, arm, slot, family, repeat in t.expected_keys(generation):
        success = (population * 3 + generation + slot + len(arm) + repeat) % 5 == 0
        duration = 400 if success else 10 + (population * 7 + generation * 13 + slot * 11 + repeat) % 389
        out.append({
            "kind": t.KIND,
            "population": population, "generation": g, "arm": arm,
            "slot": slot, "family": family, "repeat": repeat,
            "logical_world": t.logical_world(population, g, family, repeat),
            "censored": success, "steps_lived": duration,
        })
    return out


def toy_genes(positive: int = 13, neutral_hits: int = 0, zero: int = 0) -> list[dict]:
    """Invent 16 cluster-mean directions, no mutation or genome sampled."""
    out = []
    for population, arm, slot in itertools.product(range(16), t.ARMS, range(24)):
        if population < zero:
            expressed = 1.0
        elif population < positive + zero:
            expressed = 1.1 if arm == "selected" else 1.0
        else:
            expressed = 0.9 if arm == "selected" else 1.0
        row = {"kind": t.KIND, "population": population,
               "arm": arm, "slot": slot, "beta_u_eff": expressed,
               "omega": 0.5, "temperament.affiliation": 0.5,
               "temperament.reward_sensitivity": 0.5}
        if population < 13 and arm == "selected":
            if neutral_hits >= 1:
                row["omega"] = 0.7
            if neutral_hits >= 2:
                row["temperament.affiliation"] = 0.7
            if neutral_hits >= 3:
                row["temperament.reward_sensitivity"] = 0.7
        out.append(row)
    return out


def toy_complete() -> t.SyntheticLineageTransport:
    obj = t.SyntheticLineageTransport()
    for g in (0, 1, 2):
        seal = obj.seal_generation(g, toy_rows(g))
        assert seal["receipt_count"] == (2304 if g == 0 else 4608)
        if g < 2:
            select = obj.select_next(g)
            assert select["parent_count"] == 768
    return obj


class Stage6LightToyTransportTests(unittest.TestCase):
    def test_module_has_no_engine_world_genome_runtime_or_runnable_cli(self):
        src = Path(inspect.getfile(t)).read_text(encoding="utf-8")
        tree = ast.parse(src)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)
        self.assertFalse(any(name and (name == "i3" or name.startswith("i3."))
                             for name in imports))
        self.assertFalse(any(isinstance(node, ast.If) and
                             isinstance(node.test, ast.Compare) and
                             "__main__" in ast.unparse(node.test)
                             for node in ast.walk(tree)))
        self.assertNotIn("World(", src)
        self.assertNotIn("run_life(", src.split("def run_life(self", 1)[0])

    def test_pre_authorization_is_never_replaced_by_a_toy_token(self):
        m = t.load_method()
        self.assertEqual(m["status"], "METHOD_FIXED_PREAUTH_NOT_EXECUTABLE")
        for key in ("worlds_allowed", "cohorts_allowed", "engineering_rehearsal_allowed",
                    "science_admission_allowed", "adr0017_lineage_exception_accepted"):
            self.assertIs(m["authorization"][key], False)
        for permission in m["authorization"]:
            altered = deepcopy(m)
            altered["authorization"][permission] = True
            with self.subTest(key=permission), self.assertRaises(PermissionError):
                t._inert(altered)

    def test_symbolic_calendar_and_founding_slots_are_unassigned(self):
        plan = t.preview_unassigned_allocation()
        self.assertEqual(plan["status"], "SYMBOLIC_ONLY_NOT_ALLOCATED")
        self.assertEqual(plan["world_indices_assigned"], False)
        self.assertEqual(plan["new_worlds_opened"], 0)
        self.assertEqual(plan["actual_lives_executed"], 0)
        self.assertEqual(plan["founder_seed_slots"], 384)
        self.assertEqual(plan["life_seed_slots"], 288)
        self.assertEqual(plan["parent_draw_slots"], 1536)
        self.assertEqual(plan["mutation_slots"], 1536)
        self.assertIsNone(plan["founder_seeds_assigned"])
        self.assertIsNone(plan["parent_or_mutation_seeds_assigned"])
        self.assertEqual([x["logical_coordinate"] for x in plan["coordinates"]], list(range(288)))
        self.assertTrue(all(x["physical_world_seed"] is None and x["physical_life_seed"] is None
                            for x in plan["coordinates"]))
        self.assertFalse(plan["independent_world_sampling_verified"])
        self.assertFalse(plan["historical_seed_disjointness_verified"])
        self.assertEqual(plan["coordinate_sha256"], t.preview_unassigned_allocation()["coordinate_sha256"])

    def test_mock_seed_collision_audit_never_grants_actual_independence(self):
        mock = [{"kind": t.KIND, "logical_coordinate": i, "mock_seed": 4_000_000+i}
                for i in range(288)]
        r = t.inspect_mock_world_seed_mapping(mock, toy_only=True)
        self.assertEqual(r["count"], 288)
        self.assertFalse(r["scientific_permission"])
        self.assertFalse(r["independence_certified"])
        self.assertEqual(r["worlds_opened"], r["lives_executed"])
        with self.assertRaises(PermissionError):
            t.inspect_mock_world_seed_mapping(mock, toy_only=False)
        for coordinate, mock_seed in ((1, mock[0]["mock_seed"]), (1, 90_003),
                                      (1, 10_000), (1, 1_200_000),
                                      (1, 100_000), (1, 300_200)):
            mutated = deepcopy(mock)
            mutated[coordinate]["mock_seed"] = mock_seed
            with self.subTest(seed=mock_seed), self.assertRaises(ValueError):
                t.inspect_mock_world_seed_mapping(mutated, toy_only=True)
        duplicate = deepcopy(mock)
        duplicate[1]["logical_coordinate"] = 0
        with self.assertRaises(ValueError):
            t.inspect_mock_world_seed_mapping(duplicate, toy_only=True)
        with self.assertRaises(PermissionError):
            t.inspect_mock_world_seed_mapping(mock[:-1], toy_only=True)

    def test_exact_generation_cardinality_and_g0_shared_once(self):
        self.assertEqual([len(t.expected_keys(g)) for g in range(3)],
                         [2304, 4608, 4608])
        self.assertEqual(sum(len(t.expected_keys(g)) for g in range(3)), 11520)
        self.assertEqual({key[2] for key in t.expected_keys(0)}, {"shared"})
        self.assertEqual({key[2] for key in t.expected_keys(1)}, set(t.ARMS))
        self.assertEqual(t.logical_world(0, 0, "stable", 0), 0)
        self.assertEqual(t.logical_world(15, 2, "pulse", 1), 287)
        for bad in ((-1, 0, "stable", 0), (16, 0, "stable", 0),
                    (0, 3, "stable", 0), (0, 0, "reserve", 0),
                    (0, 0, "stable", 2)):
            with self.assertRaises(ValueError):
                t.logical_world(*bad)

    def test_full_toy_g_s_g_s_g_r_is_read_only_and_deterministic(self):
        a = toy_complete()
        self.assertEqual(a.phase, "R_FINAL")
        self.assertEqual([len(a._rows[g]) for g in (0, 1, 2)], [2304, 4608, 4608])
        self.assertEqual([len(a._choices[g]) for g in (1, 2)], [768, 768])
        self.assertTrue(all(set(ch) == {"population", "arm", "offspring_slot", "parent_slot"}
                            for g in (1, 2) for ch in a._choices[g]))
        result = a.final_synthetic_signs(toy_genes())
        self.assertEqual(result["status"], "TOY_SIGN_CONCORDANCE")
        self.assertEqual(result["statistics"]["beta_u_eff"],
                         {"positive": 13, "negative": 3, "zero": 0, "concordant": 13})
        self.assertEqual(result["science_verdict"], "NOT_ISSUED")
        self.assertEqual(result["worlds_opened"], result["lives_executed"])
        self.assertEqual(result["input_scope"], t.KIND)
        self.assertEqual(a.phase, "DONE_TOY_ONLY")
        with self.assertRaises(RuntimeError):
            a.final_synthetic_signs(toy_genes())

    def test_permutation_does_not_change_seals_or_parent_choices(self):
        records = toy_rows(0)
        a = t.SyntheticLineageTransport()
        b = t.SyntheticLineageTransport()
        x = a.seal_generation(0, records)
        y = b.seal_generation(0, list(reversed(records)))
        self.assertEqual(x["sha256"], y["sha256"])
        self.assertEqual(a.select_next(0)["parent_choices_sha256"],
                         b.select_next(0)["parent_choices_sha256"])

    def test_missing_duplicate_or_foreign_receipt_fails_without_restart(self):
        records = toy_rows(0)
        variants = []
        variants.append(records[:-1])
        duplicates = deepcopy(records)
        duplicates[-1] = deepcopy(duplicates[0])
        variants.append(duplicates)
        wrong_world = deepcopy(records)
        wrong_world[0]["logical_world"] = 1
        variants.append(wrong_world)
        extra_field = deepcopy(records)
        extra_field[0]["oracle_reward"] = 100
        variants.append(extra_field)
        bad_kind = deepcopy(records)
        bad_kind[0]["kind"] = "LIVE_FROM_WORLD"
        variants.append(bad_kind)
        bad_steps = deepcopy(records)
        bad_steps[0]["steps_lived"] = 401
        variants.append(bad_steps)
        for idx, data in enumerate(variants):
            with self.subTest(case=idx):
                obj = t.SyntheticLineageTransport()
                with self.assertRaises(ValueError):
                    obj.seal_generation(0, data)
                self.assertEqual(obj.phase, "FAILED_NO_RETRY")
                with self.assertRaises(RuntimeError):
                    obj.seal_generation(0, records)

    def test_generational_state_transitions_are_one_shot(self):
        obj = t.SyntheticLineageTransport()
        with self.assertRaises(RuntimeError):
            obj.select_next(0)
        self.assertEqual(obj.phase, "FAILED_NO_RETRY")
        with self.assertRaises(RuntimeError):
            obj.seal_generation(0, toy_rows(0))
        obj = t.SyntheticLineageTransport()
        with self.assertRaises(RuntimeError):
            obj.seal_generation(1, toy_rows(1))
        self.assertEqual(obj.phase, "FAILED_NO_RETRY")

    def test_tampering_sealed_receipts_or_parent_slots_blocks_next_phase(self):
        a = t.SyntheticLineageTransport()
        a.seal_generation(0, toy_rows(0))
        a._rows[0][0]["steps_lived"] = 345
        with self.assertRaises(ValueError):
            a.select_next(0)
        self.assertEqual(a.phase, "FAILED_NO_RETRY")
        b = t.SyntheticLineageTransport()
        b.seal_generation(0, toy_rows(0))
        b.select_next(0)
        b._choices[1][0]["parent_slot"] = (b._choices[1][0]["parent_slot"] + 1) % 24
        with self.assertRaises(ValueError):
            b.seal_generation(1, toy_rows(1))
        self.assertEqual(b.phase, "FAILED_NO_RETRY")

    def test_symmetric_null_mixed_signs_and_zero_are_not_positive(self):
        result = toy_complete().final_synthetic_signs(toy_genes(positive=8))
        self.assertEqual(result["status"], "TOY_NO_SIGN_CONCORDANCE")
        self.assertEqual(result["statistics"]["beta_u_eff"]["concordant"], 8)
        zero = toy_complete().final_synthetic_signs(toy_genes(positive=8, zero=3))
        self.assertEqual(zero["statistics"]["beta_u_eff"]["zero"], 3)
        self.assertLess(zero["statistics"]["beta_u_eff"]["concordant"], 13)
        self.assertEqual(zero["science_verdict"], "NOT_ISSUED")

    def test_two_neutral_sentinels_invalidate_toy_sign_result(self):
        single = toy_complete().final_synthetic_signs(toy_genes(neutral_hits=1))
        self.assertEqual(single["status"], "TOY_SIGN_CONCORDANCE")
        self.assertEqual(single["neutral_marker_warnings"], 1)
        double = toy_complete().final_synthetic_signs(toy_genes(neutral_hits=2))
        self.assertEqual(double["status"], "TOY_INVALID_SENTINEL")
        self.assertEqual(double["neutral_marker_warnings"], 2)

    def test_malformed_gene_table_fails_closed(self):
        full = toy_complete()
        data = toy_genes()
        data[0]["beta_u_eff"] = math.nan
        with self.assertRaises(ValueError):
            full.final_synthetic_signs(data)
        self.assertEqual(full.phase, "FAILED_NO_RETRY")
        with self.assertRaises(RuntimeError):
            full.final_synthetic_signs(toy_genes())

    def test_no_toy_function_mints_a_ticket_or_launches_lives(self):
        subject = t.SyntheticLineageTransport()
        for forbidden in (subject.open_world, subject.authorize_science, subject.run_life):
            with self.subTest(method=forbidden.__name__), self.assertRaises(PermissionError):
                forbidden("any", owner_token="fake", source_sha="fake")
        self.assertEqual(subject.phase, "G0")


if __name__ == "__main__":
    unittest.main()
