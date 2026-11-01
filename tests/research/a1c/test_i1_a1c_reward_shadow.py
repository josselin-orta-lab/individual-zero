"""Adversarial contracts for frozen-tape reward shadow; no I1 imports/births."""
from copy import deepcopy
from pathlib import Path
import json
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "research"))

from i1_a1c_reward_shadow import (
    DualFrozenTD, config_from_birth, discounted, reward_between,
    reward_components,
)
from i1_a1c_reward_shadow_audit import summarize, audit


SETPOINTS={'energy':50., 'food':60., 'water':60., 'integrity':100.}
WEIGHTS={'energy':1., 'food':1., 'water':1., 'integrity':1.}
INITIAL={'energy':70., 'food':35., 'water':35., 'integrity':85.}


def birth():
    return {
        'source_commit':'26f7929b6db43f68e78b0cc0d9c67e7444f924c6',
        'setpoints':dict(SETPOINTS),
        'born_temperament':{'body_weights':dict(WEIGHTS)},
        'born_td':{'version':'p31-stage8-reference-v1', 'eta':.05,
                   'lambda_e':.8, 'beta':.8},
    }


class RewardAndFixedTapeContracts(unittest.TestCase):
    def test_real_drinking_overshoot_abs_vs_shortfall(self):
        before=INITIAL
        after={'energy':69.5,'food':34.8,'water':74.6,'integrity':85.}
        native=reward_between(before,after,setpoints=SETPOINTS,
                              weights=WEIGHTS,mode='absolute_setpoint')
        candidate=reward_between(before,after,setpoints=SETPOINTS,
                                 weights=WEIGHTS,mode='deficit_only')
        self.assertAlmostEqual(native,10.7)
        self.assertAlmostEqual(candidate,24.8)
        second={'energy':69.,'food':34.6,'water':100.,'integrity':85.}
        self.assertAlmostEqual(reward_between(after,second,setpoints=SETPOINTS,
                            weights=WEIGHTS,mode='absolute_setpoint'),-25.1)
        self.assertAlmostEqual(reward_between(after,second,setpoints=SETPOINTS,
                            weights=WEIGHTS,mode='deficit_only'),-.2)

    def test_native_equals_deficit_plus_above_setpoint_drifts_by_need(self):
        a = INITIAL
        b = {'energy':69.5, 'food':34.8, 'water':74.6, 'integrity':85.}
        parts = reward_components(a,b,setpoints=SETPOINTS,weights=WEIGHTS)
        self.assertAlmostEqual(parts['native_total'], 10.7)
        self.assertAlmostEqual(parts['deficit_total'], 24.8)
        self.assertAlmostEqual(parts['surplus_total'], -14.1)
        self.assertAlmostEqual(parts['surplus_by_need']['energy'], .5)
        self.assertAlmostEqual(parts['surplus_by_need']['water'], -14.6)
        self.assertAlmostEqual(parts['native_total'],
                               parts['deficit_total'] + parts['surplus_total'])
        second = {'energy':69.,'food':34.6,'water':100.,'integrity':85.}
        p2 = reward_components(b, second,setpoints=SETPOINTS,weights=WEIGHTS)
        self.assertAlmostEqual(p2['surplus_by_need']['water'], -25.4)
        self.assertAlmostEqual(p2['native_total'],-25.1)
        self.assertAlmostEqual(p2['deficit_total'],-.2)

    def test_collection_cost_cannot_learn_good_berry_or_reward_inaction(self):
        before={'energy':70.,'food':35.,'water':95.,'integrity':85.}
        after={'energy':69.,'food':34.8,'water':94.6,'integrity':85.}
        self.assertAlmostEqual(reward_between(before,after,setpoints=SETPOINTS,
                               weights=WEIGHTS,mode='absolute_setpoint'),1.2)
        self.assertAlmostEqual(reward_between(before,after,setpoints=SETPOINTS,
                               weights=WEIGHTS,mode='deficit_only'),-.2)
        self.assertEqual(reward_between(before,before,setpoints=SETPOINTS,
                         weights=WEIGHTS,mode='deficit_only'),0.)

    def test_shortfall_penalty_never_rewards_harmful_loss_below_target(self):
        before={'energy':40.,'food':35.,'water':25.,'integrity':80.}
        after={'energy':39.,'food':34.,'water':24.,'integrity':79.}
        result=reward_between(before,after,setpoints=SETPOINTS,
                              weights=WEIGHTS,mode='deficit_only')
        self.assertEqual(result,-4.)

    def test_malformed_nonfinite_out_of_range_body_rejected(self):
        for malformed in (
            {**INITIAL, 'water':float('nan')},
            {**INITIAL, 'water':101},
            {**INITIAL, 'water':True},
            {**INITIAL, 'water':{'$f64':'0x1p+1'}},
            {k:v for k,v in INITIAL.items() if k!='food'},
        ):
            with self.subTest(malformed=malformed),self.assertRaises(ValueError):
                reward_between(malformed,INITIAL,setpoints=SETPOINTS,
                               weights=WEIGHTS,mode='deficit_only')
        with self.assertRaises(ValueError):
            reward_between(INITIAL,INITIAL,setpoints=SETPOINTS,
                           weights=WEIGHTS,mode='arbitrary_bonus_for_manger')

    def test_source_and_born_coefficients_are_immutable(self):
        base=birth()
        self.assertEqual(config_from_birth(base)[1]['water'],1.)
        for f in (
            lambda d: d.update(source_commit='false-sha'),
            lambda d: d['born_td'].update(eta=.5),
            lambda d: d['born_temperament']['body_weights'].update(food=-2.),
            lambda d: d['setpoints'].update(water=101.),
        ):
            b=deepcopy(base)
            f(b)
            with self.assertRaises(ValueError):
                config_from_birth(b)

    def test_segment_discounting_and_empty_rejection(self):
        self.assertAlmostEqual(discounted([2,3,4],.8),2+2.4+2.56)
        with self.assertRaises(ValueError):
            discounted([],.8)

    def test_dual_replay_changes_q_but_not_original_actions(self):
        model=DualFrozenTD()
        features=(1.,) * 12
        row={'segment_length':1,'return_g':1.2,'q_previous':0.,
             'q_next':0.,'delta':1.2, 'previous_signature':'collect',
             'next_signature':'wait','td_version':'p31-stage8-reference-v1',
             'updated_signatures':['collect']}
        model.update(previous_sig='collect',previous_phi=features,
                     next_sig='wait',next_phi=features,
                     native_segment=[1.2],shadow_segment=[-.2],row=row)
        self.assertGreater(model.q('collect',features,mode='native'),0.)
        self.assertLess(model.q('collect',features,mode='shadow'),0.)
        self.assertEqual(model.counts,{'collect':1})
        self.assertEqual(model.updates,1)

    def test_tampered_native_return_snapshot_and_signature_rejected(self):
        feats=(1.,)*12
        original={'segment_length':1,'return_g':1.2,'q_previous':0.,
                  'q_next':0.,'delta':1.2,'previous_signature':'collect',
                  'next_signature':'wait','td_version':'p31-stage8-reference-v1',
                  'updated_signatures':['collect']}
        for name,value in (
            ('return_g',-1),('q_previous',2),('q_next',2),('delta',2),
            ('updated_signatures',['foreign']),('segment_length',2),
            ('previous_signature','foreign'),('td_version','not-current'),
        ):
            with self.subTest(field=name),self.assertRaises(ValueError):
                DualFrozenTD().update(
                    previous_sig='collect',previous_phi=feats,
                    next_sig='wait',next_phi=feats,
                    native_segment=[1.2],shadow_segment=[-.2],
                    row={**original,name:value})

    def test_never_infer_from_partial_or_wrong_cohort(self):
        with self.assertRaises(ValueError):
            summarize([])
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)
            manifest={'original_run_id':40944104333,
                      'original_source_sha':'26f7929b6db43f68e78b0cc0d9c67e7444f924c6',
                      'archived_independent_lives':48,
                      'original_zip_archives':[]}
            (path/'I1_ECO_A1C_EVIDENCE_MANIFEST.json').write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                audit(path)
            manifest['original_source_sha']='forged'
            (path/'I1_ECO_A1C_EVIDENCE_MANIFEST.json').write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                audit(path)


if __name__=='__main__':
    unittest.main()
