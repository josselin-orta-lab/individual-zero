"""Regression: M11 cold current-image preserves integer vs float body types.

Never reconstruct a dead life or an older committed generation.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate


class M11BodyTypeFidelity(unittest.TestCase):
    def test_generated_body_type_contract_and_canonical_distinction(self):
        with TemporaryDirectory(prefix="i1-m11-typed-") as folder:
            generated=Path(folder)/"generated"
            generate(generated)
            code=r"""
from i1lab.world import BodyState
from i1lab.determinism import canonical_causal_bytes
from i1lab.m11_transactional_mortal import _install_trusted_current_on_fresh
import inspect
integer=BodyState(energy=85,food=50,water=50,integrity=85)
floating=BodyState(energy=85.0,food=50.0,water=50.0,integrity=85.0)
assert integer.as_dict()==floating.as_dict()
assert canonical_causal_bytes(integer.as_dict()) != canonical_causal_bytes(floating.as_dict())
src=inspect.getsource(_install_trusted_current_on_fresh)
assert 'staging._body = exact_body' in src
assert 'cold body type fidelity differs from SQLite image' in src
print('M11_BODY_TYPES_PINNED')
"""
            p=subprocess.run([sys.executable,"-c",code],
                cwd=ROOT,env={"PYTHONPATH":str(generated)+":"+str(ROOT/"src")},
                text=True,capture_output=True,check=False)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertIn("M11_BODY_TYPES_PINNED",p.stdout)


if __name__=="__main__":
    unittest.main()
