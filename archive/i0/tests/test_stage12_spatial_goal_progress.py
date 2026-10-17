"""GA-SPATIAL-01 bounded criterion regression, *not* autonomous evidence."""
from dataclasses import replace
import unittest

from i0.modules.stage12_goal_progress import (
    LivedSpatialGoalIntent, Stage12GoalProgressLedger,
    SPATIAL_CONTRACT_VERSION,
)


def intent(ref="intent:spatial:1", step=1):
    return LivedSpatialGoalIntent(
        intent_ref=ref, goal_ref="goal:food", option_ref="opt:move",
        command_hash="hash:action", measure="spatial_distance",
        value_before=1.0, sent_world_step=step,
        observe_world_step=step+1, life_id="life:one",
        start_x=2, start_y=2, target_x=3, target_y=2,
        target_kind="berry_a", direction="east",
    )


class SpatialGoalProgressTests(unittest.TestCase):
    def test_success_only_from_later_observed_position(self):
        ledger = Stage12GoalProgressLedger()
        ledger.preregister(intent())
        result = ledger.followup(world_step=2, body={"food": 10},
                                 position=(3, 2))
        self.assertEqual(result.criterion_outcome, "success")
        self.assertEqual(result.value_after, 0.0)
        self.assertEqual(result.contract_version, SPATIAL_CONTRACT_VERSION)

    def test_non_progress_does_not_imply_world_agency(self):
        ledger = Stage12GoalProgressLedger()
        ledger.preregister(intent())
        result = ledger.followup(world_step=2, body={"food": 90},
                                 position=(2, 2))
        self.assertEqual(result.criterion_outcome, "failure")
        self.assertEqual(result.reason, "no_measured_spatial_progress")

    def test_no_perception_is_unknown(self):
        ledger = Stage12GoalProgressLedger()
        ledger.preregister(intent())
        result = ledger.followup(world_step=2, body={"food": 100},
                                 position=None)
        self.assertEqual(result.criterion_outcome, "unknown")

    def test_late_observation_is_unknown(self):
        ledger = Stage12GoalProgressLedger()
        ledger.preregister(intent())
        result = ledger.followup(world_step=3, body={"food": 100},
                                 position=(3, 2))
        self.assertEqual(result.criterion_outcome, "unknown")

    def test_refused_uc_is_unknown(self):
        ledger = Stage12GoalProgressLedger()
        ledger.preregister(intent())
        result = ledger.followup(world_step=2, body={"food": 100},
                                 position=(3, 2), diagnostic_paid=False)
        self.assertEqual(result.criterion_outcome, "unknown")

    def test_no_duplicate_and_cold_import_current_only(self):
        ledger = Stage12GoalProgressLedger()
        ledger.preregister(intent())
        state = ledger.export_causal_state()
        other = Stage12GoalProgressLedger()
        other.restore_causal_state(state)
        self.assertEqual(other.pending, intent())
        with self.assertRaises(ValueError):
            other.restore_causal_state(state)
        self.assertEqual(other.followup(world_step=2, body={},
                                        position=(2, 2)).criterion_outcome, "failure")
        with self.assertRaises(ValueError):
            ledger.preregister(intent(ref="different", step=1))

    def test_bad_target_and_direction_are_refused(self):
        with self.assertRaises(ValueError):
            replace(intent(), target_x=5).validate()
        with self.assertRaises(ValueError):
            replace(intent(), direction="west").validate()
        with self.assertRaises(ValueError):
            replace(intent(), value_before=2.0).validate()

    def test_malformed_position_cannot_mutate_ledger(self):
        ledger = Stage12GoalProgressLedger()
        ledger.preregister(intent())
        with self.assertRaises(ValueError):
            ledger.followup(world_step=2, body={}, position=(True, 2))
        self.assertEqual(ledger.pending, intent())


if __name__ == "__main__":
    unittest.main()
