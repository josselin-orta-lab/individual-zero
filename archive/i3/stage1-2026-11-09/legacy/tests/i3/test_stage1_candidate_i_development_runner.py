"""Pre-exposure tests for the frozen Candidate-I 60/61 runner."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_i_development_pilot as d


class CandidateIDevelopmentRunnerTests(unittest.TestCase):
    def test_runner_uses_exact_frozen_plan_and_runtime_baseline(self):
        self.assertEqual(
            d.design.digest(d.plan()), d.design.EXPECTED_PLAN_SHA256)
        self.assertEqual(len(d.plan()["cases"]), 48)
        self.assertEqual(
            d.IMPLEMENTATION_BASELINE,
            "c3f8afc30eab6a66e38d8ca2733fe0a0c18b96b6")

    def test_import_is_inert(self):
        root = str(Path(d.__file__).resolve().parents[2])
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_candidate_i_development_pilot as d; "
            "assert len(d.plan()['cases']) == 48; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.modules.mind' not in sys.modules; "
            "assert 'i3.lab.p2_ecologies' not in sys.modules"
        ], check=True)

    def test_source_lock_rejects_protocol_source_and_runtime_drift(self):
        with patch.object(
                d, "_git", side_effect=AssertionError("no git for bad SHA")):
            with self.assertRaises(ValueError):
                d.validate_launch(None, None)

        with patch.object(d, "_git", return_value="a" * 40):
            with self.assertRaisesRegex(ValueError, "protocol"):
                d.validate_launch("a" * 40, "wrong")

        with patch.object(
                d, "_git",
                side_effect=("a" * 40, "", "src/i3/runtime/life.py")):
            with self.assertRaisesRegex(ValueError, "preserve"):
                d.validate_launch(
                    "a" * 40, d.design.EXPECTED_PLAN_SHA256)

        with patch.object(
                d, "_git", side_effect=("a" * 40, "", "")):
            d.validate_launch(
                "a" * 40, d.design.EXPECTED_PLAN_SHA256)

    def test_composite_funding_normalizes_fail_closed(self):
        base_info = {
            "funding": d.COMPOSITE,
            "candidate_h_probe_funding": "NO_FUNDED_SCORE",
            "candidate_i_probe_funding": "NO_FUNDED_SCORE",
            "observer": {"decision_outcome": "no_funded_score"},
        }
        event = {
            "decision_funding": d.COMPOSITE,
            "decision_outcome": "no_funded_score",
        }
        receipt = d._normalized_funding(base_info, event)
        self.assertEqual(receipt["normalized"], "NO_FUNDED_SCORE")
        self.assertTrue(receipt["processing_paid"])

        bad = dict(base_info)
        bad["candidate_i_probe_funding"] = "NO_PROCESSING_BUDGET"
        with self.assertRaises(ValueError):
            d._normalized_funding(bad, event)

        bad = dict(base_info)
        bad["candidate_h_probe_funding"] = "FUNDED"
        with self.assertRaises(ValueError):
            d._normalized_funding(bad, event)

    def test_synthetic_common_state_pair_qualifies_for_j2(self):
        common_event = {
            "body_before_decision": [80., 80., 40., 80., 80.],
            "personal_position": [0, 0],
            "capture_here_water": True,
            "capture_here_food_tokens": [],
            "capture_neighbor_water_cells": 0,
            "capture_neighbor_food_cells": 0,
            "capture_inventory": [],
            "capture_food": 80.,
            "capture_water": 40.,
            "death_causes": [],
            "body_after_physics": [79., 79.8, 39.6, 80., 79.],
        }
        native_info = {
            "funding": "FUNDED",
            "candidate_i_route": "INFORMATION_FINAL",
            "candidate_i_direct_trial_count": 1,
            "candidate_i_imagined_trial_count": 0,
            "first_contact_omega": 0.5,
            "omega_source": "GENOME_V4_OMEGA",
        }
        zero_info = {
            "funding": "FUNDED",
            "candidate_i_route": "P1.3_BASE_FINAL",
            "candidate_i_direct_trial_count": 1,
            "candidate_i_imagined_trial_count": 0,
            "first_contact_omega": 0.0,
            "omega_source": "SOFTWARE_OMEGA_ABLATION",
        }
        native = {
            "genome": "same",
            "steps_lived": 1,
            "candidate_i": {
                "first_contact_omega": 0.5,
                "omega_source": "GENOME_V4_OMEGA",
            },
            "trace": [{
                "t": 1, "option": "boire", "action": "boire",
                "param": None, "info": native_info,
            }],
            "observer_resource_acquisition": {
                "steps": [{**common_event, "action": "boire"}]},
        }
        zero = {
            "genome": "same",
            "steps_lived": 1,
            "candidate_i": {
                "first_contact_omega": 0.0,
                "omega_source": "SAME_GENOME_SOFTWARE_ABLATION",
                "native_genome_omega": 0.5,
                "applied_first_contact_omega": 0.0,
            },
            "trace": [{
                "t": 1, "option": "attendre", "action": "attendre",
                "param": None, "info": zero_info,
            }],
            "observer_resource_acquisition": {
                "steps": [{**common_event, "action": "attendre"}]},
        }
        receipt = d.paired_omega_receipt(native, zero)
        self.assertEqual(receipt["identical_prefix_steps"], 0)
        self.assertEqual(receipt["first_divergence_step"], 1)
        self.assertTrue(receipt["first_divergence"]["common_predecision_state"])
        self.assertTrue(receipt["qualifies_for_J2"])

    def test_runtime_reduction_smoke_uses_only_exposed_index_zero(self):
        from i3.lab.p2_ecologies import world_for
        from i3.modules.genome import generation_zero
        from i3.runtime.life import run_life

        genome = generation_zero(901)
        for policy in (d.CANDIDATE_I, d.CANDIDATE_I_OMEGA0):
            with self.subTest(policy=policy):
                life = run_life(
                    genome,
                    world_for("stable", "development", 0),
                    7_495_001,
                    4,
                    protocol="CANDIDATE_I_60_61_RUNNER_PREFLIGHT",
                    decision_policy=policy,
                    keep_trace=True,
                    observer_mind_digest=True,
                    observer_decision_diagnostics=True,
                    observer_resource_acquisition=True,
                    observer_full_competition=True,
                )
                summary = d.behavioral_summary(life)
                self.assertEqual(summary["policy"], policy)
                self.assertIn("candidate_i", summary)
                self.assertEqual(
                    summary["candidate_i"]["max_body_settlement_gap"], 0.0)

    def test_j_rules_ignore_survival_and_omega_direction(self):
        def row(policy, *, energy, vigilance, nonfunded, processing,
                water=0, food=0, routes=None, terminal="dead"):
            decisions = 10
            funding = {"FUNDED": decisions - nonfunded}
            if nonfunded:
                funding["NO_FUNDED_SCORE"] = nonfunded
            normalized = dict(funding)
            if processing:
                normalized["NO_PROCESSING_BUDGET"] = processing
            behavior = {
                "funding_counts": funding,
                "normalized_funding_counts": normalized,
                "actions": {"attendre": decisions},
                "positive_water_uptakes": water,
                "positive_food_uptakes": food,
                "collected_inventory": 0,
                "consumed_inventory": 0,
                "personally_mapped_cells": 1,
            }
            if policy == d.CANDIDATE_H:
                behavior["candidate_h"] = {"routes": routes or {}}
            if policy in (d.CANDIDATE_I, d.CANDIDATE_I_OMEGA0):
                behavior["candidate_i"] = {"routes": routes or {}}
            return {
                "identity": {"policy": policy},
                "energy": {
                    "steps_lived": 10,
                    "paid": {"energy": energy, "vigilance": vigilance},
                    "terminal": terminal,
                },
                "revision": {"status": "NOT_EVALUATED"},
                "behavior": behavior,
            }

        cases = [
            row(d.REFERENCE, energy=5, vigilance=5,
                nonfunded=0, processing=0, terminal="censored"),
            row(d.CANDIDATE_H, energy=20, vigilance=24,
                nonfunded=2, processing=1,
                routes={"P1.3_FINAL": 5, "CANDIDATE_F_FINAL": 3}),
            row(d.CANDIDATE_I, energy=15, vigilance=18,
                nonfunded=1, processing=0, water=1,
                routes={"INFORMATION_FINAL": 4, "P1.3_BASE_FINAL": 5},
                terminal="dead"),
            row(d.CANDIDATE_I_OMEGA0, energy=14, vigilance=17,
                nonfunded=1, processing=0,
                routes={"INFORMATION_FINAL": 3, "P1.3_BASE_FINAL": 6},
                terminal="censored"),
        ]
        pairs = [{"qualifies_for_J2": True}]
        summary = d.aggregate(cases, pairs)
        native = summary[d.CANDIDATE_I]
        self.assertTrue(native["engineering_continuation_rule_met"])
        self.assertEqual(native["dead"], 1)
        self.assertEqual(
            summary[d.CANDIDATE_I_OMEGA0]["censored"], 1)


if __name__ == "__main__":
    unittest.main()
