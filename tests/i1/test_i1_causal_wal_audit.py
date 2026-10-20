"""Adversarial unit tests: no physical or learning proof without full lineage."""
import importlib.util
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[2]/"tools/audit_i1_causal_wal.py"
SPEC=importlib.util.spec_from_file_location("i1_audit_causal",PATH)
audit=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def event(kind, t=1, data=None, **kwargs):
    return {"kind":kind,"t_monde":t,"data":data or {},**kwargs}


class CausalWalAuditTests(unittest.TestCase):
    def test_reject_missing_physical_transition(self):
        events=[event("command_experienced",emitter="action_control",
                      primitive="attendre"),
                event("step_closed",data={"outcome":"normal",
                      "applied_command_count":1,"world_advance_count":1})]
        with self.assertRaises(ValueError):
            audit.classify(events)

    def test_td_must_precede_personal_learned_local_proposal(self):
        candidate={"option_ref":"option:i1:local:test",
                   "learning_signature":"i1:affordance:touch:test",
                   "learned_value_status":"learned"}
        report=audit.classify([event("i1_local_opportunity_proposed",data=candidate)])
        self.assertEqual(report["learned_local_proposals_without_prior_personal_TD"],1)
        prior=audit.classify([
            event("td_update_published",t=1,data={
                "updated_signatures":["i1:affordance:touch:test"]}),
            event("i1_local_opportunity_proposed",t=2,data=candidate)])
        self.assertEqual(prior["learned_local_proposals_with_prior_personal_TD"],1)
        self.assertFalse(prior["claim_of_survival_improvement"])

    def test_cannot_claim_motor_for_only_evaluation(self):
        events=[event("i1_local_opportunity_proposed",
                      data={"option_ref":"option:i1:local:test"}),
                event("i1_local_opportunity_registration",data={
                    "option_ref":"option:i1:local:test","registered":True}),
                event("stage8_option_evaluation",data={
                    "option_ref":"option:i1:local:test"})]
        report=audit.classify(events)
        self.assertEqual(report["local_physical_decision_chain_proven"],0)

    def test_irreversible_death(self):
        events=[]
        for step,dead in ((1,True),(2,False)):
            events.extend([
                event("command_experienced",t=step,emitter="action_control",primitive="attendre"),
                event("world_transition_experienced",t=step),
                event("step_closed",t=step,data={"outcome":"dead" if dead else "normal",
                   "applied_command_count":1,"world_advance_count":1})])
        with self.assertRaises(ValueError):
            audit.classify(events)

if __name__=="__main__":
    unittest.main()
