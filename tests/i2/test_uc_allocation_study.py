"""Synthetic, counterbalanced UC-allocation comparison; no living I2."""
from dataclasses import fields, replace
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from i2.modules.competition_preview import (  # noqa: E402
    CompetitionPreview, CompetitionReceipt, SubjectiveValuation, OPERATION,
)
from i2.modules.intention_continuity import (  # noqa: E402
    FirstPersonCapture, IntentionContinuity,
)
from i2.modules.intention_ingress import ObservationClaim  # noqa: E402
from i2.modules.option_reconstruction import reconstruct_candidates  # noqa: E402
from i2.modules.uc_allocation_study import (  # noqa: E402
    SCHEMA, POLICIES, PROFILES, AllocationPlan, DiagnosticAdvice,
    plan_without_values, advise_on_sample_only, audit_heldout_after_choice,
    synthetic_frame, synthetic_values, run_comparison,
)


def frame(n=3, step=3):
    return synthetic_frame(step, n)


def plan(n=3, budget=2, policy="rotating_quota", phase=0):
    return plan_without_values(frame(n), policy=policy,
                               uc_ceiling=budget, phase=phase)


class Source:
    def verify(self, *, life_ref, frame):
        return life_ref == frame.life_ref


class SyntheticLedger:
    def __init__(self, budget):
        self.balance = budget

    def debit_batch(self, *, life_ref, frame_ref, claim_digest,
                    candidate_refs, operation, units_each):
        if self.balance < len(candidate_refs) * units_each:
            return None
        self.balance -= len(candidate_refs) * units_each
        return tuple(CompetitionReceipt(
            f"synthetic:{i}", life_ref, frame_ref, claim_digest, ref,
            operation, units_each,
        ) for i, ref in enumerate(candidate_refs))


class SyntheticEvaluator:
    def evaluate_batch(self, *, frame, receipts):
        return tuple(SubjectiveValuation(
            r.candidate_ref, r.ref, "test:evidence", i + 1,
        ) for i, r in enumerate(receipts))


