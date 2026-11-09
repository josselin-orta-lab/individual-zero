"""Stage-1 Candidate E: canonical event + fixed local quadratic-4."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.archive.stage1.lab import projection_candidate_e_characterization as E
from i3.lab import projection_consistency_characterization as P
from i3.lab import projection_end_to_end_numeric_oracle as O
from i3.modules.body import BodyLaws, CognitiveBudget
from i3.modules.genome import midpoint
from i3.modules.mind import PROJECTION_ACCOUNTING


class CandidateELocalQuadraticTests(unittest.TestCase):
    def test_candidate_is_opt_in_and_default_remains_reference(self):
        mind = P.make_mind(midpoint())
        self.assertEqual(mind.projection_accounting, "chunk_end")
        self.assertIn("event_local_quadratic4", PROJECTION_ACCOUNTING)

    def test_two_step_local_block_matches_direct_endpoint_accounting(self):
        body = (100., 100., 80., 100., 100.)
        candidate = P.make_mind(
            midpoint(), sleep_learned=False)
        exact = P.make_mind(
            midpoint(), sleep_learned=False)
        candidate.proj_chunks = (2,)
        candidate.projection_accounting = "event_local_quadratic4"
        exact.proj_chunks = (1, 1)
        exact.projection_accounting = "chunk_end"

        c_values, c_body = candidate.project(
            body, candidate._drift)
        e_values, e_body = exact.project(
            body, exact._drift)

        for a, b in zip(c_values, e_values):
            self.assertAlmostEqual(a, b, delta=1e-10)
        for a, b in zip(c_body, e_body):
            self.assertAlmostEqual(a, b, delta=1e-10)

    def test_exposed_boundary_uses_canonical_final_state(self):
        body = (80., 10., 80., 80., 80.)
        _candidate, candidate_body, _paid = E.direct(
            midpoint(), body, sleep_learned=True)
        _oracle, oracle_body, _oracle_paid = O.direct_projection(
            midpoint(), body, sleep_learned=True)
        for a, b in zip(candidate_body, oracle_body):
            self.assertAlmostEqual(a, b, delta=1e-10)

    def test_candidate_is_strictly_cheaper_on_representative_projection(self):
        body = (80., 30., 30., 80., 80.)
        mind = P.make_mind(midpoint(), sleep_learned=True)
        mind.projection_accounting = "event_local_quadratic4"
        budget = CognitiveBudget(body, BodyLaws())
        mind.project(body, mind._drift, budget)
        self.assertLess(budget.work.simulated_steps, 255)
        self.assertGreater(budget.work.simulated_steps, 0)

    def test_full_frozen_characterization_records_gate(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "candidate-e.json"
            report = E.run(path)
            loaded = json.loads(path.read_text())

        self.assertEqual(loaded, report)
        self.assertEqual(report["cases"], 486)
        self.assertEqual(
            report["selection"]["verdict"] in (
                "CANDIDATE_E_PROMOTED_AS_OPT_IN",
                "NO_CANDIDATE_PROMOTED"),
            True)
        self.assertFalse(report["default_changed"])
        self.assertFalse(report["reference_adoption_authorized"])
        print(
            "CANDIDATE_E_CHARACTERIZATION",
            json.dumps({
                "stats": report["stats"],
                "invariant":
                    report[
                        "projection_equivalent_invariant_max_gap"],
                "paid": report["paid_projection_units"],
                "selection": report["selection"],
                "omega_rerun_authorized":
                    report["omega_rerun_authorized"],
                "worst_cases": report["worst_cases"],
            }, sort_keys=True))

    def test_characterization_import_does_not_load_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.archive.stage1.lab.projection_candidate_e_characterization; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
