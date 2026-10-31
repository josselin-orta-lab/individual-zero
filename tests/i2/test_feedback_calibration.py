"""Bounded past-only feedback remains a nonmotor, noncausal study."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.modules.delayed_credit_study import (
    ClaimedLivedStep, MatchedLivedEpisode, ForecastOpportunity,
    project_matched_outcome, empty_feedback_memory, read_feedback,
    learn_from_feedback,
)
def event(t, action, delta):
    return ClaimedLivedStep("life:one",t,f"capture:{t}","goal:one",
                           action,f"admit:{t}",f"evidence:{t}",f"outcome:{t}",delta)
def episode(ref, t, action, result):
    return MatchedLivedEpisode(ref,("context:seen",),
                              (event(t,action,-2),event(t+1,"finish",result)))
class Source:
    def verify_lived(self,*,event): return True
    def verify_complete_episode(self,*,episode): return True
    def verify_forecast_capture(self,*,opportunity): return True
    def verify_issued_forecast(self,*,forecast): return True
    def verify_feedback_issue(self,*,readout): return True
class NoIssue(Source):
    def verify_feedback_issue(self,*,readout): return False
def training():
    return episode("train:prep",1,"prepare",8),episode("train:alt",5,"alternative",1)
def opportunity(t):
    return ForecastOpportunity("life:one","goal:one",f"capture:{t}",t,
                               ("context:seen",),"prepare","alternative","finish")
def heldout(t, prepared_result, control_result):
    return (episode(f"test:prep:{t}",t,"prepare",prepared_result),
            episode(f"test:alt:{t}",t+4,"alternative",control_result))
def forecast(t):
    a,b=training()
    return project_matched_outcome(prepared=a,control=b,
                                  opportunity=opportunity(t),source=Source())
class FeedbackTests(unittest.TestCase):
    def test_later_adverse_outcome_changes_next_prediction_without_rewriting_first(self):
        memory=empty_feedback_memory(opportunity(10))
        first=read_feedback(memory=memory,forecast=forecast(10),source=Source())
        self.assertEqual(first.predicted_outcome_difference,7)
        a,b=heldout(12,-8,4)
        update=learn_from_feedback(memory=memory,readout=first,
                                   prepared=a,control=b,source=Source())
        self.assertEqual(update.heldout_score.observed_outcome_difference,-12)
        self.assertEqual(first.predicted_outcome_difference,7)
        self.assertEqual(memory.observed_differences,())
        second=read_feedback(memory=update.new_memory,forecast=forecast(25),source=Source())
        self.assertEqual(second.predicted_outcome_difference,-12)
        self.assertEqual(second.memory_version,1)
        self.assertEqual(second.motor_authority,"NONE")
        self.assertFalse(update.new_memory.m11_authenticated)
    def test_feedback_can_get_next_result_wrong(self):
        first=read_feedback(memory=empty_feedback_memory(opportunity(10)),
                            forecast=forecast(10),source=Source())
        a,b=heldout(12,-8,4)
        updated=learn_from_feedback(memory=empty_feedback_memory(opportunity(10)),
                                    readout=first,prepared=a,control=b,source=Source())
        second=read_feedback(memory=updated.new_memory,forecast=forecast(25),source=Source())
        p,c=heldout(27,10,0)
        later=learn_from_feedback(memory=updated.new_memory,readout=second,
                                  prepared=p,control=c,source=Source())
        self.assertEqual(later.heldout_score.observed_outcome_difference,10)
        self.assertFalse(later.direction_agreement)
        self.assertEqual(later.new_memory.observed_differences,(-12,10))
        third=read_feedback(memory=later.new_memory,forecast=forecast(40),source=Source())
        self.assertEqual(third.predicted_outcome_difference,-1)
    def test_missing_prior_issuance_or_changed_prediction_refused(self):
        memory=empty_feedback_memory(opportunity(10))
        readout=read_feedback(memory=memory,forecast=forecast(10),source=Source())
        a,b=heldout(12,5,2)
        for bad in (replace(readout,predicted_outcome_difference=42),
                    replace(readout,motor_authority="ADMITTED"),
                    replace(readout,memory_version=1)):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                learn_from_feedback(memory=memory,readout=bad,
                                    prepared=a,control=b,source=Source())
        with self.assertRaises(ValueError):
            learn_from_feedback(memory=memory,readout=readout,
                                prepared=a,control=b,source=NoIssue())
    def test_same_mean_different_histories_have_different_receipts(self):
        from fractions import Fraction
        from i2.modules.delayed_credit_study import OutcomeFeedbackMemory
        op=opportunity(30)
        a=replace(empty_feedback_memory(op),last_observed_step=20,
                  observed_differences=(2,4),
                  used_issue_captures=("capture:11","capture:15"),
                  used_episode_refs=("episode:a","episode:b","episode:c","episode:d"))
        b=replace(a,observed_differences=(1,5))
        first=read_feedback(memory=a,forecast=forecast(30),source=Source())
        second=read_feedback(memory=b,forecast=forecast(30),source=Source())
        self.assertEqual(first.predicted_outcome_difference,Fraction(3))
        self.assertEqual(first.predicted_outcome_difference,second.predicted_outcome_difference)
        self.assertNotEqual(first.memory_digest,second.memory_digest)
        self.assertEqual(len(first.memory_digest),71)
        # A receipt from another equally sized/equally averaged memory
        # must not authorize learning against this snapshot.
        p,c=heldout(32,6,3)
        with self.assertRaisesRegex(ValueError,"changed or reused"):
            learn_from_feedback(memory=b,readout=first,
                                prepared=p,control=c,source=Source())

    def test_identical_values_but_different_provenance_are_not_interchangeable(self):
        op=opportunity(30)
        a=replace(empty_feedback_memory(op),last_observed_step=20,
                  observed_differences=(3,),
                  used_issue_captures=("capture:11",),
                  used_episode_refs=("episode:a","episode:b"))
        b=replace(a,used_episode_refs=("episode:c","episode:d"))
        f=forecast(30)
        ra=read_feedback(memory=a,forecast=f,source=Source())
        rb=read_feedback(memory=b,forecast=f,source=Source())
        self.assertEqual(ra.predicted_outcome_difference,rb.predicted_outcome_difference)
        self.assertNotEqual(ra.memory_digest,rb.memory_digest)

    def test_replay_and_foreign_context_refused(self):
        memory=empty_feedback_memory(opportunity(10))
        first=read_feedback(memory=memory,forecast=forecast(10),source=Source())
        a,b=heldout(12,5,2)
        updated=learn_from_feedback(memory=memory,readout=first,
                                    prepared=a,control=b,source=Source())
        with self.assertRaises(ValueError):
            read_feedback(memory=updated.new_memory,forecast=forecast(10),source=Source())
        with self.assertRaises(ValueError):
            read_feedback(memory=updated.new_memory,forecast=replace(
                forecast(25),opportunity=replace(opportunity(25),
                                                context_signature=("context:foreign",))),
                source=Source())
        later=read_feedback(memory=updated.new_memory,forecast=forecast(25),source=Source())
        with self.assertRaises(ValueError):
            learn_from_feedback(memory=updated.new_memory,readout=later,
                                prepared=a,control=b,source=Source())
if __name__=="__main__": unittest.main()
