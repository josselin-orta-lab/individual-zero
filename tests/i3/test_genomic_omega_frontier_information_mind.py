"""Genome-v4 omega live frontier integration: software fixtures only."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork)
from i3.modules.genome import midpoint, validate
from i3.archive.stage1.modules.genomic_omega_candidate_f import GenomicOmegaCandidateFMind
from i3.archive.stage1.modules.genomic_omega_frontier_information_mind import (
    GenomicOmegaFrontierInformationMind, POLICY, STOP_AFTER_PREFIX)
from i3.modules.reference_frontier_information_mind import (
    ReferenceFrontierInformationMind)
from i3.modules.reference_memory_mind import ReferenceBranchMemoryMind
from i3.modules.rms_three_leaf_target_prior import (
    paid_rms_three_leaf_target_prior,
    rms_three_leaf_target_prior_work_ceiling)
from i3.modules.water_future_opportunity import (
    paid_water_one_future_opportunity_value,
    water_one_future_opportunity_work_ceiling)
from i3.modules.world import WorldSpec
from i3.runtime.competition_observer import capture_competition
from i3.runtime.life import run_life

BODY = (100., 80., 30., 80., 100.)
BASE = (50., 50., 50., 50., 50.)
EXPLORE = (("se_deplacer",),)


def genome(omega):
    g = midpoint()
    g["genes"]["omega"] = omega
    validate(g)
    return g


def cap(body=BODY):
    # One personally visible passable neighbor plus three edges. The neighbor
    # has unseen adjacent cells, so ordinary P1.3 proposes a frontier explorer.
    return {
        "body": body,
        "here": (False, ()),
        "neighbors": ((False, ()), None, None, None),
        "inventory": (),
    }


def fixture(body=BODY):
    return WorldSpec(
        name="genomic-omega-live-frontier-software",
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


def prime_personal_drink(mind, delta=(-.5, -.2, 35., 0., 0.)):
    mind.effects.observe(("boire",), delta)
    record(mind.branch_memory, ("boire", None), delta)
    # Personal water incidence for the old post-contact frontier belief. It is
    # deliberately disconnected from the current local frontier.
    mind.map[(9, 9)] = (True, ())


class GenomicOmegaLiveFrontierTests(unittest.TestCase):
    def test_candidate_composes_existing_controls_without_replacing_learning(self):
        m = GenomicOmegaFrontierInformationMind(genome(.5), 17)
        self.assertIsInstance(m, GenomicOmegaCandidateFMind)
        self.assertIsInstance(m, ReferenceFrontierInformationMind)
        self.assertIsInstance(m, ReferenceBranchMemoryMind)
        self.assertEqual(m.simulation_mode, "candidate_f")
        self.assertEqual(
            m.projection_accounting, "event_local_quadratic4")
        self.assertEqual(m.first_contact_omega, .5)
        self.assertIs(
            GenomicOmegaFrontierInformationMind.prepare_learning,
            ReferenceBranchMemoryMind.prepare_learning)
        self.assertIs(
            GenomicOmegaFrontierInformationMind.learn_from_outcome,
            ReferenceBranchMemoryMind.learn_from_outcome)

    def test_rms_structural_quote_matches_paid_prior_for_nonzero_support(self):
        m = GenomicOmegaFrontierInformationMind(genome(.5), 19)
        prime_generic(m)
        m.map = {(0, 0): (False, ()), (1, 0): None}
        quote = rms_three_leaf_target_prior_work_ceiling(
            m.map, m.branch_memory)
        b = CognitiveBudget(BODY, BodyLaws())
        result = paid_rms_three_leaf_target_prior(
            m.map, m.branch_memory, "water", b, omega=m.first_contact_omega)
        self.assertEqual(b.work, quote)
        self.assertEqual(result["work"], {
            "cycles": quote.cycles,
            "simulated_steps": quote.simulated_steps,
            "memory_items": quote.memory_items,
            "replays": quote.replays,
        })

    def test_first_contact_structural_ceiling_covers_candidate_f_kernel(self):
        m = GenomicOmegaFrontierInformationMind(genome(.5), 23)
        prime_generic(m)
        m.map = {}
        quote = water_one_future_opportunity_work_ceiling(
            m, m.branch_memory, EXPLORE, STOP_AFTER_PREFIX, 6)
        b = CognitiveBudget(BODY, BodyLaws())
        result = paid_water_one_future_opportunity_value(
            m, m.branch_memory, EXPLORE, STOP_AFTER_PREFIX, 6, b,
            forecast_work=quote, omega=m.first_contact_omega)
        self.assertEqual(
            result["forecast_work_ceiling"],
            {"cycles": quote.cycles,
             "simulated_steps": quote.simulated_steps,
             "memory_items": quote.memory_items,
             "replays": quote.replays})
        for key in ("cycles", "simulated_steps", "memory_items", "replays"):
            self.assertLessEqual(result["work"][key], getattr(quote, key))

    def test_omega_changes_only_first_contact_frontier_scores(self):
        minds = []
        infos = []
        for omega in (-1., 1.):
            m = GenomicOmegaFrontierInformationMind(
                genome(omega), 29, observer_decision_diagnostics=True)
            prime_generic(m)
            b = CognitiveBudget(BODY, BodyLaws())
            _action, _param, work, info = m.decide(cap(), b)
            self.assertEqual(work, b.work)
            self.assertEqual(info["frontier_phase"], "FIRST_CONTACT_GENOMIC_OMEGA")
            self.assertEqual(m.first_contact_queries, 1)
            self.assertEqual(m.post_contact_queries, 0)
            minds.append(m)
            infos.append(info)

        by_option = []
        for info in infos:
            by_option.append({
                row["option"]: row
                for row in info["observer"]["score_witness"]})
        common = set(by_option[0]) & set(by_option[1])
        ordinary = [
            oid for oid in common if not oid.startswith("explorer:")]
        frontier = [
            oid for oid in common if oid.startswith("explorer:")]
        self.assertTrue(ordinary)
        self.assertTrue(frontier)
        for oid in ordinary:
            self.assertEqual(
                by_option[0][oid]["total_score"],
                by_option[1][oid]["total_score"])
            self.assertNotIn("first_contact_omega", by_option[0][oid])
        self.assertTrue(any(
            by_option[0][oid]["total_score"]
            != by_option[1][oid]["total_score"]
            for oid in frontier))
        for omega, rows in zip((-1., 1.), by_option):
            for oid in frontier:
                self.assertEqual(rows[oid]["first_contact_omega"], omega)
                self.assertFalse(rows[oid]["personal_drink_support"])

        ceilings = [{
            tuple(sorted(row["common_forecast_work_ceiling"].items()))
            for row in rows.values()}
            for rows in by_option]
        self.assertEqual(len(ceilings[0]), 1)
        self.assertEqual(ceilings[0], ceilings[1])

    def test_personal_drink_history_makes_post_contact_path_omega_invariant(self):
        outputs = []
        for omega in (-1., 1.):
            m = GenomicOmegaFrontierInformationMind(
                genome(omega), 31, observer_decision_diagnostics=True)
            prime_generic(m)
            prime_personal_drink(m)
            before = deepcopy(m.effects.stats)
            result = m.decide(
                cap(), CognitiveBudget(BODY, BodyLaws()))
            self.assertEqual(result[3]["frontier_phase"], "POST_CONTACT_PERSONAL")
            self.assertEqual(m.first_contact_queries, 0)
            self.assertEqual(m.post_contact_queries, 1)
            self.assertEqual(m.effects.stats, before)
            frontier = [
                row for row in result[3]["observer"]["score_witness"]
                if row["option"].startswith("explorer:")]
            self.assertTrue(frontier)
            self.assertTrue(all(row["personal_drink_support"] for row in frontier))
            self.assertTrue(all("first_contact_omega" not in row
                                for row in frontier))
            outputs.append(result)
        self.assertEqual(outputs[0], outputs[1])

    def test_harmful_personal_drink_also_disables_innate_omega(self):
        outputs = []
        for omega in (-1., 1.):
            m = GenomicOmegaFrontierInformationMind(
                genome(omega), 37, observer_decision_diagnostics=True)
            prime_generic(m)
            prime_personal_drink(m, (-.5, -.2, -20., -2., 0.))
            outputs.append(m.decide(
                cap(), CognitiveBudget(BODY, BodyLaws())))
            self.assertEqual(m.first_contact_queries, 0)
            self.assertEqual(m.post_contact_queries, 1)
        self.assertEqual(outputs[0], outputs[1])

    def test_first_contact_competition_witness_authenticates_existing_score_schema(self):
        m = GenomicOmegaFrontierInformationMind(
            genome(1.), 41,
            observer_full_competition=True)
        prime_generic(m)
        b = CognitiveBudget(BODY, BodyLaws())
        action, param, work, info = m.decide(cap(), b)
        receipt = capture_competition(
            info=info, action=action, param=param, work=work,
            allowed=b, capture=cap())
        frontier = [
            row for row in receipt["paid_option_scores"]
            if row["option"].startswith("explorer:")]
        self.assertTrue(frontier)
        self.assertTrue(all(
            row["score_kind"] == "frontier_water_expected_distress"
            for row in frontier))
        for row in frontier:
            self.assertAlmostEqual(
                row["total_score"],
                row["base_return"] + row["information_value"])

    def test_runtime_policy_manifest_and_receipts_are_explicit(self):
        life = run_life(
            genome(.5), fixture((100., 80., 70., 80., 100.)),
            43, 3, keep_trace=True,
            observer_mind_digest=True,
            observer_decision_diagnostics=True,
            decision_policy=POLICY,
            protocol="GENOMIC_OMEGA_FRONTIER_SOFTWARE_ONLY")
        policy = life["experimental_policy"]
        self.assertEqual(policy["name"], POLICY)
        self.assertEqual(policy["simulation_mode"], "candidate_f")
        self.assertEqual(
            policy["projection_accounting"], "event_local_quadratic4")
        self.assertEqual(
            policy["post_contact"],
            "personal_frontier_information_omega_free_v1")
        frontier = life["frontier_information"]
        self.assertEqual(frontier["first_contact_omega"], .5)
        self.assertEqual(
            frontier["omega_use"], "FIRST_CONTACT_ONLY_UNSUPPORTED_DRINK")
        self.assertIn("branch_effect_memory", life)
        self.assertIn("branch_outcomes_sha256", life)
        self.assertEqual(
            life["cognitive_accounting"]["status"],
            "SETTLED_FOR_DECLARED_WORK")

    def test_reference_and_storage_only_never_construct_live_omega_candidate(self):
        with patch(
            "i3.archive.stage1.modules.genomic_omega_frontier_information_mind."
            "GenomicOmegaFrontierInformationMind.__init__",
            side_effect=AssertionError("implicit genomic omega policy")):
            for policy in ("reference", "reference_branch_memory_v1"):
                with self.subTest(policy=policy):
                    life = run_life(
                        genome(1.), fixture((100., 80., 70., 80., 100.)),
                        47, 2, decision_policy=policy)
                    self.assertNotEqual(
                        life.get("experimental_policy", {}).get("name"),
                        POLICY)

    def test_historical_ablations_fail_before_birth(self):
        with patch(
            "i3.runtime.life.World",
            side_effect=AssertionError("born too soon")):
            for kwargs in (
                {"learning_mode": "discard_values"},
                {"effect_readout": "blind_all"},
                {"score_addend_mode": "discard_curiosity_bonus"},
            ):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    run_life(
                        genome(.5), fixture(), 53, 2,
                        decision_policy=POLICY, **kwargs)


if __name__ == "__main__":
    unittest.main()
