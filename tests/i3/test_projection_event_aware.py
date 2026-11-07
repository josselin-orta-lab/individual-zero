"""Stage-1 event-aware projection candidate C: software characterization."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import projection_consistency_characterization as P
from i3.lab import projection_event_aware_characterization as C
from i3.modules.body import BodyLaws, CognitiveBudget
from i3.modules.genome import midpoint


class EventAwareProjectionTests(unittest.TestCase):
    def test_default_reference_remains_chunk_end(self):
        mind = P.make_mind(midpoint())
        self.assertEqual(mind.projection_accounting, "chunk_end")

    def test_unit_chunks_match_endpoint_reference_values(self):
        body = (80., 30., 30., 80., 80.)
        a = P.make_mind(midpoint())
        b = P.make_mind(midpoint())
        a.proj_chunks = b.proj_chunks = (1,) * 40
        b.projection_accounting = "event_quadratic"
        self.assertEqual(
            a.project(body, a._drift)[0],
            b.project(body, b._drift)[0])

    def test_linear_distress_is_exact_under_quadratic_accounting(self):
        body = (100., 100., 80., 100., 100.)
        truth = P.linear_regime_mind() if hasattr(P, "linear_regime_mind") else None
        # The characterization module does not export the test helper, so
        # construct the same linear regime directly when absent.
        if truth is None:
            from i3.modules import genome as G
            g = G.midpoint()
            for ch in ("energy", "food", "integrity", "vigilance"):
                g["genes"][f"theta.{ch}"] = 30.0
            g["genes"]["theta.water"] = 90.0
            g["genes"]["p.water"] = 1.0
            from i3.modules.mind import Mind
            truth = Mind(G.validate(g), 3)
            truth.effects.observe(("attendre",), (0., 0., -.1, 0., 0.))
            truth._drift = truth.drift()
        event = P.make_mind(midpoint(), sleep_learned=False)
        # Use the exact same linear-regime model state for candidate.
        from copy import deepcopy
        event = deepcopy(truth)
        truth.proj_chunks = P.PER_STEP
        truth.projection_accounting = "chunk_end"
        event.projection_accounting = "event_quadratic"
        exact = truth.project(body, truth._drift)[0]
        approx = event.project(body, event._drift)[0]
        for e, a in zip(exact, approx):
            self.assertAlmostEqual(e, a, delta=1e-9 * max(1.0, abs(e)))

    def test_event_candidate_pays_dynamic_projection_evaluations(self):
        body = (80., 30., 30., 80., 80.)
        mind = P.make_mind(midpoint())
        mind.projection_accounting = "event_quadratic"
        budget = CognitiveBudget(body, BodyLaws())
        mind.project(body, mind._drift, budget)
        self.assertGreater(budget.work.simulated_steps, len(mind.proj_chunks))
        self.assertLess(budget.work.simulated_steps, len(P.PER_STEP))

    def test_frozen_characterization_records_verdict_without_forcing_pass(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "event-aware.json"
            report = C.run(path)
            self.assertEqual(
                report["cases"],
                3 * len(tuple(P.genomes())) * len(tuple(P.bodies())))
            self.assertIn(
                report["selection"]["verdict"],
                ("EVENT_AWARE_PROMOTED_AS_OPT_IN_CANDIDATE",
                 "NO_CANDIDATE_PROMOTED"))
            self.assertLess(
                report["paid_projection_units"]["max"],
                report["paid_projection_units"]["per_step_truth"])
            loaded = json.loads(path.read_text())
            self.assertEqual(loaded, report)
            print("EVENT_AWARE_PROJECTION_CHARACTERIZATION", json.dumps({
                "stats": report["stats"],
                "invariant":
                    report["projection_equivalent_invariant_max_gap"],
                "paid_projection_units": report["paid_projection_units"],
                "selection": report["selection"],
            }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
