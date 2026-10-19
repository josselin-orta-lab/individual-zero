"""Fail closed on partial / forged 32-life factorial evidence."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location("audit32",ROOT/"tools/audit_i1_317_wake_recovery_cohort.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class AuditFactorialTests(unittest.TestCase):
    def test_unregistered_arm_and_partial_cohort(self):
        with self.assertRaises(ValueError):m.flags("unknown")
        with TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):m.analyse(Path(folder))
    def test_forged_birth_and_original_sha(self):
        with self.assertRaises(ValueError):m.check_birth({}, "oasis", 11117,m.EXACT_ENGINE_SHA)
        with TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):m.analyse(Path(folder),"f"*40)
    def test_precise_four_arm_factorial(self):
        assert {m.flags(a) for a in m.ARMS}=={
            (False,False),(False,True),(True,False),(True,True)}
        self.assertEqual(len(m.ARMS)*len(m.PRESETS)*len(m.SEEDS),32)
    def test_wake_cardinality_fail_closed(self):
        from json import dumps
        with TemporaryDirectory() as folder:
            f=Path(folder)/"fake.wal"
            f.write_text(dumps({"causal_event":{"kind":"stage10_sleep_woke",
                         "t_monde":1,"data":{"reason":"alert"}}})+"\n")
            with self.assertRaises(ValueError):m._wake_events(f)
if __name__=="__main__":unittest.main()
