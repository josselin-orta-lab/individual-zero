"""Prospective execution registration for the Stage-1 omega ADR-0015 gate.

This file is intentionally a software/preflight witness only. It never imports
World/runtime and never executes a life.
"""
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_omega_adr0015_design as D
from i3.lab import stage1_omega_adr0015_runner as R

BASELINE = "034349844ced2f3d6ba00efe7a0fdc42e74fbbaa"
EXPECTED_DESIGN_SHA256 = (
    "e4934b4994bc97043deee9b9760df9fe31481aeb8ed4d0a75715eebc5f5e5d48")
EXPECTED_PROTOCOL_SHA256 = (
    "125d708706bce266abb41446ef577dbe0096ba96d0e7be60169165e327d11944")
EXECUTION_BRANCH = "i3/stage1-omega-adr0015-execute2-20261107"
EXECUTION_WORKFLOW = ".github/workflows/i3-proposal-checks.yml"


class OmegaAdr0015ExecutionRegistrationTests(unittest.TestCase):
    def test_frozen_design_and_protocol_digests(self):
        self.assertEqual(D.plan()["sha256"], EXPECTED_DESIGN_SHA256)
        self.assertEqual(
            R.protocol_manifest()["sha256"], EXPECTED_PROTOCOL_SHA256)
        self.assertFalse(D.plan()["execution_authorized"])

    def test_replacement_execution_identity(self):
        self.assertEqual(
            EXECUTION_BRANCH,
            "i3/stage1-omega-adr0015-execute2-20261107")
        self.assertEqual(
            EXECUTION_WORKFLOW,
            ".github/workflows/i3-proposal-checks.yml")
        self.assertEqual(
            BASELINE,
            "034349844ced2f3d6ba00efe7a0fdc42e74fbbaa")

    def test_frozen_allocation_and_barriers(self):
        plan = D.plan()
        protocol = R.protocol_manifest()
        self.assertEqual(
            {row["world_seed"] for row in plan["selection_worlds"]},
            set(range(10072, 10120)))
        self.assertEqual(
            {row["world_seed"] for row in plan["validation_worlds"]},
            set(range(30120, 30168)))
        self.assertEqual(len(protocol["selection_shards"]), 16)
        self.assertEqual(len(protocol["validation_shards"]), 24)
        self.assertEqual(
            protocol["selection_barrier"],
            "ALL_16_COMPLETE_BEFORE_ANY_RANKING")
        self.assertEqual(
            protocol["validation_barrier"],
            "ALL_24_COMPLETE_BEFORE_GATE")
        self.assertEqual(protocol["retry_policy"], "NO_RETRY_NO_REPLACEMENT")
        self.assertEqual(protocol["reserve_policy"], "SEALED")

    def test_execution_registration_imports_no_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_omega_adr0015_design; "
            "import i3.lab.stage1_omega_adr0015_runner; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
