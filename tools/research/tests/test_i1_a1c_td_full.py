"""Adversarial A1-C full-vector M11 Q/TD replay, no life generation."""
import sys
import json
import unittest
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from i1_a1c_td_full import FROZEN_TD_VERSION, p32_features, replay_life, numeric
from i1_a1c_td_full_audit import audit, one

TD = {"version": FROZEN_TD_VERSION, "beta": .8, "lambda_e": .8, "eta": .05}
COLLECT = "i1:affordance:collecter:target=berry_a"
EAT = "i1:affordance:manger:target=berry_a"
BODIES = [
    {"energy":70,"food":35,"water":35,"integrity":85},
    {"energy":69,"food":34.8,"water":34.8,"integrity":85},
    {"energy":68,"food":34.6,"water":34.6,"integrity":85},
]


def capture(step, body):
    return {"kind":"perceptual_capture","t_monde":step,"data":{
        "capture_t_monde":step,"dual_scope_visible_body":dict(body),
        "position":{"x":8,"y":8}}}


def stage(step, signature, learned=False, value=None):
    return {"kind":"stage8_option_evaluation","t_monde":step,"cycle":1,
            "data":{"option_ref":"option:"+signature,
                    "learning_signature":signature,
                    "learned_value_status":"learned" if learned else "unlearned",
                    "learned_value":value,"evidence":.2}}


def competition(step, signature):
    return {"kind":"competition_cycle","t_monde":step,"cycle":1,
            "data":{"traces":[{"option_ref":"option:"+signature,
                               "crossed":True,"evidence":.2}]}}


def admission(step, signature):
    return {"kind":"command_admitted","t_monde":step,
            "data":{"source":"decision","option_ref":"option:"+signature}}


def update(step, previous, nxt, delta, qp, qn, sigs):
    return {"kind":"td_update_published","t_monde":step,
            "data":{"previous_signature":previous,"next_signature":nxt,
                    "td_version":FROZEN_TD_VERSION,"segment_length":1,
                    "return_g":delta + qp - .8*qn,"q_previous":qp,
                    "q_next":qn,"delta":delta,"updated_signatures":sigs}}


def fixture(mode="canonical"):
    captures=[capture(i+1,b) for i,b in enumerate(BODIES)]
    phi1=p32_features(captures[0],None)
    phi3=p32_features(captures[2],None)
    learned_q=.05*1.5*sum(x*y for x,y in zip(phi1,phi3))
    events=[]
    for step, cap, sig, primitive in (
        (1,captures[0],COLLECT,"collecter"),
        (2,captures[1],EAT,"manger"),
        (3,captures[2],COLLECT,"collecter"),
    ):
        events.extend([
            cap, stage(step,sig,step==3 and mode=="canonical",
                       learned_q if step==3 and mode=="canonical" else None),
            competition(step,sig),admission(step,sig),
            {"kind":"command_experienced","t_monde":step,
             "primitive":primitive,"parameters":{"target":"berry_a"}},
            {"kind":"world_transition_experienced","t_monde":step,
             "body_before":dict(BODIES[step-1])},
        ])
        if step==2:
            events.append(update(2,COLLECT,EAT,1.5,0.,0.,[COLLECT]))
        if step==3:
            events.append(update(3,EAT,COLLECT,.5+.8*learned_q,
                                 0.,learned_q,[COLLECT,EAT]))
    for step in range(4,49):
        events.extend([
            {"kind":"command_experienced","t_monde":step,
             "primitive":"dormir","parameters":{}},
            {"kind":"world_transition_experienced","t_monde":step,
             "body_before":dict(BODIES[-1])},
        ])
    return events


