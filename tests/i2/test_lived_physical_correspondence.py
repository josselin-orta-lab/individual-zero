"""Read-only G2 physical evidence gate: rejects forged, stale and terminal claims."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.modules.delayed_credit_study import (
    ClaimedLivedStep, PhysicalEffectClaim, verify_lived_physical_correspondence,
)
def event():
    return ClaimedLivedStep("life:test",2,"capture:after","goal:test",
                           "action:collect","admit:1","subjective:2",
                           "observed:2",-1)
def effect():
    return PhysicalEffectClaim("life:test","generation:test","admit:1",
                               "action:collect",1,2,"state:before",
                               "state:after","commit:2",False)
class Authority:
    def __init__(self,physical=True,subjective=True):
        self.physical=physical
        self.subjective=subjective
        self.calls=[]
    def verify_committed_effect(self,*,effect):
        self.calls.append("physical")
        return self.physical
    def verify_subjective_after(self,*,event,effect):
        self.calls.append("subjective")
        return self.subjective
class CorrespondenceTests(unittest.TestCase):
    def test_matching_claims_remain_nonmotor_non_m11(self):
        port=Authority()
        receipt=verify_lived_physical_correspondence(
            effect=effect(),event=event(),authority=port)
        self.assertEqual(port.calls,["physical","subjective"])
        self.assertEqual(receipt.observed_delta,-1)
        self.assertEqual(receipt.motor_authority,"NONE")
        self.assertFalse(receipt.m11_authenticated)
    def test_reject_mismatched_physical_identity_time_and_action(self):
        a=effect()
        cases=(replace(a,life_ref="life:foreign"),
               replace(a,admission_ref="admit:other"),
               replace(a,command_ref="action:other"),
               replace(a,after_step=3),
               replace(a,before_step=True),
               replace(a,terminal=True),
               replace(a,committed_event_ref="capture:after"))
        for claim in cases:
            with self.subTest(claim=claim),self.assertRaises(ValueError):
                verify_lived_physical_correspondence(
                    effect=claim,event=event(),authority=Authority())
    def test_no_authentication_no_correspondence(self):
        for port in (Authority(False,True),Authority(True,False),
                     Authority(1,True),Authority(True,1),None):
            with self.subTest(port=port),self.assertRaises(ValueError):
                verify_lived_physical_correspondence(
                    effect=effect(),event=event(),authority=port)
    def test_future_cognition_cannot_be_inferred_from_advisory(self):
        # A Competition advice has no physical commit identity or provenance.
        with self.assertRaises(ValueError):
            verify_lived_physical_correspondence(
                effect=None,event=event(),authority=Authority())
if __name__=="__main__":unittest.main()
