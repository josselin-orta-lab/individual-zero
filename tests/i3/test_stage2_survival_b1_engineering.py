"""B1 new-world engineering G/R is not an admission into scientific lives."""
from copy import deepcopy
from unittest.mock import patch
import unittest

from i3.lab import stage2_survival_b1_engineering as B1
from i3.lab import stage2_survival_b1_sampling as SAMPLE
from i3.lab import stage2_survival_b1_worldspec_audit as SPECS
from i3.runtime import admission as RA


class NewWorldGRCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = B1.cases()

    def test_exact_first_96_public_preview_pairs_and_no_science(self):
        rows = self.rows
        self.assertEqual(len(rows), 192)
        preview = SAMPLE.preview(SAMPLE.PREVIEW_WITNESS)["proposed_units"]
        self.assertEqual({r["cohort"] for r in rows}, {"engineering"})
        self.assertEqual([r["index"] for r in rows[::2]], list(range(96)))
        for i in range(96):
            first, second, source = rows[2*i], rows[2*i+1], preview[i]
            with self.subTest(pair=i):
                self.assertEqual(first["policy"], "reference")
                self.assertEqual(second["policy"], "p13_replay_gate_v1")
                for name in ("pair_id", "world_seed", "genome_seed", "life_seed",
                             "family"):
                    self.assertEqual(first[name], source[name])
                    self.assertEqual(second[name], first[name])
                self.assertEqual(first["index"], source["ordinal"])
        self.assertEqual(len(set(x["world_seed"] for x in rows)), 96)
        self.assertEqual(len(set(x["genome_seed"] for x in rows)), 96)
        self.assertEqual(len(set(x["life_seed"] for x in rows)), 96)
        self.assertEqual(B1.HORIZON, 400)
        self.assertEqual(B1.LIVES, 192)
        self.assertEqual(rows, B1.cases())

    def test_no_forged_world_or_policy_case_gets_to_world_generator(self):
        cases = self.rows
        execute = B1._run_case(cases, "f" * 64)
        alterations = (
            {"cohort": "validation"},
            {"cohort": "development"},
            {"cohort": "reserve"},
            {"index": 96},
            {"index": True},
            {"world_seed": SAMPLE.WORLD_BASE + 1},
            {"family": "another_ecology"},
            {"genome_seed": SAMPLE.GENOME_BASE + 2},
            {"life_seed": SAMPLE.LIFE_BASE + 3},
            {"pair_id": "forged"},
            {"policy": "p13_replay_gate_zero_perceived_cost_v1"},
            {"policy": "p13_replay_gate_random_equal_mean_v1"},
        )
        for change in alterations:
            bad = dict(cases[0], **change)
            with self.subTest(change=change), patch.object(
                    SPECS, "_construct_f0_spec") as construct:
                with self.assertRaises(PermissionError):
                    execute(bad)
                construct.assert_not_called()
        with self.assertRaises(PermissionError):
            execute(None)

    def test_new_world_ticket_is_physically_bound_before_life_run(self):
        # Constructor is real; actual running of any individual's life
        # is explicitly mocked in the software unit-test phase.
        case = self.rows[1]
        def fake_run(genome, spec, seed, horizon, *, admission, **kwargs):
            self.assertEqual(seed, case["life_seed"])
            self.assertEqual(horizon, 400)
            self.assertEqual(kwargs["decision_policy"], case["policy"])
            self.assertEqual(kwargs["protocol"], B1.PROTOCOL)
            receipt = RA.verify(admission, spec)
            self.assertEqual(receipt["world_seed"], case["world_seed"])
            self.assertEqual(receipt["cohort"], "engineering")
            self.assertEqual(receipt["transport_fingerprint"], B1.source_fingerprint())
            return {"mocked": True}
        with patch.object(B1, "run_life", side_effect=fake_run):
            receipt = B1._run_case(self.rows, B1.source_fingerprint())(case)
        self.assertTrue(receipt["mocked"])
        self.assertEqual(receipt["admission_receipt"]["world_seed"],
                         case["world_seed"])
        self.assertEqual(receipt["admission_receipt"]["family"],
                         case["family"])

    def test_normal_fixed_arm_does_not_get_gate_ticket(self):
        case = self.rows[0]
        def no_ticket(*_args, admission=None, **_kwargs):
            self.assertIsNone(admission)
            return {"mocked": True}
        with patch.object(B1, "run_life", side_effect=no_ticket):
            result = B1._run_case(self.rows, B1.source_fingerprint())(case)
        self.assertEqual(result["admission_receipt"]["cohort"], "engineering")

    def test_rehearsal_only_returns_finite_structural_receipt(self):
        sample = {
            "schema": "i3-two-phase-panel/v1/sealed-rehearsal",
            "status": "PASS", "planned": 192, "generated": 192,
            "reduced": 192, "invariant_failures": {"settled": 0},
        }
        with patch.object(B1.TP, "sealed_rehearsal", return_value=sample):
            result = B1.rehearse()
        self.assertIs(result, sample)
        self.assertEqual(result["scientific_lives"], 0)
        self.assertEqual(result["scientific_admission"], "BLOCKED")
        self.assertFalse(result["observed_survival_results_published"])
        self.assertEqual(result["pair_count"], 96)
        self.assertTrue(result["public_root_synthetic"])
        self.assertFalse(result["independent_pairs_proven"])
        self.assertEqual(result["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(result["source_fingerprint"], B1.source_fingerprint())
        for field in ("death", "survival", "energy", "vigilance",
                      "mean_lived_steps", "rows", "genome"):
            self.assertNotIn(field, result)

    def test_guard_refuses_tampered_world_even_same_name_and_forged_source(self):
        from dataclasses import replace
        from i3.lab import stage2_admission as GUARD
        case = self.rows[1]
        spec = SPECS._construct_f0_spec(case["family"], case["world_seed"])
        for kwargs in (
            {"index": 96},
            {"index": True},
            {"world_seed": case["world_seed"] + 1},
            {"family": "unknown"},
            {"transport_fingerprint": "f" * 64},
        ):
            payload = {
                "family": case["family"], "index": case["index"],
                "world_seed": case["world_seed"], "spec": spec,
                "transport_fingerprint": B1.source_fingerprint(),
            }
            payload.update(kwargs)
            with self.subTest(change=kwargs), self.assertRaises(PermissionError):
                GUARD.admit_b1_newworld_engineering(**payload)
        fake = replace(spec, body=(1.0, 60.0, 60.0, 60.0, 60.0))
        with self.assertRaises(PermissionError):
            GUARD.admit_b1_newworld_engineering(
                family=case["family"], index=case["index"],
                world_seed=case["world_seed"], spec=fake,
                transport_fingerprint=B1.source_fingerprint())
        self.assertNotEqual(RA.world_sha256(spec), RA.world_sha256(fake))

    def test_no_scientific_entrypoint_or_unscoped_cli(self):
        for argv in (["prog", "run"], ["prog", "run", "archive"],
                     ["prog"], ["prog", "rehearse", "--scientific"]):
            with self.subTest(argv=argv), self.assertRaises(SystemExit):
                B1.main(argv)
        with self.assertRaises(PermissionError):
            B1.execute()
        with self.assertRaises(PermissionError):
            B1.execute("real_scientific_cohort", "new_archive")


if __name__ == "__main__":
    unittest.main()
