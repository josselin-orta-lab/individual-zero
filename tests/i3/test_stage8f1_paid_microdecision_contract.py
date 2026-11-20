"""Stage8-F1 DEVELOPMENT-ONLY: synthetic payment and motor-authority falsifiers.

No WorldSpec, no run_life, no birth, no alteration of closed Stage8-E2 source.
"""
import unittest

from i3.modules.body import (ACTION_COSTS, BodyLaws, CognitiveBudget,
                             CognitiveFundingError, CognitiveWork,
                             cognitive_cost, transition)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.stage8f1_paid_microdecision_mind import (
    CANDIDATE, EVIDENCE, MICRO_WORK, PaidMicrodecisionMind,
    PaidMicrodecisionEqualPaidDiscardMind)


def cap(energy=.052, food=75., water=75., integrity=90., vigilance=95.,
        at_water=False, open_neighbors=0):
    return {
        "body":(energy,food,water,integrity,vigilance),
        "inventory":(),
        "here":(at_water,()),
        "neighbors":tuple((False,()) if i < open_neighbors else None
                          for i in range(4)),
    }


def prediction(sleep_energy=0.,sleep_water=0.):
    def personally_learned(key):
        if key==("dormir",):
            return ((sleep_energy,-.15,sleep_water,0.,4.),.02)
        return ((0.,0.,0.,0.,0.),1.)
    return personally_learned


