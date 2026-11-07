"""Genome-v4 omega wiring into opt-in Candidate-F first contact."""
from inspect import signature
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_genomic_omega_candidate_f_wiring as G
from i3.modules.genomic_omega_candidate_f import GenomicOmegaCandidateFMind
from i3.modules.reference_memory_mind import ReferenceBranchMemoryMind


class GenomicOmegaCandidateFWiringTests(unittest.TestCase):
    def test_full_480_state_parity_with_frozen_explicit_omega(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "parity.json"
            report = G.run(path)
            self.assertEqual(json.loads(path.read_text()), report)

        self.assertEqual(report["total_states_compared"], 480)
        self.assertTrue(report["exact_statewise_parity"])
        self.assertEqual(report["first_mismatch_per_arm"], [])
        self.assertEqual(
            report["verdict"],
            "GENOMIC_OMEGA_WIRING_EXACTLY_REPRODUCES_FROZEN_EXPLICIT_OMEGA")
        self.assertTrue(report["genomic_adapter_reads_omega"])
        self.assertFalse(report["reference_mind_reads_omega"])
        self.assertFalse(report["runtime_policy_registered"])
        self.assertFalse(report["selection_authorized"])
        print(
            "GENOMIC_OMEGA_CANDIDATE_F_WIRING",
            json.dumps({
                "arms": report["arms"],
                "parity": report["exact_statewise_parity"],
                "verdict": report["verdict"],
            }, sort_keys=True))

    def test_adapter_configuration_and_genomic_value_are_exact(self):
        hopeful = G.make_genomic_mind(1.0)
        fearful = G.make_genomic_mind(-1.0)
        self.assertEqual(hopeful.simulation_mode, "candidate_f")
        self.assertEqual(
            hopeful.projection_accounting, "event_local_quadratic4")
        self.assertEqual(hopeful.first_contact_omega, 1.0)
        self.assertEqual(fearful.first_contact_omega, -1.0)
        self.assertIsInstance(hopeful, ReferenceBranchMemoryMind)
        self.assertEqual(hopeful.branch_records, 0)

    def test_caller_cannot_override_omega(self):
        params = signature(
            GenomicOmegaCandidateFMind.paid_water_first_contact).parameters
        self.assertNotIn("omega", params)

    def test_adapter_does_not_override_decide_or_learning(self):
        self.assertIs(
            GenomicOmegaCandidateFMind.decide,
            ReferenceBranchMemoryMind.decide)
        self.assertIs(
            GenomicOmegaCandidateFMind.prepare_learning,
            ReferenceBranchMemoryMind.prepare_learning)
        self.assertIs(
            GenomicOmegaCandidateFMind.learn_from_outcome,
            ReferenceBranchMemoryMind.learn_from_outcome)

    def test_reference_mind_source_remains_omega_blind(self):
        root = Path(__file__).resolve().parents[2] / "src/i3/modules"
        self.assertNotIn("omega", (root / "mind.py").read_text())
        self.assertNotIn(
            "omega", (root / "reference_memory_mind.py").read_text())

    def test_import_does_not_load_world_or_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.genomic_omega_candidate_f; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
