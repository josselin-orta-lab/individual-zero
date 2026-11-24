"""No-engine PH1 abuse tests on F1J threshold witness algebra only."""
from __future__ import annotations
import ast
from copy import deepcopy
import pathlib
import unittest
import importlib.util

PATH=pathlib.Path(__file__).resolve().parents[1] / 'tools' / 'stage8f1m_ph1_archival_thresholds.py'
if not PATH.is_file():
    PATH=pathlib.Path(__file__).with_name('stage8f1m_ph1_archival_thresholds.py')
spec=importlib.util.spec_from_file_location('ph1_readonly_thresholds',PATH)
ph1=importlib.util.module_from_spec(spec)
spec.loader.exec_module(ph1)


def make_step(initial_B=1.7, rounds=3):
    evidence={'A':0.9,'B':0.2}
    thresholds={'A':1.5,'B':1.5}
    state={'A':0.0,'B':initial_B}
    hist=[]
    for i in range(rounds):
        state={key:max(0.0,0.8*state[key]+evidence[key]) for key in state}
        hist.append(dict(state))
    finals=hist[-1]
    w={
        'scored_order':['B','A'],'normalized_evidence':evidence,'thresholds':thresholds,
        'accumulators_before':{'A':0.0,'B':initial_B},
        'accumulators_before_residual':finals,
        'accumulators_after_residual':{'A':0.0,'B':0.5*finals['B']},
        'actual_substantive_round_snapshots':hist,
        'round_capacity_from_actual_body':rounds,'paid_competition_cycles':rounds,
        'budget_blocked_before_full_round_capacity':False,
        'winner_before_control':'A','tie_candidates':['A'],
        'selection_mechanism':'final_round_threshold','final_admitted_action':'wait'
    }
    return {'action':'wait','decision_info':{'observer':{'competition_witness':w}}}


class TestReadOnlyThresholds(unittest.TestCase):
    def test_no_engine_imports_or_native_birth_calls(self):
        tree=ast.parse(PATH.read_text(encoding='utf8'))
        modules=[node.module for node in ast.walk(tree)
                 if isinstance(node,ast.ImportFrom)]
        modules += [name.name for node in ast.walk(tree)
                    if isinstance(node,ast.Import) for name in node.names]
        self.assertFalse(any(m.startswith(('i3.','tools.stage8f1m_scientific_native'))
                             for m in modules if m))
        self.assertNotIn('World.step(', PATH.read_text())

    def test_early_threshold_change_may_vanish_by_fixed_last_round(self):
        carry=make_step(initial_B=1.7)
        zero=make_step(initial_B=0.0)
        w1,r1=ph1.validate_competition_witness(carry,'carry')
        w2,r2=ph1.validate_competition_witness(zero,'zero')
        self.assertEqual(w1['winner_before_control'],w2['winner_before_control'])
        self.assertEqual(r1[0]['crossed'],['B'])
        self.assertEqual(r2[0]['crossed'],[])
        self.assertEqual(r1[-1]['candidates'],r2[-1]['candidates'])
        self.assertEqual(ph1._first_round_crossing(r1),1)
        self.assertEqual(ph1._first_round_crossing(r2),2)
        self.assertEqual(ph1._first_round_final_winner_crossing(w1,r1),2)
        self.assertEqual(ph1._first_round_final_winner_crossing(w2,r2),2)

    def test_tampered_funded_substantive_round_rejected(self):
        bad=make_step()
        bad['decision_info']['observer']['competition_witness']['actual_substantive_round_snapshots'][1]['B']+=0.1
        with self.assertRaisesRegex(ValueError,'not substantive F1J'):
            ph1.validate_competition_witness(bad,'tampered')

    def test_after_residual_and_threshold_tamper_rejected(self):
        for key,amount in [('accumulators_after_residual',0.11),('thresholds',-1)]:
            bad=make_step()
            bad['decision_info']['observer']['competition_witness'][key]['B']+=amount
            with self.assertRaises(ValueError):
                ph1.validate_competition_witness(bad,'mutated')

    def test_missing_roots_cannot_be_relabelled_conclusive(self):
        with self.assertRaisesRegex(ValueError,'not 64 contrasts'):
            ph1.summary([])
        # Invalid archive bytes must fail before any simulated calculation.
        self.assertNotEqual(ph1.sha(b'corrupted-raw'),ph1.RAW_TAR_SHA)

    def test_final_mind_source_pin_is_exact(self):
        self.assertEqual(ph1.RAW_TAR_SHA,
                         '4e4888d00d5494f071d84d469e26f62d497dba8ce390bbe01101607a018992bc')
        self.assertEqual(ph1.FROZEN_MAIN_SHA,
                         'a0d063402cad87d6dd255e2f842586b8f8f95267')


if __name__=='__main__':
    unittest.main()
