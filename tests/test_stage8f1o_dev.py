"""DEV-only software tests; no World.step and no reserved births."""
import copy
import unittest
from types import SimpleNamespace
from tools import stage8f1o_dev_native as N
from tools import stage8f1o_prereg_static_guard as F

class TestF1ODev(unittest.TestCase):
    def test_reserved_birth_rejected(self):
        grid,_=F.check_files()
        with self.assertRaises(RuntimeError):
            N.create_dev("A",grid["origins"][0])

    def test_substantive_reads_and_order(self):
        class Spy(dict):
            def __init__(self,*a):
                super().__init__(*a)
                self.reads=[]
            def get(self,k):
                self.reads.append(k)
                return super().get(k)
        key=("boire",)
        stats=Spy({("*",):[1.,[1.,2.,3.,4.,5.],1]})
        b=(50.,)*5
        history=[{"t":1,"key":["boire"],"body":list(b),"error":[2.]*5},
                 {"t":2,"key":["boire"],"body":list(b),"error":[4.]*5}]
        mind=SimpleNamespace(last=(b,key,"boire",None),
                             effects=SimpleNamespace(stats=stats),_f1o_errors=history)
        old=copy.deepcopy(history)
        a=N.paid_forecast(mind,"corrected",3)
        c=N.paid_forecast(mind,"masked",3)
        self.assertEqual(stats.reads,[key,("boire",None),("*",)]*2)
        self.assertEqual(a["selected_tick"],2)
        self.assertEqual(a["prediction"],[53.,54.,55.,56.,57.])
        self.assertEqual(c["prediction"],[51.,52.,53.,54.,55.])
        self.assertEqual(len(a["inspections"]),2)
        self.assertEqual(history,old)

    def test_unmatched_and_future_rejected(self):
        mind=SimpleNamespace(last=((50.,)*5,("se_deplacer","north"),"se_deplacer","north"),
                             effects=SimpleNamespace(stats={}),_f1o_errors=[
                                 {"t":1,"key":["boire"],"body":[50.]*5,"error":[9.]*5}])
        self.assertEqual(N.paid_forecast(mind,"corrected",2)["prediction"],[50.]*5)
        with self.assertRaises(RuntimeError):
            N.paid_forecast(mind,"corrected",1)

if __name__=="__main__":
    unittest.main()
