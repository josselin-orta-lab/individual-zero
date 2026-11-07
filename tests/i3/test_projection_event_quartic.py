"""Stage-1 fixed five-node event projection candidate D."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import projection_consistency_characterization as P
from i3.lab import projection_event_quartic_characterization as D
from i3.modules.body import BodyLaws, CognitiveBudget
from i3.modules.genome import midpoint


class EventQuarticProjectionTests(unittest.TestCase):
    def test_default_reference_remains_chunk_end(self):
        self.assertEqual(
            P.make_mind(midpoint()).projection_accounting,
            "chunk_end")

    def test_unit_chunks_match_endpoint_reference_values(self):
        body = (80., 30., 30., 80., 80.)
        a = P.make_mind(midpoint())
        b = P.make_mind(midpoint())
        a.proj_chunks = b.proj_chunks = (1,) * 40
        b.projection_accounting = "event_quartic"
        self.assertEqual(
            a.project(body, a._drift)[0],
            b.project(body, b._drift)[0])

    def test_linear_distress_is_exact(self):
        from copy import deepcopy
        from i3.modules import genome as G
        from i3.modules.mind import Mind

        g = G.midpoint()
        for ch in ("energy", "food", "integrity", "vigilance"):
            g["genes"][f"theta.{ch}"] = 30.0
        g["genes"]["theta.water"] = 90.0
        g["genes"]["p.water"] = 1.0
        truth = Mind(G.validate(g), 3)
        truth.effects.observe(("attendre",), (0., 0., -.1, 0., 0.))
        truth._drift = truth.drift()
        candidate = deepcopy(truth)

        body = (100., 100., 80., 100., 100.)
        truth.proj_chunks = P.PER_STEP
        truth.projection_accounting = "chunk_end"
        candidate.projection_accounting = "event_quartic"
        exact = truth.project(body, truth._drift)[0]
        approx = candidate.project(body, candidate._drift)[0]
        for e, a in zip(exact, approx):
            self.assertAlmostEqual(e, a, delta=1e-9 * max(1.0, abs(e)))

    def test_candidate_is_more_expensive_than_C_but_below_per_step_representative(self):
        body = (80., 30., 30., 80., 80.)
        c = P.make_mind(midpoint())
        d = P.make_mind(midpoint())
        c.projection_accounting = "event_quadratic"
        d.projection_accounting = "event_quartic"
        bc = CognitiveBudget(body, BodyLaws())
        bd = CognitiveBudget(body, BodyLaws())
        c.project(body, c._drift, bc)
        d.project(body, d._drift, bd)
        self.assertGreater(
            bd.work.simulated_steps,
            bc.work.simulated_steps)
        self.assertLess(
            bd.work.simulated_steps,
            len(P.PER_STEP))

    def test_frozen_characterization_records_verdict_without_forcing_pass(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "event-quartic.json"
            report = D.run(path)
            self.assertEqual(
                report["cases"],
                3 * len(tuple(P.genomes())) * len(tuple(P.bodies())))
            self.assertIn(
                report["selection"]["verdict"],
                ("EVENT_QUARTIC_PROMOTED_AS_OPT_IN_CANDIDATE",
                 "NO_CANDIDATE_PROMOTED"))
            loaded = json.loads(path.read_text())
            self.assertEqual(loaded, report)
            print("EVENT_QUARTIC_PROJECTION_CHARACTERIZATION", json.dumps({
                "stats": report["stats"],
                "invariant":
                    report["projection_equivalent_invariant_max_gap"],
                "paid_projection_units":
                    report["paid_projection_units"],
                "selection": report["selection"],
            }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
