"""Adversarial pure Action Control M11 join; no living I1 birth."""
import copy
import unittest
from unittest.mock import patch
from i1_a2r_control_cold import audit_native_action_control

HASH="a"*64
def fixture():
    common={"t_monde":1,"attempt_ref":"attempt-1"}
    competition=dict(common,kind="competition_cycle",cycle=1,
        data={"traces":[{"option_ref":"permanent:attendre","crossed":True}]})
    admission=dict(common,kind="command_admitted",
        data={"source":"decision","primitive":"attendre",
              "command_hash":HASH,"policy_version":"mvp-v1.2.1",
              "option_ref":"permanent:attendre","reason":None,
              "scope":None,"rule_id":None,"rule_type":None})
    experienced=dict(common,kind="command_experienced",
                     primitive="attendre",command_hash=HASH)
    replay={"scope":"A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3",
            "full_q_replay_verified":True,"adaptive_learning_go":"NOT_ESTABLISHED",
            "birth_source_provenance_verified":False,"m11_identity":"life",
            "mode":"CANONICAL_ABS","generation":1,"status":"active",
            "decisions":[{"step":1,"cycle":1,"option":"permanent:attendre"}]}
    birth={"scope":"SOURCE_RECONSTRUCTED_ZERO_STEP_REFERENCE_NOT_NEW_LIFE",
           "q_at_birth_empty":True,"identity":"life","mode":"CANONICAL_ABS",
           "action_control_policy_version":"mvp-v1.2.1"}
    return [competition,admission,experienced],replay,birth

def invoke(events,replay,birth):
    with patch("i1_a2r_control_cold.physical_steps",
               return_value=[{"step":1,"action":"attendre"}]):
        return audit_native_action_control(events,q_replay=replay,birth=birth)

class ControlTests(unittest.TestCase):
    def test_exact_admission_not_causal_go(self):
        e,q,b=fixture()
        x=invoke(e,q,b)
        self.assertEqual(x["physical_experiences_with_prior_admission"],1)
        self.assertEqual(len(x["admitted_decision_occurrences"]),1)
        self.assertFalse(x["Q_to_action_counterfactual_proven"])
        self.assertFalse(x["study_admissible"])
    def test_each_tampering_fails(self):
        for attack in ("wrong_hash","wrong_attempt","wrong_policy","late_competition",
                       "late_veto","wrong_primitive","forged_source","missing_admission",
                       "duplicate_admission","wrong_decision","invalid_sha"):
            e,q,b=fixture()
            if attack=="wrong_hash":e[-1]["command_hash"]="b"*64
            elif attack=="wrong_attempt":e[1]["attempt_ref"]="other"
            elif attack=="wrong_policy":e[1]["data"]["policy_version"]="other"
            elif attack=="late_competition":e=[e[1],e[0],e[2]]
            elif attack=="late_veto":
                veto=copy.deepcopy(e[1])
                veto["kind"]="command_vetoed"
                veto["data"].update(reason="protocol_mask",scope="protocol",
                    rule_id="rollback_sequence_mask",rule_type="protocol")
                e.insert(2,veto)
            elif attack=="wrong_primitive":e[1]["data"]["primitive"]="boire"
            elif attack=="forged_source":e[1]["data"]["source"]="oracle"
            elif attack=="missing_admission":e.pop(1)
            elif attack=="duplicate_admission":e.insert(2,copy.deepcopy(e[1]))
            elif attack=="wrong_decision":q["decisions"][0]["option"]="other"
            elif attack=="invalid_sha":e[1]["data"]["command_hash"]="a"
            with self.subTest(attack=attack), self.assertRaises(ValueError):
                invoke(e,q,b)
if __name__=="__main__":
    unittest.main()
