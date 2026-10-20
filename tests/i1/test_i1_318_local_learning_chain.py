"""Synthetic temporal joins are not population or physical certificates."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location("learning318",ROOT/"tools/audit_i1_318_local_learning_chain.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def ev(kind,t,data=None,attempt="a",**extra):
    return dict(kind=kind,t_monde=t,attempt_ref=attempt,data=data or {},**extra)

class TemporalEvidenceTests(unittest.TestCase):
    def test_empty_not_causal(self):
        observed=m.observe([],treatment=True)
        self.assertEqual(observed["counts"],{})
        self.assertFalse(observed["causal_learning_proven"])

    def test_control_cannot_propose_independent_local(self):
        with self.assertRaises(ValueError):
            m.observe([ev("i1_local_opportunity_proposed",1,{
                "option_ref":"option:i1:local:one",
                "learning_signature":"i1:affordance:boire:here"
            })],treatment=False)

    def test_unexecuted_proposal_is_not_learning(self):
        observed=m.observe([ev("i1_local_opportunity_proposed",1,{
            "option_ref":"option:i1:local:t1:boire:here",
            "learning_signature":"i1:affordance:boire:here"
        })],treatment=True)
        self.assertEqual(observed["counts"],{})
        self.assertFalse(observed["causal_learning_proven"])

    def test_no_benefit_assumed_without_capture(self):
        sig="i1:affordance:boire:here"
        option="option:i1:local:t1:boire:here"
        events=[
            ev("i1_local_opportunity_proposed",1,{
                "option_ref":option,"learning_signature":sig,
                "command":{"primitive":"boire","parameters":{}}}),
            ev("competition_cycle",1,{"traces":[{"option_ref":option,"crossed":True}]}),
            ev("command_admitted",1,{"option_ref":option,"source":"decision",
                                     "command_hash":"h"}),
            ev("command_experienced",1,primitive="boire",
               command_hash="h",emitter="action_control"),
            ev("world_transition_experienced",1,body_after={
                "water":90,"food":90,"energy":90,"integrity":90}),
        ]
        result=m.observe(events,treatment=True)
        self.assertEqual(result["counts"]["local_physical_actions"],1)
        self.assertEqual(result["counts"]["lacks_prior_first_person_body_capture"],1)
        self.assertFalse(result["body_delta_causally_attributed_to_action"])

if __name__=="__main__":
    unittest.main()
