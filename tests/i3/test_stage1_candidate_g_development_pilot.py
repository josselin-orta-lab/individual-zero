"""Prospective software checks for the fresh Candidate-G 56/57 pilot."""
from pathlib import Path
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage0_design
from i3.lab import stage1_candidate_g_development_pilot as d


class CandidateGDevelopmentPilotTests(unittest.TestCase):
    def test_frozen_three_arm_development_envelope(self):
        plan = d.plan()
        self.assertEqual(len(plan["cases"]), 36)
        self.assertEqual(plan["maximum_steps"], 14400)
        self.assertEqual({row["cohort"] for row in plan["cases"]},
                         {"development"})
        self.assertEqual({row["index"] for row in plan["cases"]}, {56, 57})
        self.assertEqual({row["world_seed"] for row in plan["cases"]},
                         {2056, 2057})
        self.assertEqual(
            tuple(dict.fromkeys(row["policy"] for row in plan["cases"])),
            d.POLICIES)
        self.assertEqual(
            d.digest(plan),
            "5837c98a9f94b10255e87526a0d4fa4718db09f3a9638cba3f9ff591246ba798")
        self.assertTrue(plan["survival_is_not_a_continuation_rule"])
        self.assertTrue(plan["no_selection_validation_or_reserve"])

    def test_new_indices_are_inside_p2_development_and_not_stage0_history(self):
        historical = {
            row["index"] for row in stage0_design.world_rows("development")}
        self.assertTrue({56, 57}.isdisjoint(historical))
        first, stop = stage0_design.COHORT_BOUNDS["development"]
        self.assertEqual((first, stop), (2000, 2100))
        self.assertEqual(
            {first + index for index in d.INDICES}, {2056, 2057})

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
                    "block", "family", "cohort", "index", "world_seed",
                    "genome_seed", "life_seed")}
            for row in block[1:]:
                self.assertEqual(
                    {key: row[key] for key in shared}, shared)

    def test_plan_import_does_not_load_runtime_world_or_mind(self):
        root = str(Path(d.__file__).resolve().parents[2])
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "from i3.lab.stage1_candidate_g_development_pilot import plan; "
            "assert len(plan()['cases']) == 36; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.modules.mind' not in sys.modules"
        ], check=True)

    def test_launch_lock_rejects_wrong_protocol_and_runtime_drift(self):
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
            "src/i3/runtime/life.py",
        )
        with patch.object(d, "_git", side_effect=responses):
            with self.assertRaisesRegex(ValueError, "preserve"):
                d.validate_launch(
                    "a" * 40, d.digest(d.plan()))

    def test_runtime_opt_in_candidate_g_has_no_omega_and_restores_reference(self):
        from i3.lab.p2_ecologies import world_for
        from i3.modules.genome import generation_zero
        from i3.runtime.life import run_life

        # Development index 0 is an existing software fixture, not fresh 56/57.
        life = run_life(
            generation_zero(901),
            world_for("stable", "development", 0),
            8_670_000,
            24,
            protocol="CANDIDATE_G_RUNTIME_PREFLIGHT_SOFTWARE_ONLY",
            decision_policy=d.CANDIDATE,
            keep_trace=True,
            observer_mind_digest=True,
            observer_decision_diagnostics=True,
            observer_resource_acquisition=True,
            observer_full_competition=True,
        )
        self.assertEqual(
            life["experimental_policy"]["name"], d.CANDIDATE)
        self.assertNotIn("first_contact_omega", json.dumps(life))
        frontier = life["frontier_information"]
        self.assertEqual(
            frontier["persistent_simulation_mode"], "reference")
        self.assertEqual(
            frontier["persistent_projection_accounting"], "chunk_end")
        self.assertEqual(
            frontier["omega_source"], "NONE_PERSONAL_RECURRENCE_ONLY")
        self.assertIn("opportunity_recurrence_memory", life)
        self.assertEqual(
            len(life["observer_full_competition"]["steps"]),
            life["steps_lived"])
        reduced = d.behavioral_summary(life)
        self.assertEqual(
            reduced["trace_candidate_f_projection_decisions"]
            + reduced["trace_reference_projection_decisions"],
            life["steps_lived"])

    def test_continuation_rule_is_cost_and_activation_not_survival(self):
        def row(policy, paid_energy, paid_vigilance, no_processing,
                *, active=0, reference=1, terminal="dead"):
            funding = {"FUNDED": 9, "NO_PROCESSING_BUDGET": no_processing}
            behavior = {
                "funding_counts": funding,
                "actions": {"attendre": 10 - no_processing,
                            "physical_inactivity": no_processing},
                "positive_water_uptakes": 0,
                "positive_food_uptakes": 0,
                "opportunity_recurrence_memory": (
                    {"recorded": 1} if policy == d.CANDIDATE else None),
                "frontier_information": (
                    {
                        "information_active_decisions": active,
                        "reference_only_decisions": reference,
                        "recurrence_supported_decisions": active,
                        "frontier_options_scored": active,
                        "positive_information_options": active,
                    } if policy == d.CANDIDATE else None),
            }
            return {
                "identity": {"policy": policy},
                "energy": {
                    "steps_lived": 10,
                    "paid": {
                        "energy": paid_energy,
                        "vigilance": paid_vigilance,
                    },
                    "terminal": terminal,
                },
                "revision": {"status": "NOT_EVALUATED"},
                "behavior": behavior,
            }

        cases = [
            row(d.REFERENCE, 10.0, 10.0, 0, terminal="dead"),
            row(d.CANDIDATE, 20.0, 25.0, 1,
                active=4, reference=6, terminal="dead"),
            row(d.COST_ANCHOR, 30.0, 40.0, 4, terminal="censored"),
        ]
        summary = d.aggregate(cases)
        self.assertTrue(
            summary[d.CANDIDATE]["engineering_continuation_rule_met"])
        self.assertEqual(summary[d.CANDIDATE]["dead"], 1)
        self.assertEqual(summary[d.COST_ANCHOR]["censored"], 1)

    def test_behavioral_summary_rejects_candidate_omega_evidence(self):
        life = {
            "steps_lived": 0,
            "manifest": {"experimental_policy": {"name": d.CANDIDATE}},
            "trace": [],
            "observer_resource_acquisition": {
                "steps": [],
                "summary": {
                    "positive_water_uptakes": 0,
                    "positive_food_uptakes": 0,
                    "collected_inventory": 0,
                    "consumed_inventory": 0,
                    "new_personally_mapped_cells": 0,
                },
            },
            "observer_full_competition": {"steps": []},
            "frontier_information": {
                "omega_source": "NONE_PERSONAL_RECURRENCE_ONLY",
                "persistent_simulation_mode": "reference",
                "persistent_projection_accounting": "chunk_end",
                "information_active_decisions": 0,
                "reference_only_decisions": 0,
                "recurrence_supported_decisions": 0,
                "frontier_options_scored": 0,
                "positive_information_options": 0,
            },
            "opportunity_recurrence_memory": {
                "recorded": 0,
                "snapshot": {},
            },
            "first_contact_omega": 0.0,
        }
        with self.assertRaisesRegex(ValueError, "first_contact_omega"):
            d.behavioral_summary(life)


if __name__ == "__main__":
    unittest.main()
