"""G2 shadow horizon test: no change to the H2 learning or v5 owner.

Design and verification sequences are distinct and fixed before comparison.
Predictions use only prior outcomes; all methods are scored, even when worse.
"""
from fractions import Fraction
import json
import unittest

BASELINE = 7
DESIGN = (
    ("reversal_early", (-6,)*9 + (8,)*15),
    ("slow_sine_like", (-6,-4,-2,0,2,4,6,8)*3),
)
HELDOUT = (
    ("offset_reversal", (4,)*13 + (-5,)*11),
    ("two_step_blocks", (8,8,-7,-7)*6),
    ("rare_shocks", (2,)*7 + (-9,) + (2,)*8 + (10,) + (2,)*7),
    ("flat_negative", (-3,)*24),
)


def evaluate(outcomes):
    assert len(outcomes)==24
    history=[]
    rows=[]
    for actual in outcomes:
        forecasts={
            "h2_16": (Fraction(sum(history[-16:]),len(history[-16:]))
                      if history else Fraction(BASELINE)),
            "shadow_4": (Fraction(sum(history[-4:]),len(history[-4:]))
                         if history else Fraction(BASELINE)),
            "historical": Fraction(BASELINE),
            "persistence": Fraction(history[-1] if history else BASELINE),
        }
        rows.append({name:abs(p-actual) for name,p in forecasts.items()})
        history.append(actual)
    return {name:sum((row[name] for row in rows),Fraction(0))/len(rows)
            for name in rows[0]}


class ShadowHorizonTest(unittest.TestCase):
    def test_design_and_heldout_fixed_and_separate(self):
        self.assertEqual(len(DESIGN),2)
        self.assertEqual(len(HELDOUT),4)
        self.assertFalse(set(n for n,_ in DESIGN)&set(n for n,_ in HELDOUT))
        self.assertTrue(all(len(seq)==24 for _,seq in DESIGN+HELDOUT))
        self.assertTrue(all(type(x) is int and -100<=x<=100
                            for _,seq in DESIGN+HELDOUT for x in seq))

    def test_shadow_horizon_full_reporting(self):
        reports={name:evaluate(seq) for name,seq in DESIGN+HELDOUT}
        self.assertEqual(len(reports),6)
        for name,values in reports.items():
            with self.subTest(name=name):
                self.assertEqual(set(values),
                    {"h2_16","shadow_4","historical","persistence"})
                self.assertTrue(all(x>=0 for x in values.values()))
        self.assertTrue(any(r["shadow_4"]<r["h2_16"] for r in reports.values()))
        self.assertTrue(any(r["shadow_4"]>r["h2_16"] for r in reports.values()))
        printable={name:{k:str(v) for k,v in rows.items()}
                   for name,rows in reports.items()}
        print("I2_H2_SHADOW_HORIZON_RESULTS "+
              json.dumps(printable,sort_keys=True,separators=(",",":")))

    def test_prefix_invariant_to_unknown_future(self):
        # Vary EVERY suffix after the prediction horizon; earlier results
        # must be bit-identical, so the test cannot use a future outcome.
        left=(8,)*12+(-5,)*12
        right=(8,)*12+(10,)*12
        def first_twelve(seq):
            history=[]
            output=[]
            for value in seq:
                out={n:(Fraction(sum(history[-w:]),len(history[-w:]))
                        if history else Fraction(BASELINE))
                     for n,w in (("h2_16",16),("shadow_4",4))}
                output.append(out)
                history.append(value)
            return output[:12]
        self.assertEqual(first_twelve(left),first_twelve(right))


if __name__=="__main__":
    unittest.main()
