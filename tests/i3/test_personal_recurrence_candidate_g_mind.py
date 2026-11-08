"""No-omega personal-recurrence Candidate-G software integration tests."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_g_no_omega_integration as G
from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveFundingError
from i3.modules.personal_recurrence_candidate_g_mind import (
    PersonalRecurrenceCandidateGMind)
from i3.modules.reference_frontier_information_mind import (
    ReferenceFrontierInformationMind)
from i3.modules.reference_opportunity_memory_mind import (
    ReferenceOpportunityMemoryMind)


class PersonalRecurrenceCandidateGTests(unittest.TestCase):
    def test_candidate_composes_existing_paid_memories_without_omega(self):
        mind = G.make_mind()
        self.assertIsInstance(mind, PersonalRecurrenceCandidateGMind)
        self.assertIsInstance(mind, ReferenceOpportunityMemoryMind)
        self.assertIsInstance(mind, ReferenceFrontierInformationMind)
        self.assertFalse(hasattr(mind, "first_contact_omega"))
        self.assertEqual(
            (mind.simulation_mode, mind.projection_accounting),
            ("reference", "chunk_end"))
        self.assertEqual(
            mind.opportunity_memory.snapshot()["gaps"]["water"], ())

    def test_no_recurrence_support_never_activates_candidate_f(self):
        fx = G.decision_fixture(recurrence=False, omega=-1.0)
        self.assertEqual(
            fx["frontier_phase"],
            "FIRST_CONTACT_NO_RECURRENCE_SUPPORT")
        self.assertEqual(fx["decision_projection_mode"], "reference")
        self.assertEqual(fx["score_modes"], ["reference"])
        self.assertEqual(fx["after_mode"], ("reference", "chunk_end"))
        self.assertNotEqual(fx["funding"], "NO_PROCESSING_BUDGET")

    def test_personal_recurrence_activates_one_commensurate_candidate_f_decision(self):
        fx = G.decision_fixture(recurrence=True, omega=-1.0)
        self.assertEqual(
            fx["frontier_phase"],
            "FIRST_CONTACT_PERSONAL_RECURRENCE")
        self.assertEqual(fx["decision_projection_mode"], "candidate_f")
        self.assertEqual(fx["score_modes"], ["candidate_f"])
        self.assertEqual(
            fx["recurrence_status"],
            "COMPLETE_EMPIRICAL_RECURRENCE_ESTIMATE")
        self.assertEqual(fx["after_mode"], ("reference", "chunk_end"))
        self.assertFalse(fx["omega_witness_fields"])

    def test_genome_omega_is_observationally_irrelevant(self):
        low = G.decision_fixture(recurrence=True, omega=-1.0)
        high = G.decision_fixture(recurrence=True, omega=1.0)
        self.assertEqual(low["result"], high["result"])

        low_post = G.decision_fixture(drink=True, omega=-1.0)
        high_post = G.decision_fixture(drink=True, omega=1.0)
        self.assertEqual(low_post["result"], high_post["result"])

    def test_post_contact_uses_candidate_f_for_whole_active_decision(self):
        fx = G.decision_fixture(drink=True, omega=-1.0)
        self.assertEqual(fx["frontier_phase"], "POST_CONTACT_PERSONAL")
        self.assertEqual(fx["decision_projection_mode"], "candidate_f")
        self.assertEqual(fx["score_modes"], ["candidate_f"])
        self.assertEqual(fx["after_mode"], ("reference", "chunk_end"))

    def test_fail_closed_active_ceiling_restores_reference_mode(self):
        mind = G.make_mind(observer=True)
        G.prime_recurrence(mind)
        with patch(
            "i3.modules.personal_recurrence_candidate_g_mind.debit_cognition",
            side_effect=CognitiveFundingError("forced software boundary")):
            result = mind.decide(
                G.cap(), CognitiveBudget(G.BODY, BodyLaws()))
        self.assertEqual(result[3]["funding"], "NO_FUNDED_SCORE")
        self.assertEqual(
            (mind.simulation_mode, mind.projection_accounting),
            ("reference", "chunk_end"))

    def test_decision_does_not_mutate_personal_effects(self):
        mind = G.make_mind(observer=True)
        G.prime_recurrence(mind)
        before = deepcopy(mind.effects.stats)
        mind.decide(G.cap(), CognitiveBudget(G.BODY, BodyLaws()))
        self.assertEqual(mind.effects.stats, before)

    def test_frozen_gate_runs_without_prejudging_verdict(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as fh:
            report = G.run(fh.name)
        self.assertFalse(report["world_access"])
        self.assertEqual(report["lives"], 0)
        self.assertFalse(report["runtime_registered"])
        self.assertIn(
            report["verdict"],
            (
                "PERSONAL_RECURRENCE_CANDIDATE_G_INTEGRATION_PASS",
                "PERSONAL_RECURRENCE_CANDIDATE_G_INTEGRATION_FAIL",
            ))
        self.assertEqual(report["kernel"]["evaluated"], 80)
        print(
            "PERSONAL_RECURRENCE_CANDIDATE_G_INTEGRATION "
            + json.dumps({
                "verdict": report["verdict"],
                "rules": report["rules"],
                "fixtures": report["fixtures"],
                "kernel": report["kernel"],
                "omega_invariance": report["omega_invariance"],
            }, sort_keys=True))

    def test_import_does_not_load_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.personal_recurrence_candidate_g_mind; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
