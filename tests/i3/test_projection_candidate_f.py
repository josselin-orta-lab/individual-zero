"""Stage-1 Candidate F laboratory integration."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import projection_candidate_e_characterization as E
from i3.lab import projection_candidate_f_characterization as F
from i3.lab import projection_consistency_characterization as P
from i3.lab import projection_end_to_end_numeric_oracle as O
from i3.modules.body import BodyLaws, CognitiveBudget
from i3.modules.genome import midpoint


class CandidateFEndToEndTests(unittest.TestCase):
    def test_sparse_projector_matches_candidate_e_directly(self):
        body = (80., 30., 30., 80., 80.)
        mind = P.make_mind(midpoint(), sleep_learned=True)
        budget = CognitiveBudget(body, BodyLaws())
        with __import__("decimal").localcontext() as ctx:
            ctx.prec = 100
            state = [mind._projection_decimal(x) for x in body]
            values, final_state = F._project_sparse_decimal_state(
                mind, state, budget)
        e_values, e_body, e_paid = E.direct(
            midpoint(), body, sleep_learned=True)

        self.assertEqual(budget.work.simulated_steps, e_paid)
        for a, b in zip(values, e_values):
            self.assertAlmostEqual(a, b, delta=1e-12)
        for a, b in zip(
                (float(x) for x in final_state), e_body):
            self.assertAlmostEqual(a, b, delta=1e-12)

    def test_projection_equivalent_plan_is_continuous_end_to_end(self):
        body = (80., 20., 80., 80., 80.)
        values = F.values(
            midpoint(), body,
            sleep_learned=False,
            projection_equivalent=True)
        self.assertAlmostEqual(
            values["plus_1_wait"] - values["prefix"],
            0.0,
            delta=1e-3)
        self.assertAlmostEqual(
            values["plus_3_waits"] - values["prefix"],
            0.0,
            delta=1e-3)

    def test_candidate_f_keeps_candidate_e_direct_cost(self):
        body = (80., 30., 30., 80., 80.)
        _values, _final, paid = E.direct(
            midpoint(), body, sleep_learned=True)
        self.assertLess(paid, 255)

    def test_full_frozen_characterization_records_gate(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "candidate-f.json"
            report = F.run(path)
            loaded = json.loads(path.read_text())

        self.assertEqual(loaded, report)
        self.assertEqual(report["cases"], 486)
        self.assertIn(
            report["selection"]["verdict"],
            (
                "CANDIDATE_F_PASSES_LAB_SOFTWARE_GATE",
                "NO_CANDIDATE_PROMOTED",
            ))
        self.assertFalse(report["omega_rerun_authorized"])
        self.assertFalse(report["reference_adoption_authorized"])
        print(
            "CANDIDATE_F_CHARACTERIZATION",
            json.dumps({
                "stats": report["stats"],
                "invariant":
                    report[
                        "projection_equivalent_invariant_max_gap"],
                "paid": report["paid_projection_units"],
                "selection": report["selection"],
                "runtime_integration_authorized":
                    report[
                        "mind_runtime_integration_authorized"],
                "worst_cases": report["worst_cases"],
            }, sort_keys=True))

    def test_characterization_import_does_not_load_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.projection_candidate_f_characterization; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
