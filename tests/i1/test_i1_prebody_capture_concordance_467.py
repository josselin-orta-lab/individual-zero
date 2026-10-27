"""#467: a physical before-state is not automatically a perceived before-state."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class PrebodyConcordance467(unittest.TestCase):
    def test_generated_i1_fail_closed_prebody_gate(self):
        with TemporaryDirectory() as folder:
            generated = Path(folder) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
            code = r"""
from i1lab.i1_natural_prebody_policy import (
    captured_prebody_matches_transition as concordant,
    LIVED_PREBODY_POLICY,
)
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY as OLD
visible = dict(energy=40.0, water=62.0, food=55.0, integrity=90.0)
physical = dict(visible)
assert concordant(captured_body=visible, physical_body_before=physical)
# An after-admission external change means the technical pre-action
# state was NOT the state witnessed at the waking capture.
for key in visible:
    changed = dict(physical); changed[key] += 1.0
    assert not concordant(captured_body=visible,
                          physical_body_before=changed)
for malformed in (
    dict(visible, oracle_ground_truth=1),
    dict(visible, water={"hidden": 1}),
    dict(visible, water=float("nan")),
    dict(visible, energy=True),
    dict(visible, food=-2),
    {k:v for k,v in visible.items() if k != "food"},
):
    assert not concordant(captured_body=visible,
                          physical_body_before=malformed)
assert "body_before" in LIVED_PREBODY_POLICY.allowed_fields_by_kind[
    "world_transition_experienced"]
assert "body_before" not in OLD.allowed_fields_by_kind[
    "world_transition_experienced"]
print("I1_467_PREBODY_CONCORDANCE_OK")
"""
            p = subprocess.run([sys.executable, "-c", code],
                env={"PYTHONPATH": str(generated)},
                capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("I1_467_PREBODY_CONCORDANCE_OK", p.stdout)


if __name__ == "__main__":
    unittest.main()
