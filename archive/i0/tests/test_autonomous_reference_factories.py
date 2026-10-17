"""Stage10/11 autonomous reference factories must never create evaluation services."""
from __future__ import annotations

import subprocess
import sys
import unittest


class AutonomousFactoryTests(unittest.TestCase):
    def test_stage10_and_11_factory_chains_never_import_external_science(self):
        code = r'''
import importlib.abc
import sys

class NoExternalScience(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in ("lab.oracle", "lab.bench", "lab.evaluation_trace"):
            raise ImportError("scientific service forbidden: " + fullname)
        return None
sys.meta_path.insert(0, NoExternalScience())

from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime

stage10 = build_stage10_reference_runtime(
    start_fatigued=True, autonomous_mortal=True,
)
assert stage10.bench is None
assert stage10.run_step().command_primitive == "dormir"
assert stage10.run_step().source == "sleep"
assert stage10.journal.verify()

stage11 = build_stage11_reference_runtime(
    enable_geography=True, autonomous_mortal=True,
)
assert stage11.bench is None
assert stage11.run_step().execution_status == "applied"
assert stage11.journal.verify()
for forbidden in ("lab.oracle", "lab.bench", "lab.evaluation_trace"):
    assert forbidden not in sys.modules, forbidden
print("stage10_stage11_reference_factories_are_autonomous:OK")
'''
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=90,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "stage10_stage11_reference_factories_are_autonomous:OK",
            result.stdout,
        )

    def test_historical_default_factories_keep_their_old_evaluation_contract(self):
        from lab.stage9_reference_fixture import build_stage9_reference_runtime
        from lab.stage10_reference_fixture import build_stage10_reference_runtime
        from lab.stage11_reference_fixture import build_stage11_reference_runtime

        stage9 = build_stage9_reference_runtime()
        stage10 = build_stage10_reference_runtime()
        stage11 = build_stage11_reference_runtime()
        self.assertIsNotNone(stage9.bench)
        self.assertIsNotNone(stage10.bench)
        self.assertIsNotNone(stage11.bench)

    def test_mortal_and_evaluated_stage11_decisions_match_unchanged_world(self):
        from lab.stage11_reference_fixture import build_stage11_reference_runtime

        standalone = build_stage11_reference_runtime(autonomous_mortal=True)
        observed = build_stage11_reference_runtime()
        observed.stage3.substrate.enable_mortal_world()
        for _ in range(5):
            standalone_result = standalone.run_step()
            observed_result = observed.run_step()
            self.assertEqual(
                standalone_result.execution_status,
                observed_result.execution_status,
            )
            self.assertEqual(
                standalone_result.command_primitive,
                observed_result.command_primitive,
            )
            self.assertEqual(
                standalone.world.export_causal_state(),
                observed.world.export_causal_state(),
            )
            self.assertEqual(
                standalone.journal.canonical_bytes(),
                observed.journal.canonical_bytes(),
            )


if __name__ == "__main__":
    unittest.main()
