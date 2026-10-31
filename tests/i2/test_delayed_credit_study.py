"""H2 synthetic temporal credit controls, never a living learning test."""
from dataclasses import fields, replace
from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.delayed_credit_study import (
    ClaimedLivedStep, DelayedCreditStudy, study_delayed_credit,
)

def step(i, action, delta, *, goal="goal:one", life="life:synthetic"):
    return ClaimedLivedStep(life, i, f"capture:{i}", goal, action,
                           f"admission:{i}", f"evidence:{i}",
                           None if delta is None else f"outcome:{i}", delta)

class Source:
    def __init__(self, accept=True):
        self.accept = accept
    def verify_lived(self, *, event):
        return self.accept

def study(*events, source=None, **kw):
    return study_delayed_credit(events=tuple(events),
                                source=Source() if source is None else source, **kw)

class TemporalCreditTests(unittest.TestCase):
    def test_later_benefit_can_offset_preparation_cost(self):
        before = study(step(1, "A", -2))
        after = study(step(1, "A", -2), step(2, "B", 10))
        self.assertEqual(dict(before.credits)["A"], -2)
        self.assertEqual(dict(after.credits), {"A": Fraction(3), "B": Fraction(10)})
        self.assertEqual(after.contributions[-2].lag, 1)
        self.assertEqual(after.contributions[-2].weight, Fraction(1, 2))
        self.assertEqual(after.motor_authority, "NONE")

    def test_neutral_adverse_missing_and_absent_preparation(self):
        a = step(1, "A", -2)
        for delta, expected in [(0,-2), (-8,-6), (None,-2)]:
            with self.subTest(delta=delta):
                self.assertEqual(dict(study(a, step(2,"B",delta)).credits)["A"], expected)
        self.assertNotIn("A", dict(study(step(2, "B", 10)).credits))

    def test_inverted_roles_have_no_semantic_priority(self):
        direct = dict(study(step(1,"A",-2),step(2,"B",10)).credits)
        swapped = dict(study(step(1,"B",-2),step(2,"A",10)).credits)
        self.assertEqual(direct["A"],swapped["B"])
        self.assertEqual(direct["B"],swapped["A"])

    def test_goal_switch_and_delay_cut_trace(self):
        x = study(step(1,"A",-2),step(2,"B",10,goal="goal:two"))
        y = study(step(1,"A",-2),step(11,"B",10))
        self.assertEqual(dict(x.credits)["A"],-2)
        self.assertEqual(dict(y.credits)["A"],-2)

    def test_incidental_action_exposes_noncausal_limitation(self):
        x = study(step(1,"A",0),step(2,"noise",0),step(3,"B",8))
        self.assertGreater(dict(x.credits)["noise"],0)
        self.assertEqual(x.interpretation,"TEMPORAL_ASSOCIATION_NOT_CAUSAL_PROOF")
        self.assertFalse(x.m11_authenticated)

    def test_identity_replay_and_unverified_provenance_rejected(self):
        a,b=step(1,"A",0),step(2,"B",4)
        cases=((a,a),(a,replace(b,capture_ref=a.capture_ref)),
               (a,replace(b,admission_ref=a.admission_ref)),
               (a,replace(b,outcome_ref=a.outcome_ref)),
               (a,replace(b,life_ref="life:foreign")),(b,a),
               (a,replace(b,physical_step=1)))
        for c in cases:
            with self.subTest(c=c),self.assertRaises(ValueError):
                study(*c)
        for bad_source in (Source(False),Source(1),None):
            with self.subTest(source=bad_source),self.assertRaises(ValueError):
                study(a,source=bad_source) if bad_source is not None else study_delayed_credit(events=(a,),source=None)

    def test_invalid_types_and_budgets_rejected(self):
        a=step(1,"A",0)
        for invalid in (replace(a,lived_delta=True),replace(a,lived_delta=101),
                        replace(a,physical_step=True),replace(a,goal_ref="with spaces"),
                        replace(a,lived_delta=None)):
            with self.subTest(item=invalid),self.assertRaises(ValueError):
                study(invalid)
        for kwargs in (dict(horizon=True),dict(horizon=33),
                       dict(decay_numerator=1,decay_denominator=1),
                       dict(decay_numerator=False),dict(decay_denominator=0)):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                study(a,**kwargs)
        for events in ([],[a],()):
            with self.subTest(events=events),self.assertRaises(ValueError):
                study_delayed_credit(events=events,source=Source())

    def test_determinism_and_no_motor_q_exports(self):
        a,b=step(1,"A",-2),step(2,"B",8)
        result=study(a,b)
        self.assertEqual(result,study(a,b))
        self.assertEqual(len(result.contributions),3)
        self.assertFalse({"command","winner","admission","Q","action"} &
                         {f.name for f in fields(DelayedCreditStudy)})
        self.assertFalse(result.scheduler_uc_authenticated)

if __name__ == "__main__":
    unittest.main()
