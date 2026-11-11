"""Stage 2.1 software-only phase-aligned readout: source, funds and seals."""
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_action_phase_readout_budget as E
from i3.lab.stage2_action_conditional_existing_effects import _fixture
from i3.lab.stage2_compact_paid_first_person_engineering import _source_seal
from i3.modules.body import (BodyLaws, CognitiveBudget, CognitiveWork,
                              cognitive_cost, debit_cognition)
from i3.modules.mind import Mind
from i3.modules.world import World

BODY = (30.,30.,30.,35.,30.)
IMMEDIATE = (27.,29.,29.,35.,29.)


def prepared(*, body=BODY, action="attendre", identity="synthetic-case"):
    mind=_fixture()
    budget=E._synthetic_budget(mind,body,action)
    original=_source_seal(mind)
    ticket=E.admit_and_freeze(
        mind=mind,capture_body=body,action=action,param=None,
        budget=budget,identity=identity)
    return mind,budget,ticket,original


def record_world(ticket,budget,*,body=IMMEDIATE,dead=()):
    ticket.observe_synthetic_world(
        seal=ticket.sha256,action="attendre",param=None,
        work=budget.work,body=body,dead=dead,
        accounting=debit_cognition(BODY,budget.laws,budget.work)[1])


class NativeActionPhaseReadoutBudgetTests(unittest.TestCase):
    def test_predeclared_technical_audit_never_creates_world(self):
        with patch.object(World,"__init__",
                          side_effect=AssertionError("no World allowed")
        ),patch("i3.runtime.life.run_life",
                side_effect=AssertionError("no life allowed")):
            receipt=E.audit()
        print("I3_ACTION_PHASE_MODEL_BUDGET_RESULT="+json.dumps(
            receipt,sort_keys=True))
        self.assertEqual(receipt["status"],
                         "SOFTWARE_PHASE_AND_PREAUTHORIZATION_CONTRACT_ONLY")
        self.assertEqual(receipt["primary_target_phase"],"POST_PAID_LEARNING")
        self.assertEqual(receipt["secondary_target_phase"],"IMMEDIATE_POST_WORLD")
        self.assertTrue(receipt["positive_learning_phase_target_diverges"])
        self.assertTrue(receipt["no_learning_phase_target_identical"])
        self.assertTrue(receipt["terminal_phase_target_identical"])
        self.assertTrue(receipt["explicit_unscored_right_censor"])
        self.assertEqual(receipt["actual_worlds_created"],0)
        self.assertEqual(receipt["actually_lived_readout_debits"],0)
        self.assertEqual(receipt["scientific_lives"],0)
        self.assertEqual(receipt["scientific_verdict"],"NOT_ISSUED")
        self.assertFalse(receipt["stage2_2_go"])
        self.assertTrue(receipt["native_model_admissions_only"])
        self.assertFalse(receipt["cost_tariff_host_cpu_calibrated"])
        self.assertFalse(receipt["experimental_utility_established"])

    def test_model_tariff_is_monotone_two_currency_not_measured_cpu(self):
        for n in (0,1,6,16,64,128,512):
            w=E.proposed_readout_work(n)
            self.assertEqual(w,CognitiveWork(cycles=6,memory_items=48+n))
            energy,vigilance=cognitive_cost(BodyLaws(),w)
            self.assertGreater(energy,0)
            self.assertGreater(vigilance,0)
            self.assertAlmostEqual(energy,0.12+0.0002*(48+n))
            self.assertAlmostEqual(vigilance,0.30)
        for bad in (-1,513,2.0,True,"6",None):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                E.proposed_readout_work(bad)

    def test_original_decision_prepaid_then_optional_authorized_without_mutation(self):
        mind,budget,ticket,old=prepared()
        self.assertIsInstance(ticket,E.SyntheticPhaseTicket)
        self.assertEqual(_source_seal(mind),old)
        self.assertTrue(ticket.payload["forecast_before_both_future_phases"])
        self.assertEqual(ticket.payload["primary_target_phase"],
                         E.PRIMARY_TARGET)
        self.assertEqual(ticket.payload["secondary_target_phase"],
                         E.SECONDARY_TARGET)
        self.assertEqual(ticket.payload["native_personal_memory_count"],0)
        self.assertEqual(ticket.payload["incremental_model_work"]["cycles"],6)
        self.assertEqual(ticket.payload["incremental_model_work"]["memory_items"],48)
        self.assertEqual(ticket.work,budget.work)
        self.assertTrue(ticket.sha256)
        self.assertEqual(len(ticket.sha256),64)
        e,v=cognitive_cost(budget.laws,budget.work)
        self.assertGreater(e,0)
        self.assertGreater(v,0)
        self.assertEqual(tuple(ticket.payload["frozen_forecasts"]),
                         ("action","global","persistence"))

    def test_low_energy_vigilance_and_motor_reserve_never_start_readout(self):
        # Original decision has its own paid work first, and optional
        # readout must not begin unless both currencies + motor fit.
        for before,reason in (
            ((.15,30.,30.,35.,50.),"energy"),
            ((20.,30.,30.,35.,.22),"vigilance"),
            ((.52,30.,30.,35.,50.),"motor_reserve")):
            mind=_fixture()
            budget=E._synthetic_budget(mind,before)
            old=_source_seal(mind)
            prior=budget.work
            remaining=budget.remaining
            with self.subTest(reason=reason),patch.object(
                    E,"passive_readouts",
                    side_effect=AssertionError("unfunded readout executed")):
                denial=E.admit_and_freeze(
                    mind=mind,capture_body=before,action="attendre",
                    param=None,budget=budget,
                    identity="synthetic-"+reason)
            self.assertEqual(denial["status"],"NO_FUNDED_READOUT")
            self.assertEqual(denial["work_added"],0)
            self.assertEqual(denial["readouts_executed"],0)
            self.assertEqual(prior,budget.work)
            self.assertEqual(remaining,budget.remaining)
            self.assertEqual(_source_seal(mind),old)

    def test_null_action_and_forged_action_cannot_claim_preselected_movement(self):
        mind=_fixture()
        b=CognitiveBudget(BODY,BodyLaws())
        self.assertTrue(b.try_spend(CognitiveWork(cycles=3,memory_items=12)))
        mind.last=None
        with patch.object(E,"passive_readouts",
                          side_effect=AssertionError("no action must not read")):
            missing=E.admit_and_freeze(
                mind=mind,capture_body=BODY,action=None,param=None,
                budget=b,identity="null-action")
        self.assertEqual(missing["status"],"NO_SELECTED_ACTION")
        self.assertEqual(b.work,CognitiveWork(cycles=3,memory_items=12))
        mind.last=(BODY,("attendre",),"attendre",None)
        for act,param,body in (
            ("boire",None,BODY),("attendre","N",BODY),
            ("invented",None,BODY),("attendre",None,(29.,30.,30.,35.,30.))):
            with self.subTest(act=act,param=param,body=body), self.assertRaises(
                    (ValueError,PermissionError)):
                E.admit_and_freeze(
                    mind=mind,capture_body=body,action=act,param=param,
                    budget=b,identity="forged-choice")
        no_decision=CognitiveBudget(BODY,BodyLaws())
        with self.assertRaises(PermissionError):
            E.admit_and_freeze(
                mind=mind,capture_body=BODY,action="attendre",
                param=None,budget=no_decision,identity="unfunded-original")

    def test_prior_native_buffer_bound_refusal_and_null_tuple_labels(self):
        mind=_fixture()
        mind.m_max=1
        record=(1.,BODY,BODY,False)
        mind.buffer.extend([record,record])
        b=E._synthetic_budget(mind,BODY)
        with self.assertRaises(ValueError),patch.object(
                E,"passive_readouts",
                side_effect=AssertionError("invalid source must not read")):
            E.admit_and_freeze(
                mind=mind,capture_body=BODY,action="attendre",
                param=None,budget=b,identity="genomic-memory-overflow")
        mind.buffer.pop()
        mind.buffer.pop()
        mind.buffer.append((1.,BODY,BODY,False,"forged_action"))
        before=b.work
        # Source integrity check happens only AFTER a successful budget grant;
        # such laboratory exceptions are not successful living receipts.
        with self.assertRaises(PermissionError):
            E.admit_and_freeze(
                mind=mind,capture_body=BODY,action="attendre",
                param=None,budget=b,identity="forged-buffer-label")
        self.assertNotEqual(b.work,before)

    def test_paid_phase_is_exact_debit_and_prevents_phase_switching(self):
        mind,b,t,original=prepared()
        with self.assertRaises(RuntimeError):
            t.score_synthetic(seal=t.sha256)
        with self.assertRaises(RuntimeError):
            t.observe_synthetic_learning(
                seal=t.sha256,status="PAID_LEARNING",
                work=CognitiveWork(cycles=2),
                body=IMMEDIATE,accounting=E._zero_account())
        with self.assertRaises(PermissionError):
            t.observe_synthetic_world(
                seal=t.sha256,action="boire",param=None,
                work=b.work,body=IMMEDIATE,dead=(),
                accounting=debit_cognition(BODY,b.laws,b.work)[1])
        wrong_account=debit_cognition(BODY,b.laws,b.work)[1]
        wrong_account["energy"]["paid"]-=.01
        with self.assertRaises(ValueError):
            t.observe_synthetic_world(
                seal=t.sha256,action="attendre",param=None,
                work=b.work,body=IMMEDIATE,dead=(),
                accounting=wrong_account)
        record_world(t,b)
        with self.assertRaises(RuntimeError):
            record_world(t,b)
        work=CognitiveWork(cycles=2,simulated_steps=16,memory_items=1)
        correct, receipt=debit_cognition(IMMEDIATE,b.laws,work)
        self.assertNotEqual(correct,IMMEDIATE)
        invalid_body=list(correct)
        invalid_body[2]-=.1  # cannot silently make extra water decay
        with self.assertRaises(ValueError):
            t.observe_synthetic_learning(
                seal=t.sha256,status="PAID_LEARNING",work=work,
                body=tuple(invalid_body),accounting=receipt)
        with self.assertRaises(ValueError):
            t.observe_synthetic_learning(
                seal=t.sha256,status="NO_FUNDED_LEARNING",work=work,
                body=IMMEDIATE,accounting=receipt)
        t.observe_synthetic_learning(
            seal=t.sha256,status="PAID_LEARNING",work=work,
            body=correct,accounting=receipt)
        scored=t.score_synthetic(seal=t.sha256)
        self.assertEqual(scored["status"],"SYNTHETIC_TWO_PHASE_SCORED")
        self.assertFalse(scored["terminal_observed"])
        self.assertNotEqual(scored["phase_targets"][E.PRIMARY_TARGET],
                            scored["phase_targets"][E.SECONDARY_TARGET])
        self.assertEqual(scored["phase_bodies"][E.PRIMARY_TARGET],correct)
        self.assertEqual(scored["phase_bodies"][E.SECONDARY_TARGET],IMMEDIATE)
        self.assertFalse(scored["native_living_debit_attested"])
        self.assertEqual(_source_seal(mind),original)
        with self.assertRaises(RuntimeError):
            t.score_synthetic(seal=t.sha256)
        with self.assertRaises(RuntimeError):
            t.right_censor_synthetic(seal=t.sha256)

    def test_unfunded_learning_terminal_and_horizon_censor_are_true_nulls(self):
        _,b,t,_=prepared(identity="zero-learning")
        record_world(t,b)
        t.observe_synthetic_learning(
            seal=t.sha256,status="NO_FUNDED_LEARNING",
            work=CognitiveWork(),body=IMMEDIATE,
            accounting=E._zero_account())
        score=t.score_synthetic(seal=t.sha256)
        self.assertEqual(score["phase_targets"][E.PRIMARY_TARGET],
                         score["phase_targets"][E.SECONDARY_TARGET])
        _,b,t,_=prepared(identity="terminal")
        terminal=(25.,29.,0.,35.,29.)
        record_world(t,b,body=terminal,dead=("zero_water",))
        work=CognitiveWork(cycles=2)
        post,receipt=debit_cognition(terminal,b.laws,work)
        with self.assertRaises(ValueError):
            t.observe_synthetic_learning(
                seal=t.sha256,status="PAID_LEARNING",work=work,
                body=post,accounting=receipt)
        t.observe_synthetic_learning(
            seal=t.sha256,status="TERMINAL_NO_LEARNING",
            work=CognitiveWork(),body=terminal,
            accounting=E._zero_account())
        score=t.score_synthetic(seal=t.sha256)
        self.assertTrue(score["terminal_observed"])
        self.assertEqual(score["phase_targets"][E.PRIMARY_TARGET],
                         -_fixture().d_max)
        self.assertEqual(score["phase_targets"][E.PRIMARY_TARGET],
                         score["phase_targets"][E.SECONDARY_TARGET])
        _,_,t,_=prepared(identity="censor")
        missing=t.right_censor_synthetic(seal=t.sha256)
        self.assertEqual(missing["status"],"RIGHT_CENSORED_NOT_SCORED")
        self.assertIsNone(missing["target"])
        self.assertIsNone(missing["squared_loss"])
        with self.assertRaises(RuntimeError):
            t.score_synthetic(seal=t.sha256)

    def test_tampering_with_preoutcome_seal_refuses_outcome_and_score(self):
        _,b,t,_=prepared(identity="tamper")
        sealed=t.sha256
        t.payload["frozen_forecasts"]["action"]=123.45
        with self.assertRaises(RuntimeError):
            t.observe_synthetic_world(
                seal=sealed,action="attendre",param=None,work=b.work,
                body=IMMEDIATE,dead=(),
                accounting=debit_cognition(BODY,b.laws,b.work)[1])
        _,b,t,_=prepared(identity="tamper-2")
        record_world(t,b)
        t.payload["selected_action"]="boire"
        with self.assertRaises(RuntimeError):
            t.observe_synthetic_learning(
                seal=t.sha256,status="NO_FUNDED_LEARNING",
                work=CognitiveWork(),body=IMMEDIATE,
                accounting=E._zero_account())


if __name__ == "__main__":
    unittest.main()
