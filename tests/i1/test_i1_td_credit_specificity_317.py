"""Adversarial negative controls for #317 TD memory action specificity."""
from pathlib import Path
import importlib.util
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location(
    "td_specificity_317",ROOT/"tools/audit_i1_317_td_credit_specificity.py")
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def row(t,sig,q,evidence=0.05):
    return {"kind":"stage8_option_evaluation","t_monde":t,
            "data":{"learning_signature":sig,
                    "learned_value_status":"learned",
                    "learned_value":q,"evidence":evidence}}


class TDMemorySpecificity317Tests(unittest.TestCase):
    target="memory_place_return:sighting:a:2:2"
    other="memory_place_return:sighting:b:3:3"

    def test_only_target_q_may_change(self):
        a=[row(58,self.target,2),row(58,self.other,1),
           row(64,self.target,2.3),row(64,self.other,1,0.1)]
        b=[row(58,self.target,0.2),row(58,self.other,1),
           row(64,self.target,0.3),row(64,self.other,1,0.12)]
        report=audit.contrast_learned_q(a,b,self.target,64)
        self.assertEqual(report["first_target_q_difference_step"],58)
        self.assertEqual(report["non_target_q_differences"],[])
        self.assertEqual(report["non_target_learned_q_compared"],2)
        self.assertEqual(len(report["non_target_evidence_differences_at_divergent_step"]),1)

    def test_unrelated_q_mutation_is_detected(self):
        a=[row(58,self.target,2),row(58,self.other,1)]
        b=[row(58,self.target,0.2),row(58,self.other,3)]
        result=audit.contrast_learned_q(a,b,self.target,64)
        self.assertEqual(len(result["non_target_q_differences"]),1)

    def test_unmatched_candidates_are_not_zeros(self):
        with self.assertRaises(ValueError):
            audit.contrast_learned_q([row(58,self.target,2)],
                                     [row(58,self.other,2)],self.target,64)

    def test_unmatched_predecision_cycle_counts_rejected(self):
        a=[row(58,self.target,2)]
        b=[row(58,self.target,2),row(58,self.target,2)]
        with self.assertRaises(ValueError):
            audit.contrast_learned_q(a,b,self.target,64)

    def test_nonfinite_or_invalid_wal_value_rejected(self):
        with self.assertRaises(ValueError):
            audit.contrast_learned_q([row(58,self.target,{"$f64":"nan"})],
                                     [row(58,self.target,2)],self.target,64)


if __name__=="__main__":
    unittest.main()
