"""Generated-I1 tests for pure interruption semantics; no canonical activation."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class IntentLifecycleTest(unittest.TestCase):
    def test_generated_contract(self):
        with TemporaryDirectory(prefix="i1-326-lifecycle-") as directory:
            output = Path(directory) / "built"
            generate(output)
            program = """
from i1.experimental.intention_continuity import IntentEvidence, intention_reentry
prior = IntentEvidence("seen-place", 10, (1, 0), .8)
kw = dict(intended_ref="seen-place", now_step=11, observed_origin=(1,0), ceiling=.5, residual=.5,
          applied=True, active_goal_unchanged=True, observed_route_valid=True,
          urgent_need=False, sleeping=False)
assert intention_reentry(prior, **kw) == ("reconsider", .25)
assert intention_reentry(prior, **(kw | {"urgent_need": True})) == ("suspended", None)
assert intention_reentry(prior, **(kw | {"sleeping": True})) == ("suspended", None)
assert intention_reentry(prior, **(kw | {"observed_route_valid": False})) == ("invalidated", None)
assert intention_reentry(prior, **(kw | {"active_goal_unchanged": False})) == ("invalidated", None)
assert intention_reentry(prior, **(kw | {"observed_origin": (2,0)})) == ("unconfirmed", None)
assert intention_reentry(prior, **(kw | {"applied": False})) == ("unconfirmed", None)
assert intention_reentry(prior, **(kw | {"now_step": 12})) == ("unconfirmed", None)
for field in ("urgent_need", "sleeping", "active_goal_unchanged", "observed_route_valid"):
    try:
        intention_reentry(prior, **(kw | {field: 1}))
        raise AssertionError(field)
    except ValueError:
        pass
try:
    intention_reentry(prior, **(kw | {"ceiling": float("nan"), "sleeping": True}))
    raise AssertionError("NaN must be rejected even if suspended")
except ValueError:
    pass
"""
            env = dict(os.environ, PYTHONPATH=str(output) + os.pathsep + str(ROOT / "src"),
                       PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run([sys.executable, "-B", "-c", program],
                                    cwd=ROOT, env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
