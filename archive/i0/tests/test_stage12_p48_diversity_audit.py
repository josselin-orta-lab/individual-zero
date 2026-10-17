"""Read-only A2.5 independent census: never convert P-48 into causal truth."""
from copy import deepcopy
import unittest

from lab.stage12_p48_diversity_audit import summarize_stage12_p48_diversity_events


def _life():
    signal = "exploration:frontier:frontier:3:2:from:2:2:t1"
    return [
        {"kind": "perceptual_capture", "t_monde": 1,
         "data": {"position": {"x": 2, "y": 2}}},
        {"kind": "stage11_intrinsic_evaluation", "t_monde": 1, "cycle": 2,
         "data": {"option_ref": "autonomous", "signal_ids": [signal],
                  "intrinsic_value": {"$f64": "0x1.0000000000000p-1"}}},
        {"kind": "stage11_intrinsic_evaluation", "t_monde": 1, "cycle": 2,
         "data": {"option_ref": "goal", "signal_ids": [signal],
                  "intrinsic_value": {"$f64": "0x1.0000000000000p-1"}}},
        {"kind": "command_experienced", "t_monde": 1, "attempt_ref": "s1",
         "primitive": "se_deplacer", "parameters": {"direction": "east"}},
        {"kind": "world_transition_experienced", "t_monde": 1,
         "attempt_ref": "s1", "position_after": {"x": 3, "y": 2},
         "body_after": {"food": {"$f64": "0x1.8000000000000p+4"}},
         "effects": {"movement": "moved"}},
        {"kind": "command_experienced", "t_monde": 2, "attempt_ref": "s2",
         "primitive": "manger", "parameters": {"target": "berry_a"}},
        {"kind": "world_transition_experienced", "t_monde": 2,
         "attempt_ref": "s2", "position_after": {"x": 3, "y": 2},
         "body_after": {"food": {"$f64": "0x1.e000000000000p+4"}},
         "effects": {"ate": "berry_a"}},
    ]


class A25IndependentSignalAndBodyCensus(unittest.TestCase):
    def test_two_options_same_frontier_share_one_information_source(self):
        actual = summarize_stage12_p48_diversity_events(_life())
        self.assertEqual(actual["world_steps"], 2)
        self.assertEqual(actual["physically_distinct_sites"], 2)
        self.assertEqual(actual["confirmed_moves"], 1)
        self.assertEqual(actual["physically_confirmed_eats"], 1)
        self.assertEqual(actual["net_food_increase_steps_after_first"], 1)
        self.assertEqual(actual["distinct_p48_source_signals"], 1)
        self.assertEqual(actual["cross_option_shared_signal_groups"], 1)
        self.assertEqual(actual["equal_numeric_interest_groups"], 1)
        self.assertFalse(actual["subjective_agency_inferred_from_p48"])

    def test_within_option_repetition_is_refused(self):
        raw = _life()
        raw[1]["data"]["signal_ids"] *= 2
        with self.assertRaisesRegex(ValueError, "repeats"):
            summarize_stage12_p48_diversity_events(raw)

    def test_same_numeric_interest_different_sources_not_claimed_causal(self):
        raw = _life()
        raw[2]["data"]["signal_ids"] = ["exploration:other-frontier:t1"]
        actual = summarize_stage12_p48_diversity_events(raw)
        self.assertEqual(actual["distinct_p48_source_signals"], 2)
        self.assertEqual(actual["cross_option_shared_signal_groups"], 0)
        self.assertEqual(actual["equal_numeric_interest_groups"], 1)

    def test_body_gain_without_eating_is_not_ingestion(self):
        raw = _life()
        raw[5]["primitive"] = "attendre"
        raw[5]["parameters"] = {}
        raw[6]["effects"] = {"rest": "attendre"}
        actual = summarize_stage12_p48_diversity_events(raw)
        self.assertEqual(actual["attempted_eats"], 0)
        self.assertEqual(actual["physically_confirmed_eats"], 0)
        self.assertEqual(actual["net_food_increase_steps_after_first"], 1)

    def test_spatial_gain_without_body_gain_is_not_feeding(self):
        raw = _life()
        raw[5]["primitive"] = "attendre"
        raw[5]["parameters"] = {}
        raw[6]["effects"] = {"rest": "attendre"}
        raw[6]["body_after"]["food"] = deepcopy(raw[4]["body_after"]["food"])
        actual = summarize_stage12_p48_diversity_events(raw)
        self.assertEqual(actual["physically_distinct_sites"], 2)
        self.assertEqual(actual["physically_confirmed_eats"], 0)
        self.assertEqual(actual["net_food_increase_steps_after_first"], 0)

    def test_forged_movement_receipt_rejected(self):
        raw = _life()
        raw[4]["position_after"] = {"x": 2, "y": 2}
        with self.assertRaisesRegex(ValueError, "without displacement"):
            summarize_stage12_p48_diversity_events(raw)

    def test_noncanonical_duplicate_world_step_rejected(self):
        raw = _life()
        raw.append(deepcopy(raw[6]))
        with self.assertRaisesRegex(ValueError, "duplicate physical"):
            summarize_stage12_p48_diversity_events(raw)

    def test_p48_options_in_one_cycle_are_unique(self):
        raw = _life()
        raw.append(deepcopy(raw[1]))
        with self.assertRaisesRegex(ValueError, "per-cycle"):
            summarize_stage12_p48_diversity_events(raw)

    def test_missing_physical_step_rejected(self):
        raw = _life()
        raw[5]["t_monde"] = 3
        raw[6]["t_monde"] = 3
        with self.assertRaisesRegex(ValueError, "noncontiguous"):
            summarize_stage12_p48_diversity_events(raw)


if __name__ == "__main__":
    unittest.main()
