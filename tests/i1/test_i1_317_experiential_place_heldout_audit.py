import importlib.util,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location("holdaudit",ROOT/"tools/audit_i1_317_experiential_place_heldout.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class HeldoutEvidence(unittest.TestCase):
 def test_design(self):
  self.assertEqual(len(m.SEEDS)*len(m.WORLDS)*len(m.ARMS),32)
  self.assertEqual(m.EXACT_RUN,39324485459)
 def test_incomplete_cohort(self):
  with TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.certify(Path(d))
 def test_goal_switch_must_be_authenticated_at_stage8(self):
  from tempfile import TemporaryDirectory
  from json import dumps
  with TemporaryDirectory() as d:
   wal=Path(d)/"life.wal"
   rows=[
    {"kind":"active_goal_changed","t_monde":1,"cycle":1,"data":{
      "before":None,"after":{"goal_type":"eat","id":"goal:eat:x"}}},
    {"kind":"i1_place_memory_option_proposed","t_monde":1,"cycle":1,"data":{
      "option_ref":"option:place-memory:x","target":[8,8],
      "active_goal":"goal:eat:x","next":[9,8]}},
    {"kind":"stage11_intrinsic_evaluation","t_monde":1,"cycle":1,"data":{
      "option_ref":"option:place-memory:x",
      "signal_ids":["i1:personally-relieved-water:8:8"],
      "intrinsic_producers":["i1:conditional-lived-site-relevance"]}},
   ]
   wal.write_text("".join(dumps({"causal_event":row})+"\n" for row in rows))
   with self.assertRaisesRegex(ValueError,"without live drink goal"):
    m.inspect_wal(wal,"guard_experiential",1)
 def test_no_unnatural_motor_credit(self):
  with self.assertRaises(ValueError):m.require(False,"no forged credit")
if __name__=="__main__":unittest.main()
