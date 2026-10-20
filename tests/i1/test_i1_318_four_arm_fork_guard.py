"""Adversarial first-person / Q provenance controls for certified first forks."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location(
    "fork318",ROOT/"tools/audit_i1_318_matched_four_arm_first_fork.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class FourArmGuards(unittest.TestCase):
    def test_prior_td_required_and_same_signature(self):
        events=[
            {"kind":"td_update_published",
             "data":{"updated_signatures":["i1:affordance:boire:here"]}},
            {"kind":"i1_local_opportunity_proposed","data":{}},
        ]
        self.assertTrue(m.q_signature_is_prior_lived(
            events,proposal_index=1,signature="i1:affordance:boire:here"))
        self.assertFalse(m.q_signature_is_prior_lived(
            events,proposal_index=1,signature="i1:affordance:manger:here"))
        self.assertFalse(m.q_signature_is_prior_lived(
            events,proposal_index=0,signature="i1:affordance:boire:here"))

    def test_no_physical_divergence_is_not_positive_evidence(self):
        def trace():
            return (
                {1:{"primitive":"boire","parameters":{}}},
                {1:{"body_after":{"water":40},"position_after":{"x":1},
                    "effects":{}}},
                {1:{"capture_t_monde":1,"position":{"x":1},
                    "adjacent_creature_count":0}},
            )
        out=m.first_fork({a:trace() for a in m.ARMS})
        self.assertIsNone(out["first_motor_fork_step"])
        self.assertFalse(out["prior_physical_states_agree"])

    def test_reject_unexpected_first_person_schema(self):
        self.assertIn("adjacent_creature_count",m.REQUIRED_CAPTURE_FIELDS)
        self.assertIn("agency_visible_adjacent",m.REQUIRED_CAPTURE_FIELDS)

if __name__=="__main__":
    unittest.main()
