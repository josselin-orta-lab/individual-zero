"""Predeclared synthetic comparison: H2 against frozen historical forecast.

No WorldBody, M11, causal improvement, motor authority or scientific GO.
Use only information known BEFORE each heldout outcome.
"""
from fractions import Fraction
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_feedback_calibration import Source, opportunity, forecast, heldout
from i2.modules.delayed_credit_study import (
    empty_feedback_memory, read_feedback, learn_from_feedback,
)

class PairedAblationTests(unittest.TestCase):
    def run_scenario(self, values):
        source=Source()
        memory=empty_feedback_memory(opportunity(10))
        frozen=Fraction(forecast(10).predicted_outcome_difference)
        observed=[]
        for index, outcome in enumerate(values):
            step=10+index*15
            prediction=read_feedback(memory=memory,forecast=forecast(step),source=source)
            p,c=heldout(step+2,outcome,0)
            update=learn_from_feedback(memory=memory,readout=prediction,
                                       prepared=p,control=c,source=source)
            actual=Fraction(update.heldout_score.observed_outcome_difference)
            observed.append((prediction.predicted_outcome_difference,frozen,actual))
            memory=update.new_memory
        return observed

    def test_stable_negative_adaptation_can_improve_error(self):
        rows=self.run_scenario((-8,)*12)
        adaptive=sum(abs(p-y) for p,_,y in rows)
        frozen=sum(abs(f-y) for _,f,y in rows)
        self.assertEqual(rows[0][0],rows[0][1])
        self.assertLess(adaptive,frozen)

    def test_abrupt_reversal_can_hurt_adaptive_forecast(self):
        # No claim of universal improvement; a short reversal exposes
        # adaptation lag and the memory horizon.
        rows=self.run_scenario((-8,)*8+(7,))
        last=rows[-1]
        self.assertGreater(abs(last[0]-last[2]),abs(last[1]-last[2]))

    def test_alternating_outcomes_have_no_guaranteed_benefit(self):
        rows=self.run_scenario((-8,7)*6)
        self.assertEqual(len(rows),12)
        self.assertTrue(any(p != f for p,f,_ in rows))
        self.assertTrue(any(abs(p-y)>0 for p,_,y in rows))

    def test_foreign_context_cannot_read_or_update_this_memory(self):
        from dataclasses import replace
        memory=empty_feedback_memory(opportunity(10))
        foreign=replace(forecast(10),opportunity=replace(
            opportunity(10),context_signature=("context:foreign",)))
        with self.assertRaisesRegex(ValueError,"different context"):
            read_feedback(memory=memory,forecast=foreign,source=Source())

if __name__=="__main__":
    unittest.main()
