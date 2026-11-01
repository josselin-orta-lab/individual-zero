"""Adversarial frozen M11 static Competition gate contracts (no births)."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "research"))

from i1_a1c_wait_gate import scan_gate, summarize, ROLES, SEEDS, ARMS
from i1_a1c_wait_gate_audit import audited_cohort


def fixture(*, role='canonical', q=0.7, final_cross=True,
            other_cross=False, food=35, inventory=1,
            permanent=True, simulator_unavailable=True):
    ref = 'permanent:attendre' if permanent else 'option:i1:affordance:goal:restore_integrity:t1:attendre:here'
    signature = 'primitive:attendre' if permanent else 'i1:affordance:attendre:here'
    other = 'option:sleep:1'
    data = {
        'option_ref': ref, 'learning_signature': signature,
        'status': 'evaluated',
        'learned_value_status': 'learned' if role == 'canonical' else 'unlearned',
        'learned_value': q if role == 'canonical' else None,
        'simulated_value_status': 'unavailable' if simulator_unavailable else 'computed',
        'simulated_value': None if simulator_unavailable else 1.0,
    }
    events = [
        {'t_monde':1, 'kind':'perceptual_capture', 'data':{
            'dual_scope_visible_body':{'energy':80,'food':food,'water':85,'integrity':90},
            'agency_visible_inventory':{'berry_a':inventory,'berry_b':0}}},
        {'t_monde':1,'kind':'stage8_option_evaluation','cycle':1,'data':data},
        {'t_monde':1,'kind':'stage8_option_evaluation','cycle':1,'data':{
            'option_ref':other,'learning_signature':'primitive:dormir',
            'status':'evaluated','learned_value_status':'unlearned',
            'learned_value':None,'simulated_value_status':'unavailable','simulated_value':None}},
        {'t_monde':1,'kind':'competition_cycle','cycle':1,'data':{'traces':[
            {'option_ref':ref,'accumulator_before':0.25,
             'accumulator_after':0.55 if final_cross else 0.35,
             'threshold':0.5,'crossed':final_cross,'evidence':0.3},
            {'option_ref':other,'accumulator_before':0.,
             'accumulator_after':0.65 if other_cross else 0.12,
             'threshold':0.5,'crossed':other_cross,'evidence':0.15}] }},
        {'t_monde':1,'kind':'command_admitted','data':{
            'source':'decision','primitive':'attendre','option_ref':ref}}
    ]
    if not final_cross:
        events[-1]['data']['option_ref']='permanent:attendre'
    events.extend({'t_monde':t,'kind':'command_admitted','data':{
        'source':'sleep','primitive':'dormir'}} for t in range(2,49))
    return events


class StaticGateContracts(unittest.TestCase):
    def test_permanent_positive_Q_only_sole_crossing(self):
        r=scan_gate(fixture(),mode='canonical')
        self.assertEqual(r['counts']['hungry_stock_opportunities'],1)
        self.assertEqual(r['counts']['wait_admissions'],1)
        self.assertEqual(r['counts']['permanent_wait_Q_only_wins'],1)
        self.assertEqual(r['counts']['permanent_wait_Q_only_sole_crossing'],1)
        self.assertEqual(r['counts']['permanent_Q_only_new_threshold_crossing'],1)
        self.assertEqual(r['witnesses'][0]['Q_only_under_frozen_Stage8'],True)
        self.assertEqual(r['scope'],'RECORDED_FINAL_CYCLE_ONLY_NOT_CAUSAL_POLICY_REPLAY')

    def test_competing_crossing_is_not_sole(self):
        r=scan_gate(fixture(other_cross=True),mode='canonical')
        self.assertEqual(r['counts']['permanent_wait_Q_only_sole_crossing'],0)
        self.assertEqual(r['counts']['permanent_wait_Q_only_other_crossed'],1)

    def test_local_Q_uses_possible_prior_and_must_not_be_called_Q_only(self):
        r=scan_gate(fixture(permanent=False),mode='canonical')
        self.assertEqual(r['counts']['other_wait_Q_with_possible_prior'],1)
        self.assertNotIn('permanent_wait_Q_only_wins',r['counts'])
        self.assertIs(r['witnesses'][0]['Q_only_under_frozen_Stage8'],False)

    def test_masked_and_negative_or_simulated_Q_not_Q_only(self):
        for mode,kwargs in (
            ('td_read_masked',{}),('canonical',{'q':-0.4}),
            ('canonical',{'simulator_unavailable':False})):
            with self.subTest(mode=mode,kwargs=kwargs):
                r=scan_gate(fixture(role=mode,**kwargs),mode=mode)
                self.assertNotIn('observed_positive_Q_without_sim_wait_wins',r['counts'])

    def test_inaction_without_food_is_not_an_opportunity(self):
        for kwargs in ({'inventory':0},{'food':60},{'food':80}):
            with self.subTest(kwargs=kwargs):
                self.assertNotIn('hungry_stock_opportunities',
                                 scan_gate(fixture(**kwargs),mode='canonical')['counts'])

    def test_below_threshold_is_fallback_not_a_learning_win(self):
        r=scan_gate(fixture(final_cross=False),mode='canonical')
        self.assertEqual(r['counts']['wait_fallback_without_crossing'],1)
        self.assertNotIn('permanent_wait_Q_only_wins',r['counts'])

    def test_forged_threshold_stage8_option_and_duplicate_m11_rejected(self):
        a=fixture()
        for changed in (lambda e: e[3]['data']['traces'][0].update(crossed=False),
                        lambda e: e[3]['data']['traces'][1].update(option_ref='other'),
                        lambda e: e.append(deepcopy(e[1])),
                        lambda e: e.pop(0),
                        lambda e: e.pop(-1)):
            e=deepcopy(a)
            changed(e)
            with self.assertRaises(ValueError):
                scan_gate(e,mode='canonical')

    def test_per_temperament_not_pseudoreplicated(self):
        lives=[]
        for role in ROLES:
            for seed in SEEDS:
                for arm in ARMS:
                    n=7 if role=='native' and seed==101 and arm=='canonical' else 0
                    lives.append({'role':role,'seed':seed,'mode':arm,
                                  'scope':'RECORDED_FINAL_CYCLE_ONLY_NOT_CAUSAL_POLICY_REPLAY',
                                  'counts':{'permanent_wait_Q_only_sole_crossing':n}})
        z=summarize(lives)
        self.assertEqual(z['number_affected_independent_temperament_blocks'],1)
        self.assertEqual(z['affected_independent_temperament_seeds'],[101])
        self.assertEqual(z['independent_temperament_blocks'],12)
        self.assertEqual(z['a1c_confirmatory_status'],'NO_GO')
        for bad in (lives[:-1],lives+[lives[0]],
                    [{**q,'seed':100} if i==0 else q
                     for i,q in enumerate(lives)]):
            with self.assertRaises(ValueError):
                summarize(bad)

    def test_archival_wrong_run_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'I1_ECO_A1C_EVIDENCE_MANIFEST.json'
            p.write_text(json.dumps({'original_run_id':99,
                                     'original_source_sha':'foreign',
                                     'archived_independent_lives':48}))
            with self.assertRaises(ValueError):
                audited_cohort(Path(d),workers=1)

if __name__=='__main__':
    unittest.main()