class FullVectorM11Contracts(unittest.TestCase):
    def test_native_q_and_masked_value_reconstructed_without_model(self):
        for mode,native,masked in (("canonical",1,0),
                                   ("td_read_masked",0,1)):
            with self.subTest(mode=mode):
                r=replay_life(fixture(mode),born_td=TD,mode=mode)
                self.assertEqual(r["native_m11_q_checks"],native)
                self.assertEqual(r["masked_stage8_consistency_checks"],masked)
                self.assertEqual(r["td_updates"],2)
                self.assertEqual(r["postmeal_td"],1)
                self.assertEqual(r["stage8_to_competition_links"],3)
                self.assertLess(r["max_m11_numeric_residual"],1e-10)
                self.assertEqual(r["a1c_status"],"NO_GO")
                self.assertEqual(r["general_L3"],"NOT_ESTABLISHED")

    def test_features_pinned_to_true_p32_state(self):
        vec=p32_features(capture(1,BODIES[0]),"eat")
        self.assertEqual(len(vec),12)
        self.assertEqual(vec[0],1.)
        self.assertEqual(vec[2],.35)
        self.assertAlmostEqual(vec[5],8/31)
        self.assertEqual(vec[9],1.)
        self.assertEqual(sum(vec[8:]),1.)

    def test_td_q_delta_and_signature_tampering_all_rejected(self):
        for field in ("q_previous","q_next","delta","updated_signatures"):
            with self.subTest(field=field):
                e=fixture()
                pub=next(x for x in e if x["kind"]=="td_update_published"
                         and x["t_monde"]==3)
                pub["data"][field]=["rogue"] if field=="updated_signatures" else 14.
                with self.assertRaises(ValueError):
                    replay_life(e,born_td=TD,mode="canonical")

    def test_stage8_learned_q_forgery_and_mask_leak_rejected(self):
        e=fixture()
        published=next(x for x in e if x["kind"]=="stage8_option_evaluation"
                       and x["t_monde"]==3)
        published["data"]["learned_value"]=12.
        with self.assertRaises(ValueError):
            replay_life(e,born_td=TD,mode="canonical")
        e=fixture("td_read_masked")
        published=next(x for x in e if x["kind"]=="stage8_option_evaluation"
                       and x["t_monde"]==3)
        published["data"]["learned_value_status"]="learned"
        with self.assertRaises(ValueError):
            replay_life(e,born_td=TD,mode="td_read_masked")

    def test_competition_and_motor_admission_forgery_rejected(self):
        e=fixture()
        cycle=next(x for x in e if x["kind"]=="competition_cycle")
        cycle["data"]["traces"][0]["evidence"]=-.9
        with self.assertRaises(ValueError):
            replay_life(e,born_td=TD,mode="canonical")
        e=fixture()
        cycle=next(x for x in e if x["kind"]=="competition_cycle")
        cycle["data"]["traces"][0]["crossed"]=False
        with self.assertRaises(ValueError):
            replay_life(e,born_td=TD,mode="canonical")

    def test_wrong_body_goal_and_td_coefficients_rejected(self):
        e=fixture()
        physical=next(x for x in e if x["kind"]=="world_transition_experienced")
        physical["body_before"]["food"]=12.
        with self.assertRaises(ValueError):
            replay_life(e,born_td=TD,mode="canonical")
        e=fixture()
        e.insert(1,{"kind":"active_goal_changed","t_monde":1,"cycle":1,
                    "data":{"after":{"goal_type":"eat"}}})
        with self.assertRaises(ValueError):
            replay_life(e,born_td=TD,mode="canonical")
        for field in ("beta","eta","lambda_e"):
            with self.subTest(field=field),self.assertRaises(ValueError):
                replay_life(fixture(),born_td={**TD,field:.9},mode="canonical")

    def test_noncanonical_and_nonfinite_inputs_rejected(self):
        for value in (True,float("nan"),{"$f64":"0x1p+1"},
                      {"$f64":"0x1.0p+01"}):
            with self.subTest(value=str(value)),self.assertRaises(ValueError):
                numeric(value)

    def test_unverified_cohort_identity_and_zip_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"I1_ECO_A1C_EVIDENCE_MANIFEST.json"
            p.write_text(json.dumps({
                "original_run_id":3,"original_source_sha":"forged",
                "archived_independent_lives":48}))
            with self.assertRaises(ValueError):
                audit(Path(directory))
            name="a1c-native-s101-canonical"
            (Path(directory)/(name+".zip")).write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                one((Path(directory),name,{"bytes":8,"sha256":"00"*32},
                     "native",101,"canonical"))


if __name__=="__main__":
    unittest.main()
