"""Controlled hard process exits reveal the precise v1.3.1 RAM journal window.

These tests are negative capability evidence, NOT proof of crash durability.
All os._exit injections occur in disposable subprocesses. The test observer's
fsynced witness is not I0's journal and is not independent physical truth.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from lab.independent_journal_audit import audit_export_file


# The first coherent step is explicitly archived before the second begins.
# Only the explicit archive survives a hard exit in the current architecture.
_WORKER = r"""
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch
from lab.journal_export import export_immutable_journal
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import Command

case, base_file, witness_file, death_file = sys.argv[1:]
instance = build_stage4_reference_runtime(autonomous_mortal=True)
sub = instance.stage3.substrate
sub.open_step()
assert sub.execute(Command("attendre")).status == "applied"
export_immutable_journal(instance.journal, Path(base_file))

def record_physical_outcome(kind):
    # Witness is deliberately NOT part of I0. It is a controlled test
    # artifact that the parent uses to locate the injected exit boundary.
    report = {
        "boundary": kind,
        "world_step": sub.scheduler.t_monde,
        "position": instance.world.position.as_dict(),
        "body": instance.world.body.as_dict(),
    }
    with open(witness_file, "w", encoding="utf-8") as stream:
        json.dump(report, stream, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())

if case == "after_physical_apply":
    actual_apply = instance.world.apply
    def apply_then_die(command, *, t_monde):
        result = actual_apply(command, t_monde=t_monde)
        record_physical_outcome("after_physical_apply_before_journal_receipt")
        os._exit(72)
    sub.open_step()
    with patch.object(instance.world, "apply", side_effect=apply_then_die):
        sub.execute(Command("attendre"))
elif case in ("after_death", "after_death_export"):
    position = instance.world.position.as_dict()
    instance.world.apply_scenario_event("set_lethal_zone", {
        "position": position, "active": True,
    })
    sub.open_step()
    result = sub.execute(Command("attendre"))
    assert result.status == "dead"
    if case == "after_death_export":
        export_immutable_journal(instance.journal, Path(death_file))
    record_physical_outcome(case)
    os._exit(74 if case == "after_death_export" else 73)
else:
    raise RuntimeError("unknown controlled exit boundary")
raise AssertionError("hard exit was not reached")
"""


class AbruptCrashWindowTests(unittest.TestCase):
    def test_exported_prefix_survives_but_unexported_physical_or_terminal_steps_do_not(self):
        cases = (
            ("after_physical_apply", 72, 0),
            ("after_death", 73, 0),
            ("after_death_export", 74, 1),
        )
        for case, expected_exit, expected_durable_deaths in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                prefix = Path(tmp) / "prior-complete-life-prefix.jsonl"
                witness = Path(tmp) / "test-observer-boundary.json"
                death = Path(tmp) / "explicit-postmortem-export.jsonl"
                completed = subprocess.run(
                    [sys.executable, "-c", _WORKER, case,
                     str(prefix), str(witness), str(death)],
                    capture_output=True, text=True, timeout=35,
                )
                self.assertEqual(completed.returncode, expected_exit, completed.stderr)
                self.assertTrue(prefix.is_file())
                self.assertTrue(witness.is_file())
                marker = json.loads(witness.read_text(encoding="utf-8"))
                self.assertEqual(marker["world_step"], 2)
                # The only automatically preserved journal image is the
                # previously operator-requested fsynced export (step 1).
                old = audit_export_file(prefix)
                self.assertEqual(old.world_steps_closed, 1)
                self.assertEqual(old.terminal_deaths, 0)
                self.assertEqual(death.is_file(), bool(expected_durable_deaths))
                if expected_durable_deaths:
                    final = audit_export_file(death)
                    self.assertEqual(final.world_steps_closed, 2)
                    self.assertEqual(final.terminal_deaths, 1)
                # It would be a forbidden resurrection to "recover" this
                # identity from the prior prefix and claim the life continued.


if __name__ == "__main__":
    unittest.main()
