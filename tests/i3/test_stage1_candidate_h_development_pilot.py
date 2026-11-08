"""Prospective checks for the fresh Candidate-H 58/59 DEVELOPMENT pilot."""
from pathlib import Path
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage0_design
from i3.lab import stage1_candidate_h_development_pilot as d


class CandidateHDevelopmentPilotTests(unittest.TestCase):
    def test_frozen_three_arm_development_envelope(self):
        plan = d.plan()
        self.assertEqual(len(plan["cases"]), 36)
        self.assertEqual(plan["maximum_steps"], 14400)
        self.assertEqual({row["cohort"] for row in plan["cases"]},
                         {"development"})
        self.assertEqual({row["index"] for row in plan["cases"]}, {58, 59})
        self.assertEqual({row["world_seed"] for row in plan["cases"]},
                         {2058, 2059})
        self.assertEqual(
            tuple(dict.fromkeys(row["policy"] for row in plan["cases"])),
            d.POLICIES)
        self.assertEqual(
            d.digest(plan),
            "c307db1ec5b01b860bce40b1aa1f359a502da32fe3f7e46625b1c80811fd5951")
        self.assertTrue(plan["survival_is_not_a_continuation_rule"])
        self.assertTrue(plan["no_selection_validation_or_reserve"])

    def test_new_indices_are_inside_p2_development_and_not_stage0_history(self):
        historical = {
            row["index"] for row in stage0_design.world_rows("development")}
        self.assertTrue({58, 59}.isdisjoint(historical))
        first, stop = stage0_design.COHORT_BOUNDS["development"]
        self.assertEqual((first, stop), (2000, 2100))
        self.assertEqual(
            {first + index for index in d.INDICES}, {2058, 2059})

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
            "from i3.lab.stage1_candidate_h_development_pilot import plan; "
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

    def test_probe_unfunded_clears_stale_learning_authority_and_has_observer(self):
        from i3.lab import stage1_candidate_g_no_omega_integration as G
        from i3.modules.body import BodyLaws, CognitiveBudget
        from i3.modules.personal_relevance_candidate_h_mind import (
            PersonalRelevanceCandidateHMind)

        body = (0.01, 80.0, 80.0, 80.0, 0.01)
        mind = PersonalRelevanceCandidateHMind(
            G.genome(0.0), 211,
            observer_decision_diagnostics=True)
        G.prime_generic(mind)
        G.prime_recurrence(mind)
        mind.last = ("STALE_PREVIOUS_ACTION",)

        result = mind.decide(
            G.cap(body), CognitiveBudget(body, BodyLaws()))
        info = result[3]

        self.assertEqual(info["candidate_h_route"], "PROBE_UNFUNDED")
        self.assertEqual(info["funding"], "NO_FUNDED_RELEVANCE_PROBE")
        self.assertIsNone(mind.last)
        self.assertIsNone(result[0])
        self.assertIn(
            info["observer"]["decision_outcome"],
            ("no_processing_budget", "no_funded_score"))
        self.assertEqual(info["observer"]["offered_options"], 0)
        self.assertEqual(info["observer"]["scored_options"], 0)
        self.assertEqual(info["observer"]["score_witness"], [])

    def test_runtime_opt_in_candidate_h_is_observer_safe_on_old_fixture(self):
        from i3.lab.p2_ecologies import world_for
        from i3.modules.genome import generation_zero
        from i3.runtime.life import run_life

        # Development index 0 is an existing software fixture, not fresh 58/59.
        life = run_life(
            generation_zero(901),
            world_for("stable", "development", 0),
            8_680_000,
            24,
            protocol="CANDIDATE_H_RUNTIME_PREFLIGHT_SOFTWARE_ONLY",
            decision_policy=d.CANDIDATE_H,
            keep_trace=True,
            observer_mind_digest=True,
            observer_decision_diagnostics=True,
            observer_resource_acquisition=True,
            observer_full_competition=True,
        )
        self.assertEqual(
            life["experimental_policy"]["name"], d.CANDIDATE_H)
        self.assertNotIn("first_contact_omega", json.dumps(life))
        summary = life["candidate_h_relevance"]
        self.assertEqual(summary["probes"], life["steps_lived"])
        self.assertEqual(
            summary["probe_unfunded"]
            + summary["candidate_f_final"]
            + summary["p13_final"],
            life["steps_lived"])
        self.assertEqual(
            summary["persistent_simulation_mode"], "reference")
        self.assertEqual(
            summary["persistent_projection_accounting"], "chunk_end")
        self.assertEqual(
            len(life["observer_full_competition"]["steps"]),
            life["steps_lived"])

        reduced = d.behavioral_summary(life)
        self.assertEqual(
            sum(reduced["candidate_h"]["routes"].values()),
            life["steps_lived"])
        self.assertLessEqual(
            reduced["candidate_h"]["max_body_settlement_gap"], 1e-12)

    def test_continuation_rules_are_mechanistic_and_not_survival(self):
        def row(policy, *, paid_energy, paid_vigilance, funding,
                terminal="dead", h=None, g=None):
            steps = sum(funding.values())
            behavior = {
                "funding_counts": funding,
                "nonfunded_decisions": sum(
                    value for key, value in funding.items()
                    if key != "FUNDED"),
                "processing_collapse_decisions":
                    funding.get("NO_PROCESSING_BUDGET", 0),
                "actions": {"attendre": steps},
                "positive_water_uptakes": 0,
                "positive_food_uptakes": 0,
                "candidate_h": h,
                "candidate_g": g,
            }
            return {
                "identity": {"policy": policy},
                "energy": {
                    "steps_lived": steps,
                    "paid": {
                        "energy": paid_energy,
                        "vigilance": paid_vigilance},
                    "terminal": terminal,
                },
                "revision": {"status": "NOT_EVALUATED"},
                "behavior": behavior,
            }

        cases = [
            row(
                d.REFERENCE,
                paid_energy=8.0, paid_vigilance=8.0,
                funding={"FUNDED": 10},
                terminal="censored"),
            row(
                d.CANDIDATE_G,
                paid_energy=20.0, paid_vigilance=24.0,
                funding={"FUNDED": 7, "NO_PROCESSING_BUDGET": 3},
                terminal="censored",
                g={
                    "information_active_decisions": 5,
                    "reference_only_decisions": 5}),
            row(
                d.CANDIDATE_H,
                paid_energy=15.0, paid_vigilance=18.0,
                funding={"FUNDED": 9, "NO_PROCESSING_BUDGET": 1},
                terminal="dead",
                h={
                    "routes": {
                        "P1.3_FINAL": 6,
                        "CANDIDATE_F_FINAL": 4},
                    "relevance": {
                        "FALLBACK": 6,
                        "RELEVANT": 4},
                    "probe_phases": {
                        "FIRST_CONTACT_PERSONAL_RECURRENCE": 5,
                        "POST_CONTACT_PERSONAL": 5},
                    "support_but_fallback_decisions": 3,
                    "max_body_settlement_gap": 0.0}),
        ]
        summary = d.aggregate(cases)
        self.assertTrue(
            summary[d.CANDIDATE_H]["engineering_continuation_rule_met"])
        self.assertEqual(summary[d.CANDIDATE_H]["dead"], 1)
        self.assertEqual(summary[d.CANDIDATE_G]["censored"], 1)


if __name__ == "__main__":
    unittest.main()
