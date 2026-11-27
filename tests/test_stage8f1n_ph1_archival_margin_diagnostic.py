"""Tests for the archival-only F1N-PH1 diagnostic (no engine or new life)."""
import ast
import io
from pathlib import Path
import unittest
from unittest.mock import patch

from tools import stage8f1n_ph1_archival_margin_diagnostic as ph


class ArchivalMarginTests(unittest.TestCase):
    def test_wrong_cold_fails_before_archive_read(self):
        def forbidden(*args):
            self.fail('archive must not be read with wrong cold report')
        with self.assertRaisesRegex(ValueError, 'wrong cold report'):
            ph.audit_assets(forbidden, forbidden, b'{}')

    def test_wrong_tar_fails_before_manifest_read(self):
        with patch.object(ph, 'COLD', ph.sha(b'{}')):
            with self.assertRaisesRegex(ValueError, 'wrong immutable original tar'):
                ph.audit_assets(lambda _: self.fail('must not read manifest'),
                                lambda: io.BytesIO(b'not original tar'), b'{}')

    def test_round_crossing_differs_without_final_crossing_diff(self):
        trace=[{'boire':.6,'dormir':.8}, {'boire':1.1,'dormir':1.4},
               {'boire':1.47,'dormir':1.9}, {'boire':1.78,'dormir':2.29},
               {'boire':2.02,'dormir':2.60}]
        a={'thresholds':{'boire':.773,'dormir':1.5},
           'actual_substantive_round_snapshots':trace,
           'accumulators_before_residual':trace[-1]}
        b=dict(a, thresholds={'boire':1.5,'dormir':1.5})
        self.assertEqual(ph.first_cross(a,'boire'),2)
        self.assertEqual(ph.first_cross(b,'boire'),4)
        self.assertEqual(ph.crossings(a,trace[-1]),ph.crossings(b,trace[-1]))
        self.assertGreater(ph.final_surplus(a,'boire'),ph.final_surplus(a,'dormir'))
        self.assertLess(ph.final_surplus(b,'boire'),ph.final_surplus(b,'dormir'))
        self.assertIsNone(ph.first_cross(b,'absent'))

    def test_rank_tied_scores_and_absent_key(self):
        scores={'attendre':{'total_score':-.041},'dormir':{'total_score':-.041},
                'boire':{'total_score':-.048}}
        self.assertEqual(ph.score_rank(scores,'attendre'),1)
        self.assertEqual(ph.score_rank(scores,'boire'),3)
        self.assertIsNone(ph.score_rank(scores,'absent'))

    def test_no_engine_or_producer_import(self):
        tree=ast.parse(Path(ph.__file__).read_text())
        permitted={'__future__','argparse','collections','gzip','hashlib','json',
                   'pathlib','statistics','tarfile','zipfile'}
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):
                self.assertTrue(all(a.name in permitted for a in n.names))
            elif isinstance(n,ast.ImportFrom):
                self.assertIn(n.module,permitted)


if __name__=='__main__':
    unittest.main()
