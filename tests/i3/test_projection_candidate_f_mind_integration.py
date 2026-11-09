"""Stage-1 Candidate F opt-in Mind integration."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.archive.stage1.lab import projection_candidate_f_characterization as F
from i3.archive.stage1.lab import projection_candidate_f_mind_integration as I
from i3.lab import projection_consistency_characterization as P
from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.genome import midpoint
from i3.modules.mind import Mind, SIMULATION_MODES


class CandidateFMindIntegrationTests(unittest.TestCase):
    def test_default_mode_is_reference_and_unknown_rejected(self):
        mind = Mind(midpoint(), 97)
        self.assertEqual(mind.simulation_mode, "reference")
        self.assertEqual(SIMULATION_MODES, ("reference", "candidate_f"))
        with self.assertRaises(ValueError):
            Mind(midpoint(), 97, simulation_mode="unknown")

    def test_reference_mode_matches_default_exactly(self):
        body = (80., 30., 30., 80., 80.)
        default = P.make_mind(midpoint(), sleep_learned=True)
        explicit = P.make_mind(midpoint(), sleep_learned=True)
        explicit.simulation_mode = "reference"
        a = default.simulate(
            body, P.PLANS["plus_3_waits"], P.HORIZON,
            CognitiveBudget(body, BodyLaws()))
        b = explicit.simulate(
            body, P.PLANS["plus_3_waits"], P.HORIZON,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(a, b)

    def test_candidate_f_invalid_pairing_fails_before_spending(self):
        body = (80., 30., 30., 80., 80.)
        mind = Mind(midpoint(), 97, simulation_mode="candidate_f")
        budget = CognitiveBudget(body, BodyLaws())
        with self.assertRaises(ValueError):
            mind.simulate(
                body, P.PLANS["prefix"], P.HORIZON, budget)
        self.assertEqual(budget.work, CognitiveWork())

    def test_integrated_candidate_matches_frozen_lab_representative(self):
        body = (80., 20., 80., 80., 80.)
        mind = P.make_mind(
            midpoint(),
            sleep_learned=False,
            projection_equivalent=True)
        mind.simulation_mode = "candidate_f"
        mind.projection_accounting = "event_local_quadratic4"
        integrated = mind.simulate(
            body, P.PLANS["plus_3_waits"], P.HORIZON,
            CognitiveBudget(body, BodyLaws()))[0]
        frozen = F.values(
            midpoint(), body,
            sleep_learned=False,
            projection_equivalent=True)["plus_3_waits"]
        self.assertAlmostEqual(integrated, frozen, delta=1e-12)

    def test_candidate_f_preserves_observer_first_forecast(self):
        body = (80., 30., 30., 80., 80.)
        mind = P.make_mind(midpoint(), sleep_learned=True)
        mind.simulation_mode = "candidate_f"
        mind.projection_accounting = "event_local_quadratic4"
        mind.observer_decision_diagnostics = True
        mind.simulate(
            body, P.PLANS["prefix"], P.HORIZON,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            mind._observer_first_forecast["action_key"],
            ("se_deplacer",))
        self.assertEqual(
            mind._observer_first_forecast["delta"],
            (-2., -.2, -.4, 0., 0.))

    def test_full_frozen_integration_parity_gate(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "candidate-f-integration.json"
            report = I.run(path)
            loaded = json.loads(path.read_text())

        self.assertEqual(loaded, report)
        self.assertEqual(report["cases"], 486)
        self.assertIn(
            report["verdict"],
            (
                "CANDIDATE_F_MIND_INTEGRATION_PASS",
                "CANDIDATE_F_MIND_INTEGRATION_FAIL",
            ))
        self.assertFalse(report["omega_rerun_authorized"])
        self.assertFalse(report["reference_adoption_authorized"])
        print(
            "CANDIDATE_F_MIND_INTEGRATION",
            json.dumps({
                "parity_error":
                    report["max_abs_value_error_vs_frozen_lab"],
                "paid": report["paid_projection_units"],
                "gate": report["gate"],
                "verdict": report["verdict"],
                "forecast_cost_contract_authorized":
                    report[
                        "forecast_cost_contract_authorized"],
                "worst_case": report["worst_case"],
            }, sort_keys=True))

    def test_integration_import_does_not_load_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.archive.stage1.lab.projection_candidate_f_mind_integration; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
