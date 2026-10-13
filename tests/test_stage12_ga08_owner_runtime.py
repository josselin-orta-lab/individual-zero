"""GA-08 owner custody and real integrated passive-runtime compatibility.

These tests do not force goal decisions or count synthetic samples as science.
"""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import PerceptualCapture, PerceivedCell
from i0.modules.stage12_spatial_goal_evidence import (
    preregister_spatial_subgoal, SpatialGoalPrecommit,
)
from i0.modules.stage12_goal_progress import Stage12GoalProgressLedger
from i0.modules.stage12_goal_agency import GoalAgencyService
from i0.modules.stage12_detectors import Stage12DetectionPolicy
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage12_runtime import Stage12Runtime
from lab.stage12_spatial_provenance_audit import audit_stage12_spatial_provenance
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs


def capture(t=1, *, x=2, y=2, blocked=False):
    return PerceptualCapture(
        t_monde=t, x=x, y=y,
        body={"food": 35.0, "water": 30.0, "energy": 40.0, "integrity": 100.0},
        current_water_source=False, current_resources=(), inventory={},
        adjacent=(
            PerceivedCell("north", x, y - 1, True, False, (), False),
            PerceivedCell("south", x, y + 1, True, False, (), False),
            PerceivedCell("east", x + 1, y, not blocked, True, (), False),
            PerceivedCell("west", x - 1, y, True, False, (), False),
        ),
    )


def commitment(blocked=False):
    return preregister_spatial_subgoal(
        life_id="life:test", intent_ref="intent:1",
        assessment_ref="agency:1", goal_ref="goal:water",
        option_ref="option:water", command_hash="digest:east",
        goal_measure="water",
        command=PrimitiveCommand("se_deplacer", {"direction": "east"}),
        capture=capture(blocked=blocked),
    )


class GA08CanonicalOwnerTests(unittest.TestCase):
    def test_spatial_precommit_in_existing_owners_separate_classifiers(self):
        p = commitment(blocked=True)
        self.assertIsNotNone(p)
        goal = Stage12GoalProgressLedger()
        goal.enable_spatial()
        agency = GoalAgencyService()
        agency.enable_spatial()
        goal.preregister(p)
        agency.preregister_spatial(
            commitment=p, capture=capture(blocked=True),
            command=PrimitiveCommand("se_deplacer", {"direction": "east"}),
        )
        self.assertEqual(goal.pending.intent_ref, agency.pending.intent_ref)
        self.assertEqual(goal.export_causal_state()["schema"],
                         "stage12-lived-goal-progress-one-step-v1+ga08")
        self.assertEqual(agency.export_causal_state()["schema"],
                         "stage12-first-person-goal-agency-v1+ga08")
        follow = goal.followup(
            world_step=2, body=capture(2, blocked=True).body,
            capture=capture(2, blocked=True), diagnostic_paid=True,
        )
        judgement = agency.evaluate(
            capture=capture(2, blocked=True), world_step=2,
            cue_ref="perceived-adjacency:2", paid=True,
        )
        self.assertEqual(follow.criterion_outcome, "failure")
        self.assertEqual(judgement.subjective_agency, "world")
        self.assertEqual(judgement.policy_version, p.policy_version)
        self.assertIsNone(goal.pending)
        self.assertIsNone(agency.pending)

    def test_cold_restore_of_spatial_pending_is_exact_and_once_only(self):
        source = Stage12GoalProgressLedger()
        source.enable_spatial()
        agency = GoalAgencyService()
        agency.enable_spatial()
        p = commitment()
        source.preregister(p)
        agency.preregister_spatial(
            commitment=p, capture=capture(),
            command=PrimitiveCommand("se_deplacer", {"direction": "east"}),
        )
        good_goal = source.export_causal_state()
        good_agency = agency.export_causal_state()
        fresh_goal = Stage12GoalProgressLedger()
        fresh_goal.enable_spatial()
        fresh_agency = GoalAgencyService()
        fresh_agency.enable_spatial()
        fresh_goal.restore_causal_state(good_goal)
        fresh_agency.restore_causal_state(good_agency)
        self.assertEqual(fresh_goal.export_causal_state(), good_goal)
        self.assertEqual(fresh_agency.export_causal_state(), good_agency)
        with self.assertRaises(ValueError):
            fresh_goal.restore_causal_state(good_goal)
        with self.assertRaises(ValueError):
            fresh_agency.restore_causal_state(good_agency)
        corrupt = source.export_causal_state()
        corrupt["pending_intent"]["target"] = [6, 6]
        clean = Stage12GoalProgressLedger()
        clean.enable_spatial()
        image = clean.export_causal_state()
        with self.assertRaises(ValueError):
            clean.restore_causal_state(corrupt)
        self.assertEqual(clean.export_causal_state(), image)

    def test_refused_uc_or_missing_observation_is_not_failure_or_world(self):
        p = commitment(blocked=True)
        ledger = Stage12GoalProgressLedger()
        ledger.enable_spatial()
        ledger.preregister(p)
        unknown = ledger.followup(
            world_step=2, body=None, diagnostic_paid=False, capture=None,
        )
        self.assertEqual(unknown.criterion_outcome, "unknown")
        service = GoalAgencyService()
        service.enable_spatial()
        service.preregister_spatial(
            commitment=p, capture=capture(blocked=True),
            command=PrimitiveCommand("se_deplacer", {"direction": "east"}),
        )
        result = service.evaluate(
            world_step=2, capture=capture(2, blocked=True),
            cue_ref=None, paid=False,
        )
        self.assertEqual(result.subjective_agency, "unavailable")


