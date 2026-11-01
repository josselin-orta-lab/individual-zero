"""Execute an actually independent I1 Stage6 life, never an I0 alias."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from build_i1_fork import generate


class I1FirstPhysicalStep(unittest.TestCase):
    def test_separate_stage6_world_and_cognitive_owner(self):
        with TemporaryDirectory() as folder:
            output = Path(folder) / "isolated"
            generate(output)
            code = """
import sys
import i1.modules.stage6_planning as o
from i1lab.stage6_reference_fixture import build_stage6_reference_runtime
from i1lab.independent_journal_audit import audit_export_bytes
assert o.SimulatorPlanner.__module__.startswith('i1.')
life = build_stage6_reference_runtime(autonomous_mortal=True)
assert life.individual_id.startswith('i1-')
assert type(life.planning).__module__ == 'i1.modules.stage6_planning'
assert type(life.world).__module__ == 'i1lab.world'
assert life.stage3.substrate.bench is None
before = len(life.journal.entries)
result = life.run_step()
assert result.execution_status in ('applied', 'safety_block', 'dead')
assert len(life.journal.entries) > before
assert life.journal.verify()
audit_export_bytes(life.journal.canonical_bytes())
# Importing or running I1 must not drag frozen I0 modules into a live step.
assert not any(name == 'i0' or name.startswith('i0.') for name in sys.modules)
print('I1_REAL_STEP_OK:' + result.execution_status)
"""
            child = subprocess.run(
                [sys.executable, "-c", code],
                env={"PYTHONPATH": str(output) + ":" + str(
                    Path(__file__).resolve().parents[2] / "src"
                )},
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(child.returncode, 0, child.stderr)
            self.assertIn("I1_REAL_STEP_OK:", child.stdout)


if __name__ == "__main__":
    unittest.main()
