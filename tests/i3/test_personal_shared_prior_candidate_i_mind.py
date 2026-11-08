"""Runnable Candidate-I software integration guards."""
from copy import deepcopy
from pathlib import Path
import sys
from types import MethodType
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_g_reference_recurrence_falsifier as G
from i3.lab.p2_ecologies import world_for
from i3.lab.stage0_energy import energy_receipt
from i3.lab.stage0_revision import (
    _normalize_processing_status, revision_receipt)
from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork, debit_cognition)
from i3.modules.genome import generation_zero, midpoint
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

    def test_supported_water_does_not_bypass_unknown_food_first_contact(self):
        mind = PersonalSharedPriorCandidateIMind(
            midpoint(), 43,
            observer_decision_diagnostics=True)
        prime(mind)
        prime_drink(mind)
        body = (80., 30., 40., 80., 80.)
        mixed = {
            "body": body,
            "here": (True, ()),
            "neighbors": (None, None, None, None),
            "inventory": (("new-food", 1),),
        }
        result = mind.decide(
            mixed, CognitiveBudget(body, BodyLaws()))
        self.assertNotEqual(
            result[3]["candidate_i_route"],
            "POST_CONTACT_CANDIDATE_H")
        self.assertGreaterEqual(
            result[3]["candidate_i_direct_trial_count"], 1)

    def test_supported_food_does_not_bypass_unknown_water_first_contact(self):
        mind = PersonalSharedPriorCandidateIMind(
            midpoint(), 47,
            observer_decision_diagnostics=True)
        prime(mind)
        mind.effects.observe(
            ("manger", "tok0"), (0., 30., 0., 0., 0.))
        body = (80., 30., 40., 80., 80.)
        mixed = {
            "body": body,
            "here": (True, ()),
            "neighbors": (None, None, None, None),
            "inventory": (("known-food", 1),),
        }
        result = mind.decide(
            mixed, CognitiveBudget(body, BodyLaws()))
        self.assertNotEqual(
            result[3]["candidate_i_route"],
            "POST_CONTACT_CANDIDATE_H")
        self.assertGreaterEqual(
            result[3]["candidate_i_direct_trial_count"], 1)


    def test_fallback_receipt_reports_complete_stage_a_and_single_real_perception(self):
        mind = PersonalSharedPriorCandidateIMind(
            midpoint(), 53,
            observer_decision_diagnostics=True,
            observer_full_competition=True)
        body = (80., 80., 40., 80., 80.)
        budget = CognitiveBudget(body, BodyLaws())
        result = mind.decide(
            cap(body, water=True), budget)
        info = result[3]

        self.assertEqual(
            info["candidate_i_route"], "P1.3_BASE_FINAL")
        keys = ("cycles", "simulated_steps", "memory_items", "replays")
        for key in keys:
            self.assertEqual(
                info["candidate_i_stage_a_work"][key]
                + info["candidate_i_stage_b_work"][key],
                info["candidate_i_total_work"][key])
        stage_a = CognitiveWork(**info["candidate_i_stage_a_work"])
        total = CognitiveWork(**info["candidate_i_total_work"])
        stage_body, _ = debit_cognition(body, BodyLaws(), stage_a)
        final_body, _ = debit_cognition(body, BodyLaws(), total)
        self.assertTrue(all(
            abs(a - b) <= 1e-12
            for a, b in zip(
                stage_body, info["candidate_i_stage_a_body_after"])))
        self.assertTrue(all(
            abs(a - b) <= 1e-12
            for a, b in zip(
                final_body, info["candidate_i_body_after_cognition"])))
        self.assertGreaterEqual(
            info["candidate_i_stage_a_work"]["cycles"], 3)
        # Probe perception is detached; fallback retains exactly one real
        # first-person perception at the current cell.
        self.assertEqual(mind.hist[(0, 0)][0], 1)
        witness = info["observer"]["score_witness"]
        self.assertTrue(witness)
        self.assertTrue(all(
            row["curiosity_bonus_applied"] == 0.0
            and row["risk_penalty_applied"] == 0.0
            for row in witness))

    def test_frozen_complete_option_set_routes_cover_s2_cases(self):
        body = (80., 30., 40., 80., 80.)

        def run_case(*, water=False, inventory=(),
                     drink_supported=False, supported_foods=()):
            mind = PersonalSharedPriorCandidateIMind(
                midpoint(), 59,
                observer_decision_diagnostics=True,
                observer_full_competition=True)
            prime(mind)
            if drink_supported:
                prime_drink(mind)
            for index, external in enumerate(supported_foods):
                internal = f"tok{index}"
                mind.tokens[external] = internal
                mind.external[internal] = external
                mind.effects.observe(
                    ("manger", internal),
                    (0., 30., 0., 0., 0.))
            return mind.decide(
                cap(body, water=water, inventory=inventory),
                CognitiveBudget(body, BodyLaws()))[3]

        cases = {
            "no_trial": (run_case(), 0),
            "water_only": (run_case(water=True), 1),
            "one_unknown_food": (
                run_case(inventory=(("food-a", 1),)), 1),
            "water_plus_one_unknown_food": (
                run_case(
                    water=True,
                    inventory=(("food-a", 1),)), 2),
            "two_unknown_foods": (
                run_case(
                    inventory=(("food-a", 1), ("food-b", 1))), 2),
            "water_plus_two_unknown_foods": (
                run_case(
                    water=True,
                    inventory=(("food-a", 1), ("food-b", 1))), 3),
            "supported_plus_unsupported": (
                run_case(
                    water=True, drink_supported=True,
                    inventory=(("food-a", 1),)), 1),
        }
        for name, (info, expected) in cases.items():
            with self.subTest(name=name):
                self.assertEqual(
                    info["candidate_i_direct_trial_count"], expected)
                self.assertIn(
                    info["candidate_i_route"],
                    ("INFORMATION_FINAL", "P1.3_BASE_FINAL"))

        supported = run_case(
            water=True, drink_supported=True,
            inventory=(("known-food", 1),),
            supported_foods=("known-food",))
        self.assertEqual(
            supported["candidate_i_route"],
            "POST_CONTACT_CANDIDATE_H")
        self.assertFalse(
            supported["candidate_i_first_contact_omega_used"])

    def test_same_genome_omega_ablation_is_inert_post_contact(self):
        genome = generation_zero(901)
        self.assertNotEqual(genome["genes"]["omega"], 0.0)
        native = PersonalSharedPriorCandidateIMind(
            genome, 61,
            observer_decision_diagnostics=True)
        zero = PersonalSharedPriorCandidateIMind(
            genome, 61,
            first_contact_omega_override=0.0,
            observer_decision_diagnostics=True)
        for mind in (native, zero):
            prime(mind)
            prime_drink(mind)
        body = (80., 80., 40., 80., 80.)
        left = native.decide(
            cap(body), CognitiveBudget(body, BodyLaws()))
        right = zero.decide(
            cap(body), CognitiveBudget(body, BodyLaws()))
        self.assertEqual(left[:3], right[:3])
        self.assertEqual(left[3]["observer"], right[3]["observer"])
        self.assertEqual(
            left[3]["candidate_i_route"], "POST_CONTACT_CANDIDATE_H")
        self.assertEqual(
            right[3]["candidate_i_route"], "POST_CONTACT_CANDIDATE_H")
        self.assertFalse(left[3]["candidate_i_first_contact_omega_used"])
        self.assertFalse(right[3]["candidate_i_first_contact_omega_used"])

    def test_probe_unfunded_restores_detached_state_and_normalizes_reducer_receipt(self):
        mind = PersonalSharedPriorCandidateIMind(
            midpoint(), 67,
            observer_decision_diagnostics=True)
        before = {
            "map": deepcopy(mind.map),
            "hist": deepcopy(mind.hist),
            "tokens": deepcopy(mind.tokens),
            "external": deepcopy(mind.external),
            "unknown_present": hasattr(mind, "_unknown"),
            "unknown": deepcopy(getattr(mind, "_unknown", None)),
            "presence_present": hasattr(mind, "_presence"),
            "presence": deepcopy(getattr(mind, "_presence", None)),
            "rng": mind.rng.getstate(),
            "budget_rng": mind._budget_rng.getstate(),
        }

        def fail_after_perception(self, **kwargs):
            self.map[(99, 99)] = (True, ())
            self.hist[(99, 99)] = [1, 1.0, {}]
            self.rng.random()
            return {
                "status": "UNFUNDED",
                "probe_funding": "NO_FUNDED_SCORE",
                "work": CognitiveWork(),
                "body_after_computation": kwargs["budget"].remaining,
                "forecast_work_ceiling": kwargs["budget"].work,
                "offered_options": len(kwargs["opts"]),
                "offered_families": self._observer_option_families(
                    row[0] for row in kwargs["opts"]),
            }

        mind._first_contact_score = MethodType(
            fail_after_perception, mind)
        body = (80., 80., 40., 80., 80.)
        result = mind.decide(
            cap(body, water=True),
            CognitiveBudget(body, BodyLaws()))
        info = result[3]
        self.assertEqual(
            info["funding"], "NO_FUNDED_RELEVANCE_PROBE")
        self.assertEqual(
            info["candidate_h_probe_funding"], "NO_FUNDED_SCORE")
        self.assertEqual(mind.map, before["map"])
        self.assertEqual(mind.hist, before["hist"])
        self.assertEqual(mind.tokens, before["tokens"])
        self.assertEqual(mind.external, before["external"])
        self.assertEqual(
            hasattr(mind, "_unknown"), before["unknown_present"])
        self.assertEqual(
            getattr(mind, "_unknown", None), before["unknown"])
        self.assertEqual(
            hasattr(mind, "_presence"), before["presence_present"])
        self.assertEqual(
            getattr(mind, "_presence", None), before["presence"])
        self.assertEqual(mind.rng.getstate(), before["rng"])
        self.assertEqual(
            mind._budget_rng.getstate(), before["budget_rng"])
        normalized = _normalize_processing_status(
            {"info": info},
            {
                "decision_funding": info["funding"],
                "decision_outcome":
                    info["observer"]["decision_outcome"],
            })
        self.assertEqual(normalized["normalized"], "NO_FUNDED_SCORE")
        self.assertTrue(normalized["processing_paid"])
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])

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
            energy["schema"], "i3-stage0-energy/v1")
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