def spawn_real_spatial_runtime(wal_path: str):
    s11 = build_stage11_reference_runtime(autonomous_mortal=True)
    s10 = build_stage10_reference_runtime(autonomous_mortal=True)
    sleep = replace(s10._stage10_config.sleep, fatigue_gain=0.0,
                    night_weight=0.0, consolidation_weight=0.0)
    cfg = replace(s10._stage10_config, stage9=s11._stage11_config.stage9,
                  sleep=sleep)
    return Stage12Runtime(
        world_config=s11.world.config, layout=s11.world._layout,
        safety_config=s11.stage3.substrate.safety._config,
        safety_facts=s11._canonical_safety._innate,
        protected_integrity_threshold=s11.stage3.control._config.protected_integrity_threshold,
        stage11_config=s11._stage11_config, stage10_config=cfg,
        equipment=s11.equipment, autonomous_mortal=True, wal_path=wal_path,
        subjective_goal_agency=True, goal_agency_cost_uc=1,
        attribution_join=True, attribution_join_cost_uc=1,
        spatial_goal_agency=True, spatial_progress_cost_uc=1,
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
        detector_policy=Stage12DetectionPolicy(
            version="stage12-ga08-real-integration-v1", window=12,
            stagnation_steps=3, stagnation_tolerance=0.05,
            loop_repetitions=2, loop_max_period=2,
            entropy_min_samples=3, entropy_warning_fraction=0.25,
            bias_min_outcomes_each=2, attribution_bias_threshold=0.75,
        ),
    )


class GA08RealRuntimeSmokeTests(unittest.TestCase):
    def test_real_wal_and_audits_never_forge_a_world_judgement(self):
        with TemporaryDirectory() as root:
            rt = spawn_real_spatial_runtime(str(Path(root) / "spatial.wal"))
            owners = [x.owner_id for x in rt.causal_owners]
            self.assertEqual(owners.count("metacognition_health"), 1)
            self.assertEqual(len(owners), len(set(owners)))
            self.assertEqual(rt.compute_budget._config.operation_costs[
                "stage12_diagnostic_sample"], 2)
            for _ in range(6):
                result = rt.run_step()
                self.assertEqual(result.execution_status, "applied")
            raw = rt.journal.canonical_bytes()
            self.assertTrue(rt.journal.verify())
            senses = [
                x.causal_event["data"]
                for x in rt.journal.entries
                if x.causal_event["kind"] == "perceptual_capture"
            ]
            self.assertGreaterEqual(len(senses), 1)
            self.assertTrue(all(
                len(s["agency_visible_adjacent"]) == 4
                and s["spatial_capture_version"] == "stage12-ga08-local-adjacent-v1"
                for s in senses
            ))
            assert rt._meta_custody.goal_progress.export_causal_state()["schema"].endswith("+ga08")
            assert rt.stage3.control.goal_agency.export_causal_state()["schema"].endswith("+ga08")
            anchors = {
                "expected_head": rt.journal.head_hash,
                "expected_count": len(rt.journal.entries),
            }
            spatial = audit_stage12_spatial_provenance(raw, **anchors)
            self.assertEqual(spatial.judgements_world, 0)
            goals = audit_stage12_goal_progress(raw, **anchors)
            agency = audit_stage12_first_person_agency(raw, **anchors)
            pairs = audit_stage12_attribution_pairs(raw, **anchors)
            self.assertEqual(pairs.applied_world, 0)
            self.assertEqual(spatial.preregistered, goals.spatial_preregistered)
            self.assertGreaterEqual(agency.judgements_unknown, 0)
            self.assertIsNone(rt.detection_report.attribution_bias)


if __name__ == "__main__":
    unittest.main()
