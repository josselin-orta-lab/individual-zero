"""Issue 110: real physical transitions, independent audit, rehashed forgeries."""
from __future__ import annotations

from dataclasses import replace
import json
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from i0.contracts import PredictedConsequence
from i0.interfaces import PrimitiveCommand
from i0.modules.agency_comparator import AgencyComparator, AgencyComparatorConfig
from i0.modules.stage12_goal_progress import (
    LivedGoalProgressIntent, Stage12GoalProgressLedger,
)
from lab.determinism import canonical_causal_bytes
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import GENESIS_HASH
from lab.stage12_attribution_provenance_audit import (
    audit_stage12_attribution_provenance,
)
from test_action_control import capture_with_creature
from test_stage12_operator_alert_runtime import actual_stage12_runtime


def _rechain(rows):
    previous = GENESIS_HASH
    for index, row in enumerate(rows):
        row["index"] = index
        row["previous_hash"] = previous
        previous = sha256(bytes.fromhex(previous) + canonical_causal_bytes({
            "event_id": row["event_id"], "causal_event": row["causal_event"],
        })).hexdigest()
        row["event_hash"] = previous
    return b"\n".join(canonical_causal_bytes(row) for row in rows)


def _five_step_life(folder: str) -> tuple[bytes, str, int]:
    runtime = actual_stage12_runtime(str(Path(folder) / "life.wal"))
    for _ in range(5):
        assert runtime.run_step().execution_status == "applied"
    assert runtime.detection_report.attribution_bias is None
    return runtime.journal.canonical_bytes(), runtime.journal.head_hash, len(runtime.journal.entries)


