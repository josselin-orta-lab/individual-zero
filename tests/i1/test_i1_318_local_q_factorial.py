"""Factorial Q visibility cannot alter TD ownership or motor authority."""
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class LocalQFactorial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=TemporaryDirectory()
        generated=Path(cls.tmp.name)/"generated"
        generate(generated)
        sys.path.insert(0,str(generated))
        from i1lab.i1_active_runtime import _local_q_visibility
        cls.visibility=staticmethod(_local_q_visibility)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_all_four_research_arms(self):
        self.assertEqual(self.visibility("neutral"),(False,False))
        self.assertEqual(self.visibility("rank_only"),(True,False))
        self.assertEqual(self.visibility("evidence_only"),(False,True))
        self.assertEqual(self.visibility("learned"),(True,True))

    def test_reject_invalid_policy(self):
        for bad in (None,True,42,"oracle",""):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.visibility(bad)

    def test_q_owner_unmodified(self):
        source=(ROOT/"src/i1/runtime/i1_active_runtime.py").read_text()
        self.assertIn("learned = self.q_active.learned_value(context, signature)",source)
        self.assertIn("selected_evidence = learned if expose_evidence else None",source)
        self.assertIn("if expose_rank else 0.0",source)
        self.assertIn("forced_motor",source)

if __name__=="__main__":
    unittest.main()
