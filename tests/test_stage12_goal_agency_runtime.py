"""Opt-in GA producer across genuine mortal WorldBody physical steps."""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from i0.modules.stage12_detectors import Stage12DetectionPolicy
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage12_runtime import Stage12Runtime
from lab.independent_journal_audit import audit_export_bytes
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs
from lab.stage12_diagnostic_audit import audit_stage12_diagnostics
from lab.determinism import canonical_causal_bytes
from lab.journal import GENESIS_HASH


def opt_in_runtime(wal_path: str, *, join: bool = False):
    st11 = build_stage11_reference_runtime(autonomous_mortal=True)
    st10 = build_stage10_reference_runtime(autonomous_mortal=True)
    sleep = replace(st10._stage10_config.sleep, fatigue_gain=0.0,
                    night_weight=0.0, consolidation_weight=0.0)
    config = replace(st10._stage10_config,
                     stage9=st11._stage11_config.stage9, sleep=sleep)
    return Stage12Runtime(
        world_config=st11.world.config, layout=st11.world._layout,
        safety_config=st11.stage3.substrate.safety._config,
        safety_facts=st11._canonical_safety._innate,
        protected_integrity_threshold=st11.stage3.control._config.protected_integrity_threshold,
        stage11_config=st11._stage11_config, stage10_config=config,
        equipment=st11.equipment, autonomous_mortal=True, wal_path=wal_path,
        subjective_goal_agency=True, goal_agency_cost_uc=1,
        attribution_join=join, attribution_join_cost_uc=1,
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
        detector_policy=Stage12DetectionPolicy(
            version="issue110-first-person-real-smoke-v1", window=12,
            stagnation_steps=3, stagnation_tolerance=0.05,
            loop_repetitions=2, loop_max_period=2,
            entropy_min_samples=3, entropy_warning_fraction=0.25,
            bias_min_outcomes_each=2, attribution_bias_threshold=0.75,
        ),
    )


class Stage12FirstPersonIntegratedSmokeTests(unittest.TestCase):
    def test_real_life_ga_enabled_does_not_fabricate_pairs(self):
        with TemporaryDirectory() as root:
            rt = opt_in_runtime(str(Path(root) / "life.wal"))
            self.assertIsNotNone(rt.stage3.control.goal_agency)
            self.assertIn("goal_agency", rt.stage3.control.export_causal_state())
            self.assertEqual(len({o.owner_id for o in rt.causal_owners}),
                             len(rt.causal_owners))
            for _ in range(5):
                self.assertEqual(rt.run_step().execution_status, "applied")
            self.assertIsNone(rt.detection_report.attribution_bias)
            raw = rt.journal.canonical_bytes()
            self.assertEqual(audit_export_bytes(
                raw, expected_head=rt.journal.head_hash,
                expected_count=len(rt.journal.entries),
            ).world_steps_closed, 5)
            self.assertTrue(rt.journal.verify())
            verdict = audit_stage12_first_person_agency(
                raw, expected_head=rt.journal.head_hash,
                expected_count=len(rt.journal.entries),
            )
            self.assertEqual(verdict.judgements_world, 0)
            self.assertEqual(verdict.as_dict()["attribution_pairs_admitted"], 0)
            self.assertEqual(
                verdict.precommits,
                verdict.judgements_self + verdict.judgements_world
                + verdict.judgements_unknown + verdict.unavailable
                + verdict.pending_terminal,
            )



    def test_opt_in_paid_join_never_invents_lived_pairs(self):
        with TemporaryDirectory() as root:
            rt = opt_in_runtime(str(Path(root) / "joined.wal"), join=True)
            self.assertIsNotNone(rt._meta_custody.attribution_pairs)
            self.assertEqual(
                rt._meta_custody.attribution_pairs.schema,
                "stage12-goal-outcome-agency-pair-v1",
            )
            self.assertEqual(
                rt._config.compute_budget.operation_costs["stage12_attribution_join"], 1,
            )
            for _ in range(5):
                self.assertEqual(rt.run_step().execution_status, "applied")
            raw = rt.journal.canonical_bytes()
            report = audit_stage12_attribution_pairs(
                raw, expected_head=rt.journal.head_hash,
                expected_count=len(rt.journal.entries),
            )
            self.assertEqual(report.applied_pairs,
                             report.applied_successes + report.applied_failures)
            self.assertEqual(report.applied_pairs,
                             report.applied_self + report.applied_world)
            self.assertEqual(len(report.diagnostic_labels), 5)
            self.assertEqual(
                audit_stage12_diagnostics(raw).diagnostic_samples, 5,
            )

    def test_forged_but_rehashed_attribution_pair_refused(self):
        with TemporaryDirectory() as root:
            rt = opt_in_runtime(str(Path(root) / "forged.wal"), join=True)
            for _ in range(3):
                self.assertEqual(rt.run_step().execution_status, "applied")
            rows = [json.loads(r) for r in rt.journal.canonical_bytes().split(b"\\n")]
            idx = next(i for i, r in enumerate(rows)
                       if r["causal_event"]["kind"] == "perceptual_capture"
                       and r["causal_event"]["t_monde"] == 2)
            event = rows[idx]["causal_event"]
            rows.insert(idx + 1, {
                "index": -1, "event_id": "forged:goal-outcome-agency",
                "previous_hash": GENESIS_HASH, "event_hash": GENESIS_HASH,
                "causal_event": {
                    "emitter": "stage4-runtime",
                    "kind": "stage12_attribution_pair_admitted",
                    "t_monde": 2, "cycle": 1,
                    "attempt_ref": event["attempt_ref"],
                    "data": {
                        "version": "stage12-goal-outcome-agency-pair-v1",
                        "intent_ref": "invented", "life_id": rt.individual_id,
                        "agency_judgement_ref": "invented",
                        "goal_followup_ref": "invented",
                        "agency_assessment_ref": "invented",
                        "observed_world_step": 2,
                        "outcome": "success", "agency": "self",
                    },
                },
            })
            previous = GENESIS_HASH
            for i, row in enumerate(rows):
                row["index"] = i
                row["previous_hash"] = previous
                previous = sha256(
                    bytes.fromhex(previous) + canonical_causal_bytes({
                        "event_id": row["event_id"],
                        "causal_event": row["causal_event"],
                    })
                ).hexdigest()
                row["event_hash"] = previous
            forged = b"\\n".join(canonical_causal_bytes(r) for r in rows)
            self.assertEqual(audit_export_bytes(forged).world_steps_closed, 3)
            with self.assertRaisesRegex(ValueError, "attribution join"):
                audit_stage12_attribution_pairs(forged)


if __name__ == "__main__":
    unittest.main()
