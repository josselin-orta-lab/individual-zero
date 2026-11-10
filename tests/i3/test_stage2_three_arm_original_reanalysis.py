"""Read-only archived three-arm originals checker; no new World or life."""
import inspect
from pathlib import Path
import tempfile
import unittest

from i3.lab import stage2_three_arm_original_reanalysis as VERIFY


class ThreeArmOriginalReanalysisTests(unittest.TestCase):
    def test_source_pins_and_no_scientific_go(self):
        self.assertEqual(VERIFY.LIVES,192)
        self.assertEqual(VERIFY.UNITS,64)
        self.assertEqual(len(VERIFY.SOURCE_SHA),40)
        for value in (VERIFY.FINGERPRINT,VERIFY.PLAN_SHA,VERIFY.MANIFEST_SHA):
            self.assertEqual(len(value),64)
            self.assertTrue(all(c in "0123456789abcdef" for c in value))
        self.assertNotEqual(VERIFY.FINGERPRINT,VERIFY.MANIFEST_SHA)

    def test_missing_originals_fail_closed_and_never_become_deaths(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,"missing original evidence"):
                VERIFY.verify(tmp)
            (Path(tmp)/"originals").mkdir()
            with self.assertRaises(FileNotFoundError):
                VERIFY.verify(tmp)

    def test_no_execution_entrypoint_or_world_runtime_dependency(self):
        src=inspect.getsource(VERIFY)
        self.assertNotIn("run_life(",src)
        self.assertNotIn("generation_zero(",src)
        self.assertNotIn("World(",src)
        self.assertNotIn("World.step(",src)
        with self.assertRaises(SystemExit):
            VERIFY.main(["prog"])


if __name__=="__main__":
    unittest.main()
