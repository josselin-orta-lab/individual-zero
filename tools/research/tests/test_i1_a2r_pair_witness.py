"""Fail-closed, synthetic pair chronology. Never a cohort birth."""
import unittest
from i1_a2r_pair_witness import compare_pair

def pair(mode, q=0.1, evidence=.2, action="attendre", td=1.):
    events=[]
    for t in (1,2,3):
        before=dict(energy=80.,food=50.,water=48.,integrity=100.)
        after=dict(before,water=48.+t)
        opt="permanent:attendre" if action=="attendre" or t<3 else "option:boire"
        options=["permanent:attendre"] if t<3 else ["permanent:attendre","option:boire"]
        for o in options:
            qq=q if o=="permanent:attendre" else q+.1
            ev=evidence if o=="permanent:attendre" else evidence+.1
            events.append({"kind":"stage8_option_evaluation","t_monde":t,"cycle":1,
                "data":{"option_ref":o,"evidence":ev,
                "learned_value_status":"learned","learned_value":qq,
                "simulated_value_status":"evaluated","simulated_value":0.0}})
        events.append({"kind":"competition_cycle","t_monde":t,"cycle":1,
            "data":{"traces":[{"option_ref":o,"evidence":
                evidence if o=="permanent:attendre" else evidence+.1,
                "crossed":True} for o in options]}})
        events.append({"kind":"command_admitted","t_monde":t,"cycle":1,
            "data":{"source":"decision","option_ref":opt}})
        events.extend([
            {"kind":"command_experienced","t_monde":t,"attempt_ref":str(t),
             "primitive":"attendre" if t<3 else action,"parameters":{}},
            {"kind":"world_transition_experienced","t_monde":t,"attempt_ref":str(t),
             "body_before":before,"body_after":after},
            {"kind":"step_closed","t_monde":t,"attempt_ref":str(t),"data":{
                "applied_command_count":1,"world_advance_count":1,"outcome":"normal"}}])
    row={"scope":"A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3","mode":mode,
       "full_q_replay_verified":True,"birth_source_provenance_verified":False,
       "adaptive_learning_go":"NOT_ESTABLISHED","m11_identity":"id:"+mode,
       "m11_journal_head":"a"*64,"generation":3,"status":"active",
       "td_recurrences":[{"step":2,"segment_start":1,"length":1,
        "previous_signature":"attendre","next_signature":"attendre",
        "return_g":td}],"stage8_observations":[
            {"step":t,"cycle":1,"option":o,"signature":o,
             "status":"learned","q":q if o=="permanent:attendre" else q+.1}
            for t in (1,2,3) for o in (["permanent:attendre"] if t<3 else options)],
       "decisions":[]}
    return row,events

class PairWitnessTests(unittest.TestCase):
    def test_reward_difference_and_td_without_motor_not_l3(self):
        a,ae=pair("CANONICAL_ABS")
        b,be=pair("RESEARCH_DEFICIT",q=.3,evidence=.5,td=2.)
        # Different Stage8 signals alone never constitute a certified motor switch.
        result=compare_pair(canonical=a,candidate=b,canonical_events=ae,
              candidate_events=be,setpoints=dict.fromkeys(("energy","food","water","integrity"),60.),
              weights=dict.fromkeys(("energy","food","water","integrity"),1.))
        self.assertFalse(result["preregistered_mechanism_exposed"])
        self.assertEqual(result["general_L3"],"NOT_ESTABLISHED")

    def test_pre_reward_motor_difference_fail_closed(self):
        a,ae=pair("CANONICAL_ABS")
        b,be=pair("RESEARCH_DEFICIT",action="boire")
        be[3]["primitive"]="boire"
        with self.assertRaises(ValueError):
            compare_pair(canonical=a,candidate=b,canonical_events=ae,
              candidate_events=be,setpoints=dict.fromkeys(("energy","food","water","integrity"),60.),
              weights=dict.fromkeys(("energy","food","water","integrity"),1.))
if __name__=="__main__":
    unittest.main()
