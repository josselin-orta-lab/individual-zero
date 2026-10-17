"""Stage10 pending-index fast cursor regression on generated natural I1 code."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class PendingCursorTests(unittest.TestCase):
    def test_exact_parity_exception_rejects_extra_changes(self):
        spec = importlib.util.spec_from_file_location("parity", ROOT / "scripts/test_i1_artifact_parity.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        source = (ROOT / "src/i1/modules/consolidation_pending_index.py").read_bytes()
        self.assertFalse(module._approved_pending_index_cursor(source, source))
        self.assertFalse(module._approved_pending_index_cursor(source, source + b"\n# drift"))

    def test_cursor_preserves_order_after_rebuild_and_retirement(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"), "--output", str(output)],
                capture_output=True, text=True, check=False)
            self.assertEqual(build.returncode, 0, build.stderr)
            script = """
from i1.modules.consolidation_pending_index import ChargedPendingEpisodeIndex
from types import SimpleNamespace
idx = ChargedPendingEpisodeIndex(policy_version="p1")
payloads = {f"episode:{n}":{"id":f"episode:{n}"} for n in range(200)}
idx._pending = dict(payloads)
idx._pending_order = list(payloads)
idx._rank_cursor = 70
idx._ranked = [payloads[k] for k in list(payloads)[:70]]
idx._seen_count = 200
idx._history_version = "h:0"
idx._cut = SimpleNamespace(world_step=300)
idx._target = 200
class Budget:
    config = SimpleNamespace(step_slot_uc=8, period_capacity_uc=8,
                             operation_costs={"episode_scan":1})
    open_world_step = 300
    consumed_step_uc = 0
    consumed_period_uc = 0
    def charge(self, *, operation, count):
        assert operation == "episode_scan" and count <= 8
        self.consumed_step_uc += count
        self.consumed_period_uc += count
        return SimpleNamespace(accepted=True, count=count)
budget = Budget()
selector = SimpleNamespace(policy=SimpleNamespace(version="p1", scan_uc_per_episode=1))
read_calls = []
def forbidden_reader(start, end):
    read_calls.append((start,end))
    raise AssertionError("rank may not read unseen episode payloads")
assert idx.advance(budget=budget, episode_count=200,
                   read_paid_slice=forbidden_reader, selector=selector) == 8
assert idx._rank_cursor == 78
assert idx._ranked == list(payloads.values())[:78]
assert budget.consumed_step_uc == 8
assert not read_calls
# The indexed slice and original insertion-order slice must be exactly equal.
for cursor in (0, 1, 70, 99, 199):
    for count in (1, 7, 30):
        expected = list(idx._pending.values())[cursor:cursor + count]
        actual = [idx._pending[k] for k in idx._pending_order[cursor:cursor + count]]
        assert expected == actual
# Retirement rebuild preserves the remaining ranked order, and is uncharged
# only here in a deliberately isolated, synthetic index fixture.
for key in ("episode:0", "episode:11", "episode:180"):
    del idx._pending[key]
removed = {"episode:0", "episode:11", "episode:180"}
idx._pending_order = [k for k in idx._pending_order if k not in removed]
assert idx._pending_order == list(idx._pending)
assert len(idx._pending_order) == 197
print("STAGE10_PENDING_CURSOR_ORDER_OK")
"""
            p = subprocess.run(
                [sys.executable, "-c", script], capture_output=True, text=True,
                check=False, env={"PYTHONPATH": str(output)})
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("STAGE10_PENDING_CURSOR_ORDER_OK", p.stdout)


if __name__ == "__main__":
    unittest.main()
