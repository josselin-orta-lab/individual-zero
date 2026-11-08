"""Runnable Candidate-I software integration guards."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_g_reference_recurrence_falsifier as G
from i3.lab.p2_ecologies import world_for
from i3.lab.stage0_energy import energy_receipt
from i3.lab.stage0_revision import revision_receipt
from i3.modules.body import BodyLaws, CognitiveBudget
from i3.modules.genome import midpoint
from i3.modules.personal_relevance_candidate_h_mind import (
    PersonalRelevanceCandidateHMind)
from i3.modules.personal_shared_prior_candidate_i_mind import (
    POLICY, PersonalSharedPriorCandidateIMind)
from i3.runtime.life import run_life


def cap(body=(80., 80., 40., 80., 80.), *, water=False, inventory=()):
    return {
        "body": tuple(body),
        "here": (bool(water), ()),
        "neighbors": (None, None, None, None),
        "inventory": tuple(inventory),
    }


def prime(mind):
    mind.branch_memory = G.effect_memory()
    mind.opportunity_memory = G.recurrence_2_6_10()
    for key, delta in (
            (("se_deplacer",), (-2., -.2, -.4, 0., 0.)),
            (("attendre",), (-.35, -.2, -.4, .2, 0.)),
            (("dormir",), (3., -.35, -.4, 0., 4.))):
        mind.effects.observe(key, delta)
    mind._drift = mind.drift()


def prime_drink(mind):
    mind.effects.observe(("boire",), (-.5, -.2, 35., 0., 0.))
    base = (50.,) * 5
    after = (49.5, 49.8, 85., 50., 50.)
    mind.branch_memory.observe(
        ("boire", None), base, G.CognitiveWork(),
        CognitiveBudget(after, BodyLaws()))


class PersonalSharedPriorCandidateIRuntimeTests(unittest.TestCase):
    def test_omega_override_is_explicit_software_control(self):
        native = PersonalSharedPriorCandidateIMind(midpoint(), 31)
        zero = PersonalSharedPriorCandidateIMind(
            midpoint(), 31, first_contact_omega_override=0.0)
        self.assertEqual(
            native.first_contact_omega,
            midpoint()["genes"]["omega"])
        self.assertEqual(
            native.first_contact_omega_source,
            "GENOME_V4_OMEGA")
        self.assertEqual(zero.first_contact_omega, 0.0)
        self.assertEqual(
            zero.first_contact_omega_source,
            "SOFTWARE_OMEGA_ABLATION")

    def test_direct_first_contact_never_leaks_persistent_projector(self):
        mind = PersonalSharedPriorCandidateIMind(
            midpoint(), 37,
            observer_decision_diagnostics=True,
            observer_full_competition=True)
        prime(mind)
        body = (80., 80., 40., 80., 80.)
        budget = CognitiveBudget(body, BodyLaws())
        result = mind.decide(
            cap(body, water=True), budget)
        self.assertEqual(result[2], budget.work)
        self.assertIn(
            result[3]["candidate_i_route"],
            ("INFORMATION_FINAL", "P1.3_BASE_FINAL"))
        self.assertEqual(
            (mind.simulation_mode, mind.projection_accounting),
            ("reference", "chunk_end"))
        self.assertEqual(
            result[3]["persistent_simulation_mode"], "reference")
        self.assertEqual(
            result[3]["persistent_projection_accounting"], "chunk_end")
        if result[3]["candidate_i_route"] == "P1.3_BASE_FINAL":
            witness = result[3]["observer"]["score_witness"]
            self.assertTrue(witness)
            self.assertTrue(all(
                row["curiosity_bonus_applied"] == 0.0
                and row["risk_penalty_applied"] == 0.0
                for row in witness))

    def test_personal_drink_post_contact_matches_candidate_h_motor_and_work(self):
        left = PersonalSharedPriorCandidateIMind(
            midpoint(), 41,
            observer_decision_diagnostics=True)
        right = PersonalRelevanceCandidateHMind(
            midpoint(), 41,
            observer_decision_diagnostics=True)
        for mind in (left, right):
            prime(mind)
            prime_drink(mind)

        body = (80., 80., 40., 80., 80.)
        l = left.decide(cap(body), CognitiveBudget(body, BodyLaws()))
        r = right.decide(cap(body), CognitiveBudget(body, BodyLaws()))
        self.assertEqual(l[:3], r[:3])
        self.assertEqual(
            l[3]["observer"], r[3]["observer"])
        self.assertEqual(
            l[3]["candidate_i_route"],
            "POST_CONTACT_CANDIDATE_H")
        self.assertFalse(
            l[3]["candidate_i_first_contact_omega_used"])

    def test_existing_p2_development_zero_runtime_smoke_reduces(self):
        protocol = "STAGE1_CANDIDATE_I_RUNTIME_SOFTWARE_SMOKE"
        world = world_for("stable", "development", 0)
        life = run_life(
            midpoint(), world, 7101, 3,
            keep_trace=True,
            protocol=protocol,
            observer_mind_digest=True,
            observer_decision_diagnostics=True,
            observer_resource_acquisition=True,
            observer_full_competition=True,
            decision_policy=POLICY)
        self.assertEqual(
            life["experimental_policy"]["name"], POLICY)
        self.assertIn("candidate_i", life)
        self.assertEqual(
            life["candidate_i"]["persistent_simulation_mode"],
            "reference")
        self.assertEqual(
            life["candidate_i"]["persistent_projection_accounting"],
            "chunk_end")
        source = life["manifest"]["source"]["sha256"]
        energy = energy_receipt(
            life, expected_protocol=protocol,
            expected_source_sha256=source)
        revision = revision_receipt(
            life, expected_protocol=protocol,
            expected_source_sha256=source)
        self.assertEqual(
            energy["scientific_verdict"], "NOT_EVALUATED")
        self.assertEqual(
            revision["scientific_verdict"], "NOT_EVALUATED")

    def test_policy_is_opt_in_and_reference_does_not_construct_candidate_i(self):
        world = world_for("stable", "development", 0)
        reference = run_life(
            midpoint(), world, 7103, 1,
            decision_policy="reference",
            protocol="STAGE1_CANDIDATE_I_REFERENCE_SMOKE")
        self.assertNotEqual(
            reference.get("experimental_policy", {}).get("name"),
            POLICY)


if __name__ == "__main__":
    unittest.main()
