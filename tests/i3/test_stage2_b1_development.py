"""B1 scoped developmental experiment regression; tests create no life."""
from copy import deepcopy
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from i3.lab import stage2_b1_development as B1
from i3.lab import stage2_survival_b1_sampling as SAMPLE
from i3.lab import stage2_survival_b1_worldspec_audit as SPECS
from i3.lab import stage2_admission as GUARD
from i3.runtime import admission as RA


class NewDevelopmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = B1.cases()

    def test_exact_fixed96_and_independence_of_public_preview(self):
        rows = self.rows
        self.assertEqual(len(rows), 192)
        self.assertEqual(len({r["world_seed"] for r in rows}), 96)
        self.assertEqual(len({r["genome_seed"] for r in rows}), 96)
        self.assertEqual(len({r["life_seed"] for r in rows}), 96)
        self.assertEqual([r["index"] for r in rows[::2]], list(range(240000, 240096)))
        self.assertNotEqual(B1.load_plan()["witness"], SAMPLE.PREVIEW_WITNESS)
        self.assertEqual(rows, B1.cases())
        self.assertEqual({r["cohort"] for r in rows}, {"development"})
        self.assertTrue(all(rows[i]["policy"] == "reference"
                            and rows[i+1]["policy"] == "p13_replay_gate_v1"
                            for i in range(0, len(rows), 2)))
        for i in range(0, len(rows), 2):
            for k in ("index", "family", "world_seed", "genome_seed", "life_seed"):
                self.assertEqual(rows[i][k], rows[i + 1][k])

    def test_modified_cases_fail_before_world_construction(self):
        runner = B1._run_case(self.rows, B1.ENG.source_fingerprint())
        for edit in (
            {"cohort": "selection"}, {"cohort": "validation"},
            {"cohort": "reserve"}, {"index": 80}, {"index": 240096},
            {"index": True}, {"family": "unknown"},
            {"world_seed": SAMPLE.WORLD_BASE + 22},
            {"genome_seed": SAMPLE.GENOME_BASE + 2},
            {"life_seed": SAMPLE.LIFE_BASE + 3},
            {"policy": "p13_replay_gate_random_equal_mean_v1"},
            {"pair_id": "forged"},
        ):
            case = dict(self.rows[0], **edit)
            with self.subTest(edit=edit), patch.object(
                    SPECS, "_construct_f0_spec") as constructor:
                with self.assertRaises(PermissionError):
                    runner(case)
                constructor.assert_not_called()

    def test_guard_world_binding_and_ticket_scope(self):
        row = self.rows[1]
        spec = SPECS._construct_f0_spec(row["family"], row["world_seed"])
        fingerprint = B1.ENG.source_fingerprint()
        ticket = GUARD.admit_b1_newworld_development(
            case=row, spec=spec, transport_fingerprint=fingerprint)
        self.assertEqual(RA.verify(ticket, spec)["cohort"], "development")
        self.assertEqual(ticket.index, 240000)
        with self.assertRaises(PermissionError):
            GUARD.admit_b1_newworld_development(
                case=row, spec=spec, transport_fingerprint="f" * 64)
        from dataclasses import replace
        bad = replace(spec, body=(1.0, 60.0, 60.0, 60.0, 60.0))
        with self.assertRaises(PermissionError):
            GUARD.admit_b1_newworld_development(
                case=row, spec=bad, transport_fingerprint=fingerprint)

    def test_control_has_no_replay_gate_ticket_and_same_life_seed(self):
        fixed, gate = self.rows[:2]
        def fake_run(*args, admission=None, decision_policy=None, **kwargs):
            if decision_policy == "reference":
                self.assertIsNone(admission)
            else:
                self.assertEqual(RA.verify(admission, args[1])["cohort"], "development")
            self.assertEqual(args[2], fixed["life_seed"])
            return {"mocked": True}
        runner = B1._run_case(self.rows, B1.ENG.source_fingerprint())
        with patch.object(B1, "run_life", side_effect=fake_run):
            self.assertTrue(runner(fixed)["mocked"])
            self.assertTrue(runner(gate)["mocked"])

    def test_missing_original_or_swapped_pair_rejected(self):
        fake = []
        for row in self.rows:
            fake.append({**row, "terminal": "censored", "steps_lived": 400,
                         "world_sha256": str(row["world_seed"]),
                         "genome_sha256": str(row["genome_seed"]),
                         "source_sha256": "source",
                         "paid_energy": 5.0, "paid_vigilance": 6.0})
        summary = B1.analyze(self.rows, fake)
        self.assertEqual(summary["primary"]["pairs"], 96)
        self.assertEqual(summary["primary"]["gate_only"], 0)
        self.assertEqual(summary["primary"]["fixed_only"], 0)
        self.assertEqual(summary["scientific_decision"],
                         "EXPLORATORY_ONLY_NOT_CONFIRMATORY")
        self.assertFalse(summary["iid_sampling_independently_attested"])
        with self.assertRaises(ValueError):
            B1.analyze(self.rows, fake[:-1])
        swapped = deepcopy(fake)
        swapped[0], swapped[2] = swapped[2], swapped[0]
        with self.assertRaises(ValueError):
            B1.analyze(self.rows, swapped)
        adverse = deepcopy(fake)
        adverse[1]["terminal"] = "dead"
        adverse[1]["steps_lived"] = 100
        result = B1.analyze(self.rows, adverse)
        self.assertEqual(result["primary"]["fixed_only"], 1)
        self.assertEqual(result["primary"]["paired_risk_difference"], -1 / 96)

    def test_no_retry_and_no_science_admission_via_old_route(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d) / "cohort"
            directory.mkdir()
            (directory / "ATTEMPT_CLAIM.json").write_text("consumed")
            with self.assertRaises(PermissionError):
                B1.execute(directory)
        with self.assertRaises(PermissionError):
            GUARD.admit("development", "stable", 80, B1.PLAN)
        with self.assertRaises(PermissionError):
            GUARD.admit("validation", "stable", 90, B1.PLAN)


if __name__ == "__main__":
    unittest.main()
