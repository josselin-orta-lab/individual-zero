"""Fixed synthetic local replay-content falsifier, no World construction."""
from copy import deepcopy
import random
import unittest

from i3.lab import stage2_replay_content_local as C
from i3.modules.body import BodyLaws, CognitiveFundingError


class LocalReplayContentTests(unittest.TestCase):
    def test_fixed_synthetic_states_have_twelve_distinct_memories(self):
        self.assertEqual(C.TRIALS,48)
        for i in range(C.TRIALS):
            mind=C.synthetic_mind(i)
            self.assertEqual(len(mind.buffer),12)
            self.assertEqual(len({x[0] for x in mind.buffer}),12)
            self.assertEqual([x[0] for x in mind.buffer],
                             list(map(float,range(12,0,-1))))

    def test_selection_only_changes_memory_identity_and_random_rng_is_separate(self):
        mind=C.synthetic_mind(0)
        state=random.getstate()
        internal=mind.rng.getstate()
        self.assertEqual(C.select_indices(mind.buffer,3,mode="priority",
                                          life_seed=9900000,trial=0),(0,1,2))
        a=C.select_indices(mind.buffer,3,mode="random_content",
                           life_seed=9900000,trial=0)
        self.assertEqual(a,C.select_indices(mind.buffer,3,
                         mode="random_content",life_seed=9900000,trial=0))
        self.assertEqual(len(a),len(set(a)))
        self.assertTrue(all(0<=i<12 for i in a))
        self.assertEqual(mind.rng.getstate(),internal)
        self.assertEqual(random.getstate(),state)
        for kw in ({"count":13},{"count":True},{"count":-1},
                   {"life_seed":True},{"trial":-1},{"mode":"unknown"}):
            params={"count":3,"mode":"random_content",
                    "life_seed":9900000,"trial":0}
            params.update(kw)
            with self.subTest(kw=kw),self.assertRaises(ValueError):
                C.select_indices(mind.buffer,**params)

    def test_actual_td_update_is_detached_and_equal_prepaid_work(self):
        mind=C.synthetic_mind(0)
        before=deepcopy(mind)
        priority=C.apply_detached_replays(mind,mode="priority",count=3,trial=0)
        random_arm=C.apply_detached_replays(mind,mode="random_content",
                                            count=3,trial=0)
        self.assertEqual(mind.values,before.values)
        self.assertEqual(list(mind.buffer),list(before.buffer))
        self.assertEqual(mind.rng.getstate(),before.rng.getstate())
        self.assertEqual(priority["replays_executed"],3)
        self.assertEqual(random_arm["replays_executed"],3)
        self.assertEqual(priority["prepaid_work"],random_arm["prepaid_work"])
        self.assertEqual(priority["would_debit_energy"],
                         random_arm["would_debit_energy"])
        self.assertEqual(priority["would_debit_vigilance"],
                         random_arm["would_debit_vigilance"])
        self.assertFalse(priority["world_debit_applied"])
        self.assertGreaterEqual(priority["absolute_update_L1"],0)
        self.assertNotEqual(priority["selected_indices"],
                            random_arm["selected_indices"])
        with self.assertRaises(CognitiveFundingError):
            C.apply_detached_replays(mind,mode="priority",count=3,
                                     body=(0.,65.,65.,90.,0.),trial=0)

    def test_fixed_complete_panel_and_no_biological_claim(self):
        report=C.probe()
        self.assertEqual(report["status"],"COMPLETE_SYNTHETIC_MECHANISM_ONLY")
        self.assertEqual(report["trial_count"],48)
        self.assertEqual(report["equal_actual_replays_per_arm"],3)
        self.assertTrue(report["identical_replay_work_and_projected_physical_tariff"])
        self.assertEqual(len(report["observations"]),48)
        self.assertTrue(report["no_source_mutation"])
        self.assertTrue(report["no_world_or_full_life_executed"])
        self.assertFalse(report["physical_debit_applied_by_world"])
        self.assertEqual(report["scientific_survival_verdict"],"NOT_ISSUED")
        self.assertGreater(report["differing_memory_subsets"],0)
        self.assertEqual(report,C.probe())


if __name__=="__main__":
    unittest.main()
