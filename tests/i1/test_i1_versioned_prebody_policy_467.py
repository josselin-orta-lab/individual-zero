"""#467: exact DC-09 pre-action body policy, not automatically active."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class NativePrebodyPolicy467(unittest.TestCase):
    def test_no_historical_projection_broadening(self):
        with TemporaryDirectory() as tmp:
            generated = Path(tmp) / "generated"
            a = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)], capture_output=True, text=True)
            self.assertEqual(a.returncode, 0, a.stderr)
            code = r"""
from types import SimpleNamespace
from i1lab.stage2_runtime import STAGE2_AUTOBIOGRAPHICAL_POLICY as P2
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY as P7
from i1lab.i1_natural_prebody_policy import LIVED_PREBODY_POLICY as NEW
from i1lab.epistemic_guard import validate_lived_kind_fields
assert NEW.version not in (P2.version, P7.version)
assert "body_before" not in P2.allowed_fields_by_kind["world_transition_experienced"]
assert "body_before" not in P7.allowed_fields_by_kind["world_transition_experienced"]
assert NEW.allowed_fields_by_kind["world_transition_experienced"] == (
    "t_monde", "position_after", "body_before", "body_after", "effects")
for policy in (P2, P7, NEW): policy.validate()
body_before = dict(energy=35., food=61., water=72., integrity=99.)
body_after = dict(energy=45., food=60., water=71., integrity=99.)
entry = SimpleNamespace(event_id="physical:3", causal_event=dict(
    kind="world_transition_experienced", t_monde=3,
    position_after=dict(x=2,y=4),
    body_before=body_before, body_after=body_after, effects=dict(rest=True)))
assert NEW.project(entry)["body_before"] == body_before
assert "body_before" not in P7.project(entry)
assert "body_before" not in P2.project(entry)
for poison in ({"oracle_ground_truth": "secret"}, {"water": {"hidden": 1}}):
    entry.causal_event["body_before"] = poison
    try: NEW.project(entry)
    except ValueError: pass
    else: raise AssertionError("unapproved hidden data crossed DC-09")
print("I1_467_VERSIONED_PREBODY_POLICY_OK")
"""
            z = subprocess.run(
                [sys.executable, "-c", code],
                env={"PYTHONPATH": str(generated)},
                capture_output=True, text=True)
            self.assertEqual(z.returncode, 0, z.stderr)
            self.assertIn("I1_467_VERSIONED_PREBODY_POLICY_OK", z.stdout)


if __name__ == "__main__":
    unittest.main()
