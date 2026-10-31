"""Fail-closed synthetic chain from claimed physical effects to H2 credit."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.modules.delayed_credit_study import (
    ClaimedLivedStep, PhysicalEffectClaim, study_physically_linked_credit,
)
def event(step):
    return ClaimedLivedStep("life:test",step,f"capture:{step}","goal:test",
        f"action:{step}",f"admit:{step}",f"subjective:{step}",f"outcome:{step}",step)
def effect(step):
    return PhysicalEffectClaim("life:test","I2",f"admit:{step}",f"action:{step}",
        step-1,step,f"state:{step-1}",f"state:{step}",f"commit:{step}",False)
class Proof:
    def __init__(self,physical=True,subjective=True):
        self.physical,self.subjective=physical,subjective
    def verify_committed_effect(self,*,effect):return self.physical
    def verify_subjective_after(self,*,event,effect):return self.subjective
class LinkedTests(unittest.TestCase):
    def test_complete_chain_allows_only_synthetic_association(self):
        result=study_physically_linked_credit(
            events=(event(1),event(2)),effects=(effect(1),effect(2)),authority=Proof())
        self.assertEqual(result.study.observed_steps,2)
        self.assertEqual(len(result.correspondences),2)
        self.assertEqual(result.motor_authority,"NONE")
        self.assertFalse(result.m11_authenticated)
    def test_no_partial_credit_on_missing_or_unverified_effect(self):
        e=(event(1),event(2));p=(effect(1),effect(2))
        for effects,authority in ((p[:1],Proof()),(p,Proof(False)),(p,Proof(True,False))):
            with self.subTest(effects=effects),self.assertRaises(ValueError):
                study_physically_linked_credit(events=e,effects=effects,authority=authority)
    def test_disconnected_replayed_and_terminal_physics_refused(self):
        e=(event(1),event(2));a,b=effect(1),effect(2)
        cases=((a,replace(b,before_state_ref="state:foreign")),
               (a,replace(b,committed_event_ref=a.committed_event_ref)),
               (a,replace(b,terminal=True)),
               (a,replace(b,generation_ref="I1")),
               (a,replace(b,before_state_ref=b.after_state_ref)))
        for effects in cases:
            with self.subTest(effects=effects),self.assertRaises(ValueError):
                study_physically_linked_credit(events=e,effects=effects,authority=Proof())
    def test_unobserved_outcome_not_inferred_from_physics(self):
        missing=replace(event(2),outcome_ref=None,lived_delta=None)
        with self.assertRaises(ValueError):
            study_physically_linked_credit(
                events=(event(1),missing),effects=(effect(1),effect(2)),authority=Proof())
if __name__=="__main__":unittest.main()
