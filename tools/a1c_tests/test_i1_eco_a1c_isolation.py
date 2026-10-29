"""A1-C: 48 frozen independent M11 identities and no A1-P reuse."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_i1_eco_a1c import IDENTITIES, MATRIX, SEEDS, SCHEMA, _PROGRAM
from i1_eco_a1c_mechanism import verify_mechanism

class ConfirmatoryIsolation(unittest.TestCase):
    def test_registered_48_distinct_opaque_births(self):
        self.assertEqual(len(MATRIX),48)
        self.assertEqual(len(set(IDENTITIES.values())),48)
        self.assertEqual(SEEDS,tuple(range(101,113)))
        self.assertTrue(all(v.startswith("i1:eco:a1c:confirmatory:")
                            for v in IDENTITIES.values()))
        self.assertTrue(all("pilot" not in v for v in IDENTITIES.values()))
        self.assertIn("confirmatory-fragment",SCHEMA)
        self.assertIn("a1c_matched_temperament_birth",_PROGRAM)
        self.assertIn("from run_i1_eco_a1c import",_PROGRAM)
        self.assertNotIn("from run_i1_eco_a1 import",_PROGRAM)

    def test_observer_cannot_claim_benefit_without_motor_change(self):
        out=verify_mechanism(
            canonical_events=[], masked_events=[],
            masked_reads=[],adapters=[],
            canonical_prefix=[{"primitive":"attendre"}],
            masked_prefix=[{"primitive":"attendre"}],
            first_masked_step=None)
        self.assertFalse(out["mechanism_exposed"])
        self.assertEqual(out["reason"],"NOT_EXPOSED")

    def test_m11_anchored_learned_read_and_real_competition_with_motor_change(self):
        read = {"step": 1, "cycle": 1, "signature": "primitive:attendre",
                "source": "stage8_direct", "option_ref": "opt",
                "original_status": "learned", "masked": True}
        c = [
            {"kind": "stage8_option_evaluation", "t_monde": 1, "cycle": 1,
             "data": {"option_ref": "opt", "status": "evaluated",
                      "learning_signature": "primitive:attendre",
                      "learned_value_status": "learned"}},
            {"kind": "stage8_option_evaluation", "t_monde": 1, "cycle": 1,
             "data": {"option_ref": "other", "status": "evaluated",
                      "learning_signature": "primitive:boire"}},
            {"kind": "competition_cycle", "t_monde": 1, "cycle": 1,
             "data": {"traces": [{"option_ref": "opt"},
                                 {"option_ref": "other"}]}}
        ]
        from copy import deepcopy
        m = deepcopy(c)
        m[0]["data"]["learned_value_status"] = "unlearned"
        outcome = verify_mechanism(
            canonical_events=c, masked_events=m, masked_reads=[read],
            adapters=[], canonical_prefix=[{"primitive": "boire"}],
            masked_prefix=[{"primitive": "attendre"}], first_masked_step=1)
        self.assertTrue(outcome["mechanism_exposed"])
        self.assertEqual(outcome["reason"],
                         "M11_LINKED_COMPETITIVE_Q_TO_MOTOR")
        with self.assertRaises(ValueError):
            verify_mechanism(
                canonical_events=c, masked_events=m, masked_reads=[read],
                adapters=[], canonical_prefix=[{"primitive":"boire"}],
                masked_prefix=[{"primitive":"attendre"}],
                first_masked_step=2)

    def test_strong_q_observer_without_competitors_is_not_exposure(self):
        read={"step":1,"cycle":1,"signature":"primitive:attendre",
              "source":"stage8_direct", "option_ref":"opt",
              "original_status":"learned","masked":True}
        c=[{"kind":"stage8_option_evaluation","t_monde":1,"cycle":1,
            "data":{"option_ref":"opt","status":"evaluated",
                    "learning_signature":"primitive:attendre"}}]
        m=c+[{"kind":"competition_cycle","t_monde":1,"cycle":1,
              "data":{"traces":[{"option_ref":"opt"}]}}]
        out=verify_mechanism(
            canonical_events=c,masked_events=m,masked_reads=[read],
            adapters=[],canonical_prefix=[{"primitive":"boire"}],
            masked_prefix=[{"primitive":"attendre"}],
            first_masked_step=1)
        self.assertFalse(out["mechanism_exposed"])
        self.assertEqual(out["reason"],"NO_COMPETITIVE_M11_CHAIN")

if __name__ == "__main__":
    unittest.main()
