"""#490: absence of an autobiographical sleep-session boundary is explicit.

The Stage10 sleep-mode control events are technical custody, not a first-person
experience merely because they share the world step of a physical command.
This regression prevents L2 claims before a versioned, perceptual DC-09 source
has been defined and tested. It neither grants a new source nor changes I1.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class SleepBoundaryProjectionGap490(unittest.TestCase):
    def test_native_sleep_control_events_are_not_personal_memories(self):
        with TemporaryDirectory() as folder:
            generated = Path(folder) / "native"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            proof = r"""
from i1lab.stage2_runtime import STAGE2_AUTOBIOGRAPHICAL_POLICY as P2
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY as P7
from i1lab.i1_natural_prebody_policy import LIVED_PREBODY_POLICY as NEW
from i1lab.i1_natural_prebody_policy import (
    policy_for_proven_prebody_transition as selector)
from i1lab.journal import HashChainedJournal

# These are legitimate technical labels, but none is a personally
# projected event or evidence of voluntary re-admission.
technical = ("stage10_sleep_entered", "stage10_sleep_woke",
             "stage10_reduced_capture")
for policy in (P2, P7, NEW):
    policy.validate()
    assert all(kind not in policy.allowed_fields_by_kind
               for kind in technical)
    assert "perceptual_capture" not in policy.allowed_fields_by_kind
    assert "command_admitted" not in policy.allowed_fields_by_kind

assert "command_experienced" in NEW.allowed_fields_by_kind
assert "world_transition_experienced" in NEW.allowed_fields_by_kind
assert "body_before" in NEW.allowed_fields_by_kind[
    "world_transition_experienced"]
assert "body_before" not in P7.allowed_fields_by_kind[
    "world_transition_experienced"]

# An untrusted technical wake label, even in a hash-chained journal, cannot
# authorize the lived prebody policy without capture/admission/physical pairs.
journal = HashChainedJournal()
journal.append(event_id="technical:wake", causal_event={
    "emitter": "stage10-runtime", "kind": "stage10_sleep_woke",
    "t_monde": 4, "attempt_ref": "attempt:4",
    "data": {"world_step": 4, "reason": "alert"}})
assert selector(journal=journal, t_monde=4, attempt_ref="attempt:4",
                command_ref="unseen:command", physical_ref="unseen:body") is P7
print("I1_490_SLEEP_BOUNDARY_REMAINS_TECHNICAL_OK")
"""
            done = subprocess.run(
                [sys.executable, "-c", proof],
                env={"PYTHONPATH": str(generated)},
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertIn(
                "I1_490_SLEEP_BOUNDARY_REMAINS_TECHNICAL_OK", done.stdout,
            )


if __name__ == "__main__":
    unittest.main()
