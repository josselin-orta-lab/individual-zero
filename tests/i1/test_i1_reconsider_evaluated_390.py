"""Reconsideration is post-evaluation, not registration-only (controlled wiring)."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class ReconsiderationPhase(unittest.TestCase):
    def test_generated_wiring(self):
        with TemporaryDirectory(prefix="i1-390-") as tmp:
            generated=Path(tmp)/"generated"
            generate(generated)
            script="""
import inspect
from i1lab.stage11_runtime import Stage11Runtime
from i1.modules.competition import Competition
registration=inspect.getsource(Stage11Runtime._phase_hooks)
evaluation=inspect.getsource(Stage11Runtime._evaluate_competition_cycle)
assert "reconsider_confirmed_intention(" not in registration
assert "reconsider_confirmed_intention(" in evaluation
assert 'row.status == "evaluated"' in evaluation
assert "result = super()._evaluate_competition_cycle" in evaluation
assert evaluation.index("result = super()._evaluate_competition_cycle") < evaluation.index("reconsider_confirmed_intention(")
assert '"evaluation_status": "evaluated"' in evaluation
assert "candidate.accumulator or last_threshold" not in evaluation
print("I1_390_POST_PAID_EVALUATION_WIRING_OK")
"""
            env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(generated),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
            p=subprocess.run([sys.executable,"-B","-c",script],cwd=ROOT,env=env,text=True,capture_output=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            self.assertIn("I1_390_POST_PAID_EVALUATION_WIRING_OK",p.stdout)
