"""P2 audit controls: development-only provenance and correctly paid bills."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p2_cost_panel as panel
from i3.lab import p2_ecologies as eco
from i3.lab import p2_validation as validation
from i3.modules.body import CognitiveWork, BodyLaws


class P2CostPanelContractTests(unittest.TestCase):
    def test_panel_never_requests_selection_validation_or_reserve(self):
        self.assertEqual(panel.INDICES, (2, 3, 4, 5))
        self.assertEqual(panel.GENOME_SEEDS, (6000, 6001, 6002))
        self.assertEqual(panel.HORIZON, 120)
        self.assertEqual(set(eco.FAMILIES), {"stable", "depletion", "pulse"})
        self.assertEqual(panel.PROTOCOL, "i3-p2-development-charge-panel-v1")
        self.assertTrue(all(i not in (0, 1) for i in panel.INDICES))
        self.assertTrue(all(i < len(eco.COHORTS["development"]) for i in panel.INDICES))

    def test_payments_report_both_energy_and_vigilance(self):
        block = CognitiveWork(cycles=2, simulated_steps=3, memory_items=4, replays=1)
        result = panel._totals(BodyLaws(), (block, block))
        self.assertEqual(set(result), {"energy", "vigilance"})
        self.assertGreater(result["energy"], 0)
        self.assertGreater(result["vigilance"], 0)
        self.assertAlmostEqual(result["energy"], 2 * panel._totals(BodyLaws(), (block,))["energy"])

    def test_zero_reference_does_not_invent_division(self):
        self.assertEqual(panel._relative_difference(0, 0), 0)
        self.assertIsNone(panel._relative_difference(1, 0))
        self.assertAlmostEqual(panel._relative_difference(2, 4), -0.5)

    def test_cost_witness_requires_an_actual_complete_trace(self):
        with self.assertRaises(ValueError):
            validation.work_witness({
                "steps_lived": 1, "trace": [],
                "cognitive_accounting": {"shortfall_steps": 0, "pending_replays": 0}
            })

    def test_frozen_tariff_metadata_is_explicitly_not_exact_per_life(self):
        profile = validation.calibrate_fixed_tariff()
        self.assertEqual(profile["cohort"], "development")
        self.assertEqual(len(profile["calibration"]), 6)
        self.assertEqual(profile["sampled_ticks"] > 0, True)
        self.assertIn("not_per_instruction_equivalence", profile["purpose"])


if __name__ == "__main__":
    unittest.main()
