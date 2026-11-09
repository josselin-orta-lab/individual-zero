"""ADR-0017 pipeline and Stage-2.1 pilot plan tests (engineering worlds only)."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i3.lab import engineering_cohort as ENG
from i3.lab import p2_ecologies as P2
from i3.archive.stage2 import development_68_69 as PILOT
from i3.lab import two_phase_panel as TP


class EngineeringCohort(unittest.TestCase):
    def test_disjoint_and_never_evidence(self):
        for cohort in P2.COHORTS.values():
            self.assertTrue(ENG.ENGINEERING.stop <= cohort.start
                            or cohort.stop <= ENG.ENGINEERING.start)
        with self.assertRaises(PermissionError):
            ENG.assert_not_engineering(ENG.ENGINEERING[0])
        ENG.assert_not_engineering(P2.COHORTS["development"][68])

    def test_same_generator_as_p2(self):
        spec = ENG.engineering_world("stable", 0)
        self.assertEqual(spec, P2._generate_ecology("stable", 90_000))


class TwoPhase(unittest.TestCase):
    def test_generation_failure_stops_without_retry(self):
        def run_case(case):
            if case == 2:
                raise RuntimeError("boom")
            return {"x": case}
        with tempfile.TemporaryDirectory() as tmp:
            m = TP.generate([0, 1, 2, 3], run_case, tmp)
            self.assertEqual((m["status"], m["generated"]), ("ENGINEERING_FAILURE_NOT_A_DEATH", 2))
            with self.assertRaises(ValueError):
                list(TP.load_sealed(tmp))

    def test_reduction_defect_returns_no_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            TP.generate([0, 1, 2], lambda c: {"x": c}, tmp)
            def reducer(identity, life):
                if identity == 1:
                    raise KeyError("missing")
                return life["x"]
            r = TP.reduce(tmp, reducer)
            self.assertEqual(r["status"], "REDUCTION_DEFECT_PENDING_REPAIR")
            self.assertNotIn("rows", r)
            self.assertEqual(TP.reduce(tmp, lambda i, l: l["x"])["rows"], [0, 1, 2])

    def test_tampered_original_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            TP.generate([0, 1], lambda c: {"x": c}, tmp)
            (Path(tmp) / "life-001.json.gz").write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                list(TP.load_sealed(tmp))

    def test_rehearsal_returns_no_rows(self):
        report = TP.sealed_rehearsal([0, 1], lambda c: {"x": c, "mean_step_ms": 1.0},
                                     lambda i, l: l, lambda i, l: {"ok": True})
        self.assertEqual(report["status"], "PASS")
        self.assertNotIn("rows", report)


class PilotPlan(unittest.TestCase):
    def test_development_and_engineering_plans(self):
        dev, eng = PILOT.cases("development"), PILOT.cases("engineering")
        self.assertEqual((len(dev), len(eng)), (36, 36))
        self.assertEqual({c["world_seed"] for c in dev}, {2068, 2069})
        self.assertTrue(all(ENG.is_engineering_seed(c["world_seed"]) for c in eng))
        self.assertEqual({c["genome_seed"] for c in dev}, {909, 910})
        blocks = {}
        for c in dev:
            blocks.setdefault(c["block"], set()).add((c["life_seed"], c["policy"]))
        self.assertEqual(len(blocks), 12)
        for arms in blocks.values():
            self.assertEqual(len({s for s, _ in arms}), 1)
            self.assertEqual({p for _, p in arms}, set(PILOT.ARMS))


if __name__ == "__main__":
    unittest.main()
