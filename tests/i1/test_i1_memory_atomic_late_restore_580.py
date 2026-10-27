"""Generated-I1 Memory owner must not mutate on late invalid causal images."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class AtomicLateMemoryRestore580(unittest.TestCase):
    def test_generated_memory_late_corruption_rejection(self):
        with TemporaryDirectory(prefix="i1-580-") as home:
            out = Path(home) / "generated"
            generate(out)
            program = r"""
from copy import deepcopy
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime

runtime = build_stage11_reference_runtime(autonomous_mortal=True)
memory = runtime.memory
before = deepcopy(memory.export_causal_state())
def check_bad(field, invalid):
    bad = deepcopy(before)
    # Valid earlier mutation must not survive a later decoding exception.
    bad["seen_event_refs"] = ["reference:not-in-original"]
    bad[field] = invalid
    try:
        memory.restore_causal_state(bad)
    except (ValueError, TypeError, KeyError):
        pass
    else:
        raise AssertionError("invalid late Memory field accepted: " + field)
    assert memory.export_causal_state() == before, "Memory mutated: " + field

check_bad("open_reward", "invalid-number")
check_bad("open_surprise", "invalid-number")
check_bad("episode_sequence", "invalid-integer")
check_bad("open_body_end", 42)
memory.restore_causal_state(deepcopy(before))
assert memory.export_causal_state() == before
print("I1_MEMORY_LATE_ATOMIC_RESTORE_580_OK")
"""
            env = dict(os.environ, PYTHONPATH=os.pathsep.join(
                (str(out), str(ROOT / "src"))), PYTHONDONTWRITEBYTECODE="1")
            proc = subprocess.run([sys.executable, "-B", "-c", program],
                cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("I1_MEMORY_LATE_ATOMIC_RESTORE_580_OK", proc.stdout)
