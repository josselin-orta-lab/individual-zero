"""Synthetic arithmetic and static safeguards; no engine, no scientific lives."""
import copy
import json
import unittest
from tools import stage8f1o_prereg_static_guard as S


class TestF1OStatic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g=json.loads(S.GRID.read_bytes())

    def test_grid_structure(self):
        S.verify_grid(self.g)

    def test_exact_exposure_and_threshold_guards(self):
        for path,key,value in [('exposure','scientific_dispatch_authorized',True),
                               ('primary','min_global_gain',0),
                               ('memory','correction_gain',1.),
                               ('scope','motor_or_adaptation_claim_allowed',True)]:
            g=copy.deepcopy(self.g);g[path][key]=value
            with self.assertRaises(ValueError): S.verify_grid(g)

    def test_native_fallback_reads_three_candidates(self):
        class Counted(dict):
            def __init__(self,*a): super().__init__(*a);self.reads=[]
            def get(self,k): self.reads.append(k);return super().get(k)
        a=Counted({('manger',None):[2,[1,2,3,4,5],2],('*',):[8,[0]*5,8]})
        self.assertEqual(S.native_mean_reference(a,('manger','x')),(1,2,3,4,5))
        self.assertEqual(a.reads,[('manger','x'),('manger',None),('*',)])

    def test_context_selection_and_tie_no_other_key(self):
        b=[50]*5
        rows=[{'t':1,'key':['boire'],'body':[40]*5,'error':[1]*5},
              {'t':2,'key':['boire'],'body':[60]*5,'error':[2]*5},
              {'t':3,'key':['dormir'],'body':b,'error':[3]*5}]
        self.assertEqual(S.choose_record(rows,('boire',),b,4),(2,(2.,)*5))
        self.assertEqual(S.choose_record(rows,('manger','x'),b,4),(None,(0.,)*5))
        rows[1]['t']=4
        with self.assertRaises(ValueError): S.choose_record(rows,('boire',),b,4)

    def test_mask_same_math_and_clamp(self):
        b=[95,3,50,50,50];m=[4,-1,0,0,0];e=[8,-8,4,-4,0]
        self.assertEqual(S.point_forecast(b,m,e,'corrected'),(100.,0.,52.,48.,50.))
        self.assertEqual(S.point_forecast(b,m,e,'masked'),(99.,2.,50.,50.,50.))
        self.assertEqual(S.point_forecast(b,m,[0]*5,'corrected'),
                         S.point_forecast(b,m,e,'masked'))
        self.assertEqual(S.forecast_work(8),{'cycles':1,'simulated_steps':1,'memory_items':11,'replays':0})
        with self.assertRaises(ValueError): S.forecast_work(9)

    def rows(self,gain):
        return [{'id':o['id'],'ecology':o['ecology'],'independent_quality_verified':True,
                 'pairs':[{'t':t,'target':[50]*5,'masked':[51]*5,
                           'corrected':[51-gain]*5} for t in S.VALIDATE]}
                for o in self.g['origins']]

    def test_joint_gain_thresholds_and_negative(self):
        self.assertEqual(S.reference_verdict(self.g,self.rows(.5))['verdict'],S.POSITIVE)
        self.assertEqual(S.reference_verdict(self.g,self.rows(.05))['verdict'],S.NEGATIVE)
        self.assertEqual(S.reference_verdict(self.g,self.rows(-.5))['verdict'],S.NEGATIVE)
        a=self.rows(.5)
        for r in a[30:]:
            for p in r['pairs']: p['corrected']=p['masked']
        self.assertEqual(S.reference_verdict(self.g,a)['verdict'],S.NEGATIVE)
        a=self.rows(.5)
        # 32 wins can be concentrated in fewer than 6 positive ecology means.
        for r in a[30:]:
            for p in r['pairs']: p['corrected']=[51.1]*5
        for r in a[30:32]:
            for p in r['pairs']: p['corrected']=[50.99]*5
        v=S.reference_verdict(self.g,a)
        self.assertEqual(v['positive_roots'],32)
        self.assertEqual(v['positive_ecologies'],5)
        self.assertEqual(v['verdict'],S.NEGATIVE)

    def test_incomplete_unpaid_or_invalid_is_inconclusive(self):
        for case in ('missing','unpaid','tick','wrong_origin','nan'):
            rows=self.rows(.5)
            if case=='missing': rows.pop()
            elif case=='unpaid': rows[0]['independent_quality_verified']=False
            elif case=='tick': rows[0]['pairs'].pop()
            elif case=='wrong_origin': rows[0]['id']='O02'
            elif case=='nan': rows[0]['pairs'][0]['corrected'][0]=float('nan')
            self.assertEqual(S.reference_verdict(self.g,rows)['verdict'],S.INCONCLUSIVE)


if __name__=='__main__': unittest.main()
