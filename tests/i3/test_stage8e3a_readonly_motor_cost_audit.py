"""Synthetic-only falsifiers for the posthoc original-level descriptive audit.

No engine, World or native life launched in these tests.
"""
from hashlib import sha256
import json
import unittest

from tools import stage8e3a_readonly_motor_cost_audit as M


def cost(e=0.,v=0.):
    return {'energy':{'requested':e,'paid':e,'unpaid':0.},
            'vigilance':{'requested':v,'paid':v,'unpaid':0.}}


def work(cycles=0):
    return {'cycles':cycles,'simulated_steps':0,'memory_items':0,'replays':0}


def fixture():
    identity={'population':0,'generation':2,'arm':'S_sham','slot':0,'family':'stable',
              'repeat':0,'genome_sha256':'a'*64,'world_sha256':'b'*64,'world_seed':2,
              'life_seed':10,'source_sha256':M.ENGINE_SHA}
    manifest={'protocol':M.PROTOCOL,
              'source':{'git_head':M.ENGINE_HEAD,'sha256':M.ENGINE_SHA},
              'world_sha256':'b'*64,'world':{'name':'F0'},'life_seed':10,'horizon':400}
    mid=M.digest(manifest)
    head=sha256(json.dumps(['a'*64,'F0',10,400],separators=(',',':')).encode()).hexdigest()
    evidence=mid
    trace=[]
    for i in range(2):
        state=[99.,99.,0.2 if i==0 else 0.,100.,99.]
        core={'t':i+1,'action':'attendre','param':None,'option':'rest','body':state,
              'pos':[0,0],'dead':[] if i==0 else ['zero_water']}
        decision={'work':work(1),'accounting':cost(.02,.05),
                  'body_before':[100.,100.,0.6,100.,100.],
                  'body_after_debit':[99.98,100.,0.6,100.,99.95]}
        learning={'work':work(),'accounting':cost(),
                  'body_before':state,'body_after_debit':state}
        phases={'decision':decision,'learning':learning}
        step={**core,'cognitive_work':work(1),
              'cognitive_accounting':cost(.02,.05),'funding_phases':phases,
              'info':{'option':'rest'}}
        head=sha256((head+json.dumps(core,separators=(',',':'),sort_keys=True)).encode()).hexdigest()
        evidence=M.digest({'previous':evidence,'record':core,'work':step['cognitive_work'],
                           'accounting':step['cognitive_accounting'],
                           'funding_phases':phases})
        trace.append(step)
    audit={'schema':'i3-cognitive-funding/v2','totals':cost(.04,.10),
           'shortfall_steps':0,'pending_replays':0,'pending_energy':0.,
           'pending_vigilance':0.,'learning_updates':0,'replays_executed':0,
           'inactive_steps':0,'status':'SETTLED_FOR_DECLARED_WORK'}
    evidence=M.digest({'previous':evidence,'terminal':'dead','accounting':audit})
    life={'manifest':manifest,'manifest_id':mid,'trace_head':head,'evidence_head':evidence,
          'world':'F0','life_seed':10,'genome':'a'*64,'horizon':400,
          'steps_lived':2,'terminal':'dead','death_causes':['zero_water'],
          'actions':{'attendre':2},'drinks':0,'meals':0,
          'final_body':[99.,99.,0.,100.,99.],
          'cognitive_accounting':audit,'trace':trace}
    return identity,life


class ReadonlyMechanismTests(unittest.TestCase):
    def test_authentic_first_person_steps_and_costs(self):
        idn,life=fixture()
        one=M.summarize_one(idn,life)
        self.assertEqual(one['lives'],1)
        self.assertEqual(one['steps'],2)
        self.assertEqual(one['dead'],1)
        self.assertEqual(one['deaths']['zero_water'],1)
        self.assertEqual(one['actions']['attendre'],2)
        self.assertAlmostEqual(one['paid']['energy'],.04)
        self.assertAlmostEqual(one['paid']['vigilance'],.10)
        self.assertEqual(one['body_low10']['water'],2)

    def test_broken_native_trace_chain_rejected(self):
        idn,life=fixture()
        life['trace'][1]['action']='boire'
        with self.assertRaisesRegex(ValueError,'chain'):
            M.summarize_one(idn,life)

    def test_paid_phase_aggregates_must_match(self):
        idn,life=fixture()
        life['cognitive_accounting']['totals']['energy']['paid']=0.03
        with self.assertRaises(ValueError):
            M.summarize_one(idn,life)

    def test_action_counter_cannot_be_substituted(self):
        idn,life=fixture()
        life['actions']={'boire':2}
        with self.assertRaisesRegex(ValueError,'action counter'):
            M.summarize_one(idn,life)

    def test_life_provenance_cannot_be_retargeted(self):
        idn,life=fixture()
        life['manifest']['source']['sha256']='b'*64
        with self.assertRaises(ValueError):
            M.summarize_one(idn,life)

    def test_dead_at_horizon_is_not_misclassified_as_censored(self):
        idn,life=fixture()
        life['terminal']='censored'
        with self.assertRaises(ValueError):
            M.summarize_one(idn,life)

    def test_population_arm_units_not_per_life_significance(self):
        idn,life=fixture()
        one=M.summarize_one(idn,life)
        group=M._accumulator()
        for _ in range(144):
            M._merge(group,one)
        out=M.aggregate_group(group)
        self.assertEqual(out['lives'],144)
        self.assertEqual(out['lived_steps'],288)
        self.assertEqual(out['mean_steps'],2)
        self.assertEqual(out['dead_fraction'],1)
        self.assertEqual(out['death_zero_water_per_life'],1)
        self.assertAlmostEqual(out['cognition_energy_paid_per_step'],.02)
        self.assertEqual(out['action_attendre_per_step'],1.)
        self.assertEqual(out['body_water_below10_per_step'],1.)

    def test_unpaid_work_funding_without_matching_bill_rejected(self):
        idn,life=fixture()
        life['trace'][0]['cognitive_accounting']['energy']['requested']=.20
        with self.assertRaises(ValueError):
            M.summarize_one(idn,life)


if __name__=='__main__':
    unittest.main()
