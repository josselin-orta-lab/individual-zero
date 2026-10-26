"""#555: sleep interface is a byte-stable view of the general h core."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class SharedSituatedCore555(unittest.TestCase):
    def test_compatible_sleep_history_and_independent_generic_view(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(target)],
                cwd=ROOT, text=True, capture_output=True, timeout=90)
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            program = r"""
from copy import deepcopy
from i1.modules.paid_action_consolidation import record_paid_source, merge_paid_fragments
from i1.modules.situated_action_history import describe_situated_action_history
from i1.modules.situated_sleep_history import describe_situated_sleep_history

def body(e,w): return {"energy":e,"water":w,"food":70,"integrity":90}
sources=[]
for t,verb,xy,e0,e1 in (
    (1,"dormir",(2,3),100,100),
    (3,"attendre",(2,3),40,39),
    (5,"dormir",(5,6),45,48),
    (7,"dormir",(2,3),50,49),
    (9,"dormir",(2,3),60,65),
):
    for i,event in enumerate((
        {"event_id":f"c{t}","kind":"command_experienced",
         "t_monde":t,"primitive":verb,"parameters":{}},
        {"event_id":f"w{t}","kind":"world_transition_experienced",
         "t_monde":t,"position_after":{"x":xy[0],"y":xy[1]},
         "body_before":body(e0,60),"body_after":body(e1,59),
         "effects":{}},
    )):
        sources=record_paid_source(sources,episode_ref=f"ep{t}",
            event_offset=i,event=event,before_step=11)
fragments=merge_paid_fragments(sources,[],cut_step=11)
original=deepcopy(fragments)
sleep=describe_situated_sleep_history(
    published_fragments=fragments,current_site=(2,3),before_step=12)
generic=describe_situated_action_history(
    published_fragments=fragments,current_site=(2,3),
    before_step=12,primitive="dormir",parameters={})
generic["schema"]="i1-situated-observed-sleep-history-v1"
generic["current_site_ref"]="sleep-site:2:3"
for row in generic["site_observations"]:
    row["site_ref"]="sleep-site:"+":".join(map(str,row["site"]))
expected={
    ("complete_subjective_session_proven"
     if k=="independent_action_session_proven" else k):v
    for k,v in generic.items()
}
assert sleep==expected
assert list(sleep)==list(expected)
assert "independent_action_session_proven" not in sleep
assert sleep["complete_subjective_session_proven"] is False
assert sleep["historical_fragment_count"]==4
assert sleep["same_site_fragment_count"]==3
assert sleep["other_site_fragment_count"]==1
assert sleep["site_observations"][0]["sign_counts_by_fragment"]["energy"]["contradictory"]
assert sleep["site_observations"][0]["observed_full_energy_before_count"]==1
assert sleep["decision_evidence"] is False
assert sleep["causal_attribution"] is False
assert sleep["motor_permission"] is False
assert sleep["site_safety_inferred"] is False
assert sleep["expected_consequence"] is None
assert fragments==original
sleep["site_observations"][0]["experiences"][0]["observed_body_after"]["energy"]=-1
assert fragments==original
unknown=describe_situated_sleep_history(
    published_fragments=fragments,current_site=(9,9),before_step=12)
assert unknown["current_site_record_status"]=="not_observed_in_bounded_h"
assert unknown["current_site_ref"]=="sleep-site:9:9"
try:
    describe_situated_sleep_history(
        published_fragments=fragments,current_site=(2,3),before_step=10)
except ValueError:pass
else:raise AssertionError("future h read accepted")
print("I1_555_SHARED_SITUATED_CORE_OK")
"""
            env=os.environ.copy()
            env["PYTHONPATH"]=os.pathsep.join((str(target),str(ROOT/"src")))
            run=subprocess.run([sys.executable,"-c",program],cwd=ROOT,
                 env=env,text=True,capture_output=True,timeout=120)
            self.assertEqual(run.returncode,0,run.stdout+"\n"+run.stderr)
            self.assertIn("I1_555_SHARED_SITUATED_CORE_OK",run.stdout)


if __name__=="__main__":
    unittest.main()
