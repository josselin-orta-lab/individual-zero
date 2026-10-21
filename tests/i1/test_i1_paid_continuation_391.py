"""Bounded spatial continuation requires a paid, actually evaluated option."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class PaidContinuation(unittest.TestCase):
    def test_generated_sequence_and_negative_evaluation(self):
        with TemporaryDirectory(prefix="i1-391-") as d:
            built=Path(d)/"generated";generate(built)
            program="""
import inspect
from i1lab.stage10_runtime import Stage10Runtime
from i1lab.stage11_runtime import Stage11Runtime
stage10=inspect.getsource(Stage10Runtime._evaluate_competition_cycle)
stage11=inspect.getsource(Stage11Runtime._before_competition_accumulation)
phase3=inspect.getsource(Stage11Runtime._phase_hooks)
assert "retain_bounded_intention_evidence" not in phase3
assert "retain_bounded_intention_evidence" in stage11
assert 'supplied.evaluation.status != "evaluated"' in stage11
assert "evidence_inputs.get(ref)" in stage11
assert stage10.index("self._before_competition_accumulation(") < stage10.index("return self.competition.evaluate(")
assert stage10.index("self.stage8_option_evaluator.evaluate(") < stage10.index("self._before_competition_accumulation(")
assert "motor_admission_inherited" not in stage11
print("I1_391_PAID_CONTINUATION_GATE_OK")
"""
            env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(built),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
            p=subprocess.run([sys.executable,"-B","-c",program],cwd=ROOT,env=env,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            self.assertIn("I1_391_PAID_CONTINUATION_GATE_OK",p.stdout)
