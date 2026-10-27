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
        with TemporaryDirectory(prefix="i1-329-") as directory:
            built=Path(directory)/"built"
            generate(built)
            source="import unittest\nfrom i1.experimental.critical_alert_wake import critical_alert_channels\nfrom types import SimpleNamespace\n\nclass TestPure(unittest.TestCase):\n    def test_read_only_physiological_alert(self):\n        pending=SimpleNamespace(woke=True,reason=\"alert\",world_step=3)\n        capture=SimpleNamespace(t_monde=3,body=dict(energy=70,food=10,water=8,integrity=95))\n        k=dict(pending=pending,sleep_mode=\"awake\",world_step=3,capture=capture,thresholds=dict(energy=10,food=10,water=10,integrity=10))\n        self.assertEqual(critical_alert_channels(**k),(\"water\",\"food\"))\n        self.assertEqual(critical_alert_channels(**(k|dict(sleep_mode=\"sleeping\"))),())\n        with self.assertRaises(RuntimeError):\n            critical_alert_channels(**(k|dict(capture=SimpleNamespace(t_monde=3,body={}))))\nunittest.main()"
            result=subprocess.run([sys.executable,"-B","-c",source],
                cwd=ROOT,env={"PYTHONPATH":str(built)+":"+str(ROOT/"src"),"PYTHONDONTWRITEBYTECODE":"1"},
                text=True,capture_output=True,check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
