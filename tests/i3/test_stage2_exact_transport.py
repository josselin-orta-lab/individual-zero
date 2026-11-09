"""Stage-2.1 exact transport (ADR-0019): fail-closed admission, one path, tickets."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from i3.lab import engineering_cohort as ENG
from i3.lab import p2_ecologies as P2
from i3.lab import stage2_admission as ADM
from i3.lab import stage2_panel as SP
from i3.modules.genome import generation_zero
from i3.runtime import admission as RA
from i3.runtime.life import run_life

PLAN = ROOT / "src/i3/docs/studies/stage2-replay-gate-development-80-81/PLAN.json"


class FailClosedAdmissionTests(unittest.TestCase):
    def setUp(self):
        self._world_for = P2.world_for

        def forbidden(*a, **k):
            raise AssertionError("a scientific World was constructed")
        P2.world_for = forbidden

    def tearDown(self):
        P2.world_for = self._world_for

    def test_every_scientific_cohort_fails_closed_before_any_world(self):
        # Preserve the pre-lift admission contract independently of today's
        # owner-lifted canonical ledger. No scientific World is constructed.
        with patch.object(ADM, "canonical_owner_lift_recorded", return_value=False):
            for cohort in RA.SCIENTIFIC_COHORTS:
                with self.assertRaises(PermissionError):
                    ADM.admit(cohort, "stable", 80, PLAN)

    def test_status_ledger_without_lift_or_with_wrong_fingerprint_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            status = Path(tmp) / "STATUS.md"
            status.write_text("ADR-0017 OWNER LIFT: Stage-2.1 transport " + "0" * 64 + "\n")
            self.assertFalse(ADM.owner_lift_recorded(status.read_text(),
                                                       ADM.transport_fingerprint(PLAN)))
            with patch.object(ADM, "canonical_owner_lift_recorded", return_value=False):
                with self.assertRaises(PermissionError):
                    ADM.admit("development", "stable", 80, PLAN)

    def test_fake_owner_lift_file_cannot_authorize_scientific_cohort(self):
        fingerprint = ADM.transport_fingerprint(PLAN)
        with tempfile.TemporaryDirectory() as tmp:
            forged_status = Path(tmp) / "STATUS.md"
            forged_status.write_text("note\n" + ADM.LIFT_PREFIX + fingerprint + "\n")
            self.assertTrue(ADM.owner_lift_recorded(forged_status.read_text(), fingerprint))
            # The historic lift remains on disk but cannot lift altered source.
            self.assertFalse(ADM.canonical_owner_lift_recorded(fingerprint))
            with patch.object(ADM, "canonical_owner_lift_recorded", return_value=False):
                with self.assertRaises(PermissionError):
                    ADM.admit("development", "stable", 80, PLAN)
            with self.assertRaises(TypeError):
                ADM.admit("development", "stable", 80, PLAN,
                          lift_status_path=forged_status)
            with self.assertRaises(TypeError):
                SP.execute(PLAN, Path(tmp) / "out",
                           lift_status_path=forged_status)
        self.assertEqual(ADM.CANONICAL_STATUS_PATH.resolve(),
                         ROOT / "src/i3/docs/STATUS.md")

    def test_scientific_execute_fails_before_creating_anything(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "never"
            with patch.object(ADM, "canonical_owner_lift_recorded", return_value=True):
                with self.assertRaises(PermissionError):
                    SP.execute(PLAN, archive)
            self.assertFalse(archive.exists())

    def test_historical_lift_never_reopens_consumed_development_indices(self):
        # setUp makes scientific World construction a test failure. Even a
        # forged positive lift check cannot reopen 80/81 or new cohorts.
        fingerprint = ADM.transport_fingerprint(PLAN)
        self.assertFalse(ADM.canonical_owner_lift_recorded(fingerprint))
        with patch.object(ADM, "canonical_owner_lift_recorded", return_value=True):
            for cohort, index in (("development", 80), ("development", 81),
                                  ("selection", 72), ("validation", 120),
                                  ("reserve", 0)):
                with self.subTest(cohort=cohort, index=index):
                    with self.assertRaises(PermissionError):
                        ADM.admit(cohort, "stable", index, PLAN)


class TicketAndDispatchTests(unittest.TestCase):
    def test_engineering_ticket_is_bound_to_its_world(self):
        ticket, spec = ADM.admit("engineering", "pulse", 2, PLAN)
        self.assertEqual(ticket.world_name, spec.name)
        self.assertEqual(ticket.world_sha256, RA.world_sha256(spec))
        self.assertTrue(ENG.is_engineering_seed(ticket.world_seed))
        with self.assertRaises(ValueError):
            ADM.admit("engineering", "pulse", 5000, PLAN)

    def test_runtime_refuses_missing_forged_or_misbound_tickets(self):
        ticket, spec = ADM.admit("engineering", "stable", 2, PLAN)
        other = ENG.engineering_world("stable", 3)
        g = generation_zero(90011)
        with self.assertRaises(PermissionError):
            run_life(g, spec, 1, 5, decision_policy="p13_replay_gate_v1")
        with self.assertRaises(PermissionError):
            run_life(g, other, 1, 5, decision_policy="p13_replay_gate_v1", admission=ticket)
        from dataclasses import replace
        same_name_changed_spec = replace(spec, width=spec.width + 1)
        with self.assertRaises(PermissionError):
            run_life(g, same_name_changed_spec, 1, 5,
                     decision_policy="p13_replay_gate_v1", admission=ticket)
        forged = RA.AdmissionTicket("engineering", "stable", 2, ticket.world_seed,
                                    spec.name, ticket.world_sha256,
                                    ticket.transport_fingerprint, object())
        with self.assertRaises(PermissionError):
            run_life(g, spec, 1, 5, decision_policy="p13_replay_gate_v1", admission=forged)
        with self.assertRaises(ValueError):
            run_life(g, spec, 1, 5, decision_policy="reference", admission=ticket)

    def test_admitted_gate_lives_report_policy_summary_and_receipt(self):
        for policy, mode in (("p13_replay_gate_v1", "gate"),
                             ("p13_replay_gate_zero_perceived_cost_v1", "zero_perceived_cost"),
                             ("p13_replay_gate_random_equal_mean_v1", "random_equal_mean")):
            ticket, spec = ADM.admit("engineering", "depletion", 3, PLAN)
            life = run_life(generation_zero(90012), spec, 9_010_011, 30,
                            decision_policy=policy, admission=ticket)
            self.assertEqual(life["replay_gate"]["mode"], mode)
            self.assertEqual(life["admission"]["world_name"], life["world"])
            self.assertEqual(life["admission"]["world_sha256"],
                             life["manifest"]["world_sha256"])
            self.assertEqual(life["manifest"]["experimental_policy"]["name"], policy)
            if mode == "random_equal_mean":
                schedule = life["replay_gate"]["random_schedule"]
                self.assertEqual(schedule["mean_numerator"], 5532)
                self.assertEqual(schedule["mean_denominator"], 867)
                self.assertEqual(schedule["actual_replays_paid"],
                                 life["cognitive_accounting"]["replays_executed"])
                self.assertLessEqual(schedule["draws_funded"],
                                     schedule["lived_sleep_ordinals"])
                self.assertLessEqual(schedule["eligible_replays_scheduled"],
                                     schedule["nominal_replays_scheduled"])

    def test_only_the_guard_mints_tickets(self):
        callers = [p for p in (ROOT / "src/i3").rglob("*.py")
                   if "mint(" in p.read_text() and p.name not in ("admission.py",)]
        self.assertEqual([p.name for p in callers], ["stage2_admission.py"])


class LedgerTests(unittest.TestCase):
    def test_status_ledger_records_exact_owner_lift_and_only_one_transport(self):
        status = (ROOT / "src/i3/docs/STATUS.md").read_text()
        old_fingerprint = "dcada9e221f79b9450a4f05fecd20e60ac6595bb306aa871f29e45aefea0b6f1"
        current_fingerprint = ADM.transport_fingerprint(PLAN)
        self.assertTrue(ADM.owner_lift_recorded(status, old_fingerprint))
        self.assertEqual(status.count(ADM.LIFT_PREFIX + old_fingerprint), 1)
        self.assertNotEqual(current_fingerprint, old_fingerprint)
        self.assertFalse(ADM.canonical_owner_lift_recorded(current_fingerprint))
        self.assertFalse(ADM.owner_lift_recorded(status, "0" * 64))


class OnePathTests(unittest.TestCase):
    def test_rehearsal_and_pilot_share_shape_and_differ_only_by_namespace(self):
        plan = SP.load_plan(PLAN)
        eng, sci = SP.cases(plan, "engineering"), SP.cases(plan, "scientific")
        self.assertEqual(len(eng), 36)
        self.assertEqual(len(sci), 36)
        for a, b in zip(eng, sci):
            self.assertEqual((a["family"], a["policy"]), (b["family"], b["policy"]))
        self.assertEqual({c["cohort"] for c in eng}, {"engineering"})
        self.assertEqual({c["index"] for c in sci}, {80, 81})

    def test_fingerprint_covers_plan_and_transport_code(self):
        files = [p.name for p in ADM.transport_files(PLAN)]
        for name in ("life.py", "admission.py", "p13_replay_gate_mind.py", "mind.py",
                     "two_phase_panel.py", "stage2_admission.py", "stage2_panel.py",
                     "PLAN.json", "stage2_random_equal_mean.py"):
            self.assertIn(name, files)
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp) / "PLAN.json"
            data = json.loads(PLAN.read_text())
            data["horizon"] = 401
            changed.write_text(json.dumps(data))
            self.assertNotEqual(ADM.transport_fingerprint(changed), ADM.transport_fingerprint(PLAN))

    def test_four_arm_random_rehearsal_is_engineering_only(self):
        # Future random control is exercised on NON-EVIDENTIARY engineering
        # worlds, without changing the frozen three-arm 80/81 plan or Worlds.
        with tempfile.TemporaryDirectory() as tmp:
            mini = Path(tmp) / "PLAN.json"
            data = json.loads(PLAN.read_text())
            data["arms"].append("p13_replay_gate_random_equal_mean_v1")
            data["families"] = ["stable"]
            data["horizon"] = 25
            for ns in ("engineering", "scientific"):
                data[ns]["indices"] = data[ns]["indices"][:1]
                data[ns]["genome_seeds"] = data[ns]["genome_seeds"][:1]
            mini.write_text(json.dumps(data))
            report = SP.rehearse(mini)
            self.assertEqual(report["status"], "PASS", report)
            self.assertEqual((report["planned"], report["reduced"]), (4, 4))
            self.assertEqual(report["namespace"], "engineering")
            self.assertNotIn("rows", report)

    def test_miniature_rehearsal_passes_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            mini = Path(tmp) / "PLAN.json"
            data = json.loads(PLAN.read_text())
            data["families"] = ["stable"]
            data["horizon"] = 25
            for ns in ("engineering", "scientific"):
                data[ns]["indices"] = data[ns]["indices"][:1]
                data[ns]["genome_seeds"] = data[ns]["genome_seeds"][:1]
            mini.write_text(json.dumps(data))
            report = SP.rehearse(mini)
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual(report["planned"], 3)
        self.assertEqual(report["reduced"], 3)
        self.assertNotIn("rows", report)


if __name__ == "__main__":
    unittest.main()
