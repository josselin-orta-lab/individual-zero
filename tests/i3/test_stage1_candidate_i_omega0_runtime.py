"""Pre-exposure checks for the frozen Candidate-I same-genome omega0 arm."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab.p2_ecologies import world_for
from i3.lab.stage0_energy import energy_receipt
from i3.lab.stage0_revision import revision_receipt
from i3.modules.genome import generation_zero
from i3.runtime.life import run_life

NATIVE = "personal_shared_prior_candidate_i_v1"
OMEGA0 = "personal_shared_prior_candidate_i_omega0_ablation_v1"
PROTOCOL = "STAGE1_CANDIDATE_I_OMEGA0_RUNTIME_PREFLIGHT"


def run(policy, genome, seed=7_490_001, horizon=6):
    return run_life(
        genome,
        world_for("stable", "development", 0),
        seed,
        horizon,
        protocol=PROTOCOL,
        decision_policy=policy,
        keep_trace=True,
        observer_mind_digest=True,
        observer_decision_diagnostics=True,
        observer_resource_acquisition=True,
        observer_full_competition=True,
    )


class CandidateIOmega0RuntimeTests(unittest.TestCase):
    def test_omega0_is_same_genome_candidate_i_with_only_zero_override(self):
        genome = generation_zero(901)
        before = deepcopy(genome)
        self.assertNotEqual(genome["genes"]["omega"], 0.0)

        native = run(NATIVE, genome)
        zero = run(OMEGA0, genome)

        self.assertEqual(genome, before)
        self.assertEqual(native["genome"], zero["genome"])
        self.assertEqual(
            native["manifest"]["genome"], zero["manifest"]["genome"])
        self.assertEqual(
            native["manifest"]["world"], zero["manifest"]["world"])

        self.assertEqual(
            native["experimental_policy"]["name"], NATIVE)
        self.assertEqual(
            zero["experimental_policy"]["name"], OMEGA0)
        self.assertEqual(
            zero["experimental_policy"]["candidate_class"],
            "PersonalSharedPriorCandidateIMind")
        self.assertEqual(
            zero["experimental_policy"]["native_genome_omega"],
            genome["genes"]["omega"])
        self.assertEqual(
            zero["experimental_policy"]["applied_first_contact_omega"], 0.0)
        self.assertEqual(
            zero["experimental_policy"]["omega_source"],
            "SAME_GENOME_SOFTWARE_ABLATION")
        self.assertEqual(
            zero["experimental_policy"]["only_allowed_difference"],
            "first_contact_omega_override_0.0")

        self.assertEqual(
            native["candidate_i"]["first_contact_omega"],
            genome["genes"]["omega"])
        self.assertEqual(
            native["candidate_i"]["omega_source"], "GENOME_V4_OMEGA")
        self.assertEqual(
            zero["candidate_i"]["first_contact_omega"], 0.0)
        self.assertEqual(
            zero["candidate_i"]["applied_first_contact_omega"], 0.0)
        self.assertEqual(
            zero["candidate_i"]["native_genome_omega"],
            genome["genes"]["omega"])
        self.assertEqual(
            zero["candidate_i"]["omega_source"],
            "SAME_GENOME_SOFTWARE_ABLATION")
        self.assertEqual(
            zero["candidate_i"]["omega_ablation"],
            "FIRST_CONTACT_ONLY_SAME_GENOME")

    def test_both_candidate_i_runtime_arms_reduce_on_exposed_index_zero(self):
        genome = generation_zero(901)
        for policy in (NATIVE, OMEGA0):
            with self.subTest(policy=policy):
                life = run(policy, genome, seed=7_490_003, horizon=4)
                source = life["manifest"]["source"]["sha256"]
                energy = energy_receipt(
                    life,
                    expected_protocol=PROTOCOL,
                    expected_source_sha256=source)
                revision = revision_receipt(
                    life,
                    expected_protocol=PROTOCOL,
                    expected_source_sha256=source)
                self.assertEqual(
                    energy["schema"], "i3-stage0-energy/v1")
                self.assertEqual(
                    revision["scientific_verdict"], "NOT_EVALUATED")
                self.assertEqual(
                    life["candidate_i"]["persistent_simulation_mode"],
                    "reference")
                self.assertEqual(
                    life["candidate_i"]["persistent_projection_accounting"],
                    "chunk_end")

    def test_omega0_arm_is_opt_in_and_does_not_change_other_policy_names(self):
        genome = generation_zero(901)
        reference = run_life(
            genome,
            world_for("stable", "development", 0),
            7_490_005,
            1,
            protocol=PROTOCOL,
            decision_policy="reference")
        native = run(NATIVE, genome, seed=7_490_005, horizon=1)
        zero = run(OMEGA0, genome, seed=7_490_005, horizon=1)

        self.assertNotIn("candidate_i", reference)
        self.assertEqual(native["experimental_policy"]["name"], NATIVE)
        self.assertEqual(zero["experimental_policy"]["name"], OMEGA0)
        self.assertEqual(
            native["candidate_i"]["omega_source"], "GENOME_V4_OMEGA")
        self.assertEqual(
            zero["candidate_i"]["omega_source"],
            "SAME_GENOME_SOFTWARE_ABLATION")


if __name__ == "__main__":
    unittest.main()
