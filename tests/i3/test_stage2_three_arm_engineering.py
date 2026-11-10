"""Three-arm engineering custody tests; no actual life is run in tests."""
from copy import deepcopy
from unittest.mock import patch
import unittest

from i3.lab import stage2_three_arm_engineering as THREE
from i3.lab import stage2_survival_b1_sampling as SAMPLE
from i3.lab import stage2_survival_b1_worldspec_audit as SPECS
from i3.lab import stage2_admission as GUARD
from i3.runtime import admission as RA


class ThreeArmEngineeringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = THREE.cases()
        cls.source = THREE.SOURCE.source_fingerprint()

    def test_fixed_unused_triples_and_nonoverlap(self):
        rows = self.rows
        self.assertEqual(len(rows), 72)
        self.assertEqual([rows[i]["index"] for i in range(0, 72, 3)],
                         list(range(96, 120)))
        preview = SAMPLE.preview(SAMPLE.PREVIEW_WITNESS)["proposed_units"]
        for i in range(24):
            original = preview[i + 96]
            trio = rows[3*i:3*i+3]
            self.assertEqual(tuple(x["policy"] for x in trio), THREE.ARMS)
            for r in trio:
                self.assertEqual(r["cohort"], "engineering")
                for k in ("world_seed", "life_seed", "genome_seed", "family", "pair_id"):
                    self.assertEqual(r[k], original[k])
        self.assertEqual(len({r["world_seed"] for r in rows}), 24)
        self.assertEqual(len({r["life_seed"] for r in rows}), 24)
        self.assertEqual(THREE.cases(), rows)
        old = SAMPLE.preview(SAMPLE.PREVIEW_WITNESS)["proposed_units"][:96]
        self.assertTrue({r["world_seed"] for r in rows}.isdisjoint(
            {u["world_seed"] for u in old}))

    def test_mutation_of_case_rejected_before_world_or_life(self):
        runner = THREE._run_case(self.rows, self.source)
        for change in (
            {"index": 95}, {"index": 120}, {"index": True},
            {"cohort": "development"}, {"cohort": "selection"},
            {"cohort": "validation"}, {"cohort": "reserve"},
            {"family": "unknown"}, {"policy": "p13_replay_gate_zero_perceived_cost_v1"},
            {"life_seed": SAMPLE.LIFE_BASE+17},
            {"genome_seed": SAMPLE.GENOME_BASE+17},
            {"world_seed": SAMPLE.WORLD_BASE+17},
        ):
            case = dict(self.rows[0], **change)
            with self.subTest(change=change), patch.object(
                    SPECS, "_construct_f0_spec") as factory:
                with self.assertRaises(PermissionError):
                    runner(case)
                factory.assert_not_called()
        with self.assertRaises(PermissionError):
            runner(None)

    def test_all_three_policies_are_actually_funded_and_world_bound(self):
        row = self.rows[:3]
        def fake_run(genome, spec, seed, horizon, *, decision_policy, admission, **kw):
            self.assertEqual(horizon, THREE.HORIZON)
            self.assertEqual(seed, row[0]["life_seed"])
            self.assertEqual(kw["protocol"], THREE.PROTOCOL)
            if decision_policy == "reference":
                self.assertIsNone(admission)
            else:
                self.assertEqual(RA.verify(admission, spec)["cohort"], "engineering")
            return {"mocked": True}
        runner = THREE._run_case(self.rows, self.source)
        with patch.object(THREE, "run_life", side_effect=fake_run):
            for case in row:
                result = runner(case)
                self.assertTrue(result["mocked"])
                self.assertEqual(result["admission_receipt"]["index"], 96)

    def test_central_guard_rejects_forged_source_or_world(self):
        case = self.rows[2]
        spec = SPECS._construct_f0_spec(case["family"], case["world_seed"])
        with self.assertRaises(PermissionError):
            GUARD.admit_three_arm_newworld_engineering(
                case=case, spec=spec, transport_fingerprint="f"*64)
        from dataclasses import replace
        bad_spec = replace(spec, body=(1.0, 60.0, 60.0, 60.0, 60.0))
        with self.assertRaises(PermissionError):
            GUARD.admit_three_arm_newworld_engineering(
                case=case, spec=bad_spec, transport_fingerprint=self.source)
        ticket = GUARD.admit_three_arm_newworld_engineering(
            case=case, spec=spec, transport_fingerprint=self.source)
        self.assertEqual(RA.verify(ticket, spec)["world_sha256"],
                         RA.world_sha256(spec))

    def test_funding_invariants_reject_nominal_fiction(self):
        identity = self.rows[2]
        receipt = {"cohort": "engineering", "index": identity["index"],
                   "family": identity["family"], "world_seed": identity["world_seed"],
                   "world_name": "dummy", "world_sha256": "sha",
                   "transport_fingerprint": self.source}
        life = {
            "admission_receipt": receipt, "world": "dummy",
            "steps_lived": 400, "terminal": "censored",
            "actions": {"dormir": 5},
            "manifest": {"experimental_policy": {"name": identity["policy"]},
                         "world_sha256": "sha", "life_seed": identity["life_seed"]},
            "cognitive_accounting": {
                "totals": {"energy": {"unpaid": 0.0}, "vigilance": {"unpaid": 0.0}},
                "shortfall_steps": 0, "status": "SETTLED_FOR_DECLARED_WORK",
                "replays_executed": 9,
            },
            "replay_gate": {"random_schedule": {
                "nominal_replays_scheduled": 12,
                "eligible_replays_scheduled": 10,
                "actual_replays_paid": 9, "draws_funded": 2,
                "lived_sleep_ordinals": 5,
                "mean_numerator": 5532, "mean_denominator": 867}},
        }
        check = THREE._invariants(self.source)
        self.assertTrue(all(check(identity,life).values()))
        for change in (
            {"actual_replays_paid": 10},
            {"eligible_replays_scheduled": 8},
            {"nominal_replays_scheduled": 15},
            {"draws_funded": 6},
            {"mean_denominator": 866},
        ):
            broken = deepcopy(life)
            broken["replay_gate"]["random_schedule"].update(change)
            self.assertFalse(all(check(identity,broken).values()), change)
        self.assertEqual(THREE.execute.__name__, "execute")
        with self.assertRaises(PermissionError):
            THREE.execute()
        with self.assertRaises(SystemExit):
            THREE.main(["script","scientific"])

    def test_rehearsal_does_not_return_outcomes(self):
        sample={"status":"PASS","planned":72,"generated":72,
                "reduced":72,"invariant_failures":{"paid_energy":0}}
        with patch.object(THREE.TP,"sealed_rehearsal",return_value=sample):
            output=THREE.rehearse()
        self.assertIs(sample,output)
        self.assertEqual(output["scientific_lives"],0)
        self.assertEqual(output["scientific_admission"],"CLOSED")
        self.assertFalse(output["survival_outcomes_disclosed"])
        self.assertEqual(output["pair_count"],24)
        for forbidden in ("survival","death","energy","vigilance","rows","lives"):
            self.assertNotIn(forbidden,output)


if __name__ == "__main__":
    unittest.main()
