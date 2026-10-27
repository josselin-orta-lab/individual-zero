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
        with TemporaryDirectory(prefix="i1-327-") as directory:
            built=Path(directory)/"built"
            generate(built)
            source="import unittest\nfrom i1.experimental.local_opportunity_selection import local_interaction_choices,local_q_visibility\nfrom types import SimpleNamespace\n\nclass TestPure(unittest.TestCase):\n    def test_no_unearned_command(self):\n        commands=tuple(SimpleNamespace(primitive=p) for p in (\"boire\",\"attendre\",\"collecter\"))\n        self.assertEqual([x.primitive for x in local_interaction_choices(commands,enabled=True)],[\"boire\",\"collecter\"])\n        self.assertEqual(local_interaction_choices(commands,enabled=False),())\n        self.assertEqual(local_q_visibility(\"neutral\"),(False,False))\n        self.assertEqual(local_q_visibility(\"learned\"),(True,True))\n        with self.assertRaises(ValueError):local_q_visibility(\"forced\")\nunittest.main()"
            result=subprocess.run([sys.executable,"-B","-c",source],
                cwd=ROOT,env={"PYTHONPATH":str(built)+":"+str(ROOT/"src"),"PYTHONDONTWRITEBYTECODE":"1"},
                text=True,capture_output=True,check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
