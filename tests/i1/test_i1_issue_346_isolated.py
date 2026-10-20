"""I1 generated-only #346 finite-continuation contract."""
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class IsolatedIntent346(unittest.TestCase):
    def test_generated_contract(self):
        with TemporaryDirectory(prefix="i1-346-") as directory:
            built = Path(directory) / "built"
            generate(built)
            code = r"""
from i1.experimental.intention_continuity import IntentEvidence, bounded_continuation

prior=IntentEvidence("same-site", 10, (1,0), 0.8)
params=dict(intended_ref="same-site", now_step=11, observed_origin=(1,0),
            ceiling=0.5, residual=0.5, applied=True)
assert bounded_continuation(prior, **params) == 0.25
for changes in (dict(applied=False), dict(now_step=12),
                dict(observed_origin=(2,0)), dict(intended_ref="other")):
    assert bounded_continuation(prior, **(params | changes)) is None
for value in (float("nan"), float("inf"), -float("inf"), True):
    for field in ("accumulated", "ceiling", "residual"):
        p=IntentEvidence("same-site",10,(1,0),value) if field=="accumulated" else prior
        args=params if field=="accumulated" else (params | {field:value})
        try: bounded_continuation(p,**args)
        except ValueError: pass
        else: raise AssertionError("invalid numeric continuation admitted")
for bad in ((), (1,), (1,2,3), (True,0), [1,0]):
    for field in ("observed_destination","observed_origin"):
        p=IntentEvidence("same-site",10,bad,0.8) if field=="observed_destination" else prior
        args=params if field=="observed_destination" else params | {field:bad}
        try: bounded_continuation(p,**args)
        except ValueError: pass
        else: raise AssertionError("invalid coordinate admitted")
try: bounded_continuation(IntentEvidence("",10,(1,0),0.8),**params)
except ValueError: pass
else: raise AssertionError("empty semantic identity admitted")
print("I1_346_OK")
"""
            result = subprocess.run(
                [sys.executable, "-B", "-c", code],
                cwd=ROOT, env={"PYTHONPATH":str(built)+":"+str(ROOT/"src"),
                                "PYTHONDONTWRITEBYTECODE":"1"},
                capture_output=True,text=True,check=False,
            )
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
