"""Isolated generated-I1 test runner, never importing source I1 in CI process."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class IsolatedIssueTest(unittest.TestCase):
    def test_generated_python_contract(self):
        with TemporaryDirectory(prefix="i1-326-") as directory:
            built=Path(directory)/"built"
            generate(built)
            source="import unittest\nfrom i1.experimental.intention_continuity import IntentEvidence, bounded_continuation\n\nclass TestPure(unittest.TestCase):\n    def test_transfer_requires_observed_applied_hop(self):\n        prior=IntentEvidence(\"same-site\", 10, (1, 0), 0.8)\n        kw=dict(intended_ref=\"same-site\",now_step=11,observed_origin=(1,0),ceiling=0.5,residual=0.5,applied=True)\n        self.assertEqual(bounded_continuation(prior,**kw),0.25)\n        for delta in (dict(applied=False),dict(now_step=12),dict(observed_origin=(2,0)),dict(intended_ref=\"different\")):\n            self.assertIsNone(bounded_continuation(prior,**(kw|delta)))\n    def test_invalid_values_fail_closed(self):\n        with self.assertRaises(ValueError):\n            bounded_continuation(IntentEvidence(\"a\",10,(1,0),0.5),intended_ref=\"a\",now_step=11,observed_origin=(1,0),ceiling=0.5,residual=True,applied=True)\nunittest.main()"
            result=subprocess.run([sys.executable,"-B","-c",source],
                cwd=ROOT,env={"PYTHONPATH":str(built)+":"+str(ROOT/"src"),"PYTHONDONTWRITEBYTECODE":"1"},
                text=True,capture_output=True,check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
