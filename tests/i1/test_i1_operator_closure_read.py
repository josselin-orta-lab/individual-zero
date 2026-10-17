"""Stage2 operator closure read must not materialize journal.entries."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class OperatorClosureReadTests(unittest.TestCase):
    def test_closed_step_receipt_uses_constant_space_journal_access(self):
        with TemporaryDirectory() as folder:
            out = Path(folder) / "built"
            generated = subprocess.run([sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                "--output", str(out)], text=True, capture_output=True)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            code = r"""
from i1lab.stage2_runtime import ScriptedStage2Runtime
from types import SimpleNamespace
class ReadOnlyJournal:
    durable_wal_enabled = True
    head_hash = "a" * 64
    entry_count = 4000
    @property
    def entries(self):
        raise AssertionError("full journal copy forbidden")
    def iter_entries_reversed(self):
        yield SimpleNamespace(causal_event={
            "kind": "step_closed", "t_monde": 9,
            "attempt_ref": "attempt:9",
            "data": {"world_advance_count": 1},
        }, event_hash="b" * 64)
world = SimpleNamespace(
    capture_operator_world_frame=lambda *, t_monde: {"t_monde":t_monde},
    operator_world_geometry=lambda: {"width":10, "height":10},
)
obj = SimpleNamespace(
    journal=ReadOnlyJournal(),
    scheduler=SimpleNamespace(t_monde=9, active_attempt=None),
    world=world,
)
receipt = ScriptedStage2Runtime.capture_operator_closed_step(obj)
assert receipt["journal_event_count"] == 4000
assert receipt["journal_head_sha256"] == "a"*64
assert receipt["journal_closure_hash"] == "b"*64
assert receipt["frame"] == {"t_monde":9, "step_boundary":"committed"}
obj.scheduler.t_monde = 10
try:
    ScriptedStage2Runtime.capture_operator_closed_step(obj)
except RuntimeError:
    pass
else:
    raise AssertionError("incorrect closure clock accepted")
print("I1_OPERATOR_CLOSURE_CONSTANT_SPACE_OK")
"""
            run = subprocess.run([sys.executable, "-c", code], env={"PYTHONPATH":str(out)},
                                 text=True, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("I1_OPERATOR_CLOSURE_CONSTANT_SPACE_OK", run.stdout)


if __name__ == "__main__":
    unittest.main()
