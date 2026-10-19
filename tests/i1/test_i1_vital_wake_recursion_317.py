"""Adversarial tests for alert-wake physical reacquisition, no invented benefit."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location(
    "wake_317",ROOT/"tools/audit_i1_317_vital_wake_recursion.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def sample():
    def row(kind, **kw):
        return {"kind":kind,"t_monde":1,"attempt_ref":"attempt:a",**kw}
    body={"energy":{"$f64":"0x1.9p+6"},"food":{"$f64":"0x1.2p+3"},
          "water":{"$f64":"0x0p+0"},"integrity":{"$f64":"0x1.ap+5"}}
    return [
        row("stage10_reduced_capture",data={"critical_body_channels":["water"]}),
        row("stage10_sleep_woke",data={"reason":"alert"}),
        row("stage10_sleep_pressure_frozen",data={
            "sleep_pressure":{"$f64":"0x1.ccccccccccccdp-1"}}),
        row("competition_cycle",data={"traces":[
            {"option_ref":"sleep:test","crossed":True}]}),
        row("command_admitted",data={
            "command_hash":"hash:a","primitive":"dormir",
            "option_ref":"sleep:test"}),
        row("command_experienced",primitive="dormir",command_hash="hash:a"),
        row("world_transition_experienced",body_after=body,effects={
            "rest":"dormir"}),
        row("step_closed",data={"outcome":"normal",
            "applied_command_count":1,"world_advance_count":1}),
    ]


class AlertWake317Tests(unittest.TestCase):
    def test_wake_to_sleep_is_observation_not_causal_repair(self):
        out=m.classify(sample(),1)
        ct=out["counters"]
        self.assertEqual(ct["critical_alert_wakes"],1)
        self.assertEqual(ct["alert_wakes_reselecting_sleep_same_step"],1)
        self.assertEqual(ct["alert_resleep_with_verified_competition_crossing"],1)
        self.assertEqual(ct["sleep_at_zero_water"],1)

    def test_broken_command_hash_is_not_lived_action(self):
        events=sample()
        events[-3]["command_hash"]="forged"
        with self.assertRaises(ValueError):
            m.classify(events,1)

    def test_missing_reduced_capture_is_not_alert_proof(self):
        events=[x for x in sample() if x["kind"]!="stage10_reduced_capture"]
        with self.assertRaises(ValueError):
            m.classify(events,1)

    def test_missing_competition_crossing_stays_explicit(self):
        events=[x for x in sample() if x["kind"]!="competition_cycle"]
        ct=m.classify(events,1)["counters"]
        self.assertEqual(ct["alert_resleep_without_visible_crossing"],1)

    def test_broken_life_step_closure_fails(self):
        events=sample()
        events[-1]["data"]["world_advance_count"]=0
        with self.assertRaises(ValueError):
            m.classify(events,1)

if __name__=="__main__":
    unittest.main()
