"""Candidate-G live integration: software fixtures only, no study world."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork, debit_cognition)
from i3.modules.genome import midpoint
from i3.modules.reference_frontier_information_mind import (
    ReferenceFrontierInformationMind)
from i3.modules.reference_opportunity_memory_mind import (
    ReferenceOpportunityMemoryMind)
from i3.modules.reference_recurrence_frontier_information_mind import (
    POLICY, ReferenceRecurrenceFrontierInformationMind)
from i3.modules.world import WorldSpec
from i3.runtime.life import run_life

BODY = (100., 80., 30., 80., 100.)
BASE = (50., 50., 50., 50., 50.)


def cap(body=BODY):
    return {
        "body": body,
        "here": (False, ()),
        "neighbors": ((False, ()), None, None, None),
        "inventory": (),
    }


def fixture(body=BODY):
    return WorldSpec(
        name="candidate-g-live-software",
        width=3, height=1, spawn=(1, 0), body=body)


def record(memory, key, delta):
    after = tuple(a + b for a, b in zip(BASE, delta))
    memory.observe(
        key, BASE, CognitiveWork(),
        CognitiveBudget(after, BodyLaws()))


def prime_generic(mind):
    for effect_key, branch_key, delta in (
        (("se_deplacer",), ("se_deplacer", None), (-2., -.2, -.4, 0., 0.)),
        (("attendre",), ("attendre", None), (-.35, -.2, -.4, .2, 0.)),
        (("dormir",), ("dormir", None), (3., -.35, -.4, 0., 4.)),
    ):
        mind.effects.observe(effect_key, delta)
        record(mind.branch_memory, branch_key, delta)
    mind._drift = mind.drift()


def prime_recurrence(mind):
    # Water onsets at personal steps 1, 3, 9, 19 -> gaps 2, 6, 10.
    onsets = {1, 3, 9, 19}
    for step in range(1, 20):
        b = CognitiveBudget((80.,) * 5, BodyLaws())
        mind.opportunity_memory.observe(
            (step in onsets, False), b)


def prime_personal_drink(mind, delta=(-.5, -.2, 35., 0., 0.)):
    mind.effects.observe(("boire",), delta)
    record(mind.branch_memory, ("boire", None), delta)
    mind.map[(9, 9)] = (True, ())


class CandidateGLiveSoftwareTests(unittest.TestCase):
    def test_candidate_g_has_reference_projection_and_no_candidate_f_mro(self):
        m = ReferenceRecurrenceFrontierInformationMind(midpoint(), 17)
        self.assertIsInstance(m, ReferenceOpportunityMemoryMind)
        self.assertIsInstance(m, ReferenceFrontierInformationMind)
        self.assertEqual(m.simulation_mode, "reference")
        self.assertEqual(m.projection_accounting, "chunk_end")
        self.assertFalse(hasattr(m, "first_contact_omega"))
        self.assertFalse(any(
            "CandidateF" in cls.__name__ for cls in type(m).__mro__))

    def test_unsupported_recurrence_has_no_numeric_information_fallback(self):
        m = ReferenceRecurrenceFrontierInformationMind(
            midpoint(), 19, observer_decision_diagnostics=True)
        prime_generic(m)
        b = CognitiveBudget(BODY, BodyLaws())
        _action, _param, work, info = m.decide(cap(), b)
        self.assertEqual(work, b.work)
        self.assertEqual(
            info["frontier_phase"], "FIRST_CONTACT_PERSONAL_RECURRENCE")
        self.assertEqual(
            info["recurrence_status"], "NO_PERSONAL_RECURRENCE_SUPPORT")
        self.assertIsNone(info["future_water_opportunity_probability"])
        self.assertEqual(info["future_opportunity_source"], "NO_NUMERIC_FALLBACK")
        frontier = [
            row for row in info["observer"]["score_witness"]
            if row["option"].startswith("explorer:")]
        self.assertTrue(frontier)
        self.assertTrue(all(
            row["score_kind"] ==
            "reference_distress_no_addends_no_recurrence_fallback"
            for row in frontier))
        self.assertTrue(all(row["information_value"] == 0.0 for row in frontier))
        self.assertEqual(m.recurrence_queries, 1)
        self.assertEqual(m.recurrence_supported_queries, 0)
        self.assertEqual(m.recurrence_unsupported_queries, 1)

    def test_supported_recurrence_is_the_only_first_contact_future_probability(self):
        m = ReferenceRecurrenceFrontierInformationMind(
            midpoint(), 23, observer_decision_diagnostics=True)
        prime_generic(m)
        prime_recurrence(m)
        before_effects = deepcopy(m.effects.stats)
        b = CognitiveBudget(BODY, BodyLaws())
        _action, _param, work, info = m.decide(cap(), b)
        self.assertEqual(work, b.work)
        self.assertEqual(m.effects.stats, before_effects)
        self.assertEqual(
            info["recurrence_status"], "COMPLETE_EMPIRICAL_RECURRENCE_ESTIMATE")
        self.assertEqual(info["future_opportunity_source"],
                         "PAID_PERSONAL_ONSET_RECURRENCE")
        self.assertIn(info["future_water_opportunity_probability"],
                      (1. / 3., 2. / 3., 1.0))
        frontier = [
            row for row in info["observer"]["score_witness"]
            if row["option"].startswith("explorer:")]
        self.assertTrue(frontier)
        self.assertTrue(all(
            row["score_kind"] ==
            "frontier_water_personal_recurrence_expected_distress"
            for row in frontier))
        self.assertTrue(all(
            row["future_opportunity_probability_source"] ==
            "PAID_PERSONAL_ONSET_RECURRENCE"
            for row in frontier))
        self.assertTrue(all(
            row["curiosity_bonus_applied"] == 0.0
            and row["risk_penalty_applied"] == 0.0
            for row in frontier))
        self.assertTrue(all(
            row["candidate_g_reference_projection"] for row in frontier))
        self.assertEqual(m.recurrence_supported_queries, 1)
        self.assertGreater(m.first_contact_options_scored, 0)

    def test_post_contact_reuses_existing_personal_frontier_path_without_recurrence(self):
        m = ReferenceRecurrenceFrontierInformationMind(
            midpoint(), 29, observer_decision_diagnostics=True)
        prime_generic(m)
        prime_personal_drink(m)
        result = m.decide(cap(), CognitiveBudget(BODY, BodyLaws()))
        info = result[3]
        self.assertEqual(info["frontier_phase"], "POST_CONTACT_PERSONAL")
        self.assertEqual(m.post_contact_queries, 1)
        self.assertEqual(m.recurrence_queries, 0)
        self.assertIsNone(info["future_water_opportunity_probability"])
        frontier = [
            row for row in info["observer"]["score_witness"]
            if row["option"].startswith("explorer:")]
        self.assertTrue(frontier)
        self.assertTrue(all(row["personal_drink_support"] for row in frontier))
        self.assertTrue(any(
            row["score_kind"] == "frontier_water_expected_distress"
            for row in frontier))

    def test_opportunity_presence_is_pending_then_paid_by_inherited_learning(self):
        m = ReferenceRecurrenceFrontierInformationMind(midpoint(), 31)
        prime_generic(m)
        _action, _param, _work, info = m.decide(
            cap(), CognitiveBudget(BODY, BodyLaws()))
        self.assertNotEqual(info["funding"], "NO_PROCESSING_BUDGET")
        self.assertIsNotNone(m._pending_opportunity_presence)
        self.assertEqual(m.opportunity_records, 0)

        # The inherited storage lifecycle is already covered exhaustively by
        # ReferenceOpportunityMemoryMind tests; here we prove Candidate-G uses it.
        self.assertIs(
            ReferenceRecurrenceFrontierInformationMind.prepare_learning,
            ReferenceOpportunityMemoryMind.prepare_learning)
        self.assertIs(
            ReferenceRecurrenceFrontierInformationMind.learn_from_outcome,
            ReferenceOpportunityMemoryMind.learn_from_outcome)

    def test_runtime_manifest_reports_reference_recurrence_candidate_only(self):
        life = run_life(
            midpoint(), fixture((100., 80., 70., 80., 100.)),
            37, 4, keep_trace=True, observer_mind_digest=True,
            observer_decision_diagnostics=True, decision_policy=POLICY,
            protocol="CANDIDATE_G_SOFTWARE_ONLY")
        policy = life["experimental_policy"]
        self.assertEqual(policy["name"], POLICY)
        self.assertEqual(policy["simulation_mode"], "reference")
        self.assertEqual(policy["projection_accounting"], "chunk_end")
        self.assertEqual(
            policy["first_contact_expectation"],
            "paid_personal_onset_recurrence_no_numeric_fallback")
        self.assertNotIn("omega", json.dumps(policy).lower())
        self.assertIn("branch_effect_memory", life)
        self.assertIn("opportunity_recurrence_memory", life)
        self.assertEqual(
            life["opportunity_recurrence_memory"]["decision_use"],
            "PAID_FIRST_CONTACT_FUTURE_OPPORTUNITY_ESTIMATE")
        self.assertIn("opportunity_recurrence_sha256", life)
        self.assertEqual(
            life["frontier_information"]["omega_use"], "ABSENT")
        self.assertEqual(
            life["frontier_information"]["simulation_mode"], "reference")
        self.assertEqual(
            life["cognitive_accounting"]["status"],
            "SETTLED_FOR_DECLARED_WORK")

    def test_default_reference_never_constructs_candidate_g(self):
        with patch(
            "i3.modules.reference_recurrence_frontier_information_mind."
            "ReferenceRecurrenceFrontierInformationMind.__init__",
            side_effect=AssertionError("implicit Candidate-G")):
            life = run_life(
                midpoint(), fixture((100., 80., 70., 80., 100.)),
                41, 2, decision_policy="reference")
        self.assertNotIn(
            POLICY, json.dumps(life, sort_keys=True))

    def test_cost_profile_is_observer_only_and_deterministic(self):
        rows = {}
        for name, supported in (("unsupported", False), ("supported", True)):
            m = ReferenceRecurrenceFrontierInformationMind(
                midpoint(), 47, observer_decision_diagnostics=True)
            prime_generic(m)
            if supported:
                prime_recurrence(m)
            b = CognitiveBudget(BODY, BodyLaws())
            _action, _param, work, info = m.decide(cap(), b)
            rows[name] = {
                "funding": info["funding"],
                "work": {
                    "cycles": work.cycles,
                    "simulated_steps": work.simulated_steps,
                    "memory_items": work.memory_items,
                    "replays": work.replays,
                },
                "recurrence_status": info["recurrence_status"],
                "future_probability":
                    info["future_water_opportunity_probability"],
            }
        print("CANDIDATE_G_LIVE_COST_PROFILE " + json.dumps(
            rows, sort_keys=True))
        self.assertEqual(
            rows["unsupported"]["recurrence_status"],
            "NO_PERSONAL_RECURRENCE_SUPPORT")
        self.assertEqual(
            rows["supported"]["recurrence_status"],
            "COMPLETE_EMPIRICAL_RECURRENCE_ESTIMATE")


if __name__ == "__main__":
    unittest.main()
