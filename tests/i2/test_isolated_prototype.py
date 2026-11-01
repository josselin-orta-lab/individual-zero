"""Internal I2 causal prototype: engineering controls, not living/M11 science."""
from __future__ import annotations
import sqlite3
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.runtime.isolated_prototype import (
    IsolatedI2, PrototypeRefusal, COLLECT, EAT, SCENARIOS, demo,
    paired_decision_contrast, world_demo, world_endpoint,
    paired_world_endpoints, DRINK, WORLD_TICK_LIMIT,
)
from i2.modules.cognitive_cycle_fixture import (
    FaultInjected, CommitAcknowledgmentLost,
)


class IsolatedPrototypeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "prototype.sqlite"

    def create(self, **kwargs):
        return IsolatedI2.create(
            self.path, learning=kwargs.pop("learning", True),
            impulses=kwargs.pop("impulses", SCENARIOS["stable"]), **kwargs)

    def test_one_owner_paid_admitted_and_delayed_experience(self):
        i2 = self.create()
        a = i2.step()
        b = i2.step()
        self.assertEqual((a.chosen, b.chosen), (COLLECT, EAT))
        self.assertIsNotNone(a.admission_ref)
        self.assertNotEqual(a.admission_ref, b.admission_ref)
        self.assertEqual((a.actual_uc_spent, b.actual_uc_spent), (4, 5))
        self.assertEqual(b.energy, 42)
        self.assertEqual(i2.audit()["revision"], 2)
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM events").fetchone()[0], 2)
            self.assertEqual(db.execute("SELECT count(*) FROM proto_steps").fetchone()[0], 2)
            first, second = [r[0] for r in db.execute(
                "SELECT event_json FROM events ORDER BY seq")]
        self.assertNotIn("evidence:i2:outcome:2", second)
        self.assertNotIn("evidence:i2:outcome:1", first)
        self.assertIn("evidence:i2:outcome:1", second)
        self.assertFalse(i2.audit()["m11_authenticated"])

    def test_veto_prevents_internal_admission_but_costs_uc(self):
        i2 = self.create()
        veto = i2.step(veto=True)
        self.assertIsNone(veto.chosen)
        self.assertIsNone(veto.admission_ref)
        self.assertEqual(veto.control_status, "VETOED")
        self.assertEqual(veto.resources, 8)
        self.assertEqual(veto.energy, 39)
        self.assertEqual(veto.actual_uc_spent, 4)

    def test_before_commit_rolls_back_world_and_uc(self):
        i2 = self.create()
        before = i2.audit()
        with self.assertRaises(FaultInjected):
            i2.step(fault="before_commit")
        self.assertEqual(i2.audit(), before)
        self.assertEqual(i2.step().chosen, COLLECT)

    def test_after_commit_halts_no_retry_or_cold_reentry(self):
        i2 = self.create()
        with self.assertRaises(CommitAcknowledgmentLost):
            i2.step(fault="after_commit")
        self.assertEqual(i2.audit()["revision"], 1)
        with self.assertRaises(PrototypeRefusal):
            i2.step()
        cold = IsolatedI2.inspect(self.path)
        self.assertEqual(cold.audit()["revision"], 1)
        with self.assertRaises(PrototypeRefusal):
            cold.step()

    def test_terminal_absorbs_and_ancient_identity_rejected(self):
        i2 = self.create(initial_energy=2)
        self.assertTrue(i2.step().terminal)
        with self.assertRaises(PrototypeRefusal):
            i2.step()
        self.assertTrue(IsolatedI2.inspect(self.path).audit()["terminal"])
        with self.assertRaises(PrototypeRefusal):
            IsolatedI2.create(self.path, learning=False, impulses=(6,))
        other = IsolatedI2(self.path, "i2:prototype:life:foreign",
                           i2.genesis_ref, inspection_only=True)
        with self.assertRaises(PrototypeRefusal):
            other.audit()

    def test_history_tamper_rejected(self):
        i2 = self.create()
        i2.step()
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE proto_steps SET energy=99 WHERE seq=1")
        with self.assertRaises(PrototypeRefusal):
            i2.audit()
        with self.assertRaises(PrototypeRefusal):
            i2.step()

    def test_no_hidden_first_capture_or_learning_overclaim(self):
        result = demo("adverse", steps=5)
        self.assertEqual(result["scientific_verdict"], "NOT_ESTABLISHED")
        self.assertEqual(set(result["arms"]), {"observed_chosen", "fixed"})
        first = [arm["trace"][0]["chosen"] for arm in result["arms"].values()]
        self.assertEqual(first, [COLLECT, COLLECT])
        self.assertTrue(all(not arm["audit"]["engine_registered"]
                            for arm in result["arms"].values()))

    def test_adverse_first_divergence_is_a_matched_engineered_score_contrast(self):
        report = demo("adverse", steps=6)
        difference = report["behavioral_contrast"]
        self.assertEqual(
            difference["classification"],
            "MATCHED_PRECHOICE_PROGRAMMED_VALUATION_CONTRAST",
        )
        self.assertEqual(difference["first_divergence_seq"], 4)
        self.assertTrue(difference["matched_prechoice"])
        self.assertEqual(difference["observational_action"], COLLECT)
        self.assertEqual(difference["fixed_action"], EAT)
        self.assertEqual(difference["candidate_score_differences"][EAT],
                         {"observational": -5, "fixed": 4})
        left = report["arms"]["observed_chosen"]["decisions"]
        right = report["arms"]["fixed"]["decisions"]
        for idx in range(3):
            self.assertEqual(left[idx]["chosen"], right[idx]["chosen"])
            self.assertEqual(left[idx]["energy_after"], right[idx]["energy_after"])
            self.assertEqual(left[idx]["uc_spent"], right[idx]["uc_spent"])
        self.assertEqual(left[3]["uc_before"], right[3]["uc_before"])
        self.assertEqual(left[3]["subjective_outcomes_available"],
                         right[3]["subjective_outcomes_available"])
        self.assertEqual(left[3]["outcomes_used_by_valuation"],
                         left[3]["subjective_outcomes_available"])
        self.assertEqual(right[3]["outcomes_used_by_valuation"], ())
        self.assertTrue(difference["not_a_natural_learning_or_survival_verdict"])

    def test_stable_null_and_neutral_tie_are_preserved_not_tuned(self):
        stable = demo("stable", steps=6)
        self.assertEqual(
            stable["behavioral_contrast"]["classification"],
            "NO_ACTION_DIVERGENCE_IN_OBSERVED_HORIZON",
        )
        self.assertIsNone(stable["behavioral_contrast"]["first_divergence_seq"])
        neutral = demo("neutral", steps=6)
        contrast = neutral["behavioral_contrast"]
        self.assertEqual(contrast["first_divergence_seq"], 4)
        self.assertTrue(contrast["matched_prechoice"])
        self.assertIsNone(contrast["observational_action"])
        self.assertEqual(contrast["fixed_action"], EAT)

    def test_decision_inspection_cannot_feed_subject_or_fabricate_match(self):
        subject = self.create()
        self.assertEqual(subject.decision_evidence(), ())
        subject.step()
        self.assertEqual(subject.decision_evidence()[0]["subjective_outcomes_available"], ())
        subject.step()
        readings = subject.decision_evidence()
        self.assertEqual(len(readings), 2)
        self.assertEqual(readings[1]["subjective_outcomes_available"][0]["seq"], 1)
        self.assertNotIn("impulses", readings[1])
        forged = [dict(v) for v in readings]
        forged[0]["energy_after"] += 1
        # Context that only diverges AFTER a selected action cannot be
        # treated as the same prehistory for a later divergence.
        forged[1]["chosen"] = None
        compared = paired_decision_contrast(tuple(forged), readings)
        self.assertEqual(compared["classification"],
                         "UNMATCHED_PRECHOICE_NO_CAUSAL_ATTRIBUTION")

    def test_physics_continues_at_zero_uc_and_terminal_absorbs(self):
        subject = self.create(initial_uc=0, initial_energy=3, impulses=(6,))
        self.assertEqual(subject.audit()["remaining_uc"], 0)
        for n in (1, 2, 3):
            result = subject.advance_physics()
            self.assertEqual(result["energy"], 3 - n)
            self.assertFalse(result["cognition_committed"])
            self.assertEqual(subject.audit()["revision"], 0)
            self.assertEqual(subject.audit()["actual_uc_spent"], 0)
            self.assertEqual(subject.audit()["physical_ticks"], n)
        self.assertTrue(subject.audit()["terminal"])
        with self.assertRaises(PrototypeRefusal):
            subject.advance_physics()
        with self.assertRaises(PrototypeRefusal):
            subject.step()
        self.assertTrue(IsolatedI2.inspect(self.path).audit()["terminal"])

    def test_cognition_sees_new_energy_only_after_committed_ticks(self):
        subject = self.create(initial_energy=20)
        subject.advance_physics()
        subject.advance_physics()
        decision = subject.step()
        self.assertEqual(decision.before_energy, 18)
        self.assertEqual(subject.decision_evidence()[0]["physical_ticks_before"], 2)
        subject.advance_physics()
        next_decision = subject.step()
        self.assertEqual(next_decision.before_energy, decision.energy - 1)
        self.assertEqual(subject.decision_evidence()[1]["physical_ticks_before"], 3)
        self.assertEqual(subject.audit()["revision"], 2)
        self.assertEqual(subject.audit()["physical_ticks"], 3)

    def test_tick_before_commit_rolls_back_and_after_commit_halts(self):
        subject = self.create(initial_uc=0, initial_energy=4)
        before = subject.audit()
        with self.assertRaises(FaultInjected):
            subject.advance_physics(fault="before_commit")
        self.assertEqual(subject.audit(), before)
        with self.assertRaises(CommitAcknowledgmentLost):
            subject.advance_physics(fault="after_commit")
        self.assertEqual(subject.audit()["physical_ticks"], 1)
        with self.assertRaises(PrototypeRefusal):
            subject.advance_physics()
        cold = IsolatedI2.inspect(self.path)
        self.assertEqual(cold.audit()["energy"], 3)
        with self.assertRaises(PrototypeRefusal):
            cold.advance_physics()

    def test_physical_tick_tamper_rejected_before_any_action(self):
        subject = self.create()
        subject.advance_physics()
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE proto_ticks SET energy=99 WHERE seq=1")
        with self.assertRaises(PrototypeRefusal):
            subject.audit()
        with self.assertRaises(PrototypeRefusal):
            subject.step()

    def test_scheduled_world_owns_metabolism_and_paid_action_windows(self):
        subject = self.create(initial_energy=20)
        execution = subject.run_world(ticks=4)
        trace = execution["trace"]
        self.assertEqual(len(trace), 4)
        self.assertEqual([row["physical_tick"] for row in trace], [1, 2, 3, 4])
        self.assertEqual([row["cognitive_committed"] for row in trace],
                         [False, True, False, True])
        self.assertEqual(trace[0]["reason"], "NO_COGNITIVE_WINDOW")
        self.assertEqual(trace[1]["selected_action"], COLLECT)
        self.assertEqual(trace[3]["selected_action"], EAT)
        self.assertTrue(all(
            row["internal_admission"] is None
            for row in (trace[0], trace[2])
        ))
        self.assertEqual(subject.audit()["physical_ticks"], 4)
        self.assertEqual(subject.audit()["revision"], 2)
        self.assertEqual(subject.audit()["actual_uc_spent"], 9)
        self.assertEqual(subject.decision_evidence()[0]["physical_ticks_before"], 2)
        self.assertEqual(subject.decision_evidence()[1]["physical_ticks_before"], 4)
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM proto_ticks").fetchone()[0], 4)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM events").fetchone()[0], 2)
        self.assertEqual(execution["status"], "BOUNDED_OBSERVATION_END_NONTERMINAL")
        self.assertFalse(execution["m11_authenticated"])

    def test_scheduled_world_ages_to_terminal_with_no_uc_or_cognition(self):
        subject = self.create(initial_uc=0, initial_energy=4, impulses=(6,))
        report = subject.run_world(ticks=12)
        self.assertEqual(report["status"], "MODELED_TERMINAL")
        self.assertEqual(len(report["trace"]), 4)
        self.assertEqual(report["audit"]["energy"], 0)
        self.assertEqual(report["audit"]["physical_ticks"], 4)
        self.assertEqual(report["audit"]["revision"], 0)
        self.assertEqual(report["audit"]["remaining_uc"], 0)
        self.assertEqual(report["trace"][1]["reason"], "COGNITION_UNFUNDED")
        self.assertEqual(report["trace"][-1]["reason"], "PHYSICAL_TERMINAL")
        with self.assertRaisesRegex(PrototypeRefusal, "terminal"):
            subject.run_world(ticks=1)
        self.assertTrue(IsolatedI2.inspect(self.path).audit()["terminal"])

    def test_scheduled_world_cognition_runs_out_before_physics(self):
        subject = self.create(initial_uc=4, initial_energy=8, impulses=(6,) * 8)
        result = subject.run_world(ticks=12)
        trace = result["trace"]
        self.assertEqual(trace[1]["selected_action"], COLLECT)
        self.assertEqual(trace[1]["remaining_uc"], 0)
        self.assertEqual(trace[3]["reason"], "COGNITION_UNFUNDED")
        self.assertEqual(result["status"], "MODELED_TERMINAL")
        self.assertEqual(result["audit"]["revision"], 1)
        self.assertEqual(result["audit"]["actual_uc_spent"], 4)
        self.assertGreater(result["audit"]["physical_ticks"], 2)

    def test_scheduled_world_preserves_physics_after_cognitive_horizon(self):
        subject = self.create(initial_energy=30, impulses=(6,))
        result = subject.run_world(ticks=6)
        self.assertEqual(result["audit"]["revision"], 1)
        self.assertEqual(result["audit"]["physical_ticks"], 6)
        self.assertEqual(result["trace"][3]["reason"],
                         "COGNITIVE_HORIZON_EXHAUSTED")
        self.assertEqual(result["trace"][5]["reason"],
                         "COGNITIVE_HORIZON_EXHAUSTED")
        self.assertFalse(result["audit"]["terminal"])

    def test_scheduled_world_chunked_calls_preserve_decisions_and_uc(self):
        subject = self.create(initial_energy=30)
        first = subject.run_world(ticks=3)
        second = subject.run_world(ticks=5)
        path2 = Path(self.tmp.name) / "whole.sqlite"
        whole = IsolatedI2.create(
            path2, learning=True, impulses=SCENARIOS["stable"],
            initial_energy=30)
        single = whole.run_world(ticks=8)
        combined = (*first["trace"], *second["trace"])
        for a, b in zip(combined, single["trace"]):
            self.assertEqual(
                (a["physical_tick"], a["reason"], a["selected_action"],
                 a["physical_end_energy"], a["remaining_uc"]),
                (b["physical_tick"], b["reason"], b["selected_action"],
                 b["physical_end_energy"], b["remaining_uc"]),
            )
        self.assertEqual(subject.audit()["revision"], whole.audit()["revision"])
        self.assertEqual(subject.audit()["energy"], whole.audit()["energy"])
        self.assertEqual(subject.audit()["remaining_uc"], whole.audit()["remaining_uc"])

    def test_scheduled_world_horizon_is_censored_not_claimed_survival(self):
        subject = self.create(initial_uc=0, initial_energy=40)
        report = subject.run_world(ticks=WORLD_TICK_LIMIT)
        self.assertEqual(report["status"], "RESEARCH_HORIZON_CENSORED")
        self.assertFalse(report["audit"]["terminal"])
        self.assertEqual(report["audit"]["energy"], 40 - WORLD_TICK_LIMIT)
        self.assertEqual(report["audit"]["revision"], 0)
        self.assertEqual(subject.run_world(ticks=1)["trace"], ())
        with self.assertRaisesRegex(PrototypeRefusal, "horizon"):
            subject.advance_physics()

    def test_scheduled_world_paired_behavioral_contrast_not_overclaimed(self):
        report = world_demo("adverse", ticks=8)
        self.assertEqual(report["scientific_verdict"], "NOT_ESTABLISHED")
        self.assertEqual(report["first_choice_contrast"]["first_divergence_seq"], 4)
        self.assertEqual(
            report["first_choice_contrast"]["classification"],
            "MATCHED_PRECHOICE_PROGRAMMED_VALUATION_CONTRAST",
        )
        for arm in report["arms"].values():
            self.assertEqual(arm["audit"]["physical_ticks"], 8)
            self.assertEqual(arm["audit"]["revision"], 4)
            self.assertFalse(arm["audit"]["m11_authenticated"])


    def test_no_resources_genesis_uses_only_observed_affordance(self):
        subject = self.create(resources=0, initial_energy=12)
        first = subject.step()
        self.assertEqual(first.visible, (DRINK,))
        self.assertEqual(first.chosen, DRINK)
        self.assertIsNotNone(first.admission_ref)
        self.assertEqual((first.inventory, first.resources), (0, 0))
        self.assertEqual(first.actual_uc_spent, 3)
        decisions = subject.decision_evidence()
        self.assertEqual(decisions[0]["candidate_scores"], {DRINK: 1})
        self.assertEqual(decisions[0]["subjective_outcomes_available"], ())
        self.assertEqual(subject.audit()["revision"], 1)

    def test_resource_empty_world_runs_without_forced_collect(self):
        report = world_demo("adverse", ticks=4, resources=0,
                            initial_energy=12)
        self.assertEqual(report["scientific_verdict"], "NOT_ESTABLISHED")
        for arm in report["arms"].values():
            self.assertEqual([d["chosen"] for d in arm["decisions"]],
                             [DRINK, DRINK])
            self.assertEqual(arm["audit"]["resources"], 0)
            self.assertEqual(arm["audit"]["inventory"], 0)
            self.assertEqual(arm["audit"]["actual_uc_spent"], 6)
            self.assertTrue(all(d["visible"] == (DRINK,)
                                for d in arm["decisions"]))
        self.assertEqual(
            report["first_choice_contrast"]["classification"],
            "NO_ACTION_DIVERGENCE_IN_OBSERVED_HORIZON",
        )

    def test_endpoints_preserve_null_and_censoring_at_zero_uc(self):
        report = world_demo("adverse", ticks=8, initial_uc=0,
                            initial_energy=20)
        for arm in report["arms"].values():
            endpoint = arm["endpoint"]
            self.assertEqual(endpoint["observed_physical_ticks"], 8)
            self.assertEqual(endpoint["ending_energy"], 12)
            self.assertEqual(endpoint["actual_uc_spent"], 0)
            self.assertEqual(endpoint["paid_decisions"], 0)
            self.assertEqual(endpoint["unfunded_cognitive_windows"], 4)
            self.assertTrue(endpoint["right_censored"])
            self.assertIsNone(endpoint["modeled_death_tick"])
        self.assertEqual(
            report["world_endpoint_contrast"]["classification"],
            "NO_PAID_COGNITIVE_EXPOSURE",
        )
        self.assertIsNone(report["world_endpoint_contrast"][
            "learned_modeled_death_tick"])
        self.assertEqual(report["world_endpoint_contrast"][
            "generalized_survival_benefit"], "NOT_ESTABLISHED")

    def test_endpoint_terminal_is_not_treated_as_survival_success(self):
        report = world_demo("neutral", ticks=12, initial_uc=0,
                            initial_energy=4)
        for arm in report["arms"].values():
            endpoint = arm["endpoint"]
            self.assertTrue(endpoint["modeled_terminal_observed"])
            self.assertEqual(endpoint["modeled_death_tick"], 4)
            self.assertFalse(endpoint["right_censored"])
            self.assertEqual(endpoint["ending_energy"], 0)
            self.assertEqual(endpoint["observed_physical_ticks"], 4)
        self.assertIsNone(report["world_endpoint_contrast"][
            "ending_energy_difference"])
        self.assertTrue(report["world_endpoint_contrast"][
            "ending_energy_is_not_survival_evidence"])

    def test_world_endpoint_is_descriptive_even_when_policies_diverge(self):
        report = world_demo("adverse", ticks=8)
        self.assertEqual(
            report["first_choice_contrast"]["first_divergence_seq"], 4)
        self.assertEqual(
            report["world_endpoint_contrast"]["classification"],
            "COMMON_WINDOW_NONTERMINAL_DESCRIPTIVE_ONLY")
        self.assertIsInstance(
            report["world_endpoint_contrast"]["ending_energy_difference"],
            int)
        self.assertEqual(report["world_endpoint_contrast"][
            "natural_autonomous_learning"], "NOT_ESTABLISHED")
        self.assertEqual(report["arms"]["observed_chosen"]["endpoint"][
            "ending_physical_tick"], 8)

    def test_terminal_or_unequal_exposure_rejects_false_energy_comparison(self):
        a = {"ending_physical_tick": 4, "modeled_terminal_observed": True,
             "modeled_death_tick": 4, "ending_energy": 0,
             "paid_decisions": 1}
        b = {"ending_physical_tick": 8, "modeled_terminal_observed": False,
             "modeled_death_tick": None, "ending_energy": 5,
             "paid_decisions": 1}
        contrast = paired_world_endpoints(a, b)
        self.assertEqual(contrast["classification"],
                         "TERMINAL_OR_UNEQUAL_EXPOSURE_NO_COMMON_END_ENERGY")
        self.assertIsNone(contrast["ending_energy_difference"])
        self.assertFalse(contrast["observed_at_same_tick"])



if __name__ == "__main__":
    unittest.main()
