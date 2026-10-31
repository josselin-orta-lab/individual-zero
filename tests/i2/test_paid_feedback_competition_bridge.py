"""H2 only influences paid, synthetic Competition advice, never motor rights."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_unified_control_cycle import (LIFE,A,B,C,claim,ObservationPort,Values,Current,Safety)
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture
from i2.modules.delayed_credit_study import (
    ClaimedLivedStep, MatchedLivedEpisode, ForecastOpportunity,
    project_matched_outcome, empty_feedback_memory, PaidFeedbackValuationPort,
)
def event(t,action,delta):
    return ClaimedLivedStep(LIFE,t,f"history:capture:{t}","goal:food",action,
        f"history:admit:{t}",f"history:evidence:{t}",f"history:outcome:{t}",delta)
def episode(ref,t,first,delta):
    return MatchedLivedEpisode(ref,("context:synthetic",),
        (event(t,first,-2),event(t+1,C,delta)))
class Proofs:
    def verify_lived(self,*,event):return True
    def verify_complete_episode(self,*,episode):return True
    def verify_forecast_capture(self,*,opportunity):return True
    def verify_issued_forecast(self,*,forecast):return True
class CountValues(Values):
    def __init__(self,scores=None):
        super().__init__(scores)
        self.evaluation_count=0
    def evaluate_batch(self,*,frame,receipts):
        self.evaluation_count+=1
        return super().evaluate_batch(frame=frame,receipts=receipts)
class BridgeTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.db=Path(temp.name)/"bridge.sqlite"
        self.source=ObservationPort()
        self.current=Current()
        self.safety=Safety()
        self.base=CountValues({A:0,B:2,C:0})
    def make(self,delta,*,capacity=20,control_veto=False):
        c=self.source.add(claim(30,visible=(A,B,C)))
        op=ForecastOpportunity(LIFE,"goal:food",c.capture.ref,30,
                               ("context:synthetic",),A,B,C)
        prepared=episode("history:prepared",1,A,delta)
        alternative=episode("history:alternative",5,B,0)
        f=project_matched_outcome(prepared=prepared,control=alternative,
                                  opportunity=op,source=Proofs())
        port=PaidFeedbackValuationPort(
            claim=c,forecast=f,memory=empty_feedback_memory(op),
            source=Proofs(),baseline=self.base)
        self.safety.veto=control_veto
        fixture=CognitiveCycleFixture.create(
            path=self.db,life_ref=LIFE,synthetic_uc=capacity,
            observation_source=self.source,valuation_source=port,
            current_source=self.current,safety_source=self.safety)
        return fixture,c
    def test_favorable_history_changes_paid_advice_and_keeps_veto(self):
        fixture,c=self.make(8,control_veto=True)
        r=fixture.open(claim=c,semantic_ref=A,evidence_ref="evidence:30",ttl_steps=12)
        self.assertEqual((r.intake_uc,r.competition_uc,r.control_uc),(1,3,1))
        self.assertEqual(r.competition_status,"ADVISORY_ONLY")
        self.assertIsNotNone(r.suggested_candidate_ref)
        self.assertIsNone(r.control_suggested_candidate_ref)
        self.assertEqual(r.motor_authority,"NONE")
        self.assertEqual(fixture.audit()["remaining_synthetic_uc"],15)
        self.assertEqual(self.base.evaluation_count,1)
    def test_adverse_history_can_reverse_suggestion_with_same_uc(self):
        fixture,c=self.make(-8)
        r=fixture.open(claim=c,semantic_ref=A,evidence_ref="evidence:30",ttl_steps=12)
        self.assertEqual((r.intake_uc,r.competition_uc,r.control_uc),(1,3,1))
        self.assertIsNotNone(r.suggested_candidate_ref)
        self.assertEqual(fixture.audit()["remaining_synthetic_uc"],15)
    def test_unfunded_batch_never_reads_feedback_or_values(self):
        fixture,c=self.make(8,capacity=3)
        r=fixture.open(claim=c,semantic_ref=A,evidence_ref="evidence:30",ttl_steps=12)
        self.assertEqual(r.competition_status,"UNFUNDED")
        self.assertEqual(r.competition_uc,0)
        self.assertEqual(self.base.evaluation_count,0)
        self.assertEqual(fixture.audit()["remaining_synthetic_uc"],2)
    def test_ablation_changes_advice_but_not_uc_or_motor_rights(self):
        from i2.modules.option_reconstruction import reconstruct_candidates
        from i2.modules.competition_preview import CompetitionPreview
        from i2.modules.cognitive_cycle_fixture import CycleReceipt
        from dataclasses import fields
        # Paired synthetic lives share a capture and baseline, but use
        # independent SQLite stores; neither run actuates a physical body.
        for delta, expected_semantic in ((8,A),(-8,B),(0,B)):
            with self.subTest(delta=delta):
                self.source=ObservationPort()
                self.base=CountValues({A:0,B:2,C:0})
                self.db=Path(self.db.parent)/f"feedback_{delta}.sqlite"
                f,c=self.make(delta)
                result=f.open(claim=c,semantic_ref=A,
                              evidence_ref="evidence:30",ttl_steps=12)
                self.assertEqual(result.competition_status,"ADVISORY_ONLY")
                self.assertEqual((result.intake_uc,result.competition_uc,result.control_uc),(1,3,1))
                self.assertEqual(result.motor_authority,"NONE")
                self.assertEqual(f.audit()["remaining_synthetic_uc"],15)
                # Audit the actual committed advice rather than inferring
                # the preferred candidate from a non-null receipt.
                import sqlite3,json
                with sqlite3.connect(self.db) as conn:
                    stored=json.loads(conn.execute(
                        "SELECT event_json FROM events WHERE seq=1").fetchone()[0])
                options={entry["candidate_ref"]:entry["semantic_ref"]
                         for entry in stored["frame"]["candidates"]}
                self.assertEqual(options[result.suggested_candidate_ref],expected_semantic)
                self.assertEqual(options[result.control_suggested_candidate_ref],expected_semantic)
                self.assertEqual(len(stored["advice"]["values"]),3)
                self.assertEqual(self.base.evaluation_count,1)

    def test_veto_masks_both_positive_and_negative_feedback(self):
        for delta in (8,-8):
            with self.subTest(delta=delta):
                self.source=ObservationPort()
                self.base=CountValues({A:0,B:2,C:0})
                self.db=Path(self.db.parent)/f"veto_{delta}.sqlite"
                f,c=self.make(delta,control_veto=True)
                r=f.open(claim=c,semantic_ref=A,
                         evidence_ref="evidence:30",ttl_steps=12)
                self.assertEqual(r.control_status,"VETOED")
                self.assertIsNone(r.control_suggested_candidate_ref)
                self.assertEqual(r.motor_authority,"NONE")
                self.assertEqual(f.audit()["remaining_synthetic_uc"],15)

    def test_unrepresentable_half_step_rolls_back_all_uc(self):
        # Exact integer units are required; fractional feedback isn't rounded.
        c=self.source.add(claim(30,visible=(A,B,C)))
        op=ForecastOpportunity(LIFE,"goal:food",c.capture.ref,30,
                               ("context:synthetic",),A,B,C)
        p=episode("history:prepared",1,A,1)
        q=episode("history:alternative",5,B,0)
        f=project_matched_outcome(prepared=p,control=q,opportunity=op,source=Proofs())
        from dataclasses import replace
        from fractions import Fraction
        from i2.modules.delayed_credit_study import OutcomeFeedbackMemory
        mem=replace(empty_feedback_memory(op),last_observed_step=8,
             observed_differences=(0,1),used_issue_captures=("historic:1","historic:2"),
             used_episode_refs=("e1","e2","e3","e4"))
        port=PaidFeedbackValuationPort(claim=c,forecast=f,memory=mem,
                                     source=Proofs(),baseline=self.base)
        fixture=CognitiveCycleFixture.create(path=self.db,life_ref=LIFE,
            synthetic_uc=20,observation_source=self.source,valuation_source=port,
            current_source=self.current,safety_source=self.safety)
        with self.assertRaisesRegex(ValueError,"fractional"):
            fixture.open(claim=c,semantic_ref=A,evidence_ref="evidence:30",ttl_steps=12)
        self.assertEqual(fixture.audit()["remaining_synthetic_uc"],20)
        self.assertEqual(fixture.audit()["committed"],0)
        self.assertEqual(self.base.evaluation_count,0)
if __name__=="__main__": unittest.main()
