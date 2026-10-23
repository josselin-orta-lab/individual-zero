"""Fail-closed physical cohort analysis without modifying born I1."""
import sys
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from analyze_i1_population_cohort import analyze, _summarize

class CohortAnalysisTests(unittest.TestCase):
    def test_absent_cohort_refuses_claim(self):
        with self.assertRaises(ValueError):
            analyze([],expected_sha="test",candidates=[0,3],
                    worlds=["oasis"],seeds=[921])
    def test_missing_body_is_not_healthy(self):
        with self.assertRaises(ValueError):
            _summarize({"trajectory":[{"body":{}}],
                        "observed_steps":1,"steps_requested":1,"wal_entries":2,
                        "wal_head":"x","birth_capability_sha256":"x",
                        "birth_capability_manifest":{"birth_profile_sha256":"x"},
                        "effective_goal":{"hysteresis":.04,"critical":.35},
                        "status":"COMPLETED_WITHOUT_SCIENTIFIC_VERDICT",
                        "lifecycle":"dead"})
if __name__=="__main__":
    unittest.main()
