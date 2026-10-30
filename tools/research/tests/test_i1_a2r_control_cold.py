"""Adversarial pure Action Control M11 join; no living I1 birth."""
import copy
import unittest
from unittest.mock import patch
from i1_a2r_control_cold import audit_native_action_control

HASH="a"*64
def fixture():
    common={"t_monde":1,"attempt_ref":"attempt-1"}
    competition=dict(common,kind="competition_cycle",cycle=1,
        data={"traces":[{"option_ref":"permanent:attendre","crossed":True,"accumulator_before":0.0,"accumulator_after":1.0,"threshold":1.0,"evidence":0.5}]})
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
            "decisions":[{"step":1,"cycle":1,"option":"permanent:attendre"}],
            "stage8_observations":[{"step":1,"cycle":1,"option":"permanent:attendre",
                                     "signature":"primitive:attendre"}]}
    birth={"scope":"SOURCE_RECONSTRUCTED_ZERO_STEP_REFERENCE_NOT_NEW_LIFE",
           "q_at_birth_empty":True,"identity":"life","mode":"CANONICAL_ABS",
           "action_control_policy_version":"mvp-v1.2.1",
           "competition_calibration":{"urgency_max":1.0,"urgency_scale_cycles":1.0,
               "leak":0.0,"gain":2.0,"noise_sigma":0.0,
               "base_threshold":1.0,"threshold_floor":0.5,"inertia":0.0}}
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
        self.assertEqual(x["native_accumulator_equations_verified"],1)
    def test_ranked_veto_then_admission(self):
        e,q,b=fixture()
        second=copy.deepcopy(e[0]["data"]["traces"][0])
        second.update(option_ref="candidate:b", accumulator_after=1.5, evidence=0.75)
        e[0]["data"]["traces"].append(second)
        q["stage8_observations"].append(
            {"step":1,"cycle":1,"option":"candidate:b","signature":"b"})
        veto=copy.deepcopy(e[1])
        veto["kind"]="command_vetoed"
        veto["data"].update(option_ref="candidate:b",reason="known_toxic_item",
                            scope="option",rule_id="toxic_item_consumption",
                            rule_type="semantic_prohibition")
        e.insert(1,veto)
        audited=invoke(e,q,b)
        self.assertEqual(audited["crossed_ranked_control_attempts"],2)
        self.assertTrue(audited["native_rank_is_not_independent_state_replay"])
        e[0]["data"]["traces"][0].update(accumulator_after=1.5, evidence=0.75)
        e[0]["data"]["traces"][1].update(accumulator_after=1.0, evidence=0.5)
        with self.assertRaisesRegex(ValueError,"higher-ranked"):
            invoke(e,q,b)

    def test_missing_or_forged_rank_provenance_fails(self):
        for attack in ("missing_candidate","false_cross","wrong_margin","wrong_recurrence",
                       "wrong_threshold","noncanonical_float","negative",
                       "unevaluated_mutated"):
            e,q,b=fixture()
            tr=e[0]["data"]["traces"][0]
            if attack=="missing_candidate":
                q["stage8_observations"]=[]
            elif attack=="false_cross":tr["crossed"]=False
            elif attack=="wrong_margin":tr["accumulator_after"]=0.3
            elif attack=="wrong_recurrence":tr["accumulator_after"]=1.1
            elif attack=="wrong_threshold":tr["threshold"]=0.0
            elif attack=="noncanonical_float":
                tr["accumulator_after"]={"$f64":"0X1.0000000000000P+0"}
            elif attack=="negative":tr["accumulator_before"]=-1.0
            elif attack=="unevaluated_mutated":
                tr.update(evidence=None,crossed=False,accumulator_after=1.0)
            with self.subTest(attack=attack),self.assertRaises(ValueError):
                invoke(e,q,b)

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
