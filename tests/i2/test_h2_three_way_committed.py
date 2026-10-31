"""New read-only three-way G2 comparator, evaluated on committed v5 regimes."""
from fractions import Fraction
import unittest
from test_h2_frozen_regime_battery import FrozenH2Battery

REGIMES = (
    ("three_way_plateau", (2,)*10+(-7,)*14),
    ("three_way_blocks", (6,6,-5,-5)*6),
    ("three_way_shocks", (1,)*8+(-9,)+(1,)*7+(10,)+(1,)*7),
)

class ThreeWayCommittedTests(unittest.TestCase):
    def test_fixed_regimes_and_past_only_selection(self):
        self.assertEqual(len(REGIMES),3)
        for name, seq in REGIMES:
            with self.subTest(name=name):
                self.assertEqual(len(seq),24)
                old, shadow, three=FrozenH2Battery().run_regime(
                    name,seq,return_three=True)
                self.assertEqual(three["samples"],24)
                self.assertEqual(three["h2_16_mae"],old["adaptive_mae"])
                self.assertEqual(three["h2_4_mae"],shadow["h2_4_mae"])
                self.assertEqual(three["persistence_mae"],old["persistence_mae"])
                self.assertEqual(three["motor_authority"],"NONE")
                previous={key:[] for key in ("h2_16","h2_4","persistence")}
                order=tuple(previous)
                for row in three["rows"]:
                    choice=min(order,key=lambda key:(
                        sum(previous[key][-8:],Fraction(0)),order.index(key)))
                    self.assertEqual(row["choice"],choice)
                    self.assertEqual(row["error"],row[choice+"_error"])
                    for key in order:
                        previous[key].append(row[key+"_error"])
                self.assertEqual(three["selected_mae"],
                    sum((row["error"] for row in three["rows"]),Fraction(0))/24)

if __name__=="__main__":
    unittest.main()
