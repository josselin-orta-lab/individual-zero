"""Negative tests for the independent #317 first-person vital-chain audit."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location("audit_water_chain",ROOT/"tools/audit_i1_317_vital_memory_decision_chain.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class VitalMemoryChain317Tests(unittest.TestCase):
    def test_partial_cohort_rejected(self):
        with TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):m.certify(Path(folder))
    def test_no_ungrounded_synthetic_life(self):
        with self.assertRaises(ValueError):
            m.classify_life([],physical_steps=1)
        with self.assertRaises(ValueError):
            m.classify_life([{"kind":"perceptual_capture","t_monde":2}],physical_steps=1)
        with self.assertRaises(ValueError):
            m.classify_life([],physical_steps=301)
    def test_nonapplied_and_wrong_command_rejected(self):
        def event(kind, extra=None):
            v={"kind":kind,"t_monde":1,"attempt_ref":"a"}
            if extra:v.update(extra)
            return v
        command=event("command_experienced",{"emitter":"action_control",
                      "primitive":"dormir","command_hash":"h"})
        movement=event("world_transition_experienced",{"effects":{}})
        admission=event("command_admitted",{"data":{"primitive":"dormir",
                        "command_hash":"h","option_ref":"sleep"}})
        closure=event("step_closed",{"data":{"outcome":"normal",
                      "applied_command_count":0,"world_advance_count":1}})
        with self.assertRaises(ValueError):
            m.classify_life([command,movement,admission,closure],physical_steps=1)
        closure["data"]["applied_command_count"]=1
        with self.assertRaises(ValueError):
            m.classify_life([command,movement,closure],physical_steps=1)
    def test_compliant_synthetic_physical_step_is_not_automatically_water_success(self):
        events=[
            {"kind":"perceptual_capture","t_monde":1,"data":{
                "dual_scope_visible_body":{"water":{"$f64":"0x1.cp+3"}}}},
            {"kind":"command_admitted","t_monde":1,"data":{
                "primitive":"dormir","command_hash":"h","option_ref":"s"}},
            {"kind":"command_experienced","t_monde":1,"emitter":"action_control",
             "primitive":"dormir","command_hash":"h"},
            {"kind":"world_transition_experienced","t_monde":1,"effects":{},
             "position_after":{"x":8,"y":8}},
            {"kind":"step_closed","t_monde":1,"data":{
                "outcome":"normal","applied_command_count":1,
                "world_advance_count":1}},
        ]
        d=m.classify_life(events,physical_steps=1)["counters"]
        self.assertEqual(d["water_critical_waking_steps"],1)
        self.assertEqual(d["water_critical_chose_dormir"],1)
        self.assertEqual(d.get("water_critical_water_memory_proposed_steps",0),0)
if __name__=="__main__":unittest.main()
