"""Issue #328 isolated prototype: execute in generated I1 namespace."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class Place(unittest.TestCase):
    def test_physical_provenance(self):
        with TemporaryDirectory(prefix="i1-lived-site-") as d:
            built=Path(d)/"built"
            generate(built)
            script=r"""
from types import SimpleNamespace
from i1.experimental.experienced_place_relevance import experienced_site_relevance, personally_supported_site_gain
owner=SimpleNamespace(life_id="i1:alpha",enabled=True,examples=[{"source_position":[2,3],"delta_water":12.0,"sent_world_step":1,"observed_world_step":2}])
assert personally_supported_site_gain(owner,site=(2,3),life_id="i1:alpha")==12.0
assert personally_supported_site_gain(owner,site=(3,2),life_id="i1:alpha") is None
try:personally_supported_site_gain(owner,site=(2,3),life_id="i1:wrong")
except ValueError:pass
else:raise AssertionError("unowned place gain accepted")
assert experienced_site_relevance(observed_gain=12,current_water=10,confidence=.8,observed_hops=2)>0
assert experienced_site_relevance(observed_gain=12,current_water=90,confidence=.8,observed_hops=2)==0
print("I1_328_ISOLATED_PLACE_OK")
"""
            p=subprocess.run([sys.executable,"-c",script],
               cwd=ROOT,env={"PYTHONPATH":str(built)+":"+str(ROOT/"src")},
               text=True,capture_output=True,check=False)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            self.assertIn("I1_328_ISOLATED_PLACE_OK",p.stdout)
