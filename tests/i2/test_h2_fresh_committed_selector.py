"""Independent fixed G2 check of the already-frozen 4-vs-16 selector.

Four new 24-outcome regimes, no tuning or switching rules changed.
The only results are derived from 24 cold-replayed commits in one v5 owner
per regime. Publish all wins AND losses, and retain baseline comparators.
"""
import json
import unittest
from test_h2_frozen_regime_battery import FrozenH2Battery

FRESH = (
    ("fresh_plateau_switch", (3,) * 9 + (-6,) * 15),
    ("fresh_asymmetric_blocks", (6, 6, 6, -4, -4) * 4 + (6, 6, -4, -4)),
    ("fresh_spikes", (1,) * 8 + (-10,) + (1,) * 7 + (9,) + (1,) * 7),
    ("fresh_smooth_ramp", tuple(range(-11, 13))),
)

class FreshCommittedSelectorTests(unittest.TestCase):
    def test_independent_full_reporting_and_fault_recovery(self):
        self.assertEqual(len(FRESH), 4)
        self.assertEqual(len(set(name for name,_ in FRESH)), 4)
        self.assertTrue(all(len(sequence)==24 for _,sequence in FRESH))
        engine=FrozenH2Battery()
        reports={}
        for name,sequence in FRESH:
            with self.subTest(regime=name):
                old, shadow=engine.run_regime(
                    name,sequence,return_shadow=True,
                    fault_index=5 if name=="fresh_plateau_switch" else None,
                    lost_ack_index=13 if name=="fresh_plateau_switch" else None,
                )
                self.assertEqual(shadow["samples"],24)
                self.assertEqual(shadow["h2_16_mae"],old["adaptive_mae"])
                self.assertEqual(shadow["historical_mae"],old["historical_mae"])
                self.assertEqual(shadow["persistence_mae"],old["persistence_mae"])
                self.assertTrue(all(row["horizon"] in (4,16) for row in shadow["rows"]))
                self.assertEqual(shadow["motor_authority"],"NONE")
                self.assertFalse(shadow["m11_authenticated"])
                # Three-way selector stays an audited read-only research view.\n                # The existing runner now returns the three-way report below.\n                reports[name]={
                    "selected":str(shadow["selected_mae"]),
                    "h2_16":str(shadow["h2_16_mae"]),
                    "h2_4":str(shadow["h2_4_mae"]),
                    "historical":str(shadow["historical_mae"]),
                    "persistence":str(shadow["persistence_mae"]),
                    "short_horizon_count":sum(r["horizon"]==4 for r in shadow["rows"]),
                }
        self.assertEqual(len(reports),len(FRESH))
        print("I2_FRESH_COMMITTED_SELECTOR_RESULTS "+
              json.dumps(reports,sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    unittest.main()
