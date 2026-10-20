"""Adversarial pure-pressure and preregistration tests for issue #317."""
from pathlib import Path
from dataclasses import replace
from tempfile import TemporaryDirectory
import importlib.util
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location("wake317",ROOT/"tools/run_i1_317_wake_recovery_factorial.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class WakeFactorial317Tests(unittest.TestCase):
    def test_exact_locked_four_arm_design(self):
        self.assertEqual(len(mod.ARMS),4)
        self.assertEqual(len(mod.SEEDS),2)
        self.assertEqual(len(mod.PRESETS),4)
        self.assertEqual({mod._factor(a) for a in mod.ARMS},
                         {(False,False),(True,False),(False,True),(True,True)})
        with self.assertRaises(ValueError):mod._factor("retuned")
        self.assertEqual(mod.HORIZON,300)
    def test_recovery_is_not_a_hidden_memory_credit(self):
        from types import SimpleNamespace
        frozen=SimpleNamespace(fatigue=0.8,consolidation_pressure=1.0,
                               sleep_pressure=0.65*0.8+0.25)
        cfg=SimpleNamespace(fatigue_weight=0.65,consolidation_weight=0.25,
                            night_weight=0.2)
        call=lambda current:mod.recovered_fatigue_pressure(
            frozen=frozen,entry_fatigue=0.8,current_fatigue=current,
            sleep_config=cfg,frozen_night=False)
        self.assertAlmostEqual(call(0.8),0.77)
        self.assertAlmostEqual(call(0.5),0.575)
        self.assertAlmostEqual(call(0.0),0.25)
        self.assertGreater(call(0.0),0.1)
        for n in (float("nan"),float("inf"),-0.1,0.9):
            with self.assertRaises(ValueError):call(n)
        with self.assertRaises(RuntimeError):
            mod.recovered_fatigue_pressure(
                frozen=SimpleNamespace(fatigue=0.8,
                   consolidation_pressure=1.0,sleep_pressure=0.1),
                entry_fatigue=0.8,current_fatigue=0.5,
                sleep_config=cfg,frozen_night=False)
    def test_threshold_can_change_no_other_birth_parameter(self):
        from dataclasses import dataclass
        @dataclass(frozen=True)
        class C:
            version:str
            natural_wake_threshold:float=0.1
        @dataclass(frozen=True)
        class B:
            version:str
            sleep:C
            def validate(self):pass
        canonical=B("native",C("sleep"))
        changed=mod.calibrate_native_birth(canonical,"natural_threshold")
        self.assertEqual(changed.sleep.natural_wake_threshold,0.35)
        self.assertEqual(changed.sleep.version,"sleep+i1-317-wake-factorial-natural_threshold")
        self.assertEqual(replace(changed,version="native",
                         sleep=replace(changed.sleep,version="sleep",
                           natural_wake_threshold=0.1)),canonical)
        with self.assertRaises(ValueError):
            mod.calibrate_native_birth(canonical,"recovered_fatigue")

if __name__=="__main__":unittest.main()
