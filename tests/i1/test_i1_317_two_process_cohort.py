"""#317 sleep cohort negative tests; synthetic evidence is never physical GO."""
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("audit_sleep317",ROOT/"tools/audit_i1_317_two_process_cohort.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class SleepCohortAuditTests(unittest.TestCase):
    def test_design_cannot_accept_partial_or_alien_cohort(self):
        with TemporaryDirectory() as folder:
            for sha in ("wrong", "f"*40):
                with self.assertRaises(ValueError):
                    mod.analyse(Path(folder),sha,verifier=lambda path: None)

    def test_rejects_unapplied_and_postmortem_and_missing_transition(self):
        with TemporaryDirectory() as folder:
            wal=Path(folder)/"test.wal"
            def scan(cmd="dormir", applied=1, close="normal", extra=False):
                attempt="a"
                rows=[
                    {"kind":"command_experienced","t_monde":1,
                     "attempt_ref":attempt,"emitter":"action_control","primitive":cmd},
                    {"kind":"world_transition_experienced","t_monde":1,
                     "attempt_ref":attempt,"body_after":{"water":{"$f64":"0x1.0p+5"}},
                     "position_after":{"x":8,"y":8}},
                    {"kind":"step_closed","t_monde":1,"attempt_ref":attempt,
                     "data":{"applied_command_count":applied,
                             "world_advance_count":1,"outcome":close}},
                ]
                if extra:
                    rows.extend([
                        {"kind":"command_experienced","t_monde":2,
                         "attempt_ref":"b","emitter":"action_control","primitive":"dormir"},
                        {"kind":"world_transition_experienced","t_monde":2,
                         "attempt_ref":"b","body_after":{"water":30},
                         "position_after":{"x":8,"y":8}},
                        {"kind":"step_closed","t_monde":2,"attempt_ref":"b",
                         "data":{"applied_command_count":1,
                                 "world_advance_count":1,"outcome":"normal"}}
                    ])
                wal.write_text("".join(json.dumps({"causal_event":x})+"\n" for x in rows))
                return mod._scan_physical_wal(wal)
            assert scan()["actions"]=={"dormir":1}
            self.assertEqual(scan(close="dead")["lifecycle"],"dead")
            for kwargs in ({"applied":0},{"close":"blocked"},{"close":"dead","extra":True}):
                with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                    scan(**kwargs)
            wal.write_text(json.dumps({"causal_event":{"kind":"step_closed","t_monde":1,
                            "attempt_ref":"a","data":{"outcome":"normal",
                            "applied_command_count":1,"world_advance_count":1}}})+"\n")
            with self.assertRaises(ValueError):
                mod._scan_physical_wal(wal)

    def test_night_is_not_inferred_before_step_201(self):
        with TemporaryDirectory() as folder:
            wal=Path(folder)/"test.wal"
            rows=[]
            for t in range(1,201):
                rows.extend([
                    {"kind":"command_experienced","t_monde":t,
                     "attempt_ref":str(t),"emitter":"action_control","primitive":"dormir"},
                    {"kind":"world_transition_experienced","t_monde":t,
                     "attempt_ref":str(t),"body_after":{"water":20},
                     "position_after":{"x":8,"y":8}},
                    {"kind":"step_closed","t_monde":t,"attempt_ref":str(t),
                     "data":{"outcome":"normal","applied_command_count":1,"world_advance_count":1}},
                ])
            wal.write_text("".join(json.dumps({"causal_event":r})+"\n" for r in rows))
            output=mod._scan_physical_wal(wal)
            self.assertEqual(output["night_observed_steps"],0)
            self.assertIsNone(output["night_sleep_fraction"])
            self.assertEqual(output["day_sleep_fraction"],1.0)


if __name__=="__main__":
    unittest.main()
