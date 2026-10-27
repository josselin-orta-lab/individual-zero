"""#467: technical before-body is not automatically autobiographical."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class PrebodyBoundary467(unittest.TestCase):
    def test_native_projection_is_still_fail_closed(self):
        with TemporaryDirectory() as folder:
            generated = Path(folder) / "generated"
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            code = """
from i1lab.stage2_runtime import STAGE2_AUTOBIOGRAPHICAL_POLICY as P2
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY as P7
from i1lab.journal_views import AutobiographicalPolicy
from i1lab.epistemic_guard import validate_lived_kind_fields
assert "body_before" not in P2.allowed_fields_by_kind["world_transition_experienced"]
assert "body_before" not in P7.allowed_fields_by_kind["world_transition_experienced"]
for policy in (P2, P7):
    policy.validate()
# The global I1 guard now supports a NEW explicitly versioned policy.
# Historical Stage2/Stage7 projections still do not grant this field.
validate_lived_kind_fields("world_transition_experienced", ("body_before",))
try:
    validate_lived_kind_fields("world_transition_experienced",
                               ("oracle_ground_truth",))
except ValueError:
    pass
else:
    raise AssertionError("hidden truth passed the DC-09 boundary")
print("I1_467_PREBODY_BOUNDARY_OK")
"""
            check = subprocess.run(
                [sys.executable, "-c", code],
                env={"PYTHONPATH": str(generated) + ":" + str(ROOT / "src")},
                capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertIn("I1_467_PREBODY_BOUNDARY_OK", check.stdout)


if __name__ == "__main__":
    unittest.main()
