"""#356: no post-Action-Control WAL writes on witnessed spatial intention."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate

class SpatialPostcommitTest(unittest.TestCase):
    def test_generated_dispatch_has_no_late_event(self):
        with TemporaryDirectory() as folder:
            built=Path(folder)/"generated"
            generate(built)
            script="""
import inspect
from i1lab.stage11_runtime import Stage11Runtime
source=inspect.getsource(Stage11Runtime._dispatch_decision)
segment=source.split('record_applied_memory_intention(',1)[1].split('if (',1)[0]
assert 'self._write(' not in segment, 'cannot journal after physical commit'
assert 'Action Control already closed' in source
print('I1_356_WAL_SAFE')
"""
            env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(built),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
            p=subprocess.run([sys.executable,"-B","-c",script],env=env,cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            self.assertIn("I1_356_WAL_SAFE",p.stdout)

if __name__=="__main__":
    unittest.main()
