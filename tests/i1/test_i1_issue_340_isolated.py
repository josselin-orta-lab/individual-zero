"""Contract tests execute the generated I1 utility, not a live actor."""
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class LocalDedup340(unittest.TestCase):
    def test_generated_i1(self):
        with TemporaryDirectory() as directory:
            out = Path(directory) / "generated"
            generate(out)
            code = r"""
from i1.experimental.local_command_dedup import distinct_local_commands
from i1.interfaces import PrimitiveCommand
from types import SimpleNamespace

def option(command, expiry, *more):
    steps = tuple(SimpleNamespace(command=c) for c in (command,) + more)
    return SimpleNamespace(option=SimpleNamespace(expires_at_step=expiry),
                           plan=SimpleNamespace(steps=steps))
a = PrimitiveCommand("collecter", {"nested":{"x":1,"y":[2]}})
b = PrimitiveCommand("boire", {})
c = PrimitiveCommand("collecter", {"nested":{"y":[2],"x":1}})
available = (a, b, c)
present = (option(a, 5),)
assert distinct_local_commands(available, present, now_step=4) == (b,)
assert distinct_local_commands(available, (option(a, 4),), now_step=4) == (a,b)
assert distinct_local_commands(available, (option(a, 5, b),), now_step=4) == (b,)
assert available == (a,b,c) and present == (option(a,5),)

# Python's True == 1 == 1.0 and list == tuple collisions must not merge commands.
typed = tuple(PrimitiveCommand("collecter", {"p":p}) for p in
              (True, 1, 1.0, [1], (1,)))
assert distinct_local_commands(typed, (), now_step=2) == typed

for bad in (float("nan"), float("inf"), -float("inf"), object(), {1: "x"}):
    try:
        distinct_local_commands((PrimitiveCommand("collecter", {"p":bad}),), (), now_step=4)
    except ValueError:
        pass
    else:
        raise AssertionError("untrusted parameter accepted")
cyclic = []
cyclic.append(cyclic)
too_deep = 0
for _ in range(20):
    too_deep = [too_deep]
for bad in (cyclic, too_deep, list(range(257))):
    try:
        distinct_local_commands((PrimitiveCommand("collecter", {"p":bad}),), (), now_step=4)
    except ValueError:
        pass
    else:
        raise AssertionError("unbounded parameter accepted")
for bad in (0, True, 1.0):
    try:
        distinct_local_commands((a,), (), now_step=bad)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid step accepted")
print("I1_340_OK")
"""
            result = subprocess.run(
                [sys.executable, "-B", "-c", code],
                env={"PYTHONPATH": str(out) + ":" + str(ROOT / "src"),
                     "PYTHONDONTWRITEBYTECODE": "1"},
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
