"""No study lives: prospective checks for the 48/49 frontier-water panel."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage0_design
from i3.lab import stage1_frontier_water_diagnostic as d


class FrontierWaterDiagnosticTests(unittest.TestCase):
    def test_frozen_three_arm_development_envelope(self):
        plan = d.plan()
        self.assertEqual(len(plan["cases"]), 36)
        self.assertEqual(plan["maximum_steps"], 14400)
        self.assertEqual({row["cohort"] for row in plan["cases"]},
                         {"development"})
        self.assertEqual({row["index"] for row in plan["cases"]}, {48, 49})
        self.assertEqual(
            tuple(dict.fromkeys(row["policy"] for row in plan["cases"])),
            d.POLICIES)
        self.assertEqual(
            d.digest(plan),
            "cc225b0eb6c0b402f4736d8c97a5106d7d28310fe8870072d0a8d4ea74744fa4")
        self.assertTrue(plan["no_selection_validation_or_reserve"])

    def test_48_49_are_last_planned_stage0_development_ids(self):
        planned = {row["index"]
                   for row in stage0_design.world_rows("development")}
        self.assertEqual(planned, {44, 45, 46, 47, 48, 49})
        self.assertTrue({48, 49}.issubset(planned))
        self.assertTrue({48, 49}.isdisjoint({44, 45, 46, 47}))

    def test_each_opportunity_is_an_exact_three_policy_block(self):
        cases = d.plan()["cases"]
        self.assertEqual(len({row["life_seed"] for row in cases}), 12)
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
            "from i3.lab.stage1_frontier_water_diagnostic import plan; "
            "assert len(plan()['cases']) == 36; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.modules.mind' not in sys.modules"
        ], check=True)

    def test_launch_locks_fail_closed_before_runtime(self):
        with patch.object(
                d, "_git", side_effect=AssertionError("no git for bad SHA")):
            with self.assertRaises(ValueError):
                d.validate_launch(None, None)
        with patch.object(d, "_git", return_value="a" * 40):
            with self.assertRaises(ValueError):
                d.validate_launch("a" * 40, "wrong")

        # Correct HEAD, clean tree, but any frozen runtime change blocks launch.
        responses = (
            "a" * 40,
            "",
            "src/i3/modules/mind.py",
        )
        with patch.object(d, "_git", side_effect=responses):
            with self.assertRaisesRegex(ValueError, "preserve"):
                d.validate_launch(
                    "a" * 40, d.digest(d.plan()))

    def test_bootstrap_status_distinguishes_nonexposure_and_mechanism_failure(self):
        base = {
            "positive_water_uptakes": 0,
            "frontier_information": {
                "actionable_water_queries": 0,
                "positive_information_options": 0,
            },
        }
        self.assertEqual(
            d.bootstrap_status(base),
            "NO_WATER_EXPERIENCE_BOOTSTRAP_NOT_OBSERVED")

        water = {
            **base,
            "positive_water_uptakes": 2,
        }
        self.assertEqual(
            d.bootstrap_status(water),
            "WATER_EXPERIENCED_BUT_NO_ACTIONABLE_MODEL")

        actionable = {
            "positive_water_uptakes": 2,
            "frontier_information": {
                "actionable_water_queries": 4,
                "positive_information_options": 0,
            },
        }
        self.assertEqual(
            d.bootstrap_status(actionable),
            "ACTIONABLE_MODEL_BUT_ZERO_INFORMATION")

        positive = {
            "positive_water_uptakes": 2,
            "frontier_information": {
                "actionable_water_queries": 4,
                "positive_information_options": 1,
            },
        }
        self.assertEqual(
            d.bootstrap_status(positive),
            "POSITIVE_FRONTIER_INFORMATION_OBSERVED")

    def test_positive_information_without_actionable_water_is_invalid(self):
        with self.assertRaises(ValueError):
            d.bootstrap_status({
                "positive_water_uptakes": 1,
                "frontier_information": {
                    "actionable_water_queries": 0,
                    "positive_information_options": 1,
                },
            })

    def test_behavioral_reduction_uses_original_frontier_witness(self):
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
        self.assertEqual(result["paid_frontier_information_options"], 1)
        self.assertEqual(result["positive_information_options"], 1)
        self.assertEqual(result["first_positive_information_step"], 1)
        self.assertEqual(
            result["bootstrap_status"],
            "POSITIVE_FRONTIER_INFORMATION_OBSERVED")

    def test_trace_and_runtime_frontier_counts_must_reconcile(self):
        life = {
            "steps_lived": 1,
            "trace": [{
                "t": 1, "action": None,
                "info": {
                    "funding": "FUNDED",
                    "observer": {
                        "decision_outcome": "action_admitted",
                        "score_witness": [],
                    },
                },
                "funding_phases": {
                    "decision": {
                        "body_before": [80] * 5,
                        "work": {
                            "cycles": 1, "simulated_steps": 0,
                            "memory_items": 0, "replays": 0,
                        },
                    },
                },
            }],
            "observer_resource_acquisition": {
                "steps": [{
                    "step": 1, "action": None,
                    "decision_funding": "FUNDED",
                    "decision_outcome": "action_admitted",
                    "positive_water_uptake": False,
                }],
                "summary": {
                    "positive_water_uptakes": 0,
                    "positive_food_uptakes": 0,
                    "collected_inventory": 0,
                    "consumed_inventory": 0,
                    "new_personally_mapped_cells": 0,
                },
            },
            "observer_full_competition": {
                "steps": [{
                    "physical_action": None,
                    "decision_outcome": "action_admitted",
                }],
            },
            "frontier_information": {
                "belief_queries": 1,
                "actionable_water_queries": 1,
                "frontier_options_scored": 1,
                "positive_information_options": 0,
            },
        }
        with self.assertRaisesRegex(ValueError, "trace/output"):
            d.behavioral_summary(life)


if __name__ == "__main__":
    unittest.main()