class Stage8F1UnwiredPaidMicrodecisionTests(unittest.TestCase):
    def mind(self):
        return PaidMicrodecisionMind(midpoint(),1234)

    def test_reference_cannot_pay_original_three_cycle_start(self):
        c=cap()
        ref=Mind(midpoint(),1234)
        allowance=CognitiveBudget(c["body"],BodyLaws())
        act,param,work,info=ref.decide(c,allowance)
        self.assertIsNone(act)
        self.assertEqual(info["funding"],"NO_PROCESSING_BUDGET")
        self.assertEqual(work,CognitiveWork())
        self.assertEqual(allowance.work,CognitiveWork())

    def test_low_energy_genuine_learned_sleep_choice_after_prepayment(self):
        c=cap()
        m=self.mind()
        m._read_plan_prediction=prediction(sleep_energy=3.,sleep_water=0.)
        budget=CognitiveBudget(c["body"],BodyLaws())
        action,param,work,info=m.decide(c,budget)
        self.assertEqual(action,"dormir")
        self.assertIsNone(param)
        self.assertEqual(work,MICRO_WORK)
        self.assertEqual(budget.work,work)
        self.assertEqual(info["funding"],"F1_PAID_SELF_SELECTED_ACTION")
        self.assertEqual(info["option"],"dormir")
        self.assertEqual(info["candidate"],CANDIDATE)
        self.assertEqual(info["experimental"],EVIDENCE)
        self.assertEqual(info["offered_motor_options"],1)
        self.assertEqual(m.last[2],"dormir")
        self.assertGreater(budget.remaining[0],0)
        self.assertLess(budget.remaining[0],c["body"][0])
        # Physics is still the separate world's paid, hydrated sleep recovery.
        nxt,_=transition(c["body"],action,BodyLaws(),work)
        self.assertAlmostEqual(nxt[0],c["body"][0]-cognitive_cost(BodyLaws(),work)[0]+3.)

    def test_no_sleep_bonus_or_forced_rest_when_self_model_is_unfavorable(self):
        c=cap()
        m=self.mind()
        m._read_plan_prediction=prediction(sleep_energy=-.02,sleep_water=-50.)
        budget=CognitiveBudget(c["body"],BodyLaws())
        action,param,work,info=m.decide(c,budget)
        self.assertIsNone(action)
        self.assertIsNone(param)
        self.assertEqual(info["funding"],"F1_PAID_VOLUNTARY_ABSTENTION")
        self.assertEqual(info["option"],"abstain")
        self.assertIsNone(m.last)
        self.assertEqual(budget.work,MICRO_WORK)
        self.assertLess(budget.remaining[0],c["body"][0])
        nxt,_=transition(c["body"],None,BodyLaws(),work)
        self.assertAlmostEqual(nxt[0],budget.remaining[0]) # no free sleep

    def test_unlearned_equal_forecasts_choose_paid_abstention(self):
        m=self.mind()
        m._read_plan_prediction=prediction(0.,0.)
        c=cap()
        b=CognitiveBudget(c["body"],BodyLaws())
        a,p,work,info=m.decide(c,b)
        self.assertIsNone(a)
        self.assertEqual(info["funding"],"F1_PAID_VOLUNTARY_ABSTENTION")
        self.assertNotEqual(work,CognitiveWork())
        self.assertEqual(b.work,work)

    def test_no_borrow_from_future_recovery_when_micro_bill_is_unaffordable(self):
        m=self.mind()
        m._read_plan_prediction=prediction(3.)
        c=cap(energy=.03)
        b=CognitiveBudget(c["body"],BodyLaws())
        a,p,work,info=m.decide(c,b)
        self.assertIsNone(a)
        self.assertEqual(info["funding"],"NO_PROCESSING_BUDGET")
        self.assertEqual(work,CognitiveWork())
        self.assertEqual(b.remaining,c["body"])
        self.assertIsNone(m.last)

    def test_no_processing_or_motor_choice_after_vital_death(self):
        m=self.mind()
        c=cap(food=0.)
        b=CognitiveBudget(c["body"],BodyLaws())
        with self.assertRaisesRegex(ValueError,"death"):
            m.decide(c,b)
        self.assertEqual(b.work,CognitiveWork())

    def test_no_action_from_uncosted_hidden_world_or_unauthorized_water(self):
        m=self.mind()
        m._read_plan_prediction=prediction(0.)
        c=cap(energy=.052,at_water=True,open_neighbors=4)
        b=CognitiveBudget(c["body"],BodyLaws())
        a,_,work,info=m.decide(c,b)
        self.assertIsNone(a)
        self.assertEqual(work,MICRO_WORK)
        # With <0.03 remaining, no drink/move/wait is motor-fundable.
        self.assertEqual(info["offered_motor_options"],1)
        with self.assertRaises(CognitiveFundingError):
            transition(c["body"],"se_deplacer",BodyLaws(),work)

    def test_mismatched_body_allowance_never_admits_a_choice(self):
        m=self.mind()
        c=cap()
        b=CognitiveBudget(cap(energy=.08)["body"],BodyLaws())
        with self.assertRaisesRegex(ValueError,"allowance"):
            m.decide(c,b)

    def test_sleep_nominal_025_not_executed_by_frozen_world_physics(self):
        laws=BodyLaws()
        self.assertEqual(ACTION_COSTS["dormir"],.25)
        start=(20.,90.,90.,90.,90.)
        slept,_=transition(start,"dormir",laws,CognitiveWork())
        waited,_=transition(start,None,laws,CognitiveWork())
        self.assertAlmostEqual(slept[0],23.)
        self.assertAlmostEqual(waited[0],20.)
        # Paying the microdecision is separate and not a sleep-action debit.
        paid,_=transition(start,"dormir",laws,MICRO_WORK)
        self.assertAlmostEqual(paid[0],23.-cognitive_cost(laws,MICRO_WORK)[0])

    def test_equal_paid_discard_computes_learned_choice_but_never_motors(self):
        c=cap()
        real=self.mind()
        shadow=PaidMicrodecisionEqualPaidDiscardMind(midpoint(),1234)
        real._read_plan_prediction=prediction(sleep_energy=3.)
        shadow._read_plan_prediction=prediction(sleep_energy=3.)
        rb=CognitiveBudget(c["body"],BodyLaws())
        sb=CognitiveBudget(c["body"],BodyLaws())
        action,_,real_work,ri=real.decide(c,rb)
        control_action,_,control_work,si=shadow.decide(c,sb)
        self.assertEqual(action,"dormir")
        self.assertIsNone(control_action)
        self.assertEqual(real_work,control_work)
        self.assertEqual(real_work,MICRO_WORK)
        self.assertEqual(rb.remaining,sb.remaining)
        self.assertEqual(sb.work,real_work)
        self.assertEqual(si["funding"],"F1_EQUAL_PAID_MICRO_RESULT_DISCARDED")
        self.assertEqual(si["computed_and_discarded_option"],ri["option"])
        self.assertIsNone(shadow.last)
        self.assertIsNone(shadow.intention)
        slept,_=transition(c["body"],action,BodyLaws(),real_work)
        inactive,_=transition(c["body"],control_action,BodyLaws(),control_work)
        self.assertGreater(slept[0],inactive[0])
        self.assertAlmostEqual(inactive[0],sb.remaining[0])

    def test_equal_paid_discard_cannot_restore_work_if_micro_unfunded(self):
        m=PaidMicrodecisionEqualPaidDiscardMind(midpoint(),1234)
        c=cap(energy=.03)
        b=CognitiveBudget(c["body"],BodyLaws())
        action,_,work,info=m.decide(c,b)
        self.assertIsNone(action)
        self.assertEqual(info["funding"],"NO_PROCESSING_BUDGET")
        self.assertEqual(work,CognitiveWork())
        self.assertEqual(b.work,CognitiveWork())

    def test_micro_work_is_positive_two_currency_and_native_law_dependent(self):
        cost=cognitive_cost(BodyLaws(),MICRO_WORK)
        self.assertGreater(cost[0],0)
        self.assertGreater(cost[1],0)
        self.assertAlmostEqual(cost[0],.0328)
        self.assertAlmostEqual(cost[1],.05)
        self.assertLess(cost[0],.052)

if __name__ == "__main__":
    unittest.main()
