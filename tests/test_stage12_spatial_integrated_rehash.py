"""Real autonomous Stage12 integration and rehashed forgery resistance.

Six physical steps in a preregistered food-free context give one genuine
spatial goal and Action Control judgement. This is a SOFTWARE regression,
not a statistical replication or proof of universal causal truth.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_stage12_issue110_first_planning_state as trial

from lab.determinism import canonical_causal_bytes
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import GENESIS_HASH
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs


def rechain(rows):
    previous = GENESIS_HASH
    for index, row in enumerate(rows):
        row["index"] = index
        row["previous_hash"] = previous
        previous = sha256(bytes.fromhex(previous) + canonical_causal_bytes({
            "event_id": row["event_id"], "causal_event": row["causal_event"],
        })).hexdigest()
        row["event_hash"] = previous
    return b"\n".join(canonical_causal_bytes(row) for row in rows)


class GenuineAutonomousSpatialEvidenceTests(unittest.TestCase):
    def test_lived_spatial_success_and_adversarial_rehash(self):
        old_limit = trial.MAX_STEPS
        try:
            trial.MAX_STEPS = 6
            with TemporaryDirectory() as directory:
                folder = Path(directory)
                life = trial.run_life(
                    folder, "near_food_free", 70.0, "horizon_three",
                )
                self.assertIsNone(life["audit_error"], life["audit_error"])
                self.assertEqual(life["executed_steps"], 6)
                raw = (folder / "canonical.jsonl").read_bytes()
                receipts = [json.loads(line) for line in raw.splitlines()]
                goal = audit_stage12_goal_progress(raw)
                self.assertEqual(goal.spatial_preregistered, 1)
                self.assertEqual(goal.spatial_verified_progress, 1)
                self.assertEqual(goal.as_dict()["verified_spatial_progress"], 1)
                self.assertEqual(
                    goal.as_dict()["verified_one_step_resource_gains"], 1,
                )
                agency = audit_stage12_first_person_agency(raw)
                self.assertGreaterEqual(agency.judgements_self, 1)
                pairs = audit_stage12_attribution_pairs(raw)
                self.assertGreaterEqual(pairs.admitted_pairs, 1)

                forged = json.loads(json.dumps(receipts))
                frozen = next(row["causal_event"]["data"] for row in forged
                              if row["causal_event"]["kind"]
                              == "stage12_goal_progress_preregistered"
                              and row["causal_event"]["data"]["measure"]
                              == "spatial_distance")
                frozen["target_x"] += 1
                altered = rechain(forged)
                self.assertEqual(
                    audit_export_bytes(altered).world_steps_closed, 6,
                )
                with self.assertRaises(ValueError):
                    audit_stage12_goal_progress(altered)

                forged = json.loads(json.dumps(receipts))
                frozen = next(row["causal_event"]["data"] for row in forged
                              if row["causal_event"]["kind"]
                              == "stage12_goal_agency_precommitted"
                              and row["causal_event"]["data"]["mechanism"]
                              == "witnessed_goal_spatial_target_v1")
                frozen["spatial_prepassable"] = False
                altered = rechain(forged)
                self.assertEqual(
                    audit_export_bytes(altered).world_steps_closed, 6,
                )
                with self.assertRaises(ValueError):
                    audit_stage12_first_person_agency(altered)
        finally:
            trial.MAX_STEPS = old_limit


if __name__ == "__main__":
    unittest.main()
