"""No fresh study lives: prospective checks for the 50/51 frontier-water panel."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage0_design
from i3.lab import stage1_frontier_water_fresh_diagnostic as d


class FreshFrontierWaterDiagnosticTests(unittest.TestCase):
    def test_frozen_three_arm_development_envelope(self):
        plan = d.plan()
        self.assertEqual(len(plan["cases"]), 36)
        self.assertEqual(plan["maximum_steps"], 14400)
        self.assertEqual({row["cohort"] for row in plan["cases"]},
                         {"development"})
        self.assertEqual({row["index"] for row in plan["cases"]}, {50, 51})
        self.assertEqual(
            tuple(dict.fromkeys(row["policy"] for row in plan["cases"])),
            d.POLICIES)
        self.assertEqual(
            d.digest(plan),
            "01fcd7bf03f7dc8b64b93e17ffa221740c1aca4081c1433f1c893bbee237576d")
        self.assertEqual(
            plan["allocation_contract"],
            "FRESH_STAGE1_EXTENSION_50_51_OUTSIDE_FROZEN_STAGE0_44_49")
        self.assertEqual(
            plan["previous_panel"],
            "48_49_CLOSED_ENGINEERING_FAILURE_NO_REUSE")
        self.assertTrue(plan["no_selection_validation_or_reserve"])

    def test_new_indices_extend_but_do_not_rewrite_frozen_stage0_metadata(self):
        historical = {
            row["index"] for row in stage0_design.world_rows("development")}
        self.assertEqual(historical, {44, 45, 46, 47, 48, 49})
        self.assertTrue({50, 51}.isdisjoint(historical))
        first, stop = stage0_design.COHORT_BOUNDS["development"]
        self.assertEqual((first, stop), (2000, 2100))
        self.assertTrue(all(0 <= index < stop - first for index in d.INDICES))
        self.assertEqual(
            {first + index for index in d.INDICES}, {2050, 2051})

    def test_each_opportunity_is_an_exact_three_policy_block(self):
        cases = d.plan()["cases"]
        self.assertEqual(len({row["life_seed"] for row in cases}), 12)
        self.assertTrue(all(
            7_430_000 <= row["life_seed"] < 7_433_000
            for row in cases))
        for start in range(0, len(cases), len(d.POLICIES)):
            block = cases[start:start + len(d.POLICIES)]
            self.assertEqual(
                tuple(row["policy"] for row in block), d.POLICIES)
            shared = {
                key: block[0][key]
                for key in (
                    "block", "family", "cohort", "index",
                    "genome_seed", "life_seed")}
            for row in block[1:]:
                self.assertEqual(
                    {key: row[key] for key in shared}, shared)

    def test_plan_import_does_not_load_runtime_or_world(self):
        root = str(Path(d.__file__).resolve().parents[2])
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "from i3.lab.stage1_frontier_water_fresh_diagnostic import plan; "
            "assert len(plan()['cases']) == 36; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.modules.mind' not in sys.modules"
        ], check=True)

    def test_launch_locks_repaired_source_and_runtime(self):
        with patch.object(
                d, "_git", side_effect=AssertionError("no git for bad SHA")):
            with self.assertRaises(ValueError):
                d.validate_launch(None, None)
        with patch.object(d, "_git", return_value="a" * 40):
            with self.assertRaises(ValueError):
                d.validate_launch("a" * 40, "wrong")

        responses = (
            "a" * 40,
            "",
            "src/i3/runtime/competition_observer.py",
        )
        with patch.object(d, "_git", side_effect=responses):
            with self.assertRaisesRegex(ValueError, "preserve"):
                d.validate_launch(
                    "a" * 40, d.digest(d.plan()))

    def test_bootstrap_status_semantics_are_unchanged_from_failed_panel(self):
        cases = (
            ({
                "positive_water_uptakes": 0,
                "frontier_information": {
                    "actionable_water_queries": 0,
                    "positive_information_options": 0,
                }},
             "NO_WATER_EXPERIENCE_BOOTSTRAP_NOT_OBSERVED"),
            ({
                "positive_water_uptakes": 2,
                "frontier_information": {
                    "actionable_water_queries": 0,
                    "positive_information_options": 0,
                }},
             "WATER_EXPERIENCED_BUT_NO_ACTIONABLE_MODEL"),
            ({
                "positive_water_uptakes": 2,
                "frontier_information": {
                    "actionable_water_queries": 4,
                    "positive_information_options": 0,
                }},
             "ACTIONABLE_MODEL_BUT_ZERO_INFORMATION"),
            ({
                "positive_water_uptakes": 2,
                "frontier_information": {
                    "actionable_water_queries": 4,
                    "positive_information_options": 1,
                }},
             "POSITIVE_FRONTIER_INFORMATION_OBSERVED"),
        )
        for behavior, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(d.bootstrap_status(behavior), expected)

    def test_positive_information_without_actionable_water_is_invalid(self):
        with self.assertRaises(ValueError):
            d.bootstrap_status({
                "positive_water_uptakes": 1,
                "frontier_information": {
                    "actionable_water_queries": 0,
                    "positive_information_options": 1,
                },
            })

    def test_exact_failed_observer_path_is_software_preflighted_on_old_fixture(self):
        from i3.lab.p2_ecologies import world_for
        from i3.modules.genome import generation_zero
        from i3.runtime.life import run_life

        # Existing development index 0 is a software fixture already used by
        # I3 tests. It is not part of the fresh 50/51 scientific allocation.
        life = run_life(
            generation_zero(901),
            world_for("stable", "development", 0),
            8_650_000,
            24,
            protocol="FRONTIER_OBSERVER_PREFLIGHT_SOFTWARE_ONLY",
            decision_policy="reference_frontier_information_v1",
            keep_trace=True,
            observer_mind_digest=True,
            observer_decision_diagnostics=True,
            observer_resource_acquisition=True,
            observer_full_competition=True,
        )
        self.assertEqual(
            len(life["observer_full_competition"]["steps"]),
            life["steps_lived"])
        self.assertEqual(
            life["cognitive_accounting"]["status"],
            "SETTLED_FOR_DECLARED_WORK")
        for row in life["observer_full_competition"]["steps"]:
            for score in row["paid_option_scores"]:
                if score.get("score_kind") == "frontier_water_expected_distress":
                    self.assertAlmostEqual(
                        score["total_score"],
                        score["base_return"] + score["information_value"])

    def test_behavioral_reduction_keeps_candidate_trace_counts(self):
        witness = {
            "option": "explorer:1,0",
            "score_kind": "frontier_water_expected_distress",
            "information_value": 0.25,
        }
        life = {
            "steps_lived": 1,
            "trace": [{
                "t": 1,
                "action": "se_deplacer",
                "info": {
                    "funding": "FUNDED",
                    "observer": {
                        "decision_outcome": "action_admitted",
                        "score_witness": [witness],
                    },
                },
                "funding_phases": {
                    "decision": {
                        "body_before": [80, 80, 40, 80, 80],
                        "work": {
                            "cycles": 3, "simulated_steps": 2,
                            "memory_items": 1, "replays": 0,
                        },
                    },
                },
            }],
            "observer_resource_acquisition": {
                "steps": [{
                    "step": 1,
                    "action": "se_deplacer",
                    "decision_funding": "FUNDED",
                    "decision_outcome": "action_admitted",
                    "positive_water_uptake": False,
                }],
                "summary": {
                    "positive_water_uptakes": 0,
                    "positive_food_uptakes": 0,
                    "collected_inventory": 0,
                    "consumed_inventory": 0,
                    "new_personally_mapped_cells": 2,
                },
            },
            "observer_full_competition": {
                "steps": [{
                    "physical_action": "se_deplacer",
                    "decision_outcome": "action_admitted",
                }],
            },
            "branch_effect_memory": {
                "capacity": 18, "retained": 1, "recorded": 1,
                "td_capacity": 8, "td_retained": 1,
            },
            "frontier_information": {
                "scope": "one_generic_new_cell_water_only",
                "belief_queries": 1,
                "actionable_water_queries": 1,
                "frontier_options_scored": 1,
                "positive_information_options": 1,
                "food_information": "NOT_IMPLEMENTED",
                "multi_cell_joint_outcomes": "NOT_IMPLEMENTED",
            },
        }
        result = d.behavioral_summary(life)
        self.assertEqual(result["positive_information_options"], 1)
        self.assertEqual(
            result["bootstrap_status"],
            "POSITIVE_FRONTIER_INFORMATION_OBSERVED")


if __name__ == "__main__":
    unittest.main()
