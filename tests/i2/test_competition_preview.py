"""Independent-source-only competition tests. No true Scheduler, birth or motor."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import fields, replace
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.modules.intention_continuity import (  # noqa: E402
    FirstPersonCapture, IntentionContinuity,
)
from i2.modules.intention_ingress import ObservationClaim  # noqa: E402
from i2.modules.option_reconstruction import (  # noqa: E402
    CandidateFrame, SemanticCandidate, reconstruct_candidates, _bound_id,
)
from i2.modules.competition_preview import (  # noqa: E402
    OPERATION, UC_PER_CANDIDATE, MAX_CANDIDATES, CompetitionPreview,
    CompetitionReceipt, SubjectiveValuation, CompetitionAdvice, VetoPreview,
    veto_preview,
)

COLLECT = "affordance:collect:berry_a"
EAT = "affordance:eat:berry_a"
DRINK = "affordance:drink:water"
LIFE = "life:competition-fixture"


def make_frame(step=3, visible=(COLLECT, DRINK, EAT), *, life=LIFE,
               tagged=None, capture_ref=None):
    capture = FirstPersonCapture(step, capture_ref or f"capture:{step}",
                                 "goal:food", tuple(sorted(visible)))
    claim = ObservationClaim(life, capture, f"source:synthetic:{step}",
                             (f"evidence:{step}",))
    owner = IntentionContinuity()
    if tagged is None:
        transition = owner.observe(capture=capture, work_ref=f"work:{step}")
    else:
        transition = owner.open(capture=capture, semantic_ref=tagged,
                                evidence_ref=f"evidence:{step}",
                                ttl_steps=10, work_ref=f"work:{step}")
    return reconstruct_candidates(claim=claim, transition=transition,
                                  current=owner.current)


class SyntheticFrameSource:
    """Permissive dummy port, NOT an authenticated M11/owner frame source."""

    def __init__(self):
        self.calls = []
        self.result = True

    def verify(self, *, life_ref, frame):
        self.calls.append((life_ref, frame.frame_ref))
        return self.result


class SyntheticBatchLedger:
    """Synthetic full-frame budget; NOT a real UC debit or a durable ledger."""

    def __init__(self, balance=100):
        self.balance = balance
        self.calls = []
        self.serial = 0
        self.tamper = None
        self.raise_after_charge = False

    def debit_batch(self, *, life_ref, frame_ref, claim_digest,
                    candidate_refs, operation, units_each):
        self.calls.append((life_ref, frame_ref, claim_digest, candidate_refs,
                           operation, units_each))
        if self.balance < len(candidate_refs) * units_each:
            return None
        self.balance -= len(candidate_refs) * units_each
        result = []
        for candidate_ref in candidate_refs:
            self.serial += 1
            result.append(CompetitionReceipt(
                f"synthetic:uc:{self.serial}", life_ref, frame_ref,
                claim_digest, candidate_ref, operation, units_each,
            ))
        if self.raise_after_charge:
            raise RuntimeError("lost external debit response")
        ticket_batch = tuple(result)
        return self.tamper(ticket_batch) if self.tamper else ticket_batch


class SyntheticEvidence:
    """Caller-controlled synthetic values. Never inferred from physical outcomes."""

    def __init__(self, mapping=None):
        self.mapping = dict(mapping or {})
        self.calls = []
        self.tamper = None
        self.throw = False

    def evaluate_batch(self, *, frame, receipts):
        self.calls.append((frame, receipts))
        if self.throw:
            raise ValueError("untrusted value service failed")
        semantic_by_ref = {c.candidate_ref: c.semantic_ref for c in frame.candidates}
        scores = tuple(SubjectiveValuation(
            r.candidate_ref, r.ref, "test:subjective:not-verified",
            self.mapping.get(semantic_by_ref[r.candidate_ref], 0)) for r in receipts)
        return self.tamper(scores) if self.tamper else scores


def setup(balance=100, scores=None):
    source = SyntheticFrameSource()
    ledger, evidence = SyntheticBatchLedger(balance), SyntheticEvidence(scores)
    return (CompetitionPreview(life_ref=LIFE, frame_authority=source,
                               ledger=ledger, evidence=evidence), ledger, evidence)


class TestCompetitionPreview(unittest.TestCase):
    def test_upstream_source_must_attest_frame_before_any_charge(self):
        source = SyntheticFrameSource()
        source.result = False
        ledger, ev = SyntheticBatchLedger(), SyntheticEvidence()
        gate = CompetitionPreview(life_ref=LIFE, frame_authority=source,
                                  ledger=ledger, evidence=ev)
        with self.assertRaises(ValueError):
            gate.review(make_frame())
        self.assertEqual(ledger.calls, [])
        self.assertEqual(ev.calls, [])
        self.assertEqual(len(source.calls), 1)

    def test_truthy_nonboolean_frame_provenance_is_rejected(self):
        source = SyntheticFrameSource()
        source.result = 1
        ledger, ev = SyntheticBatchLedger(), SyntheticEvidence()
        gate = CompetitionPreview(life_ref=LIFE, frame_authority=source,
                                  ledger=ledger, evidence=ev)
        with self.assertRaises(ValueError):
            gate.review(make_frame())
        self.assertEqual(ledger.calls, [])

    def test_foreign_life_refuses_before_source_and_uc(self):
        source = SyntheticFrameSource()
        ledger, ev = SyntheticBatchLedger(), SyntheticEvidence()
        gate = CompetitionPreview(life_ref=LIFE, frame_authority=source,
                                  ledger=ledger, evidence=ev)
        with self.assertRaises(ValueError):
            gate.review(make_frame(life="life:alien"))
        self.assertEqual(source.calls, [])
        self.assertEqual(ledger.calls, [])

    def test_all_candidates_get_a_paid_batch_before_any_advice(self):
        frame = make_frame()
        gate, ledger, evaluator = setup(scores={COLLECT: 3, EAT: 5, DRINK: 2})
        advice = gate.review(frame)
        self.assertEqual(advice.status, "ADVISORY_ONLY")
        self.assertEqual(advice.suggested_candidate_ref, next(
            c.candidate_ref for c in frame.candidates if c.semantic_ref == EAT))
        self.assertEqual(advice.evaluated_candidate_refs,
                         tuple(c.candidate_ref for c in frame.candidates))
        self.assertEqual(len(advice.receipt_refs), 3)
        self.assertEqual(tuple(v.value for v in advice.valuation_records),
                         tuple({COLLECT: 3, EAT: 5, DRINK: 2}[c.semantic_ref]
                               for c in frame.candidates))
        self.assertEqual(tuple(v.receipt_ref for v in advice.valuation_records),
                         advice.receipt_refs)
        self.assertEqual(ledger.balance, 97)
        self.assertEqual(len(ledger.calls), 1)
        self.assertEqual(ledger.calls[0][-2:], (OPERATION, UC_PER_CANDIDATE))
        self.assertEqual(len(evaluator.calls[0][1]), 3)

    def test_learned_intention_tag_does_not_bias_ranking(self):
        without, with_intent = make_frame(), make_frame(tagged=COLLECT)
        self.assertEqual([c.candidate_ref for c in without.candidates],
                         [c.candidate_ref for c in with_intent.candidates])
        self.assertNotEqual(without.frame_ref, with_intent.frame_ref)
        winners = []
        for frame in (without, with_intent):
            gate, _, _ = setup(scores={COLLECT: 1, EAT: 7, DRINK: 2})
            winners.append(gate.review(frame).suggested_candidate_ref)
        self.assertEqual(winners[0], winners[1])

    def test_candidate_selections_have_no_hardcoded_food_policy(self):
        for winner in (COLLECT, EAT, DRINK):
            with self.subTest(winner=winner):
                gate, _, _ = setup(scores={winner: 3})
                choice = gate.review(make_frame())
                self.assertEqual(choice.suggested_candidate_ref,
                    next(c.candidate_ref for c in make_frame().candidates
                         if c.semantic_ref == winner))

    def test_equal_top_valuations_abstain_no_lexical_tiebreak(self):
        for tagged in (None, COLLECT):
            gate, _, _ = setup(scores={COLLECT: 4, EAT: 4})
            choice = gate.review(make_frame(tagged=tagged))
            self.assertEqual(choice.status, "AMBIGUOUS")
            self.assertIsNone(choice.suggested_candidate_ref)
            self.assertEqual(len(choice.evaluated_candidate_refs), 3)

    def test_zero_and_negative_evidence_abstains(self):
        for scores in ({}, {COLLECT: -3, EAT: -1, DRINK: -2}):
            gate, ledger, evaluator = setup(scores=scores)
            result = gate.review(make_frame())
            self.assertEqual(result.status, "NO_POSITIVE_EVIDENCE")
            self.assertIsNone(result.suggested_candidate_ref)
            self.assertEqual(ledger.balance, 97)

    def test_one_positive_candidate_yields_advice_not_command(self):
        gate, _, _ = setup(scores={EAT: 1})
        result = gate.review(make_frame(visible=(EAT,)))
        self.assertEqual(result.status, "ADVISORY_ONLY")
        self.assertFalse({"command", "approved", "motor", "admission", "winner", "action"} &
                         {f.name for f in fields(CompetitionAdvice)})
        self.assertFalse(any(hasattr(gate, name) for name in
                             ("birth", "run_step", "dispatch", "execute", "admit_motor")))

    def test_no_candidates_evaluates_nothing_and_no_debit(self):
        frame = make_frame(visible=())
        gate, ledger, evaluator = setup(balance=0)
        advice = gate.review(frame)
        self.assertEqual(advice.status, "NO_CANDIDATES")
        self.assertEqual(ledger.calls, [])
        self.assertEqual(evaluator.calls, [])
        self.assertEqual(advice.evaluated_candidate_refs, ())
        self.assertEqual(advice.valuation_records, ())
        self.assertIsNone(advice.suggested_candidate_ref)

    def test_all_or_none_short_budget_denies_early_candidate_bias(self):
        for budget in (0, 1, 2):
            gate, ledger, evaluator = setup(balance=budget, scores={COLLECT: 100})
            result = gate.review(make_frame())
            self.assertEqual(result.status, "UNFUNDED")
            self.assertEqual(ledger.balance, budget)
            self.assertEqual(evaluator.calls, [])
            self.assertEqual(result.evaluated_candidate_refs, ())
            self.assertEqual(result.valuation_records, ())

    def test_exact_budget_funds_all_candidates_no_partial(self):
        gate, ledger, _ = setup(balance=3, scores={COLLECT: 1})
        self.assertEqual(gate.review(make_frame()).status, "ADVISORY_ONLY")
        self.assertEqual(ledger.balance, 0)

    def test_second_frame_new_capture_rebills_without_old_accumulators(self):
        gate, ledger, _ = setup(scores={EAT: 2})
        old = gate.review(make_frame(3))
        new = gate.review(make_frame(4))
        self.assertNotEqual(old.frame_ref, new.frame_ref)
        self.assertTrue(set(old.evaluated_candidate_refs).isdisjoint(
            new.evaluated_candidate_refs))
        self.assertEqual(ledger.balance, 94)
        self.assertEqual(len(ledger.calls), 2)
        self.assertEqual(len(new.receipt_refs), 3)

    def test_replay_same_frame_cannot_charge_twice(self):
        frame = make_frame()
        gate, ledger, _ = setup()
        gate.review(frame)
        with self.assertRaises(ValueError):
            gate.review(frame)
        self.assertEqual(len(ledger.calls), 1)

    def test_same_capture_different_frame_ref_no_second_charge(self):
        gate, ledger, _ = setup()
        frame = make_frame()
        gate.review(frame)
        spoof = replace(frame, frame_ref="frame:i2:"+"0"*64)
        with self.assertRaises(ValueError):
            gate.review(spoof)
        self.assertEqual(len(ledger.calls), 1)

    def test_old_step_rejected_pre_debit(self):
        gate, ledger, _ = setup()
        gate.review(make_frame(5))
        with self.assertRaises(ValueError):
            gate.review(make_frame(4))
        self.assertEqual(len(ledger.calls), 1)

    def test_cross_life_frame_refused(self):
        gate, ledger, _ = setup()
        with self.assertRaises(ValueError):
            gate.review(make_frame(life="life:other"))
        self.assertEqual(ledger.calls, [])

    def test_mutated_candidates_rejected_before_charging(self):
        frame = make_frame()
        bad = (
            replace(frame, candidates=frame.candidates[::-1]),
            replace(frame, candidates=(frame.candidates[0], frame.candidates[0])),
            replace(frame, candidates=(replace(frame.candidates[0],
                candidate_ref="candidate:i2:malformed"),)),
            replace(frame, candidates=(replace(frame.candidates[0],
                intention_ref="foreign:tag"),)),
            replace(frame, candidates=list(frame.candidates)),
            replace(frame, physical_step=True),
            replace(frame, claim_digest="a" * 63),
            replace(frame, frame_ref="bad frame ref"),
            replace(frame, candidates=("string",)),
        )
        for b in bad:
            with self.subTest(b=b):
                gate, ledger, _ = setup()
                with self.assertRaises(ValueError):
                    gate.review(b)
                self.assertEqual(ledger.calls, [])

    def test_max_candidates_is_a_software_bound_not_policy_priority(self):
        frame = make_frame(visible=())
        names = tuple(f"item:{i:03d}" for i in range(MAX_CANDIDATES+1))
        bad = replace(frame, candidates=tuple(SemanticCandidate(
            _bound_id("candidate", frame.life_ref, frame.claim_digest, s), s, None)
            for s in names))
        gate, ledger, _ = setup()
        with self.assertRaises(ValueError):
            gate.review(bad)
        self.assertEqual(ledger.calls, [])

    def test_batch_receipts_require_exact_set_and_canonical_order(self):
        frame = make_frame()
        mutations = [
            lambda r: r[:-1],
            lambda r: list(r),
            lambda r: r[::-1],
            lambda r: (r[0], r[0], r[2]),
            lambda r: tuple(replace(x, units=2) for x in r),
            lambda r: tuple(replace(x, units=True) for x in r),
            lambda r: tuple(replace(x, operation="wrong") for x in r),
            lambda r: tuple(replace(x, claim_digest="0"*64) for x in r),
            lambda r: tuple(replace(x, frame_ref="frame:alien") for x in r),
            lambda r: tuple(replace(x, life_ref="life:alien") for x in r),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                gate, ledger, evidence = setup()
                ledger.tamper = mutate
                with self.assertRaises(ValueError):
                    gate.review(frame)
                self.assertEqual(evidence.calls, [])
                self.assertEqual(len(ledger.calls), 1)

    def test_reused_receipt_across_frames_rejected(self):
        gate, ledger, evidence = setup(scores={EAT: 3})
        gate.review(make_frame(3))
        first_ref = "synthetic:uc:1"
        ledger.tamper = lambda r: tuple(replace(x, ref=first_ref) if i == 0 else x
                                        for i, x in enumerate(r))
        with self.assertRaises(ValueError):
            gate.review(make_frame(4))
        self.assertEqual(len(evidence.calls), 1)

    def test_missing_or_misaligned_evidence_never_yields_advice(self):
        mutations = [
            lambda vals: vals[:-1],
            lambda vals: list(vals),
            lambda vals: vals[::-1],
            lambda vals: (vals[0], vals[0], vals[2]),
            lambda vals: tuple(replace(v, candidate_ref="candidate:alien") for v in vals),
            lambda vals: tuple(replace(v, receipt_ref="charge:unpaid") for v in vals),
            lambda vals: tuple(replace(v, value=True) for v in vals),
            lambda vals: tuple(replace(v, value=1.1) for v in vals),
            lambda vals: tuple(replace(v, value=1025) for v in vals),
            lambda vals: tuple(replace(v, evidence_ref="bad evidence ref") for v in vals),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                gate, ledger, ev = setup()
                ev.tamper = mutate
                with self.assertRaises(ValueError):
                    gate.review(make_frame())
                self.assertEqual(ledger.balance, 97)

    def test_after_debit_missing_values_no_free_retry(self):
        frame = make_frame()
        gate, ledger, ev = setup()
        ev.throw = True
        with self.assertRaises(ValueError):
            gate.review(frame)
        self.assertEqual(ledger.balance, 97)
        with self.assertRaises(ValueError):
            gate.review(frame)
        self.assertEqual(ledger.balance, 97)

    def test_uncertain_external_charge_response_no_free_retry(self):
        frame = make_frame()
        gate, ledger, _ = setup()
        ledger.raise_after_charge = True
        with self.assertRaises(RuntimeError):
            gate.review(frame)
        with self.assertRaises(ValueError):
            gate.review(frame)
        self.assertEqual(ledger.balance, 97)

    def test_refusal_is_not_a_real_financial_ledger_or_m11(self):
        gate, ledger, _ = setup(balance=0)
        gate.review(make_frame())
        self.assertFalse(any(hasattr(gate, n) for n in
                             ("cold_recover", "scheduler", "m11", "commit", "world")))
        self.assertEqual(ledger.balance, 0)

    def test_veto_preview_always_remains_motor_unauthorized(self):
        gate, _, _ = setup(scores={EAT: 10})
        advice = gate.review(make_frame())
        veto = veto_preview(advice, vetoed=True)
        cleared = veto_preview(advice, vetoed=False)
        self.assertEqual(veto.status, "VETOED")
        self.assertIsNone(veto.suggested_candidate_ref)
        self.assertEqual(cleared.status, "NOT_ADMITTED")
        self.assertEqual(cleared.suggested_candidate_ref, advice.suggested_candidate_ref)
        self.assertEqual(veto.motor_authority, "NONE")
        self.assertEqual(cleared.motor_authority, "NONE")
        self.assertFalse({"command", "admit", "execute", "action"} &
                         {f.name for f in fields(VetoPreview)})

    def test_veto_preview_rejects_truthy_nonbool_and_forged_inputs(self):
        gate, _, _ = setup()
        advice = gate.review(make_frame())
        for v in (1, "false", None):
            with self.subTest(v=v), self.assertRaises(ValueError):
                veto_preview(advice, vetoed=v)
        with self.assertRaises(ValueError):
            veto_preview("candidate:anything", vetoed=False)

    def test_veto_on_no_advice_cannot_summon_a_candidate(self):
        gate, _, _ = setup()
        advice = gate.review(make_frame())
        self.assertIsNone(veto_preview(advice, vetoed=False).suggested_candidate_ref)
        self.assertIsNone(veto_preview(advice, vetoed=True).suggested_candidate_ref)

    def test_both_ports_mandatory_no_default_unpaid_choice(self):
        options = (
            (None, SyntheticBatchLedger(), SyntheticEvidence()),
            (SyntheticFrameSource(), None, SyntheticEvidence()),
            (SyntheticFrameSource(), SyntheticBatchLedger(), None),
        )
        for source, ledger, ev in options:
            with self.assertRaises(ValueError):
                CompetitionPreview(life_ref=LIFE, frame_authority=source,
                                   ledger=ledger, evidence=ev)

    def test_two_thread_attempts_same_frame_only_one_evaluated(self):
        gate, ledger, _ = setup(scores={EAT: 2})
        frame = make_frame()
        def attempt(_):
            try:
                return gate.review(frame).status
            except ValueError:
                return "REJECTED_REPLAY"
        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = list(pool.map(attempt, (0, 1)))
        self.assertCountEqual(statuses, ["ADVISORY_ONLY", "REJECTED_REPLAY"])
        self.assertEqual(len(ledger.calls), 1)


if __name__ == "__main__":
    unittest.main()