"""Fail-closed tests for observational, non-coma Stage10 capacity audits."""
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location("capacity317",ROOT/"tools/audit_i1_317_consolidation_capacity.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def event(t,kind,**kwargs):
    return {"t_monde":t,"kind":kind,**kwargs}
def minimal():
    body={x:{"$f64":"0x1.0p+4"} for x in ("water","food","integrity","energy")}
    return [
        event(1,"episode_closed",data={"id":"episode:0"}),
        event(1,"world_transition_experienced",body_after=body),
        event(1,"step_closed",data={"outcome":"normal",
            "world_advance_count":1,"applied_command_count":1}),
        event(2,"stage10_consolidation_version_activated",data={
            "batch":["episode:0"],"consolidation_id":"c","new_history_version":"h"}),
        event(2,"stage10_consolidation_committed",data={
            "consolidation_id":"c","new_history_version":"h","world_step":2}),
        event(2,"world_transition_experienced",body_after=body),
        event(2,"step_closed",data={"outcome":"normal",
            "world_advance_count":1,"applied_command_count":1}),
    ]
class CapacityTests(unittest.TestCase):
    def test_real_episode_then_atomic_batch(self):
        x=m.classify(minimal(),2)
        self.assertEqual(x["episodes_closed"],1)
        self.assertEqual(x["episode_objects_consolidated"],1)
        self.assertEqual(x["final_pending"],0)
        self.assertEqual(x["actual_coma_events"],0)
    def test_unlived_or_double_consolidation_rejected(self):
        x=minimal()
        x[3]["data"]["batch"]=["episode:future"]
        with self.assertRaises(ValueError):m.classify(x,2)
        x=minimal()
        x[3]["data"]["batch"]=["episode:0","episode:0"]
        with self.assertRaises(ValueError):m.classify(x,2)
    def test_unmatched_receipt_rejected(self):
        x=minimal()
        x[4]["data"]["consolidation_id"]="wrong"
        with self.assertRaises(ValueError):m.classify(x,2)
    def test_missing_physical_step_not_counted(self):
        x=minimal()
        x.pop()
        with self.assertRaises(ValueError):m.classify(x,2)
    def test_threshold_crossing_is_not_coma(self):
        x=[event(1,"episode_closed",data={"id":f"episode:{i}"})
            for i in range(16)]
        x+=minimal()[1:3]
        r=m.classify(x,1)
        self.assertTrue(r["probes"]["16"]["crossed"])
        self.assertEqual(r["actual_coma_events"],0)
        self.assertFalse(r["probes"]["16"]["physically_witnessed_recovery_to_half"])
if __name__=="__main__":unittest.main()
