"""Adversarial checks for original Q-ablation first-motor-fork certificate."""
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location(
    "q318audit",ROOT/"tools/audit_i1_318_local_q_ablation_cohort.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def e(kind,t,*,data=None,**extra):
    return {"kind":kind,"t_monde":t,
            "data":{} if data is None else data,**extra}

def sleep_without_capture():
    return [
        e("command_experienced",1,primitive="dormir",command_hash="h",
          attempt_ref="a",emitter="action_control"),
        e("world_transition_experienced",1,body_after={"water":50},
          position_after={"x":1,"y":1},effects={}),
    ]

def minimal():
    return {
        "motor":{1:{"primitive":"attendre","parameters":{},
                    "digest":"h"}},
        "physical":{1:{"body_after":{"water":50},"position_after":{"x":1,"y":1},
                       "effects":{}}},
        "captures":{1:{"position":{"x":1,"y":1}}},
        "local_motor":{},
        "first_learned_Q_local_proposal_step":None,
        "proposals":{},
    }

class OriginalQAblationAuditTests(unittest.TestCase):
    def test_sleep_is_real_without_fabricated_capture(self):
        motor,transitions,captures,*_=m.physical_history(sleep_without_capture())
        self.assertEqual(len(motor),1)
        self.assertEqual(len(transitions),1)
        self.assertFalse(captures)

    def test_local_proposal_requires_capture(self):
        trace=sleep_without_capture()+[
            e("i1_local_opportunity_proposed",1,data={"option_ref":"option:i1:local:x"})]
        with self.assertRaises(ValueError):
            m.physical_history(trace)

    def test_no_divergence_is_not_q_proof(self):
        a=minimal()
        p=m.compare_pair(a,a)
        self.assertIsNone(p["first_motor_divergence"])
        self.assertFalse(p["fork"])

    def test_motor_divergence_without_learning_not_q_proof(self):
        a,b=minimal(),minimal()
        b["motor"][1]={"primitive":"boire","parameters":{},"digest":"z"}
        result=m.compare_pair(a,b)
        self.assertEqual(result["first_motor_divergence"],1)
        self.assertFalse(result["fork"]["exposed_learned_Q_no_later_than_fork"])

if __name__=="__main__":
    unittest.main()
