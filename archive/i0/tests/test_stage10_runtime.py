"""Stage-10 real life cycle: waking, sleeping, and same-step wake."""
import unittest
from lab.stage10_reference_fixture import build_stage10_reference_runtime

class Stage10RuntimeTests(unittest.TestCase):
    def test_single_metacognition_custodian(self):
        r=build_stage10_reference_runtime()
        ids=[o.owner_id for o in r.causal_owners]
        self.assertEqual(ids.count("metacognition_health"),1)
        self.assertEqual(len(ids),len(set(ids)))
        before=r._meta_custody.export_causal_state()
        r._meta_custody.restore_causal_state(before)
        self.assertEqual(r._meta_custody.export_causal_state(),before)

    def test_sleep_option_real_command_next_step_sleeping(self):
        r=build_stage10_reference_runtime(start_fatigued=True)
        first=r.run_step()
        self.assertEqual(first.execution_status,"applied")
        self.assertEqual(first.source,"decision")
        self.assertEqual(first.command_primitive,"dormir")
        self.assertEqual(r.sleep_session.mode,"awake")
        self.assertEqual(r.scheduler.t_monde,1)
        second=r.run_step()
        self.assertEqual(second.execution_status,"applied")
        self.assertEqual(second.source,"sleep")
        self.assertEqual(second.cycles_used,0)
        self.assertEqual(r.sleep_session.mode,"sleeping")
        self.assertEqual(r.scheduler.t_monde,2)
        self.assertLess(r.sleep_health.fatigue,1.0)
        kinds=[e.causal_event["kind"] for e in r.journal.entries]
        self.assertEqual(kinds.count("stage10_reduced_capture"),1)
        self.assertEqual(kinds.count("step_closed"),2)
        self.assertTrue(r.journal.verify())

    def test_waking_reuses_physical_step_and_runs_cognition(self):
        r=build_stage10_reference_runtime(start_fatigued=True)
        self.assertEqual(r.run_step().command_primitive,"dormir")
        self.assertEqual(r.run_step().source,"sleep")
        result=r.run_step()
        self.assertEqual(result.execution_status,"applied")
        self.assertEqual(r.scheduler.t_monde,3)
        self.assertEqual(r.sleep_session.mode,"awake")
        kinds=[e.causal_event["kind"] for e in r.journal.entries]
        self.assertEqual(kinds.count("stage10_reduced_capture"),2)
        self.assertIn("stage10_sleep_woke",kinds)
        self.assertEqual(kinds.count("step_closed"),3)
        self.assertTrue(r.journal.verify())

    def test_two_seeded_lives_have_identical_causal_bytes(self):
        a=build_stage10_reference_runtime(start_fatigued=True)
        b=build_stage10_reference_runtime(start_fatigued=True)
        for _ in range(3):
            a.run_step();b.run_step()
        self.assertEqual(a.journal.canonical_bytes(),b.journal.canonical_bytes())
        self.assertEqual(a.sleep_health.export_causal_state(),
                         b.sleep_health.export_causal_state())

if __name__ == "__main__":
    unittest.main()
