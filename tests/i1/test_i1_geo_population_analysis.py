"""Fail-closed geometry and WAL audit (no actor or world simulation changes)."""
import io
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from analyze_i1_geo_population import _physical_evidence, aggregate, PROFILES

class GeographicAuditTests(unittest.TestCase):
    def test_requires_all_mortal_wal_artifacts(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                aggregate(Path(d),"test-sha")
    def test_rejects_forged_wal_and_missing_chain(self):
        with self.assertRaises(ValueError):
            _physical_evidence(io.BytesIO(b'{"index":0}\n'),
                final_hash="0"*64,expected_count=1,water_positions={(8,8)})
        with self.assertRaises(ValueError):
            _physical_evidence(io.BytesIO(b''),
                final_hash="0"*64,expected_count=1,water_positions={(8,8)})
    def test_profiles_are_bounded_and_control_untouched(self):
        self.assertEqual(PROFILES[0],(.15,.35))
        for novelty,weight in PROFILES:
            self.assertTrue(0 < novelty <= 1)
            self.assertTrue(0 < weight <= 1)

if __name__=="__main__":
    unittest.main()