class Stage12AttributionProvenanceTests(unittest.TestCase):
    def test_real_physical_life_keeps_unproven_attribution_unavailable(self):
        with TemporaryDirectory() as folder:
            raw, head, count = _five_step_life(folder)
            report = audit_stage12_attribution_provenance(
                raw, expected_head=head, expected_count=count,
            )
            self.assertEqual(report.admitted_pairs, 0)
            self.assertEqual(report.unavailable_diagnostics, 5)
            self.assertEqual(
                report.verified_successes + report.verified_failures
                + report.unknown_results,
                sum(json.loads(line)["causal_event"]["kind"]
                    == "stage12_goal_progress_followup"
                    for line in raw.split(b"\n")),
            )
            self.assertFalse(report.as_dict()["bias_calibration_supported"])

    def test_changed_prediction_cannot_change_precommitted_goal_result(self):
        capture = replace(
            capture_with_creature(creature_direction=None), t_monde=2,
        )
        comparator = AgencyComparator(AgencyComparatorConfig(
            version="p47-issue110-negative-control-v1",
            tolerances={name: 0.0 for name in (
                "position_x", "position_y", "energy", "food", "water", "integrity",
            )}, max_observation_window_steps=2,
        ))
        for baseline, expected_outcome in ((50.0, "success"), (60.0, "failure")):
            with self.subTest(baseline=baseline):
                ledger = Stage12GoalProgressLedger()
                ledger.preregister(LivedGoalProgressIntent(
                    intent_ref="intent:1", goal_ref="goal:water",
                    option_ref="option:water", command_hash="physical:one",
                    measure="water", value_before=baseline,
                    sent_world_step=1, observe_world_step=2,
                ))
                result = ledger.followup(world_step=2, body=capture.body)
                self.assertEqual(result.criterion_outcome, expected_outcome)
                # *Same lived consequence* with two different predictions.
                correct = comparator.compare(
                    option_ref="option:water", sent_t_monde=1,
                    deadline_t_monde=2,
                    predictions=(PredictedConsequence("water", 60.0, 0.0),),
                    capture=capture, command=PrimitiveCommand("attendre"),
                )
                wrong = comparator.compare(
                    option_ref="option:water", sent_t_monde=1,
                    deadline_t_monde=2,
                    predictions=(PredictedConsequence("water", 30.0, 0.0),),
                    capture=capture, command=PrimitiveCommand("attendre"),
                )
                self.assertEqual(correct.status, "conforming")
                self.assertEqual(correct.attribution, "self_compatible")
                self.assertEqual(wrong.status, "nonconforming")
                self.assertEqual(wrong.attribution, "uncertain")
                self.assertEqual(result.criterion_outcome, expected_outcome)
                self.assertNotIn(correct.attribution, ("self", "world"))
                self.assertNotIn(wrong.attribution, ("self", "world"))

    def test_rehashed_diagnostic_triplet_is_not_evidence(self):
        with TemporaryDirectory() as folder:
            raw, _, _ = _five_step_life(folder)
            rows = [json.loads(x) for x in raw.split(b"\n")]
            target = next(row["causal_event"]["data"] for row in rows
                          if row["causal_event"]["kind"] == "stage12_lived_diagnostics_published")
            target.update(attribution_ref="invented", agency="self", outcome="success")
            forged = _rechain(rows)
            self.assertEqual(audit_export_bytes(forged).world_steps_closed, 5)
            with self.assertRaisesRegex(ValueError, "uncontracted attribution source"):
                audit_stage12_attribution_provenance(forged)

    def test_rehashed_positive_bias_is_refused(self):
        with TemporaryDirectory() as folder:
            raw, _, _ = _five_step_life(folder)
            rows = [json.loads(x) for x in raw.split(b"\n")]
            target = next(row["causal_event"]["data"] for row in rows
                          if row["causal_event"]["kind"] == "stage12_lived_diagnostics_published")
            target["attribution_bias"] = "self_serving_pattern"
            forged = _rechain(rows)
            audit_export_bytes(forged)
            with self.assertRaisesRegex(ValueError, "unverified lived attribution bias claim"):
                audit_stage12_attribution_provenance(forged)

    def test_rehashed_forged_p47_receipt_lacks_valid_time(self):
        with TemporaryDirectory() as folder:
            raw, _, _ = _five_step_life(folder)
            rows = [json.loads(x) for x in raw.split(b"\n")]
            cap_index = next(i for i, row in enumerate(rows)
                             if row["causal_event"]["kind"] == "perceptual_capture"
                             and row["causal_event"]["t_monde"] == 2)
            captured = rows[cap_index]["causal_event"]
            rows.insert(cap_index + 1, {
                "index": 0, "event_id": "forged:issue110:p47",
                "previous_hash": GENESIS_HASH, "event_hash": GENESIS_HASH,
                "causal_event": {
                    "emitter": "stage4-runtime", "kind": "agency_comparison",
                    "t_monde": 2, "attempt_ref": captured["attempt_ref"],
                    "data": {
                        "option_ref": "invented", "sent_t_monde": 2,
                        "observed_t_monde": 2, "status": "conforming",
                        "attribution": "self_compatible",
                        "effects": [{"variable": "water", "status": "conforming"}],
                    },
                },
            })
            forged = _rechain(rows)
            self.assertEqual(audit_export_bytes(forged).world_steps_closed, 5)
            with self.assertRaisesRegex(ValueError, "invalid observation time"):
                audit_stage12_attribution_provenance(forged)

    def test_rehashed_foreign_subjective_source_is_refused(self):
        with TemporaryDirectory() as folder:
            raw, _, _ = _five_step_life(folder)
            rows = [json.loads(x) for x in raw.split(b"\n")]
            cap_index = next(i for i, row in enumerate(rows)
                             if row["causal_event"]["kind"] == "perceptual_capture"
                             and row["causal_event"]["t_monde"] == 2)
            captured = rows[cap_index]["causal_event"]
            rows.insert(cap_index + 1, {
                "index": 0, "event_id": "forged:issue110:subjective",
                "previous_hash": GENESIS_HASH, "event_hash": GENESIS_HASH,
                "causal_event": {
                    "emitter": "laboratory", "kind": "stage12_subjective_agency_judgement",
                    "t_monde": 2, "attempt_ref": captured["attempt_ref"],
                    "data": {"agency": "self", "outcome": "success"},
                },
            })
            forged = _rechain(rows)
            self.assertEqual(audit_export_bytes(forged).world_steps_closed, 5)
            with self.assertRaisesRegex(ValueError, "uncontracted subjective agency source"):
                audit_stage12_attribution_provenance(forged)


if __name__ == "__main__":
    unittest.main()