class TestUCAllocationStudy(unittest.TestCase):
    def test_default_study_is_not_a_motored_engine(self):
        forbidden = {"command", "option_ref", "motor", "winner", "admission", "approved", "action"}
        for obj in (AllocationPlan, DiagnosticAdvice):
            self.assertFalse(forbidden & {f.name for f in fields(obj)})
        for p in POLICIES:
            self.assertEqual(plan(policy=p).motor_authority, "NONE")

    def test_all_or_none_short_budget_abstains_and_spends_zero(self):
        p = plan(budget=2, policy="full_frame")
        self.assertEqual(p.status, "UNFUNDED")
        self.assertEqual(p.uc_scheduled, 0)
        self.assertEqual(p.selected_candidate_refs, ())
        advice = advise_on_sample_only(p, {})
        self.assertIsNone(advice.suggested_candidate_ref)
        self.assertEqual(advice.status, "UNFUNDED")

    def test_full_frame_at_exact_budget_matches_legacy_behavior(self):
        f = frame(3)
        p = plan_without_values(f, policy="full_frame", uc_ceiling=3, phase=0)
        self.assertEqual(p.status, "COMPLETE_DIAGNOSTIC")
        self.assertEqual(p.uc_scheduled, 3)
        for budget, expected in ((2, "UNFUNDED"), (3, "ADVISORY_ONLY")):
            with self.subTest(budget=budget):
                gate = CompetitionPreview(life_ref=f.life_ref,
                    frame_authority=Source(), ledger=SyntheticLedger(budget),
                    evidence=SyntheticEvaluator())
                self.assertEqual(gate.review(f).status, expected)

    def test_equal_per_capture_ceiling_not_equal_actual_spend(self):
        p = [plan(budget=2, policy=policy) for policy in POLICIES]
        self.assertTrue(all(x.uc_ceiling == 2 for x in p))
        self.assertEqual([x.uc_scheduled for x in p], [0, 2, 2])

    def test_prefix_is_explicitly_an_order_biased_negative_control(self):
        seq = [plan(budget=2, policy="fixed_prefix_control", phase=t) for t in range(3)]
        self.assertTrue(all(p.selected_candidate_refs == seq[0].selected_candidate_refs for p in seq))
        self.assertEqual(len(seq[0].selected_candidate_refs), 2)

    def test_rotating_quota_balances_three_candidates_at_budget_two(self):
        seq = [plan(budget=2, phase=t) for t in range(3)]
        names = seq[0].all_candidate_refs
        self.assertEqual([sum(ref in p.selected_candidate_refs for p in seq)
                          for ref in names], [2, 2, 2])
        self.assertTrue(all(p.uc_scheduled == 2 for p in seq))

    def test_rotating_quota_balances_five_candidates_at_budget_two(self):
        seq = [plan(n=5, budget=2, phase=t) for t in range(5)]
        names = seq[0].all_candidate_refs
        self.assertEqual([sum(ref in p.selected_candidate_refs for p in seq)
                          for ref in names], [2] * 5)

    def test_budget_one_visits_every_candidate_before_repeating(self):
        seq = [plan(n=5, budget=1, phase=t) for t in range(5)]
        names = seq[0].all_candidate_refs
        self.assertEqual([sum(ref in p.selected_candidate_refs for p in seq)
                          for ref in names], [1] * 5)

    def test_rotating_uses_new_frame_without_transferring_motor_scores(self):
        first = plan_without_values(frame(3, 3), policy="rotating_quota",
                                    uc_ceiling=2, phase=0)
        second = plan_without_values(frame(3, 4), policy="rotating_quota",
                                     uc_ceiling=2, phase=1)
        self.assertNotEqual(first.frame_ref, second.frame_ref)
        self.assertTrue(set(first.all_candidate_refs).isdisjoint(second.all_candidate_refs))
        self.assertEqual(first.motor_authority, second.motor_authority)

    def test_study_candidates_ignore_intention_metadata(self):
        f = frame(3)
        # Intention annotations cannot influence which candidate is sampled.
        from dataclasses import replace
        tagged = replace(f, candidates=tuple(replace(c, intention_ref="intent:i2:tag")
                                             for c in f.candidates))
        for policy in POLICIES:
            first = plan_without_values(f, policy=policy, uc_ceiling=2, phase=1)
            second = plan_without_values(tagged, policy=policy, uc_ceiling=2, phase=1)
            self.assertEqual(first.selected_candidate_refs, second.selected_candidate_refs)

    def test_permutation_cannot_create_extra_uc_budget(self):
        for policy in POLICIES:
            for n in (3, 5):
                for budget in (0, 1, 2, 3, 5):
                    p = plan(n=n, budget=budget, policy=policy)
                    self.assertLessEqual(p.uc_scheduled, budget)
                    self.assertEqual(p.uc_scheduled, len(p.selected_candidate_refs))
                    self.assertEqual(len(p.selected_candidate_refs),
                                     len(set(p.selected_candidate_refs)))

    def test_no_hidden_values_are_available_to_allocating_policy(self):
        f = frame()
        p = plan_without_values(f, policy="rotating_quota", uc_ceiling=2, phase=1)
        rising = synthetic_values(f, "ascending")
        falling = synthetic_values(f, "descending")
        self.assertNotEqual(rising, falling)
        # The allocation never accepts any values argument, hence unchanged.
        self.assertEqual(p.selected_candidate_refs,
                         plan_without_values(f, policy="rotating_quota", uc_ceiling=2,
                                             phase=1).selected_candidate_refs)
        self.assertFalse(hasattr(p, "value"))

    def test_extra_hidden_value_is_rejected_by_advisory(self):
        p = plan()
        hidden = next(x for x in p.all_candidate_refs if x not in p.selected_candidate_refs)
        with self.assertRaises(ValueError):
            advise_on_sample_only(p, {p.selected_candidate_refs[0]: 1,
                                      p.selected_candidate_refs[1]: 2, hidden: 10})

    def test_missing_evaluation_rejected(self):
        p = plan()
        with self.assertRaises(ValueError):
            advise_on_sample_only(p, {p.selected_candidate_refs[0]: 1})

    def test_invalid_non_numeric_or_unbounded_values_rejected(self):
        p = plan()
        for value in (True, 1.5, 1025, -1025, None, "1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                advise_on_sample_only(p, dict.fromkeys(p.selected_candidate_refs, value))

    def test_partial_positive_is_diagnostic_never_motor(self):
        p = plan()
        vals = {p.selected_candidate_refs[0]: 1, p.selected_candidate_refs[1]: 2}
        advice = advise_on_sample_only(p, vals)
        self.assertEqual(advice.status, "PARTIAL_UNVERIFIED")
        self.assertEqual(advice.suggested_candidate_ref, p.selected_candidate_refs[1])
        self.assertEqual(advice.motor_authority, "NONE")

    def test_tied_partial_values_abstain(self):
        p = plan()
        advice = advise_on_sample_only(p, dict.fromkeys(p.selected_candidate_refs, 2))
        self.assertEqual(advice.status, "AMBIGUOUS")
        self.assertIsNone(advice.suggested_candidate_ref)

    def test_no_positive_values_abstain(self):
        p = plan()
        advice = advise_on_sample_only(p, dict.fromkeys(p.selected_candidate_refs, -1))
        self.assertEqual(advice.status, "NO_POSITIVE_EVIDENCE")
        self.assertIsNone(advice.suggested_candidate_ref)

    def test_heldout_audit_is_separate_from_advice(self):
        p = plan()
        full = {ref: i + 1 for i, ref in enumerate(p.all_candidate_refs)}
        observed = {ref: full[ref] for ref in p.selected_candidate_refs}
        advice = advise_on_sample_only(p, observed)
        audit = audit_heldout_after_choice(p, advice, full)
        self.assertTrue(audit.withheld_oracle)
        self.assertFalse(audit.matched_unique_oracle)
        self.assertEqual(audit.motor_authority, "NONE")

    def test_oracle_can_be_present_in_rotation_without_full_knowledge(self):
        p = plan(budget=2, phase=1)
        full = {ref: 1 for ref in p.all_candidate_refs}
        best = p.selected_candidate_refs[0]
        full[best] = 7
        advice = advise_on_sample_only(p, {ref: full[ref] for ref in p.selected_candidate_refs})
        audit = audit_heldout_after_choice(p, advice, full)
        self.assertTrue(audit.matched_unique_oracle)
        self.assertFalse(audit.withheld_oracle)
        self.assertEqual(advice.status, "PARTIAL_UNVERIFIED")

    def test_tied_global_oracle_is_not_a_false_success(self):
        p = plan()
        full = dict.fromkeys(p.all_candidate_refs, 4)
        a = advise_on_sample_only(p, dict.fromkeys(p.selected_candidate_refs, 4))
        scored = audit_heldout_after_choice(p, a, full)
        self.assertIsNone(scored.unique_positive_oracle_ref)
        self.assertIsNone(scored.matched_unique_oracle)
        self.assertIsNone(scored.withheld_oracle)

    def test_an_advice_cannot_be_audit_for_another_frame(self):
        p = plan()
        a = advise_on_sample_only(p, dict.fromkeys(p.selected_candidate_refs, 1))
        with self.assertRaises(ValueError):
            audit_heldout_after_choice(p, replace(a, frame_ref="frame:alien"),
                                       dict.fromkeys(p.all_candidate_refs, 1))

    def test_bad_plan_value_and_forged_refs_rejected(self):
        p = plan()
        bad = (
            replace(p, motor_authority="ADMIT"),
            replace(p, uc_scheduled=99),
            replace(p, selected_candidate_refs=("forged:candidate",)),
            replace(p, uc_ceiling=-1),
            replace(p, all_candidate_refs=list(p.all_candidate_refs)),
            replace(p, status="COMPLETE_DIAGNOSTIC"),
            replace(p, policy="oracle_lookahead"),
            replace(p, selected_candidate_refs=p.selected_candidate_refs[::-1]),
            replace(p, uc_scheduled=True),
        )
        for variant in bad:
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                advise_on_sample_only(variant, {})

    def test_reject_unbounded_budgets_and_non_integer_phases(self):
        f = frame()
        for budget in (-1, 65, True, 2.0):
            with self.subTest(budget=budget), self.assertRaises(ValueError):
                plan_without_values(f, policy="full_frame", uc_ceiling=budget, phase=0)
        for phase in (-1, True, 1.5):
            with self.subTest(phase=phase), self.assertRaises(ValueError):
                plan_without_values(f, policy="rotating_quota", uc_ceiling=2, phase=phase)
        with self.assertRaises(ValueError):
            plan_without_values(f, policy="oracle_lookahead", uc_ceiling=2, phase=0)

    def test_frame_forgery_is_rejected_by_shape_before_allocation(self):
        f = frame()
        with self.assertRaises(ValueError):
            plan_without_values(replace(f, candidates=f.candidates[::-1]),
                                policy="rotating_quota", uc_ceiling=1, phase=0)

    def test_zero_candidates_is_funding_neutral(self):
        c = FirstPersonCapture(3, "capture:empty", "goal:neutral", ())
        claim = ObservationClaim("life:empty", c, "src:empty", ("ev:empty",))
        owner = IntentionContinuity()
        tr = owner.observe(capture=c, work_ref="work:empty")
        f = reconstruct_candidates(claim=claim, transition=tr, current=None)
        for policy in POLICIES:
            p = plan_without_values(f, policy=policy, uc_ceiling=2, phase=0)
            self.assertEqual(p.status, "NO_CANDIDATES")
            self.assertEqual(p.uc_scheduled, 0)
            self.assertEqual(advise_on_sample_only(p, {}).status, "NO_CANDIDATES")

    def test_predeclared_grid_is_deterministic_and_paired(self):
        a = run_comparison()
        self.assertEqual(a, run_comparison())
        self.assertEqual(a["schema"], SCHEMA)
        self.assertEqual(len(a["records"]), 2 * 5 * len(PROFILES) * len(POLICIES))
        counts = {}
        for row in a["records"]:
            key = (row["candidate_count"], row["uc_ceiling_each_step"], row["profile"])
            counts[key] = counts.get(key, 0) + 1
            self.assertLessEqual(row["uc_scheduled"], row["uc_ceiling_total"])
        self.assertEqual(set(counts.values()), {len(POLICIES)})

    def test_rotation_exposure_fairness_where_prefix_is_not(self):
        rows = run_comparison()["records"]
        for n in (3, 5):
            for budget in (1, 2):
                rotate = next(x for x in rows if x["candidate_count"] == n and
                              x["uc_ceiling_each_step"] == budget and
                              x["profile"] == "ascending" and x["policy"] == "rotating_quota")
                prefix = next(x for x in rows if x["candidate_count"] == n and
                              x["uc_ceiling_each_step"] == budget and
                              x["profile"] == "ascending" and x["policy"] == "fixed_prefix_control")
                self.assertEqual(rotate["exposure_gap"], 0)
                self.assertGreater(prefix["exposure_gap"], 0)
                self.assertEqual(rotate["uc_scheduled"], prefix["uc_scheduled"])

    def test_no_food_specific_preferences_or_individual_birth(self):
        text = Path(ROOT / "src/i2/modules/uc_allocation_study.py").read_text()
        for marker in ("berry_a", "nutrient_oracle", "admit_motor", "WorldBody", "death_resurrection"):
            self.assertNotIn(marker, text)
        study = run_comparison()
        self.assertEqual(study["status"], "SYNTHETIC_ONLY_NOT_SCIENTIFIC_GO")


if __name__ == "__main__":
    unittest.main()
