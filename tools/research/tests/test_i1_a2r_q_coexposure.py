"""Pure signed-occurrence coexposure adversarial fixtures: never birth I1."""
import copy
import unittest

from i1_a2r_q_coexposure import summarize_paid_q_coexposure


def fixture():
    events = []
    obs = []
    for option, status, q, evidence in (("a","learned",0.5,0.4),
                                        ("b","learned",-0.2,0.1)):
        data={"option_ref":option,"learning_signature":"sig:"+option,
              "learned_value_status":status,"learned_value":q,
              "status":"evaluated","evidence":evidence}
        events.append({"kind":"stage8_option_evaluation","t_monde":2,
                       "cycle":1,"data":data})
        obs.append({"step":2,"cycle":1,"option":option,"signature":"sig:"+option,
                    "status":status,"q":q})
    events.append({"kind":"competition_cycle","t_monde":2,"cycle":1,
                   "data":{"traces":[
                       {"option_ref":"a","evidence":0.4,"crossed":True,
                        "accumulator_before":0,"accumulator_after":0.6,
                        "threshold":0.5},
                       {"option_ref":"b","evidence":0.1,"crossed":False,
                        "accumulator_before":0,"accumulator_after":0.2,
                        "threshold":0.5}]}})
    q={"scope":"A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3",
       "full_q_replay_verified":True,"adaptive_learning_go":"NOT_ESTABLISHED",
       "stage8_observations":obs,"stage8_read_count":2}
    control={"scope":"A2R_COLD_NATIVE_ACTION_CONTROL_PATH_NOT_L3",
             "all_motor_receipts_matched":True,
             "native_crossing_and_rank_prefix_consistent":True,
             "admitted_decision_occurrences":[{"step":2,"cycle":1,
                                               "option":"a"}],
             "native_q_decisions_joined_to_admission":1,
             "nondecision_motor_sources":0}
    stage8={"scope":"A2R_STAGE8_NATIVE_EVIDENCE_RECONSTRUCTED_NOT_L3",
            "same_full_m11_q_replay":True,
            "stage8_evaluations_recomputed":2,
            "stage8_other_evaluations_unreplayed":0,
            "unreplayed_evaluations":[]}
    local={"scope":"A2R_NATIVE_LOCAL_AFFORDANCE_ARITHMETIC_NOT_L3",
           "verified_evaluations":[],
           "native_local_affordance_recomputed":0}
    return events,q,control,stage8,local


class CoexposureTests(unittest.TestCase):
    def call(self, parts):
        e,q,c,s,l=parts
        return summarize_paid_q_coexposure(e,q_replay=q,controller=c,
                                            stage8=s,local=l)

    def test_two_learned_candidates_one_physical_admission_not_l3(self):
        result=self.call(fixture())
        self.assertEqual(result["paid_cycles_with_two_learned_q_candidates"],1)
        self.assertEqual(result["paid_cycles_with_two_formula_checked_learned_candidates"],1)
        self.assertEqual(result["physically_admitted_crossed_learned_q_options"],1)
        self.assertFalse(result["Q_to_action_counterfactual_proven"])
        self.assertFalse(result["study_admissible"])

    def test_single_learned_competitor_is_not_two(self):
        parts=fixture()
        parts[1]["stage8_observations"][1].update(status="unlearned",q=None)
        parts[0][1]["data"].update(learned_value_status="unlearned",
                                     learned_value=None)
        result=self.call(parts)
        self.assertEqual(result["paid_cycles_with_two_learned_q_candidates"],0)
        self.assertEqual(result["cycle_classifications"][
            "LEARNED_Q_WITH_NONLEARNED_ALTERNATIVE"],1)

    def test_reject_tampered_q_evidence_admission_and_family(self):
        for mutation in ("q","evidence","admitted","unreplayed","duplicate"):
            parts=copy.deepcopy(fixture())
            events,q,c,s,l=parts
            if mutation=="q":
                events[0]["data"]["learned_value"]=7.0
            elif mutation=="evidence":
                events[-1]["data"]["traces"][0]["evidence"]=0.7
            elif mutation=="admitted":
                c["admitted_decision_occurrences"][0]["option"]="forged"
            elif mutation=="unreplayed":
                s["unreplayed_evaluations"]=[{"step":2,"cycle":1,"option":"a"}]
                s["stage8_evaluations_recomputed"]=1
                s["stage8_other_evaluations_unreplayed"]=1
                l["verified_evaluations"]=[{"step":2,"cycle":1,"option":"forged"}]
                l["native_local_affordance_recomputed"]=1
            elif mutation=="duplicate":
                events.insert(0,copy.deepcopy(events[0]))
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                self.call(parts)


if __name__=="__main__":
    unittest.main()
